from urllib import parse

# urlにクエリを付与


def update_target_url(target_url, update_dict):
    parsed = parse.urlparse(target_url)
    query_dict = parse.parse_qs(parsed.query, True)
    query_dict.update(update_dict)
    query_string = parse.urlencode(query_dict, True)
    return parse.urlunparse(parsed._replace(query=query_string))
