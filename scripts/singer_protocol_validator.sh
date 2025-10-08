#!/bin/bash
# FLEXT Singer Protocol Compliance Validation Script
# Validates Singer specification compliance across FLEXT tap/target projects
# Usage: ./scripts/singer_protocol_validator.sh [project_name]

set -euo pipefail

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Global counters
COMPLIANCE_VIOLATIONS=0
PROJECTS_VALIDATED=0

# Singer tap/target projects to validate
readonly SINGER_PROJECTS=(
	"flext-tap-oracle-oic"
	"flext-tap-oracle"
	"flext-target-oracle"
	"flext-target-oracle-wms"
	"flext-target-oracle-oic"
	"flext-tap-oracle-wms"
	"flext-tap-ldap"
	"flext-target-ldap"
	"flext-tap-ldif"
	"flext-target-ldif"
)

print_header() {
	echo -e "${BLUE}=== FLEXT SINGER PROTOCOL COMPLIANCE VALIDATION ===${NC}"
	echo -e "Date: $(date)"
	echo -e "Validator: Singer Specification Compliance Checker"
	echo ""
}

print_section() {
	echo -e "${YELLOW}=== $1 ===${NC}"
}

log_violation() {
	local project=$1
	local violation_type=$2
	local details=$3
	echo -e "${RED}❌ SINGER VIOLATION: $project - $violation_type${NC}"
	echo -e "   Details: $details"
	((COMPLIANCE_VIOLATIONS++))
}

log_success() {
	local project=$1
	local check_type=$2
	echo -e "${GREEN}✅ SINGER COMPLIANT: $project - $check_type${NC}"
}

validate_singer_tap_structure() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d "$project_dir/src" ]]; then
		return 0
	fi

	# Check for Singer tap implementation patterns
	local tap_implementation
	tap_implementation=$(find "$project_dir/src" -name "*.py" -exec grep -l "class.*Tap\|def discover\|def get_records" {} \; 2>/dev/null || true)

	if [[ -n $tap_implementation ]]; then
		log_success "$project_name" "Tap Implementation Structure"

		# Validate discover method presence
		local discover_method
		discover_method=$(find "$project_dir/src" -name "*.py" -exec grep -l "def discover" {} \; 2>/dev/null || true)

		if [[ -n $discover_method ]]; then
			log_success "$project_name" "Catalog Discovery Method"
		else
			log_violation "$project_name" "Missing Catalog Discovery" "No discover method found"
		fi

		# Validate stream implementation
		local stream_implementation
		stream_implementation=$(find "$project_dir/src" -name "*.py" -exec grep -l "def get_records\|class.*Stream" {} \; 2>/dev/null || true)

		if [[ -n $stream_implementation ]]; then
			log_success "$project_name" "Stream Implementation"
		else
			log_violation "$project_name" "Missing Stream Implementation" "No stream classes or get_records methods found"
		fi
	else
		log_violation "$project_name" "Missing Tap Structure" "No Singer tap implementation found"
	fi
}

validate_singer_target_structure() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d "$project_dir/src" ]]; then
		return 0
	fi

	# Check for Singer target implementation patterns
	local target_implementation
	target_implementation=$(find "$project_dir/src" -name "*.py" -exec grep -l "class.*Target\|def process_record\|def process_schema" {} \; 2>/dev/null || true)

	if [[ -n $target_implementation ]]; then
		log_success "$project_name" "Target Implementation Structure"

		# Validate record processing
		local record_processing
		record_processing=$(find "$project_dir/src" -name "*.py" -exec grep -l "def process_record\|def load_record" {} \; 2>/dev/null || true)

		if [[ -n $record_processing ]]; then
			log_success "$project_name" "Record Processing Implementation"
		else
			log_violation "$project_name" "Missing Record Processing" "No record processing methods found"
		fi

		# Validate schema processing
		local schema_processing
		schema_processing=$(find "$project_dir/src" -name "*.py" -exec grep -l "def process_schema\|def ensure_table" {} \; 2>/dev/null || true)

		if [[ -n $schema_processing ]]; then
			log_success "$project_name" "Schema Processing Implementation"
		else
			log_violation "$project_name" "Missing Schema Processing" "No schema processing methods found"
		fi
	else
		log_violation "$project_name" "Missing Target Structure" "No Singer target implementation found"
	fi
}

validate_singer_message_handling() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d "$project_dir/src" ]]; then
		return 0
	fi

	# Check for Singer message format handling - includes Singer SDK patterns
	local message_handling
	message_handling=$(find "$project_dir/src" -name "*.py" -exec grep -l "SCHEMA\|RECORD\|STATE\|singer.*message\|from singer_sdk\|import singer_sdk\|singer_sdk.*typing\|FlextMeltanoStream\|FlextSingerTarget" {} \; 2>/dev/null || true)

	if [[ -n $message_handling ]]; then
		log_success "$project_name" "Singer Message Handling"
	else
		log_violation "$project_name" "Missing Message Handling" "No Singer message format handling found"
	fi
}

validate_configuration_schema() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d "$project_dir/src" ]]; then
		return 0
	fi

	# Check for configuration schema definition
	local config_schema
	config_schema=$(find "$project_dir/src" -name "*.py" -exec grep -l "config.*schema\|ConfigModel\|pydantic\|BaseModel" {} \; 2>/dev/null || true)

	if [[ -n $config_schema ]]; then
		log_success "$project_name" "Configuration Schema"
	else
		log_violation "$project_name" "Missing Configuration Schema" "No configuration schema definition found"
	fi
}

validate_flext_meltano_integration() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d "$project_dir/src" ]]; then
		return 0
	fi

	# Check for proper flext-meltano integration
	local meltano_integration
	meltano_integration=$(find "$project_dir/src" -name "*.py" -exec grep -l "from flext_meltano\|import flext_meltano" {} \; 2>/dev/null || true)

	if [[ -n $meltano_integration ]]; then
		log_success "$project_name" "FLEXT Meltano Integration"
	else
		log_violation "$project_name" "Missing FLEXT Meltano Integration" "No flext-meltano integration found"
	fi
}

validate_singer_project() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d $project_dir ]]; then
		echo -e "${YELLOW}⚠️  SKIP: $project_name (directory not found)${NC}"
		return 0
	fi

	print_section "Validating Singer Project: $project_name"

	# Determine if this is a tap or target project
	if [[ $project_name == *"tap"* ]]; then
		validate_singer_tap_structure "$project_dir"
	elif [[ $project_name == *"target"* ]]; then
		validate_singer_target_structure "$project_dir"
	else
		echo -e "${YELLOW}⚠️  UNKNOWN: $project_name (not clearly tap or target)${NC}"
	fi

	# Common validations for all Singer projects
	validate_singer_message_handling "$project_dir"
	validate_configuration_schema "$project_dir"
	validate_flext_meltano_integration "$project_dir"

	((PROJECTS_VALIDATED++))
	echo ""
}

generate_singer_compliance_report() {
	print_section "SINGER PROTOCOL COMPLIANCE REPORT"

	echo -e "Projects Validated: ${PROJECTS_VALIDATED}"
	echo -e "Compliance Violations: ${COMPLIANCE_VIOLATIONS}"

	if [[ $COMPLIANCE_VIOLATIONS -eq 0 ]]; then
		echo -e "${GREEN}🎉 ALL SINGER PROJECTS COMPLIANT: Zero Singer protocol violations detected${NC}"
		echo -e "${GREEN}✅ Singer Specification: FULLY IMPLEMENTED${NC}"
	else
		echo -e "${RED}❌ SINGER VIOLATIONS DETECTED: $COMPLIANCE_VIOLATIONS Singer protocol violations found${NC}"
		echo -e "${RED}🔧 ACTION REQUIRED: Fix Singer compliance violations before proceeding${NC}"
	fi

	echo ""
	echo -e "${BLUE}Singer Protocol Requirements Validated:${NC}"
	echo -e "1. 🎵 Singer Message Format: SCHEMA, RECORD, STATE message handling"
	echo -e "2. 📋 Catalog Discovery: Dynamic schema discovery for taps"
	echo -e "3. 🔄 Data Processing: Record extraction (taps) and loading (targets)"
	echo -e "4. ⚙️ Configuration: Proper configuration schema definition"
	echo -e "5. 🔗 FLEXT Integration: Proper flext-meltano integration"
}

main() {
	print_header

	# Change to flext workspace directory
	if [[ ! -d "/home/marlonsc/flext" ]]; then
		echo -e "${RED}Error: FLEXT workspace not found at /home/marlonsc/flext${NC}"
		exit 1
	fi

	cd "/home/marlonsc/flext"

	# If specific project provided, validate only that project
	if [[ $# -gt 0 ]]; then
		validate_singer_project "$1"
	else
		# Validate all Singer projects
		for project in "${SINGER_PROJECTS[@]}"; do
			validate_singer_project "$project"
		done
	fi

	generate_singer_compliance_report

	# Exit with error code if violations found
	exit $COMPLIANCE_VIOLATIONS
}

main "$@"
