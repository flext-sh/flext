{{ config(
    materialized='view',
    indexes=[
        {'columns': ['group_name'], 'unique': true},
        {'columns': ['group_type']}
    ]
) }}

with source_data as (
    select *
    from {{ source('ldap', 'groups') }}
    where {{ validate_dn_format('dn') }}
),

transformed as (
    select
        {{ map_ldap_group_attributes() }},

        -- Group classification
        case
            when group_name like 'app-%' then 'Application'
            when group_name like 'role-%' then 'Role-based'
            when group_name like 'dept-%' then 'Department'
            when group_name like 'team-%' then 'Team'
            when group_name like 'project-%' then 'Project'
            else 'General'
        end as group_classification,

        -- Check if group is empty
        case
            when {{ count_group_members('member') }} = 0 then true
            when {{ count_group_members('member') }} = 1
                and members::text like '%placeholder%' then true
            else false
        end as is_empty,

        -- Extract year from created timestamp
        extract(year from {{ ldap_timestamp_to_timestamp('createTimestamp') }}) as created_year,

        -- Check if recently modified (within 30 days)
        case
            when current_date - {{ ldap_timestamp_to_timestamp('modifyTimestamp') }}::date <= 30
            then true
            else false
        end as recently_modified

    from source_data
)

select * from transformed
