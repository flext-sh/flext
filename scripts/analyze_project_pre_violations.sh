#!/bin/bash
# analyze_project_pre_violations.sh - Analyze all pre-edit violations in any FLEXT project
# Usage: ./analyze_project_pre_violations.sh <project_name> [directories...]
# Examples:
#   ./analyze_project_pre_violations.sh flext-api                    # Default: src, tests, scripts, examples
#   ./analyze_project_pre_violations.sh flext-core src tests         # Custom directories
#   ./analyze_project_pre_violations.sh flext-auth src               # Only src directory

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Validate arguments
if [[ $# -lt 1 ]]; then
    echo "❌ Usage: $0 <project_name> [directories...]"
    echo "   project_name: Name of FLEXT project (e.g., flext-api, flext-core)"
    echo "   directories: Source directories within project (default: src tests scripts examples)"
    echo ""
    echo "Examples:"
    echo "  $0 flext-api                    # Analyze src, tests, scripts, examples"
    echo "  $0 flext-core src tests         # Analyze only src and tests"
    echo "  $0 flext-auth src               # Analyze only src"
    echo ""
    echo "Output: violations_analysis_<project_name>.json"
    exit 1
fi

PROJECT_NAME="$1"
shift
PROJECT_DIR="$PROJECT_ROOT/$PROJECT_NAME"

# Default directories if none specified
if [[ $# -eq 0 ]]; then
    DIRECTORIES=("src" "tests" "scripts" "examples")
else
    DIRECTORIES=("$@")
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Output JSON file
OUTPUT_JSON="violations_analysis_${PROJECT_NAME}.json"

echo "🔍 Analyzing all pre-edit violations in $PROJECT_NAME project..."
echo "📁 Project directory: $PROJECT_DIR"
echo "📂 Analyzing directories: ${DIRECTORIES[*]}"
echo "📄 Output file: $OUTPUT_JSON"
echo ""

# Validate project exists
if [[ ! -d "$PROJECT_DIR" ]]; then
    echo "❌ Project directory not found: $PROJECT_DIR"
    exit 1
fi

# Results tracking
VIOLATION_FILES=()
TOTAL_FILES=0
TOTAL_VIOLATIONS=0
DIRECTORY_STATS=()
ALL_VIOLATIONS_DETAILS=()

# Function to analyze a directory
analyze_directory() {
    local dir_name="$1"
    local dir_path="$PROJECT_DIR/$dir_name"

    echo "📂 Analyzing directory: $dir_name"

    # Get all Python files in directory
    local python_files=$(find "$dir_path" -name "*.py" -type f 2>/dev/null | sort || true)

    if [[ -z "$python_files" ]]; then
        echo "   ℹ️  No Python files found in $dir_name"
        return
    fi

    local dir_total_files=$(echo "$python_files" | wc -l)
    local dir_violation_files=()
    local dir_total_violations=0
    local dir_violations_details=()

    echo "   📊 Found $dir_total_files Python files"

    # Analyze each file
    for file in $python_files; do
        echo -n "   🔍 $(basename "$file") ... "

        # Run pre-edit validation
        local result=$("$SCRIPT_DIR/pre_edit_validate.sh" "$file" 2>/dev/null)

        # Extract warnings count and details
        local warnings=$(echo "$result" | jq -r '.pre_warnings // 0' 2>/dev/null || echo "0")
        local warnings_details=$(echo "$result" | jq -r '.warnings // []' 2>/dev/null || echo "[]")

        if [[ "$warnings" -gt 0 ]]; then
            echo -e "${RED}❌ $warnings violations${NC}"
            VIOLATION_FILES+=("$file")
            dir_violation_files+=("$file")
            dir_total_violations=$((dir_total_violations + warnings))

            # Store violation details
            local file_details=$(cat <<EOF
{
  "file": "$file",
  "directory": "$dir_name",
  "violations_count": $warnings,
  "violations": $warnings_details
}
EOF
)
            dir_violations_details+=("$file_details")
        else
            echo -e "${GREEN}✅ Clean${NC}"
        fi
    done

    # Update global counters
    TOTAL_FILES=$((TOTAL_FILES + dir_total_files))
    TOTAL_VIOLATIONS=$((TOTAL_VIOLATIONS + dir_total_violations))

    # Store directory stats
    DIRECTORY_STATS+=("{\"directory\": \"$dir_name\", \"files\": $dir_total_files, \"violations\": $dir_total_violations}")

    # Add to all violations details
    for detail in "${dir_violations_details[@]}"; do
        ALL_VIOLATIONS_DETAILS+=("$detail")
    done

    echo "   📈 $dir_name: $dir_total_files files, $dir_total_violations violations"
    echo ""
}

# Analyze each specified directory
for dir in "${DIRECTORIES[@]}"; do
    if [[ -d "$PROJECT_DIR/$dir" ]]; then
        analyze_directory "$dir"
    else
        echo "⚠️  Directory $dir not found in $PROJECT_DIR, skipping..."
    fi
done

# Generate JSON output
generate_json_output() {
    local timestamp=$(date -Iseconds)
    local directories_json=$(printf '%s\n' "${DIRECTORY_STATS[@]}" | jq -s '.' 2>/dev/null || echo "[]")
    local violations_json=$(printf '%s\n' "${ALL_VIOLATIONS_DETAILS[@]}" | jq -s '.' 2>/dev/null || echo "[]")

    cat > "$OUTPUT_JSON" <<EOF
{
  "analysis_timestamp": "$timestamp",
  "project_name": "$PROJECT_NAME",
  "project_directory": "$PROJECT_DIR",
  "analyzed_directories": $(printf '%s\n' "${DIRECTORIES[@]}" | jq -R . | jq -s .),
  "summary": {
    "total_files_analyzed": $TOTAL_FILES,
    "files_with_violations": ${#VIOLATION_FILES[@]},
    "total_violations": $TOTAL_VIOLATIONS,
    "clean_files": $(($TOTAL_FILES - ${#VIOLATION_FILES[@]}))
  },
  "directory_breakdown": $directories_json,
  "violations_details": $violations_json,
  "recommendations": {
    "auto_fix_available": true,
    "manual_fix_required": $([[ $TOTAL_VIOLATIONS -gt 0 ]] && echo "true" || echo "false"),
    "next_steps": [
      "Run auto-fix: ./scripts/architecture/fix_violations.sh $PROJECT_DIR",
      "Re-analyze: $0 $PROJECT_NAME",
      "Individual fixes: ./scripts/pre_edit_validate.sh <file_path>"
    ]
  }
}
EOF
}

# Generate JSON output
generate_json_output

echo ""
echo "📈 SUMMARY:"
echo "   Total files analyzed: $TOTAL_FILES"
echo "   Files with violations: ${#VIOLATION_FILES[@]}"
echo "   Total violations: $TOTAL_VIOLATIONS"
echo "   Clean files: $(($TOTAL_FILES - ${#VIOLATION_FILES[@]}))"
echo ""
echo "📄 Detailed results saved to: $OUTPUT_JSON"

if [[ ${#VIOLATION_FILES[@]} -gt 0 ]]; then
    echo ""
    echo -e "${YELLOW}⚠️ CRITICAL: Violations found that must be fixed before any code changes!${NC}"
    echo ""
    echo -e "${RED}🚨 BLOCKING ISSUES:${NC}"
    echo "   These pre-edit violations indicate architectural or quality problems"
    echo "   that will prevent successful code modifications."
    echo ""

    # Show top violating files
    echo -e "${YELLOW}📋 Top violating files:${NC}"
    for file in "${VIOLATION_FILES[@]:0:5}"; do
        echo "   • $file"
    done
    if [[ ${#VIOLATION_FILES[@]} -gt 5 ]]; then
        echo "   ... and $((${#VIOLATION_FILES[@]} - 5)) more files"
    fi

    echo ""
    echo -e "${BLUE}🛠️ REQUIRED FIXES (choose one approach):${NC}"
    echo ""
    echo -e "${GREEN}Option 1 - Automated Architecture Fix:${NC}"
    echo "   ./scripts/architecture/fix_violations.sh $PROJECT_DIR"
    echo "   # This will automatically fix common architectural violations"
    echo ""
    echo -e "${GREEN}Option 2 - Manual Individual Fixes:${NC}"
    echo "   1. Review detailed violations in: $OUTPUT_JSON"
    echo "   2. Fix violations file by file using:"
    echo "      ./scripts/pre_edit_validate.sh <file_path>"
    echo "      # Edit the file to fix violations"
    echo "      ./scripts/post_edit_validate.sh <backup_id> <file_path>"
    echo "   3. Repeat for each violating file"
    echo ""
    echo -e "${GREEN}Option 3 - Project-wide Manual Review:${NC}"
    echo "   1. Examine $OUTPUT_JSON for violation patterns"
    echo "   2. Apply fixes across similar files"
    echo "   3. Re-run analysis to verify: $0 $PROJECT_NAME"
    echo ""
    echo -e "${RED}⚠️ IMPORTANT: You cannot proceed with code changes until ALL violations are resolved!${NC}"
    echo "   Pre-validation ensures you start with clean, compliant code."
else
    echo ""
    echo -e "${GREEN}✅ EXCELLENT: All files are clean! No pre-edit violations found.${NC}"
    echo ""
    echo -e "${BLUE}🎉 READY FOR DEVELOPMENT:${NC}"
    echo "   Your $PROJECT_NAME project is in excellent condition!"
    echo "   You can now safely make code changes using the standard workflow:"
    echo ""
    echo "   1. For individual file changes:"
    echo "      ./scripts/pre_edit_validate.sh <file_path>"
    echo "      # make your changes"
    echo "      ./scripts/post_edit_validate.sh <backup_id> <file_path>"
    echo ""
    echo "   2. For bulk operations, continue monitoring quality with:"
    echo "      $0 $PROJECT_NAME  # periodic checks"
    echo ""
    echo "   3. Always run post-validation after changes to ensure compliance"
fi

echo ""
echo -e "${BLUE}📊 Analysis complete. Check $OUTPUT_JSON for full details.${NC}"
