{{ config(materialized='view') }}

-- Replaces the hand-written `CREATE VIEW all_data` that used to live in
-- sql_scripts/script_create.sql. Consumed by dags/load_to_cloud.py.

select
    c.name              as city_name,
    c.lat               as lat,
    c.lon               as lon,
    cnt.name            as country_name,
    w.condition_id      as weather_id,
    wmt.main_name       as weather_main,
    wc.description      as weather_description,
    wi.icon_code        as weather_icon,
    w.temp              as temp,
    w.temp_min          as temp_min,
    w.temp_max          as temp_max,
    w.pressure          as pressure,
    w.humidity          as humidity,
    w.visibility        as visibility,
    w.wind_speed        as wind_speed,
    w.wind_deg          as wind_deg,
    w.clouds_all        as clouds_all,
    w.recorded_at       as dt,
    w.sunrise           as sunrise,
    w.sunset            as sunset,
    w.created_at        as data_loaded_at

from {{ ref('stg_weather_observations') }} w
join {{ ref('stg_cities') }}             c   on w.city_id = c.city_id
join {{ ref('stg_country') }}            cnt on c.country = cnt.id
join {{ ref('stg_weather_conditions') }} wc  on w.condition_id = wc.condition_id
join {{ ref('stg_weather_main_types') }} wmt on wc.main = wmt.main_id
join {{ ref('stg_weather_icons') }}      wi  on wc.icon = wi.icons_id
