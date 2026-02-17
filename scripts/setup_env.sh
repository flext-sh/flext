#!/bin/bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# =============================================================================
# FLEXT Environment Setup Script
# =============================================================================
# Automatically configures PYTHONPATH for cross-project dependencies
# Usage: source scripts/setup_env.sh
# =============================================================================

set -e

# Determine workspace root
if [ -n "$FLEXT_ROOT" ]; then
	WORKSPACE_ROOT="$FLEXT_ROOT"
elif [ -d ".git" ] && [ -f "base.mk" ]; then
	WORKSPACE_ROOT="$(pwd)"
else
	WORKSPACE_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || dirname "$(dirname "$(realpath "$0")")")"
fi

export FLEXT_ROOT="$WORKSPACE_ROOT"

# Load .env file from workspace root if exists
if [ -f "$WORKSPACE_ROOT/.env" ]; then
	set -a
	# shellcheck disable=SC1091
	source "$WORKSPACE_ROOT/.env"
	set +a
fi

# Core projects that are commonly dependencies (in dependency order)
CORE_PROJECTS=(
	"flext-core"
	"flext-cli"
	"flext-ldif"
	"flext-ldap"
	"flext-api"
	"flext-auth"
	"flext-grpc"
	"flext-observability"
	"flext-db-oracle"
	"flext-meltano"
	"flext-plugin"
	"flext-web"
	"client-a-oud-mig"
)

# Build PYTHONPATH with all project src directories
build_pythonpath() {
	local paths=""

	# Add current project's src first (if exists)
	if [ -d "src" ]; then
		paths="$(pwd)/src"
	fi

	# Add core projects in dependency order
	for project in "${CORE_PROJECTS[@]}"; do
		local project_src="$WORKSPACE_ROOT/$project/src"
		if [ -d "$project_src" ]; then
			if [ -n "$paths" ]; then
				paths="$paths:$project_src"
			else
				paths="$project_src"
			fi
		fi
	done

	# Append existing PYTHONPATH if not already included
	if [ -n "$PYTHONPATH" ]; then
		# Remove duplicates
		IFS=':' read -ra EXISTING <<<"$PYTHONPATH"
		for existing_path in "${EXISTING[@]}"; do
			if [[ ! $paths =~ $existing_path ]]; then
				paths="$paths:$existing_path"
			fi
		done
	fi

	echo "$paths"
}

# Set PYTHONPATH
export PYTHONPATH="$(build_pythonpath)"

# Activate virtual environment if exists and not already activated
if [ -z "$VIRTUAL_ENV" ]; then
	if [ -f "$WORKSPACE_ROOT/.venv/bin/activate" ]; then
		# shellcheck disable=SC1091
		source "$WORKSPACE_ROOT/.venv/bin/activate"
	elif [ -f ".venv/bin/activate" ]; then
		# shellcheck disable=SC1091
		source ".venv/bin/activate"
	fi
fi

# Export common environment variables
export POETRY_VIRTUALENVS_IN_PROJECT=true
export POETRY_VIRTUALENVS_CREATE=false

# Function to get PYTHONPATH for a specific project
get_project_pythonpath() {
	local project_name="$1"
	local project_path="$WORKSPACE_ROOT/$project_name"

	if [ -d "$project_path/src" ]; then
		echo "$project_path/src:$PYTHONPATH"
	else
		echo "$PYTHONPATH"
	fi
}

# Export function for subshells
export -f get_project_pythonpath

# Print status if not in quiet mode
if [ "${FLEXT_QUIET:-0}" != "1" ]; then
	echo "FLEXT environment configured:"
	echo "  FLEXT_ROOT: $FLEXT_ROOT"
	echo "  PYTHONPATH: $(echo "$PYTHONPATH" | tr ':' '\n' | head -5 | tr '\n' ':')..."
	echo "  VIRTUAL_ENV: ${VIRTUAL_ENV:-not set}"
fi
