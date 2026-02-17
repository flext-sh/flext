#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# post_edit_validate.sh - Post-edit validation with backup maintenance for iterative fixes
# Usage: ./post_edit_validate.sh <backup_id> <file_path> [old_text] [new_text]
# Returns: JSON with validation result, maintains backup for iterative fixes

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="/tmp/flext_edit_backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

HOOKS_DIR="$HOME/.claude/hooks"
PROJECT_ROOT="/home/marlonsc/flext"

# Validate arguments
if [[ $# -lt 2 ]]; then
	echo "{\"error\": \"Usage: $0 <backup_id> <file_path> [old_text] [new_text]\"}" >&2
	exit 1
fi

BACKUP_ID="$1"
FILE_PATH="$2"
OLD_TEXT="${3:-edit}"
NEW_TEXT="${4:-edit}"

BACKUP_FILE="$BACKUP_DIR/pre_backup_${BACKUP_ID}.json"

# Restore from backup
restore_backup() {
	local backup_file="$1"

	if [[ ! -f $backup_file ]]; then
		echo "❌ Backup file not found: $backup_file" >&2
		return 1
	fi

	local file_path
	file_path=$(jq -r '.file_path' "$backup_file" 2>/dev/null || echo "")

	if [[ -z $file_path ]]; then
		echo "❌ Invalid backup file format" >&2
		return 1
	fi

	local original_content_base64
	original_content_base64=$(jq -r '.original_content_base64' "$backup_file" 2>/dev/null || echo "")

	if [[ -n $original_content_base64 ]]; then
		echo "$original_content_base64" | base64 -d >"$file_path"
	else
		echo "❌ No content found in backup" >&2
		return 1
	fi

	echo "✅ File restored from backup: $file_path" >&2

	# Clean up backup
	rm -f "$backup_file"
	return 0
}

# Validate after edit using comprehensive FLEXT quality checks
validate_post_edit() {
	local file_path="$1"

	echo "🔍 Running comprehensive FLEXT post-validation..."

	# Quality validation using FLEXT modules
	echo "  🛡️ Running code quality validation..."

	# Create a temporary validation script
	local validation_script="/tmp/validate_post_$$.py"
	cat >"$validation_script" <<'EOF'
import sys
import json
sys.path.insert(0, '/home/marlonsc/.claude/hooks/utils')
sys.path.insert(0, '/home/marlonsc/flext/src')

try:
    from validators import get_all_code_quality_violations

    # Read current file content
    temp_file = sys.argv[1]
    with open(temp_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Get all violations
    violations = get_all_code_quality_violations(content, temp_file)

    # Separate blocking vs warning violations
    blocking_violations = []
    warning_violations = []

    for v in violations:
        # Define blocking violation types (critical issues that require rollback)
        blocking_types = [
            'tier_violation', 'private_import', 'relative_private_import',
            'cross_project_import_rename', 'generic_namespace_reexposition',
            'TypeAlias_wrong_module', 'Protocol_wrong_module', 'StrEnum_wrong_module',
            'IntEnum_wrong_module', 'Final_wrong_module', 'loose_function',
            'root_alias', 'class_outside_facade', 'import_inside_function',
            'star_import', 'deep_relative_import', 'sys_path_manipulation',
            'lazy_import_function', 'lazy_import_getattr', 'blind_except',
            'swallowed_exception', 'ImportError_fallback', 'ModuleNotFoundError_fallback',
            'try_except_pass', 'mock_import', 'mock_import_alt', 'Mock_usage',
            'MagicMock_usage', 'monkeypatch_setattr', 'patch_decorator',
            'patch_context', 'empty_function_pass', 'empty_function_ellipsis',
            'empty_function_docstring_only', 'unused_parameter_underscore',
            'pylint_disable', 'ruff_noqa', 'pragma_no_cover', 'skip_without_reason',
            'skip_empty_reason', 'getattr_usage', 'class_getattr', 'model_rebuild',
            'model_construct', 'field_validator_no_mode', 'model_validator_no_mode'
        ]

        if v['name'] in blocking_types:
            blocking_violations.append(v)
        else:
            warning_violations.append(v)

    result = {
        'total_violations': len(violations),
        'blocking_violations': len(blocking_violations),
        'warning_violations': len(warning_violations),
        'blocking_details': [{'name': v['name'], 'message': v['message'], 'line': v['line']} for v in blocking_violations[:5]],
        'warning_details': [{'name': v['name'], 'message': v['message'], 'line': v['line']} for v in warning_violations[:10]]
    }

    # Print JSON to stdout
    sys.stdout.write(json.dumps(result))
    sys.stdout.flush()

except Exception as e:
    import traceback
    error_details = str(e) + '\n' + traceback.format_exc()
    error_result = {'validation': 'error', 'reason': error_details}
    sys.stdout.write(json.dumps(error_result))
    sys.stdout.flush()
EOF

	local quality_result
	quality_result=$(python3 "$validation_script" "$file_path" 2>&1)

	# Clean up validation script
	rm -f "$validation_script"

	# Extract JSON from quality result
	local json_result
	json_result=$(echo "$quality_result" | grep '^{' | tail -1)

	# Parse quality results
	local total_violations
	total_violations=$(echo "$json_result" | jq -r '.total_violations // 0' 2>/dev/null || echo "0")

	local blocking_violations
	blocking_violations=$(echo "$json_result" | jq -r '.blocking_violations // 0' 2>/dev/null || echo "0")

	echo "Found $total_violations total violations ($blocking_violations blocking)"

	if [[ $blocking_violations -gt 0 ]]; then
		echo "❌ BLOCKING violations found - fix ALL issues before proceeding"
		echo "$json_result"
		return 1
	elif [[ $total_violations -gt 0 ]]; then
		echo "⚠️ WARNINGS found - fix ALL warnings for quality compliance"
		echo "💡 Warnings must be resolved before confirmation"
		echo "$json_result"
		return 1
	else
		echo "✅ NO violations found - ready for confirmation"
		echo "$json_result"
		return 0
	fi
}

# Create temp file for agent to edit
create_temp_file() {
	local source_file="$1"
	local backup_id="$2"
	local temp_file="/tmp/flext_agent_edit_${backup_id}.py"

	# Copy current content to temp file
	if [[ -f $source_file ]]; then
		cp "$source_file" "$temp_file"
		echo "$temp_file"
	else
		echo "" >&2
		return 1
	fi
}

# Apply changes from temp file to original
apply_temp_changes() {
	local temp_file="$1"
	local original_file="$2"
	local backup_id="$3"

	if [[ -f $temp_file && -f $original_file ]]; then
		cp "$temp_file" "$original_file"
		rm -f "$temp_file"

		# Clean up backup
		local backup_file="$BACKUP_DIR/pre_backup_${backup_id}.json"
		rm -f "$backup_file"

		echo "✅ Changes applied successfully from $temp_file to $original_file"
		echo "🧹 Backup and temp files cleaned up"
		return 0
	else
		echo "❌ Error applying changes - files not found" >&2
		return 1
	fi
}

# Main execution
main() {
	echo "🚀 Starting post-edit validation for: $FILE_PATH"

	# Check if this is a temp file application request
	if [[ ${OLD_TEXT:-} == "apply_temp" ]]; then
		echo "📋 Applying changes from temp file..."
		if apply_temp_changes "$FILE_PATH" "$NEW_TEXT" "$BACKUP_ID"; then
			echo "🎉 File updated successfully!"
			exit 0
		else
			echo "❌ Failed to apply changes"
			exit 1
		fi
	fi

	# Validate the result
	local validation_result
	if ! validation_result=$(validate_post_edit "$FILE_PATH"); then
		echo "❌ Validation found issues - AGENT CAN FIX ITERATIVELY"
		echo ""

		# Create temp file for agent to edit
		local temp_file
		if temp_file=$(create_temp_file "$FILE_PATH" "$BACKUP_ID"); then
			echo "📝 TEMP FILE CREATED FOR AGENT EDITING:"
			echo "   📁 File to edit: $temp_file"
			echo "   🔄 After fixing, run:"
			echo "   ./scripts/post_edit_validate.sh $BACKUP_ID \"$temp_file\" apply_temp \"$FILE_PATH\""
			echo ""
			echo "   💡 Edit $temp_file directly, then run the command above to apply changes"
			echo ""
		else
			echo "❌ Failed to create temp file for editing"
		fi

		echo "🔄 Current validation result:"
		echo "$validation_result"
		exit 1
	else
		echo "✅ ZERO violations - CHANGES ACCEPTED AUTOMATICALLY!"
		echo ""

		# Clean up backup automatically since validation passed
		local backup_file="$BACKUP_DIR/pre_backup_${BACKUP_ID}.json"
		rm -f "$backup_file"

		echo "🧹 Backup cleaned up automatically"
		echo "🎉 Your corrections have been successfully applied."
		echo ""
		echo "🔄 Validation result:"
		echo "$validation_result"
		exit 0
	fi
}

main "$@"
