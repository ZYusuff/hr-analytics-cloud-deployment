/*
  This mart model aggregates job demand data by occupation hierarchy
  (field, group, and specific occupation label), now using publication_date.
*/

WITH base AS (
  SELECT * FROM {{ ref('fct_job_ads') }}
),

occupation_dim AS (
  SELECT * FROM {{ ref('dim_occupation') }}
),


-- Aggregate by occupation field
occupation_field_metrics AS (
  SELECT 
    o.occupation_field,
    NULL AS occupation_group,
    NULL AS occupation_label,
    SUM(b.vacancies) AS vacancy_count
  FROM base b
  LEFT JOIN occupation_dim o ON b.occupation_id = o.occupation_id
  GROUP BY o.occupation_field
),

-- Aggregate by occupation group
occupation_group_metrics AS (
  SELECT
    o.occupation_field,
    o.occupation_group,
    NULL AS occupation_label,
    SUM(b.vacancies) AS vacancy_count
  FROM base b
  LEFT JOIN occupation_dim o ON b.occupation_id = o.occupation_id
  GROUP BY o.occupation_field, o.occupation_group
),

-- Aggregate by specific occupation label
occupation_label_metrics AS (
  SELECT
    o.occupation_field,
    o.occupation_group,
    o.occupation_label,
    SUM(b.vacancies) AS vacancy_count
  FROM base b
  LEFT JOIN occupation_dim o ON b.occupation_id = o.occupation_id
  GROUP BY o.occupation_field, o.occupation_group, o.occupation_label
)

-- Final combined mart model
SELECT 'field' AS level, * FROM occupation_field_metrics
UNION ALL
SELECT 'group' AS level, * FROM occupation_group_metrics
UNION ALL
SELECT 'occupation' AS level, * FROM occupation_label_metrics
