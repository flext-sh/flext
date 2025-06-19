#!/bin/bash
set -e

# Use Python 3.10 to create an isolated environment
echo "Creating an isolated virtual environment with Python 3.10..."
rm -rf .venv_final
/usr/bin/python3.10 -m venv .venv_final --clear

# Activate and configure the environment
echo "Activating virtual environment..."
source .venv_final/bin/activate
unset PYTHONPATH
export PYTHONNOUSERSITE=1

# Verify the Python version
python --version

# Install packages in the correct order with Python 3.10
echo "Installing required packages..."
pip install --upgrade pip setuptools wheel
pip install pydantic-core==2.14.1
pip install pydantic==2.5.0
pip install ldap3==2.9.1

# Test with a simple import first
echo "Testing simple import of LdapAuthProvider..."
cd dc-api-x
pip install -e .
python -c "from dc_api_x.ext.auth.ldap import LdapAuthProvider; print('LDAP module imported successfully')"

# Now test with a more comprehensive test
echo "Testing with a comprehensive test..."
python -c "from dc_api_x.ext.auth.ldap import LdapAuthProvider; auth_provider = LdapAuthProvider('cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com', 'password', 'ldap.example.com'); print('LDAP provider instance created successfully')"

echo "Fix complete. Use the following command to activate this environment:"
echo "source .venv_final/bin/activate && export PYTHONNOUSERSITE=1"
