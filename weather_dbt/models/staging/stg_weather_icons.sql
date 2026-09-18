select
    icons_id,
    icon_code
from {{ source('raw', 'weather_icons') }}
