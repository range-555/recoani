from src.common.crawl.crawler import Crawler
from src.common.db.DBConnection import DBConnection


def main():
    crawler = Crawler()
    connection = DBConnection()

    connection.cursor.execute("SELECT id,url,status FROM animes")
    animes = connection.cursor.fetchall()

    for anime in animes:
        if anime[2] >= 1:
            continue
        crawler.get(anime[1])
        crawler.scroll_to_bottom()
        html = crawler.driver.page_source
        connection.execute_query("update_animes_html", {"id": anime[0], "html": html})
        print(anime[0])

    print("03完了\n")

    del crawler
    del connection


if __name__ == "__main__":
    main()
