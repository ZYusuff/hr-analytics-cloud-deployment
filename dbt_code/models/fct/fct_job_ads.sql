with base as (
  select * from {{ ref('src_job_ads') }}
),

auxilliary_attributes_dim as (
  select
    auxilliary_attributes_id,
    experience_required,
    driver_license,
    access_to_own_car
  from {{ ref('dim_auxilliary_attributes') }}
),

employer_dim as (
  select
    employer_id,
    employer_organization_number,
    employer_name,
    employer_workplace
  from {{ ref('dim_employer') }}
),

occupation_dim as (
  select
    occupation_id,
    occupation_label
  from {{ ref('dim_occupation') }}
),

job_details_dim as (
  select
    job_details_id,
    job_ad_id
  from {{ ref('dim_job_details') }}
)

select
  base.vacancies,
  base.relevance,
  base.application_deadline,
  base.publication_date,
  base.last_publication_date,

  a.auxilliary_attributes_id as auxilliary_attributes_id,      -- foreign key linking to dim_auxilliary_attributes
  e.employer_id as employer_id, -- foreign key linking to dim_employer
  o.occupation_id as occupation_id, -- foreign key linking to dim_occupation
  jd.job_details_id as job_details_id      -- foreign key linking to dim_job_details

from base
left join auxilliary_attributes_dim a
  on base.experience_required = a.experience_required 
    and base.driver_license = a.driver_license
    and base.access_to_own_car = a.access_to_own_car
left join employer_dim e
  on base.employer_organization_number = e.employer_organization_number
    and base.employer_name = e.employer_name
    and base.employer_workplace = e.employer_workplace
left join occupation_dim o
  on base.occupation_label = o.occupation_label
left join job_details_dim jd
    on base.job_ad_id = jd.job_ad_id
