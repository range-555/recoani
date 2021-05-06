import mysql.connector as mydb
import os

connection = mydb.connect(
  host = os.environ.get('ml_db_host'),
  port = os.environ.get('local_port'),
  user = os.environ.get('recoani_user'),
  password = os.environ.get('recoani_pass'),
  database = os.environ.get('recoani_db')
)

cursor = connection.cursor()

cursor.execute("UPDATE animes SET title_full = title")

print("12完了\n")

# セッション破棄
cursor.close()
connection.close()
