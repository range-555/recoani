import json
import re
from bs4 import BeautifulSoup


def anime_list(soup):
    anime_list = []
    anime_list = soup.select("[class='itemModule list']")

    return anime_list


def anime_params(anime):
    title = _get_text(anime.select_one(".webkit2LineClamp"))
    url = anime.select_one(".itemModuleIn > a")["href"]
    work_id = anime["data-workid"]
    params = {'title': title, 'url': url, 'work_id': work_id}

    return params


def basic_data(anime_id, soup):
    # 全体あらすじ
    outline_entire = _get_text(soup.select_one(".outlineContainer > p"))
    outline_entire = outline_entire.strip('\n') if outline_entire is not None else None
    # お気に入り数
    favorite = _get_text(soup.select_one(".nonmemberFavoriteCount > span"))
    # 制作年
    cast_container = soup.select(".castContainer > p")
    producted_year = ''
    for ptag in cast_container:
        if '製作年' in ptag.text:
            producted_year = ptag.text.strip('\n')
            producted_year = re.search('([0-9]+)', producted_year)
            producted_year = producted_year.group() if producted_year is not None else None
    # サムネイル画像
    target_img = soup.select_one(".keyVisual")
    target_img = target_img.select_one("img")
    thumbnail_url = target_img["src"] if target_img is not None else None

    return {'outline_entire': outline_entire, 'favorite': favorite, 'producted_year': producted_year, 'thumbnail_url': thumbnail_url, 'id': anime_id}


def cast_ids(soup, connection):
    cast_ids = []
    cast_tags = _tags(soup, "キャスト")
    for cast_tag in cast_tags:
        tag_id = _tag_id(cast_tag)
        cast_name = _get_text(cast_tag.select_one("a"))
        # castsにこのキャストが存在しなければinsert
        connection.execute_query("insert_into_casts_data_if_not_exist", {'tag_id': tag_id, 'cast_name': cast_name})
        connection.cursor.execute("SELECT id FROM casts WHERE tag_id = %(tag_id)s LIMIT 1", {"tag_id": tag_id})
        cast_id = connection.cursor.fetchone()
        cast_ids.append(cast_id[0])

    return cast_ids


def genre_cds(soup, connection):
    genre_cds = []
    genre_tags = _genre_tags(soup)
    for genre_tag in genre_tags:
        genre_cd = _tag_cd(genre_tag)
        genre_name = _get_text(genre_tag)
        connection.execute_query("insert_into_genres_data_if_not_exist", {'genre_cd': genre_cd, 'genre': genre_name})
        connection.cursor.execute("SELECT id FROM genres WHERE genre_cd = %(genre_cd)s LIMIT 1", {"genre_cd": genre_cd})
        genre_cd = connection.cursor.fetchone()
        genre_cds.append(genre_cd[0])

    return genre_cds


def other_information_ids(soup, connection):
    other_information_ids = []
    other_information_tags = _tags(soup, "その他")
    for other_information_tag in other_information_tags:
        tag_id = _tag_id(other_information_tag)
        other_information_name = _get_text(other_information_tag.select_one("a"))
        # other_informationsに存在しなければinsert
        connection.execute_query("insert_into_other_informations_data_if_not_exist", {'tag_id': tag_id, 'other_information': other_information_name})
        connection.cursor.execute("SELECT id FROM other_informations WHERE tag_id = %(tag_id)s LIMIT 1", {"tag_id": tag_id})
        other_information_id = connection.cursor.fetchone()
        other_information_ids.append(other_information_id[0])

    return other_information_ids


def outline_jsons(soup):
    outline_jsons = []
    if soup.find_all("script", {"type": "application/ld+json"}) is not None:
        outline_jsons = soup.find_all("script", {"type": "application/ld+json"})

    return outline_jsons


def outline_params_from_json(outline_json, anime_work_id):
    outline_json = _get_text(outline_json)
    if not outline_json:
        return None
    json_data = json.loads(outline_json, strict=False)
    # あらすじ取得
    outline = ""
    if type(json_data) == list:
        return None
    elif "video" in json_data.keys():
        outline = json_data["video"]["description"]
    elif "description" in json_data.keys():
        outline = json_data["description"]
    outline = re.search('(?<=』).+?($)', outline)
    outline = outline.group() if outline is not None else None
    outline = outline.replace("&ldquo;", "").replace("&rdquo;", "").replace("&hellip;", "") \
        if outline is not None else None  # 特殊文字が実体になっている箇所は除去

    if not outline:
        return None

    # 話数取得
    part_id = ""
    episode_number = ""
    if "@id" in json_data.keys():
        part_id = json_data["@id"]
        episode_number = part_id.replace(str(anime_work_id), "")

    return {'episode_number': episode_number, 'outline': outline, 'json': str(json_data), 'part_id': part_id}


def related_anime_ids(soup, connection):
    related_anime_ids = []
    related_anime_tags = _related_anime_tags(soup)
    for related_anime_tag in related_anime_tags:
        related_anime_work_id = _tag_id(related_anime_tag)
        connection.cursor.execute("SELECT id FROM animes WHERE work_id = %(related_anime_work_id)s LIMIT 1", {"related_anime_work_id": related_anime_work_id})
        related_anime_id = connection.cursor.fetchone()
        if related_anime_id is not None:
            related_anime_ids.append(related_anime_id[0])

    return related_anime_ids


def staff_ids(soup, connection):
    staff_ids = []
    staff_tags = _tags(soup, "スタッフ")
    for staff_tag in staff_tags:
        tag_id = _tag_id(staff_tag)
        staff_name = _get_text(staff_tag.select_one("a"))
        # staffsにこのスタッフが存在しなければinsert
        connection.execute_query("insert_into_staffs_data_if_not_exist", {'tag_id': tag_id, 'staff_name': staff_name})
        connection.cursor.execute("SELECT id FROM staffs WHERE tag_id = %(tag_id)s LIMIT 1", {"tag_id": tag_id})
        staff_id = connection.cursor.fetchone()
        staff_ids.append(staff_id[0])

    return staff_ids


def _genre_tags(soup):
    genre_tags = []
    if soup.select(".outlineContainer > .footerLink > a") is not None:
        genre_tags = soup.select(".outlineContainer > .footerLink > a")

    return genre_tags


def _get_text(x):
    return x.text if x is not None else None


def _related_anime_tags(soup):
    related_anime_tags = []
    if soup.select(".relationSwiper") is not None:
        related_anime_tags = soup.select(".relationSwiper > .itemWrapper > .itemModule")

    return related_anime_tags


def _tags(soup, text):
    tags = []
    if soup.find(class_="tagCaption", text=text) is not None:
        tags = soup.find(class_="tagCaption", text=text).findNext("ul").findAll("li")

    return tags


def _tag_cd(tag):
    tag_cd = tag["href"]
    tag_cd = re.search('.*(?<=Cd=)(.+?)$', tag_cd)
    tag_cd = tag_cd.group(1) if tag_cd is not None else None

    return tag_cd


def _tag_id(tag):
    tag_id = tag.select_one("a")["href"]
    tag_id = re.search('.*(?<=Id=)(.+?)$', tag_id)
    tag_id = tag_id.group(1) if tag_id is not None else None

    return tag_id
