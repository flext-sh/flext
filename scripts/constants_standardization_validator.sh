#!/bin/bash
# FLEXT Constants Standardization Validator
# Validates and enforces [Project]Constants pattern across all FLEXT projects
# Usage: ./scripts/constants_standardization_validator.sh [project_name]

set -euo pipefail

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m' # No Color

# Global counters
TOTAL_VIOLATIONS=0
TOTAL_PROJECTS=0
COMPLIANCE_PASSED=0

# FLEXT projects for constants validation
readonly FLEXT_PROJECTS=(
	"flext-core"
	"flext-cli"
	"flext-api"
	"flext-auth"
	"flext-db-oracle"
	"flext-ldap"
	"flext-ldif"
	"flext-meltano"
	"flext-observability"
	"flext-tap-oracle"
	"flext-target-oracle"
	"flext-tap-oracle-oic"
	"flext-target-oracle-oic"
	"flext-tap-ldap"
	"flext-target-ldap"
	"flext-plugin"
	"flext-quality"
	"flext-grpc"
	"flext-web"
	"client-a-oud-mig"
	"client-b-meltano-native"
)

print_header() {
	echo -e "${BLUE}=== FLEXT CONSTANTS STANDARDIZATION VALIDATOR ===${NC}"
	echo -e "Date: $(date)"
	echo -e "Validator: [Project]Constants Pattern Compliance"
	echo -e "Standard: Single class with nested domains, FlextCore.Constants inheritance"
	echo ""
}

print_section() {
	echo -e "${YELLOW}=== $1 ===${NC}"
}

log_violation() {
	local project=$1
	local violation_type=$2
	local details=$3
	echo -e "${RED}❌ CONSTANTS VIOLATION: $project - $violation_type${NC}"
	echo -e "   Details: $details"
	((TOTAL_VIOLATIONS++))
}

log_success() {
	local project=$1
	local check_type=$2
	echo -e "${GREEN}✅ CONSTANTS COMPLIANT: $project - $check_type${NC}"
}

log_warning() {
	local project=$1
	local warning_type=$2
	local details=$3
	echo -e "${YELLOW}⚠️  CONSTANTS WARNING: $project - $warning_type${NC}"
	echo -e "   Details: $details"
}

validate_single_class_pattern() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")
	local constants_file="$project_dir/src/*/constants.py"

	if ! ls "$constants_file" >/dev/null 2>&1; then
		log_warning "$project_name" "No Constants File" "No constants.py found"
		return 0
	fi

	for file in $constants_file; do
		if [[ ! -f $file ]]; then
			continue
		fi

		# Check for single class pattern
		local class_count
		class_count=$(grep -c "^class " "$file" 2>/dev/null || echo "0")
		class_count=${class_count//[^0-9]/} # Ensure numeric
		if [[ ${class_count:-0} -gt 1 ]]; then
			log_violation "$project_name" "Multiple Classes" "$class_count classes found in $(basename "$file")"
		elif [[ ${class_count:-0} -eq 1 ]]; then
			log_success "$project_name" "Single Class Pattern"
		else
			log_violation "$project_name" "No Constants Class" "No class definition found in $(basename "$file")"
		fi

		# Check for loose constants (critical violation)
		local loose_constants
		loose_constants=$(grep -c "^[A-Z_][A-Z0-9_]*:" "$file" 2>/dev/null || echo "0")
		loose_constants=${loose_constants//[^0-9]/} # Ensure numeric
		if [[ ${loose_constants:-0} -gt 0 ]]; then
			log_violation "$project_name" "Loose Constants" "$loose_constants loose constants found outside class"
		else
			log_success "$project_name" "No Loose Constants"
		fi
	done
}

validate_flext_constants_inheritance() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")
	local constants_file="$project_dir/src/*/constants.py"

	for file in $constants_file; do
		if [[ ! -f $file ]]; then
			continue
		fi

		# Check for FlextCore.Constants inheritance (skip for flext-core itself)
		if [[ $project_name == "flext-core" ]]; then
			if grep -q "class FlextCore.Constants:" "$file" 2>/dev/null; then
				log_success "$project_name" "FlextCore.Constants Foundation Class"
			else
				log_warning "$project_name" "Unexpected FlextCore.Constants Structure" "Expected class FlextCore.Constants in flext-core"
			fi
		else
			if grep -q "class.*Constants.*FlextCore.Constants" "$file" 2>/dev/null; then
				log_success "$project_name" "FlextCore.Constants Inheritance"
			else
				log_violation "$project_name" "Missing FlextCore.Constants Inheritance" "Constants class should inherit from FlextCore.Constants"
			fi
		fi

		# Check for proper imports (skip for flext-core itself)
		if [[ $project_name == "flext-core" ]]; then
			log_success "$project_name" "Foundation - No Import Required"
		else
			if grep -q "from flext_core import FlextCore" "$file" 2>/dev/null; then
				log_success "$project_name" "Proper FlextCore.Constants Import"
			else
				log_violation "$project_name" "Missing FlextCore.Constants Import" "Should import FlextCore.Constants from flext_core"
			fi
		fi
	done
}

validate_no_duplication_with_flext_constants() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")
	local constants_file="$project_dir/src/*/constants.py"

	for file in $constants_file; do
		if [[ ! -f $file ]]; then
			continue
		fi

		# Check for common duplication patterns
		local duplications=0

		# Check for timeout duplications (skip for flext-core foundation)
		if [[ $project_name != "flext-core" ]]; then
			if grep -q "DEFAULT_TIMEOUT.*=" "$file" && ! grep -q 'FlextCore.Constants\..*DEFAULT_TIMEOUT' "$file" 2>/dev/null; then
				log_violation "$project_name" "Timeout Duplication" "Should use FlextCore.Constants.Network.DEFAULT_TIMEOUT"
				((duplications++))
			fi
		fi

		# Check for batch size duplications (skip for flext-core foundation)
		if [[ $project_name != "flext-core" ]]; then
			# Look for actual batch size constant definitions that don't reference FlextCore.Constants
			if grep -q "BATCH_SIZE.*=" "$file" && ! grep -q 'FlextCore.Constants\.Performance\.BatchProcessing' "$file" 2>/dev/null; then
				log_violation "$project_name" "Batch Size Duplication" "Should use FlextCore.Constants.Performance.BatchProcessing constants"
				((duplications++))
			fi
		fi

		# Check for error code duplications (skip for flext-core foundation)
		if [[ $project_name != "flext-core" ]]; then
			# Look for actual VALIDATION_ERROR constant definitions, not logging config
			if grep -q "^[[:space:]]*VALIDATION_ERROR.*=" "$file" && ! grep -q 'FlextCore.Constants\..*VALIDATION_ERROR' "$file" 2>/dev/null; then
				log_violation "$project_name" "Error Code Duplication" "Should extend FlextCore.Constants.Errors.VALIDATION_ERROR"
				((duplications++))
			fi
		fi

		if [[ $duplications -eq 0 ]]; then
			log_success "$project_name" "No Obvious Duplications"
		fi
	done
}

validate_nested_domain_organization() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")
	local constants_file="$project_dir/src/*/constants.py"

	for file in $constants_file; do
		if [[ ! -f $file ]]; then
			continue
		fi

		# Check for nested domain classes
		local nested_classes
		nested_classes=$(grep -c "^[[:space:]]\+class " "$file" 2>/dev/null || echo "0")
		if [[ $nested_classes -gt 0 ]]; then
			log_success "$project_name" "Nested Domain Organization ($nested_classes nested classes)"
		else
			log_warning "$project_name" "No Domain Organization" "Consider organizing constants in nested classes"
		fi

		# Check for project metadata constants
		if grep -q "CONSTANTS_VERSION\|PROJECT_PREFIX\|PROJECT_NAME" "$file" 2>/dev/null; then
			log_success "$project_name" "Project Metadata Present"
		else
			log_warning "$project_name" "Missing Project Metadata" "Should include CONSTANTS_VERSION, PROJECT_PREFIX, PROJECT_NAME"
		fi
	done
}

validate_type_annotations() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")
	local constants_file="$project_dir/src/*/constants.py"

	for file in $constants_file; do
		if [[ ! -f $file ]]; then
			continue
		fi

		# Check for Final type annotations
		if grep -q "from typing import.*Final" "$file" 2>/dev/null; then
			log_success "$project_name" "Final Type Annotations Imported"
		else
			log_warning "$project_name" "Missing Final Import" "Should import Final from typing for constants"
		fi

		# Check for proper Final usage
		local final_usage
		final_usage=$(grep -c ": Final\[" "$file" 2>/dev/null || echo "0")
		if [[ $final_usage -gt 0 ]]; then
			log_success "$project_name" "Final Annotations Used ($final_usage instances)"
		else
			log_warning "$project_name" "No Final Annotations" "Constants should use Final[type] annotations"
		fi
	done
}

validate_project_constants() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d $project_dir ]]; then
		echo -e "${YELLOW}⚠️  SKIP: $project_name (directory not found)${NC}"
		return 0
	fi

	print_section "Validating Constants Pattern: $project_name"

	# Core validation checks
	validate_single_class_pattern "$project_dir"
	validate_flext_constants_inheritance "$project_dir"
	validate_no_duplication_with_flext_constants "$project_dir"
	validate_nested_domain_organization "$project_dir"
	validate_type_annotations "$project_dir"

	((TOTAL_PROJECTS++))
	echo ""
}

generate_constants_compliance_report() {
	print_section "FLEXT CONSTANTS STANDARDIZATION REPORT"

	echo -e "Projects Validated: ${TOTAL_PROJECTS}"
	echo -e "Total Constants Violations: ${TOTAL_VIOLATIONS}"

	# Calculate compliance score
	local compliance_score=0
	if [[ $TOTAL_PROJECTS -gt 0 ]]; then
		compliance_score=$(((TOTAL_PROJECTS * 100) / (TOTAL_PROJECTS + TOTAL_VIOLATIONS)))
	fi

	echo -e "Constants Compliance Score: ${compliance_score}%"

	if [[ $TOTAL_VIOLATIONS -eq 0 ]]; then
		echo -e "${GREEN}🎉 CONSTANTS EXCELLENCE ACHIEVED: Zero violations detected${NC}"
		echo -e "${GREEN}✅ FLEXT Ecosystem: CONSTANTS STANDARDIZED${NC}"
	elif [[ $compliance_score -ge 90 ]]; then
		echo -e "${YELLOW}🟡 HIGH CONSTANTS COMPLIANCE: Minor standardization needed${NC}"
		echo -e "${YELLOW}⚡ Compliance Score: ${compliance_score}% (Excellent)${NC}"
	elif [[ $compliance_score -ge 75 ]]; then
		echo -e "${YELLOW}🟡 GOOD CONSTANTS COMPLIANCE: Some standardization needed${NC}"
		echo -e "${YELLOW}📈 Compliance Score: ${compliance_score}% (Good)${NC}"
	else
		echo -e "${RED}❌ CONSTANTS STANDARDIZATION NEEDED: ${TOTAL_VIOLATIONS} violations found${NC}"
		echo -e "${RED}🔧 ACTION REQUIRED: Apply [Project]Constants pattern for compliance${NC}"
		echo -e "${RED}📉 Compliance Score: ${compliance_score}% (Needs Improvement)${NC}"
	fi

	echo ""
	echo -e "${BLUE}Constants Standardization Patterns Validated:${NC}"
	echo -e "1. 🏗️  Single Class Pattern: One [Project]Constants class per module"
	echo -e "2. 🧬 FlextCore.Constants Inheritance: Proper inheritance from flext-core"
	echo -e "3. 🚫 No Duplication: Reference FlextCore.Constants instead of duplicating"
	echo -e "4. 🏘️  Nested Organization: Domain-specific nested classes"
	echo -e "5. 🏷️  Type Annotations: Proper Final[type] annotations"
	echo -e "6. 📋 Project Metadata: Version, prefix, and name constants"

	echo ""
	echo -e "${BLUE}Next Steps for Constants Excellence:${NC}"
	if [[ $TOTAL_VIOLATIONS -gt 0 ]]; then
		echo -e "1. Address ${TOTAL_VIOLATIONS} constants violations identified"
		echo -e "2. Apply [Project]Constants pattern to non-compliant projects"
		echo -e "3. Eliminate loose constants and multiple classes"
		echo -e "4. Ensure FlextCore.Constants inheritance and reference patterns"
		echo -e "5. Re-run validator to confirm standardization"
	else
		echo -e "1. Maintain current constants excellence"
		echo -e "2. Monitor constants compliance in new development"
		echo -e "3. Apply proven patterns to new projects"
		echo -e "4. Share constants standardization across development teams"
	fi
}

main() {
	print_header

	# Change to flext workspace directory
	if [[ ! -d ".." ]]; then
		echo -e "${RED}Error: FLEXT workspace not found at ..${NC}"
		exit 1
	fi

	cd ".."

	# If specific project provided, validate only that project
	if [[ $# -gt 0 ]]; then
		validate_project_constants "$1"
	else
		# Validate all FLEXT projects
		for project in "${FLEXT_PROJECTS[@]}"; do
			validate_project_constants "$project"
		done
	fi

	generate_constants_compliance_report

	# Exit with appropriate code based on compliance level
	if [[ $TOTAL_VIOLATIONS -eq 0 ]]; then
		exit 0 # Perfect compliance
	elif [[ $TOTAL_VIOLATIONS -le 5 ]]; then
		exit 1 # Minor issues
	else
		exit 2 # Major issues requiring attention
	fi
}

main "$@"
