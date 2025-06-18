-- Insert test data for dbt transformations

-- Test users
INSERT INTO raw_ldap.users (
    _sdc_extracted_at, _sdc_received_at, _sdc_sequence, _sdc_table_version,
    dn, uid, cn, sn, given_name, mail, employee_number, employee_type,
    department_number, telephone_number, mobile, object_class, member_of,
    create_timestamp, modify_timestamp, title
) VALUES
(
    '2024-01-01 12:00:00+00', '2024-01-01 12:00:00+00', 1, 1,
    'uid=john.doe,ou=users,dc=test,dc=com', 'john.doe', 'John Doe', 'Doe', 'John',
    'john.doe@test.com', '1001', 'active', 'engineering', '+1-555-1234', '+1-555-5678',
    ARRAY['inetOrgPerson', 'organizationalPerson', 'person', 'top'],
    ARRAY['cn=engineering-team,ou=groups,dc=test,dc=com', 'cn=managers,ou=groups,dc=test,dc=com'],
    '2024-01-01 10:00:00+00', '2024-01-01 11:00:00+00', 'Senior Engineer'
),
(
    '2024-01-01 12:00:01+00', '2024-01-01 12:00:01+00', 2, 1,
    'uid=jane.smith,ou=users,dc=test,dc=com', 'jane.smith', 'Jane Smith', 'Smith', 'Jane',
    'jane.smith@test.com', '1002', 'active', 'sales', '+1-555-2345', '+1-555-6789',
    ARRAY['inetOrgPerson', 'organizationalPerson', 'person', 'top'],
    ARRAY['cn=sales-team,ou=groups,dc=test,dc=com', 'cn=managers,ou=groups,dc=test,dc=com'],
    '2024-01-01 10:01:00+00', '2024-01-01 11:01:00+00', 'Sales Manager'
),
(
    '2024-01-01 12:00:02+00', '2024-01-01 12:00:02+00', 3, 1,
    'uid=bob.wilson,ou=users,dc=test,dc=com', 'bob.wilson', 'Bob Wilson', 'Wilson', 'Bob',
    'bob.wilson@test.com', '1003', 'active', 'engineering', '+1-555-3456', '+1-555-7890',
    ARRAY['inetOrgPerson', 'organizationalPerson', 'person', 'top'],
    ARRAY['cn=engineering-team,ou=groups,dc=test,dc=com', 'cn=developers,ou=groups,dc=test,dc=com'],
    '2024-01-01 10:02:00+00', '2024-01-01 11:02:00+00', 'Software Developer'
),
(
    '2024-01-01 12:00:03+00', '2024-01-01 12:00:03+00', 4, 1,
    'uid=alice.johnson,ou=users,dc=test,dc=com', 'alice.johnson', 'Alice Johnson', 'Johnson', 'Alice',
    'alice.johnson@test.com', '1004', 'active', 'hr', '+1-555-4567', '+1-555-8901',
    ARRAY['inetOrgPerson', 'organizationalPerson', 'person', 'top'],
    ARRAY['cn=hr-team,ou=groups,dc=test,dc=com', 'cn=managers,ou=groups,dc=test,dc=com'],
    '2024-01-01 10:03:00+00', '2024-01-01 11:03:00+00', 'HR Director'
),
(
    '2024-01-01 12:00:04+00', '2024-01-01 12:00:04+00', 5, 1,
    'uid=charlie.brown,ou=users,dc=test,dc=com', 'charlie.brown', 'Charlie Brown', 'Brown', 'Charlie',
    'charlie.brown@test.com', '1005', 'inactive', 'sales', '+1-555-5678', '+1-555-9012',
    ARRAY['inetOrgPerson', 'organizationalPerson', 'person', 'top'],
    ARRAY['cn=sales-team,ou=groups,dc=test,dc=com'],
    '2024-01-01 10:04:00+00', '2024-01-01 11:04:00+00', NULL
),
(
    '2024-01-01 12:00:05+00', '2024-01-01 12:00:05+00', 6, 1,
    'uid=svc-app1,ou=users,dc=test,dc=com', 'svc-app1', NULL, NULL, NULL,
    NULL, NULL, NULL, NULL, NULL, NULL,
    ARRAY['account', 'simpleSecurityObject'],
    ARRAY['cn=service-accounts,ou=groups,dc=test,dc=com'],
    '2024-01-01 10:05:00+00', '2024-01-01 11:05:00+00', NULL
);

-- Test groups
INSERT INTO raw_ldap.groups (
    _sdc_extracted_at, _sdc_received_at, _sdc_sequence, _sdc_table_version,
    dn, cn, description, member, member_uid, object_class,
    create_timestamp, modify_timestamp
) VALUES
(
    '2024-01-01 12:01:00+00', '2024-01-01 12:01:00+00', 1, 1,
    'cn=engineering-team,ou=groups,dc=test,dc=com', 'engineering-team', 'Engineering Team Members',
    ARRAY['uid=john.doe,ou=users,dc=test,dc=com', 'uid=bob.wilson,ou=users,dc=test,dc=com'],
    ARRAY['john.doe', 'bob.wilson'],
    ARRAY['groupOfNames', 'top'],
    '2024-01-01 10:00:00+00', '2024-01-01 11:30:00+00'
),
(
    '2024-01-01 12:01:01+00', '2024-01-01 12:01:01+00', 2, 1,
    'cn=sales-team,ou=groups,dc=test,dc=com', 'sales-team', 'Sales Team Members',
    ARRAY['uid=jane.smith,ou=users,dc=test,dc=com', 'uid=charlie.brown,ou=users,dc=test,dc=com'],
    ARRAY['jane.smith', 'charlie.brown'],
    ARRAY['groupOfNames', 'top'],
    '2024-01-01 10:01:00+00', '2024-01-01 11:31:00+00'
),
(
    '2024-01-01 12:01:02+00', '2024-01-01 12:01:02+00', 3, 1,
    'cn=managers,ou=groups,dc=test,dc=com', 'managers', 'Company Managers',
    ARRAY['uid=john.doe,ou=users,dc=test,dc=com', 'uid=jane.smith,ou=users,dc=test,dc=com', 'uid=alice.johnson,ou=users,dc=test,dc=com'],
    ARRAY['john.doe', 'jane.smith', 'alice.johnson'],
    ARRAY['groupOfNames', 'top'],
    '2024-01-01 10:02:00+00', '2024-01-01 11:32:00+00'
),
(
    '2024-01-01 12:01:03+00', '2024-01-01 12:01:03+00', 4, 1,
    'cn=developers,ou=groups,dc=test,dc=com', 'developers', 'Software Developers',
    ARRAY['uid=john.doe,ou=users,dc=test,dc=com', 'uid=bob.wilson,ou=users,dc=test,dc=com'],
    ARRAY['john.doe', 'bob.wilson'],
    ARRAY['groupOfNames', 'top'],
    '2024-01-01 10:03:00+00', '2024-01-01 11:33:00+00'
),
(
    '2024-01-01 12:01:04+00', '2024-01-01 12:01:04+00', 5, 1,
    'cn=hr-team,ou=groups,dc=test,dc=com', 'hr-team', 'HR Team Members',
    ARRAY['uid=alice.johnson,ou=users,dc=test,dc=com'],
    ARRAY['alice.johnson'],
    ARRAY['groupOfNames', 'top'],
    '2024-01-01 10:04:00+00', '2024-01-01 11:34:00+00'
),
(
    '2024-01-01 12:01:05+00', '2024-01-01 12:01:05+00', 6, 1,
    'cn=service-accounts,ou=groups,dc=test,dc=com', 'service-accounts', 'Service Accounts',
    ARRAY['uid=svc-app1,ou=users,dc=test,dc=com'],
    ARRAY['svc-app1'],
    ARRAY['groupOfNames', 'top'],
    '2024-01-01 10:05:00+00', '2024-01-01 11:35:00+00'
);

-- Test organizational units
INSERT INTO raw_ldap.organizational_units (
    _sdc_extracted_at, _sdc_received_at, _sdc_sequence, _sdc_table_version,
    dn, ou, description, business_category, object_class,
    create_timestamp, modify_timestamp
) VALUES
(
    '2024-01-01 12:02:00+00', '2024-01-01 12:02:00+00', 1, 1,
    'ou=users,dc=test,dc=com', 'users', 'User accounts', NULL,
    ARRAY['organizationalUnit', 'top'],
    '2024-01-01 09:00:00+00', '2024-01-01 09:00:00+00'
),
(
    '2024-01-01 12:02:01+00', '2024-01-01 12:02:01+00', 2, 1,
    'ou=groups,dc=test,dc=com', 'groups', 'Group definitions', NULL,
    ARRAY['organizationalUnit', 'top'],
    '2024-01-01 09:01:00+00', '2024-01-01 09:01:00+00'
),
(
    '2024-01-01 12:02:02+00', '2024-01-01 12:02:02+00', 3, 1,
    'ou=departments,dc=test,dc=com', 'departments', 'Organizational departments', NULL,
    ARRAY['organizationalUnit', 'top'],
    '2024-01-01 09:02:00+00', '2024-01-01 09:02:00+00'
),
(
    '2024-01-01 12:02:03+00', '2024-01-01 12:02:03+00', 4, 1,
    'ou=engineering,ou=departments,dc=test,dc=com', 'engineering', 'Engineering Department', 'Technology',
    ARRAY['organizationalUnit', 'top'],
    '2024-01-01 09:03:00+00', '2024-01-01 09:03:00+00'
),
(
    '2024-01-01 12:02:04+00', '2024-01-01 12:02:04+00', 5, 1,
    'ou=sales,ou=departments,dc=test,dc=com', 'sales', 'Sales Department', 'Sales',
    ARRAY['organizationalUnit', 'top'],
    '2024-01-01 09:04:00+00', '2024-01-01 09:04:00+00'
),
(
    '2024-01-01 12:02:05+00', '2024-01-01 12:02:05+00', 6, 1,
    'ou=hr,ou=departments,dc=test,dc=com', 'hr', 'Human Resources Department', 'Human Resources',
    ARRAY['organizationalUnit', 'top'],
    '2024-01-01 09:05:00+00', '2024-01-01 09:05:00+00'
);
