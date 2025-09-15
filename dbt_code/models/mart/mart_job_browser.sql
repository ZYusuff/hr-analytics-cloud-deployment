/*
  This mart model provides a denormalized view of job listings
  optimized for search and detailed browsing
*/

WITH base AS (
  SELECT * FROM {{ ref('fct_job_ads') }}
),

auxilliary_attributes AS (
  SELECT * FROM {{ ref('dim_auxilliary_attributes') }}
),

employer_dim AS (
  SELECT * FROM {{ ref('dim_employer') }}
),

job_details_dim AS (
  SELECT * FROM {{ ref('dim_job_details') }}
),

occupation_dim AS (
  SELECT * FROM {{ ref('dim_occupation') }}
)

-- Create a fully denormalized view for job browsing and search
SELECT
  -- Job details for display
  jd.headline,
  jd.description,
  jd.employment_type,
  jd.duration,
  jd.salary_type,
  jd.job_ad_id,
  
  -- Employer details for display and filtering
  e.employer_name,
  e.workplace_street_address,
  e.workplace_postcode,
  e.workplace_city,
  e.workplace_region,
  e.workplace_country,

  
  -- Occupation details for filtering
  o.occupation_field,
  o.occupation_group,
  o.occupation_label,
  
  -- Requirements for filtering
  a.experience_required,
  a.driver_license,
  a.access_to_own_car,
  
  
FROM base b
LEFT JOIN occupation_dim o ON b.occupation_id = o.occupation_id
LEFT JOIN employer_dim e ON b.employer_id = e.employer_id
LEFT JOIN auxilliary_attributes a ON b.auxilliary_attributes_id = a.auxilliary_attributes_id
LEFT JOIN job_details_dim jd ON b.job_details_id = jd.job_details_id
