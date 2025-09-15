-- This test fails if the sum of group-level vacancies != field-level vacancies for any field

WITH group_sum_per_field AS (
  SELECT
    occupation_field,
    SUM(vacancy_count) AS sum_vacancies
  FROM {{ ref('mart_occupation_demand') }}
  WHERE level = 'group'
  GROUP BY occupation_field
),
field_metrics AS (
  SELECT
    occupation_field,
    vacancy_count AS field_vacancies
  FROM {{ ref('mart_occupation_demand') }}
  WHERE level = 'field'
)
SELECT
  f.occupation_field,
  f.field_vacancies,
  g.sum_vacancies
FROM field_metrics f
LEFT JOIN group_sum_per_field g
  ON f.occupation_field = g.occupation_field
WHERE f.field_vacancies != g.sum_vacancies