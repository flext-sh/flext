{{ config(
    materialized='view',
    indexes=[
        {'columns': ['uid'], 'unique': true},
        {'columns': ['email']},
        {'columns': ['employee_id']}
    ]
) }}

with source_data as (
    select *
    from {{ source('ldap', 'users') }}
    where {{ validate_dn_format('dn') }}
),

transformed as (
    select
        {{ map_ldap_user_attributes() }},
        -- Additional computed fields
        case
            when email is not null then true
            else false
        end as has_email,

        case
            when employee_id is not null then 'Employee'
            when uid like 'svc-%' then 'Service Account'
            when uid like 'app-%' then 'Application Account'
            else 'Standard User'
        end as account_type,

        -- Extract year from created timestamp
        extract(year from {{ ldap_timestamp_to_timestamp('createTimestamp') }}) as created_year,

        -- Days since last modification
        current_date - {{ ldap_timestamp_to_timestamp('modifyTimestamp') }}::date as days_since_modified

    from source_data
)

select * from transformed
