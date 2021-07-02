from db.DBConnection import DBConnection

conn = DBConnection()

conn.execute_query("SELECT html FROM anime_list_pages")
anime_list_htmls = conn.cursor.fetchall()

for i in anime_list_htmls:
    print(i)
    break

del conn
