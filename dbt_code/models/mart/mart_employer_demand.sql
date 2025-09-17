/*
  Hierarchical analysis mart for employer demand
  Focuses on identifying employers with highest vacancy counts
  and tracking new employers entering the market
*/

WITH job_ads_fct AS (
    SELECT * FROM {{ ref('fct_job_ads') }}
),

job_details_dim AS (
    SELECT * FROM {{ ref('dim_job_details') }}
),

employer_dim AS (
    SELECT * FROM {{ ref('dim_employer') }}
),

occupation_dim AS (
    SELECT * FROM {{ ref('dim_occupation') }}
),

-- Base join between facts and dimensions with active job filtering
base AS (
    SELECT
        jd.job_ad_id,
        ja.employer_id,
        e.employer_name,
        ja.publication_date,
        ja.vacancies,
        o.occupation_field,
        o.occupation_group,
        DATEDIFF('day', CURRENT_DATE(), ja.application_deadline) AS days_to_deadline
    FROM job_ads_fct ja
    LEFT JOIN job_details_dim jd ON ja.job_details_id = jd.job_details_id
    LEFT JOIN employer_dim e ON ja.employer_id = e.employer_id
    LEFT JOIN occupation_dim o ON ja.occupation_id = o.occupation_id
    WHERE DATEDIFF('day', CURRENT_DATE(), ja.application_deadline) >= 0  -- Only consider active job ads
),

-- Calculate first publication date per employer (for new employer identification)
employer_first_publication AS (
    SELECT
        employer_id,
        MIN(publication_date) AS first_publication_date
    FROM base
    GROUP BY employer_id
),

-- Identify new employers (those that first appeared in the last 30 days)
current_date_info AS (
    SELECT MAX(publication_date) AS latest_date FROM base
),

-- Aggregate by employer within occupation field
employer_field_metrics AS (
    SELECT 
        b.employer_id,
        b.employer_name,
        b.occupation_field,
        NULL AS occupation_group,
        SUM(b.vacancies) AS vacancy_count,
        COUNT(DISTINCT b.job_ad_id) AS job_ads_count,
        CASE 
            WHEN DATEDIFF('day', efp.first_publication_date, cd.latest_date) <= 30 THEN 1
            ELSE 0
        END AS is_new_employer
    FROM base b
    JOIN employer_first_publication efp ON b.employer_id = efp.employer_id
    CROSS JOIN current_date_info cd
    GROUP BY 
        b.employer_id, 
        b.employer_name, 
        b.occupation_field, 
        efp.first_publication_date,
        cd.latest_date
),

-- Aggregate by employer within occupation group
employer_group_metrics AS (
    SELECT 
        b.employer_id,
        b.employer_name,
        b.occupation_field,
        b.occupation_group,
        SUM(b.vacancies) AS vacancy_count,
        COUNT(DISTINCT b.job_ad_id) AS job_ads_count,
        CASE 
            WHEN DATEDIFF('day', efp.first_publication_date, cd.latest_date) <= 30 THEN 1
            ELSE 0
        END AS is_new_employer
    FROM base b
    JOIN employer_first_publication efp ON b.employer_id = efp.employer_id
    CROSS JOIN current_date_info cd
    GROUP BY 
        b.employer_id, 
        b.employer_name, 
        b.occupation_field, 
        b.occupation_group,
        efp.first_publication_date,
        cd.latest_date
),

-- Combined hierarchical metrics
combined_metrics AS (
    SELECT 'field' AS level, * FROM employer_field_metrics
    UNION ALL
    SELECT 'group' AS level, * FROM employer_group_metrics
)

-- Add rankings and final selection
SELECT
    level,
    employer_id,
    employer_name,
    occupation_field,
    occupation_group,
    vacancy_count,
    job_ads_count,
    is_new_employer,
    -- Count of total employers (for KPIs)
    COUNT(*) OVER (PARTITION BY level, occupation_field) AS total_employer_count,
    -- Count of new employers (for KPIs)
    SUM(is_new_employer) OVER (PARTITION BY level, occupation_field) AS new_employer_count,
    -- Rank within overall level
    ROW_NUMBER() OVER (
        PARTITION BY level 
        ORDER BY vacancy_count DESC
    ) AS overall_rank,
    -- Rank within parent category
    CASE
        WHEN level = 'field' THEN 
            ROW_NUMBER() OVER (
                PARTITION BY level, occupation_field 
                ORDER BY vacancy_count DESC
            )
        WHEN level = 'group' THEN
            ROW_NUMBER() OVER (
                PARTITION BY level, occupation_field, occupation_group 
                ORDER BY vacancy_count DESC
            )
        ELSE 1
    END AS parent_category_rank
FROM combined_metrics
ORDER BY level, occupation_field, occupation_group, vacancy_count DESC
