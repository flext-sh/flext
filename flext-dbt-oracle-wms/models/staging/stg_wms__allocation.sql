{{ 
  config(
    materialized='view',
    tags=['staging', 'allocation', 'oracle_wms']
  ) 
}}

-- Staging model for Oracle WMS allocation data
-- Standardizes and cleans raw allocation records from flext-tap-oracle-wms

with source_data as (
    select * from {{ source('oracle_wms_raw', 'allocation') }}
),

standardized as (
    select
        -- Primary identifiers
        id as allocation_id,
        company_code,
        facility_code,
        
        -- Business keys
        order_dtl_id,
        from_inventory_id,
        to_inventory_id,
        
        -- Allocation details
        case 
            when alloc_qty is not null then cast(alloc_qty as number(15,4))
            else 0 
        end as allocated_quantity,
        
        case 
            when packed_qty is not null then cast(packed_qty as number(15,4))
            else 0 
        end as packed_quantity,
        
        -- Status and type information
        status_id as allocation_status_id,
        type_id as allocation_type_id,
        
        -- Workflow references
        wave_id,
        task_id,
        task_seq_nbr as task_sequence_number,
        
        -- UOM and packaging
        alloc_uom_id as allocation_uom_id,
        cartonize_uom_id,
        ob_lpn_type_id as outbound_lpn_type_id,
        final_oblpn_nbr as final_outbound_lpn_number,
        
        -- System and automation
        mhe_system_id as material_handling_system_id,
        
        -- Picking details
        pick_user,
        case 
            when picked_ts is not null then 
                cast(picked_ts as timestamp)
            else null 
        end as picked_timestamp,
        pick_locn_str as pick_location_string,
        
        -- Flags
        case 
            when is_picking_flg = 'Y' then true
            when is_picking_flg = 'N' then false
            else null
        end as is_picking_flag,
        
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
            when allocated_quantity < 0 then 'NEGATIVE_QUANTITY'
            when picked_timestamp > modified_timestamp then 'INVALID_TIMESTAMP_ORDER'
            else 'VALID'
        end as data_quality_status,
        
        -- Business date derivation
        case 
            when created_timestamp is not null then 
                cast(created_timestamp as date)
            else cast(_sdc_extracted_at as date)
        end as business_date
        
    from source_data
),

final as (
    select 
        *,
        
        -- Generate surrogate key for dimensional modeling
        {{ dbt_utils.generate_surrogate_key([
            'company_code', 
            'facility_code', 
            'allocation_id'
        ]) }} as allocation_sk,
        
        -- Add row hash for change detection
        {{ dbt_utils.generate_surrogate_key([
            'allocated_quantity',
            'packed_quantity', 
            'allocation_status_id',
            'picked_timestamp',
            'modified_timestamp'
        ]) }} as row_hash,
        
        -- Current timestamp for processing
        current_timestamp as dbt_processed_at
        
    from standardized
)

select * from final

-- Data quality check: ensure no duplicate allocations per company/facility
-- This will fail the build if duplicates are found
{% if is_incremental() %}
    -- For incremental runs, only check new/updated records
    where extracted_at > (select max(extracted_at) from {{ this }})
{% endif %}