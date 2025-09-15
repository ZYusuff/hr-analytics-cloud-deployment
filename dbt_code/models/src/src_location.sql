with

stg_job_ads as (select * from {{ source('job_ads', 'stg_ads') }}),
stg_coords as (select * from {{ source('job_ads', 'stg_coords') }}),

coords_pivot as (

select
    _dlt_parent_id,
    max(case when _dlt_list_idx = 0 then c.value end) as longitude,
    max(case when _dlt_list_idx = 1 then c.value end) as latitude
from stg_coords c
group by _dlt_parent_id

)

-- location
select
    workplace_address__country as location_country,
    workplace_address__country_code as location_country_code,
    workplace_address__region as location_region,
    workplace_address__region_code as location_region_code,
    workplace_address__municipality as location_municipality,
    workplace_address__municipality_code as location_municipality_code,
    c.longitude,
    c.latitude
from stg_job_ads p
join coords_pivot c on p._dlt_id = c._dlt_parent_id
