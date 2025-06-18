-- Tests for LDAP macros

-- Test parse_dn macro
{% test test_parse_dn %}
with test_data as (
    select 'uid=jdoe,ou=users,dc=example,dc=com' as dn
)
select
    {{ parse_dn('dn') }}
from test_data
where rdn != 'uid=jdoe'
   or rdn_value != 'jdoe'
   or rdn_attribute != 'uid'
   or parent_dn != 'ou=users,dc=example,dc=com'
{% endtest %}

-- Test extract_ou_from_dn macro
{% test test_extract_ou_from_dn %}
with test_data as (
    select 'uid=jdoe,ou=users,dc=example,dc=com' as dn1,
           'cn=admin,dc=example,dc=com' as dn2
)
select
    {{ extract_ou_from_dn('dn1') }} as ou1,
    {{ extract_ou_from_dn('dn2') }} as ou2
from test_data
where ou1 != 'users'
   or ou2 is not null
{% endtest %}

-- Test normalize_array_field macro
{% test test_normalize_array_field %}
with test_data as (
    select '["value1", "value2"]' as array_field,
           '"single_value"' as single_field,
           null as null_field
)
select
    {{ normalize_array_field('array_field') }} as normalized_array,
    {{ normalize_array_field('single_field') }} as normalized_single,
    {{ normalize_array_field('null_field') }} as normalized_null
from test_data
where json_array_length(normalized_array::json) != 2
   or json_array_length(normalized_single::json) != 1
   or normalized_null::text != '[]'
{% endtest %}

-- Test ldap_timestamp_to_timestamp macro
{% test test_ldap_timestamp_conversion %}
with test_data as (
    select '20240101120000Z' as ldap_ts,
           '20240101120000.0Z' as ldap_ts_with_fraction,
           '2024-01-01 12:00:00' as normal_ts
)
select
    {{ ldap_timestamp_to_timestamp('ldap_ts') }} as converted_ts1,
    {{ ldap_timestamp_to_timestamp('ldap_ts_with_fraction') }} as converted_ts2,
    {{ ldap_timestamp_to_timestamp('normal_ts') }} as converted_ts3
from test_data
where extract(year from converted_ts1) != 2024
   or extract(hour from converted_ts1) != 12
   or converted_ts3 is null
{% endtest %}

-- Test count_group_members macro
{% test test_count_group_members %}
with test_data as (
    select '["member1", "member2", "member3"]' as members_array,
           '"single_member"' as single_member,
           null as no_members
)
select
    {{ count_group_members('members_array') }} as count1,
    {{ count_group_members('single_member') }} as count2,
    {{ count_group_members('no_members') }} as count3
from test_data
where count1 != 3
   or count2 != 1
   or count3 != 0
{% endtest %}

-- Test extract_email_domain macro
{% test test_extract_email_domain %}
with test_data as (
    select 'user@example.com' as email1,
           'admin@subdomain.example.org' as email2,
           'invalid-email' as email3,
           null as email4
)
select
    {{ extract_email_domain('email1') }} as domain1,
    {{ extract_email_domain('email2') }} as domain2,
    {{ extract_email_domain('email3') }} as domain3,
    {{ extract_email_domain('email4') }} as domain4
from test_data
where domain1 != 'example.com'
   or domain2 != 'subdomain.example.org'
   or domain3 is not null
   or domain4 is not null
{% endtest %}

-- Test validate_dn_format macro
{% test test_validate_dn_format %}
with test_data as (
    select 'uid=jdoe,ou=users,dc=example,dc=com' as valid_dn,
           'invalid_dn_format' as invalid_dn,
           'uid=,dc=com' as empty_value_dn,
           '=value,dc=com' as empty_key_dn
)
select *
from test_data
where not {{ validate_dn_format('valid_dn') }}
   or {{ validate_dn_format('invalid_dn') }}
   or {{ validate_dn_format('empty_value_dn') }}
   or {{ validate_dn_format('empty_key_dn') }}
{% endtest %}

-- Test has_object_class macro
{% test test_has_object_class %}
with test_data as (
    select '["inetOrgPerson", "person", "top"]' as object_classes
)
select *
from test_data
where not {{ has_object_class('object_classes', 'person') }}
   or not {{ has_object_class('object_classes', 'inetOrgPerson') }}
   or {{ has_object_class('object_classes', 'nonexistent') }}
{% endtest %}
