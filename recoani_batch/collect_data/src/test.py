import mysql.connector as mydb
import os

connection = mydb.connect(
  host = os.environ.get('recoani_host'),
  port = 3306,
  user = os.environ.get('recoani_user'),
  password = os.environ.get('recoani_pass'),
  database = os.environ.get('recoani_db')
)

try:
  cursor = connection.cursor()
  print('connection success!!')
except:
  print("Error")

# セッション破棄
cursor.close()
connection.close()