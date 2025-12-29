#!/bin/bash
# pre_edit_validate.sh - Pre-edit backup and warnings only
# Usage: ./pre_edit_validate.sh <file_path>
# Returns: JSON with backup_id and warnings (no blocking)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="/tmp/flext_edit_backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create backup directory
mkdir -p "$BACKUP_DIR"

HOOKS_DIR="$HOME/.claude/hooks"
PROJECT_ROOT="/home/marlonsc/flext"

# Validate arguments
if [[ $# -ne 1 ]]; then
    echo "{\"error\": \"Usage: $0 <file_path>\"}" >&2
    exit 1
fi

FILE_PATH="$1"

# Generate unique backup ID
BACKUP_ID=$(date +%s)_$$_$RANDOM
BACKUP_FILE="$BACKUP_DIR/pre_backup_${BACKUP_ID}.json"

# Create automatic backup of current file state
create_backup() {
    local file_path="$1"
    local backup_id="$2"

    if [[ -f "$file_path" ]]; then
        # Create backup with base64 encoded content to avoid JSON issues
        local content_base64
        content_base64=$(base64 -w 0 "$file_path")

        local backup_data=$(cat <<EOF
{
  "backup_id": "$backup_id",
  "timestamp": "$(date -Iseconds)",
  "file_path": "$file_path",
  "original_content_base64": "$content_base64",
  "file_permissions": "$(stat -c '%a' "$file_path" 2>/dev/null || echo '644')",
  "file_owner": "$(stat -c '%U:%G' "$file_path" 2>/dev/null || echo 'user:user')"
}
EOF
)
        echo "$backup_data" > "$BACKUP_FILE"
        echo "✅ Backup created: $BACKUP_FILE"
    else
        echo "⚠️ File not found for backup: $file_path"
    fi
}

# Show warnings only (no blocking)
show_warnings() {
    local file_path="$1"

    echo "🔍 Running FLEXT pre-validation (warnings only)..."

    # Create temporary file with current content for validation
    local temp_file="$PROJECT_ROOT/.tmp_validation_$$.py"
    if [[ -f "$file_path" ]]; then
        cp "$file_path" "$temp_file"
    else
        # For new files, create empty Python file
        echo '"""Temporary validation file."""' > "$temp_file"
    fi

    # Extract validation path (simulate project context for FLEXT rules)
    local validation_path="src/flext_test/validation_temp.py"
    if [[ "$file_path" == *"/flext-api/"* ]]; then
        validation_path="src/flext_api/$(basename "$file_path")"
    elif [[ "$file_path" == *"/flext-core/"* ]]; then
        validation_path="src/flext_core/$(basename "$file_path")"
    fi

    # Run validation script
    local validation_result
    validation_result=$(python3 -c "
import sys
import os
import json
sys.path.insert(0, '$HOOKS_DIR/utils')
sys.path.insert(0, '$PROJECT_ROOT/src')

try:
    from validators import get_all_code_quality_violations

    # Read content
    with open('$temp_file', 'r', encoding='utf-8') as f:
        content = f.read()

    violations = get_all_code_quality_violations(content, '$validation_path')

    # All violations are warnings in pre-edit (no blocking)
    warnings = violations

    result = {
        'total_warnings': len(warnings),
        'warnings': warnings[:5]  # Show first 5 warnings
    }

    print(json.dumps(result))

except Exception as e:
    print(json.dumps({'error': str(e), 'total_warnings': 0}))
")

    # Clean up temp file
    rm -f "$temp_file"

    echo "$validation_result"
}

# Main execution
main() {
    echo "🚀 Starting pre-edit validation for: $FILE_PATH"

    # Create backup
    create_backup "$FILE_PATH" "$BACKUP_ID"

    # Show warnings only
    warnings_output=$(show_warnings "$FILE_PATH")

    # Parse warnings (extract JSON from output)
    json_output=$(echo "$warnings_output" | grep '^{' | head -1)
    total_warnings=$(echo "$json_output" | jq -r '.total_warnings // 0' 2>/dev/null || echo "0")

    if [[ "$total_warnings" -gt 0 ]]; then
        echo "⚠️ Found $total_warnings pre-edit warnings - FIX ALL before editing:"
        echo "$json_output" | jq -r '.warnings[]?.message' 2>/dev/null || echo "Could not parse warnings"
        echo ""
        echo "💡 IMPORTANT: Fix all pre-edit warnings BEFORE making changes!"
        echo "   This ensures you start with clean code."
    else
        echo "✅ No pre-edit warnings found."
    fi

    # Always allow edit - return backup info
    result=$(cat <<EOF
{
  "backup_created": true,
  "backup_id": "$BACKUP_ID",
  "backup_file": "$BACKUP_FILE",
  "pre_warnings": $total_warnings,
  "status": "ready_for_edit"
}
EOF
)

    echo "$result"
}

main "$@"