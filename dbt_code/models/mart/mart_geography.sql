-- This model aggregates vacancy data at country, region, and municipality levels.
-- It is designed to be a clean, fast data source for BI tools and visualization
-- scripts (e.g., Python/Plotly) where geographic shapes (GeoJSON) are loaded separately.

with

fct_job_ads as (
    -- Renamed from 'job_ads' to be more explicit
    select
        location_id,
        vacancies
    from {{ ref('fct_job_ads') }}
),

dim_location as (
    -- Renamed from 'locations' to be more explicit
    select
        location_id,
        location_country_code,
        location_country,
        location_region_code,
        location_region,
        location_municipality_code,
        location_municipality
    from {{ ref('dim_location') }}
),

joined_facts_and_dims as (
    select
        fct_job_ads.vacancies,
        dim_location.location_country_code,
        dim_location.location_country,
        dim_location.location_region_code,
        dim_location.location_region,
        dim_location.location_municipality_code,
        dim_location.location_municipality
    from fct_job_ads
    join dim_location on fct_job_ads.location_id = dim_location.location_id
),

-- Use GROUPING SETS to efficiently aggregate at all three geographic levels
aggregated_with_hierarchy as (
    select
        sum(vacancies) as total_vacancies,

        -- The GROUPING() function helps us identify the aggregation level for each row
        case
            when grouping(location_municipality_code) = 0 then 'municipality'
            when grouping(location_region_code) = 0 then 'region'
            else 'country'
        end as location_level,

        location_country_code,
        location_country,
        location_region_code,
        location_region,
        location_municipality_code,
        location_municipality

    from joined_facts_and_dims
    group by grouping sets (
        -- Level 1: Country
        (location_country_code, location_country),

        -- Level 2: Region (while keeping country context)
        (location_country_code, location_country, location_region_code, location_region),

        -- Level 3: Municipality (while keeping all parent context)
        (location_country_code, location_country, location_region_code, location_region, location_municipality_code, location_municipality)
    )
),

-- Final step: Add a unified key and name for easy filtering and display
final as (
    select
        -- Metric to visualize
        agg.total_vacancies,

        -- The level of geography for this row (e.g., 'country', 'region')
        agg.location_level,

        -- A unified key to join against a GeoJSON file. This is the crucial column.
        coalesce(agg.location_municipality_code, agg.location_region_code, agg.location_country_code) as location_key,

        -- A unified name for display in tooltips or labels
        coalesce(agg.location_municipality, agg.location_region, agg.location_country) as location_display_name,

        -- The full hierarchical context remains available for filtering or drill-downs
        agg.location_country_code,
        agg.location_country,
        agg.location_region_code,
        agg.location_region,
        agg.location_municipality_code,
        agg.location_municipality

        -- The 'geometry' column and the join to dim_geography have been removed.

    from aggregated_with_hierarchy as agg
)

select *
from final
order by location_country_code, location_region_code nulls first, location_municipality_code nulls first
