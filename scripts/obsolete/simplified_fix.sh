#!/bin/bash
set -e

# Create a clean virtual environment
echo "Creating a completely clean virtual environment..."
rm -rf .venv_fix
/usr/bin/python3.10 -m venv .venv_fix --clear --system-site-packages

# Activate virtual environment and install packages
echo "Activating and configuring environment..."
source .venv_fix/bin/activate
export PYTHONNOUSERSITE=1 # Don't use user site packages

# Install the required packages
echo "Installing packages..."
pip install -U pip
pip install ldap3==2.9.1
pip install pydantic==2.11.5 pydantic-core

# Install our flx_project in development mode
echo "Installing flx_project in development mode..."
pip install -e dc-api-x

# Test the import
echo "Testing module import..."
cd dc-api-x
python -c "from dc_api_x.ext.auth.ldap import LdapAuthProvider; print('LDAP module loaded successfully')"

echo "Fix complete. Use 'source .venv_fix/bin/activate && export PYTHONNOUSERSITE=1' to use this environment."
