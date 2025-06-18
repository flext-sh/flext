{{ config(
    materialized='table',
    indexes=[
        {'columns': ['group_id'], 'unique': true},
        {'columns': ['group_type']},
        {'columns': ['group_classification']},
        {'columns': ['managed_by_id']}
    ]
) }}

with groups as (
    select * from {{ ref('stg_groups') }}
),

group_members as (
    select
        group_dn,
        count(distinct uid) as unique_member_count,
        string_agg(distinct account_type, ', ' order by account_type) as member_account_types
    from {{ ref('int_user_groups') }}
    group by group_dn
),

org_hierarchy as (
    select * from {{ ref('int_org_hierarchy') }}
),

final as (
    select
        -- Identifiers
        g.group_name as group_id,
        g.dn as group_dn,

        -- Basic Information
        g.group_name,
        g.description,

        -- Group Classification
        g.group_type,
        g.group_category,
        g.group_classification,

        -- Membership Information
        g.member_count as total_member_count,
        coalesce(gm.unique_member_count, 0) as active_member_count,
        g.is_empty,
        case
            when g.member_count > 100 then 'Large'
            when g.member_count > 20 then 'Medium'
            when g.member_count > 0 then 'Small'
            else 'Empty'
        end as group_size_category,
        gm.member_account_types,

        -- Organizational Hierarchy
        g.organizational_unit,
        oh.ou_name,
        oh.path as ou_path,
        oh.ou_type,
        oh.dn as organizational_unit_id,

        -- Management
        split_part(split_part(g.managed_by_dn, '=', 2), ',', 1) as managed_by_id,
        g.managed_by_dn,

        -- Status Indicators
        g.recently_modified,
        case
            when g.is_empty and g.created_at < current_date - interval '90 days'
            then true
            else false
        end as is_orphaned,

        -- Metadata
        g.members as member_dns,
        g.member_uids,
        g.object_classes,
        g.created_at,
        g.modified_at,
        g.created_year,
        current_timestamp as last_updated_at

    from groups g
    left join group_members gm on g.dn = gm.group_dn
    left join org_hierarchy oh on g.organizational_unit = oh.ou_name
)

select * from final
