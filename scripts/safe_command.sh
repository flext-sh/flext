#!/bin/bash
# safe_command.sh - Safe command execution with pre-validation
# Usage: ./safe_command.sh <command>
# Automatically validates command safety before execution

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRE_VALIDATE_SCRIPT="$SCRIPT_DIR/pre_command_validate.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Validate arguments
if [[ $# -lt 1 ]]; then
    echo -e "${RED}Usage: $0 <command>${NC}" >&2
    echo -e "${BLUE}Example: $0 'ls -la'${NC}" >&2
    exit 1
fi

COMMAND="$*"

echo -e "${BLUE}🔒 Safe Command Execution${NC}"
echo -e "${BLUE}Command: ${YELLOW}$COMMAND${NC}"
echo

# Pre-validate the command
echo -e "${BLUE}Step 1: Pre-validation${NC}"
VALIDATION_RESULT=$("$PRE_VALIDATE_SCRIPT" "$COMMAND")

VALIDATION=$(echo "$VALIDATION_RESULT" | jq -r '.validation // "unknown"' 2>/dev/null)
RISK_LEVEL=$(echo "$VALIDATION_RESULT" | jq -r '.risk_level // "unknown"' 2>/dev/null)

if [[ "$VALIDATION" == "blocked" ]]; then
    echo -e "${RED}❌ COMMAND BLOCKED${NC}"
    echo -e "${RED}Risk Level: ${YELLOW}$RISK_LEVEL${NC}"
    echo -e "${RED}Reason: $(echo "$VALIDATION_RESULT" | jq -r '.reason' 2>/dev/null)${NC}"
    echo
    echo -e "${YELLOW}💡 Alternatives:${NC}"
    echo -e "  • Execute manually with caution"
    echo -e "  • Use safer commands"
    echo -e "  • Check command documentation"
    echo
    exit 1
fi

echo -e "${GREEN}✅ Pre-validation passed${NC}"
echo

# Execute the command safely
echo -e "${BLUE}Step 2: Safe Execution${NC}"
echo -e "${YELLOW}Executing: $COMMAND${NC}"
echo -e "${BLUE}Output:${NC}"
echo

# Execute command and capture exit code
set +e  # Temporarily disable exit on error to capture command result
eval "$COMMAND"
EXIT_CODE=$?
set -e  # Re-enable exit on error

echo
echo -e "${BLUE}Step 3: Execution Summary${NC}"

if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}✅ Command executed successfully (exit code: $EXIT_CODE)${NC}"
else
    echo -e "${RED}❌ Command failed (exit code: $EXIT_CODE)${NC}"
fi

echo -e "${BLUE}Command completed with safety validation${NC}"