#!/bin/bash
# Configure OUD for testing with production-like settings
# Based on ansible roles/oracle_oud_14/tasks/schema_configuration.yml

set -e

OUD_INSTANCE_PATH="/u01/oracle/user_projects/${OUD_INSTANCE_NAME}/OUD"
ADMIN_PASSWORD="${rootUserPassword:-TestPassword123}"
ADMIN_DN="${rootUserDN:-cn=Directory Manager}"

echo "=== Waiting for OUD to be fully started ==="
sleep 10

# Wait for OUD to be ready
for _ in {1..30}; do
	if ldapsearch -x -H ldap://localhost:1389 -b "" -s base "(objectClass=*)" >/dev/null 2>&1; then
		echo "OUD is ready"
		break
	fi
	sleep 2
done

echo "=== Applying Production OUD Configuration ==="

# Create password file for dsconfig
echo "${ADMIN_PASSWORD}" >/tmp/oud_REDACTED_LDAP_BIND_PASSWORD_pwd.txt

# 1. Set single-structural-objectclass-behavior to accept
echo "1/4 - Settingsuring single-structural-objectclass-behavior..."
"${OUD_INSTANCE_PATH}"/bin/dsconfig set-global-configuration-prop \
	--set single-structural-objectclass-behavior:accept \
	-h localhost -p 4444 \
	-D "${ADMIN_DN}" \
	-j /tmp/oud_REDACTED_LDAP_BIND_PASSWORD_pwd.txt \
	--no-prompt --trustAll || echo "Already configured"

# 2. Disable compact encoding for userRoot workflow
echo "2/4 - Disabling compact encoding for userRoot workflow..."
"${OUD_INSTANCE_PATH}"/bin/dsconfig set-workflow-element-prop \
	--element-name "userRoot" \
	--set compact-encoding:false \
	-h localhost -p 4444 \
	-D "${ADMIN_DN}" \
	-j /tmp/oud_REDACTED_LDAP_BIND_PASSWORD_pwd.txt \
	--no-prompt --trustAll || echo "Already configured"

# 3. Disable schema checking for migration compatibility
echo "3/4 - Disabling schema checking..."
"${OUD_INSTANCE_PATH}"/bin/dsconfig set-global-configuration-prop \
	--set check-schema:false \
	-h localhost -p 4444 \
	-D "${ADMIN_DN}" \
	-j /tmp/oud_REDACTED_LDAP_BIND_PASSWORD_pwd.txt \
	--no-prompt --trustAll || echo "Already configured"

# 4. Allow unauthenticated requests
echo "4/4 - Allowing unauthenticated requests..."
"${OUD_INSTANCE_PATH}"/bin/dsconfig set-global-configuration-prop \
	--set reject-unauthenticated-requests:false \
	-h localhost -p 4444 \
	-D "${ADMIN_DN}" \
	-j /tmp/oud_REDACTED_LDAP_BIND_PASSWORD_pwd.txt \
	--no-prompt --trustAll || echo "Already configured"

# Clean up password file
rm -f /tmp/oud_REDACTED_LDAP_BIND_PASSWORD_pwd.txt

echo "=== OUD Configuration Complete ==="
echo "Applied 4 production dsconfig settings:"
echo "  1. single-structural-objectclass-behavior: accept"
echo "  2. compact-encoding: false (userRoot workflow)"
echo "  3. check-schema: false"
echo "  4. reject-unauthenticated-requests: false"
