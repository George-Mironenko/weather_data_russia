from datetime import timedelta, datetime

import requests
from airflow.sdk import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable

import logging
from include.models import WeatherModel
from pydantic import ValidationError


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
    dag_id='weather_data_get',
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
    def get_cities_list(records: tuple[tuple[str, ...], ...]) -> list[str] | None:
        """
        Функция для преобразования списка кортежей в список строк
        :param records: Список кортежей
        :return: Список строк
        """
        try:
            if not records:
                task_logger.error(f"Ошибка: в функцию передан пустой список")
                return None

            def writte_log(warrning: str):
                task_logger.warning(
                    f"Запись #{idx} пропущена: warrning"
                )

            cities_list = []

            for idx, record in enumerate(records, 1):

                if not isinstance(record, tuple):
                    writte_log("ожидался tuple")
                    continue

                if not record:
                    writte_log("пустой кортеж")
                    continue

                if not isinstance(first_records :=  record[0], str):
                    writte_log("первый элемент не строка")
                    continue

                if  not first_records.strip():
                    writte_log("пустая строка или пробелы")
                    continue

                cities_list.append(first_records)

            task_logger.debug(f"Успешно список преобразован")

            if not cities_list:
                task_logger.error(
                    f"Ни одна запись не прошла валидацию. "
                )
                return None

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
        hook = PostgresHook(postgres_conn_id="my_postgres")
        valid_parameters = []

        for data in weather_data_list:
            try:
                # Магия Pydantic: валидация и маппинг в один присест
                weather = WeatherModel(**data)

                # Получаем city_id (бизнес-логика, которую не засунуть в Pydantic)
                city_res = hook.get_first('SELECT city_id FROM cities WHERE name = %s',
                                          (weather.city_name,))

                if not city_res:
                    task_logger.warning(f"Город {weather.city_name} отсутствует в БД")
                    continue

                # Формируем кортеж для вставки, обращаясь к объекту через точку
                valid_parameters.append((
                    city_res[0], weather.condition_id, weather.temp,
                    weather.temp_min, weather.temp_max, weather.pressure,
                    weather.humidity, weather.visibility, weather.wind_speed,
                    weather.wind_deg, weather.clouds_all, weather.dt,
                    weather.sunrise, weather.sunset
                ))

            except ValidationError as e:
                task_logger.error(f"Ошибка схемы для города {data.get('requested_city')}: {e.errors()}")
            except Exception as e:
                task_logger.error(f"Ошибка при обработке города: {e}")

        # Bulk insert через хук
        if valid_parameters:
            hook.insert_rows(
                table='weather_observations',
                rows=valid_parameters,
                target_fields=[
                    'city_id', 'condition_id', 'temp', 'temp_min', 'temp_max',
                    'pressure', 'humidity', 'visibility', 'wind_speed',
                    'wind_deg', 'clouds_all', 'recorded_at', 'sunrise', 'sunset'
                ],
                commit_every=100
            )

    # Выполняем задачи

    # Получаем список городов
    records = ger_list_cities()

    # Преобразовываем в нужный формат
    cities = get_cities_list(records)

    # Получаем данные о погоде для каждого города
    weather_data = get_city_weather.expand(city=cities)

    # Загружаем данные в базу данных
    load_data_base(weather_data)