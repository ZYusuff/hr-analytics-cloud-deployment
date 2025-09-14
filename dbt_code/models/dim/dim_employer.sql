with src_jobsearch as (select * from {{ ref('src_jobsearch') }})

select
    {{ dbt_utils.generate_surrogate_key(
        ['employer_name', 'employer_organization_number', 'employer_workplace']
        ) }} as employer_id,  -- alpha-numerical order
    employer_name,
    employer_workplace,
    employer_organization_number,
    workplace_street_address,
    workplace_postcode,
    workplace_city,
    workplace_region,
    workplace_country
from src_jobsearch

qualify row_number() over (
    partition by employer_id
    order by employer_id
) = 1

order by workplace_country, workplace_region, workplace_city
