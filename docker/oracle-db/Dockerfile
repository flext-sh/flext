# Oracle Database Test Container for FLEXT
# Extends gvenzl/oracle-xe:21-slim with FLEXT initialization

FROM gvenzl/oracle-xe:21-slim

# Copy FLEXT initialization script
COPY init.sql /container-entrypoint-initdb.d/

# Default environment variables are set in docker-compose.yml
# ORACLE_PASSWORD: flext_oracle_test
# APP_USER: flext_test
# APP_USER_PASSWORD: flext_test_password