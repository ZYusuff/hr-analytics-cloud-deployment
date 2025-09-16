-- 1. STAGING: Select required columns from upstream models

WITH

fct_job_ads AS (
    SELECT
        location_id,
        occupation_id,
        vacancies
    FROM {{ ref('fct_job_ads') }}
),

dim_location AS (
    -- Select both code and name columns for the geographic hierarchy
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
    -- Remove the fine-grained 'occupation_label' to create a coarser hierarchy
    SELECT
        occupation_id,
        occupation_field,
        occupation_group
    FROM {{ ref('dim_occupation') }}
),


-- 2. JOINING: Combine facts with dimensions

joined_facts_and_dims AS (
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
        dim_occ.occupation_group

    FROM fct_job_ads AS fct
    INNER JOIN dim_location AS dim_loc
        ON fct.location_id = dim_loc.location_id
    -- Use LEFT JOIN to avoid losing facts for occupations not yet in the dimension.
    -- These are handled (filtered out) in the next step.
    LEFT JOIN dim_occupation AS dim_occ
        ON fct.occupation_id = dim_occ.occupation_id
),


-- 3. AGGREGATION: Calculate totals across all hierarchy combinations

base_aggregations AS (
    SELECT
        SUM(vacancies) AS total_vacancies,

        -- Geography dimensions
        location_country_code,
        location_country,
        location_region_code,
        location_region,
        location_municipality_code,
        location_municipality,

        -- Occupation dimensions
        occupation_field,
        occupation_group,

        -- GROUPING() functions to identify aggregation levels in the next step
        GROUPING(location_municipality_code) AS is_municipality_agg,
        GROUPING(location_region_code) AS is_region_agg,
        GROUPING(occupation_group) AS is_group_agg,
        GROUPING(occupation_field) AS is_field_agg

    FROM joined_facts_and_dims
    -- This filter removes vacancies where the occupation was not found in dim_occupation.
    -- To include them, you could COALESCE nulls to 'Unknown' in the dim_occupation CTE.
    WHERE
        occupation_field IS NOT NULL
        AND occupation_group IS NOT NULL
    GROUP BY
        GROUPING SETS (
            -- This generates aggregations for all 9 combinations of the two hierarchies.

            -- Geography: COUNTRY x Occupation: Total, by Field, by Group
            (location_country_code, location_country),
            (location_country_code, location_country, occupation_field),
            (location_country_code, location_country, occupation_field, occupation_group),

            -- Geography: REGION x Occupation: Total, by Field, by Group
            (location_country_code, location_country, location_region_code, location_region),
            (location_country_code, location_country, location_region_code, location_region, occupation_field),
            (location_country_code, location_country, location_region_code, location_region, occupation_field, occupation_group),

            -- Geography: MUNICIPALITY x Occupation: Total, by Field, by Group
            (location_country_code, location_country, location_region_code, location_region, location_municipality_code, location_municipality),
            (location_country_code, location_country, location_region_code, location_region, location_municipality_code, location_municipality, occupation_field),
            (location_country_code, location_country, location_region_code, location_region, location_municipality_code, location_municipality, occupation_field, occupation_group)
        )
),


-- 4. LABELING: Create human-readable labels for hierarchy levels

labeled_aggregations AS (
    SELECT
        total_vacancies,

        -- Decode the grouping() flags into meaningful labels for BI tools
        CASE
            WHEN is_municipality_agg = 0 THEN 'municipality'
            WHEN is_region_agg = 0 THEN 'region'
            ELSE 'country'
        END AS location_level,

        CASE
            WHEN is_group_agg = 0 THEN 'group'
            WHEN is_field_agg = 0 THEN 'field'
            ELSE 'all_occupations'
        END AS occupation_level,

        -- Passthrough original dimension columns for drill-down capabilities
        location_country_code,
        location_country,
        location_region_code,
        location_region,
        location_municipality_code,
        location_municipality,
        occupation_field,
        occupation_group

    FROM base_aggregations
),


-- 5. FINAL PRESENTATION: Add unified keys and names for BI tools

final AS (
    SELECT
        -- Metric
        labeled.total_vacancies,

        -- Hierarchy level identifiers
        labeled.location_level,
        labeled.occupation_level,

        -- A unified key for joining to a GeoJSON/shapefile in a mapping tool.
        -- This creates one stable column for map joins, regardless of geo level.
        COALESCE(
            labeled.location_municipality_code,
            labeled.location_region_code,
            labeled.location_country_code
        ) AS location_key,

        -- A unified name for the location, using the most granular name available.
        COALESCE(
            labeled.location_municipality,
            labeled.location_region,
            labeled.location_country
        ) AS location_display_name,

        -- A unified name for clean display in chart tooltips or labels.
        COALESCE(
            labeled.occupation_group,
            labeled.occupation_field
        ) AS occupation_display_name,

        -- The complete set of hierarchical columns remains available for advanced filtering.
        labeled.location_country_code,
        labeled.location_country,
        labeled.location_region_code,
        labeled.location_region,
        labeled.location_municipality_code,
        labeled.location_municipality,
        labeled.occupation_field,
        labeled.occupation_group

    FROM labeled_aggregations AS labeled
)

SELECT * FROM final
-- Order to show hierarchy logically, with totals (NULLs) appearing before details.
ORDER BY
    location_country_code,
    location_country,
    location_region_code NULLS FIRST,
    location_region NULLS FIRST,
    location_municipality_code NULLS FIRST,
    location_municipality NULLS FIRST,
    occupation_field NULLS FIRST,
    occupation_group NULLS FIRST
