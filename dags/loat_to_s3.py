from datetime import datetime, timedelta
import io

import pandas as pd
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow import DAG
from airflow.decorators import task
import boto3

import logging

# get the airflow.task logger
task_logger = logging.getLogger("airflow.task")

def get_s3_client():
    """
    :return:
    """
    return boto3.client(
        's3',
        endpoint_url='https://s3.storage.selcloud.ru',
        aws_access_key_id=Variable.get("SELECTEL_ACCESS_KEY"),
        aws_secret_access_key=Variable.get("SELECTEL_SECRET_KEY")
    )

default_args = {
    'owen':'airflow',
    'email':'georgijmironenko36@gmail.com',
    'email_on_failure': True,
    'start_date': datetime(2025, 9, 9),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'depends_on_past': False,
}

with DAG(
    dag_id="Load_to_S3",
    default_args=default_args,
    schedule='@monthly',
    fail_fast=True
) as dag:

    @task
    def extract():
        sql_scripts_select = """
        SELECT 
            c.name AS city_name,
            w.condition_id AS weather_id,
            w.temp,
            w.temp_min,
            w.temp_max,
            w.pressure,
            w.humidity,
            w.visibility,
            w.wind_speed,
            w.wind_deg,
            w.clouds_all,
            w.recorded_at AS dt,
            w.sunrise,
            w.sunset
        FROM weather_observations w
        JOIN cities c ON w.city_id = c.city_id;
        """

        try:
            # Подключение к базе данных
            hook = PostgresHook(postgres_conn_id="my_postgres")
            task_logger.debug("Успешно подключились к базе данных")

            # Получение данных из таблицы
            data = hook.get_records(sql_scripts_select)
            task_logger.debug("Успешно получили данные из базы данных")

            task_logger.info("Успешно извлекли данные из базы данных")

            return data

        except PostgresHook.get_records as error:
            task_logger.error(f"Ошибка при получении данных: {error}")
            return None

        except Exception as error:
            task_logger.error(f"Ошибка: {error}")
            return None

    @task
    def transform_load(data):
        # Создание DataFrame из данных
        columns = [
            "city_name", "weather_id", "temp", "temp_min", "temp_max",
            "pressure", "humidity", "visibility", "wind_speed", "wind_deg",
            "clouds_all", "dt", "sunrise", "sunset"
        ]

        try:
            # Проверка на пустоту списка
            if data is None:
                raise Exception('Список пуст')

            # Создание DataFrame
            df = pd.DataFrame(data, columns=columns)
            task_logger.debug('Мы создали датафрейм')

            df = df.astype({
                "city_name": "string",
                "weather_id": "int32",
                "temp": "float32",
                "temp_min": "float32",
                "temp_max": "float32",
                "pressure": "int32",
                "humidity": "int32",
                "visibility": "int32",
                "wind_speed": "float32",
                "wind_deg": "int16",
                "clouds_all": "int8",
                "dt": "int64",
                "sunrise": "int64",
                "sunset": "int64"
            })

            # Сериализуем в Parquet в памяти (рекомендуется!)
            buffer = io.BytesIO()
            df.to_parquet(buffer, engine='pyarrow', compression='snappy', index=False)

            # Конфигурация для подключения к Selectel Object Storage
            s3 = get_s3_client()
            task_logger.debug('Мы прошли конфигурацию')

            bucket_name = 'weather-data'
            file_name = f'data_{datetime.now().year}-{datetime.now().month:02d}.parquet'

            # Отправка данных
            s3.put_object(
                Bucket=bucket_name,
                Key=file_name,
                Body=buffer.getvalue(),
                ContentType='application/octet-stream'
            )
            task_logger.info("Успешно отправили файл в s3")
        except Exception as error:
                task_logger.error(f"Ошибка при преобразовании данных: {error}")
                raise

    @task
    def delete_data():
        sql_scripts_delete = """
                    DELETE FROM weather_observations;
                    """
        try:
            hooks = PostgresHook(postgres_conn_id="my_postgres")
            task_logger.debug("Успешно подключились к базе данных")

            hooks.run(
                sql_scripts_delete
            )
            task_logger.info("Мы успешно освободили место для таблицы")

        except Exception as error:
             task_logger.error(f"Ошибка при удалении данных: {error}")
             raise


    # Получаем данные из postgres
    data = extract()

    # Создаем parquet и отправляем в s3
    load_task = transform_load(data)

    # Удаляем данные из postgres
    delete_task = delete_data()

    # Задаём порядок: сначала load_task, потом delete_task
    load_task >> delete_task
