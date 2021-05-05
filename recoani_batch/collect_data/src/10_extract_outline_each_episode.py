from bs4 import BeautifulSoup
from time import sleep
import mysql.connector as mydb
import os
import re
import json

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

# 存在しなかった場合INSERT
def register_to_outline_each_episode(anime_id, episode_number, outline, json, part_id):
  try:
      query = """
        INSERT INTO outline_each_episode
        (anime_id, episode_number, outline, json, part_id)
        SELECT %(anime_id)s, %(episode_number)s, %(outline)s, %(json)s, %(part_id)s FROM DUAL
        WHERE NOT EXISTS (SELECT * FROM outline_each_episode
        WHERE part_id = %(part_id)s LIMIT 1)
        """
      cursor.execute(query, {'anime_id': anime_id, 'episode_number': episode_number, 'outline': outline, 'json': json, 'part_id': part_id})
      connection.commit()
  except Exception as e:
      connection.rollback()
      raise e

def update_status(anime_id):
  try:
      query = """
        UPDATE animes
        SET status = 8
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
  cursor.execute("SELECT id,html,status,work_id FROM animes WHERE id <= {} + 300 AND id >= {}".format(i,i))
  i = i + 300
  animes = cursor.fetchall()
  if len(animes) == 0:
    break

  for anime in animes:
    if anime[2] >= 8:
      continue
    anime_id = anime[0]
    target_page_soup = BeautifulSoup(anime[1], "html.parser")
    targets = []
    if target_page_soup.find_all("script", {"type": "application/ld+json"}) is not None:
      targets = target_page_soup.find_all("script", {"type": "application/ld+json"})
    
    # jsonから各話あらすじを取得
    for target in targets:
      json_data = json.loads(get_text(target), strict=False)
      
      # あらすじ取得
      outline = ""
      if type(json_data)==list:
        continue    
      elif "video" in json_data.keys():
        outline = json_data["video"]["description"]
      elif "description" in json_data.keys():
        outline = json_data["description"]
      
      outline = re.search('(?<=』).+?($)', outline)
      outline = outline.group() if outline is not None else None
      # &ldquo; &rdquo; &hellip; 除去
      outline = outline.replace("&ldquo;","").replace("&rdquo;","").replace("&hellip;","") if outline is not None else None

      if not outline: continue

      # 話数取得
      part_id = ""
      episode_id = ""
      if "@id" in json_data.keys():
        part_id = json_data["@id"]
        episode_number = part_id.replace(str(anime[3]),"")

      register_to_outline_each_episode(anime_id, episode_number, outline, str(json_data), part_id)

    update_status(anime_id)

print("10完了\n")

cursor.close()
connection.close()