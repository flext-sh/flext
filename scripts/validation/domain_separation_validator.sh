#!/bin/bash
# FLEXT Domain Separation Validation Script
# Automatically validates domain separation compliance across FLEXT ecosystem
# Usage: ./scripts/domain_separation_validator.sh [project_name]

set -euo pipefail

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Global counters
VIOLATIONS_FOUND=0
PROJECTS_SCANNED=0

# Project directories to scan
readonly FLEXT_PROJECTS=(
	"flext-tap-oracle-oic"
	"flext-target-oracle"
	"flext-target-oracle-wms"
	"flext-tap-oracle"
	"flext-tap-oracle-wms"
	"flext-target-oracle-oic"
	"client-a-oud-mig"
	"flext-dbt-oracle"
	"flext-dbt-ldap"
	"flext-dbt-ldif"
)

print_header() {
	echo -e "${BLUE}=== FLEXT DOMAIN SEPARATION VALIDATION ===${NC}"
	echo -e "Date: $(date)"
	echo -e "Validator: Comprehensive Domain Boundary Enforcement"
	echo ""
}

print_section() {
	echo -e "${YELLOW}=== $1 ===${NC}"
}

log_violation() {
	local project=$1
	local violation_type=$2
	local details=$3
	echo -e "${RED}❌ VIOLATION: $project - $violation_type${NC}"
	echo -e "   Details: $details"
	((VIOLATIONS_FOUND++))
}

log_success() {
	local project=$1
	local check_type=$2
	echo -e "${GREEN}✅ COMPLIANT: $project - $check_type${NC}"
}

validate_singer_protocol_separation() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d "$project_dir/src" ]]; then
		return 0
	fi

	# Check for direct Singer/Meltano imports (should use flext-meltano)
	# Excludes legitimate singer_sdk usage
	local singer_violations
	singer_violations=$(find "$project_dir/src" -name "*.py" -exec grep -l "^import singer[^_]\|^from singer[^_]\|^import meltano\|^from meltano" {} \; 2>/dev/null || true)

	if [[ -n $singer_violations ]]; then
		log_violation "$project_name" "Direct Singer/Meltano Import" "Files: $singer_violations"
	else
		log_success "$project_name" "Singer Protocol Separation"
	fi
}

validate_database_separation() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d "$project_dir/src" ]]; then
		return 0
	fi

	# Check for direct database library imports (should use flext-db-oracle, flext-ldap, etc.)
	local db_violations
	db_violations=$(find "$project_dir/src" -name "*.py" -exec grep -l "^import sqlalchemy\|^from sqlalchemy\|^import oracledb\|^from oracledb\|^import cx_Oracle\|^from cx_Oracle\|^import ldap3\|^from ldap3" {} \; 2>/dev/null || true)

	if [[ -n $db_violations ]]; then
		log_violation "$project_name" "Direct Database Library Import" "Files: $db_violations"
	else
		log_success "$project_name" "Database Library Separation"
	fi
}

validate_http_client_separation() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d "$project_dir/src" ]]; then
		return 0
	fi

	# Check for direct HTTP client imports (should use flext-api)
	local http_violations
	http_violations=$(find "$project_dir/src" -name "*.py" -exec grep -l "^import requests\|^from requests\|^import httpx\|^from httpx\|^import urllib\|^from urllib" {} \; 2>/dev/null || true)

	if [[ -n $http_violations ]]; then
		log_violation "$project_name" "Direct HTTP Client Import" "Files: $http_violations"
	else
		log_success "$project_name" "HTTP Client Separation"
	fi
}

validate_cli_separation() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d "$project_dir/src" ]]; then
		return 0
	fi

	# Check for direct CLI library imports (should use flext-cli)
	local cli_violations
	cli_violations=$(find "$project_dir/src" -name "*.py" -exec grep -l "^import click\|^from click\|^import rich\|^from rich\|^import typer\|^from typer" {} \; 2>/dev/null || true)

	if [[ -n $cli_violations ]]; then
		log_violation "$project_name" "Direct CLI Library Import" "Files: $cli_violations"
	else
		log_success "$project_name" "CLI Library Separation"
	fi
}

validate_flext_core_integration() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d "$project_dir/src" ]]; then
		return 0
	fi

	# Check for proper flext-core integration
	local flext_core_usage
	flext_core_usage=$(find "$project_dir/src" -name "*.py" -exec grep -l "from flext_core\|import flext_core" {} \; 2>/dev/null || true)

	if [[ -z $flext_core_usage ]]; then
		log_violation "$project_name" "Missing FLEXT Core Integration" "No flext_core imports found"
	else
		log_success "$project_name" "FLEXT Core Integration"
	fi
}

validate_project() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d $project_dir ]]; then
		echo -e "${YELLOW}⚠️  SKIP: $project_name (directory not found)${NC}"
		return 0
	fi

	print_section "Validating $project_name"

	validate_singer_protocol_separation "$project_dir"
	validate_database_separation "$project_dir"
	validate_http_client_separation "$project_dir"
	validate_cli_separation "$project_dir"
	validate_flext_core_integration "$project_dir"

	((PROJECTS_SCANNED++))
	echo ""
}

generate_compliance_report() {
	print_section "DOMAIN SEPARATION COMPLIANCE REPORT"

	echo -e "Projects Scanned: ${PROJECTS_SCANNED}"
	echo -e "Total Violations: ${VIOLATIONS_FOUND}"

	if [[ $VIOLATIONS_FOUND -eq 0 ]]; then
		echo -e "${GREEN}🎉 ALL PROJECTS COMPLIANT: Zero domain separation violations detected${NC}"
		echo -e "${GREEN}✅ FLEXT Domain Separation: ENFORCED${NC}"
	else
		echo -e "${RED}❌ VIOLATIONS DETECTED: $VIOLATIONS_FOUND domain separation violations found${NC}"
		echo -e "${RED}🔧 ACTION REQUIRED: Fix violations before proceeding${NC}"
	fi

	echo ""
	echo -e "${BLUE}Domain Separation Rules Enforced:${NC}"
	echo -e "1. 🎵 Singer Protocol: Use flext-meltano exclusively"
	echo -e "2. 🗄️ Database Operations: Use flext-db-oracle, flext-ldap, flext-ldif exclusively"
	echo -e "3. 🌐 HTTP Operations: Use flext-api exclusively"
	echo -e "4. 🖥️ CLI Operations: Use flext-cli exclusively"
	echo -e "5. 📊 Core Patterns: Use flext-core exclusively"
}

main() {
	print_header

	# Change to flext workspace directory
	if [[ ! -d "../.." ]]; then
		echo -e "${RED}Error: FLEXT workspace not found at ../..${NC}"
		exit 1
	fi

	cd "../.."

	# If specific project provided, validate only that project
	if [[ $# -gt 0 ]]; then
		validate_project "$1"
	else
		# Validate all FLEXT projects
		for project in "${FLEXT_PROJECTS[@]}"; do
			validate_project "$project"
		done
	fi

	generate_compliance_report

	# Exit with error code if violations found
	exit $VIOLATIONS_FOUND
}

main "$@"
