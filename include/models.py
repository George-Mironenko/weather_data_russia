from pydantic import (BaseModel, Field, field_validator,
                      validation_alias, ConfigDict)
from typing import Optional


class WeatherModel(BaseModel):
    # Игнорируем лишние поля из API, чтобы не тратить память
    model_config = ConfigDict(extra='ignore')

    # Основные данные
    city_name: str = Field(alias="requested_city")
    condition_id: int = Field(validation_alias=("weather", 0, "id"))

    # Метрики из блока 'main'
    temp: float = Field(validation_alias=("main", "temp"))
    temp_min: float = Field(validation_alias=("main", "temp_min"))
    temp_max: float = Field(validation_alias=("main", "temp_max"))
    pressure: int = Field(validation_alias=("main", "pressure"))
    humidity: int = Field(validation_alias=("main", "humidity"))

    # Опциональные данные или данные с дефолтами
    visibility: int = Field(default=0)
    wind_speed: float = Field(default=0.0, validation_alias=("wind", "speed"))
    wind_deg: int = Field(default=0, validation_alias=("wind", "deg"))
    clouds_all: int = Field(default=0, validation_alias=("clouds", "all"))

    # Временные метки
    dt: int  # Время замера (Unix)
    sunrise: int = Field(validation_alias=("sys", "sunrise"))
    sunset: int = Field(validation_alias=("sys", "sunset"))

    # Валидация логики (то, что у тебя было в if-ах)
    @field_validator('temp')
    @classmethod
    def check_temp_range(cls, v):
        if not (223.15 <= v <= 323.15):
            raise ValueError(f"Температура {v} вне допустимого диапазона!")
        return v

    @field_validator('humidity')
    @classmethod
    def check_humidity(cls, v):
        if not (0 <= v <= 100):
            raise ValueError("Влажность должна быть от 0 до 100")
        return v


    @field_validator('temp_max')
    @classmethod
    def check_temp_consistency(cls, v: float, info) -> float:
        # Проверяем, что max не меньше min (info.data содержит уже валидированные поля)
        if 'temp_min' in info.data and v < info.data['temp_min']:
            raise ValueError("temp_max не может быть меньше temp_min")
        return v