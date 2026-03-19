import os

from pydantic import BaseModel, Field
from dotenv import load_dotenv


load_dotenv()

class ConfigSettings(BaseModel):
    """class config for getting parameters from .env"""

    # Postgres
    POSTGRES_USER: str = Field(
        default=os.getenv('POSTGRES_USER', 'airflow'),
        description="PostgreSQL username"
    )

    POSTGRES_PASSWORD: str = Field(
        default=os.getenv('POSTGRES_PASSWORD', 'airflow'),
        description="PostgreSQL password"
    )

    POSTGRES_DB: str = Field(
        default=os.getenv('POSTGRES_DB', 'airflow'),
        description="PostgreSQL database name"
    )

    POSTGRES_PORT: int = Field(
        default=int(os.getenv('POSTGRES_PORT', '5432')),
        description="PostgreSQL port",
        ge=1,
        le=65535
    )


    # OpenWeather
    OPENWEATHER_API_KEY: str = os.getenv('OPENWEATHER_API_KEY')

    # S3
    SELECTEL_ACCESS_KEY: str = os.getenv('SELECTEL_ACCESS_KEY')
    SELECTEL_SECRET_KEY: str = os.getenv('SELECTEL_SECRET_KEY')
    SELECTEL_ENDPOINT: str = os.getenv('SELECTEL_ENDPOINT')


    @property
    def postgres_dsh(self):
        return (f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@postgres:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    @property
    def airflow_connection(self) -> dict:
        """For create Connection in the Airflow"""
        return {
            "conn_id": "postgres_weather",
            "conn_type": "postgres",
            "host": "postgres",
            "login": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD,
            "port": self.POSTGRES_PORT,
            "schema": self.POSTGRES_DB
        }
