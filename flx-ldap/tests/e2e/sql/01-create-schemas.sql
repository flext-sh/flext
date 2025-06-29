-- Create schemas for flx-ldap E2E testing

-- Raw data schema (as created by tap-ldap)
CREATE SCHEMA IF NOT EXISTS raw_ldap;

-- Staging schema (dbt staging models)
CREATE SCHEMA IF NOT EXISTS staging_ldap;

-- Analytics schema (dbt marts)
CREATE SCHEMA IF NOT EXISTS analytics_ldap;

-- Grant permissions
GRANT USAGE ON SCHEMA raw_ldap TO flx_user;
GRANT USAGE ON SCHEMA staging_ldap TO flx_user;
GRANT USAGE ON SCHEMA analytics_ldap TO flx_user;

GRANT CREATE ON SCHEMA raw_ldap TO flx_user;
GRANT CREATE ON SCHEMA staging_ldap TO flx_user;
GRANT CREATE ON SCHEMA analytics_ldap TO flx_user;

-- Future permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA raw_ldap GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO flx_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA staging_ldap GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO flx_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics_ldap GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO flx_user;
