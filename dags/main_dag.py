from datetime import timedelta

import polars
from airflow.sdk import DAG
from airflow.models import Variable
from airflow.decorators import task
from airflow.providers.http.hooks.http import HttpHook
from sympy.physics.vector.printing import params

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
    def extract(city: str = "Moscow"):
        if city not in ("Moscow", "Saint Petersburg"):
            logger.error(f"Город {city} не поддерживается")
            raise ValueError("Город не поддерживается")

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
    def trigger_spark_transform(extract_results):
        pass

    # Динамическое создание extract-задач
    sources = ["system_a", "system_b", "system_c"]
    extracted = extract.expand(source=sources)

    # Transform дожидается всех extract
    trigger_spark_transform(extracted)