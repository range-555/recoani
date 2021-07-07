from src.common.crawl.crawler import Crawler
from src.common.crawl import url_operation
from src.common.db.DBConnection import DBConnection


def main():
    crawler = Crawler()
    connection = DBConnection()
    target_url = "https://anime.dmkt-sp.jp/animestore/c_all_pc"
    # 子音あ〜わのループ
    for page in range(10):
        page += 1
        update_dict = {'initialCollectionKey': page, 'vodTypeList': 'svod_tvod'}
        target_url = url_operation.update_target_url(target_url, update_dict)
        crawler.get(target_url)

        # 母音あ〜おのループ
        for li in crawler.driver.find_elements_by_css_selector(".headerSubTab > ul > li"):
            link = li.find_element_by_css_selector("a")
            crawler.click(link)
            crawler.scroll_to_bottom()
            initial = link.text
            html = crawler.driver.page_source
            # initialをキーに、存在しない場合INSERT、存在した場合UPDATE
            connection.execute_query("insert_into_anime_list_pages_html", {"initial": initial, "html": html})
            print(initial)

    print("01完了\n")

    del crawler
    del connection


if __name__ == "__main__":
    main()
