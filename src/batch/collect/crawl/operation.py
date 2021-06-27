from time import sleep
from urllib import parse

# ページを下までスクロール


def scroll_to_bottom(driver):
    html_tmp_1 = driver.page_source
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        html_tmp_2 = driver.page_source
        if html_tmp_1 != html_tmp_2:
            html_tmp_1 = html_tmp_2
        else:
            return driver

# urlにクエリを付与


def update_target_url(target_url, update_dict):
    parsed = parse.urlparse(target_url)
    query_dict = parse.parse_qs(parsed.query, True)
    query_dict.update(update_dict)
    query_string = parse.urlencode(query_dict, True)
    return parse.urlunparse(parsed._replace(query=query_string))
