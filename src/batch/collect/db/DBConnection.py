import mysql.connector as mydb
import os
from .DBCommand import DBCommand


class DBConnection:
    def __init__(self):
        try:
            self.connection = mydb.connect(
                host=os.environ.get('RECOANI_HOST'),
                port=os.environ.get('RECOANI_PORT'),
                user=os.environ.get('RECOANI_USER'),
                password=os.environ.get('RECOANI_PASSWORD'),
                database=os.environ.get('RECOANI_DB')
            )
            self.connection.autocommit = False
            # カーソルを格納
            self.cursor = self.connection.cursor()
        except mydb.Error as e:
            print("[DBConnection Error] ", e)
            raise
        except Exception as e:
            print("[Error] ", e)
            raise

    # SELECTクエリの実行
    def execute_select_query(self, sql, params=None):
        try:
            self.cursor.execute(sql, params=params)
        except mydb.Error as e:
            print("[SQL Excecution Error] ", e)
            raise

    # SELECT以外のクエリの実行
    def execute_query(self, sql, params=None):
        try:
            self.cursor.execute(sql, params=params)
            self.connection.commit()
        except mydb.Error as e:
            print("[SQL Excecution Error] ", e)
            self.connection.rollback()
            raise

    # DB接続終了
    def __del__(self):
        try:
            self.cursor.close()
            self.connection.close()
            print("Conncection Delete!!")
        except mydb.errors.ProgrammingError as e:
            print(e)
            raise
