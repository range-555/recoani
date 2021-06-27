class DBCommand:

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
