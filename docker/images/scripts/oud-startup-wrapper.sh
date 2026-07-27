#!/bin/bash
# OUD Startup wrapper - runs Oracle's startup script then applies configuration

set -e

echo "=== Starting OUD Instance ==="

# Run the Oracle startup script in background
/u01/oracle/container-scripts/createAndStartOUDInstance.sh &
OUD_STARTUP_PID=$!

# Wait for OUD to be fully started (check if port is responding)
echo "=== Waiting for OUD to be ready ==="
echo "Using baseDN: ${baseDN}, port: ${ldapPort}"
for _i in {1..60}; do
	if "${ORACLE_HOME}"/oud/bin/ldapsearch -h localhost -p "${ldapPort}" -b "" -s base "(objectClass=*)" >/dev/null 2>&1; then
		echo "OUD is ready!"
		break
	fi
	sleep 2
done

# Apply production configuration if script exists
if [ -f /docker-entrypoint-init.d/configure-oud.sh ]; then
	echo "=== Applying production OUD configuration ==="
	chmod +x /docker-entrypoint-init.d/configure-oud.sh
	/docker-entrypoint-init.d/configure-oud.sh
fi

# Wait for the OUD startup process
wait "${OUD_STARTUP_PID}"
