from urllib import parse
from time import sleep
from ..db.DBConnection import DBConnection
import mysql.connector as mydb
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

connection = mydb.connect(
    host=os.environ.get('recoani_host'),
    port=os.environ.get('recoani_port'),
    user=os.environ.get('recoani_user'),
    password=os.environ.get('recoani_pass'),
    database=os.environ.get('recoani_db')
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

# initialが存在しない場合INSERT、存在した場合UPDATE


def update_anime_list_pages(initial, html):
    try:
        query = """
        INSERT INTO anime_list_pages
        (initial, html)
        VALUES (%(initial)s, %(html)s)
        ON DUPLICATE KEY UPDATE
        html = %(html)s
        """
        cursor.execute(query, {'initial': initial, 'html': html})
        connection.commit()
    except Exception:
        connection.rollback()


def update_target_url(update_dict):
    parsed = parse.urlparse(target_url)
    query_dict = parse.parse_qs(parsed.query, True)
    query_dict.update(update_dict)
    query_string = parse.urlencode(query_dict, True)
    return parse.urlunparse(parsed._replace(query=query_string))


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

target_url = "https://anime.dmkt-sp.jp/animestore/c_all_pc"

for page in range(10):
    page += 1
    update_dict = {'initialCollectionKey': page, 'vodTypeList': 'svod_tvod'}
    target_url = update_target_url(update_dict)
    sleep(1)
    driver.get(target_url)
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
    except TimeoutException as te:
        raise te

    # 母音あ〜おまでループ
    for li in driver.find_elements_by_css_selector(".headerSubTab > ul > li"):
        sleep(1)
        li.find_element_by_css_selector("a").click()
        driver = scroll_to_bottom(driver)
        initial = li.find_element_by_css_selector("a").text
        html = driver.page_source
        update_anime_list_pages(initial, html)
        print(initial)

print("01完了\n")

driver.close()
driver.quit()

cursor.close()
connection.close()
