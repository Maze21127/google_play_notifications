import sqlite3
from loguru import logger

from models import App
import os


class Database:
    def __init__(self):
        logger.add("logs/error.log", format="{time} {level} {message}", level="ERROR", rotation="01:00")
        logger.add("logs/info.log", format="{time} {level} {message}", level="INFO", rotation="01:00")
        self.connection = None
        self.cursor = None
        self.db_name = 'apps.db'
        self.create_tables()
        self.check_connection()

    def create_tables(self):
        if os.path.exists(self.db_name):
            return
        self.check_connection()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS apps("
                            "id integer PRIMARY KEY,"
                            "name text NOT NULL,"
                            "link text NOT NULL UNIQUE,"
                            "author text NOT NULL)")
        self.connection.commit()
        logger.info("Таблица создана")

    def add_app(self, app: App):
        self.check_connection()
        self.cursor.execute(
            f"INSERT INTO apps (name, link, author) VALUES (?, ?, ?);", (app.name, app.link, app.author)
        )
        self.connection.commit()
        logger.info(f"{app} added")

    def is_app_exists(self, app: App):
        self.check_connection()
        self.cursor.execute(f"SELECT * FROM apps where name=? AND link=? AND author=?", (app.name, app.link, app.author))
        data = self.cursor.fetchall()
        return bool(data)

    def check_connection(self):
        if any((self.connection is None, self.cursor is None)):
            try:
                self.connection = sqlite3.connect(self.db_name)
                self.cursor = self.connection.cursor()
            except sqlite3.Error as e:
                logger.error(e)
