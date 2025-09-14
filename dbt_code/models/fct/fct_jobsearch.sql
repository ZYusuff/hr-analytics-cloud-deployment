with src_jobsearch as (select * from {{ ref('src_jobsearch') }})

select
    job_ad_id,

    {{ dbt_utils.generate_surrogate_key(
        ['access_to_own_car','driver_license','experience_required']
        ) }} as auxilliary_attributes_id,  -- alpha-numerical order
    {{ dbt_utils.generate_surrogate_key(
        ['employer_name', 'employer_organization_number', 'employer_workplace']
    ) }} as employer_id,  -- alpha-numerical order
    {{ dbt_utils.generate_surrogate_key(['job_ad_id']) }} as job_details_id,
    {{ dbt_utils.generate_surrogate_key(['occupation_label']) }} as occupation_id,

    relevance,
    vacancies,
    application_deadline
from src_jobsearch
