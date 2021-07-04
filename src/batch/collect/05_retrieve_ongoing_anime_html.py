import chromedriver_binary
import mysql.connector as mydb
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep

from src.common.db.DBConnection import DBConnection


connection = DBConnection()


def scroll_to_bottom(driver):
    html_tmp_1 = driver.page_source
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        html_tmp_2 = driver.page_source
        if html_tmp_1 != html_tmp_2:
            html_tmp_1 = html_tmp_2
        else:
            return driver


def _update_ongoing_anime_html(anime, is_ongiong, connection):
    work_id = anime[0]
    sleep(1)
    driver = webdriver.Chrome(options=options)
    target_url = "https://anime.dmkt-sp.jp/animestore/ci_pc?workId=" + str(work_id)
    driver.get(target_url)
    scroll_to_bottom(driver)
    html = driver.page_source
    connection.execute_query("update_animes_html_is_ongoing",
                             {'html': html, 'work_id': work_id, 'is_ongoing': is_ongiong})
    driver.close()

# main


# retrieveで取得したデータ用一時テーブル
connection.cursor.execute("CREATE TEMPORARY TABLE tmp_table (work_id INT, is_ongoing INT)")

options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--start-maximized")
options.add_argument('--headless')
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("disable-infobars")

driver = webdriver.Chrome(options=options)

target_url = "https://anime.dmkt-sp.jp/animestore/tp_pc"

sleep(1)
driver.get(target_url)
driver.set_window_size(1000, 2000)
driver.find_element_by_css_selector(".tvnewlink").click()

driver = scroll_to_bottom(driver)
html = driver.page_source
driver.close()
target_page_soup = BeautifulSoup(html, "html.parser")

new_contents = target_page_soup.select_one("#newContents")
new_contents = new_contents.select(".itemModule")
for new_content in new_contents:
    connection.execute_query("insert_into_tmp_table_work_id_and_is_ongoing",
                             {'work_id': new_content["data-workid"], 'is_ongoing': 2})

keep_contents = target_page_soup.select_one("#keepContents")
keep_contents = keep_contents.select(".itemModule")
for keep_content in keep_contents:
    connection.execute_query("insert_into_tmp_table_work_id_and_is_ongoing",
                             {'work_id': new_content["data-workid"], 'is_ongoing': 1})


print("更新終了アニメ")
# 更新終了アニメ status:7 is_ongoing:0
connection.execute_query("select_work_id_from_animes_end_update")
anime_end_update_list = connection.cursor.fetchall()

for anime_end_update in anime_end_update_list:
    _update_ongoing_anime_html(anime_end_update, 0, connection)


print("今期アニメ")
# 今期アニメ status:7 is_ongoing:2
connection.cursor.execute("SELECT work_id FROM tmp_table WHERE is_ongoing = 2")
anime_now_content_list = connection.cursor.fetchall()

for anime_now_content in anime_now_content_list:
    _update_ongoing_anime_html(anime_now_content, 2, connection)


print("継続アニメ")
# 継続アニメ status:7 is_ongoing:1
connection.cursor.execute("SELECT work_id FROM tmp_table WHERE is_ongoing = 1")
anime_keep_content_list = connection.cursor.fetchall()

for anime_keep_content in anime_keep_content_list:
    _update_ongoing_anime_html(anime_keep_content, 1, connection)


print("11完了\n")

del connection
