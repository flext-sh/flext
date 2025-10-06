#!/bin/bash

# FLEXT Constants Compliance Comprehensive Validation Script
# Validates [Project]Constants usage across ALL directories (src/, examples/, scripts/, tests/)
# Version: 2.0.0
# Last Updated: 2025-09-26

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly LOG_FILE="${PROJECT_ROOT}/constants_compliance_report.log"

# Validation patterns
readonly HARDCODED_PATTERNS=(
	"8080|8000|8081|3000|5000|9090"  # Common web ports
	"5432|5433|3306|27017|6379"      # Database ports
	"389|636|1389"                   # LDAP ports
	"\"localhost\"|\"127\.0\.0\.1\"" # Localhost references
	"timeout\s*=\s*[0-9]+"           # Hardcoded timeouts
	"port\s*=\s*[0-9]+"              # Hardcoded ports
)

# Projects to validate
readonly FLEXT_PROJECTS=(
	"flext-core" "flext-cli" "flext-api" "flext-auth" "flext-web"
	"flext-grpc" "flext-observability" "flext-quality" "flext-plugin"
	"flext-db-oracle" "flext-oracle-wms" "flext-oracle-oic"
	"flext-ldap" "flext-ldif" "flext-meltano"
	"flext-dbt-ldap" "flext-dbt-ldif" "flext-dbt-oracle"
	"flext-tap-ldap" "flext-tap-ldif" "flext-tap-oracle"
	"flext-target-ldap" "flext-target-ldif" "flext-target-oracle"
	"client-a-oud-mig" "client-b-meltano-native"
)

# Directories to validate in each project
readonly VALIDATE_DIRS=("src" "examples" "scripts" "tests")

# Constants that should be used instead of hardcoded values
declare -A CONSTANT_MAPPINGS=(
	["8000"]="FlextConstants.Platform.FLEXT_API_PORT"
	["8080"]="FlextConstants.Platform.DEFAULT_HTTP_PORT"
	["5432"]="FlextConstants.Platform.POSTGRES_DEFAULT_PORT"
	["27017"]="FlextConstants.Platform.MONGODB_DEFAULT_PORT"
	["6379"]="FlextConstants.Platform.REDIS_DEFAULT_PORT"
	["389"]="FlextConstants.Platform.LDAP_DEFAULT_PORT"
	["636"]="FlextConstants.Platform.LDAPS_DEFAULT_PORT"
	["localhost"]="FlextConstants.Platform.DEFAULT_HOST"
	["127.0.0.1"]="FlextConstants.Platform.LOCALHOST_IP"
	["30"]="FlextConstants.Network.DEFAULT_TIMEOUT"
)

# Global counters
declare -g TOTAL_VIOLATIONS=0
declare -g TOTAL_FILES_CHECKED=0
declare -g PROJECTS_WITH_VIOLATIONS=0

# Logging functions
log_info() {
	echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
	echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
	echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
	echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Initialize log file
init_logging() {
	echo "FLEXT Constants Compliance Report" >"$LOG_FILE"
	echo "Generated: $(date)" >>"$LOG_FILE"
	echo "=======================================" >>"$LOG_FILE"
	echo "" >>"$LOG_FILE"
}

# Check if project directory exists
project_exists() {
	local project="$1"
	[[ -d "${PROJECT_ROOT}/${project}" ]]
}

# Check if project has constants file
has_constants_file() {
	local project="$1"
	[[ -f "${PROJECT_ROOT}/${project}/src/${project//-/_}/constants.py" ]]
}

# Check if file imports FlextConstants
imports_flext_constants() {
	local file="$1"
	grep -q "from flext_core import.*FlextConstants\|import.*FlextConstants" "$file" 2>/dev/null
}

# Check if file imports project constants
imports_project_constants() {
	local file="$1"
	local project="$2"
	local project_module="${project//-/_}"
	grep -q "from ${project_module} import.*Constants\|import.*${project_module}.*Constants" "$file" 2>/dev/null
}

# Find hardcoded values in file
find_hardcoded_values() {
	local file="$1"
	local violations=()

	for pattern in "${HARDCODED_PATTERNS[@]}"; do
		while IFS= read -r line; do
			[[ -n $line ]] && violations+=("$line")
		done < <(grep -n -E "$pattern" "$file" 2>/dev/null || true)
	done

	printf '%s\n' "${violations[@]}"
}

# Check if hardcoded value is in acceptable context
is_acceptable_context() {
	local line="$1"
	local file="$2"

	# Check if it's in a test data context
	if echo "$line" | grep -qi "test\|example\|demo\|sample\|mock"; then
		return 0
	fi

	# Check if it's in a comment or docstring
	if echo "$line" | grep -E "^\s*#|^\s*\"\"\"|\*|/\*|//"; then
		return 0
	fi

	# Check if it's legitimate test URL/data
	if echo "$line" | grep -qi "httpbin\|example\.com\|test\.com\|demo\."; then
		return 0
	fi

	# Check if it's in tests directory with legitimate test values
	if echo "$file" | grep -q "/tests/" && echo "$line" | grep -qi "assert\|expect\|validate"; then
		return 0
	fi

	return 1
}

# Validate single file
validate_file() {
	local file="$1"
	local project="$2"
	local relative_path="${file#"${PROJECT_ROOT}"/}"
	local violations=()

	((TOTAL_FILES_CHECKED++))

	# Skip binary files and non-Python files for detailed analysis
	if [[ ! $file =~ \.py$ ]]; then
		return 0
	fi

	# Find hardcoded values
	local hardcoded_lines
	hardcoded_lines=$(find_hardcoded_values "$file")

	if [[ -n $hardcoded_lines ]]; then
		local file_has_violations=false

		while IFS= read -r line; do
			if [[ -n $line ]] && ! is_acceptable_context "$line" "$file"; then
				violations+=("$relative_path:$line")
				file_has_violations=true
			fi
		done <<<"$hardcoded_lines"

		if [[ $file_has_violations == true ]]; then
			# Check if file imports required constants
			local needs_flext_constants=false
			local needs_project_constants=false

			for violation in "${violations[@]}"; do
				if echo "$violation" | grep -E "localhost|127\.0\.0\.1|timeout|port" >/dev/null; then
					needs_flext_constants=true
				fi
				if echo "$violation" | grep -E "8080|5432|389|636" >/dev/null; then
					needs_project_constants=true
				fi
			done

			# Report missing imports
			if [[ $needs_flext_constants == true ]] && ! imports_flext_constants "$file"; then
				violations+=("$relative_path: Missing FlextConstants import")
			fi

			if [[ $needs_project_constants == true ]] && ! imports_project_constants "$file" "$project"; then
				violations+=("$relative_path: Missing ${project}Constants import")
			fi
		fi
	fi

	printf '%s\n' "${violations[@]}"
}

# Validate project directory
validate_project_directory() {
	local project="$1"
	local directory="$2"
	local dir_path="${PROJECT_ROOT}/${project}/${directory}"

	if [[ ! -d $dir_path ]]; then
		return 0
	fi

	log_info "Validating ${project}/${directory}/"

	local project_violations=()
	local files_found=0

	while IFS= read -r -d '' file; do
		((files_found++))
		local file_violations
		file_violations=$(validate_file "$file" "$project")

		if [[ -n $file_violations ]]; then
			while IFS= read -r violation; do
				[[ -n $violation ]] && project_violations+=("$violation")
			done <<<"$file_violations"
		fi
	done < <(find "$dir_path" -name "*.py" -type f -print0 2>/dev/null)

	if [[ ${#project_violations[@]} -gt 0 ]]; then
		log_warning "${project}/${directory}: ${#project_violations[@]} violations found"
		for violation in "${project_violations[@]}"; do
			echo "  - $violation" | tee -a "$LOG_FILE"
			((TOTAL_VIOLATIONS++))
		done
		return 1
	else
		log_success "${project}/${directory}: No violations found ($files_found files checked)"
		return 0
	fi
}

# Validate single project
validate_project() {
	local project="$1"

	if ! project_exists "$project"; then
		log_warning "Project $project not found, skipping"
		return 0
	fi

	log_info "Validating project: $project"

	# Check if project has constants file
	if ! has_constants_file "$project"; then
		log_warning "$project: No constants.py file found in src/"
	fi

	local project_has_violations=false

	# Validate each directory
	for dir in "${VALIDATE_DIRS[@]}"; do
		if ! validate_project_directory "$project" "$dir"; then
			project_has_violations=true
		fi
	done

	if [[ $project_has_violations == true ]]; then
		((PROJECTS_WITH_VIOLATIONS++))
		log_error "$project: Has constants compliance violations"
		return 1
	else
		log_success "$project: All directories compliant"
		return 0
	fi
}

# Generate recommendations
generate_recommendations() {
	local report_file="${PROJECT_ROOT}/constants_compliance_recommendations.md"

	cat >"$report_file" <<'EOF'
# FLEXT Constants Compliance Recommendations

## Quick Fixes for Common Violations

### 1. Import FlextConstants

```python
# Add to imports
from flext_core import FlextConstants

# Replace hardcoded values
timeout = 30  # ❌ BEFORE
timeout = FlextConstants.Network.DEFAULT_TIMEOUT  # ✅ AFTER

host = "localhost"  # ❌ BEFORE
host = FlextConstants.Platform.DEFAULT_HOST  # ✅ AFTER
```

### 2. Use Project Constants

```python
# Add to imports
from flext_ldap import FlextLDAPConstants

# Replace hardcoded values
port = 389  # ❌ BEFORE
port = FlextLDAPConstants.Protocol.DEFAULT_PORT  # ✅ AFTER
```

### 3. Common Constant Mappings

| Hardcoded Value | Recommended Constant |
|----------------|---------------------|
| `8000` | `FlextConstants.Platform.FLEXT_API_PORT` |
| `8080` | `FlextConstants.Platform.DEFAULT_HTTP_PORT` |
| `5432` | `FlextConstants.Platform.POSTGRES_DEFAULT_PORT` |
| `389` | `FlextConstants.Platform.LDAP_DEFAULT_PORT` |
| `"localhost"` | `FlextConstants.Platform.DEFAULT_HOST` |
| `30` (timeout) | `FlextConstants.Network.DEFAULT_TIMEOUT` |

### 4. Acceptable Hardcoded Values

These contexts are acceptable and don't need constants:
- Test data for validation functions
- Example URLs (httpbin.org, example.com)
- Comments and docstrings
- Demonstration/tutorial code with educational purpose

## Implementation Priority

1. **High Priority**: Configuration and production code in `src/`
2. **Medium Priority**: Examples that demonstrate proper patterns
3. **Low Priority**: Test data and educational examples

EOF

	log_info "Recommendations written to: $report_file"
}

# Generate summary report
generate_summary() {
	local status="FAILED"
	if [[ $TOTAL_VIOLATIONS -eq 0 ]]; then
		status="PASSED"
	fi

	cat <<EOF | tee -a "$LOG_FILE"

========================================
FLEXT CONSTANTS COMPLIANCE SUMMARY
========================================

Status: $status
Total Files Checked: $TOTAL_FILES_CHECKED
Total Violations: $TOTAL_VIOLATIONS
Projects with Violations: $PROJECTS_WITH_VIOLATIONS / ${#FLEXT_PROJECTS[@]}

EOF

	if [[ $TOTAL_VIOLATIONS -gt 0 ]]; then
		cat <<EOF | tee -a "$LOG_FILE"
❌ FAILED: Constants compliance violations found

Next Steps:
1. Review violations in: $LOG_FILE
2. Check recommendations in: constants_compliance_recommendations.md
3. Update hardcoded values to use appropriate constants
4. Re-run validation: ./scripts/validate_constants_comprehensive.sh

EOF
		return 1
	else
		cat <<EOF | tee -a "$LOG_FILE"
✅ PASSED: All projects are constants compliant

All FLEXT projects properly use [Project]Constants and FlextConstants
for configuration values, timeouts, ports, and host references.

EOF
		return 0
	fi
}

# Main validation function
main() {
	log_info "Starting FLEXT Constants Compliance Validation"
	log_info "Validating ${#FLEXT_PROJECTS[@]} projects across ${#VALIDATE_DIRS[@]} directory types"

	init_logging

	# Validate each project
	for project in "${FLEXT_PROJECTS[@]}"; do
		validate_project "$project"
		echo "" | tee -a "$LOG_FILE"
	done

	# Generate recommendations
	generate_recommendations

	# Generate summary and exit with appropriate code
	if generate_summary; then
		log_success "Constants compliance validation completed successfully"
		exit 0
	else
		log_error "Constants compliance validation failed"
		exit 1
	fi
}

# Script entry point
if [[ ${BASH_SOURCE[0]} == "${0}" ]]; then
	main "$@"
fi
