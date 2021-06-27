class DBCommand:
    def __init__(self):
        self.query = ""

    def update_anime_list_pages(self):
        self.query = """
        INSERT INTO anime_list_pages
        (initial, html)
        VALUES (%(initial)s, %(html)s)
        ON DUPLICATE KEY UPDATE
        html = %(html)s
        """
