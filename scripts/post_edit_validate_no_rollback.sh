#!/bin/bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# post_edit_validate_no_rollback.sh - Post-edit validation WITHOUT automatic rollback
# Usage: ./post_edit_validate_no_rollback.sh <backup_id> <file_path> <old_text> <new_text>
# Returns: JSON with validation result, NO automatic rollback

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="/tmp/flext_edit_backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;34m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

HOOKS_DIR="$HOME/.claude/hooks"
PROJECT_ROOT="/home/marlonsc/flext"

# Validate arguments
if [[ $# -ne 4 ]]; then
	echo "{\"error\": \"Usage: $0 <backup_id> <file_path> <old_text> <new_text>\"}" >&2
	exit 1
fi

BACKUP_ID="$1"
FILE_PATH="$2"
OLD_TEXT="$3"
NEW_TEXT="$4"

BACKUP_FILE="$BACKUP_DIR/pre_backup_${BACKUP_ID}.json"

# Validate after edit using comprehensive FLEXT quality checks (NO ROLLBACK)
validate_post_edit() {
	local file_path="$1"

	echo "🔍 Running comprehensive FLEXT post-validation (NO AUTO-ROLLBACK)..."

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
        'warning_details': [{'name': v['name'], 'message': v['message'], 'line': v['line']} for v in warning_violations[:10]],
        'backup_id': sys.argv[2],
        'backup_file': sys.argv[3]
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
	quality_result=$(python3 "$validation_script" "$FILE_PATH" "$BACKUP_ID" "$BACKUP_FILE" 2>&1)

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
		echo "❌ BLOCKING violations found - NO AUTO-ROLLBACK (you can fix and revalidate)"
		echo "$json_result"
		return 1
	else
		echo "✅ No blocking violations - validation passed"
		if [[ $total_violations -gt 0 ]]; then
			echo "⚠️ Found $((total_violations - blocking_violations)) warnings"
		fi
		echo "$json_result"
		return 0
	fi
}

# Confirm and apply changes (only when user says it's good)
confirm_changes() {
	local backup_file="$1"

	if [[ ! -f $backup_file ]]; then
		echo "❌ Backup file not found: $backup_file" >&2
		return 1
	fi

	# Clean up backup (confirm changes are good)
	rm -f "$backup_file"
	echo "✅ Changes confirmed - backup cleaned up"
	return 0
}

# Main execution
main() {
	echo "🚀 Starting post-edit validation (NO AUTO-ROLLBACK) for: $FILE_PATH"

	# Validate the result (NO rollback)
	local validation_result
	if ! validation_result=$(validate_post_edit "$FILE_PATH"); then
		echo ""
		echo "💡 To fix violations and revalidate:"
		echo "   1. Make your corrections to $FILE_PATH"
		echo "   2. Run: ./scripts/post_edit_validate_no_rollback.sh $BACKUP_ID \"$FILE_PATH\" \"$OLD_TEXT\" \"$NEW_TEXT\""
		echo "   3. When ready to confirm: ./scripts/confirm_changes.sh $BACKUP_ID"
		echo ""
		echo "🔄 Current validation result:"
		echo "$validation_result"
		exit 1
	else
		echo ""
		echo "🎉 SUCCESS! No blocking violations found."
		echo "💡 To confirm and keep these changes, run:"
		echo "   ./scripts/confirm_changes.sh $BACKUP_ID"
		echo ""
		echo "🔄 Validation result:"
		echo "$validation_result"
		exit 0
	fi
}

main "$@"
