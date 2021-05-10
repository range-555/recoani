import mysql.connector as mydb
from bs4 import BeautifulSoup
import os

connection = mydb.connect(
    host = os.environ.get('recoani_host'),
    port = os.environ.get('recoani_port'),
    user = os.environ.get('recoani_user'),
    password = os.environ.get('recoani_pass'),
    database = os.environ.get('recoani_db')
)

cursor = connection.cursor()

def get_text(x):
  return x.text if x is not None else None

# animesに存在しない場合INSERT
def register_to_animes(title, url, work_id):
  try:
      query = """
        INSERT INTO animes
        (title, url, work_id)
        SELECT %(title)s, %(url)s, %(work_id)s FROM DUAL
        WHERE NOT EXISTS (SELECT * FROM animes
        WHERE work_id=%(work_id)s)
        """
      cursor.execute(query, {'title': title, 'url': url, 'work_id': work_id})
      connection.commit()
  except Exception as e:
      connection.rollback()
      raise e

def register_to_tmp_table(title, url, work_id):
    try:
        query = """
          INSERT INTO tmp_table
          (title, url, work_id)
          VALUES (%(title)s, %(url)s, %(work_id)s)
          """
        cursor.execute(query, { 'title': title, 'url': url, 'work_id': work_id})
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e

def update_is_delivery_to_0(work_id):
    try:
        query = """
          UPDATE animes
          SET is_delivery = 0
          WHERE work_id = %(work_id)s
          """
        cursor.execute(query, { 'work_id': work_id})
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e

def update_is_delivery_to_1(work_id):
    try:
        query = """
          UPDATE animes
          SET is_delivery = 1
          WHERE work_id = %(work_id)s
          """
        cursor.execute(query, { 'work_id': work_id})
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e

# main
cursor.execute("SELECT html FROM anime_list_pages")
anime_list_htmls = cursor.fetchall()
cursor.execute("CREATE TEMPORARY TABLE tmp_table (title varchar(255), url varchar(255), work_id INT)")

for anime_list_html in anime_list_htmls:
  target_page_soup = BeautifulSoup(anime_list_html[0], "html.parser")
  anime_list = []
  anime_list = target_page_soup.select("[class='itemModule list']")
  for anime in anime_list:
    title = get_text(anime.select_one(".webkit2LineClamp"))
    url = anime.select_one(".itemModuleIn > a")["href"]
    work_id = anime["data-workid"]

    register_to_tmp_table(title, url, work_id)

# 配信終了タイトル処理
cursor.execute("""
  SELECT work_id FROM animes
  WHERE work_id NOT IN (
    SELECT work_id FROM tmp_table
  )
  """)
anime_end_delivery_list = cursor.fetchall()
for anime_end_delivery in anime_end_delivery_list:
  update_is_delivery_to_0(anime_end_delivery[0])
  
# 配信開始タイトル処理
cursor.execute("UPDATE animes SET is_new = 0")

cursor.execute("""
  SELECT title,url,work_id FROM tmp_table
  WHERE work_id NOT IN (
    SELECT work_id FROM animes
  )
  """)
anime_new_delivery_list = cursor.fetchall()
for anime_new_delivery in anime_new_delivery_list:
  register_to_animes(anime_new_delivery[0],anime_new_delivery[1],anime_new_delivery[2])

# 配信再開タイトル処理
cursor.execute("""
  SELECT work_id FROM tmp_table
  WHERE work_id IN (
    SELECT work_id FROM animes
    WHERE is_delivery = 0
  )
  """)
anime_re_delivery_list = cursor.fetchall()
for anime_re_delivery in anime_re_delivery_list:
  update_is_delivery_to_1(anime_re_delivery[0])

print("02完了\n")

# セッション破棄
cursor.close()
connection.close()