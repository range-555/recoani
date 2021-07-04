import chromedriver_binary
import mysql.connector as mydb
import os
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


# main
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

connection.cursor.execute("SELECT id,url,status FROM animes")
animes = connection.cursor.fetchall()

for anime in animes:
    if anime[2] >= 1:
        continue
    sleep(1)
    driver.get(anime[1])
    driver = scroll_to_bottom(driver)
    html = driver.page_source
    connection.execute_query("update_animes_html", {"id": anime[0], "html": html})
    print(anime[0])

print("03完了\n")

del connection
