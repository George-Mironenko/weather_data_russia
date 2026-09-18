select
    id,
    name
from {{ source('raw', 'country') }}
