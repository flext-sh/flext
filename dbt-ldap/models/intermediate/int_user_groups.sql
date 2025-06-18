{{ config(
    materialized='view'
) }}

with users as (
    select * from {{ ref('stg_users') }}
),

groups as (
    select * from {{ ref('stg_groups') }}
),

-- Unnest user memberOf to create user-group relationships
user_memberships as (
    select
        u.uid,
        u.dn as user_dn,
        u.common_name as user_name,
        u.email,
        u.account_type,
        json_array_elements_text(u.member_of::json) as group_dn
    from users u
    where u.member_of != '[]'::json
),

-- Join with groups to get group details
enriched_memberships as (
    select
        um.uid,
        um.user_dn,
        um.user_name,
        um.email,
        um.account_type,
        um.group_dn,
        g.group_name,
        g.group_category,
        g.group_classification,
        g.organizational_unit as group_ou,
        -- Check if it's a direct membership (not nested)
        case
            when g.dn = um.group_dn then true
            else false
        end as is_direct_member
    from user_memberships um
    left join groups g on g.dn = um.group_dn
),

-- Add membership statistics
final as (
    select
        *,
        -- Count total groups per user
        count(*) over (partition by uid) as total_group_count,
        -- Count security groups per user
        sum(case when group_category = 'Security' then 1 else 0 end)
            over (partition by uid) as security_group_count,
        -- Identify primary group (first alphabetically for consistency)
        first_value(group_name) over (
            partition by uid
            order by group_name
        ) as primary_group
    from enriched_memberships
)

select * from final
