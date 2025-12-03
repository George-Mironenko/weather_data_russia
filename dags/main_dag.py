from datetime import timedelta, datetime

import requests
from airflow.sdk import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable

import logging

from natsort import humansorted

task_logger = logging.getLogger("airflow.task")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(year=2025, month=11, day=10),
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

            return records

        except Exception as error:
            task_logger.error(f"Error fetching cities: {error}")
            raise

    @task
    def get_cities_list(records: tuple) -> list | None:
        """
        Функция для преобразования списка кортежей в список строк
        :param records: Список кортежей
        :return: Список строк
        """
        try:
            if not records:
                task_logger.error(f"Ошибка: в функцию передан пустой список")
                return None

            cities_list = [record[0] for record in records if record and record[0]]
            task_logger.debug(f"Успешно список преобразован")

            return cities_list

        except Exception as eroor:
            task_logger.error(f"Ошибка при преобразование списока кортежей в список строк {eroor}")
            return None

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
                %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                TO_TIMESTAMP(%s),
                TO_TIMESTAMP(%s),
                TO_TIMESTAMP(%s)
            )
        """

        parameters = []
        batch_size = 1000

        # Список для пропущенных данных
        invalid_records = []

        try:
            def invalid_records_append(name_city, data_list, test_error: str = 'Not Specified'):
                """
                Функция для добавления данные в список пропущенных данных
                """
                invalid_records.append(
                    {'city': name_city, 'error': test_error, 'data': data_list})

            # Подключение к базе данных
            hook = PostgresHook(postgres_conn_id="my_postgres")
            conn = hook.get_conn()
            cursor = conn.cursor()

            task_logger.debug("Мы подключились к postgres")

            # Цикл для, добавление данных в пакетах
            for i in range(0, len(weather_data_list), batch_size):

                # Делаем срез данных и делаем пакет
                batch = weather_data_list[i: i + batch_size]
                task_logger.debug("Создали батч")


                # Цикл для добавления данных
                for data in batch:
                    # Получаем название города
                    city_name = data.get('requested_city')

                    # Проверяем что данные есть
                    if data is None:
                        task_logger.debug(f"batch с {i} до {i + batch_size} пустой")
                        continue

                    # Проверка, что данные об температуре есть
                    if not data.get("main"):
                        invalid_records_append(city_name, data, 'Missing main object')
                        continue

                    # Проверяем, что данные об температуре есть и они правдивы
                    if (temp := data['main'].get("temp")) is None:
                        invalid_records_append(city_name, data, 'Missing temp')
                        continue

                    if  temp < -89.2 or temp > 56.7:
                        invalid_records_append(city_name, data, f'Impossible temp: {temp}')
                        continue

                    # Проверяем, что данные об влажности и они правдивы
                    if (humidity := data['main'].get('humidity')) is None:
                        invalid_records_append(city_name, data, 'Missing humidity')
                        continue

                    if not (0 <= humidity <= 100):
                        invalid_records_append(city_name, data, f'Invalid humidity: {humidity}')
                        continue

                    task_logger.debug(f"batch с {i} до {i + batch_size} не пустой")

                    city_id_sql = 'SELECT city_id FROM cities WHERE name = %s'
                    city_id = hook.get_first(city_id_sql, parameters=(city_name,))
                    task_logger.debug("Получили city_id")

                    if city_id is None:
                        task_logger.warning(f"Город {city_name} не найден в базе")
                        continue

                    task_logger.debug(f"Город {city_name} найден в базе")

                    parameters.append((
                            city_id[0],
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

                if invalid_records:
                    task_logger.warning(f"Найдено {len(invalid_records)} проблемных записей:")
                    for record in invalid_records:
                        task_logger.warning(f"Город {record['city']}: {record['error']}")


                if parameters:
                    task_logger.debug("Данные есть в parameters")

                    cursor.executemany(sql_insert, parameters)
                    conn.commit()
                    task_logger.info(f"Успешно загружено {len(parameters)} записей")
                else:
                    task_logger.warning("Нет данных для вставки")

            cursor.close()
            task_logger.info("Успешно закрытия курсора")

        except Exception as error:
            task_logger.error(f"Ошибка при преобразование: {error}")
            raise

    # Выполняем задачи

    # Получаем список городов
    records = ger_list_cities()

    # Преобразовываем в нужный формат
    cities = get_cities_list(records)

    # Получаем данные о погоде для каждого города
    weather_data = get_city_weather.expand(city=cities)

    # Загружаем данные в базу данных
    load_data_base(weather_data)