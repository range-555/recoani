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

def register_to_anime_staff(anime_id, staff_id):
  try:
      query = """
        INSERT INTO anime_staff
        (anime_id, staff_id)
        VALUES (%(anime_id)s, %(staff_id)s)
        """
      cursor.execute(query, {'anime_id': anime_id, 'staff_id': staff_id})
      connection.commit()
  except Exception as e:
      connection.rollback()
      raise e

# staffsに存在しない場合INSERT
def register_to_staffs(tag_id, staff_name):
  try:
      query = """
        INSERT INTO staffs
        (tag_id, name) 
        SELECT %(tag_id)s, %(staff_name)s FROM DUAL
        WHERE NOT EXISTS (SELECT * FROM staffs
        WHERE tag_id=%(tag_id)s LIMIT 1)
        """
      cursor.execute(query, {'tag_id': tag_id, 'staff_name': staff_name})
      connection.commit()
  except Exception as e:
      connection.rollback()
      raise e

def update_status(anime_id):
  try:
      query = """
        UPDATE animes
        SET status = 4
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
    if anime[2] >=4:
      continue
    anime_id = anime[0]
    target_page_soup = BeautifulSoup(anime[1], "html.parser")
    staffs = []
    if target_page_soup.find(class_ = "tagCaption", text="スタッフ") is not None:
      staffs = target_page_soup.find(class_ = "tagCaption", text="スタッフ").findNext("ul").findAll("li")
    for staff in staffs:
      tag_id = staff.select_one("a")["href"]
      tag_id = re.search('.*(?<=Id=)(.+?)$', tag_id)
      tag_id = tag_id.group(1) if tag_id is not None else None
      staff_name = get_text(staff.select_one("a"))
      register_to_staffs(tag_id, staff_name)
      cursor.execute("SELECT id FROM staffs WHERE tag_id = '{tag_id}' LIMIT 1".format(tag_id=tag_id))
      staff_id = cursor.fetchone()
      register_to_anime_staff(anime_id, staff_id[0])

    update_status(anime_id)

print("06完了\n")

cursor.close()
connection.close()