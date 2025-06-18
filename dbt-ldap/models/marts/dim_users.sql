{{ config(
    materialized='table',
    indexes=[
        {'columns': ['user_id'], 'unique': true},
        {'columns': ['email'], 'unique': true},
        {'columns': ['employee_id']},
        {'columns': ['manager_id']},
        {'columns': ['organizational_unit_id']}
    ]
) }}

with users as (
    select * from {{ ref('stg_users') }}
),

user_groups as (
    select
        uid,
        count(distinct group_dn) as group_count,
        count(distinct case when group_category = 'Security' then group_dn end) as security_group_count,
        string_agg(distinct group_name, ', ' order by group_name) as group_names,
        max(primary_group) as primary_group
    from {{ ref('int_user_groups') }}
    group by uid
),

org_hierarchy as (
    select * from {{ ref('int_org_hierarchy') }}
),

final as (
    select
        -- Identifiers
        u.uid as user_id,
        u.dn as user_dn,
        u.employee_id,

        -- Basic Information
        u.common_name as full_name,
        u.given_name as first_name,
        u.surname as last_name,
        u.display_name,
        u.email,
        u.email_domain,

        -- Contact Information
        u.phone,
        u.mobile_phone,

        -- Employment Information
        u.job_title,
        u.department,
        u.account_type,

        -- Account Status
        u.is_disabled,
        u.has_email,
        u.days_since_modified,
        case
            when u.days_since_modified > 365 then true
            else false
        end as is_stale_account,

        -- Organizational Hierarchy
        u.organizational_unit,
        oh.ou_name as ou_name,
        oh.path as ou_path,
        oh.ou_type,
        oh.dn as organizational_unit_id,

        -- Manager Relationship
        split_part(split_part(u.manager_dn, '=', 2), ',', 1) as manager_id,
        u.manager_dn,

        -- Group Membership
        coalesce(ug.group_count, 0) as total_groups,
        coalesce(ug.security_group_count, 0) as security_groups,
        ug.primary_group,
        ug.group_names,

        -- Metadata
        u.description,
        u.object_classes,
        u.created_at,
        u.modified_at,
        u.created_year,
        current_timestamp as last_updated_at

    from users u
    left join user_groups ug on u.uid = ug.uid
    left join org_hierarchy oh on u.organizational_unit = oh.ou_name
)

select * from final
