-- This test fails if the sum of occupation-level vacancies != group-level vacancies for any group

WITH occupation_sum_per_group AS (
  SELECT
    occupation_group,
    SUM(vacancy_count) AS sum_vacancies
  FROM {{ ref('mart_occupation_demand') }}
  WHERE level = 'occupation'
  GROUP BY occupation_group
),
group_metrics AS (
  SELECT
    occupation_group,
    vacancy_count AS group_vacancies
  FROM {{ ref('mart_occupation_demand') }}
  WHERE level = 'group'
)
SELECT
  g.occupation_group,
  g.group_vacancies,
  o.sum_vacancies
FROM group_metrics g
LEFT JOIN occupation_sum_per_group o
  ON g.occupation_group = o.occupation_group
WHERE g.group_vacancies != o.sum_vacancies