{{ config(materialized='view') }}

SELECT
    c.city_name,
    c.lat,
    c.lon,
    c.country_name,
    wo.condition_id AS weather_id,
    wc.main_name AS weather_main,
    wc.description AS weather_description,
    wc.icon_code AS weather_icon,
    wo.temp,
    wo.temp_min,
    wo.temp_max,
    wo.pressure,
    wo.humidity,
    wo.visibility,
    wo.wind_speed,
    wo.wind_deg,
    wo.clouds_all,
    wo.recorded_at AS dt,
    wo.sunrise,
    wo.sunset,
    wo.created_at AS data_loaded_at
FROM {{ ref('stg_weather_observations') }} wo
JOIN {{ ref('stg_cities') }} c ON wo.city_id = c.city_id
JOIN {{ ref('stg_weather_conditions') }} wc ON wo.condition_id = wc.condition_id