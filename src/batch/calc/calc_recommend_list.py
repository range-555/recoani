from __future__ import unicode_literals
import MeCab
import mysql.connector as mydb
import os
import re
import time
import unicodedata
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

connection = mydb.connect(
    host=os.environ.get('recoani_host'),
    port=os.environ.get('recoani_port'),
    user=os.environ.get('recoani_user'),
    password=os.environ.get('recoani_pass'),
    database=os.environ.get('recoani_db')
)

# Tools
mecab = MeCab.Tagger()
stop_word = []
stop_word_regex = []
vocab_list = []
get_word = []
tfidf = TfidfVectorizer(
    max_df=0.5,
    min_df=1,
    max_features=1500,
    analyzer='word',
    ngram_range=(1, 1)
)


class Normalize:
    def __init__(self, sentence):
        self.sentence = sentence

    def normalize(self):
        return self.normalize_neologd()

    def unicode_normalize(self, cls, s):
        pt = re.compile('([{}]+)'.format(cls))

        def norm(c):
            return unicodedata.normalize('NFKC', c) if pt.match(c) else c

        s = ''.join(norm(x) for x in re.split(pt, s))
        s = re.sub('－', '-', s)
        return s

    def remove_extra_spaces(self, s):
        s = re.sub('[ 　]+', ' ', s)
        blocks = ''.join(('\u4E00-\u9FFF',  # CJK UNIFIED IDEOGRAPHS
                          '\u3040-\u309F',  # HIRAGANA
                          '\u30A0-\u30FF',  # KATAKANA
                          '\u3000-\u303F',  # CJK SYMBOLS AND PUNCTUATION
                          '\uFF00-\uFFEF'   # HALFWIDTH AND FULLWIDTH FORMS
                          ))
        basic_latin = '\u0000-\u007F'

        def remove_space_between(cls1, cls2, s):
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


def tokenize(sentence, title):
    if len(sentence) < 10:
        return []

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


def create_vocab_list(data):
    vocab = {}
    for item in data:
        tokens = item['tokens']
        for token in tokens:
            key = token.base
            pos = token.pos
            v = vocab.get(key, {"count": 0, "pos": pos})
            v["count"] += 1
            vocab[key] = v

    for k in vocab:
        v = vocab[k]
        vocab_list.append((v["count"], k, v["pos"]))


def is_stop(vocab):
    return vocab[1] in stop_word or any([r for r in stop_word_regex if r.match(vocab[1]) is not None])


def update_recommend_list(id, recommend_list):
    try:
        query = """
          UPDATE animes
          SET recommend_list = %(recommend_list)s
          WHERE id = %(id)s
          """
        cursor.execute(query, {'id': id, 'recommend_list': recommend_list})
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e


time_start = time.perf_counter()

cursor = connection.cursor(buffered=True, dictionary=True)
cursor.execute("SELECT id, title, outline_entire FROM animes")
data = cursor.fetchall()

for item in data:
    item['tokens'] = tokenize(item['outline_entire'], item['title'])

create_vocab_list(data)
vocab_list = sorted(vocab_list, reverse=True)
vocab_list = [v for v in vocab_list if not ("助詞" in v[2] or "記号" in v[2] or "助動詞" in v[2] or "接続詞" in v[2])]

stop_word += ['する', 'れる', 'いる', 'ある', 'たち',
              'ない', 'なる', '人', 'その', '(', '"',
              ')', '.', '/', 'ー', 'そして', '年', '中',
              'そんな', '一', '2', '二', 'それ', 'この',
              '1', '3', '第', 'できる', 'させる']
stop_word += [
    '監督', 'アニメーション', 'メンバー', 'エピソード', 'スタッフ', '時代',
]
stop_word_regex = [re.compile("^[!?]+$")]

get_word = [v[1] for v in vocab_list if v[0] > 3 and not is_stop(v)]

items = {'id': [], 'title': [], 'outline': []}

for item in data:
    items['id'].append(item['id'])
    items['title'].append(item['title'])
    base = []
    for token in item["tokens"]:
        if token.base not in get_word:
            continue
        base.append(token.base)
    items['outline'].append(' '.join(base))

tfidf_fit = tfidf.fit(items['outline'])
tfidf_transform = tfidf.transform(items['outline'])

cos_sim = cosine_similarity(tfidf_transform, tfidf_transform)

print("登録")
for item in data:
    id = item['id']
    target_id = id - 1
    sim_items_idx = cos_sim[target_id].argsort()[::-1][:35]
    recommend_list = []
    rank = 1
    for idx in sim_items_idx[1:]:
        if items['title'][idx] == item['title']:
            continue
        recommend_elm = {"id": items['id'][idx], "sim": cos_sim[target_id][idx], "rank": rank}
        recommend_list.append(recommend_elm)
        rank += 1
    recommend_list = json.dumps(recommend_list)
    update_recommend_list(id, recommend_list)
    if id % 100 == 0:
        print(time.perf_counter())

print("実行完了 " + str(time.perf_counter() - time_start) + "秒")
