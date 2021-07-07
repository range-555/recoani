from bs4 import BeautifulSoup

from src.common.crawl.crawler import Crawler
from src.common.db.DBConnection import DBConnection


def main():
    crawler = Crawler()
    connection = DBConnection()

    # retrieveで取得したデータ用一時テーブル
    connection.cursor.execute("CREATE TEMPORARY TABLE tmp_table (work_id INT, is_ongoing INT)")

    crawler.get("https://anime.dmkt-sp.jp/animestore/tp_pc")
    crawler.driver.set_window_size(1000, 2000)
    link = crawler.driver.find_element_by_css_selector(".tvnewlink")
    crawler.click(link)
    crawler.scroll_to_bottom()
    html = crawler.driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    # 一時テーブルに今期アニメ、更新継続アニメを登録
    _register_contents_to_tmp_table(soup, "#newContents", 2, connection)
    _register_contents_to_tmp_table(soup, "#keepContents", 1, connection)

    # 更新終了アニメ status:7 is_ongoing:(1or2)->0
    query_name = "select_work_id_from_animes_end_update"
    _update_ongoing_anime_html(query_name, 0, crawler, connection)
    print("更新終了アニメ登録完了")

    # 今期アニメ status:7 is_ongoing:2
    query_name = "select_work_id_from_tmp_table_is_ongoing_2"
    _update_ongoing_anime_html(query_name, 2, crawler, connection)
    print("今期アニメ登録完了")

    # 更新継続アニメ status:7 is_ongoing:1
    query_name = "select_work_id_from_tmp_table_is_ongoing_1"
    _update_ongoing_anime_html(query_name, 1, crawler, connection)
    print("継続アニメ登録完了")

    print("11完了\n")

    del crawler
    del connection


if __name__ == "__main__":
    main()


def _register_contents_to_tmp_table(soup, css_id, is_ongoing, connection):
    contents = soup.select_one(css_id)
    contents = contents.select(".itemModule")
    for content in contents:
        connection.execute_query("insert_into_tmp_table_work_id_and_is_ongoing",
                                 {'work_id': content["data-workid"], 'is_ongoing': is_ongoing})


# htmlとis_ongoingを更新
def _update_ongoing_anime_html(query_name, is_ongiong, crawler, connection):
    connection.execute_query(query_name)
    anime_list = connection.cursor.fetchall()
    for anime in anime_list:
        work_id = anime[0]
        target_url = "https://anime.dmkt-sp.jp/animestore/ci_pc?workId=" + str(work_id)
        crawler.get(target_url)
        crawler.scroll_to_bottom()
        html = crawler.driver.page_source
        connection.execute_query("update_animes_html_is_ongoing",
                                 {'html': html, 'work_id': work_id, 'is_ongoing': is_ongiong})
