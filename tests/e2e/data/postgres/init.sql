-- Create schemas for dbt-ldap testing
CREATE SCHEMA IF NOT EXISTS ldap_raw;
CREATE SCHEMA IF NOT EXISTS ldap_staging;
CREATE SCHEMA IF NOT EXISTS ldap_analytics;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA ldap_raw TO dbt_user;
GRANT ALL PRIVILEGES ON SCHEMA ldap_staging TO dbt_user;
GRANT ALL PRIVILEGES ON SCHEMA ldap_analytics TO dbt_user;

-- Create audit table
CREATE TABLE IF NOT EXISTS ldap_raw.sync_audit (
    id SERIAL PRIMARY KEY,
    sync_id UUID NOT NULL,
    source_system VARCHAR(100) NOT NULL,
    sync_type VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    records_extracted INTEGER DEFAULT 0,
    records_loaded INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'running',
    error_message TEXT,
    metadata JSONB
);

-- Create tables for LDAP data
CREATE TABLE IF NOT EXISTS ldap_raw.users (
    id SERIAL PRIMARY KEY,
    dn VARCHAR(500) NOT NULL,
    uid VARCHAR(100) NOT NULL,
    cn VARCHAR(200),
    sn VARCHAR(100),
    given_name VARCHAR(100),
    display_name VARCHAR(200),
    mail VARCHAR(200),
    employee_number VARCHAR(50),
    employee_type VARCHAR(50),
    department_number VARCHAR(50),
    title VARCHAR(200),
    manager_dn VARCHAR(500),
    telephone_number VARCHAR(50),
    mobile VARCHAR(50),
    room_number VARCHAR(50),
    account_status VARCHAR(50),
    attributes JSONB,
    sync_id UUID NOT NULL,
    extracted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dn, sync_id)
);

CREATE TABLE IF NOT EXISTS ldap_raw.groups (
    id SERIAL PRIMARY KEY,
    dn VARCHAR(500) NOT NULL,
    cn VARCHAR(200) NOT NULL,
    description TEXT,
    member_dns TEXT[],
    attributes JSONB,
    sync_id UUID NOT NULL,
    extracted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dn, sync_id)
);

CREATE TABLE IF NOT EXISTS ldap_raw.organizational_units (
    id SERIAL PRIMARY KEY,
    dn VARCHAR(500) NOT NULL,
    ou VARCHAR(200) NOT NULL,
    description TEXT,
    attributes JSONB,
    sync_id UUID NOT NULL,
    extracted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dn, sync_id)
);

-- Create indexes
CREATE INDEX idx_users_uid ON ldap_raw.users(uid);
CREATE INDEX idx_users_sync_id ON ldap_raw.users(sync_id);
CREATE INDEX idx_users_employee_number ON ldap_raw.users(employee_number);
CREATE INDEX idx_groups_cn ON ldap_raw.groups(cn);
CREATE INDEX idx_groups_sync_id ON ldap_raw.groups(sync_id);
CREATE INDEX idx_ou_sync_id ON ldap_raw.organizational_units(sync_id);

-- Grant permissions on tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ldap_raw TO dbt_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ldap_raw TO dbt_user;
