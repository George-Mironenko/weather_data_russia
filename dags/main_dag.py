from datetime import timedelta

from airflow.sdk import DAG
from airflow.models import Variable
from airflow.decorators import task
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook

from loging_etl import logger


# Получаем API-ключ из переменных Airflow
API_KEY = Variable.get("data_russia_api")

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
        :return: Список городов по которым надо узнать погоду.
        """

        sql_select = f"""
            SELECT name FROM cities
        """
        try:
            hook = PostgresHook(postgres_conn_id="my_postgres")
            logger.debug("Успешно подключились к postgres для получения списка городов.")

            return hook.get_records(sql_select)

        except Exception as error:
            logger.error(error)

    @task
    def get_city_weather(city: str = "Moscow"):
        """
        Функция которая, извлекает данные из API
        :param city: Город по которому надо узнать погоду
        :return: Данные о погоде в городе
        """
        try:
            http = HttpHook(method='GET', http_conn_id='openweathermap_api')

            response = http.run(
                endpoint="/data/2.5/weather",
                params= {
                'q': city,
                'units': 'metric'
                }
            )
            response.raise_for_status()
            logger.info("Успешно извлекли данные")

            return response.json()

        except Exception as error:
            logger.error(error)
            return None


    @task
    def load_data_base(extract_results):
        """
        Функция которая, отправит данные в базу данных
        :param extract_results:
        :return:
        """
        try:
            # Получаем sql для вставки данных
            with open("sql_scripts/script_insert.sql", "r") as file:
                # Читаем файл
                sql_insert = file.read()
            logger.debug("Успешно прочитали файл script_insert")

            # Устанавливаем подключение
            hook = PostgresHook(postgres_conn_id="my_postgres")
            logger.debug("Успешно получили connection из airflow")

            # Отправляем данные в базу данных
            hook.run(
                sql_insert,
                parameters=(
                    extract_results["name"],
                    extract_results["weather"][0]["id"],
                    extract_results["main"]["temp"],
                    extract_results["main"]["temp_min"],
                    extract_results["main"]["temp_max"],
                    extract_results["main"]["pressure"],
                    extract_results["main"]["humidity"],
                    extract_results["visibility"],
                    extract_results["wind"]["speed"],
                    extract_results["wind"]["deg"],
                    extract_results["clouds"]["all"],
                    extract_results["dt"],
                    extract_results["sys"]["sunrise"],
                    extract_results["sys"]["sunset"]
                )
            )
            logger.info("Успешно загрузили данные в базу данных")

        except Exception as error:
            logger.error(error)

    # Запуск DAG
    load_data_base(
        get_city_weather.expand(
            ger_list_cities
        )
    )