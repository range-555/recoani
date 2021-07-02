class DBCommand01:
    ##########
    # 01
    ##########
    @staticmethod
    def update_anime_list_pages():
        query = """
        INSERT INTO anime_list_pages
        (initial, html)
        VALUES (%(initial)s, %(html)s)
        ON DUPLICATE KEY UPDATE
        html = %(html)s
        """
        return query


class DBCommand02:
    ##########
    # 02
    ##########
    @staticmethod
    def register_to_tmp_table(title, url, work_id):
        query = """
        INSERT INTO tmp_table
        (title, url, work_id)
        VALUES (%(title)s, %(url)s, %(work_id)s)
        """
        return query
