#!/bin/bash
set -e

echo "Creating a new virtual environment..."
rm -rf .venv_new
/usr/bin/python3.10 -m venv .venv_new

echo "Activating virtual environment..."
source .venv_new/bin/activate

echo "Installing required packages..."
pip install -e dc-api-x

echo "Testing LDAP module..."
python -c "from dc_api_x.ext.auth.ldap import LdapAuthProvider; print('LDAP module loaded successfully')"

echo "Done. Use 'source .venv_new/bin/activate' to use this environment." 
