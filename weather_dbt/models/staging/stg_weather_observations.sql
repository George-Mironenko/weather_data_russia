select
    weather_observations_id,
    city_id,
    condition_id,
    temp,
    temp_min,
    temp_max,
    pressure,
    humidity,
    visibility,
    wind_speed,
    wind_deg,
    clouds_all,
    recorded_at,
    sunrise,
    sunset,
    created_at
from {{ source('raw', 'weather_observations') }}
