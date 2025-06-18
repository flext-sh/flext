-- Create schema for raw LDAP data
CREATE SCHEMA IF NOT EXISTS raw_ldap;

-- Raw users table (as extracted by tap-ldap)
CREATE TABLE IF NOT EXISTS raw_ldap.users (
    _sdc_extracted_at TIMESTAMP WITH TIME ZONE,
    _sdc_batched_at TIMESTAMP WITH TIME ZONE,
    _sdc_received_at TIMESTAMP WITH TIME ZONE,
    _sdc_sequence BIGINT,
    _sdc_table_version BIGINT,
    dn TEXT PRIMARY KEY,
    uid TEXT,
    cn TEXT,
    sn TEXT,
    given_name TEXT,
    mail TEXT,
    employee_number TEXT,
    employee_type TEXT,
    department_number TEXT,
    telephone_number TEXT,
    mobile TEXT,
    object_class TEXT[],
    member_of TEXT[],
    create_timestamp TIMESTAMP WITH TIME ZONE,
    modify_timestamp TIMESTAMP WITH TIME ZONE,
    user_password TEXT,
    title TEXT,
    description TEXT
);

-- Raw groups table
CREATE TABLE IF NOT EXISTS raw_ldap.groups (
    _sdc_extracted_at TIMESTAMP WITH TIME ZONE,
    _sdc_batched_at TIMESTAMP WITH TIME ZONE,
    _sdc_received_at TIMESTAMP WITH TIME ZONE,
    _sdc_sequence BIGINT,
    _sdc_table_version BIGINT,
    dn TEXT PRIMARY KEY,
    cn TEXT,
    description TEXT,
    member TEXT[],
    member_uid TEXT[],
    object_class TEXT[],
    create_timestamp TIMESTAMP WITH TIME ZONE,
    modify_timestamp TIMESTAMP WITH TIME ZONE
);

-- Raw organizational units table
CREATE TABLE IF NOT EXISTS raw_ldap.organizational_units (
    _sdc_extracted_at TIMESTAMP WITH TIME ZONE,
    _sdc_batched_at TIMESTAMP WITH TIME ZONE,
    _sdc_received_at TIMESTAMP WITH TIME ZONE,
    _sdc_sequence BIGINT,
    _sdc_table_version BIGINT,
    dn TEXT PRIMARY KEY,
    ou TEXT,
    description TEXT,
    business_category TEXT,
    object_class TEXT[],
    create_timestamp TIMESTAMP WITH TIME ZONE,
    modify_timestamp TIMESTAMP WITH TIME ZONE
);

-- Grant permissions
GRANT USAGE ON SCHEMA raw_ldap TO dbt_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA raw_ldap TO dbt_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA raw_ldap TO dbt_user;
