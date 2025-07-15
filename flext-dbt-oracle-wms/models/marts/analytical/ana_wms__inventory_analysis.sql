{{ 
  config(
    materialized='table',
    tags=['marts', 'analytical', 'inventory', 'kpi'],
    indexes=[
      {'columns': ['company_code', 'facility_code', 'analysis_date'], 'unique': False},
      {'columns': ['item_id'], 'unique': False},
      {'columns': ['inventory_turnover_category'], 'unique': False}
    ]
  ) 
}}

-- Analytical inventory analysis for strategic WMS decision making
-- Provides comprehensive inventory KPIs, turnover analysis, and optimization insights

with inventory_base as (
    select 
        company_code,
        facility_code,
        item_id,
        location_id,
        on_hand_quantity,
        available_quantity,
        allocated_quantity,
        reserved_quantity,
        damaged_quantity,
        unit_cost,
        total_value,
        received_date,
        expiry_date,
        days_to_expiry,
        days_since_cycle_count,
        availability_percent,
        allocation_percent,
        business_date,
        data_quality_status
    from {{ ref('stg_wms__inventory') }}
    where data_quality_status = 'VALID'
),

order_consumption as (
    select 
        company_code,
        facility_code,
        item_id,
        business_date,
        sum(shipped_quantity) as daily_consumption,
        count(*) as daily_order_lines
    from {{ ref('stg_wms__order_dtl') }}
    where data_quality_status = 'VALID'
      and business_date >= current_date - interval '90 days'
    group by company_code, facility_code, item_id, business_date
),

inventory_metrics as (
    select
        ib.company_code,
        ib.facility_code,
        ib.item_id,
        ib.business_date as analysis_date,
        
        -- Current inventory position
        sum(ib.on_hand_quantity) as total_on_hand_quantity,
        sum(ib.available_quantity) as total_available_quantity,
        sum(ib.allocated_quantity) as total_allocated_quantity,
        sum(ib.reserved_quantity) as total_reserved_quantity,
        sum(ib.damaged_quantity) as total_damaged_quantity,
        
        -- Financial metrics
        sum(ib.total_value) as total_inventory_value,
        {{ calculate_wms_kpi('sum(ib.available_quantity * ib.unit_cost)', 'sum(ib.total_value)', 'available_value_percent') }},
        
        -- Location distribution
        count(distinct ib.location_id) as locations_count,
        count(case when ib.on_hand_quantity > 0 then ib.location_id end) as active_locations_count,
        
        -- Quality and condition metrics
        {{ calculate_wms_kpi('sum(ib.damaged_quantity)', 'sum(ib.on_hand_quantity)', 'damage_rate_percent') }},
        avg(ib.availability_percent) as avg_availability_percent,
        avg(ib.allocation_percent) as avg_allocation_percent,
        
        -- Aging analysis
        avg(ib.days_to_expiry) as avg_days_to_expiry,
        avg(ib.days_since_cycle_count) as avg_days_since_cycle_count,
        count(case when ib.days_to_expiry <= 30 then 1 end) as near_expiry_locations,
        count(case when ib.days_since_cycle_count > 365 then 1 end) as overdue_cycle_count_locations,
        
        -- Consumption analysis (last 30 days)
        coalesce(avg(case 
            when oc.business_date >= current_date - interval '30 days' 
            then oc.daily_consumption 
        end), 0) as avg_daily_consumption_30d,
        
        coalesce(sum(case 
            when oc.business_date >= current_date - interval '30 days' 
            then oc.daily_consumption 
        end), 0) as total_consumption_30d,
        
        -- Consumption analysis (last 90 days)
        coalesce(avg(oc.daily_consumption), 0) as avg_daily_consumption_90d,
        coalesce(sum(oc.daily_consumption), 0) as total_consumption_90d
        
    from inventory_base ib
    left join order_consumption oc 
        on ib.company_code = oc.company_code
        and ib.facility_code = oc.facility_code
        and ib.item_id = oc.item_id
    group by 
        ib.company_code,
        ib.facility_code,
        ib.item_id,
        ib.business_date
),

inventory_classification as (
    select 
        *,
        
        -- Calculate inventory turnover metrics
        case 
            when avg_daily_consumption_30d > 0 
            then total_available_quantity / avg_daily_consumption_30d 
            else null 
        end as days_of_supply_30d,
        
        case 
            when avg_daily_consumption_90d > 0 
            then total_available_quantity / avg_daily_consumption_90d 
            else null 
        end as days_of_supply_90d,
        
        -- Turnover rate calculation
        case 
            when total_inventory_value > 0 and total_consumption_90d > 0
            then (total_consumption_90d * 365.0 / 90.0) / total_inventory_value 
            else 0 
        end as annual_turnover_rate,
        
        -- ABC classification based on consumption value
        case 
            when total_consumption_90d * avg(total_inventory_value / nullif(total_on_hand_quantity, 0)) over(
                partition by company_code, facility_code
            ) >= percentile_cont(0.8) over(
                partition by company_code, facility_code 
                order by total_consumption_90d * avg(total_inventory_value / nullif(total_on_hand_quantity, 0)) over(
                    partition by company_code, facility_code, item_id
                )
            ) then 'A'
            when total_consumption_90d * avg(total_inventory_value / nullif(total_on_hand_quantity, 0)) over(
                partition by company_code, facility_code
            ) >= percentile_cont(0.5) over(
                partition by company_code, facility_code 
                order by total_consumption_90d * avg(total_inventory_value / nullif(total_on_hand_quantity, 0)) over(
                    partition by company_code, facility_code, item_id
                )
            ) then 'B'
            else 'C'
        end as abc_classification,
        
        -- Inventory turnover classification
        case 
            when days_of_supply_30d <= 7 then 'FAST_MOVING'
            when days_of_supply_30d <= 30 then 'MEDIUM_MOVING'
            when days_of_supply_30d <= 90 then 'SLOW_MOVING'
            when days_of_supply_30d > 90 or avg_daily_consumption_30d = 0 then 'DEAD_STOCK'
            else 'UNKNOWN'
        end as inventory_turnover_category
        
    from inventory_metrics
),

final as (
    select 
        *,
        
        -- Risk indicators
        case 
            when inventory_turnover_category = 'DEAD_STOCK' then 'HIGH'
            when damage_rate_percent > 5 then 'HIGH'
            when near_expiry_locations > active_locations_count * 0.3 then 'HIGH'
            when days_of_supply_30d < 3 then 'MEDIUM'
            when overdue_cycle_count_locations > 0 then 'MEDIUM'
            else 'LOW'
        end as inventory_risk_level,
        
        -- Optimization recommendations
        case 
            when inventory_turnover_category = 'DEAD_STOCK' then 'LIQUIDATE_OR_RELOCATE'
            when days_of_supply_30d < 7 and abc_classification = 'A' then 'INCREASE_STOCK_LEVEL'
            when days_of_supply_30d > 60 and abc_classification in ('B', 'C') then 'REDUCE_STOCK_LEVEL'
            when damage_rate_percent > 3 then 'IMPROVE_STORAGE_CONDITIONS'
            when overdue_cycle_count_locations > 0 then 'SCHEDULE_CYCLE_COUNT'
            else 'MAINTAIN_CURRENT_LEVEL'
        end as optimization_recommendation,
        
        -- Generate composite key
        {{ dbt_utils.generate_surrogate_key([
            'company_code', 
            'facility_code', 
            'item_id',
            'analysis_date'
        ]) }} as analysis_key,
        
        current_timestamp as analysis_timestamp
        
    from inventory_classification
)

select * from final

-- Add freshness monitoring for analytical models
{{ config(post_hook="
    {% if execute %}
        {% set stale_analysis_query %}
            select count(*) as stale_count
            from {{ this }}
            where analysis_date < current_date - interval '7 days'
        {% endset %}
        
        {% set results = run_query(stale_analysis_query) %}
        {% if results and results.rows and results.rows[0][0] > 0 %}
            {{ log('WARNING: Found ' ~ results.rows[0][0] ~ ' stale inventory analysis records older than 7 days', info=true) }}
        {% endif %}
    {% endif %}
") }}