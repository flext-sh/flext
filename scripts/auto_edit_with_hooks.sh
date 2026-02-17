#!/bin/bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# auto_edit_with_hooks.sh - Fully automatic edit execution with transparent hook validation and rollback
# Usage: ./auto_edit_with_hooks.sh <tool_name> <file_path> <old_string> <new_string>

set -euo pipefail

# Configuration
HOOKS_DIR="$HOME/.claude/hooks"
PROJECT_ROOT="/home/marlonsc/flext"
BACKUP_DIR="/tmp/flext_edit_backups"
ROLLBACK_SCRIPT="$HOOKS_DIR/lib/batch_bridge.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[AUTO-EDIT]${NC} $1" >&2; }
log_success() { echo -e "${GREEN}[AUTO-EDIT]${NC} $1" >&2; }
log_warning() { echo -e "${YELLOW}[AUTO-EDIT]${NC} $1" >&2; }
log_error() { echo -e "${RED}[AUTO-EDIT]${NC} $1" >&2; }

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Parse arguments
TOOL_NAME="$1"
FILE_PATH="$2"
OLD_STRING="$3"
NEW_STRING="$4"

# Generate unique backup ID
BACKUP_ID=$(date +%s)_$$_$RANDOM
BACKUP_FILE="$BACKUP_DIR/edit_backup_${BACKUP_ID}.json"

log_info "Starting fully automatic edit with hooks..."
log_info "File: $FILE_PATH"
log_info "Backup ID: $BACKUP_ID"

# Step 1: Create automatic backup of current file state
create_backup() {
	local file_path="$1"
	local backup_id="$2"

	if [[ -f $file_path ]]; then
		local backup_data=$(
			cat <<EOF
{
  "backup_id": "$backup_id",
  "timestamp": "$(date -Iseconds)",
  "file_path": "$file_path",
  "original_content": $(jq -R <<<"$(cat "$file_path")"),
  "file_permissions": "$(stat -c '%a' "$file_path" 2>/dev/null || echo '644')",
  "file_owner": "$(stat -c '%U:%G' "$file_path" 2>/dev/null || echo 'user:user')"
}
EOF
		)
		echo "$backup_data" >"$BACKUP_FILE"
		log_success "Backup created: $BACKUP_FILE"
	else
		log_warning "File does not exist, no backup needed"
	fi
}

# Step 2: Restore from backup
restore_backup() {
	local backup_file="$1"

	if [[ ! -f $backup_file ]]; then
		log_error "Backup file not found: $backup_file"
		return 1
	fi

	local file_path=$(jq -r '.file_path' "$backup_file")
	local original_content=$(jq -r '.original_content' "$backup_file")

	echo "$original_content" >"$file_path"
	log_success "Restored from backup: $file_path"

	# Cleanup backup
	rm -f "$backup_file"
}

# Step 3: Execute pre-edit validation
run_pre_validation() {
	local tool_name="$1"
	local file_path="$2"
	local old_string="$3"
	local new_string="$4"

	# For pre-validation, we need to simulate the file content after the change
	# Create a temporary file with the new content to validate
	local temp_file="/tmp/pre_validation_$$.py"

	if [[ -f $file_path ]]; then
		cp "$file_path" "$temp_file"
		# Apply the change to temp file for validation
		python3 -c "
import sys
import re

temp_file = sys.argv[1]
old_string = sys.argv[2]
new_string = sys.argv[3]

with open(temp_file, 'r', encoding='utf-8') as f:
    content = f.read()

old_escaped = re.escape(old_string)
new_content = re.sub(old_escaped, new_string, content, flags=re.MULTILINE | re.DOTALL)

with open(temp_file, 'w', encoding='utf-8') as f:
    f.write(new_content)
" "$temp_file" "$old_string" "$new_string" 2>/dev/null
	else
		# File doesn't exist, validate the new content directly
		echo "$new_string" >"$temp_file"
	fi

	local hook_data=$(
		cat <<EOF
{
  "tool_name": "$tool_name",
  "tool_input": {
    "file_path": "$temp_file",
    "old_string": $(jq -R <<<"$old_string"),
    "new_string": $(jq -R <<<"$new_string")
  },
  "cwd": "$PROJECT_ROOT"
}
EOF
	)

	log_info "Running pre-edit validation on temp file: $temp_file..."
	echo "Hook data: $hook_data" >&2
	local result
	result=$(echo "$hook_data" | python3 "$HOOKS_DIR/pre_tool_use.py" 2>&1)
	echo "Hook result: $result" >&2

	# Clean up temp file
	rm -f "$temp_file"

	if echo "$result" | grep -q '"decision": "block"'; then
		log_error "PRE-VALIDATION BLOCKED"
		echo "$result" | jq -r '.reason' >&2
		return 1
	fi

	log_success "Pre-validation passed"
	return 0
}

# Step 4: Execute post-edit validation
run_post_validation() {
	local tool_name="$1"
	local file_path="$2"
	local old_string="$3"
	local new_string="$4"

	local hook_data=$(
		cat <<EOF
{
  "tool_name": "$tool_name",
  "tool_input": {
    "file_path": "$file_path",
    "old_string": $(jq -R <<<"$old_string"),
    "new_string": $(jq -R <<<"$new_string")
  },
  "cwd": "$PROJECT_ROOT"
}
EOF
	)

	log_info "Running post-edit validation..."
	local result
	result=$(echo "$hook_data" | python3 "$HOOKS_DIR/post_tool_use.py" 2>&1)

	if echo "$result" | grep -q '"decision": "block"'; then
		log_error "POST-VALIDATION BLOCKED - Initiating automatic rollback"
		echo "$result" | jq -r '.reason' >&2
		return 1
	fi

	log_success "Post-validation passed"
	return 0
}

# Step 5: Execute the actual edit operation
execute_edit() {
	local tool_name="$1"
	local file_path="$2"
	local old_string="$3"
	local new_string="$4"

	log_info "Executing edit operation..."

	# Handle file creation (empty old_string means create new file)
	if [[ -z $old_string ]]; then
		# Create new file
		echo "$new_string" >"$file_path"
		log_success "File created: $file_path"
		return 0
	fi

	# Handle file modification
	if [[ -f $file_path ]]; then
		# Use Python for safe string replacement (handles special characters better)
		python3 -c "
import sys
import re

file_path = sys.argv[1]
old_string = sys.argv[2]
new_string = sys.argv[3]

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Escape special regex characters in old_string for replacement
old_escaped = re.escape(old_string)

# Perform replacement
new_content = re.sub(old_escaped, new_string, content, flags=re.MULTILINE | re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Edit applied successfully')
" "$file_path" "$old_string" "$new_string" 2>/dev/null

		if [[ $? -eq 0 ]]; then
			log_success "Edit applied to: $file_path"
		else
			log_error "Failed to apply edit to: $file_path"
			return 1
		fi
	else
		log_error "File does not exist and old_string is not empty: $file_path"
		return 1
	fi
}

# Main execution flow
main() {
	# Validate arguments
	if [[ $# -lt 4 ]]; then
		log_error "Usage: $0 <tool_name> <file_path> <old_string> <new_string>"
		exit 1
	fi

	local tool_name="$1"
	local file_path="$2"
	local old_string="$3"
	local new_string="$4"

	# Step 1: Automatic backup
	create_backup "$file_path" "$BACKUP_ID"

	# Step 2: Pre-edit validation
	if ! run_pre_validation "$tool_name" "$file_path" "$old_string" "$new_string"; then
		log_error "Pre-validation failed - aborting edit"
		exit 1
	fi

	# Step 3: Execute the edit
	if ! execute_edit "$tool_name" "$file_path" "$old_string" "$new_string"; then
		log_error "Edit execution failed - restoring backup"
		restore_backup "$BACKUP_FILE"
		exit 1
	fi

	# Step 4: Post-edit validation
	if ! run_post_validation "$tool_name" "$file_path" "$old_string" "$new_string"; then
		log_error "Post-validation failed - automatic rollback initiated"
		restore_backup "$BACKUP_FILE"
		log_info "Rollback completed. Edit was reverted."
		exit 1
	fi

	# Success - cleanup backup
	rm -f "$BACKUP_FILE"
	log_success "Edit completed successfully with full quality validation!"
	log_info "Backup cleaned up: $BACKUP_ID"
}

# Execute main function
main "$@"
