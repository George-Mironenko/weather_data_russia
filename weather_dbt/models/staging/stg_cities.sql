select
    city_id,
    name,
    country,
    lat,
    lon
from {{ source('raw', 'cities') }}
