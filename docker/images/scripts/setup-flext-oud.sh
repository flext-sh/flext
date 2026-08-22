#!/bin/bash
# Setup script for FLEXT Oracle Unified Directory

set -e

INSTANCE_PATH="/opt/oracle/oud/instances/flext_oud"
OUD_SETUP="/u01/oracle/oud/oud-setup"
ADMIN_PWD="${ORACLE_PWD:-invalid_password}"
BASE_DN="${BASE_DN:-dc=network,dc=invaliddc}"

echo "=== FLEXT OUD Setup Starting ==="

# Check if OUD instance already exists
if [ ! -f "${INSTANCE_PATH}/OUD/settings/settings.ldif" ]; then
	echo "Setting up new OUD instance..."

	${OUD_SETUP} \
		--cli \
		--no-prompt \
		--doNotStart \
		--instancePath "${INSTANCE_PATH}" \
		--REDACTED_LDAP_BIND_PASSWORDConnectorPort 4444 \
		--ldapPort 1389 \
		--ldapsPort 1636 \
		--generateSelfSignedCertificate \
		--enableStartTLS \
		--rootUserDN "cn=Directory Manager" \
		--rootUserPassword "${ADMIN_PWD}" \
		--baseDN "${BASE_DN}" \
		--sampleData 0

	echo "OUD setup completed successfully"
else
	echo "OUD instance already configured - skipping setup"
fi

# Start OUD server
echo "Starting OUD server..."
"${INSTANCE_PATH}/OUD/bin/start-ds"

# Wait for server to start
echo "Waiting for OUD server to be ready..."
sleep 10

# Configure single structural objectclass behavior
echo "Settingsuring OUD settings..."
"${INSTANCE_PATH}/OUD/bin/dsconfig" \
	-h localhost -p 4444 \
	-D "cn=Directory Manager" \
	-w "${ADMIN_PWD}" \
	--no-prompt \
	--trustAll \
	set-global-configuration-prop \
	--set single-structural-objectclass-behavior:accept || echo "Configuration already set"

# Create base hierarchy
echo "Creating base LDAP hierarchy..."
ldapadd -x -H ldap://localhost:1389 \
	-D "cn=Directory Manager" \
	-w "${ADMIN_PWD}" <<EOF || echo "Hierarchy may already exist"
dn: cn=Users,${BASE_DN}
objectClass: container
objectClass: top
cn: Users

dn: cn=PERFIS,${BASE_DN}
objectClass: container
objectClass: top
cn: PERFIS

dn: ou=especial,cn=Users,${BASE_DN}
objectClass: organizationalUnit
objectClass: top
ou: especial
EOF

# Create test users
echo "Creating test users..."
ldapadd -x -H ldap://localhost:1389 \
	-D "cn=Directory Manager" \
	-w "${ADMIN_PWD}" <<EOF || echo "Test users may already exist"
dn: cn=ORCLADMIN,${BASE_DN}
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
cn: ORCLADMIN
sn: Administrator
uid: orclREDACTED_LDAP_BIND_PASSWORD
userPassword: invalid_password

dn: cn=FLEXTDEPLOY,ou=especial,cn=Users,${BASE_DN}
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
cn: FLEXTDEPLOY
sn: Deploy User
uid: flextdeploy
userPassword: invalid_app_pass
EOF

echo "=== FLEXT OUD Setup Complete ==="
echo "LDAP URL: ldap://localhost:1389"
echo "Base DN: ${BASE_DN}"
echo "Admin: cn=Directory Manager"

# Keep container running by tailing server logs
if [ -f "${INSTANCE_PATH}/OUD/logs/server.out" ]; then
	tail -f "${INSTANCE_PATH}/OUD/logs/server.out"
else
	echo "Keeping container alive..."
	tail -f /dev/null
fi
