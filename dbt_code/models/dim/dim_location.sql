with src_location as (select * from {{ ref('src_location') }})

select
    {{ dbt_utils.generate_surrogate_key(
        ['location_country_code', 'location_municipality_code', 'location_region_code']
        ) }} as location_id,  -- alpha-numerical order
        location_country,
        location_country_code,
        location_region,
        location_region_code,
        location_municipality,
        location_municipality_code,
from src_location

qualify row_number() over (
    partition by location_id
    order by location_id
) = 1

order by location_country_code, location_region_code, location_municipality_code
