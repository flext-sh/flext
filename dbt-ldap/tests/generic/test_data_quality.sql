-- Generic data quality tests for dbt-ldap

-- Test that all users have unique UIDs
select count(*) as failures
from (
    select uid, count(*) as cnt
    from {{ ref('stg_users') }}
    group by uid
    having count(*) > 1
) duplicates
where failures > 0;

-- Test that all DNs are properly formatted
select count(*) as failures
from {{ ref('stg_users') }}
where not {{ validate_dn_format('dn') }};

-- Test that email domains are valid
select count(*) as failures
from {{ ref('dim_users') }}
where email is not null
  and email_domain is null;

-- Test referential integrity between users and groups
select count(*) as failures
from {{ ref('fact_memberships') }} m
left join {{ ref('dim_users') }} u on m.user_id = u.user_id
left join {{ ref('dim_groups') }} g on m.group_id = g.group_id
where u.user_id is null or g.group_id is null;

-- Test that organizational units form a valid hierarchy
with recursive ou_check as (
    select dn, parent_ou_dn, 1 as depth
    from {{ ref('stg_org_units') }}
    where parent_ou_dn = '{{ var("ldap_base_dn") }}'

    union all

    select o.dn, o.parent_ou_dn, oc.depth + 1
    from {{ ref('stg_org_units') }} o
    join ou_check oc on o.parent_ou_dn = oc.dn
    where oc.depth < 10  -- Prevent infinite loops
)
select count(*) as failures
from {{ ref('stg_org_units') }} o
left join ou_check oc on o.dn = oc.dn
where oc.dn is null
  and o.parent_ou_dn != '{{ var("ldap_base_dn") }}';

-- Test that groups have at least one member (or placeholder)
select count(*) as failures
from {{ ref('stg_groups') }}
where member_count = 0 and not is_empty;

-- Test that modifyTimestamp is not in the future
select count(*) as failures
from (
    select * from {{ ref('stg_users') }}
    union all
    select * from {{ ref('stg_groups') }}
) all_entries
where modified_at > current_timestamp;
