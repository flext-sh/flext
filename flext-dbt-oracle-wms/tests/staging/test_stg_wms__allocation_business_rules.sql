-- Business rule validation tests for Oracle WMS allocation staging
-- Validates enterprise business logic and data consistency

-- Test 1: Allocated quantity should not be negative
select *
from {{ ref('stg_wms__allocation') }}
where allocated_quantity < 0

union all

-- Test 2: Packed quantity should not exceed allocated quantity
select *
from {{ ref('stg_wms__allocation') }}
where packed_quantity > allocated_quantity

union all

-- Test 3: Picked timestamp should not be in the future
select *
from {{ ref('stg_wms__allocation') }}
where picked_timestamp > current_timestamp

union all

-- Test 4: Modified timestamp should be >= created timestamp
select *
from {{ ref('stg_wms__allocation') }}
where modified_timestamp < created_timestamp
  and created_timestamp is not null
  and modified_timestamp is not null

union all

-- Test 5: Business date should be within reasonable range (last 2 years to tomorrow)
select *
from {{ ref('stg_wms__allocation') }}
where business_date < current_date - interval '2 years'
   or business_date > current_date + interval '1 day'