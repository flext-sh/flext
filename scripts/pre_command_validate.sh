#!/bin/bash
# pre_command_validate.sh - Pre-command validation using Claude Code hooks
# Usage: ./pre_command_validate.sh <command>
# Returns: JSON with validation result and safety guidance

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_DIR="$HOME/.claude/hooks"
PROJECT_ROOT="/home/marlonsc/flext"

# Validate arguments
if [[ $# -ne 1 ]]; then
    echo "{\"error\": \"Usage: $0 <command>\"}" >&2
    exit 1
fi

COMMAND="$1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Validate command using Claude Code hooks
validate_command() {
    local command="$1"

    # Prepare hook data
    local hook_data=$(cat <<EOF
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "$command"
  },
  "cwd": "$PROJECT_ROOT"
}
EOF
)

    # Save hook data to temp file
    local hook_input_file="/tmp/hook_command_$$.json"
    echo "$hook_data" > "$hook_input_file"

    echo "🔍 Validating command safety..." >&2

    # Run pre_tool_use.py hook (contains dangerous command detection)
    local hook_result
    hook_result=$(python3 "$HOOKS_DIR/pre_tool_use.py" < "$hook_input_file" 2>&1 || echo "exit_code:$?")

    # Clean up
    rm -f "$hook_input_file"

    # Analyze hook result
    if echo "$hook_result" | grep -q '"decision": "block"\|exit_code:2'; then
        # Command is blocked - extract reason
        local reason
        reason=$(echo "$hook_result" | jq -r '.reason' 2>/dev/null || echo "$hook_result")

        # Categorize the risk level
        local risk_level="high"
        if echo "$reason" | grep -qi "dangerous\|block"; then
            risk_level="critical"
        elif echo "$reason" | grep -qi "caution\|warning"; then
            risk_level="medium"
        fi

        echo "{\"validation\": \"blocked\", \"reason\": \"$reason\", \"risk_level\": \"$risk_level\", \"command\": \"$command\"}"

    elif echo "$hook_result" | grep -q "exit_code:0"; then
        # Command is allowed
        echo "{\"validation\": \"allowed\", \"command\": \"$command\", \"safety_notes\": \"Command passed basic safety checks\"}"

    else
        # Unknown result - allow but with caution
        echo "{\"validation\": \"allowed\", \"command\": \"$command\", \"safety_notes\": \"Command validation inconclusive - use caution\", \"warning\": \"Unable to fully validate command safety\"}"
    fi
}

# Provide safety guidance based on command analysis
provide_safety_guidance() {
    local command="$1"
    local validation="$2"

    echo "🛡️ Command Safety Analysis:" >&2

    # Analyze command for common risky patterns
    if echo "$command" | grep -q "rm.*-rf\|rm.*\*\|\*\.bak\|\.git"; then
        echo "⚠️  DELETION RISK: Command involves file deletion" >&2
    fi

    if echo "$command" | grep -q "chmod.*777\|chown.*-R"; then
        echo "⚠️  PERMISSION RISK: Command modifies permissions" >&2
    fi

    if echo "$command" | grep -q "dd\|mkfs\|fdisk\|parted"; then
        echo "🚨 DISK RISK: Command can destroy disk data" >&2
    fi

    if echo "$command" | grep -q "curl.*\|\||wget.*\|\|"; then
        echo "⚠️  EXECUTION RISK: Command downloads and executes code" >&2
    fi

    if echo "$command" | grep -q "sudo\|su"; then
        echo "⚠️  PRIVILEGE RISK: Command requires elevated privileges" >&2
    fi

    if echo "$command" | grep -q "git.*--force\|git.*-f"; then
        echo "⚠️  HISTORY RISK: Command can overwrite git history" >&2
    fi

    if [[ "$validation" == "blocked" ]]; then
        echo "" >&2
        echo "❌ RECOMMENDATION: Do not execute this command" >&2
        echo "💡 Consider safer alternatives or manual execution with caution" >&2
    else
        echo "" >&2
        echo "✅ RECOMMENDATION: Command appears safe to execute" >&2
        echo "💡 Monitor output and stop if unexpected behavior occurs" >&2
    fi
}

# Main execution
main() {
    # Validate the command
    local validation_result
    validation_result=$(validate_command "$COMMAND")

    local validation_status
    validation_status=$(echo "$validation_result" | jq -r '.validation // "unknown"' 2>/dev/null)

    # Provide safety guidance
    provide_safety_guidance "$COMMAND" "$validation_status"

    # Return structured result
    echo "$validation_result"
}

# Execute main and capture output
RESULT=$(main)
echo "$RESULT"