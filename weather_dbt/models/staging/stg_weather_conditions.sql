select
    condition_id,
    main,
    description,
    icon
from {{ source('raw', 'weather_conditions') }}
