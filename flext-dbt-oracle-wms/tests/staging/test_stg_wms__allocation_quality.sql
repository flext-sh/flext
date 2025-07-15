-- Test suite for Oracle WMS allocation staging model data quality
-- Ensures enterprise-grade data validation for allocation processing

-- Test 1: No null values in critical business fields
select *
from {{ ref('stg_wms__allocation') }}
where company_code is null 
   or facility_code is null 
   or allocation_id is null
   or allocated_quantity is null