{{ 
  config(
    materialized='view',
    tags=['staging', 'inventory', 'oracle_wms']
  ) 
}}

-- Staging model for Oracle WMS inventory data
-- Standardizes and cleans raw inventory records from flext-tap-oracle-wms

with source_data as (
    select * from {{ source('oracle_wms_raw', 'inventory') }}
),

standardized as (
    select
        -- Primary identifiers
        id as inventory_id,
        company_code,
        facility_code,
        
        -- Item and location references
        item_id,
        location_id,
        lot_nbr as lot_number,
        
        -- Inventory quantities
        case 
            when on_hand_qty is not null then cast(on_hand_qty as number(15,4))
            else 0 
        end as on_hand_quantity,
        
        case 
            when available_qty is not null then cast(available_qty as number(15,4))
            else 0 
        end as available_quantity,
        
        case 
            when allocated_qty is not null then cast(allocated_qty as number(15,4))
            else 0 
        end as allocated_quantity,
        
        case 
            when in_transit_qty is not null then cast(in_transit_qty as number(15,4))
            else 0 
        end as in_transit_quantity,
        
        case 
            when reserved_qty is not null then cast(reserved_qty as number(15,4))
            else 0 
        end as reserved_quantity,
        
        case 
            when damaged_qty is not null then cast(damaged_qty as number(15,4))
            else 0 
        end as damaged_quantity,
        
        -- Status and condition
        inventory_status_id,
        inventory_condition_id,
        
        -- Unit of measure
        uom_id as unit_of_measure_id,
        
        -- Cost and valuation
        case 
            when unit_cost is not null then cast(unit_cost as number(15,4))
            else 0 
        end as unit_cost,
        
        case 
            when total_value is not null then cast(total_value as number(15,2))
            else 0 
        end as total_value,
        
        -- Dates
        case 
            when received_date is not null then 
                cast(received_date as date)
            else null 
        end as received_date,
        
        case 
            when expiry_date is not null then 
                cast(expiry_date as date)
            else null 
        end as expiry_date,
        
        case 
            when last_cycle_count_date is not null then 
                cast(last_cycle_count_date as date)
            else null 
        end as last_cycle_count_date,
        
        -- Tracking information
        receipt_id,
        shipment_id,
        cycle_count_id,
        
        -- Flags
        case 
            when is_cycle_count_pending_flg = 'Y' then true
            when is_cycle_count_pending_flg = 'N' then false
            else null
        end as is_cycle_count_pending_flag,
        
        case 
            when is_quarantined_flg = 'Y' then true
            when is_quarantined_flg = 'N' then false
            else null
        end as is_quarantined_flag,
        
        -- Audit fields
        create_user,
        case 
            when create_ts is not null then 
                cast(create_ts as timestamp)
            else null 
        end as created_timestamp,
        
        mod_user as modified_user,
        case 
            when mod_ts is not null then 
                cast(mod_ts as timestamp)
            else null 
        end as modified_timestamp,
        
        -- Singer metadata
        case 
            when _sdc_extracted_at is not null then 
                cast(_sdc_extracted_at as timestamp)
            else null 
        end as extracted_at,
        
        _sdc_entity as source_entity,
        
        -- Data quality indicators
        case 
            when company_code is null or facility_code is null then 'MISSING_REQUIRED_FIELDS'
            when item_id is null or trim(item_id) = '' then 'MISSING_ITEM_ID'
            when location_id is null or trim(location_id) = '' then 'MISSING_LOCATION_ID'
            when on_hand_quantity < 0 then 'NEGATIVE_ON_HAND'
            when available_quantity > on_hand_quantity then 'INVALID_AVAILABLE_QTY'
            when allocated_quantity > available_quantity then 'OVER_ALLOCATED'
            else 'VALID'
        end as data_quality_status,
        
        -- Business date derivation
        case 
            when received_date is not null then received_date
            when created_timestamp is not null then cast(created_timestamp as date)
            else cast(_sdc_extracted_at as date)
        end as business_date
        
    from source_data
),

final as (
    select 
        *,
        
        -- Calculate derived metrics
        case 
            when on_hand_quantity > 0 then 
                (available_quantity / on_hand_quantity) * 100 
            else 0 
        end as availability_percent,
        
        case 
            when on_hand_quantity > 0 then 
                (allocated_quantity / on_hand_quantity) * 100 
            else 0 
        end as allocation_percent,
        
        case 
            when expiry_date is not null and expiry_date > current_date then 
                expiry_date - current_date 
            else null 
        end as days_to_expiry,
        
        case 
            when last_cycle_count_date is not null then 
                current_date - last_cycle_count_date 
            else null 
        end as days_since_cycle_count,
        
        -- Generate surrogate key for dimensional modeling
        {{ dbt_utils.generate_surrogate_key([
            'company_code', 
            'facility_code', 
            'inventory_id'
        ]) }} as inventory_sk,
        
        -- Add row hash for change detection
        {{ dbt_utils.generate_surrogate_key([
            'on_hand_quantity',
            'available_quantity', 
            'allocated_quantity',
            'inventory_status_id',
            'modified_timestamp'
        ]) }} as row_hash,
        
        -- Current timestamp for processing
        current_timestamp as dbt_processed_at
        
    from standardized
)

select * from final

-- Data quality check: ensure inventory quantities are consistent
{% if is_incremental() %}
    -- For incremental runs, only check new/updated records
    where extracted_at > (select max(extracted_at) from {{ this }})
{% endif %}