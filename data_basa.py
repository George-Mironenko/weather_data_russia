import psycopg2
from typing import Optional, Tuple

from loging_etl import logger


class PostgresConnection:
    """Класс для работы с PostgreSQL."""

    def __init__(
        self,
        database: str,
        password: str,
        host: str = "localhost",
        user: str = "postgres",
        port: int = 5432
    ) -> None:
        """
        Инициализация параметров подключения к базе данных.

        :param database: Название базы данных
        :param password: Пароль пользователя
        :param host: Адрес сервера (по умолчанию 'localhost')
        :param user: Имя пользователя (по умолчанию 'postgres')
        :param port: Порт (по умолчанию 5432)
        """
        self.host: str = host
        self.database: str = database
        self.user: str = user
        self.password: str = password
        self.port: int = port
        self.connection = None
        self.cursor = None
        self._connect()


    def _connect(self):
        """Создание подключения к PostgreSQL."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            logger.info("Соединение с PostgreSQL установлено успешно.")
        except psycopg2.Error as e:
            logger.critical(f"Ошибка подключения: {e}")

    def __enter__(self):
        """
        Создаём контекстный менеджер
        :return:
        """
        try:
            self._connect()
        except Exception as error:
            logger.error(f"Ошибка подключения: {error}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Выходим из контекстного менеджера
        :return:
        """
        self._close()

    def _close(self) -> None:
        """Закрытие соединения и освобождение ресурсов."""
        try:
            if self.connection:
                self.connection.close()
            if self.cursor:
                self.cursor.close()

            logger.info("Соединение с PostgreSQL закрыто.")
        except Exception as error:
            logger.error(f"Ошибка: {error}")
            raise


    def _commit(self) -> None:
        """Сохранение изменений в базе данных."""
        try:
            self.connection.commit()

            logger.debug("Изменения сохранены.")
        except psycopg2.Error as e:
            logger.error(f"Ошибка сохранения изменений: {e}")

    def __str__(self) -> str:
        """Строковое представление объекта."""
        return (f"Подключено к базе данных '{self.database}'"
                f" от пользователя '{self.user}'")

    def execute_procedure(self, query: str, params: Optional[Tuple] = None) -> bool:
        if self.cursor is None or self.connection is None:
            logger.critical("Нет подключения к БД. Невозможно выполнить запрос.")
            return False

        try:
            self.cursor.execute(query, params or ())
            return True
        except psycopg2.Error as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            return False


    def execute_function(self, query: str, params:  Optional[Tuple] = None):
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Ошибка сохранения изменений: {e}")
            return None

    def __getattribute__(self, name):
        return super().__getattribute__(name)

    def __delattr__(self, name):
        logger.error(f"Удаление {name} запрещено!")
        raise AttributeError("Нельзя удалять!")