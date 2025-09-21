# Data Quality Issues Documentation

## Overview
This document tracks known data quality issues discovered through dbt testing. These issues have been identified but require discussion with the team to determine the appropriate resolution approach.

## Current Issues (As of September 21, 2025)

### 1. Missing Employer Organization Numbers
- **Test:** `not_null_dim_employer_employer_organization_number`
- **Failure Count:** 19 records
- **Description:** 19 employers in the dimension table are missing organization numbers
- **Business Impact:** Affects employer identification and may cause issues with reporting that relies on organization numbers

### 2. Missing Employer IDs in Fact Table
- **Test:** `not_null_fct_job_ads_employer_id`
- **Failure Count:** 21 records
- **Description:** 21 job advertisements don't have linked employers
- **Business Impact:** These records won't be included in employer-based analyses

### 3. Missing Location IDs in Fact Table
- **Test:** `not_null_fct_job_ads_location_id`
- **Failure Count:** 56 records
- **Description:** 56 job advertisements are missing location information
- **Business Impact:** Geographic analyses will be incomplete for these records

### 4. Missing Vacancy Counts
- **Test:** `not_null_fct_job_ads_vacancies`
- **Failure Count:** 1 record
- **Description:** One job advertisement is missing the number of vacancies
- **Business Impact:** Minor impact on total vacancy counts

### 5. Duplicate Job Details IDs
- **Test:** `unique_dim_job_details_job_details_id`
- **Failure Count:** 5 records
- **Description:** 5 records in dim_job_details have duplicate job_details_id values
- **Business Impact:** Violates primary key integrity, may cause incorrect joins

## Warning Issues

### 1. Vacancy Count Exceeds Expected Maximum
- **Test:** `dbt_expectations_expect_column_max_to_be_between_fct_job_ads_vacancies__20__1`
- **Warning Count:** 1 record
- **Description:** At least one job advertisement has a vacancy count exceeding the expected maximum (20)
- **Business Impact:** Could indicate data entry errors or outliers that skew analyses

## Next Steps

These issues will be discussed with the team to determine the appropriate resolution approaches. The data_quality_issue_details.sql analysis can be used to identify the specific records affected by these issues.