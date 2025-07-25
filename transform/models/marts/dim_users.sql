-- User dimension table
-- Business logic and enrichment
{{ config(materialized='table') }}

select
    user_id,
    user_name,
    user_email,
    department_code,
    case 
        when department_code = 'TI' then 'Technology'
        when department_code = 'RH' then 'Human Resources'
        when department_code = 'FINANCEIRO' then 'Finance'
        when department_code = 'MARKETING' then 'Marketing'
        when department_code = 'VENDAS' then 'Sales'
        else 'Other'
    end as department_name,
    case
        when user_email like '%@example.com' then 'Internal'
        else 'External'
    end as user_type,
    processed_at,
    current_timestamp as created_at
from {{ ref('stg_test_data') }}