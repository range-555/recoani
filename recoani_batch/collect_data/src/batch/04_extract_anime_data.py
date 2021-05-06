import mysql.connector as mydb
from bs4 import BeautifulSoup
import os
import re

connection = mydb.connect(
    host = os.environ.get('recoani_host'),
    port = os.environ.get('recoani_port'),
    user = os.environ.get('recoani_user'),
    password = os.environ.get('recoani_pass'),
    database = os.environ.get('recoani_db')
)

cursor = connection.cursor()

def register_to_animes(outline_entire, favorite, producted_year, thumbnail_url, id):
  try:
      query = """
        UPDATE animes
        SET outline_entire = %(outline_entire)s,
        favorite = %(favorite)s,
        producted_year = %(producted_year)s,
        thumbnail_url = %(thumbnail_url)s,        
        status = 2
        WHERE id = %(id)s
        """
      cursor.execute(query, {'outline_entire': outline_entire, 'favorite': favorite, 'producted_year': producted_year, 'thumbnail_url': thumbnail_url, 'id': id})
      connection.commit()
  except Exception as e:
      connection.rollback()

def get_text(x):
  return x.text if x is not None else None

# main
i = 0

while True:
  cursor.execute("SELECT id,html,status FROM animes WHERE id <= {} + 300 AND id >= {}".format(i,i))
  i = i + 300
  animes = cursor.fetchall()
  if len(animes) == 0:
    break

  for anime in animes:
    if anime[2] >= 2:
      continue
    id = anime[0]
    target_page_soup = BeautifulSoup(anime[1], "html.parser")
    # 全体あらすじ
    outline_entire = get_text(target_page_soup.select_one(".outlineContainer > p"))
    outline_entire = outline_entire.strip('\n') if outline_entire is not None else None
    # お気に入り数
    favorite = get_text(target_page_soup.select_one(".nonmemberFavoriteCount > span"))
    # 制作年
    cast_container = target_page_soup.select(".castContainer > p")
    producted_year = ''
    for ptag in cast_container:
      if '製作年' in ptag.text:
        producted_year = ptag.text.strip('\n')
        producted_year = re.search('([0-9]+)', producted_year)
        producted_year = producted_year.group() if producted_year is not None else None
    # サムネイル画像
    target_img = target_page_soup.select_one(".keyVisual")
    target_img = target_img.select_one("img")
    thumbnail_url = target_img["src"] if target_img is not None else None

    register_to_animes(outline_entire, favorite, producted_year, thumbnail_url, id)

print("04完了\n")

cursor.close()
connection.close()