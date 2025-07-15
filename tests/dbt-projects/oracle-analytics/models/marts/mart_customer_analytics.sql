{{ config(
    materialized='table',
    post_hook=[
        "CREATE INDEX IF NOT EXISTS idx_mart_customer_analytics_tier ON {{ this }} (customer_tier)",
        "INSERT INTO {{ var('flext_target_schema') }}.dbt_model_audit (model_name, rows_processed, completed_at) VALUES ('{{ this }}', SQL%ROWCOUNT, SYSDATE)"
    ]
) }}

-- Customer analytics mart combining multiple data sources
-- Demonstrates Oracle-specific SQL features and FLEXT integration patterns

WITH customer_base AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

order_metrics AS (
    SELECT 
        customer_id,
        COUNT(*) as total_orders,
        SUM(total_amount) as total_spent,
        AVG(total_amount) as avg_order_value,
        MIN(order_date) as first_order_date,
        MAX(order_date) as last_order_date,
        COUNT(CASE WHEN order_status = 'COMPLETED' THEN 1 END) as completed_orders,
        COUNT(CASE WHEN order_status = 'CANCELLED' THEN 1 END) as cancelled_orders
    FROM {{ var('flext_target_schema') }}.orders
    GROUP BY customer_id
),

product_affinity AS (
    SELECT 
        o.customer_id,
        COUNT(DISTINCT oi.product_id) as unique_products_purchased,
        LISTAGG(p.category, ', ') WITHIN GROUP (ORDER BY p.category) as purchased_categories,
        SUM(oi.quantity) as total_items_purchased
    FROM {{ var('flext_target_schema') }}.orders o
    JOIN {{ var('flext_target_schema') }}.order_items oi ON o.order_id = oi.order_id
    JOIN {{ var('flext_target_schema') }}.products p ON oi.product_id = p.product_id
    WHERE o.order_status = 'COMPLETED'
    GROUP BY o.customer_id
),

customer_scoring AS (
    SELECT 
        c.customer_id,
        -- RFM Analysis components
        TRUNC(SYSDATE - om.last_order_date) as recency_days,
        om.total_orders as frequency,
        om.total_spent as monetary,
        -- Calculate percentile rankings for RFM
        PERCENT_RANK() OVER (ORDER BY TRUNC(SYSDATE - om.last_order_date) DESC) as recency_percentile,
        PERCENT_RANK() OVER (ORDER BY om.total_orders) as frequency_percentile,
        PERCENT_RANK() OVER (ORDER BY om.total_spent) as monetary_percentile
    FROM customer_base c
    LEFT JOIN order_metrics om ON c.customer_id = om.customer_id
),

final_analytics AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.email_normalized,
        c.customer_status,
        c.customer_tier,
        c.credit_tier,
        c.customer_age_days,
        c.newsletter_opted_in,
        c.marketing_opted_in,
        
        -- Order metrics
        COALESCE(om.total_orders, 0) as total_orders,
        COALESCE(om.total_spent, 0) as total_spent,
        COALESCE(om.avg_order_value, 0) as avg_order_value,
        om.first_order_date,
        om.last_order_date,
        COALESCE(om.completed_orders, 0) as completed_orders,
        COALESCE(om.cancelled_orders, 0) as cancelled_orders,
        
        -- Product affinity
        COALESCE(pa.unique_products_purchased, 0) as unique_products_purchased,
        pa.purchased_categories,
        COALESCE(pa.total_items_purchased, 0) as total_items_purchased,
        
        -- Customer scoring
        cs.recency_days,
        cs.frequency,
        cs.monetary,
        
        -- RFM Score (1-5 scale)
        CASE 
            WHEN cs.recency_percentile >= 0.8 THEN 5
            WHEN cs.recency_percentile >= 0.6 THEN 4
            WHEN cs.recency_percentile >= 0.4 THEN 3
            WHEN cs.recency_percentile >= 0.2 THEN 2
            ELSE 1
        END as recency_score,
        
        CASE 
            WHEN cs.frequency_percentile >= 0.8 THEN 5
            WHEN cs.frequency_percentile >= 0.6 THEN 4
            WHEN cs.frequency_percentile >= 0.4 THEN 3
            WHEN cs.frequency_percentile >= 0.2 THEN 2
            ELSE 1
        END as frequency_score,
        
        CASE 
            WHEN cs.monetary_percentile >= 0.8 THEN 5
            WHEN cs.monetary_percentile >= 0.6 THEN 4
            WHEN cs.monetary_percentile >= 0.4 THEN 3
            WHEN cs.monetary_percentile >= 0.2 THEN 2
            ELSE 1
        END as monetary_score,
        
        -- Customer lifetime value prediction (simplified)
        CASE 
            WHEN om.total_orders > 0 THEN 
                (om.total_spent / om.total_orders) * 
                GREATEST(1, 12 - TRUNC(SYSDATE - om.last_order_date) / 30)
            ELSE 0
        END as predicted_clv,
        
        -- Customer segment
        CASE 
            WHEN c.customer_tier = 'enterprise' AND om.total_spent > 100000 THEN 'VIP'
            WHEN c.customer_tier IN ('enterprise', 'professional') AND om.total_orders > 10 THEN 'High Value'
            WHEN om.total_orders > 5 THEN 'Regular'
            WHEN om.total_orders > 0 THEN 'Occasional'
            ELSE 'Prospect'
        END as customer_segment,
        
        -- Analysis timestamp
        SYSDATE as analysis_date
        
    FROM customer_base c
    LEFT JOIN order_metrics om ON c.customer_id = om.customer_id
    LEFT JOIN product_affinity pa ON c.customer_id = pa.customer_id
    LEFT JOIN customer_scoring cs ON c.customer_id = cs.customer_id
)

SELECT * FROM final_analytics