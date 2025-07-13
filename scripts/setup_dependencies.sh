#!/bin/bash
# FLEXT Workspace Dependency Setup Script
# This script installs all required dependencies for FLEXT projects

set -e  # Exit on error

echo "=== FLEXT Workspace Dependency Setup ==="
echo "This script will install all required dependencies for FLEXT projects"
echo ""

# Check if we're in the correct directory
if [ ! -f ".venv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found at .venv/"
    echo "Please run this script from the FLEXT workspace root"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install flext-core first (base dependency for all projects)
echo ""
echo "=== Installing flext-core (base dependency) ==="
cd flext-core
pip install -e .
cd ..

# Install main framework modules
echo ""
echo "=== Installing FLEXT Framework Modules ==="

echo "Installing flext-api..."
cd flext-api
pip install -e .
cd ..

echo "Installing flext-auth..."
cd flext-auth
pip install -e .
cd ..

echo "Installing flext-grpc..."
cd flext-grpc
pip install -e .
cd ..

echo "Installing flext-web..."
cd flext-web
pip install -e .
cd ..

echo "Installing flext-cli..."
cd flext-cli
pip install -e .
cd ..

echo "Installing flext-plugin..."
cd flext-plugin
pip install -e .
cd ..

echo "Installing flext-observability..."
cd flext-observability
pip install -e .
cd ..

echo "Installing flext-meltano..."
cd flext-meltano
pip install -e .
cd ..

# Install additional FLEXT extensions
echo ""
echo "=== Installing FLEXT Extensions ==="

echo "Installing flext-ldap..."
cd flext-ldap
pip install -e .
cd ..

echo "Installing flext-quality..."
cd flext-quality
pip install -e .
cd ..

echo "Installing flext-db-oracle..."
cd flext-db-oracle
pip install -e .
cd ..

# Fix known dependency conflicts
echo ""
echo "=== Fixing Known Dependency Conflicts ==="

# Remove conflicting jwt package if present (keep only PyJWT)
pip uninstall -y jwt 2>/dev/null || true

# Ensure correct Django version for flext-web
pip install "Django>=5.2,<6.0"

# Install development dependencies
echo ""
echo "=== Installing Development Dependencies ==="
pip install pytest pytest-django pytest-asyncio pytest-cov

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "All FLEXT dependencies have been installed successfully."
echo "You can now run tests with: python -m pytest"
echo ""
echo "Known working configurations:"
echo "- flext-api: All 12 tests passing"
echo "- flext-web: Django models tests passing"
echo "- flext-grpc: Tests require protobuf compilation"
echo ""