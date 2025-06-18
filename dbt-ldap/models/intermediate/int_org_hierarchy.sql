{{ config(
    materialized='view'
) }}

with org_units as (
    select * from {{ ref('stg_org_units') }}
),

-- Recursive CTE to build OU hierarchy
ou_hierarchy as (
    -- Base case: top-level OUs
    select
        dn,
        ou_name,
        parent_dn,
        ou_type,
        hierarchy_depth,
        ou_name as path,
        dn as root_ou_dn,
        ou_name as root_ou_name,
        1 as level_from_root
    from org_units
    where is_top_level = true

    union all

    -- Recursive case: child OUs
    select
        o.dn,
        o.ou_name,
        o.parent_dn,
        o.ou_type,
        o.hierarchy_depth,
        h.path || ' > ' || o.ou_name as path,
        h.root_ou_dn,
        h.root_ou_name,
        h.level_from_root + 1 as level_from_root
    from org_units o
    inner join ou_hierarchy h on o.parent_ou_dn = h.dn
),

-- Add statistics about the hierarchy
hierarchy_stats as (
    select
        *,
        -- Count of direct children
        (
            select count(*)
            from org_units o2
            where o2.parent_ou_dn = ou_hierarchy.dn
        ) as direct_child_count,

        -- Count of all descendants
        (
            select count(*)
            from ou_hierarchy h2
            where h2.root_ou_dn = ou_hierarchy.dn
            and h2.dn != ou_hierarchy.dn
        ) as total_descendant_count

    from ou_hierarchy
),

-- Identify leaf nodes (OUs with no children)
final as (
    select
        *,
        case
            when direct_child_count = 0 then true
            else false
        end as is_leaf_node,

        -- Calculate the breadth of the tree at this level
        count(*) over (partition by root_ou_dn, level_from_root) as siblings_at_level

    from hierarchy_stats
)

select * from final
