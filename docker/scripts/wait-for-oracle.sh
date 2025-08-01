#!/bin/bash
# Wait for Oracle Database to be ready - Health Check Script
# Simple health check script for Oracle database readiness

set -e

# Configuration
ORACLE_HOST="${ORACLE_HOST:-oracle-db}"
ORACLE_PORT="${ORACLE_PORT:-1521}"
ORACLE_SERVICE_NAME="${ORACLE_SERVICE_NAME:-FLEXT_PDB}"
ORACLE_USERNAME="${ORACLE_USERNAME:-FLEXT_USER}"
ORACLE_PASSWORD="${ORACLE_PASSWORD:-FlextTest123!}"

# Maximum wait time (seconds)
MAX_WAIT="${MAX_WAIT:-300}"
INTERVAL="${INTERVAL:-5}"

echo "Waiting for Oracle Database at ${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME}..."

waited=0
while [ $waited -lt "$MAX_WAIT" ]; do
	# Test TCP connection first
	if timeout 5 bash -c "</dev/tcp/${ORACLE_HOST}/${ORACLE_PORT}" >/dev/null 2>&1; then
		echo "Oracle port is accessible, testing SQL connection..."

		# Test SQL connection with sqlplus if available
		if command -v sqlplus >/dev/null 2>&1; then
			if echo "SELECT 1 FROM DUAL;" | timeout 10 sqlplus -s "${ORACLE_USERNAME}/${ORACLE_PASSWORD}@${ORACLE_HOST}:${ORACLE_PORT}/${ORACLE_SERVICE_NAME}" >/dev/null 2>&1; then
				echo "Oracle Database is ready!"
				exit 0
			fi
		else
			# Test with Python oracledb if sqlplus not available
			if python3 -c "
import oracledb
try:
    conn = oracledb.connect(
        user='${ORACLE_USERNAME}',
        password='${ORACLE_PASSWORD}',
        host='${ORACLE_HOST}',
        port=${ORACLE_PORT},
        service_name='${ORACLE_SERVICE_NAME}'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM DUAL')
    cursor.close()
    conn.close()
    print('Oracle connection successful')
except Exception as e:
    exit(1)
" >/dev/null 2>&1; then
				echo "Oracle Database is ready!"
				exit 0
			fi
		fi
	fi

	echo "Oracle not ready, waiting ${INTERVAL} seconds... (${waited}/${MAX_WAIT})"
	sleep "$INTERVAL"
	waited=$((waited + INTERVAL))
done

echo "Timeout waiting for Oracle Database after ${MAX_WAIT} seconds"
exit 1
