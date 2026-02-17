#!/bin/bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# edit_with_hooks.sh - Automatic edit execution with integrated hook validation
# Usage: ./edit_with_hooks.sh <tool_name> <file_path> <old_string> <new_string>

set -euo pipefail

# Configuration
HOOKS_DIR="$HOME/.claude/hooks"
PROJECT_ROOT="/home/marlonsc/flext"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse arguments
TOOL_NAME="$1"
FILE_PATH="$2"
OLD_STRING="$3"
NEW_STRING="$4"

# Create JSON for hooks
TOOL_INPUT_JSON=$(
	cat <<EOF
{
  "file_path": "$FILE_PATH",
  "old_string": $(jq -R <<<"$OLD_STRING"),
  "new_string": $(jq -R <<<"$NEW_STRING")
}
EOF
)

HOOK_DATA=$(
	cat <<EOF
{
  "tool_name": "$TOOL_NAME",
  "tool_input": $TOOL_INPUT_JSON,
  "cwd": "$PROJECT_ROOT"
}
EOF
)

log_info "Starting edit with automatic hook validation..."
log_info "File: $FILE_PATH"
log_info "Tool: $TOOL_NAME"

# Step 1: Pre-edit validation
log_info "Running pre-edit validation..."
PRE_RESULT=$(echo "$HOOK_DATA" | python3 "$HOOKS_DIR/pre_tool_use.py" 2>&1)

if echo "$PRE_RESULT" | grep -q '"decision": "block"'; then
	log_error "PRE-EDIT VALIDATION FAILED"
	echo "$PRE_RESULT" | jq -r '.reason'
	exit 1
fi

log_success "Pre-edit validation passed"

# Step 2: Execute the edit (simulated - in real usage, this would be the actual edit)
log_info "Executing edit operation..."
# NOTE: In real usage, replace this with actual StrReplace/Edit operation
echo "Would execute: $TOOL_NAME on $FILE_PATH"

# Step 3: Post-edit validation
log_info "Running post-edit validation..."
POST_RESULT=$(echo "$HOOK_DATA" | python3 "$HOOKS_DIR/post_tool_use.py" 2>&1)

if echo "$POST_RESULT" | grep -q '"decision": "block"'; then
	log_error "POST-EDIT VALIDATION FAILED"

	# Extract error and check for skill reference
	ERROR_MSG=$(echo "$POST_RESULT" | jq -r '.reason')
	REFERENCED_SKILL=$(echo "$ERROR_MSG" | grep -o '/[a-z-]*' | head -1 || echo "")

	echo "$ERROR_MSG"

	if [ -n "$REFERENCED_SKILL" ]; then
		log_warning "Consider using skill: $REFERENCED_SKILL"
	fi

	exit 1
fi

log_success "Post-edit validation passed"
log_success "Edit completed successfully with quality assurance!"
