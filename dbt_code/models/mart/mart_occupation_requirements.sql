/*
  Requirements analysis mart for occupations
  Focuses on requirement percentages like experience, driver's license, and car by occupation hierarchy
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

auxilliary_attributes_dim AS (
    SELECT * FROM {{ ref('dim_auxilliary_attributes') }}
),

-- Base join between facts and dimensions with active job filtering
base AS (
    SELECT
        jd.job_ad_id,
        ja.vacancies,
        o.occupation_field,
        o.occupation_group,
        o.occupation_label,
        a.experience_required,
        a.driver_license,
        a.access_to_own_car
    FROM job_ads_fct ja
    LEFT JOIN job_details_dim jd ON ja.job_details_id = jd.job_details_id
    LEFT JOIN occupation_dim o ON ja.occupation_id = o.occupation_id
    LEFT JOIN auxilliary_attributes_dim a ON ja.auxilliary_attributes_id = a.auxilliary_attributes_id
    WHERE DATEDIFF('day', CURRENT_DATE(), ja.application_deadline) >= 0  -- Only consider active job ads
),

-- Aggregate metrics by occupation field
field_requirements AS (
    SELECT 
        occupation_field,
        NULL AS occupation_group,
        NULL AS occupation_label,
        SUM(vacancies) AS total_vacancies,
        
        -- Experience requirements
        SUM(CASE WHEN experience_required = TRUE THEN vacancies ELSE 0 END) AS experience_required_count,
        ROUND(100.0 * SUM(CASE WHEN experience_required = TRUE THEN vacancies ELSE 0 END) / 
              NULLIF(SUM(vacancies), 0), 1) AS experience_required_percentage,
        
        -- Driver's license requirements
        SUM(CASE WHEN driver_license = TRUE THEN vacancies ELSE 0 END) AS driver_license_count,
        ROUND(100.0 * SUM(CASE WHEN driver_license = TRUE THEN vacancies ELSE 0 END) / 
              NULLIF(SUM(vacancies), 0), 1) AS driver_license_percentage,
        
        -- Car requirements
        SUM(CASE WHEN access_to_own_car = TRUE THEN vacancies ELSE 0 END) AS own_car_count,
        ROUND(100.0 * SUM(CASE WHEN access_to_own_car = TRUE THEN vacancies ELSE 0 END) / 
              NULLIF(SUM(vacancies), 0), 1) AS own_car_percentage
    FROM base
    GROUP BY occupation_field
),

-- Aggregate metrics by occupation group
group_requirements AS (
    SELECT 
        occupation_field,
        occupation_group,
        NULL AS occupation_label,
        SUM(vacancies) AS total_vacancies,
        
        -- Experience requirements
        SUM(CASE WHEN experience_required = TRUE THEN vacancies ELSE 0 END) AS experience_required_count,
        ROUND(100.0 * SUM(CASE WHEN experience_required = TRUE THEN vacancies ELSE 0 END) / 
              NULLIF(SUM(vacancies), 0), 1) AS experience_required_percentage,
        
        -- Driver's license requirements
        SUM(CASE WHEN driver_license = TRUE THEN vacancies ELSE 0 END) AS driver_license_count,
        ROUND(100.0 * SUM(CASE WHEN driver_license = TRUE THEN vacancies ELSE 0 END) / 
              NULLIF(SUM(vacancies), 0), 1) AS driver_license_percentage,
        
        -- Car requirements
        SUM(CASE WHEN access_to_own_car = TRUE THEN vacancies ELSE 0 END) AS own_car_count,
        ROUND(100.0 * SUM(CASE WHEN access_to_own_car = TRUE THEN vacancies ELSE 0 END) / 
              NULLIF(SUM(vacancies), 0), 1) AS own_car_percentage
    FROM base
    GROUP BY occupation_field, occupation_group
),

-- Aggregate metrics by specific occupation
occupation_requirements AS (
    SELECT 
        occupation_field,
        occupation_group,
        occupation_label,
        SUM(vacancies) AS total_vacancies,
        
        -- Experience requirements
        SUM(CASE WHEN experience_required = TRUE THEN vacancies ELSE 0 END) AS experience_required_count,
        ROUND(100.0 * SUM(CASE WHEN experience_required = TRUE THEN vacancies ELSE 0 END) / 
              NULLIF(SUM(vacancies), 0), 1) AS experience_required_percentage,
        
        -- Driver's license requirements
        SUM(CASE WHEN driver_license = TRUE THEN vacancies ELSE 0 END) AS driver_license_count,
        ROUND(100.0 * SUM(CASE WHEN driver_license = TRUE THEN vacancies ELSE 0 END) / 
              NULLIF(SUM(vacancies), 0), 1) AS driver_license_percentage,
        
        -- Car requirements
        SUM(CASE WHEN access_to_own_car = TRUE THEN vacancies ELSE 0 END) AS own_car_count,
        ROUND(100.0 * SUM(CASE WHEN access_to_own_car = TRUE THEN vacancies ELSE 0 END) / 
              NULLIF(SUM(vacancies), 0), 1) AS own_car_percentage
    FROM base
    GROUP BY occupation_field, occupation_group, occupation_label
),

-- Combined hierarchical metrics
combined_requirements AS (
    SELECT 'field' AS level, * FROM field_requirements
    UNION ALL
    SELECT 'group' AS level, * FROM group_requirements
    UNION ALL
    SELECT 'occupation' AS level, * FROM occupation_requirements
)

-- Final selection
SELECT
    level,
    occupation_field,
    occupation_group,
    occupation_label,
    total_vacancies,
    experience_required_count,
    experience_required_percentage,
    driver_license_count,
    driver_license_percentage,
    own_car_count,
    own_car_percentage
FROM combined_requirements
ORDER BY level, occupation_field, occupation_group, occupation_label