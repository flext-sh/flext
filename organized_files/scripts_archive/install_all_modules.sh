#!/bin/bash

# Script to install all flext modules using poetry
set -e

# Get the current directory (workspace root)
WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lista dos módulos em ordem de dependência
modules=(
	"flext-core"
	"flext-auth"
	"flext-api"
	"flext-grpc"
	"flext-ldap"
	"flext-db-oracle"
	"flext-meltano"
	"flext-observability"
	"flext-cli"
	"flext-plugin"
	"flext-web"
	"flext-quality"
	"flext-dbt-ldap"
	"flext-tap-ldap"
	"flext-tap-oracle-oic"
	"flext-tap-oracle-wms"
	"flext-target-ldap"
	"flext-target-oracle-oic"
	"flext-target-oracle-wms"
	"flext-oracle-oic-ext"
)

echo "Starting installation of all flext modules..."

for module in "${modules[@]}"; do
	echo "Installing $module..."

	# Check if module directory exists
	if [ ! -d "$WORKSPACE_ROOT/$module" ]; then
		echo "⚠️  Module directory not found: $module"
		continue
	fi

	cd "$WORKSPACE_ROOT/$module"

	# Check if pyproject.toml exists
	if [ ! -f "pyproject.toml" ]; then
		echo "⚠️  No pyproject.toml found in $module, skipping..."
		continue
	fi

	# Skip poetry lock if poetry.lock already exists
	if [ ! -f "poetry.lock" ]; then
		echo "Creating poetry.lock for $module..."
		poetry lock --no-update || {
			echo "❌ Failed to create poetry.lock for $module"
			continue
		}
	fi

	# Install the module in development mode
	poetry install --only main || {
		echo "❌ Failed to install $module"
		continue
	}

	echo "✅ $module installed successfully"
	echo "---"
done

echo "All modules installed successfully!"
