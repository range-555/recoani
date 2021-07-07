from bs4 import BeautifulSoup

from src.common.db.DBConnection import DBConnection
from src.common.extract import extract


def main():
    connection = DBConnection()

    connection.cursor.execute("SELECT html FROM anime_list_pages")
    anime_list_htmls = connection.cursor.fetchall()
    connection.cursor.execute("CREATE TEMPORARY TABLE tmp_table (title varchar(255), url varchar(255), work_id INT)")

    # 01でクロールした時点で存在する全アニメをtmp_tableに追加
    for anime_list_html in anime_list_htmls:
        soup = BeautifulSoup(anime_list_html[0], "html.parser")
        anime_list = extract.anime_list(soup)
        for anime in anime_list:
            params = extract.anime_params(anime)
            connection.execute_query("insert_into_tmp_table_data", params)

    # 配信終了タイトル処理
    connection.execute_query("select_work_id_from_animes_end_delivery")
    anime_end_delivery_list = connection.cursor.fetchall()
    for anime_end_delivery in anime_end_delivery_list:
        connection.execute_query("update_animes_is_delivery_to_0", {"work_id": anime_end_delivery[0]})

    # 配信開始タイトル処理
    connection.cursor.execute("UPDATE animes SET is_new = 0")

    connection.execute_query("select_data_from_tmp_dable_new_delivery")
    anime_new_delivery_list = connection.cursor.fetchall()
    for anime_new_delivery in anime_new_delivery_list:
        # animesに存在しない場合INSERT
        connection.execute_query("insert_into_animes_data_new_delivery",
                                 {"title": anime_new_delivery[0], "url": anime_new_delivery[1], "work_id": anime_new_delivery[2]})

    # 配信再開タイトル処理
    connection.execute_query("select_work_id_from_tmp_table_re_delivery")
    anime_re_delivery_list = connection.cursor.fetchall()
    for anime_re_delivery in anime_re_delivery_list:
        connection.execute_query("update_animes_is_delivery_to_1", {"work_id": anime_re_delivery[0]})

    print("02完了\n")

    del connection


if __name__ == "__main__":
    main()
