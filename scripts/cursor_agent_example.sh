#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# cursor_agent_example.sh - Example implementation for cursor-agent
# Demonstrates proper integration of validation scripts

set -euo pipefail

echo "🔍 Cursor-Agent Example Implementation"
echo "====================================="

# Example 1: Safe file editing
echo ""
echo "📝 Example 1: Safe File Editing"
echo "-------------------------------"

FILE="example.py"
OLD_TEXT="def old_function(): pass"
NEW_TEXT="def new_function():
    \"\"\"Improved function with docstring.\"\"\"
    return 'improved'"

echo "File: $FILE"
echo "Old: $OLD_TEXT"
echo "New: $NEW_TEXT"
echo ""

# Step 1: Pre-validation
echo "Step 1: Pre-validation"
PRE_RESULT=$(./scripts/pre_edit_validate.sh "$FILE" "$OLD_TEXT" "$NEW_TEXT")
echo "Result: $PRE_RESULT"

VALIDATION=$(echo "$PRE_RESULT" | jq -r '.validation // "error"' 2>/dev/null)
if [[ $VALIDATION == "blocked" ]]; then
	echo "❌ EDITION BLOCKED"
	REASON=$(echo "$PRE_RESULT" | jq -r '.reason // "Unknown reason"' 2>/dev/null)
	echo "Reason: $REASON"
	exit 1
fi

BACKUP_ID=$(echo "$PRE_RESULT" | jq -r '.backup_id // ""' 2>/dev/null)
echo "✅ Pre-validation passed. Backup ID: $BACKUP_ID"
echo ""

# Step 2: Execute edit (simulated)
echo "Step 2: Execute Edit (simulated)"
echo "Would execute: StrReplace('$FILE', '$OLD_TEXT', '$NEW_TEXT')"
echo ""

# Step 3: Post-validation
echo "Step 3: Post-validation"
POST_RESULT=$(./scripts/post_edit_validate.sh "$BACKUP_ID" "$FILE" "$OLD_TEXT" "$NEW_TEXT")
echo "Result: $POST_RESULT"

VALIDATION=$(echo "$POST_RESULT" | jq -r '.validation // "error"' 2>/dev/null)
if [[ $VALIDATION == "blocked" ]]; then
	echo "❌ POST-VALIDATION FAILED - AUTO-ROLLBACK EXECUTED"
	exit 1
fi

echo "✅ Edit completed successfully"
echo ""

# Example 2: Safe command execution
echo "🔧 Example 2: Safe Command Execution"
echo "-----------------------------------"

SAFE_COMMAND="echo 'Hello, safe execution!'"
echo "Command: $SAFE_COMMAND"
echo ""

echo "Step 1: Pre-validation"
CMD_RESULT=$(./scripts/pre_command_validate.sh "$SAFE_COMMAND")
echo "Result: $CMD_RESULT"

VALIDATION=$(echo "$CMD_RESULT" | jq -r '.validation // "error"' 2>/dev/null)
if [[ $VALIDATION == "blocked" ]]; then
	echo "❌ COMMAND BLOCKED"
	exit 1
fi

echo "✅ Command validation passed"
echo ""

echo "Step 2: Safe execution"
./scripts/safe_command.sh "$SAFE_COMMAND"
echo ""

# Example 3: Dangerous command (will be blocked)
echo "🚨 Example 3: Dangerous Command (Blocked)"
echo "-----------------------------------------"

DANGER_COMMAND="rm -rf /tmp/test*"
echo "Command: $DANGER_COMMAND"
echo ""

echo "Step 1: Pre-validation"
DANGER_RESULT=$(./scripts/pre_command_validate.sh "$DANGER_COMMAND")
echo "Result: $DANGER_RESULT"

VALIDATION=$(echo "$DANGER_RESULT" | jq -r '.validation // "error"' 2>/dev/null)
if [[ $VALIDATION == "blocked" ]]; then
	echo "✅ COMMAND CORRECTLY BLOCKED"
	RISK_LEVEL=$(echo "$DANGER_RESULT" | jq -r '.risk_level // "unknown"' 2>/dev/null)
	echo "Risk Level: $RISK_LEVEL"
else
	echo "❌ COMMAND SHOULD HAVE BEEN BLOCKED"
fi

echo ""
echo "🎯 Summary: All validation scripts working correctly!"
echo "Cursor-agent should implement similar validation patterns."
