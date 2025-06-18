{{ config(
    materialized='view',
    indexes=[
        {'columns': ['ou_name'], 'unique': true},
        {'columns': ['parent_ou_dn']}
    ]
) }}

with source_data as (
    select *
    from {{ source('ldap', 'organizational_units') }}
    where {{ validate_dn_format('dn') }}
),

transformed as (
    select
        {{ map_ldap_ou_attributes() }},

        -- Calculate OU depth in hierarchy
        array_length(string_to_array(dn, ','), 1) - 1 as hierarchy_depth,

        -- Check if it's a top-level OU
        case
            when parent_dn = '{{ var("ldap_base_dn") }}' then true
            else false
        end as is_top_level,

        -- OU type classification
        case
            when lower(ou_name) in ('users', 'people', 'employees') then 'User Container'
            when lower(ou_name) in ('groups', 'roles') then 'Group Container'
            when lower(ou_name) in ('computers', 'servers', 'workstations') then 'Computer Container'
            when lower(ou_name) in ('services', 'applications') then 'Service Container'
            when business_category is not null then 'Business Unit'
            else 'General Container'
        end as ou_type,

        -- Extract year from created timestamp
        extract(year from {{ ldap_timestamp_to_timestamp('createTimestamp') }}) as created_year

    from source_data
)

select * from transformed
