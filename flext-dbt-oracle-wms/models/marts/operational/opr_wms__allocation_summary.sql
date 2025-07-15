{{ 
  config(
    materialized='table',
    tags=['marts', 'operational', 'allocation', 'real_time'],
    indexes=[
      {'columns': ['company_code', 'facility_code', 'business_date'], 'unique': False},
      {'columns': ['allocation_status'], 'unique': False}
    ]
  ) 
}}

-- Operational allocation summary for real-time WMS dashboard
-- Provides key allocation metrics for warehouse operations team

with allocation_base as (
    select 
        company_code,
        facility_code,
        business_date,
        allocation_status_id,
        allocated_quantity,
        packed_quantity,
        is_picking_flag,
        picked_timestamp,
        created_timestamp,
        modified_timestamp,
        data_quality_status
    from {{ ref('stg_wms__allocation') }}
    where data_quality_status = 'VALID'
),

allocation_metrics as (
    select
        company_code,
        facility_code,
        business_date,
        
        -- Status mapping
        case allocation_status_id
            when 10 then 'PLANNED'
            when 20 then 'RELEASED'
            when 30 then 'PICKING'
            when 40 then 'PICKED'
            when 50 then 'PACKED'
            when 90 then 'CANCELLED'
            else 'UNKNOWN'
        end as allocation_status,
        
        -- Allocation counts
        count(*) as total_allocations,
        count(case when is_picking_flag = true then 1 end) as allocations_in_picking,
        count(case when picked_timestamp is not null then 1 end) as allocations_picked,
        
        -- Quantity metrics
        sum(allocated_quantity) as total_allocated_quantity,
        sum(packed_quantity) as total_packed_quantity,
        sum(case when packed_quantity > 0 then allocated_quantity - packed_quantity else 0 end) as outstanding_quantity,
        
        -- Performance metrics
        avg(case 
            when picked_timestamp is not null and created_timestamp is not null 
            then extract(epoch from (picked_timestamp - created_timestamp)) / 3600.0 
        end) as avg_pick_time_hours,
        
        -- Efficiency metrics
        case 
            when sum(allocated_quantity) > 0 
            then sum(packed_quantity) / sum(allocated_quantity) * 100 
            else 0 
        end as pack_efficiency_percent,
        
        -- Timestamps
        min(created_timestamp) as earliest_allocation_time,
        max(modified_timestamp) as latest_modification_time,
        current_timestamp as snapshot_timestamp
        
    from allocation_base
    group by 
        company_code,
        facility_code, 
        business_date,
        allocation_status_id
),

daily_totals as (
    select
        company_code,
        facility_code,
        business_date,
        
        -- Daily totals across all statuses
        sum(total_allocations) as daily_total_allocations,
        sum(total_allocated_quantity) as daily_total_allocated_quantity,
        sum(total_packed_quantity) as daily_total_packed_quantity,
        sum(outstanding_quantity) as daily_outstanding_quantity,
        
        -- Daily performance
        avg(avg_pick_time_hours) as daily_avg_pick_time_hours,
        avg(pack_efficiency_percent) as daily_avg_pack_efficiency_percent
        
    from allocation_metrics
    group by company_code, facility_code, business_date
),

final as (
    select 
        am.*,
        dt.daily_total_allocations,
        dt.daily_total_allocated_quantity,
        dt.daily_total_packed_quantity,
        dt.daily_outstanding_quantity,
        dt.daily_avg_pick_time_hours,
        dt.daily_avg_pack_efficiency_percent,
        
        -- Status percentage of daily total
        case 
            when dt.daily_total_allocations > 0 
            then am.total_allocations / dt.daily_total_allocations * 100 
            else 0 
        end as status_percentage_of_daily,
        
        -- Alert flags for operational monitoring
        case 
            when am.allocation_status = 'PICKING' and am.avg_pick_time_hours > 4 
            then 'SLOW_PICKING'
            when am.allocation_status = 'PICKED' and am.pack_efficiency_percent < 90 
            then 'LOW_PACK_EFFICIENCY'
            when am.outstanding_quantity > 1000 
            then 'HIGH_OUTSTANDING'
            else 'NORMAL'
        end as operational_alert,
        
        -- Generate composite key
        {{ dbt_utils.generate_surrogate_key([
            'company_code', 
            'facility_code', 
            'business_date',
            'allocation_status'
        ]) }} as summary_key
        
    from allocation_metrics am
    left join daily_totals dt 
        on am.company_code = dt.company_code
        and am.facility_code = dt.facility_code  
        and am.business_date = dt.business_date
)

select * from final

-- Add test to ensure data freshness for operational dashboard
{{ config(post_hook="
    {% if execute %}
        {% set latest_date_query %}
            select max(business_date) as latest_date 
            from {{ this }}
        {% endset %}
        
        {% set results = run_query(latest_date_query) %}
        {% if results and results.rows %}
            {% set latest_date = results.rows[0][0] %}
            {% if latest_date and (modules.datetime.date.today() - latest_date).days > 1 %}
                {{ log('WARNING: Operational allocation summary is more than 1 day old. Latest date: ' ~ latest_date, info=true) }}
            {% endif %}
        {% endif %}
    {% endif %}
") }}