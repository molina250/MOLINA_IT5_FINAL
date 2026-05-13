# model/db.py

from dataclasses import dataclass
import mysql.connector


@dataclass
class DBConfig:
    host: str = "127.0.0.1"
    user: str = "root"
    password: str = ""
    database: str = "edugate_db"


DB = DBConfig()


def db_connect():
    return mysql.connector.connect(
        host=DB.host,
        user=DB.user,
        password=DB.password,
        database=DB.database,
    )
