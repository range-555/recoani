import urllib.request as req
from urllib import parse
from bs4 import BeautifulSoup
from time import sleep
import mysql.connector as mydb
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import chromedriver_binary 
import os

connection = mydb.connect(
  host = os.environ.get('ml_db_host'),
  port = os.environ.get('local_port'),
  user = os.environ.get('recoani_user'),
  password = os.environ.get('recoani_pass'),
  database = os.environ.get('recoani_db')
)

cursor = connection.cursor()

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

def register_to_tmp_table(work_id, is_ongoing):
    try:
        query = """
          INSERT INTO tmp_table
          (work_id, is_ongoing)
          VALUES (%(work_id)s, %(is_ongoing)s)
          """
        cursor.execute(query, {'work_id': work_id, 'is_ongoing': is_ongoing})
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e

def update_animes(html, work_id, is_ongoing):
    try:
        query = """
          UPDATE animes
          SET html = %(html)s,
          status = 7,
          is_ongoing = %(is_ongoing)s
          WHERE work_id = %(work_id)s
          """
        cursor.execute(query, {'html': html, 'work_id': work_id, 'is_ongoing': is_ongoing})
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e

# main

# retrieveで取得したデータ用一時テーブル
cursor.execute("CREATE TEMPORARY TABLE tmp_table (work_id INT, is_ongoing INT)")

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
driver.set_window_size(1000,2000)
driver.find_element_by_css_selector(".tvnewlink").click()

driver = scroll_to_bottom(driver)
html = driver.page_source
driver.close()
target_page_soup = BeautifulSoup(html, "html.parser")

new_contents = target_page_soup.select_one("#newContents")
new_contents = new_contents.select(".itemModule")
for new_content in new_contents:
  register_to_tmp_table(new_content["data-workid"], 2)

keep_contents = target_page_soup.select_one("#keepContents")
keep_contents = keep_contents.select(".itemModule")
for keep_content in keep_contents:
  register_to_tmp_table(keep_content["data-workid"], 1)

print("更新終了")
# 更新終了アニメ status:7 is_ongoing:0
cursor.execute("""
  SELECT work_id FROM animes
  WHERE is_ongoing >= 1
  AND work_id NOT IN (
    SELECT work_id FROM tmp_table
  )
  """)

anime_end_update_list = cursor.fetchall()
for anime_end_update in anime_end_update_list:
  work_id = anime_end_update[0]
  sleep(1)
  driver = webdriver.Chrome(options=options)
  target_url = "https://anime.dmkt-sp.jp/animestore/ci_pc?workId=" + str(work_id)
  driver.get(target_url)
  scroll_to_bottom(driver)
  html = driver.page_source
  update_animes(html, work_id, 0)
  driver.close()

print("今期")
# 今期アニメ status:7 is_ongoing:2
cursor.execute("""
  SELECT work_id FROM tmp_table
  WHERE is_ongoing = 2
  """)

anime_now_content_list = cursor.fetchall()
for anime_now_content in anime_now_content_list:
  work_id = anime_now_content[0]
  sleep(1)
  driver = webdriver.Chrome(options=options)
  target_url = "https://anime.dmkt-sp.jp/animestore/ci_pc?workId=" + str(work_id)
  driver.get(target_url)
  scroll_to_bottom(driver)
  html = driver.page_source
  update_animes(html, work_id, 2)
  driver.close()

print("継続")
# 継続アニメ status:7 is_ongoing:1
cursor.execute("""
  SELECT work_id FROM tmp_table
  WHERE is_ongoing = 1
  """)

anime_keep_content_list = cursor.fetchall()
for anime_keep_content in anime_keep_content_list:
  work_id = anime_keep_content[0]
  sleep(1)
  driver = webdriver.Chrome(options=options)
  target_url = "https://anime.dmkt-sp.jp/animestore/ci_pc?workId=" + str(work_id)  
  driver.get(target_url)
  scroll_to_bottom(driver)
  html = driver.page_source
  update_animes(html, work_id, 1)
  driver.close()

print("11完了\n")

cursor.close()
connection.close()