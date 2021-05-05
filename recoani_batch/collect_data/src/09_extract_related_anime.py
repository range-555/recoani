from bs4 import BeautifulSoup
from time import sleep
import mysql.connector as mydb
import os
import re

connection = mydb.connect(
  host = os.environ.get('ml_db_host'),
  port = os.environ.get('local_port'),
  user = os.environ.get('recoani_user'),
  password = os.environ.get('recoani_pass'),
  database = os.environ.get('recoani_db')
)

cursor = connection.cursor(buffered=True)

def get_text(x):
  return x.text if x is not None else None

def register_to_related_animes(anime_id, related_anime_id):
  try:
      query = """
        INSERT INTO related_animes
        (anime_id, related_anime_id)
        VALUES (%(anime_id)s, %(related_anime_id)s)
        """
      cursor.execute(query, {'anime_id': anime_id, 'related_anime_id': related_anime_id})
      connection.commit()
  except Exception as e:
      connection.rollback()
      raise e

def update_status(anime_id):
  try:
      query = """
        UPDATE animes
        SET status = 7
        WHERE id = %(anime_id)s
        """
      cursor.execute(query, {'anime_id': anime_id})
      connection.commit()
  except Exception as e:
      connection.rollback()
      raise e

# main
i = 0

while True:
  cursor.execute("SELECT id,html,status FROM animes WHERE id <= {} + 300 AND id >= {}".format(i,i))
  i = i + 300
  animes = cursor.fetchall()
  if len(animes) == 0:
    break

  for anime in animes:
    if anime[2] >= 7:
      continue
    anime_id = anime[0]
    target_page_soup = BeautifulSoup(anime[1], "html.parser")
    related_animes = []
    if target_page_soup.select(".relationSwiper") is not None:
      related_animes = target_page_soup.select(".relationSwiper > .itemWrapper > .itemModule")
    for related_anime in related_animes:
      related_anime_url = related_anime.select_one("a")["href"]
      related_anime_work_id = re.search('.*(?<=Id=)(.+?)$', related_anime_url)
      related_anime_work_id = related_anime_work_id.group(1) if related_anime_work_id is not None else None
      cursor.execute("SELECT id FROM animes WHERE work_id = '{related_anime_work_id}' LIMIT 1".format(related_anime_work_id=related_anime_work_id))
      related_anime_id = cursor.fetchone()
      register_to_related_animes(anime_id,related_anime_id[0])

    update_status(anime_id)

print("09完了\n")

cursor.close()
connection.close()