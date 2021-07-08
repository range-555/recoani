import mysql.connector as mydb
import os


# 命名 ##########################################################
# select_{column(カラム1個) or "data"}_from_{tablename}_{その他説明}
# insert_into_{tablename}_{column(カラム1個) or "data"}_{その他説明}
# update_{tablename}_{column(カラム1個) or "data")}
################################################################
query = {
    #############################
    # collect 01
    #############################
    # anime_list_page
    "insert_into_anime_list_pages_html":
        """
        INSERT INTO anime_list_pages
        (initial, html)
        VALUES (%(initial)s, %(html)s)
        ON DUPLICATE KEY UPDATE
        html = %(html)s
        """,
    #############################
    # collect 02
    #############################
    # tmp_tableにデータを挿入
    "insert_into_tmp_table_data":
        """
        INSERT INTO tmp_table
        (title, url, work_id)
        VALUES (%(title)s, %(url)s, %(work_id)s)
        """,
    # 配信終了アニメのwork_idを取得
    "select_work_id_from_animes_end_delivery":
        """
        SELECT work_id FROM animes
        WHERE work_id NOT IN (
        SELECT work_id FROM tmp_table
        )
        """,
    # 配信終了アニメのis_deliveryを0に
    "update_animes_is_delivery_to_0":
        """
        UPDATE animes
        SET is_delivery = 0
        WHERE work_id = %(work_id)s
        """,
    # 新規配信アニメのwork_idを取得
    "select_data_from_tmp_dable_new_delivery":
        """
        SELECT title,url,work_id FROM tmp_table
        WHERE work_id NOT IN (
        SELECT work_id FROM animes
        )
        """,
    # 新規配信アニメのデータを挿入
    "insert_into_animes_data_new_delivery":
        """
        INSERT INTO animes
        (title, url, work_id)
        SELECT %(title)s, %(url)s, %(work_id)s FROM DUAL
        WHERE NOT EXISTS (SELECT * FROM animes
        WHERE work_id=%(work_id)s)
        """,
    # 配信再開アニメのwork_idを取得
    "select_work_id_from_tmp_table_re_delivery":
        """
        SELECT work_id FROM tmp_table
        WHERE work_id IN (
        SELECT work_id FROM animes
        WHERE is_delivery = 0
        )
        """,
    # 配信再開アニメのis_deliveryを1に
    "update_animes_is_delivery_to_1":
        """
        UPDATE animes
        SET is_delivery = 1
        WHERE work_id = %(work_id)s
        """,
    #############################
    # collect 03
    #############################
    "update_animes_html":
        """
        UPDATE animes
        SET html = %(html)s,
        status = 1
        where id = %(id)s
        """,
    #############################
    # collect 04
    #############################
    # animesのステータスを更新
    "update_animes_status":
        """
        UPDATE animes
        SET status = %(status)s
        WHERE id = %(anime_id)s
        """,
    # アニメの基本データを更新
    "update_animes_basic_data":
        """
        UPDATE animes
        SET outline_entire = %(outline_entire)s,
        favorite = %(favorite)s,
        producted_year = %(producted_year)s,
        thumbnail_url = %(thumbnail_url)s,
        status = 2
        WHERE id = %(id)s
        """,
    # castsに存在していないデータであれば挿入
    "insert_into_casts_data_if_not_exist":
        """
        INSERT INTO casts
        (tag_id, name)
        SELECT %(tag_id)s, %(cast_name)s FROM DUAL
        WHERE NOT EXISTS (SELECT * FROM casts
        WHERE tag_id = %(tag_id)s LIMIT 1)
        """,
    # anime_castに紐付きを挿入
    "insert_into_anime_cast_data":
        """
        INSERT INTO anime_cast
        (anime_id, cast_id)
        VALUES (%(anime_id)s, %(cast_id)s)
        """,
    # staffsに存在していないデータであれば挿入
    "insert_into_staffs_data_if_not_exist":
        """
        INSERT INTO staffs
        (tag_id, name)
        SELECT %(tag_id)s, %(staff_name)s FROM DUAL
        WHERE NOT EXISTS (SELECT * FROM staffs
        WHERE tag_id=%(tag_id)s LIMIT 1)
        """,
    # anime_staffに紐付きを挿入
    "insert_into_anime_staff_data":
        """
        INSERT INTO anime_staff
        (anime_id, staff_id)
        VALUES (%(anime_id)s, %(staff_id)s)
        """,
    # other_informationsに存在していないデータであれば挿入
    "insert_into_other_informations_data_if_not_exist":
        """
        INSERT INTO other_informations
        (tag_id, other_information)
        SELECT %(tag_id)s, %(other_information)s FROM DUAL
        WHERE NOT EXISTS (SELECT * FROM other_informations
        WHERE tag_id= %(tag_id)s LIMIT 1)
        """,
    # anime_other_informationに紐付きを挿入
    "insert_into_anime_other_information_data":
        """
        INSERT INTO anime_other_information
        (anime_id, other_information_id)
        VALUES (%(anime_id)s, %(other_information_id)s)
        """,
    # genresに存在していないデータであれば挿入
    "insert_into_genres_data_if_not_exist":
        """
        INSERT INTO genres
        (genre_cd, genre)
        SELECT %(genre_cd)s, %(genre)s FROM DUAL
        WHERE NOT EXISTS (SELECT * FROM genres
        WHERE genre_cd=%(genre_cd)s LIMIT 1)
        """,
    # anime_genreに紐付きを挿入
    "insert_into_anime_genre_data":
        """
        INSERT INTO anime_genre
        (anime_id, genre_id)
        VALUES (%(anime_id)s, %(genre_id)s)
        """,
    # related_animesに紐付きを挿入
    "insert_into_related_animes_data":
        """
        INSERT INTO related_animes
        (anime_id, related_anime_id)
        VALUES (%(anime_id)s, %(related_anime_id)s)
        """,
    # outline_each_episodeにあらすじを挿入
    "insert_into_outline_each_episode_data":
        """
        INSERT INTO outline_each_episode
        (anime_id, episode_number, outline, json, part_id)
        SELECT %(anime_id)s, %(episode_number)s, %(outline)s, %(json)s, %(part_id)s FROM DUAL
        WHERE NOT EXISTS (SELECT * FROM outline_each_episode
        WHERE part_id = %(part_id)s LIMIT 1)
        """,
    # 全文検索用タイトルカラムにタイトルをコピー
    "update_animes_title_full":
        """
        UPDATE animes
        SET title_full = title
        """,
    #############################
    # collect 05
    #############################
    "select_work_id_from_animes_end_update":
        """
        SELECT work_id FROM animes
        WHERE is_ongoing >= 1
        AND work_id NOT IN (
        SELECT work_id FROM tmp_table
        )
        """,
    "select_work_id_from_tmp_table_is_ongoing_2":
        """
        SELECT work_id FROM tmp_table
        WHERE is_ongoing = 2
        """,
    "select_work_id_from_tmp_table_is_ongoing_1":
        """
        SELECT work_id FROM tmp_table
        WHERE is_ongoing = 1
        """,
    "update_animes_html_and_is_ongoing":
        """
        UPDATE animes
        SET html = %(html)s,
        status = 7,
        is_ongoing = %(is_ongoing)s
        WHERE work_id = %(work_id)s
        """,
    "insert_into_tmp_table_work_id_and_is_ongoing":
        """
        INSERT INTO tmp_table
        (work_id, is_ongoing)
        VALUES (%(work_id)s, %(is_ongoing)s)
        """,
    #############################
    # calc
    #############################
    "update_animes_recommend_list":
        """
        UPDATE animes
        SET recommend_list = %(recommend_list)s
        WHERE id = %(id)s
        """
}


class DBConnection:
    def __init__(self, is_calc=None):
        try:
            self.connection = mydb.connect(
                host=os.environ.get('RECOANI_HOST'),
                port=os.environ.get('RECOANI_PORT'),
                user=os.environ.get('RECOANI_USER'),
                password=os.environ.get('RECOANI_PASSWORD'),
                database=os.environ.get('RECOANI_DB')
            )
            self.connection.autocommit = False
            if is_calc:
                self.cursor = self.connection.cursor(buffered=True, dictionary=True)
            else:
                self.cursor = self.connection.cursor()
        except mydb.Error as e:
            print("[DBConnection Error] ", e)
            raise
        except Exception as e:
            print("[Error] ", e)
            raise

    # queryで定義済みのクエリを実行
    def execute_query(self, query_name, params=None):
        try:
            sql = query[query_name]
        except KeyError as e:
            print("[Key Error] ", e)
            raise
        try:
            self.cursor.execute(sql, params)
            if not query_name.startswith("select"):
                self.connection.commit()
        except mydb.Error as e:
            print("[SQL Excecution Error] ", e)
            if not sql.startswith("select"):
                self.connection.rollback()
            raise

    # DB接続終了
    def __del__(self):
        try:
            self.cursor.close()
            self.connection.close()
            print("Conncection Delete!!")
        except mydb.errors.ProgrammingError as e:
            print(e)
            raise
