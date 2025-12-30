#!/bin/bash
# Runtime Detector - Detect execution environment (Claude Code vs Standalone)
#
# Detects whether code is running in Claude Code (with hooks) or standalone (cursor-agent).
# Provides runtime context for scripts to adapt their behavior.
#
# Usage:
#   source scripts/lib/runtime_detector.sh
#   RUNTIME=$(detect_runtime)
#   if [[ "$RUNTIME" == "claude-code" ]]; then
#       # Use hooks infrastructure
#   else
#       # Use fallback validation
#   fi
#
# Copyright (c) 2025 FLEXT Team. All rights reserved.
# SPDX-License-Identifier: MIT

set -euo pipefail

# Detect runtime environment
# Returns: "claude-code" or "standalone"
detect_runtime() {
    # Claude Code has hooks installed at ~/.claude/hooks/
    if [[ -f "${HOME}/.claude/hooks/pre_tool_use.py" ]]; then
        echo "claude-code"
        return 0
    fi

    # Fallback: standalone/cursor-agent
    echo "standalone"
    return 0
}

# Get hooks directory path
# Returns: Path to hooks directory or empty if not available
get_hooks_dir() {
    local hooks_dir="${HOME}/.claude/hooks"
    if [[ -d "$hooks_dir" ]]; then
        echo "$hooks_dir"
    else
        echo ""
    fi
}

# Check if hooks infrastructure is available
# Returns: 0 if available, 1 if not
hooks_available() {
    local hooks_dir
    hooks_dir=$(get_hooks_dir)
    [[ -n "$hooks_dir" ]] && [[ -f "${hooks_dir}/pre_tool_use.py" ]]
}

# Check if fix_engine is available in current environment
# Returns: 0 if available, 1 if not
fix_engine_available() {
    python3 -c "from flext_quality.fix_engine import FlextFixRunner" 2>/dev/null
}

# Get validation command based on runtime
# Args: tool_name (ruff|mypy|pytest)
# Returns: Command to run validation
get_validation_command() {
    local tool="$1"
    local runtime
    runtime=$(detect_runtime)

    case "$tool" in
        ruff)
            if [[ "$runtime" == "claude-code" ]]; then
                echo "make lint"
            else
                echo "python3 -m ruff check src/ tests/ scripts/"
            fi
            ;;
        mypy)
            if [[ "$runtime" == "claude-code" ]]; then
                echo "make type-check"
            else
                echo "python3 -m mypy --strict src/"
            fi
            ;;
        pytest)
            if [[ "$runtime" == "claude-code" ]]; then
                echo "make test"
            else
                echo "PYTHONPATH=src python3 -m pytest tests/"
            fi
            ;;
        *)
            echo "echo 'Unknown tool: $tool'" >&2
            return 1
            ;;
    esac
}

# Get backup strategy based on runtime
# Returns: "hooks" (use iterative_edit_tracker) or "standalone" (use tar.gz backups)
get_backup_strategy() {
    if hooks_available; then
        echo "hooks"
    else
        echo "standalone"
    fi
}

# Log runtime detection result
# Useful for debugging in automation scripts
log_runtime_detection() {
    local runtime
    runtime=$(detect_runtime)
    local hooks_status
    hooks_status=$(hooks_available && echo "available" || echo "unavailable")
    local fix_engine_status
    fix_engine_status=$(fix_engine_available && echo "available" || echo "unavailable")

    cat <<EOF
🔧 Runtime Detection:
  Runtime: $runtime
  Hooks: $hooks_status
  Fix Engine: $fix_engine_status
  Backup Strategy: $(get_backup_strategy)
EOF
}

# Export functions for use in other scripts
export -f detect_runtime
export -f get_hooks_dir
export -f hooks_available
export -f fix_engine_available
export -f get_validation_command
export -f get_backup_strategy
export -f log_runtime_detection

# If sourced directly (for testing), run detection
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    detect_runtime
fi
