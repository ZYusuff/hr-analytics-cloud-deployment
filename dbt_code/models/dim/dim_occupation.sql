with src as (select * from {{ ref('src') }})

-- we use aggregate function max() for deduplicate, but there are more alternative codes one can use for this purpose
select
    {{ dbt_utils.generate_surrogate_key(['occupation_label']) }} as occupation_id,
    occupation_label,
    max(occupation_group) as occupation_group,
    max(occupation_field) as occupation_field
from src
group by occupation_label
