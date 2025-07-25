-- Staging model for test data
-- Raw data cleaning and standardization
{{ config(materialized='view') }}

select
    cast(id as integer) as user_id,
    trim(lower(name)) as user_name,
    trim(lower(email)) as user_email,
    trim(upper(department)) as department_code,
    current_timestamp as processed_at
from {{ source('tap_csv', 'test_data') }}
where id is not null
  and name is not null
  and email is not null