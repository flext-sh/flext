{{ config(
    materialized='view',
    post_hook="SELECT 'Staging customers model completed' as status FROM dual"
) }}

-- Staging model for customers data from FLEXT target
-- Uses modern Oracle SQL with JSON processing

WITH source_customers AS (
    SELECT 
        customer_id,
        customer_name,
        email,
        phone,
        address,
        created_at,
        updated_at,
        CASE 
            WHEN is_active = 1 THEN 'active'
            ELSE 'inactive' 
        END as customer_status,
        credit_limit,
        customer_metadata,
        -- Extract JSON attributes using Oracle's JSON functions
        JSON_VALUE(customer_metadata, '$.tier') as customer_tier,
        JSON_VALUE(customer_metadata, '$.preferences.newsletter') as newsletter_preference,
        JSON_VALUE(customer_metadata, '$.preferences.marketing') as marketing_preference
    FROM {{ var('flext_target_schema') }}.customers
    WHERE customer_name IS NOT NULL
),

enriched_customers AS (
    SELECT 
        *,
        -- Calculate customer age in days
        TRUNC(SYSDATE - created_at) as customer_age_days,
        -- Categorize credit limits
        CASE 
            WHEN credit_limit >= 50000 THEN 'enterprise'
            WHEN credit_limit >= 25000 THEN 'professional' 
            WHEN credit_limit >= 10000 THEN 'standard'
            ELSE 'basic'
        END as credit_tier,
        -- Extract tags from JSON array
        JSON_QUERY(customer_metadata, '$.tags[*]') as customer_tags_json
    FROM source_customers
)

SELECT 
    customer_id,
    customer_name,
    LOWER(email) as email_normalized,
    phone,
    address,
    created_at,
    updated_at,
    customer_status,
    credit_limit,
    customer_tier,
    credit_tier,
    customer_age_days,
    CASE 
        WHEN newsletter_preference = 'true' THEN 1 
        ELSE 0 
    END as newsletter_opted_in,
    CASE 
        WHEN marketing_preference = 'true' THEN 1 
        ELSE 0 
    END as marketing_opted_in,
    customer_tags_json,
    customer_metadata as raw_metadata
FROM enriched_customers