from pydantic import BaseModel, Field, field_validator, AliasPath, ConfigDict
from datetime import datetime


class WeatherModel(BaseModel):
    model_config = ConfigDict(extra='ignore', populate_by_name=True)

    # Основные данные
    city_name: str = Field(validation_alias="requested_city")
    condition_id: int = Field(validation_alias=AliasPath("weather", 0, "id"))

    # Метрики
    temp: float = Field(validation_alias=AliasPath("main", "temp"))
    temp_min: float = Field(validation_alias=AliasPath("main", "temp_min"))
    temp_max: float = Field(validation_alias=AliasPath("main", "temp_max"))
    pressure: int = Field(validation_alias=AliasPath("main", "pressure"))
    humidity: int = Field(validation_alias=AliasPath("main", "humidity"))

    # Опциональные данные
    visibility: int = Field(default=0)
    wind_speed: float = Field(default=0.0, validation_alias=AliasPath("wind", "speed"))
    wind_deg: int = Field(default=0, validation_alias=AliasPath("wind", "deg"))
    clouds_all: int = Field(default=0, validation_alias=AliasPath("clouds", "all"))

    # Unix timestamps
    dt: int
    sunrise: int = Field(validation_alias=AliasPath("sys", "sunrise"))
    sunset: int = Field(validation_alias=AliasPath("sys", "sunset"))

    # Валидация
    @field_validator('temp')
    @classmethod
    def check_temp_range(cls, v: float) -> float:
        if not (223.15 <= v <= 323.15):
            raise ValueError(f"Температура {v} вне допустимого диапазона!")
        return v

    @field_validator('humidity')
    @classmethod
    def check_humidity(cls, v: int) -> int:
        if not (0 <= v <= 100):
            raise ValueError("Влажность должна быть от 0 до 100")
        return v

    @field_validator('temp_max')
    @classmethod
    def check_temp_consistency(cls, v: float, info) -> float:
        if 'temp_min' in info.data and v < info.data['temp_min']:
            raise ValueError("temp_max не может быть меньше temp_min")
        return v

    @property
    def recorded_at(self) -> datetime:
        """Для записи в БД (timestamp с часовым поясом)"""
        return datetime.fromtimestamp(self.dt)

    @property
    def sunrise_dt(self) -> datetime:
        return datetime.fromtimestamp(self.sunrise)

    @property
    def sunset_dt(self) -> datetime:
        return datetime.fromtimestamp(self.sunset)