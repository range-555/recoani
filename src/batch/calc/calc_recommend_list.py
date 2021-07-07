from __future__ import unicode_literals
import MeCab
import time
import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.common.db.DBConnection import DBConnection
from src.batch.calc.morph import Morph
from src.batch.calc.mytokenize import mytokenize


def main():
    connection = DBConnection(1)
    tfidf = TfidfVectorizer(
        max_df=0.5,
        min_df=1,
        max_features=1500,
        analyzer='word',
        ngram_range=(1, 1)
    )

    connection.cursor.execute("SELECT id, title, outline_entire FROM animes")
    animes = connection.cursor.fetchall()

    for item in animes:
        item['tokens'] = mytokenize(item['outline_entire'], item['title'])

    get_word = _create_get_word(animes)

    items = _arrange_data(animes, get_word)

    # fit_transform?
    # https://stackoverflow.com/questions/53027864/what-is-the-difference-between-tfidfvectorizer-fit-transfrom-and-tfidf-transform
    # tfidf_fit = tfidf.fit(items['outline'])
    # tfidf_transform = tfidf.transform(items['outline'])
    tfidf_transform = tfidf.fit_transform(items['outline'])

    cos_sim = cosine_similarity(tfidf_transform, tfidf_transform)

    for item in animes:
        print(item['title'])
        _update_recommend_list(item, items, cos_sim, connection)

    print("calc 完了\n")

    del connection


def _arrange_data(animes, get_word):
    items = {'id': [], 'title': [], 'outline': []}
    for item in animes:
        items['id'].append(item['id'])
        items['title'].append(item['title'])
        base = []
        for token in item["tokens"]:
            if token.base not in get_word:
                continue
            base.append(token.base)
        items['outline'].append(' '.join(base))

    return items


def _create_get_word(animes):
    vocab_list = _create_vocab_list(animes)
    vocab_list = sorted(vocab_list, reverse=True)
    vocab_list = [v for v in vocab_list if not ("助詞" in v[2] or "記号" in v[2] or "助動詞" in v[2] or "接続詞" in v[2])]

    stop_word = _stop_word_list()
    stop_word_regex = [re.compile("^[!?]+$")]

    get_word = [v[1] for v in vocab_list if v[0] > 3 and not _is_stop(v, stop_word, stop_word_regex)]

    return get_word


def _create_vocab_list(animes):
    vocab = {}
    vocab_list = []

    for item in animes:
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

    return vocab_list


def _is_stop(vocab, stop_word, stop_word_regex):
    return vocab[1] in stop_word or any([r for r in stop_word_regex if r.match(vocab[1]) is not None])


def _stop_word_list():
    stop_word = []
    # 一般的な単語は除去
    stop_word += ['する', 'れる', 'いる', 'ある', 'たち',
                  'ない', 'なる', '人', 'その', '(', '"',
                  ')', '.', '/', 'ー', 'そして', '年', '中',
                  'そんな', '一', '2', '二', 'それ', 'この',
                  '1', '3', '第', 'できる', 'させる']
    # アニメに共通しそうな単語は除去
    stop_word += [
        '監督', 'アニメーション', 'メンバー', 'エピソード', 'スタッフ', '時代',
    ]

    return stop_word


def _update_recommend_list(item, items, cos_sim, connection):
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
    print(recommend_list)
    connection.execute_query("update_animes_recommend_list", {'id': id, 'recommend_list': recommend_list})


if __name__ == "__main__":
    main()
