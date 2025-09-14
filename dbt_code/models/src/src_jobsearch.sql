with stg_job_ads as (select * from {{ source('job_ads', 'stg_ads') }})

select
    -- source id
    id as job_ad_id,

    -- auxilliary_attributes
    experience_required,
    driving_license_required as driver_license,
    access_to_own_car,

    -- employer
    employer__name as employer_name,
    employer__workplace as employer_workplace,
    employer__organization_number as employer_organization_number,
    {{ capitalize_first_letter('workplace_address__street_address') }} as workplace_street_address,
    workplace_address__postcode as workplace_postcode,
    {{ capitalize_first_letter('workplace_address__city') }} as workplace_city,
    workplace_address__region as workplace_region,
    workplace_address__country as workplace_country,

    -- job_details
    headline,
    description__text as description,
    description__text_formatted as description_html_formatted,
    employment_type__label as employment_type,
    duration__label as duration,
    salary_type__label as salary_type,
    scope_of_work__min as scope_of_work_min,
    scope_of_work__max as scope_of_work_max,

    -- occupation
    occupation__label as occupation_label,
    occupation_group__label as occupation_group,
    occupation_field__label as occupation_field,

    -- job_ad
    relevance,
    number_of_vacancies as vacancies,
    application_deadline
from stg_job_ads
