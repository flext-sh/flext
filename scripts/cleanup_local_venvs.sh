#!/bin/bash
# =============================================================================
# FLEXT - Cleanup Local Virtual Environments
# =============================================================================
# This script removes all local .venv directories from subprojects,
# keeping only the workspace .venv at /home/marlonsc/flext/.venv
# =============================================================================

set -e

WORKSPACE_ROOT="${FLEXT_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"

echo "=== FLEXT Local .venv Cleanup ==="
echo "Workspace: $WORKSPACE_ROOT"
echo ""

# Find all .venv directories except the workspace one
LOCAL_VENVS=$(find "$WORKSPACE_ROOT" -maxdepth 2 -type d -name ".venv" ! -path "$WORKSPACE_ROOT/.venv" 2>/dev/null || true)

if [ -z "$LOCAL_VENVS" ]; then
    echo "No local .venv directories found. Already clean!"
    exit 0
fi

echo "Found local .venv directories to remove:"
echo "$LOCAL_VENVS" | while read -r venv; do
    echo "  - $venv"
done
echo ""

# Confirm before deletion
read -p "Remove all these directories? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "$LOCAL_VENVS" | while read -r venv; do
        if [ -d "$venv" ]; then
            echo "Removing $venv..."
            rm -rf "$venv"
        fi
    done
    echo ""
    echo "Done! All local .venv directories removed."
    echo ""
    echo "Next steps:"
    echo "  1. Run 'source scripts/setup_env.sh' to configure environment"
    echo "  2. Run 'make check' in any project to verify"
else
    echo "Aborted."
fi
