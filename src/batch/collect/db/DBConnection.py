import os
import mysql.connector as mydb


class DBConnection:
    connection = None

    def connect(self):
        connection = mydb.connect(
            host=os.environ.get('recoani_host'),
            port=os.environ.get('recoani_port'),
            user=os.environ.get('recoani_user'),
            password=os.environ.get('recoani_pass'),
            database=os.environ.get('recoani_db')
        )
        return connection
