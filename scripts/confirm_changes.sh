#!/bin/bash
# confirm_changes.sh - Confirm changes and clean up backup
# Usage: ./confirm_changes.sh <backup_id>

set -euo pipefail

BACKUP_DIR="/tmp/flext_edit_backups"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Validate arguments
if [[ $# -ne 1 ]]; then
	echo "Usage: $0 <backup_id>" >&2
	echo "Example: $0 1767030791_2943218_10775" >&2
	exit 1
fi

BACKUP_ID="$1"
BACKUP_FILE="$BACKUP_DIR/pre_backup_${BACKUP_ID}.json"

echo "🔄 Confirming changes for backup: $BACKUP_ID"

if [[ ! -f $BACKUP_FILE ]]; then
	echo "❌ Backup file not found: $BACKUP_FILE" >&2
	echo "💡 This backup may have already been confirmed or cleaned up." >&2
	exit 1
fi

# Get file path from backup for confirmation
FILE_PATH=$(jq -r '.file_path' "$BACKUP_FILE" 2>/dev/null || echo "")

if [[ -z $FILE_PATH ]]; then
	echo "❌ Could not determine file path from backup" >&2
	exit 1
fi

echo "📁 File: $FILE_PATH"

# Clean up backup (confirm changes are good)
rm -f "$BACKUP_FILE"

echo "✅ Changes confirmed and backup cleaned up!"
echo "🎉 Your corrections have been successfully applied."
