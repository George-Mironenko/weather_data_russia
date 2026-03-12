from pydantic import BaseModel, Field, field_validator, validation_alias
from typing import Optional


class WeatherModel(BaseModel):

    city_name: str = Field(alias="requested_city")
    temp: float = Field(validation_alias=("main", "temp"))
    temp_min: float = Field(validation_alias=("main", "temp_min"))
    temp_max: float = Field(validation_alias=("main", "temp_max"))
    humidity: int = Field(validation_alias=("main", "humidity"))
    pressure: int = Field(validation_alias=("main", "pressure"))
    dt: int

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

