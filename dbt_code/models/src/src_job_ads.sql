with stg_job_ads as (select * from {{ source('job_ads', 'stg_ads') }})

select
    -- job_ads
    number_of_vacancies as vacancies,
    relevance,
    application_deadline,
    id as job_ad_id
from stg_job_ads
