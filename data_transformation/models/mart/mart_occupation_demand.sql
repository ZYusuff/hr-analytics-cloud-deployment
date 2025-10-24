/*
  Hierarchical analysis mart for occupation demand
  Focuses on total demand and rankings by occupation hierarchy
*/

WITH job_ads_fct AS (
    SELECT * FROM {{ ref('fct_job_ads') }}
),

job_details_dim AS (
    SELECT * FROM {{ ref('dim_job_details') }}
),

occupation_dim AS (
    SELECT * FROM {{ ref('dim_occupation') }}
),

-- Base join between facts and dimensions with active job filtering
base AS (
    SELECT
        jd.job_ad_id,
        ja.publication_date,
        ja.vacancies,
        ja.occupation_id,
        o.occupation_field,
        o.occupation_group,
        o.occupation_label,
        DATEDIFF('day', CURRENT_DATE(), ja.application_deadline) AS days_to_deadline
    FROM job_ads_fct ja
    LEFT JOIN job_details_dim jd ON ja.job_details_id = jd.job_details_id
    LEFT JOIN occupation_dim o ON ja.occupation_id = o.occupation_id
    WHERE DATEDIFF('day', CURRENT_DATE(), ja.application_deadline) >= 0  -- Only consider active job ads
),

-- Aggregate by occupation field
occupation_field_metrics AS (
    SELECT 
        occupation_field,
        NULL AS occupation_group,
        NULL AS occupation_label,
        SUM(vacancies) AS vacancy_count,
        COUNT(DISTINCT job_ad_id) AS job_ads_count
    FROM base
    GROUP BY occupation_field
),

-- Aggregate by occupation group
occupation_group_metrics AS (
    SELECT
        occupation_field,
        occupation_group,
        NULL AS occupation_label,
        SUM(vacancies) AS vacancy_count,
        COUNT(DISTINCT job_ad_id) AS job_ads_count
    FROM base
    GROUP BY occupation_field, occupation_group
),

-- Aggregate by specific occupation label
occupation_label_metrics AS (
    SELECT
        occupation_field,
        occupation_group,
        occupation_label,
        SUM(vacancies) AS vacancy_count,
        COUNT(DISTINCT job_ad_id) AS job_ads_count
    FROM base
    GROUP BY occupation_field, occupation_group, occupation_label
),

-- Combined hierarchical metrics
combined_metrics AS (
    SELECT 'field' AS level, * FROM occupation_field_metrics
    UNION ALL
    SELECT 'group' AS level, * FROM occupation_group_metrics
    UNION ALL
    SELECT 'occupation' AS level, * FROM occupation_label_metrics
)

-- Add rankings within each level and parent category
SELECT
    level,
    occupation_field,
    occupation_group,
    occupation_label,
    vacancy_count,
    job_ads_count,
    -- Rank within overall level (field, group, occupation)
    ROW_NUMBER() OVER (
        PARTITION BY level 
        ORDER BY vacancy_count DESC
    ) AS overall_rank,
    -- Rank within parent category (for groups within field, occupations within group)
    CASE
        WHEN level = 'group' THEN 
            ROW_NUMBER() OVER (
                PARTITION BY level, occupation_field 
                ORDER BY vacancy_count DESC
            )
        WHEN level = 'occupation' THEN
            ROW_NUMBER() OVER (
                PARTITION BY level, occupation_field, occupation_group 
                ORDER BY vacancy_count DESC
            )
        ELSE 1
    END AS parent_category_rank
FROM combined_metrics
ORDER BY level, occupation_field, occupation_group, occupation_label
