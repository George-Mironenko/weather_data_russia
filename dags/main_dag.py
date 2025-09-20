from datetime import timedelta

import requests
from airflow.sdk import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable


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
        sql_select = "SELECT name FROM cities"
        try:
            hook = PostgresHook(postgres_conn_id="my_postgres")
            records = hook.get_records(sql_select)

            # Преобразуем список кортежей в список строк
            cities_list = [record[0] for record in records if record and record[0]]
            print(f"Found cities: {cities_list}")
            return cities_list

        except Exception as error:
            print(f"Error fetching cities: {error}")
            raise

    @task
    def get_city_weather(city: str) -> dict:
        """
        Функция для получения данных о погоде из API
        :return: Словарь с данными о погоде.
        :raises requests.exceptions.HTTPError: При HTTP ошибках.
        :raises requests.exceptions.RequestException: При ошибках запроса.
        """
        API_KEY = Variable.get("data_api")

        url = "https://samples.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": API_KEY,
        }
        try:
            response = requests.get(url=url, params=params, timeout=600)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP ошибка: {http_err}")
            raise
        except requests.exceptions.RequestException as req_err:
            print(f"Ошибка запроса: {req_err}")
            raise
        except Exception as e:
            print(f"Произошла ошибка: {e}")
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

            for data in weather_data_list:

                # Используем имя города из ответа API или из запроса
                city_name = data.get('name', data.get('requested_city', 'Unknown'))

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
        except Exception as error:
            print(error)
            raise

    # Выполняем задачи
    # Получаем список городов
    cities = ger_list_cities()

    # Получаем данные о погоде для каждого города
    weather_data = get_city_weather.expand(city=cities)

    # Загружаем данные в базу данных
    load_data_base(weather_data)