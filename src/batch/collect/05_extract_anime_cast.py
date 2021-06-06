from bs4 import BeautifulSoup
import mysql.connector as mydb
import os
import re

connection = mydb.connect(
    host=os.environ.get('recoani_host'),
    port=os.environ.get('recoani_port'),
    user=os.environ.get('recoani_user'),
    password=os.environ.get('recoani_pass'),
    database=os.environ.get('recoani_db')
)

cursor = connection.cursor(buffered=True)


def get_text(x):
    return x.text if x is not None else None


def register_to_anime_cast(anime_id, cast_id):
    try:
        query = """
        INSERT INTO anime_cast
        (anime_id, cast_id)
        VALUES (%(anime_id)s, %(cast_id)s)
        """
        cursor.execute(query, {'anime_id': anime_id, 'cast_id': cast_id})
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e

# castsに存在しない場合INSERT


def register_to_casts(tag_id, cast_name):
    try:
        query = """
        INSERT INTO casts
        (tag_id, name)
        SELECT %(tag_id)s, %(cast_name)s FROM DUAL
        WHERE NOT EXISTS (SELECT * FROM casts
        WHERE tag_id = %(tag_id)s LIMIT 1)
        """
        cursor.execute(query, {'tag_id': tag_id, 'cast_name': cast_name})
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e


def update_status(anime_id):
    try:
        query = """
        UPDATE animes
        SET status = 3
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
    cursor.execute("SELECT id,html,status FROM animes WHERE id <= {} + 300 AND id >= {}".format(i, i))
    i = i + 300
    animes = cursor.fetchall()
    if len(animes) == 0:
        break

    for anime in animes:
        if anime[2] >= 3:
            continue
        anime_id = anime[0]
        target_page_soup = BeautifulSoup(anime[1], "html.parser")
        casts = []
        if target_page_soup.find(class_="tagCaption", text="キャスト") is not None:
            casts = target_page_soup.find(class_="tagCaption", text="キャスト").findNext("ul").findAll("li")
        for cast in casts:
            tag_id = cast.select_one("a")["href"]
            tag_id = re.search('.*(?<=Id=)(.+?)$', tag_id)
            tag_id = tag_id.group(1) if tag_id is not None else None
            cast_name = get_text(cast.select_one("a"))
            register_to_casts(tag_id, cast_name)
            cursor.execute("SELECT id FROM casts WHERE tag_id = '{tag_id}' LIMIT 1".format(tag_id=tag_id))
            cast_id = cursor.fetchone()
            register_to_anime_cast(anime_id, cast_id[0])

        update_status(anime_id)

print("05完了\n")

cursor.close()
connection.close()
