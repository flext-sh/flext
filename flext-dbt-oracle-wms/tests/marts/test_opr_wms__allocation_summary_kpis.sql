-- KPI validation tests for operational allocation summary
-- Ensures enterprise metrics accuracy and consistency

-- Test 1: Pack efficiency should be between 0 and 100%
select *
from {{ ref('opr_wms__allocation_summary') }}
where pack_efficiency_percent < 0 
   or pack_efficiency_percent > 100

union all

-- Test 2: Status percentage of daily total should sum to 100% per facility/date
with daily_status_totals as (
    select 
        company_code,
        facility_code,
        business_date,
        sum(status_percentage_of_daily) as total_percentage
    from {{ ref('opr_wms__allocation_summary') }}
    group by company_code, facility_code, business_date
)
select *
from daily_status_totals
where abs(total_percentage - 100.0) > 0.1  -- Allow for minor rounding differences

union all

-- Test 3: Average pick time should be reasonable (not negative, not excessive)
select *
from {{ ref('opr_wms__allocation_summary') }}
where avg_pick_time_hours < 0 
   or avg_pick_time_hours > 24  -- No pick should take more than 24 hours

union all

-- Test 4: Outstanding quantity should not be negative
select *
from {{ ref('opr_wms__allocation_summary') }}
where outstanding_quantity < 0

union all

-- Test 5: Daily totals should match sum of status-level records
with validation_check as (
    select 
        company_code,
        facility_code,
        business_date,
        daily_total_allocations,
        sum(total_allocations) as calculated_total_allocations
    from {{ ref('opr_wms__allocation_summary') }}
    group by 
        company_code,
        facility_code,
        business_date,
        daily_total_allocations
)
select *
from validation_check
where daily_total_allocations != calculated_total_allocations