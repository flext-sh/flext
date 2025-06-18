{{ config(
    materialized='table',
    indexes=[
        {'columns': ['user_id', 'group_id'], 'unique': true},
        {'columns': ['user_id']},
        {'columns': ['group_id']},
        {'columns': ['membership_date']}
    ]
) }}

with memberships as (
    select * from {{ ref('int_user_groups') }}
),

users as (
    select
        user_id,
        full_name,
        email,
        account_type,
        is_disabled,
        organizational_unit_id,
        created_at as user_created_at
    from {{ ref('dim_users') }}
),

groups as (
    select
        group_id,
        group_name,
        group_category,
        group_classification,
        organizational_unit_id,
        created_at as group_created_at
    from {{ ref('dim_groups') }}
),

final as (
    select
        -- User dimensions
        m.uid as user_id,
        u.full_name as user_name,
        u.email as user_email,
        u.account_type,
        u.is_disabled as user_is_disabled,
        u.organizational_unit_id as user_ou_id,

        -- Group dimensions
        m.group_name as group_id,
        m.group_name,
        m.group_category,
        m.group_classification,
        g.organizational_unit_id as group_ou_id,

        -- Membership facts
        m.is_direct_member,
        m.total_group_count as user_total_groups,
        m.security_group_count as user_security_groups,

        -- Derived metrics
        case
            when u.organizational_unit_id = g.organizational_unit_id then true
            else false
        end as same_ou_membership,

        case
            when m.group_name = m.primary_group then true
            else false
        end as is_primary_group,

        -- Dates (approximate membership date as the later of user/group creation)
        greatest(u.user_created_at, g.group_created_at)::date as membership_date,

        -- Metadata
        m.user_dn,
        m.group_dn,
        current_timestamp as last_updated_at

    from memberships m
    inner join users u on m.uid = u.user_id
    inner join groups g on m.group_name = g.group_id
)

select * from final
