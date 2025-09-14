with src_jobsearch as (select * from {{ ref('src_jobsearch') }})

select
    {{ dbt_utils.generate_surrogate_key(
        ['access_to_own_car','driver_license','experience_required']
        ) }} as auxilliary_attributes_id,  -- alpha-numerical order
    experience_required,
    driver_license,
    access_to_own_car
from src_jobsearch

qualify row_number() over (
    partition by auxilliary_attributes_id
    order by auxilliary_attributes_id
) = 1
