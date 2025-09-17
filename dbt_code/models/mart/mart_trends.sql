/*
  Time series analysis mart for job market trends
  - Tracks vacancies over time by publication date
  - Supports trend analysis across multiple dimensions (occupation field, group)
  - Designed for line chart visualization with:
    * publication_date on x-axis
    * number of vacancies on y-axis
    * filterable by occupation field and group
*/

WITH job_ads_fct AS (
    SELECT * FROM {{ ref('fct_job_ads') }}
),

occupation_dim AS (
    SELECT * FROM {{ ref('dim_occupation') }}
),

-- Base join between facts and dimensions
base AS (
    SELECT
        job_ads_fct.publication_date,
        job_ads_fct.vacancies,
        occupation_dim.occupation_field,
        occupation_dim.occupation_group,
        occupation_dim.occupation_label
    FROM job_ads_fct
    LEFT JOIN occupation_dim
        ON job_ads_fct.occupation_id = occupation_dim.occupation_id
),

-- Convert publication_date to truncated date format (day level)
-- This allows for daily trend analysis
daily_trends AS (
    SELECT
        DATE_TRUNC('day', publication_date) AS trend_date,
        occupation_field,
        occupation_group,
        occupation_label,
        SUM(vacancies) AS daily_vacancies,
        COUNT(*) AS daily_job_posts
    FROM base
    GROUP BY
        DATE_TRUNC('day', publication_date),
        occupation_field,
        occupation_group,
        occupation_label
),

-- Weekly aggregation for smoother trend visualization
weekly_trends AS (
    SELECT
        DATE_TRUNC('week', publication_date) AS trend_date,
        occupation_field,
        occupation_group,
        occupation_label,
        SUM(vacancies) AS weekly_vacancies,
        COUNT(*) AS weekly_job_posts
    FROM base
    GROUP BY
        DATE_TRUNC('week', publication_date),
        occupation_field,
        occupation_group,
        occupation_label
),

-- Monthly aggregation for longer-term trend analysis
monthly_trends AS (
    SELECT
        DATE_TRUNC('month', publication_date) AS trend_date,
        occupation_field,
        occupation_group,
        occupation_label,
        SUM(vacancies) AS monthly_vacancies,
        COUNT(*) AS monthly_job_posts
    FROM base
    GROUP BY
        DATE_TRUNC('month', publication_date),
        occupation_field,
        occupation_group,
        occupation_label
),

-- Field level daily trends (highest level of aggregation)
field_daily_trends AS (
    SELECT
        DATE_TRUNC('day', publication_date) AS trend_date,
        occupation_field,
        NULL AS occupation_group,
        NULL AS occupation_label,
        SUM(vacancies) AS daily_vacancies,
        COUNT(*) AS daily_job_posts
    FROM base
    GROUP BY
        DATE_TRUNC('day', publication_date),
        occupation_field
),

-- Field level weekly trends
field_weekly_trends AS (
    SELECT
        DATE_TRUNC('week', publication_date) AS trend_date,
        occupation_field,
        NULL AS occupation_group,
        NULL AS occupation_label,
        SUM(vacancies) AS weekly_vacancies,
        COUNT(*) AS weekly_job_posts
    FROM base
    GROUP BY
        DATE_TRUNC('week', publication_date),
        occupation_field
),

-- Field level monthly trends
field_monthly_trends AS (
    SELECT
        DATE_TRUNC('month', publication_date) AS trend_date,
        occupation_field,
        NULL AS occupation_group,
        NULL AS occupation_label,
        SUM(vacancies) AS monthly_vacancies,
        COUNT(*) AS monthly_job_posts
    FROM base
    GROUP BY
        DATE_TRUNC('month', publication_date),
        occupation_field
),

-- Group level daily trends (mid-level aggregation)
group_daily_trends AS (
    SELECT
        DATE_TRUNC('day', publication_date) AS trend_date,
        occupation_field,
        occupation_group,
        NULL AS occupation_label,
        SUM(vacancies) AS daily_vacancies,
        COUNT(*) AS daily_job_posts
    FROM base
    GROUP BY
        DATE_TRUNC('day', publication_date),
        occupation_field,
        occupation_group
),

-- Group level weekly trends
group_weekly_trends AS (
    SELECT
        DATE_TRUNC('week', publication_date) AS trend_date,
        occupation_field,
        occupation_group,
        NULL AS occupation_label,
        SUM(vacancies) AS weekly_vacancies,
        COUNT(*) AS weekly_job_posts
    FROM base
    GROUP BY
        DATE_TRUNC('week', publication_date),
        occupation_field,
        occupation_group
),

-- Group level monthly trends
group_monthly_trends AS (
    SELECT
        DATE_TRUNC('month', publication_date) AS trend_date,
        occupation_field,
        occupation_group,
        NULL AS occupation_label,
        SUM(vacancies) AS monthly_vacancies,
        COUNT(*) AS monthly_job_posts
    FROM base
    GROUP BY
        DATE_TRUNC('month', publication_date),
        occupation_field,
        occupation_group
)

-- Final combined model with time granularity indicator
SELECT
    'daily' AS time_granularity,
    trend_date,
    occupation_field,
    occupation_group,
    occupation_label,
    daily_vacancies AS vacancies,
    daily_job_posts AS job_posts
FROM daily_trends

UNION ALL

SELECT
    'daily' AS time_granularity,
    trend_date,
    occupation_field,
    occupation_group,
    occupation_label,
    daily_vacancies AS vacancies,
    daily_job_posts AS job_posts
FROM field_daily_trends

UNION ALL

SELECT
    'daily' AS time_granularity,
    trend_date,
    occupation_field,
    occupation_group,
    occupation_label,
    daily_vacancies AS vacancies,
    daily_job_posts AS job_posts
FROM group_daily_trends

UNION ALL

SELECT
    'weekly' AS time_granularity,
    trend_date,
    occupation_field,
    occupation_group,
    occupation_label,
    weekly_vacancies AS vacancies,
    weekly_job_posts AS job_posts
FROM weekly_trends

UNION ALL

SELECT
    'weekly' AS time_granularity,
    trend_date,
    occupation_field,
    occupation_group,
    occupation_label,
    weekly_vacancies AS vacancies,
    weekly_job_posts AS job_posts
FROM field_weekly_trends

UNION ALL

SELECT
    'weekly' AS time_granularity,
    trend_date,
    occupation_field,
    occupation_group,
    occupation_label,
    weekly_vacancies AS vacancies,
    weekly_job_posts AS job_posts
FROM group_weekly_trends

UNION ALL

SELECT
    'monthly' AS time_granularity,
    trend_date,
    occupation_field,
    occupation_group,
    occupation_label,
    monthly_vacancies AS vacancies,
    monthly_job_posts AS job_posts
FROM monthly_trends

UNION ALL

SELECT
    'monthly' AS time_granularity,
    trend_date,
    occupation_field,
    occupation_group,
    occupation_label,
    monthly_vacancies AS vacancies,
    monthly_job_posts AS job_posts
FROM field_monthly_trends

UNION ALL

SELECT
    'monthly' AS time_granularity,
    trend_date,
    occupation_field,
    occupation_group,
    occupation_label,
    monthly_vacancies AS vacancies,
    monthly_job_posts AS job_posts
FROM group_monthly_trends
