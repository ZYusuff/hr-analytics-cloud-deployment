/*
  Analysis: Data Quality Issue Details
  
  This analysis identifies the specific records that have data quality issues.
  It can be run periodically to track progress in resolving these issues.
  
  Run with: dbt compile --select data_quality_issue_details
  Then examine the compiled SQL in the target directory.
*/

with 
-- Issue 1: Employers missing organization numbers
employers_missing_org_numbers as (
  select 
    employer_id,
    employer_name,
    employer_workplace
  from {{ ref('dim_employer') }}
  where employer_organization_number is null
),

-- Issue 2: Job ads missing employer information
job_ads_missing_employers as (
  select
    j.job_details_id,
    d.job_ad_id,
    j.publication_date
  from {{ ref('fct_job_ads') }} j
  left join {{ ref('dim_job_details') }} d
    on j.job_details_id = d.job_details_id
  where j.employer_id is null
),

-- Issue 3: Job ads missing location information
job_ads_missing_locations as (
  select
    j.job_details_id,
    d.job_ad_id,
    j.publication_date
  from {{ ref('fct_job_ads') }} j
  left join {{ ref('dim_job_details') }} d
    on j.job_details_id = d.job_details_id
  where j.location_id is null
),

-- Issue 4: Job ads missing vacancy counts
job_ads_missing_vacancies as (
  select
    j.job_details_id,
    d.job_ad_id,
    j.publication_date
  from {{ ref('fct_job_ads') }} j
  left join {{ ref('dim_job_details') }} d
    on j.job_details_id = d.job_details_id
  where j.vacancies is null
),

-- Issue 5: Duplicate job details IDs
duplicate_job_details as (
  select 
    job_details_id,
    count(*) as count
  from {{ ref('dim_job_details') }}
  group by job_details_id
  having count(*) > 1
),

job_details_with_duplicates as (
  select
    d.job_details_id,
    d.job_ad_id,
    d.headline
  from {{ ref('dim_job_details') }} d
  inner join duplicate_job_details dup
    on d.job_details_id = dup.job_details_id
)

-- Select statements for each issue type
-- (Comment out sections as needed to focus on specific issues)

-- Issue 1: Employers missing organization numbers
select
  'Employers missing org numbers' as issue_type,
  employer_id,
  employer_name,
  employer_workplace,
  null as job_ad_id,
  null as publication_date
from employers_missing_org_numbers

union all

-- Issue 2: Job ads missing employer information
select
  'Job ads missing employers' as issue_type,
  null as employer_id,
  null as employer_name,
  null as employer_workplace,
  job_ad_id,
  publication_date
from job_ads_missing_employers

union all

-- Issue 3: Job ads missing location information
select
  'Job ads missing locations' as issue_type,
  null as employer_id,
  null as employer_name,
  null as employer_workplace,
  job_ad_id,
  publication_date
from job_ads_missing_locations

union all

-- Issue 4: Job ads missing vacancy counts
select
  'Job ads missing vacancies' as issue_type,
  null as employer_id,
  null as employer_name,
  null as employer_workplace,
  job_ad_id,
  publication_date
from job_ads_missing_vacancies

union all

-- Issue 5: Duplicate job details IDs
select
  'Duplicate job details IDs' as issue_type,
  null as employer_id,
  null as employer_name,
  null as employer_workplace,
  job_ad_id,
  null as publication_date
from job_details_with_duplicates

order by issue_type, job_ad_id