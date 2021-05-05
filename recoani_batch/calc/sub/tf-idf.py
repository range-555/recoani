#!/usr/bin/env python
# coding: utf-8

# In[86]:


from __future__ import unicode_literals
import MeCab
import mysql.connector as mydb
import os
import re
import time
from tqdm import tqdm
import unicodedata
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity


# In[87]:


connection = mydb.connect(
    host = os.environ.get('ml_db_host'),
    port = os.environ.get('local_port'),
    user = os.environ.get('recoani_user'),
    password = os.environ.get('recoani_pass'),
    database = os.environ.get('recoani_db')
)


# In[88]:


stop_pos = {
    "助詞,格助詞,一般,*",
    "助詞,格助詞,引用,*",
    "助詞,格助詞,連語,*",
    "助詞,係助詞,*,*",
    "助詞,終助詞,*,*",
    "助詞,接続助詞,*,*",
    "助詞,特殊,*,*",
    "助詞,副詞化,*,*",
    "助詞,副助詞,*,*",
    "助詞,副助詞／並立助詞／終助詞,*,*",
    "助詞,並立助詞,*,*",
    "助詞,連体化,*,*",
    "助動詞,*,*,*",
    "記号,句点,*,*",
    "記号,読点,*,*",
    "記号,空白,*,*",
    "記号,一般,*,*",
    "記号,アルファベット,*,*",
    "記号,一般,*,*",
    "記号,括弧開,*,*",
    "記号,括弧閉,*,*",
    "動詞,接尾,*,*",
    "動詞,非自立,*,*",
    "名詞,非自立,一般,*",
    "名詞,非自立,形容動詞語幹,*",
    "名詞,非自立,助動詞語幹,*",
    "名詞,非自立,副詞可能,*",
    "名詞,接尾,助動詞語幹,*",
    "名詞,接尾,人名,*",
    "接頭詞,名詞接続,*,*"
    }
stop_words = []
stop_word_regex = []
vocab_list = []
get_word = []


# In[89]:


# 文章を正規化するクラス
class Normalize:
    
    def __init__(self,sentence):
        self.sentence = sentence
        
    def normalize(self):
        return self.normalize_neologd()

    def unicode_normalize(self,cls,s):
        pt = re.compile('([{}]+)'.format(cls))

        def norm(c):
            return unicodedata.normalize('NFKC', c) if pt.match(c) else c
    
        s = ''.join(norm(x) for x in re.split(pt, s))
        s = re.sub('－', '-', s)
        return s

    def remove_extra_spaces(self,s):
        s = re.sub('[ 　]+', ' ', s)
        blocks = ''.join(('\u4E00-\u9FFF',  # CJK UNIFIED IDEOGRAPHS
                          '\u3040-\u309F',  # HIRAGANA
                          '\u30A0-\u30FF',  # KATAKANA
                          '\u3000-\u303F',  # CJK SYMBOLS AND PUNCTUATION
                          '\uFF00-\uFFEF'   # HALFWIDTH AND FULLWIDTH FORMS
                          ))
        basic_latin = '\u0000-\u007F'
    
        def remove_space_between(cls1,cls2,s):
            p = re.compile('([{}]) ([{}])'.format(cls1, cls2))
            while p.search(s):
                s = p.sub(r'\1\2', s)
            return s
    
        s = remove_space_between(blocks, blocks, s)
        s = remove_space_between(blocks, basic_latin, s)
        s = remove_space_between(basic_latin, blocks, s)
        return s
    
    def normalize_neologd(self):
        s = self.sentence
        s = s.strip()
        s = self.unicode_normalize('０-９Ａ-Ｚａ-ｚ｡-ﾟ', s)
        def maketrans(f, t):
            return {ord(x): ord(y) for x, y in zip(f, t)}
    
        s = re.sub('[˗֊‐‑‒–⁃⁻₋−]+', '-', s)  # normalize hyphens
        s = re.sub('[﹣－ｰ—―─━ー]+', 'ー', s)  # normalize choonpus
        s = re.sub('[~∼∾〜〰～]+', '〜', s)  # normalize tildes (modified by Isao Sonobe)
        s = s.translate(
            maketrans('!"#$%&\'()*+,-./:;<=>?@[¥]^_`{|}~｡､･｢｣',
                  '！”＃＄％＆’（）＊＋，－．／：；＜＝＞？＠［￥］＾＿｀｛｜｝〜。、・「」'))
        s = self.remove_extra_spaces(s)
        s = self.unicode_normalize('！”＃＄％＆’（）＊＋，－．／：；＜＞？＠［￥］＾＿｀｛｜｝〜', s)  # keep ＝,・,「,」
        s = re.sub('[’]', '\'', s)
        s = re.sub('[”]', '"', s)
        s = s.upper()
        return s


# In[90]:


# 形態素解析用クラス
class Morph(object):
    def __init__(self, surface, pos, base):
        self.surface = surface
        self.pos = pos
        self.base = base
    def __repr__(self):
        return str({
            "surface": self.surface,
            "pos": self.pos,
            "base": self.base
        })


# In[91]:


def tokenize(sentence,title):
    if len(sentence) < 10:
        sentence = title
    
    s = Normalize(sentence)
    sentence = s.normalize()
    mecab.parse("")
    lines = mecab.parse(sentence).split("\n")
    tokens = []
    for line in lines:
        elems = line.split("\t")
        if len(elems) < 2:
            continue
        surface = elems[0]
        if len(surface):
            feature = elems[1].split(",")
            base = surface if len(feature) < 7 or feature[6] == "*" else feature[6]
            pos = ",".join(feature[0:4])
            tokens.append(Morph(surface=surface, pos=pos, base=base))
    return tokens


# In[92]:


def create_vocab_list(data):
    vocab = {}
    for item in data:
        tokens = item['tokens']
        for token in tokens:
            key = token.base
            pos = token.pos
            is_stop = pos in stop_pos
            v = vocab.get(key, { "count": 0, "pos": pos , "stop": is_stop})
            v["count"] += 1
            vocab[key] = v
    for k in vocab:
        v = vocab[k]
        if not v["stop"]:
            vocab_list.append((v["count"], k, v["pos"], v["stop"]))


# In[93]:


def is_stop(vocab):
    return vocab[2] in stop_pos or vocab[1] in stop_words or any([r for r in stop_word_regex if r.match(vocab[1]) is not None])


# In[94]:


# Tools
mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
tfidf = TfidfVectorizer(
    max_df=0.5,
    min_df=4,
    max_features=1280,
    analyzer='word',
    ngram_range=(1, 1)
)


# In[95]:


cursor = connection.cursor(buffered=True, dictionary=True)
cursor.execute("SELECT id, title, outline_entire FROM animes")
data = cursor.fetchall()


# In[96]:


for item in data:
    item['tokens'] = tokenize(item['outline_entire'],item['title'])


# In[97]:


create_vocab_list(data)


# In[98]:


vocab_list = sorted(vocab_list, reverse=True)
for i in range(10):
    print(vocab_list[i])


# In[99]:


# count > 500 && stop_word
stop_words += [
    'する', 'いる', 'ある', 'たち',
    'ない', 'なる', '人', 'その', '(', '"',
    ')', '.', '/', 'ー','そして', '年', '中',
    'そんな', '一','2', '二', 'それ', 'この',
    '1', '3', '第', 'できる'
]
stop_words += [
    '監督','アニメーション','メンバー','エピソード','スタッフ',''
]
stop_word_regex = [ re.compile("^[!?]+$") ]

get_word = [v[1] for v in vocab_list if v[0] > 3 and not is_stop(v)]


# In[100]:


items = {'id': [],'title': [] ,'outline': []}

for item in data:
    items['id'].append(item['id'])
    items['title'].append(item['title'])
    base = []
    for token in item["tokens"]:
        if token.base not in get_word:
            continue
        base.append(token.base)
    items['outline'].append(' '.join(base))


# In[101]:


tfidf_fit = tfidf.fit(items['outline'])
tfidf_transform = tfidf.transform(items['outline'])


# In[102]:


print(tfidf_transform.shape)


# In[103]:


cos_sim = cosine_similarity(tfidf_transform, tfidf_transform)


# In[120]:


def recommend(target):
    cursor.execute("SELECT id FROM animes where title = %s", [target])
    target_data = cursor.fetchone()
    target_id = target_data["id"]
    print(target_id)
    sim_items_idx = cos_sim_ex[target_id].argsort()[::-1][:20]
    print("タイトル " + items['title'][target_id])
    print(items['outline'][target_id])
    print("id " + str(items["id"][target_id]))
    for idx in sim_items_idx[1:]:
        print('------------------------------------')
        print(items['title'][idx])
        print(items['outline'][idx])
        print(items["id"][idx])


# In[121]:


recommend("のんのんびより")


# In[ ]:




