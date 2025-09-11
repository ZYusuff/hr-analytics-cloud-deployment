with src as (
    select * from {{ ref('src') }}
)

select
{{ dbt_utils.generate_surrogate_key([
        'employer_organization_number',
        'employer_name',
        'employer_workplace'
    ]) }} as employer_id,
    employer_organization_number,
    employer_name,
    employer_workplace,
    workplace_street_address,
    workplace_region,
    workplace_postcode,
    workplace_city,
    workplace_country,
    current_timestamp() as record_loaded_at
from src
