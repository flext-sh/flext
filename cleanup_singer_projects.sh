#!/bin/bash

# Singer/Meltano projects cleanup script
# This script will clean junk files and cache directories from all Singer/Meltano projects

set -e

# List of projects to clean
PROJECTS=(
    "flext-tap-ldap"
    "flext-tap-oracle-oic"
    "flext-tap-oracle-wms"
    "flext-target-ldap"
    "flext-target-oracle"
    "flext-target-oracle-oic"
    "flext-target-oracle-wms"
    "flext-oracle-oic-ext"
)

# Base directory
BASE_DIR="/home/marlonsc/flext"

# Function to clean a single project
clean_project() {
    local project=$1
    local project_path="$BASE_DIR/$project"
    
    echo "========================================="
    echo "Cleaning project: $project"
    echo "========================================="
    
    if [ ! -d "$project_path" ]; then
        echo "WARNING: Project directory not found: $project_path"
        return
    fi
    
    cd "$project_path"
    
    # Remove junk files
    echo "Removing junk files..."
    find . -name "requirements.txt" -type f -delete 2>/dev/null || true
    find . -name "*_REPORT*.md" -type f -delete 2>/dev/null || true
    find . -name "fix_*.py" -type f -delete 2>/dev/null || true
    find . -name "*_MIGRATION*.md" -type f -delete 2>/dev/null || true
    find . -name ".dev_deps_backup_*" -type f -delete 2>/dev/null || true
    
    # Remove cache directories
    echo "Removing cache directories..."
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".ruff_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    rm -rf reports build dist 2>/dev/null || true
    
    # Check if .gitignore exists, create Singer-specific one if missing
    if [ ! -f ".gitignore" ]; then
        echo "Creating Singer/ETL specific .gitignore..."
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv/

# Testing
.tox/
.coverage
.coverage.*
.cache
.pytest_cache/
htmlcov/
reports/

# Type checking
.mypy_cache/
.dmypy.json
dmypy.json
.pyre/
.pytype/

# Linting
.ruff_cache/

# Singer/Meltano specific
state.json
catalog.json
.meltano/
output/
*.singer.properties
tap-config.json
target-config.json

# Environment
.env
.env.*

# IDE
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
.dev_deps_backup_*
EOF
    fi
    
    # Show git status
    echo -e "\nGit status for $project:"
    git status --short || echo "Not a git repository"
    
    echo -e "\nCompleted cleanup for $project\n"
}

# Main execution
echo "Starting Singer/Meltano projects cleanup..."
echo "Base directory: $BASE_DIR"
echo

# Clean each project
for project in "${PROJECTS[@]}"; do
    clean_project "$project"
done

echo "========================================="
echo "Cleanup completed for all projects!"
echo "========================================="