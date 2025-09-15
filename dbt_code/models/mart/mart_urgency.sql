/*
  This mart model focuses on job urgency and candidate requirements
  to help prioritize recruitment efforts
*/

WITH base AS (
  SELECT * FROM {{ ref('fct_job_ads') }}
),

job_details_dim AS (
  SELECT * FROM {{ ref('dim_job_details') }}
),

occupation_dim AS (
  SELECT * FROM {{ ref('dim_occupation') }}
),

urgency_int AS (SELECT
  jd.job_ad_id,
  b.application_deadline,
  DATEDIFF('day', CURRENT_DATE(), b.application_deadline) AS days_to_deadline,
  CASE 
    WHEN DATEDIFF('day', CURRENT_DATE(), b.application_deadline) <= 7 THEN 'urgent_7days'
    WHEN DATEDIFF('day', CURRENT_DATE(), b.application_deadline) <= 14 THEN 'closing_14days'
    WHEN DATEDIFF('day', CURRENT_DATE(), b.application_deadline) <= 30 THEN 'closing_30days'
    ELSE 'normal'
  END AS urgency_category,
  b.vacancies AS number_vacancies,
  o.occupation_field,
  o.occupation_group,
  o.occupation_label
FROM base b
LEFT JOIN job_details_dim jd ON b.job_details_id = jd.job_details_id
LEFT JOIN occupation_dim o ON b.occupation_id = o.occupation_id
WHERE days_to_deadline >= 0  -- Only consider active job ads
),


urgency_field_metrics AS (
  SELECT 
    occupation_field,
    NULL AS occupation_group,
    NULL AS occupation_label,
    urgency_category,
    COUNT(job_ad_id) AS total_job_ads,
    SUM(number_vacancies) AS total_vacancies
  FROM urgency_int 
  GROUP BY occupation_field, urgency_category
),

-- Aggregate by occupation group
urgency_group_metrics AS (
  SELECT
    occupation_field,
    occupation_group,
    NULL AS occupation_label,
    urgency_category,
    COUNT(job_ad_id) AS total_job_ads,
    SUM(number_vacancies) AS total_vacancies
  FROM urgency_int
  GROUP BY occupation_field, occupation_group, urgency_category
),

-- Aggregate by specific occupation label
urgency_label_metrics AS (
  SELECT
    occupation_field,
    occupation_group,
    occupation_label,
    urgency_category,
    COUNT(job_ad_id) AS total_job_ads,
    SUM(number_vacancies) AS total_vacancies
  FROM urgency_int
  GROUP BY occupation_field, occupation_group, occupation_label, urgency_category
)

-- Final combined mart model
SELECT 'field' AS level, * FROM urgency_field_metrics
UNION ALL
SELECT 'group' AS level, * FROM urgency_group_metrics
UNION ALL
SELECT 'occupation' AS level, * FROM urgency_label_metrics
ORDER BY level, occupation_field, occupation_group, occupation_label, urgency_category;
