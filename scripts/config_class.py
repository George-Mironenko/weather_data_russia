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


    # OpenWeather - required field
    OPENWEATHER_API_KEY: str = Field(
        default=os.getenv('OPENWEATHER_API_KEY'),
        description="OpenWeather API key"
    )


    # S3
    SELECTEL_ACCESS_KEY: str = Field(
        default=os.getenv('SELECTEL_ACCESS_KEY', ''),
        description="S3 access key"
    )
    SELECTEL_SECRET_KEY: str = Field(
        default=os.getenv('SELECTEL_SECRET_KEY', ''),
        description="S3 secret key"
    )
    SELECTEL_ENDPOINT: str = Field(
        default=os.getenv('SELECTEL_ENDPOINT', ''),
        description="S3 endpoint URL"
    )


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
