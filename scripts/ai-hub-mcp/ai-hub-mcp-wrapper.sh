#!/bin/sh
# ai-hub MCP wrapper that activates direnv before running ai-hub mcp client
# This ensures the MCP runs with the correct project environment

# Get the directory where this script is located
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
# Get the project root (parent of scripts directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT" || exit 1

# Source direnv to load the project environment
# direnv exports the environment variables including PATH, VENV_DIR, etc.
eval "$(direnv export bash)" || exit 1

# Find ai-hub in the PATH (which direnv should have set up)
# First try from mise shims, then from PATH
AI_HUB_BIN="${MISE_DATA_DIR:-${XDG_DATA_HOME:-${HOME}/.local/share}/mise}/shims/ai-hub"
if [ ! -x "$AI_HUB_BIN" ]; then
    AI_HUB_BIN="$(command -v ai-hub)"
fi

if [ -z "$AI_HUB_BIN" ] || [ ! -x "$AI_HUB_BIN" ]; then
    echo "ERROR: ai-hub not found in PATH or mise shims" >&2
    exit 1
fi

# Now run the ai-hub mcp client with the project environment active
exec "$AI_HUB_BIN" mcp --action client --agent kilo "$@"