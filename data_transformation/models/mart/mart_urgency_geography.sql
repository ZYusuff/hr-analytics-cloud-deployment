-- This model calculates job urgency metrics (ad counts, vacancy counts)
-- across different geographic hierarchy levels (country, region, municipality)
-- and allows filtering by occupation.

-- 1. STAGING: Select required columns from upstream models
WITH

fct_job_ads AS (
    SELECT
        location_id,
        occupation_id,
        vacancies,
        application_deadline
    FROM {{ ref('fct_job_ads') }}
),

dim_location AS (
    SELECT
        location_id,
        location_country_code,
        location_region_code,
        location_municipality_code,
        location_country,
        location_region,
        location_municipality
    FROM {{ ref('dim_location') }}
),

dim_occupation AS (
    SELECT
        occupation_id,
        occupation_field,
        occupation_group
    FROM {{ ref('dim_occupation') }}
),

-- 2. PREPARATION: Add day counts and join sources
-- This CTE prepares the raw data for aggregation by joining facts and dimensions
-- and calculating the days to the deadline for each job ad.
prepared_data AS (
    SELECT
        fct.vacancies,
        -- Geography columns
        dim_loc.location_country_code,
        dim_loc.location_country,
        dim_loc.location_region_code,
        dim_loc.location_region,
        dim_loc.location_municipality_code,
        dim_loc.location_municipality,
        -- Occupation columns
        dim_occ.occupation_field,
        dim_occ.occupation_group,
        -- Urgency calculation
        DATEDIFF('day', CURRENT_DATE(), fct.application_deadline) AS days_to_deadline

    FROM fct_job_ads AS fct
    INNER JOIN dim_location AS dim_loc
        ON fct.location_id = dim_loc.location_id
    LEFT JOIN dim_occupation AS dim_occ
        ON fct.occupation_id = dim_occ.occupation_id
    WHERE
        -- Only consider active job ads with a future or current deadline
        DATEDIFF('day', CURRENT_DATE(), fct.application_deadline) >= 0
        -- Filter out ads without a matching occupation to ensure data quality
        AND dim_occ.occupation_field IS NOT NULL
        AND dim_occ.occupation_group IS NOT NULL
),

-- 3. AGGREGATION: Calculate total vacancies for each geo/urgency/occupation combination
-- GROUPING SETS efficiently create aggregates for region and municipality in one pass.
aggregated AS (
    SELECT
        -- The primary metric for the heatmap's color intensity
        SUM(vacancies) AS total_vacancies,
        COUNT(*) AS total_job_ads,

        -- The dimension for filtering/slicing the heatmap
        CASE
            WHEN days_to_deadline <= 7 THEN 'urgent_7days'
            WHEN days_to_deadline <= 14 THEN 'closing_14days'
            WHEN days_to_deadline <= 30 THEN 'closing_30days'
            ELSE 'normal'
        END AS urgency_category,

        -- Geographic dimensions
        location_country_code,
        location_country,
        location_region_code,
        location_region,
        location_municipality_code,
        location_municipality,
        
        -- Occupation dimensions
        occupation_field,
        occupation_group,

        -- Grouping flag to identify the aggregation level (region vs. municipality)
        GROUPING(location_municipality_code) AS is_municipality_agg

    FROM prepared_data
    GROUP BY
        GROUPING SETS (
            -- This creates aggregations for:
            -- 1. Region x Occupation x Urgency
            (location_country_code, location_country, location_region_code, location_region, urgency_category, occupation_field, occupation_group),

            -- 2. Municipality x Occupation x Urgency
            (location_country_code, location_country, location_region_code, location_region, location_municipality_code, location_municipality, urgency_category, occupation_field, occupation_group)
        )
),

-- 4. FINAL PRESENTATION: Create unified columns for easy use in BI tools
final AS (
    SELECT
        -- Metrics
        agg.total_vacancies,
        agg.total_job_ads,

        -- Filter Dimension
        agg.urgency_category,

        -- Hierarchy level identifier
        -- This lets the user switch between a 'Region' view and a 'Municipality' view
        CASE
            WHEN agg.is_municipality_agg = 0 THEN 'municipality'
            ELSE 'region'
        END AS location_level,
        
        -- UNIFIED GEOGRAPHIC KEY: The most important column for your heatmap.
        -- This provides one stable column to join against your shapefile/GeoJSON.
        COALESCE(
            agg.location_municipality_code,
            agg.location_region_code
        ) AS location_key,

        -- Unified name for tooltips and labels
        COALESCE(
            agg.location_municipality,
            agg.location_region
        ) AS location_display_name,

        -- Passthrough original dimension columns for advanced filtering
        agg.location_country_code,
        agg.location_country,
        agg.location_region_code,
        agg.location_region,
        agg.location_municipality_code,
        agg.location_municipality,
        agg.occupation_field,
        agg.occupation_group

    FROM aggregated AS agg
)

SELECT *
FROM final
ORDER BY
    location_country_code,
    location_region_code NULLS FIRST,
    location_municipality_code NULLS FIRST,
    occupation_field,
    occupation_group,
    urgency_category
