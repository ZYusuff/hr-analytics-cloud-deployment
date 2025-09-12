with src_occupation as (select * from {{ ref('src_occupation') }})

select
    {{ dbt_utils.generate_surrogate_key(['occupation_label']) }} as occupation_id,
    occupation_label,
    -- max() + group by for unqiue rows
    max(occupation_group) as occupation_group,
    max(occupation_field) as occupation_field
from src_occupation
group by occupation_label
