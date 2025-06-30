#!/bin/bash

# Script to initialize missing git repositories for FLEXT modules

set -e

echo "= Checking for missing git repositories in FLEXT modules..."

# List of expected modules (directories that should have git repos)
MODULES=(
    "flext-api"
    "flext-auth"
    "flext-cli"
    "flext-core"
    "flext-db-oracle"
    "flext-dbt-ldap"
    "flext-grpc"
    "flext-ldap"
    "flext-meltano"
    "flext-observability"
    "flext-oracle-oic-ext"
    "flext-plugin"
    "flext-quality"
    "flext-tap-ldap"
    "flext-tap-oracle-oic"
    "flext-tap-oracle-wms"
    "flext-target-ldap"
    "flext-target-oracle-oic"
    "flext-target-oracle-wms"
    "flext-web"
    "client-a-oud-mig"
    "client-b-poc-oic-wms"
)

MISSING_REPOS=()
INITIALIZED_REPOS=()

# Check each module
for module in "${MODULES[@]}"; do
    if [ -d "$module" ]; then
        if [ ! -d "$module/.git" ]; then
            echo "L Missing git repo: $module"
            MISSING_REPOS+=("$module")
        else
            echo " Git repo exists: $module"
        fi
    else
        echo "   Directory not found: $module"
    fi
done

# Initialize missing repositories
if [ ${#MISSING_REPOS[@]} -eq 0 ]; then
    echo ""
    echo "<‰ All modules have git repositories initialized!"
else
    echo ""
    echo "=' Initializing missing git repositories..."
    
    for module in "${MISSING_REPOS[@]}"; do
        echo "  =Á Initializing git repo in: $module"
        cd "$module"
        
        # Initialize git repo
        git init
        
        # Add initial files
        git add .
        
        # Make initial commit
        git commit -m "feat: initial commit for $module

- Initialize git repository
- Add existing project files
- Setup module structure" || echo "       No files to commit"
        
        cd ..
        INITIALIZED_REPOS+=("$module")
        echo "     Initialized: $module"
    done
fi

echo ""
echo "=Ê Summary:"
echo "  Total modules checked: ${#MODULES[@]}"
echo "  Modules with existing repos: $((${#MODULES[@]} - ${#MISSING_REPOS[@]}))"
echo "  Repositories initialized: ${#INITIALIZED_REPOS[@]}"

if [ ${#INITIALIZED_REPOS[@]} -gt 0 ]; then
    echo ""
    echo "<• Newly initialized repositories:"
    for repo in "${INITIALIZED_REPOS[@]}"; do
        echo "    - $repo"
    done
fi

echo ""
echo " Git repository initialization complete!"