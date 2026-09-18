select
    main_id,
    main_name
from {{ source('raw', 'weather_main_types') }}
