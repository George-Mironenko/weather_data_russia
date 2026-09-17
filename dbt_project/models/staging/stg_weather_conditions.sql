SELECT
    wc.condition_id,
    wmt.main_name,
    wc.description,
    wi.icon_code
FROM {{ source('raw', 'weather_conditions') }} wc
LEFT JOIN {{ source('raw', 'weather_main_types') }} wmt ON wc.main = wmt.main_id
LEFT JOIN {{ source('raw', 'weather_icons') }} wi ON wc.icon = wi.icons_id