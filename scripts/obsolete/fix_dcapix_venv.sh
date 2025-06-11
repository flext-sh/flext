#!/bin/bash
# Fix for PYTHONPATH conflicts when running dcapix
# This script creates a wrapper that unsets PYTHONPATH before running dcapix

set -e

# Create a new virtual environment
echo "Creating new virtual environment with Python 3.10..."
/usr/bin/python3.10 -m venv .venv_dcapix_fixed --clear

# Activate the virtual environment
source .venv_dcapix_fixed/bin/activate

# Install needed dependencies
echo "Installing dependencies..."
pip install -U pip setuptools wheel
pip install ldap3==2.9.1
pip install pydantic==2.11.5 pydantic-core

# Install the flx_project in development mode
echo "Installing flx_project in development mode..."
pip install -e dc-api-x

# Create a wrapper script that unsets PYTHONPATH
echo "Creating wrapper script..."
cat > run_dcapix_fixed.sh << 'EOF'
#!/bin/bash
# Unset PYTHONPATH to avoid conflicts with system packages
unset PYTHONPATH
# Activate the virtual environment
source "$(dirname "$0")/.venv_dcapix_fixed/bin/activate"
# Run dcapix with all arguments passed to this script
dcapix "$@"
EOF

# Make the wrapper script executable
chmod +x run_dcapix_fixed.sh

echo "Installation complete."
echo "Use './run_dcapix_fixed.sh' to run dcapix without PYTHONPATH conflicts." 
