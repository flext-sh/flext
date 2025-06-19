#!/bin/bash
set -e

# Create a new virtual environment
echo "Creating new virtual environment with Python 3.10..."
/usr/bin/python3.10 -m venv .venv_fixed --clear

# Activate the virtual environment
source .venv_fixed/bin/activate

# Install needed dependencies
echo "Installing dependencies..."
pip install -U pip setuptools wheel
pip install ldap3==2.9.1
pip install pydantic==2.11.5 pydantic-core

# Install the flx_project in development mode
echo "Installing flx_project in development mode..."
pip install -e dc-api-x

# Verify the installation
echo "Verifying installation..."
cd dc-api-x
python -c "from dc_api_x.ext.auth.ldap import LdapAuthProvider; print('LDAP module loaded successfully')"

# Now run the script that was having issues
echo "Running the verification script..."
cd ..
python -c "from dc_api_x.ext.auth.ldap import LdapAuthProvider; print('LDAP module loaded successfully')"

echo "Installation complete. Use 'source .venv_fixed/bin/activate' to activate this environment."
