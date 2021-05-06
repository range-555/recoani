from bs4 import BeautifulSoup
from time import sleep
import mysql.connector as mydb
import os
import re

connection = mydb.connect(
    host = os.environ.get('recoani_host'),
    port = os.environ.get('recoani_port'),
    user = os.environ.get('recoani_user'),
    password = os.environ.get('recoani_pass'),
    database = os.environ.get('recoani_db')
)

cursor = connection.cursor(buffered=True)

def get_text(x):
  return x.text if x is not None else None

def register_to_anime_genre(anime_id, genre_id):
  try:
      query = """
        INSERT INTO anime_genre
        (anime_id, genre_id)
        VALUES (%(anime_id)s, %(genre_id)s)
        """
      cursor.execute(query, {'anime_id': anime_id, 'genre_id': genre_id})
      connection.commit()
  except Exception as e:
      connection.rollback()
      raise e

# genresに存在しない場合INSERT
def register_to_genres(genre_cd, genre):
  try:
      query = """
        INSERT INTO genres
        (genre_cd, genre) 
        SELECT %(genre_cd)s, %(genre)s FROM DUAL
        WHERE NOT EXISTS (SELECT * FROM genres
        WHERE genre_cd=%(genre_cd)s LIMIT 1)
        """
      cursor.execute(query, {'genre_cd': genre_cd, 'genre': genre})
      connection.commit()
  except Exception as e:
      connection.rollback()
      raise e

def update_status(anime_id):
  try:
      query = """
        UPDATE animes
        SET status = 6
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
    if anime[2] >= 6:
      continue
    anime_id = anime[0]
    target_page_soup = BeautifulSoup(anime[1], "html.parser")
    genre_elms = []
    if target_page_soup.select(".outlineContainer > .footerLink > a") is not None:
      genre_elms = target_page_soup.select(".outlineContainer > .footerLink > a")
    for genre_elm in genre_elms:
      genre_cd = genre_elm["href"]
      genre_cd = re.search('.*(?<=Cd=)(.+?)$', genre_cd)
      genre_cd = genre_cd.group(1) if genre_cd is not None else None
      genre = get_text(genre_elm)
      register_to_genres(genre_cd, genre)
      cursor.execute("SELECT id FROM genres WHERE genre_cd = '{genre_cd}' LIMIT 1".format(genre_cd=genre_cd))
      genre_id = cursor.fetchone()
      register_to_anime_genre(anime_id, genre_id[0])

    update_status(anime_id)

print("08完了\n")

cursor.close()
connection.close()