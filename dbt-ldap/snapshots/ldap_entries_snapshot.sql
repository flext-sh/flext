{% snapshot ldap_entries_snapshot %}

{{
    config(
      target_schema='snapshots',
      unique_key='dn',
      strategy='timestamp',
      updated_at='modified_at',
      invalidate_hard_deletes=True,
    )
}}

-- Snapshot of all LDAP entries to track changes over time
select
    dn,
    case
        when dn like 'uid=%' then 'user'
        when dn like 'cn=%' and dn like '%ou=groups%' then 'group'
        when dn like 'ou=%' then 'organizational_unit'
        else 'other'
    end as entry_type,

    -- Extract the RDN value as a consistent identifier
    split_part(split_part(dn, '=', 2), ',', 1) as entry_id,

    -- User-specific fields
    case when uid is not null then uid else null end as uid,
    case when mail is not null then mail else null end as email,
    case when employeeNumber is not null then employeeNumber else null end as employee_id,

    -- Group-specific fields
    case when cn is not null and dn like '%ou=groups%' then cn else null end as group_name,

    -- OU-specific fields
    case when ou is not null then ou else null end as ou_name,

    -- Common fields
    cn as common_name,
    description,
    {{ normalize_array_field('objectClass') }} as object_classes,

    -- Timestamps
    {{ ldap_timestamp_to_timestamp('createTimestamp') }} as created_at,
    {{ ldap_timestamp_to_timestamp('modifyTimestamp') }} as modified_at,

    -- Snapshot metadata
    current_timestamp as snapshot_at

from {{ source('ldap', 'all_entries') }}

{% endsnapshot %}
