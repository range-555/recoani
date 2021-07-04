import json
import mysql.connector as mydb
import os
import re
from bs4 import BeautifulSoup

from src.common.db.DBConnection import DBConnection
from src.common.extract import extract


connection = DBConnection()


# メモリ不足対策に100件ずつ処理している メモリに問題がないなら一括で良い
i = 0
while True:
    connection.cursor.execute("SELECT id,html,status FROM animes WHERE id <= %(i)s + 300 AND id >= %(i)s", {"i": i})
    animes = connection.cursor.fetchall()
    i = i + 100
    if len(animes) == 0:
        break
    for anime in animes:
        anime_id = anime[0]  # DB内でのアニメのid このidと別にwork_id(dアニメ上のid)が別に存在
        html = anime[1]
        soup = BeautifulSoup(anime[1], "html.parser")
        status = anime[2]  # どこまでデータ取得したかのステータス変数
        # basic_data
        if status == 1:
            params = extract.basic_data(anime_id, soup)
            connection.execute_query("update_animes_basic_data", params)
            status = 2
        # cast
        if status == 2:
            cast_ids = extract.cast_ids(soup)
            for cast_id in cast_ids:
                # anime_castにinsert(アニメとキャストの紐付き)
                connection.execute_query("insert_into_anime_cast_data", {'anime_id': anime_id, 'cast_id': cast_id})
            connection.execute_query("update_animes_status", {"status": 3, "anime_id": anime_id})
            status = 3
        # staff
        if status == 3:
            staff_ids = extract.staff_ids(soup)
            for staff_id in staff_ids:
                # anime_staffにinsert(アニメとスタッフの紐付き)
                connection.execute_query("insert_into_anime_staff_data", {'anime_id': anime_id, 'staff_id': staff_id})
            connection.execute_query("update_animes_status", {"status": 4, "anime_id": anime_id})
            status = 4
        # other_information
        if status == 4:
            other_information_ids = extract.other_information_ids(soup)
            for other_information_id in other_information_ids:
                # anime_staffにinsert(アニメとスタッフの紐付き)
                connection.execute_query("insert_into_anime_other_information_data", {'anime_id': anime_id, 'other_information_id': other_information_id})
            connection.execute_query("update_animes_status", {"status": 5, "anime_id": anime_id})
            status = 5
        # genre
        if status == 5:
            genre_cds = extract.genre_cds(soup)
            for genre_cd in genre_cds:
                # anime_staffにinsert(アニメとスタッフの紐付き)
                connection.execute_query("insert_into_anime_genre_data", {'anime_id': anime_id, 'genre_cd': genre_cd})
            connection.execute_query("update_animes_status", {"status": 5, "anime_id": anime_id})
            status = 6
        # related_anime
        if status == 6:
            related_anime_ids = extract.related_anime_ids(soup)
            for related_anime_id in related_anime_ids:
                # related_animesにinsert(関連アニメ)
                connection.execute_query("insert_into_related_animes_data", {'anime_id': anime_id, 'related_anime_id': related_anime_id})
            connection.execute_query("update_animes_status", {"status": 7, "anime_id": anime_id})
            status = 7
        # outline_each_episode
        if status == 7:
            outline_jsons = extract.outline_jsons(soup)
            # idからwork_idを取得
            connection.cursor.execute("SELECT work_id FROM animes WHERE id = %(anime_id)s LIMIT 1", {"anime_id": anime_id})
            anime_work_id = connection.cursor.fetchone()
            # 各話あらすじを取得
            for outline_json in outline_jsons:
                params = extract.outline_params_from_json(outline_json, anime_work_id)
                if params is None:
                    continue
                params["anime_id"] = anime_id
                connection.execute_query("insert_into_outline_each_episode_data", params)

            connection.execute_query("update_animes_status", {"status": 8, "anime_id": anime_id})
            status = 8


# 全文検索用のカラムにタイトルをコピー
connection.execute_query("update_animes_title_full")

del connection
