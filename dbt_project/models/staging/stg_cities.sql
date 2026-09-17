SELECT
    c.city_id,
    c.name AS city_name,
    c.lat,
    c.lon,
    cnt.id AS country_id,
    cnt.name AS country_name
FROM {{ source('raw', 'cities') }} c
LEFT JOIN {{ source('raw', 'country') }} cnt ON c.country = cnt.id