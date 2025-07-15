{{ 
  config(
    materialized='view',
    tags=['staging', 'order', 'oracle_wms']
  ) 
}}

-- Staging model for Oracle WMS order detail data
-- Standardizes and cleans raw order detail line items from flext-tap-oracle-wms

with source_data as (
    select * from {{ source('oracle_wms_raw', 'order_dtl') }}
),

standardized as (
    select
        -- Primary identifiers
        id as order_detail_id,
        order_nbr as order_number,
        order_line_nbr as order_line_number,
        company_code,
        facility_code,
        
        -- Item information
        item_id,
        item_name,
        item_barcode,
        
        -- Quantities
        case 
            when ordered_qty is not null then cast(ordered_qty as number(15,4))
            else 0 
        end as ordered_quantity,
        
        case 
            when shipped_qty is not null then cast(shipped_qty as number(15,4))
            else 0 
        end as shipped_quantity,
        
        case 
            when allocated_qty is not null then cast(allocated_qty as number(15,4))
            else 0 
        end as allocated_quantity,
        
        case 
            when picked_qty is not null then cast(picked_qty as number(15,4))
            else 0 
        end as picked_quantity,
        
        -- Unit information
        uom_id as unit_of_measure_id,
        case 
            when unit_price is not null then cast(unit_price as number(15,4))
            else 0 
        end as unit_price,
        
        case 
            when line_value is not null then cast(line_value as number(15,2))
            else 0 
        end as line_value,
        
        -- Status and type
        status_id as line_status_id,
        line_type,
        
        -- Inventory and location references
        from_inventory_id,
        to_inventory_id,
        pick_location_id,
        
        -- Packaging
        carton_nbr as carton_number,
        lpn_nbr as license_plate_number,
        
        -- Special handling
        special_instr as special_instructions,
        
        -- Flags
        case 
            when is_substitution_flg = 'Y' then true
            when is_substitution_flg = 'N' then false
            else null
        end as is_substitution_flag,
        
        case 
            when is_backordered_flg = 'Y' then true
            when is_backordered_flg = 'N' then false
            else null
        end as is_backordered_flag,
        
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
            when order_number is null or trim(order_number) = '' then 'MISSING_ORDER_NUMBER'
            when order_line_number is null then 'MISSING_LINE_NUMBER'
            when item_id is null or trim(item_id) = '' then 'MISSING_ITEM_ID'
            when ordered_quantity <= 0 then 'INVALID_ORDERED_QUANTITY'
            when shipped_quantity > ordered_quantity then 'OVERSHIPPED'
            else 'VALID'
        end as data_quality_status,
        
        -- Business date derivation
        case 
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
            when ordered_quantity > 0 then 
                (shipped_quantity / ordered_quantity) * 100 
            else 0 
        end as fill_rate_percent,
        
        case 
            when ordered_quantity > 0 then 
                ordered_quantity - shipped_quantity 
            else 0 
        end as shortage_quantity,
        
        -- Generate surrogate key for dimensional modeling
        {{ dbt_utils.generate_surrogate_key([
            'company_code', 
            'facility_code', 
            'order_detail_id'
        ]) }} as order_detail_sk,
        
        -- Add row hash for change detection
        {{ dbt_utils.generate_surrogate_key([
            'ordered_quantity',
            'shipped_quantity', 
            'allocated_quantity',
            'line_status_id',
            'modified_timestamp'
        ]) }} as row_hash,
        
        -- Current timestamp for processing
        current_timestamp as dbt_processed_at
        
    from standardized
)

select * from final

-- Data quality check: ensure line numbers are sequential per order
{% if is_incremental() %}
    -- For incremental runs, only check new/updated records
    where extracted_at > (select max(extracted_at) from {{ this }})
{% endif %}