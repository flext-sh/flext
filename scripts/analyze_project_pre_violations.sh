#!/bin/bash
# analyze_project_pre_violations.sh - Analyze all pre-edit violations in any FLEXT project
# Usage: ./analyze_project_pre_violations.sh <project_name> [src_dir]
# Examples:
#   ./analyze_project_pre_violations.sh flext-api
#   ./analyze_project_pre_violations.sh flext-core src
#   ./analyze_project_pre_violations.sh flext-auth

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Validate arguments
if [[ $# -lt 1 ]]; then
	echo "❌ Usage: $0 <project_name> [src_dir]"
	echo "   project_name: Name of FLEXT project (e.g., flext-api, flext-core)"
	echo "   src_dir: Source directory within project (default: src)"
	echo ""
	echo "Examples:"
	echo "  $0 flext-api"
	echo "  $0 flext-core src"
	echo "  $0 flext-auth"
	exit 1
fi

PROJECT_NAME="$1"
SRC_DIR="${2:-src}"
PROJECT_DIR="$PROJECT_ROOT/$PROJECT_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Analyzing all pre-edit violations in $PROJECT_NAME project..."
echo "📁 Project directory: $PROJECT_DIR"
echo "📂 Source directory: $SRC_DIR"
echo ""

# Validate project exists
if [[ ! -d $PROJECT_DIR ]]; then
	echo "❌ Project directory not found: $PROJECT_DIR"
	exit 1
fi

# Get all Python files in project/src
PYTHON_FILES=$(find "$PROJECT_DIR/$SRC_DIR" -name "*.py" -type f 2>/dev/null | sort || true)

TOTAL_FILES=$(echo "$PYTHON_FILES" | wc -l)
echo "📊 Found $TOTAL_FILES Python files to analyze"
echo ""

# Results tracking
VIOLATION_FILES=()
TOTAL_VIOLATIONS=0

# Analyze each file
for file in $PYTHON_FILES; do
	echo -n "🔍 Analyzing: $(basename "$file") ... "

	# Run pre-edit validation
	result=$("$SCRIPT_DIR/pre_edit_validate.sh" "$file" 2>/dev/null)

	# Extract warnings count
	warnings=$(echo "$result" | jq -r '.pre_warnings // 0' 2>/dev/null || echo "0")

	if [[ $warnings -gt 0 ]]; then
		echo -e "${RED}❌ $warnings violations${NC}"
		VIOLATION_FILES+=("$file")
		TOTAL_VIOLATIONS=$((TOTAL_VIOLATIONS + warnings))

		# Show violation details
		echo "$result" | jq -r '.warnings[]?.message' 2>/dev/null | sed 's/^/    /' || true
		echo ""
	else
		echo -e "${GREEN}✅ Clean${NC}"
	fi
done

echo ""
echo "📈 SUMMARY:"
echo "   Total files analyzed: $TOTAL_FILES"
echo "   Files with violations: ${#VIOLATION_FILES[@]}"
echo "   Total violations: $TOTAL_VIOLATIONS"

if [[ ${#VIOLATION_FILES[@]} -gt 0 ]]; then
	echo ""
	echo -e "${YELLOW}⚠️ Files with violations:${NC}"
	for file in "${VIOLATION_FILES[@]}"; do
		echo "   - $file"
	done
	echo ""
	echo -e "${BLUE}💡 Next steps:${NC}"
	echo "   1. Run auto-fix script for each file"
	echo "   2. Validate fixes with post_edit_validate.sh"
	echo "   3. Confirm fixes are working"
else
	echo ""
	echo -e "${GREEN}✅ All files are clean! No violations found.${NC}"
fi
