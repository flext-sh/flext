#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# =============================================================================
# FLEXT Environment Setup Script
# =============================================================================
# Sets FLEXT_ROOT and activates workspace .venv (editable installs replace PYTHONPATH).
# Usage: source scripts/setup_env.sh
# =============================================================================

set -euo pipefail

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

# Print status if not in quiet mode
if [ "${FLEXT_QUIET:-0}" != "1" ]; then
	echo "FLEXT environment configured:"
	echo "  FLEXT_ROOT: $FLEXT_ROOT"
	echo "  VIRTUAL_ENV: ${VIRTUAL_ENV:-not set}"
fi
