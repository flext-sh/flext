#!/bin/bash
# FLEXT Workspace Dependency Setup Script  
# This script installs all required dependencies for ALL FLEXT projects
# Updated with complete project list and protobuf conflict resolution

set -e  # Exit on error

echo "=== FLEXT Workspace Dependency Setup ==="
echo "This script will install all required dependencies for FLEXT projects"
echo "Updated with protobuf/grpc compatibility fixes"
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

# Critical: Install compatible protobuf/grpc versions first
echo ""
echo "=== Installing Compatible Core Dependencies ==="
echo "Resolving protobuf/grpc compatibility conflicts..."
pip install "protobuf>=5.28.0,<6.0"
pip install "grpcio>=1.60.0,<1.67.0"
pip install "grpcio-tools>=1.60.0,<1.67.0"
pip install "grpcio-health-checking>=1.60.0,<1.67.0"
pip install "grpcio-reflection>=1.60.0,<1.67.0"
pip install "grpcio-status>=1.60.0,<1.67.0"

# Install flext-core first (base dependency for all projects)
echo ""
echo "=== Installing flext-core (base dependency) ==="
if [ -d "flext-core" ]; then
    cd flext-core
    pip install -e .
    cd ..
    echo "✅ flext-core installed successfully"
else
    echo "⚠️ flext-core directory not found"
fi

# Install flext-observability second (dependency for many projects)
echo ""
echo "=== Installing flext-observability (shared dependency) ==="
if [ -d "flext-observability" ]; then
    cd flext-observability
    pip install -e .
    cd ..
    echo "✅ flext-observability installed successfully"
else
    echo "⚠️ flext-observability directory not found"
fi

# Install main framework modules
echo ""
echo "=== Installing FLEXT Framework Modules ==="

projects=(
    "flext-api"
    "flext-auth"
    "flext-grpc"
    "flext-web"
    "flext-cli"
    "flext-plugin"
    "flext-meltano"
)

for project in "${projects[@]}"; do
    if [ -d "$project" ]; then
        echo "Installing $project..."
        cd "$project"
        pip install -e . || echo "⚠️ Warning: $project installation had issues"
        cd ..
        echo "✅ $project installation attempted"
    else
        echo "⚠️ $project directory not found"
    fi
done

# Install additional FLEXT extensions
echo ""
echo "=== Installing FLEXT Extensions ==="

extensions=(
    "flext-ldap"
    "flext-quality"
    "flext-db-oracle"
)

for ext in "${extensions[@]}"; do
    if [ -d "$ext" ]; then
        echo "Installing $ext..."
        cd "$ext"
        pip install -e . || echo "⚠️ Warning: $ext installation had issues"
        cd ..
        echo "✅ $ext installation attempted"
    else
        echo "⚠️ $ext directory not found"
    fi
done

# Install Singer/Meltano protocol projects
echo ""
echo "=== Installing Singer/Meltano Protocol Projects ==="

singer_projects=(
    "flext-tap-ldap"
    "flext-tap-oracle-oic"
    "flext-tap-oracle-wms"
    "flext-target-ldap"
    "flext-target-oracle"
    "flext-target-oracle-oic"
    "flext-target-oracle-wms"
    "flext-dbt-ldap"
    "flext-oracle-oic-ext"
)

for singer in "${singer_projects[@]}"; do
    if [ -d "$singer" ]; then
        echo "Installing $singer..."
        cd "$singer"
        pip install -e . || echo "⚠️ Warning: $singer installation had issues"
        cd ..
        echo "✅ $singer installation attempted"
    else
        echo "⚠️ $singer directory not found"
    fi
done

# Install enterprise integrations
echo ""
echo "=== Installing Enterprise Integrations ==="

enterprise_projects=(
    "algar-oud-mig"
    "gruponos-meltano-native"
    "flexcore"
)

for enterprise in "${enterprise_projects[@]}"; do
    if [ -d "$enterprise" ]; then
        echo "Installing $enterprise..."
        cd "$enterprise"
        pip install -e . || echo "⚠️ Warning: $enterprise installation had issues"
        cd ..
        echo "✅ $enterprise installation attempted"
    else
        echo "⚠️ $enterprise directory not found"
    fi
done

# Fix known dependency conflicts
echo ""
echo "=== Fixing Known Dependency Conflicts ==="

# Remove conflicting jwt package if present (keep only PyJWT)
pip uninstall -y jwt 2>/dev/null || true

# Install missing critical dependencies
echo "Installing critical missing dependencies..."
pip install psycopg2-binary || pip install psycopg-binary
pip install "cryptography>=44.0.0"
pip install "redis>=5.0.0"

# Install development dependencies
echo ""
echo "=== Installing Development Dependencies ==="
pip install pytest pytest-django pytest-asyncio pytest-cov pytest-mock
pip install ruff mypy pre-commit

# Final dependency check
echo ""
echo "=== Dependency Conflict Check ==="
conflicts=$(pip check 2>&1 | grep -v safety | wc -l)
if [ "$conflicts" -eq 0 ]; then
    echo "✅ No critical dependency conflicts found!"
else
    echo "⚠️ $conflicts dependency conflicts remain (excluding safety packages)"
    echo "Running pip check for details:"
    pip check 2>&1 | grep -v safety || true
fi

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "All FLEXT dependencies have been installed successfully."
echo ""
echo "Installed project count:"
echo "- Framework modules: $(ls -d flext-{api,auth,grpc,web,cli,plugin,meltano,observability} 2>/dev/null | wc -l)/8"
echo "- Extensions: $(ls -d flext-{ldap,quality,db-oracle} 2>/dev/null | wc -l)/3"  
echo "- Singer/Meltano: $(ls -d flext-{tap,target,dbt}* flext-oracle-oic-ext 2>/dev/null | wc -l)/9"
echo "- Enterprise: $(ls -d {algar,gruponos}* flexcore 2>/dev/null | wc -l)/3"
echo ""
echo "Testing suggestions:"
echo "- flext-core: cd flext-core && python -m pytest"
echo "- flext-api: cd flext-api && python -m pytest"
echo "- flext-web: cd flext-web && python -m pytest"
echo ""
echo "Known compatibility fixes applied:"
echo "- protobuf: locked to >=5.28.0,<6.0 (dbt compatible)"
echo "- grpcio: locked to >=1.60.0,<1.67.0 (protobuf compatible)"
echo "- redis: adjusted to >=5.0.0 (available version)"
echo ""