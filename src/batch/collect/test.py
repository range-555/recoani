from db.DBConnection import DBConnection

conn = DBConnection().connect()
cursor = conn.cursor()

cursor.execute("SELECT html FROM anime_list_pages")
anime_list_htmls = cursor.fetchall()

for i in anime_list_htmls:
    print(i)
