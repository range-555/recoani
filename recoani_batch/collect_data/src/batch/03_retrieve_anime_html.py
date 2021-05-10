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
    host = os.environ.get('recoani_host'),
    port = os.environ.get('recoani_port'),
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

def register_to_animes(id, html):
  try:
      query = """
        UPDATE animes
        SET html = %(html)s,
        status = 1
        where id = %(id)s
        """
      cursor.execute(query, {'id': id, 'html': html})
      connection.commit()
  except Exception as e:
      connection.rollback()

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

cursor.execute("SELECT id,url,status FROM animes")
animes = cursor.fetchall()

for anime in animes:
  if anime[2] >= 1:
    continue
  sleep(1)
  driver.get(anime[1])
  driver = scroll_to_bottom(driver)
  html = driver.page_source
  register_to_animes(anime[0], html)
  print(anime[0])

print("03完了\n")

cursor.close()
connection.close()