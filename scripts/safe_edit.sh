#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# safe_edit.sh - Ultra-simple safe edit wrapper for cursor-agent
# Usage: ./safe_edit.sh <file_path> <old_text> <new_text>
# Automatically handles: backup, validation, rollback on failure

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTO_EDIT_SCRIPT="$SCRIPT_DIR/auto_edit_with_hooks.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Validate arguments
if [[ $# -ne 3 ]]; then
	echo -e "${RED}Usage: $0 <file_path> <old_text> <new_text>${NC}" >&2
	exit 1
fi

FILE_PATH="$1"
OLD_TEXT="$2"
NEW_TEXT="$3"

# Execute automatic edit with full hook integration
if "$AUTO_EDIT_SCRIPT" "Edit" "$FILE_PATH" "$OLD_TEXT" "$NEW_TEXT"; then
	echo -e "${GREEN}✅ Edit completed successfully with quality assurance${NC}"
	exit 0
else
	echo -e "${RED}❌ Edit failed - automatic rollback performed${NC}" >&2
	exit 1
fi
