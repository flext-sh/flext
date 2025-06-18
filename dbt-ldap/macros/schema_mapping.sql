-- Macro to map LDAP attributes to normalized columns
{% macro map_ldap_user_attributes() %}
    dn,
    {{ parse_dn('dn') }},
    uid,
    cn as common_name,
    sn as surname,
    givenName as given_name,
    coalesce(displayName, cn) as display_name,
    mail as email,
    {{ extract_email_domain('mail') }} as email_domain,
    telephoneNumber as phone,
    mobile as mobile_phone,
    title as job_title,
    department,
    employeeNumber as employee_id,
    manager as manager_dn,
    {{ normalize_array_field('memberOf') }} as member_of,
    {{ normalize_array_field('objectClass') }} as object_classes,
    userAccountControl as account_control,
    case
        when userAccountControl::int & 2 = 2 then true
        else false
    end as is_disabled,
    {{ ldap_timestamp_to_timestamp('createTimestamp') }} as created_at,
    {{ ldap_timestamp_to_timestamp('modifyTimestamp') }} as modified_at,
    description,
    {{ extract_ou_from_dn('dn') }} as organizational_unit
{% endmacro %}

-- Macro to map LDAP group attributes
{% macro map_ldap_group_attributes() %}
    dn,
    {{ parse_dn('dn') }},
    cn as group_name,
    description,
    {{ normalize_array_field('member') }} as members,
    {{ normalize_array_field('memberUid') }} as member_uids,
    {{ count_group_members('member') }} as member_count,
    groupType as group_type,
    case
        when groupType::int & 2147483648 = 2147483648 then 'Security'
        else 'Distribution'
    end as group_category,
    {{ normalize_array_field('objectClass') }} as object_classes,
    {{ ldap_timestamp_to_timestamp('createTimestamp') }} as created_at,
    {{ ldap_timestamp_to_timestamp('modifyTimestamp') }} as modified_at,
    managedBy as managed_by_dn,
    {{ extract_ou_from_dn('dn') }} as organizational_unit
{% endmacro %}

-- Macro to map organizational unit attributes
{% macro map_ldap_ou_attributes() %}
    dn,
    {{ parse_dn('dn') }},
    ou as ou_name,
    description,
    businessCategory as business_category,
    postalAddress as postal_address,
    telephoneNumber as phone,
    {{ normalize_array_field('objectClass') }} as object_classes,
    {{ ldap_timestamp_to_timestamp('createTimestamp') }} as created_at,
    {{ ldap_timestamp_to_timestamp('modifyTimestamp') }} as modified_at,
    managedBy as managed_by_dn,
    parent_dn as parent_ou_dn
{% endmacro %}

-- Macro to validate DN format
{% macro validate_dn_format(dn_column) %}
    {{ dn_column }} ~ '^(\w+=[^,]+)(,\w+=[^,]+)*$'
{% endmacro %}

-- Macro to extract specific object class
{% macro has_object_class(object_class_field, class_name) %}
    {{ object_class_field }}::text like '%"{{ class_name }}"%'
{% endmacro %}
