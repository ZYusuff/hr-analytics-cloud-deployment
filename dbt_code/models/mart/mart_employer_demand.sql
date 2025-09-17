/*
  This mart model analyzes employer demand trends by aggregating job vacancies by employer
  and including occupation field/group information for filtering.
  It provides insights into which employers have the highest number of vacancies,
  identifies new employers, and enables analysis of employer demand by occupation.
*/

WITH base AS (
  SELECT * FROM {{ ref('fct_job_ads') }}
),

employer_dim AS (
  SELECT * FROM {{ ref('dim_employer') }}
),

occupation_dim AS (
  SELECT * FROM {{ ref('dim_occupation') }}
),

-- Current date reference (for identifying new employers)
date_info AS (
  SELECT 
    MAX(publication_date) AS current_date
  FROM base
),

-- Calculate first publication date per employer
employer_first_publication AS (
  SELECT
    e.employer_id,
    MIN(b.publication_date) AS first_publication_date
  FROM base b
  JOIN employer_dim e ON b.employer_id = e.employer_id
  GROUP BY e.employer_id
),

-- Identify new employers (first publication in the last 30 days)
new_employers AS (
  SELECT
    e.employer_id,
    CASE 
      WHEN DATEDIFF(day, efp.first_publication_date, d.current_date) <= 30 THEN 1
      ELSE 0
    END AS is_new_employer
  FROM employer_dim e
  JOIN employer_first_publication efp ON e.employer_id = efp.employer_id
  CROSS JOIN date_info d
),

-- Aggregate vacancies by employer and occupation field
employer_field_metrics AS (
  SELECT 
    e.employer_id,
    e.employer_name,
    e.employer_organization_number,
    o.occupation_field,
    NULL AS occupation_group,
    SUM(b.vacancies) AS vacancy_count,
    COUNT(DISTINCT e.employer_id) AS employer_count,
    SUM(ne.is_new_employer) AS new_employer_count,
    ROW_NUMBER() OVER (PARTITION BY o.occupation_field ORDER BY SUM(b.vacancies) DESC) AS rank_in_field
  FROM base b
  JOIN employer_dim e ON b.employer_id = e.employer_id
  JOIN occupation_dim o ON b.occupation_id = o.occupation_id
  JOIN new_employers ne ON e.employer_id = ne.employer_id
  GROUP BY e.employer_id, e.employer_name, e.employer_organization_number, o.occupation_field
),

-- Aggregate vacancies by employer and occupation group
employer_group_metrics AS (
  SELECT 
    e.employer_id,
    e.employer_name,
    e.employer_organization_number,
    o.occupation_field,
    o.occupation_group,
    SUM(b.vacancies) AS vacancy_count,
    COUNT(DISTINCT e.employer_id) AS employer_count,
    SUM(ne.is_new_employer) AS new_employer_count,
    ROW_NUMBER() OVER (PARTITION BY o.occupation_field, o.occupation_group ORDER BY SUM(b.vacancies) DESC) AS rank_in_group
  FROM base b
  JOIN employer_dim e ON b.employer_id = e.employer_id
  JOIN occupation_dim o ON b.occupation_id = o.occupation_id
  JOIN new_employers ne ON e.employer_id = ne.employer_id
  GROUP BY e.employer_id, e.employer_name, e.employer_organization_number, o.occupation_field, o.occupation_group
)

-- Final combined mart model
SELECT 
  'field' AS level,
  employer_id,
  employer_name,
  employer_organization_number,
  occupation_field,
  occupation_group,
  vacancy_count,
  employer_count,
  new_employer_count,
  rank_in_field AS rank
FROM employer_field_metrics

UNION ALL

SELECT 
  'group' AS level,
  employer_id,
  employer_name,
  employer_organization_number,
  occupation_field,
  occupation_group,
  vacancy_count,
  employer_count,
  new_employer_count,
  rank_in_group AS rank
FROM employer_group_metrics
