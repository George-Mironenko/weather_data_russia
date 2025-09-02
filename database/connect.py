import os

from data_basa import PostgresConnection
from loging_etl import logger


#Подключение к БД
try:
    DB = PostgresConnection(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    logger.info("Подключение к БД успешно")
except Exception as e:
    logger.critical(f"Ошибка подключения к БД: {e}")
    raise SystemExit(1)

#Запрет импорта через `from module import *`
__all__ = []

