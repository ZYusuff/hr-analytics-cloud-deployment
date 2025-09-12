with stg_job_ads as (select * from {{ source('job_ads', 'stg_ads') }})

select
    -- job_ads
    number_of_vacancies as vacancies,
    relevance,
    application_deadline,

    -- natrual keys for base
    -- auxilliary_attributes
    experience_required,
    driving_license_required as driver_license,
    access_to_own_car,
    -- employer
    employer__name as employer_name,
    employer__workplace as employer_workplace,
    employer__organization_number as employer_organization_number,
    -- job_details
    id as job_ad_id,
    -- occupation
    occupation__label as occupation_label,
    occupation_group__label as occupation_group,
    occupation_field__label as occupation_field
from stg_job_ads
