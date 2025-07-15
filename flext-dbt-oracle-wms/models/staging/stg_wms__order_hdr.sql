{{ 
  config(
    materialized='view',
    tags=['staging', 'order', 'oracle_wms']
  ) 
}}

-- Staging model for Oracle WMS order header data
-- Standardizes and cleans raw order header records from flext-tap-oracle-wms

with source_data as (
    select * from {{ source('oracle_wms_raw', 'order_hdr') }}
),

standardized as (
    select
        -- Primary identifiers
        id as order_header_id,
        order_nbr as order_number,
        company_code,
        facility_code,
        
        -- Business identifiers
        customer_id,
        vendor_id,
        carrier_id,
        
        -- Order classification
        order_type,
        order_status,
        priority_id as order_priority_id,
        
        -- Dates and timing
        case 
            when order_date is not null then 
                cast(order_date as date)
            else null 
        end as order_date,
        
        case 
            when ship_date is not null then 
                cast(ship_date as date)
            else null 
        end as ship_date,
        
        case 
            when delivery_date is not null then 
                cast(delivery_date as date)
            else null 
        end as delivery_date,
        
        -- Quantities and totals
        case 
            when total_qty is not null then cast(total_qty as number(15,4))
            else 0 
        end as total_quantity,
        
        case 
            when total_lines is not null then cast(total_lines as number(10,0))
            else 0 
        end as total_lines,
        
        case 
            when total_value is not null then cast(total_value as number(15,2))
            else 0 
        end as total_value,
        
        -- Shipping and delivery
        ship_to_name,
        ship_to_addr1 as ship_to_address_1,
        ship_to_addr2 as ship_to_address_2,
        ship_to_city,
        ship_to_state,
        ship_to_zip as ship_to_postal_code,
        ship_to_country,
        
        -- Special instructions
        special_instr as special_instructions,
        packing_slip_msg as packing_slip_message,
        
        -- Flags
        case 
            when is_rush_flg = 'Y' then true
            when is_rush_flg = 'N' then false
            else null
        end as is_rush_flag,
        
        case 
            when is_frozen_flg = 'Y' then true
            when is_frozen_flg = 'N' then false
            else null
        end as is_frozen_flag,
        
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
            when total_quantity < 0 then 'NEGATIVE_QUANTITY'
            when order_date > ship_date then 'INVALID_DATE_ORDER'
            else 'VALID'
        end as data_quality_status,
        
        -- Business date derivation
        case 
            when order_date is not null then order_date
            when created_timestamp is not null then cast(created_timestamp as date)
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
            'order_header_id'
        ]) }} as order_header_sk,
        
        -- Add row hash for change detection
        {{ dbt_utils.generate_surrogate_key([
            'order_status',
            'total_quantity', 
            'total_lines',
            'ship_date',
            'modified_timestamp'
        ]) }} as row_hash,
        
        -- Current timestamp for processing
        current_timestamp as dbt_processed_at
        
    from standardized
)

select * from final

-- Data quality check: ensure order numbers are unique per company/facility
{% if is_incremental() %}
    -- For incremental runs, only check new/updated records
    where extracted_at > (select max(extracted_at) from {{ this }})
{% endif %}