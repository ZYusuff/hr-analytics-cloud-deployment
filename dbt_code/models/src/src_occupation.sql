with stg_job_ads as (select * from {{ source('job_ads', 'stg_ads') }})

select
    -- occupation
    occupation__label as occupation_label,
    occupation_group__label as occupation_group,
    occupation_field__label as occupation_field
from stg_job_ads
