with src_jobsearch as (select * from {{ ref('src_jobsearch') }})

select
    {{ dbt_utils.generate_surrogate_key(['job_ad_id']) }} as job_details_id,
    headline,
    description,
    description_html_formatted,
    employment_type,
    duration,
    salary_type,
    scope_of_work_min,
    scope_of_work_max

from src_jobsearch

qualify row_number() over (
    partition by job_details_id
    order by job_details_id
) = 1

order by job_ad_id
