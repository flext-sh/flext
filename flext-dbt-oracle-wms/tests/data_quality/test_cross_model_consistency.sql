-- Cross-model consistency tests for Oracle WMS enterprise data quality
-- Validates referential integrity and business logic across all models

-- Test 1: All allocations should reference valid orders
select 
    a.company_code,
    a.facility_code,
    a.allocation_id,
    a.order_dtl_id,
    'ORPHANED_ALLOCATION' as issue_type
from {{ ref('stg_wms__allocation') }} a
left join {{ ref('stg_wms__order_dtl') }} od
    on a.company_code = od.company_code
    and a.facility_code = od.facility_code
    and a.order_dtl_id = od.order_detail_id
where od.order_detail_id is null
  and a.order_dtl_id is not null
  and a.data_quality_status = 'VALID'

union all

-- Test 2: Inventory allocations should not exceed available quantity
select 
    i.company_code,
    i.facility_code,
    i.inventory_id,
    i.item_id,
    'OVER_ALLOCATED_INVENTORY' as issue_type
from {{ ref('stg_wms__inventory') }} i
where i.allocated_quantity > i.available_quantity
  and i.data_quality_status = 'VALID'

union all

-- Test 3: Order detail quantities should align with allocations
with allocation_totals as (
    select 
        company_code,
        facility_code,
        order_dtl_id,
        sum(allocated_quantity) as total_allocated_qty
    from {{ ref('stg_wms__allocation') }}
    where data_quality_status = 'VALID'
      and order_dtl_id is not null
    group by company_code, facility_code, order_dtl_id
)
select 
    od.company_code,
    od.facility_code,
    od.order_detail_id,
    od.ordered_quantity,
    'ALLOCATION_QUANTITY_MISMATCH' as issue_type
from {{ ref('stg_wms__order_dtl') }} od
left join allocation_totals at
    on od.company_code = at.company_code
    and od.facility_code = at.facility_code
    and od.order_detail_id = at.order_dtl_id
where od.data_quality_status = 'VALID'
  and abs(coalesce(at.total_allocated_qty, 0) - od.ordered_quantity) > 0.01
  and od.line_status_id not in (90)  -- Exclude cancelled lines

union all

-- Test 4: KPI dashboard totals should match operational summaries
with kpi_allocation_check as (
    select 
        k.company_code,
        k.facility_code,
        k.kpi_date,
        k.total_allocations as kpi_total_allocations,
        coalesce(sum(o.daily_total_allocations), 0) as operational_total_allocations
    from {{ ref('met_wms__kpi_dashboard') }} k
    left join {{ ref('opr_wms__allocation_summary') }} o
        on k.company_code = o.company_code
        and k.facility_code = o.facility_code
        and k.kpi_date = o.business_date
    where k.kpi_category = 'ALLOCATION'
    group by 
        k.company_code,
        k.facility_code,
        k.kpi_date,
        k.total_allocations
)
select 
    company_code,
    facility_code,
    kpi_date,
    'KPI_OPERATIONAL_MISMATCH' as issue_type
from kpi_allocation_check
where abs(kpi_total_allocations - operational_total_allocations) > 0.01

union all

-- Test 5: Analytical inventory should have corresponding staging records
select 
    ai.company_code,
    ai.facility_code,
    ai.item_id,
    ai.analysis_date,
    'ORPHANED_INVENTORY_ANALYSIS' as issue_type
from {{ ref('ana_wms__inventory_analysis') }} ai
left join {{ ref('stg_wms__inventory') }} si
    on ai.company_code = si.company_code
    and ai.facility_code = si.facility_code
    and ai.item_id = si.item_id
    and ai.analysis_date = si.business_date
where si.inventory_id is null
  and ai.analysis_date >= current_date - interval '30 days'  -- Only check recent data

union all

-- Test 6: Business dates should be consistent across related records
select 
    a.company_code,
    a.facility_code,
    a.allocation_id,
    a.business_date as allocation_date,
    'INCONSISTENT_BUSINESS_DATE' as issue_type
from {{ ref('stg_wms__allocation') }} a
join {{ ref('stg_wms__order_dtl') }} od
    on a.company_code = od.company_code
    and a.facility_code = od.facility_code
    and a.order_dtl_id = od.order_detail_id
where a.data_quality_status = 'VALID'
  and od.data_quality_status = 'VALID'
  and abs(a.business_date - od.business_date) > 7  -- Allow up to 7 days difference