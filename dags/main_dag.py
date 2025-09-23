from datetime import timedelta

import requests
from airflow.sdk import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable

import logging

task_logger = logging.getLogger("airflow.task")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': '2025-05-13',
    'email_on_failure': True,
    'email': ['georgijmironenko36@gmail.com'],
    'retries': 4,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='russia_data_weather',
    default_args=default_args,
    schedule='@daily',
    catchup=False,
) as dag:

    @task
    def ger_list_cities():
        """
        Эта задача получает список городов из базы данных
        :return: Список городов
        """
        sql_select = 'SELECT name FROM "cities"'
        try:
            hook = PostgresHook(postgres_conn_id="my_postgres")
            task_logger.debug("Мы подключились к postgres")

            records = hook.get_records(sql_select)
            task_logger.debug("Получили данные из бд")

            # Преобразуем список кортежей в список строк
            cities_list = [record[0] for record in records if record and record[0]]
            task_logger.debug("Преобразовали в кортеж")

            task_logger.info("Успешно получили города")
            return cities_list

        except Exception as error:
            task_logger.error(f"Error fetching cities: {error}")
            raise

    @task
    def get_city_weather(city: str) -> dict:
        """
        Функция для получения данных о погоде из API
        :return: Словарь с данными о погоде.
        :raises requests.exceptions.HTTPError: При HTTP ошибках.
        :raises requests.exceptions.RequestException: При ошибках запроса.
        """
        # Получаем api ключ из airflow
        API_KEY = Variable.get("data_api")

        url = "https://api.openweathermap.org/data/2.5/weather"

        # Строим api ссылку
        params = {
            "q": city,
            "appid": API_KEY,
        }
        try:
            response = requests.get(url=url, params=params, timeout=600)
            task_logger.debug("Сделали запрос к Api")

            response.raise_for_status()
            task_logger.debug("Проверили на ошибку")

            data = response.json()
            data['requested_city'] = city
            task_logger.debug("Успешно преобразовали в json")

            return data

        except requests.exceptions.HTTPError as http_err:
            task_logger.error(f"HTTP ошибка: {http_err}")
            raise
        except requests.exceptions.RequestException as req_err:
            task_logger.error(f"Ошибка запроса: {req_err}")
            raise
        except Exception as e:
            task_logger.error(f"Произошла ошибка: {e}")
            raise


    @task
    def load_data_base(weather_data_list):
        """
        Загружает данные о погоде из списка в БД
        :param weather_data_list: Список словарей с данными о погоде
        :return None
        """

        sql_insert = """
            INSERT INTO weather_observations
                (city_id, condition_id, temp, temp_min, temp_max, pressure, humidity,
                 visibility, wind_speed, wind_deg, clouds_all, recorded_at, sunrise, sunset)
            VALUES (
                (SELECT city_id FROM cities WHERE name = %s),
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                TO_TIMESTAMP(%s),
                TO_TIMESTAMP(%s),
                TO_TIMESTAMP(%s)
            )
        """

        try:
            # Подключение к базе данных
            hook = PostgresHook(postgres_conn_id="my_postgres")
            task_logger.debug("Мы подключились к postgres")

            # Цикл для добавления данных
            for data in weather_data_list:
                city_name = data.get('requested_city')

                hook.run(sql_insert, parameters=(
                        city_name,
                        data["weather"][0]["id"],
                        data["main"]["temp"],
                        data["main"]["temp_min"],
                        data["main"]["temp_max"],
                        data["main"]["pressure"],
                        data["main"]["humidity"],
                        data.get("visibility", 0),
                        data["wind"].get("speed", 0),
                        data["wind"].get("deg", 0),
                        data["clouds"].get("all", 0),
                        data["dt"],
                        data["sys"]["sunrise"],
                        data["sys"]["sunset"]
                ))

                task_logger.info("Успешно сохранили данные")
        except Exception as error:
            task_logger.error(f"Ошибка при преобразование: {error}")
            raise

    # Выполняем задачи
    # Получаем список городов
    cities = ger_list_cities()

    # Получаем данные о погоде для каждого города
    weather_data = get_city_weather.expand(city=cities)

    # Загружаем данные в базу данных
    load_data_base(weather_data)