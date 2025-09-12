with src_employer as (select * from {{ ref('src_employer') }})

select
    {{ dbt_utils.generate_surrogate_key(
        ['employer_name', 'employer_organization_number', 'employer_workplace']
        ) }} as employer_id, -- alpha-numerical order
    employer_organization_number,
    employer_name,
    employer_workplace,
    -- max() + group by for unqiue rows
    max(workplace_street_address) as workplace_street_address,
    max(workplace_region) as workplace_region,
    max(workplace_postcode) as workplace_postcode,
    max(workplace_city) as workplace_city,
    max(workplace_country) as workplace_country
from src_employer
group by employer_organization_number, employer_name, employer_workplace
