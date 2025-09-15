from datetime import datetime, timedelta
import io

import pandas as pd
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.sdk import DAG
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
    'depends_on_pats': False,
}

with DAG(
    dag_id="Load_to_S3",
    default_args=default_args,
    schedule='@month',
    fail_fast=True
) as dag:

    @task
    def extract():
        sql_scripts_select = """
        SELECT * FROM weather_observations;
        """

        sql_scripts_delete = """
        DELETE FROM weather_observations;
        """

        try:
            # Подключение к базе данных
            hook = PostgresHook(connection="my_postgres")
            task_logger.debug("Успешно подключились к базе данных")

            # Получение данных из таблицы
            data = hook.get_records(sql_scripts_select)
            task_logger.debug("Успешно получили данные из базы данных")

            # Удаление данных из таблицы
            hook.run(
                sql_scripts_delete
            )
            task_logger.debug("Успешно удалили данные из базы данных")
            task_logger.info(f"Успешно извлекли данные из базы данных")

            return data
        except Exception as error:
            task_logger.error(f"Ошибка при извлечении данных: {error}")
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

            bucket_name = 'weather'
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
                task_logger.error(f"Ошибка при извлечении данных: {error}")
