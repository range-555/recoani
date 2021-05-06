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

def register_to_anime_other_information(anime_id, other_information_id):
  try:
      query = """
        INSERT INTO anime_other_information
        (anime_id, other_information_id)
        VALUES (%(anime_id)s, %(other_information_id)s)
        """
      cursor.execute(query, {'anime_id': anime_id, 'other_information_id': other_information_id})
      connection.commit()
  except Exception as e:
      connection.rollback()
      raise e

# other_informationsに存在しない場合INSERT
def register_to_other_informations(tag_id, other_information):
  try:
      query = """
        INSERT INTO other_informations
        (tag_id, other_information) 
        SELECT %(tag_id)s, %(other_information)s FROM DUAL
        WHERE NOT EXISTS (SELECT * FROM other_informations
        WHERE tag_id= %(tag_id)s LIMIT 1)
        """
      cursor.execute(query, {'tag_id': tag_id, 'other_information': other_information})
      connection.commit()
  except Exception as e:
      connection.rollback()
      raise e

def update_status(anime_id):
  try:
      query = """
        UPDATE animes
        SET status = 5
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
    if anime[2] >= 5:
      continue
    anime_id = anime[0]
    target_page_soup = BeautifulSoup(anime[1], "html.parser")
    other_informations = []
    if target_page_soup.find(class_ = "tagCaption", text="その他") is not None:
      other_informations = target_page_soup.find(class_ = "tagCaption", text="その他").findNext("ul").findAll("li")
    for other_information in other_informations:
      tag_id = other_information.select_one("a")["href"]
      tag_id = re.search('.*(?<=Id=)(.+?)$', tag_id)
      tag_id = tag_id.group(1) if tag_id is not None else None
      other_information = get_text(other_information.select_one("a"))
      register_to_other_informations(tag_id, other_information)
      cursor.execute("SELECT id FROM other_informations WHERE tag_id = '{tag_id}' LIMIT 1".format(tag_id=tag_id))
      other_information_id = cursor.fetchone()
      register_to_anime_other_information(anime_id, other_information_id[0])

    update_status(anime_id)

print("07完了\n")

cursor.close()
connection.close()