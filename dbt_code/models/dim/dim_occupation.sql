with src_jobsearch as (select * from {{ ref('src_jobsearch') }})

select
    {{ dbt_utils.generate_surrogate_key(['occupation_label']) }} as occupation_id,
    occupation_label,
    occupation_group,
    occupation_field
from src_jobsearch

qualify row_number() over (
    partition by occupation_id
    order by occupation_id
) = 1

order by occupation_field, occupation_group, occupation_label
