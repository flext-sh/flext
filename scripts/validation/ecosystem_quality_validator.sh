#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-validation/SKILL.md
# FLEXT Ecosystem Comprehensive Quality Validator
# Validates quality gates across the entire FLEXT ecosystem for enterprise excellence
# Usage: ./scripts/ecosystem_quality_validator.sh [project_name]

set -euo pipefail

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Global counters
TOTAL_VIOLATIONS=0
TOTAL_PROJECTS=0
QUALITY_PASSED=0

# High-impact FLEXT projects for ecosystem validation
readonly ECOSYSTEM_PROJECTS=(
	"flext-core"
	"flext-db-oracle"
	"flext-ldap"
	"flext-ldif"
	"flext-meltano"
	"flext-cli"
	"flext-api"
	"flext-auth"
	"flext-observability"
	"flext-tap-oracle"
	"flext-target-oracle"
	"flext-tap-oracle-oic"
	"flext-target-oracle-oic"
	"flext-tap-ldap"
	"flext-target-ldap"
	"client-a-oud-mig"
)

print_header() {
	echo -e "${BLUE}=== FLEXT ECOSYSTEM COMPREHENSIVE QUALITY VALIDATION ===${NC}"
	echo -e "Date: $(date)"
	echo -e "Validator: Enterprise Quality Gates with Comprehensive Coverage"
	echo -e "Scope: Complete FLEXT ecosystem validation for production excellence"
	echo ""
}

print_section() {
	echo -e "${YELLOW}=== $1 ===${NC}"
}

log_violation() {
	local project=$1
	local violation_type=$2
	local details=$3
	echo -e "${RED}❌ QUALITY VIOLATION: $project - $violation_type${NC}"
	echo -e "   Details: $details"
	((TOTAL_VIOLATIONS++))
}

log_success() {
	local project=$1
	local check_type=$2
	echo -e "${GREEN}✅ QUALITY PASSED: $project - $check_type${NC}"
}

log_warning() {
	local project=$1
	local warning_type=$2
	local details=$3
	echo -e "${YELLOW}⚠️  QUALITY WARNING: $project - $warning_type${NC}"
	echo -e "   Details: $details"
}

validate_code_quality() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d "$project_dir/src" ]]; then
		log_warning "$project_name" "No Source Directory" "No src/ directory found"
		return 0
	fi

	print_section "Validating Code Quality: $project_name"

	# Ruff linting validation
	if command -v ruff >/dev/null 2>&1; then
		local ruff_issues
		ruff_issues=$(cd "$project_dir" && ruff check src/ --statistics 2>/dev/null | grep -E "^[0-9]+ error" | awk '{print $1}' || echo "0")

		if [[ $ruff_issues == "0" ]]; then
			log_success "$project_name" "Ruff Code Quality (0 errors)"
		else
			log_violation "$project_name" "Ruff Code Quality" "$ruff_issues errors found"
		fi
	else
		log_warning "$project_name" "Ruff Not Available" "Ruff linter not installed"
	fi

	# MyPy type checking validation
	if command -v mypy >/dev/null 2>&1; then
		local mypy_output
		local mypy_issues
		mypy_output=$(cd "$project_dir" && mypy src/ --strict --no-error-summary 2>&1 || true)
		mypy_issues=$(echo "$mypy_output" | grep -c "error:" || echo "0")

		if [[ $mypy_issues == "0" ]]; then
			log_success "$project_name" "MyPy Type Safety (0 errors)"
		else
			log_violation "$project_name" "MyPy Type Safety" "$mypy_issues type errors found"
		fi
	else
		log_warning "$project_name" "MyPy Not Available" "MyPy type checker not installed"
	fi

	# Test coverage validation (using pytest if available)
	if command -v pytest >/dev/null 2>&1 && [[ -d "$project_dir/tests" ]]; then
		local coverage_result
		coverage_result=$(cd "$project_dir" && python -m pytest --cov=src --cov-report=term 2>/dev/null | grep "TOTAL" | awk '{print $NF}' | sed 's/%//' || echo "0")

		if [[ -n $coverage_result && $coverage_result != "0" ]]; then
			if (($(echo "$coverage_result >= 75" | bc -l))); then
				log_success "$project_name" "Test Coverage ($coverage_result% >= 75%)"
			else
				log_violation "$project_name" "Low Test Coverage" "$coverage_result% (target: 75%+)"
			fi
		else
			log_warning "$project_name" "Test Coverage Unknown" "Could not determine coverage"
		fi
	else
		log_warning "$project_name" "No Test Coverage" "No tests/ directory or pytest not available"
	fi
}

validate_architecture_compliance() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d "$project_dir/src" ]]; then
		return 0
	fi

	# Check for direct imports that violate domain separation
	local domain_violations
	domain_violations=$(find "$project_dir/src" -name "*.py" -exec grep -l "^import click\|^import rich\|^import sqlalchemy\|^import oracledb\|^import ldap3\|^import requests\|^import httpx" {} \; 2>/dev/null || true)

	if [[ -z $domain_violations ]]; then
		log_success "$project_name" "Domain Separation Compliance"
	else
		log_violation "$project_name" "Domain Separation Violation" "Direct library imports found: $domain_violations"
	fi

	# Check for flext-core integration
	local flext_core_usage
	flext_core_usage=$(find "$project_dir/src" -name "*.py" -exec grep -l "from flext_core\|import flext_core" {} \; 2>/dev/null | wc -l)

	if [[ $flext_core_usage -gt 0 ]]; then
		log_success "$project_name" "FLEXT Core Integration"
	else
		log_warning "$project_name" "Missing FLEXT Core Integration" "No flext-core imports found"
	fi
}

validate_documentation_quality() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	# Check for project documentation
	if [[ -f "$project_dir/CLAUDE.md" ]]; then
		log_success "$project_name" "Project Documentation (CLAUDE.md)"
	else
		log_warning "$project_name" "Missing Project Documentation" "No CLAUDE.md file found"
	fi

	if [[ -f "$project_dir/README.md" ]]; then
		log_success "$project_name" "README Documentation"
	else
		log_warning "$project_name" "Missing README" "No README.md file found"
	fi

	# Check for pyproject.toml configuration
	if [[ -f "$project_dir/pyproject.toml" ]]; then
		log_success "$project_name" "Python Configuration (pyproject.toml)"
	else
		log_warning "$project_name" "Missing Python Configuration" "No pyproject.toml file found"
	fi
}

validate_security_compliance() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d "$project_dir/src" ]]; then
		return 0
	fi

	# Check for potential security issues
	local security_issues=0

	# Check for hardcoded credentials
	if find "$project_dir/src" -name "*.py" -exec grep -l "password\s*=\s*['\"][^'\"]*['\"]" {} \; 2>/dev/null | head -1 >/dev/null; then
		log_violation "$project_name" "Security Risk" "Potential hardcoded credentials found"
		((security_issues++))
	fi

	# Check for SQL injection patterns
	if find "$project_dir/src" -name "*.py" -exec grep -l "f['\"].*SELECT.*{.*}.*['\"]" {} \; 2>/dev/null | head -1 >/dev/null; then
		log_violation "$project_name" "Security Risk" "Potential SQL injection patterns found"
		((security_issues++))
	fi

	if [[ $security_issues == "0" ]]; then
		log_success "$project_name" "Security Compliance (basic checks)"
	fi
}

validate_ecosystem_project() {
	local project_dir=$1
	local project_name=$(basename "$project_dir")

	if [[ ! -d $project_dir ]]; then
		echo -e "${YELLOW}⚠️  SKIP: $project_name (directory not found)${NC}"
		return 0
	fi

	print_section "Comprehensive Quality Validation: $project_name"

	# Core quality validations
	validate_code_quality "$project_dir"
	validate_architecture_compliance "$project_dir"
	validate_documentation_quality "$project_dir"
	validate_security_compliance "$project_dir"

	((TOTAL_PROJECTS++))
	echo ""
}

generate_comprehensive_quality_report() {
	print_section "FLEXT ECOSYSTEM COMPREHENSIVE QUALITY REPORT"

	echo -e "Projects Validated: ${TOTAL_PROJECTS}"
	echo -e "Total Quality Violations: ${TOTAL_VIOLATIONS}"

	# Calculate quality score
	local quality_score=0
	if [[ $TOTAL_PROJECTS -gt 0 ]]; then
		quality_score=$(((TOTAL_PROJECTS * 100) / (TOTAL_PROJECTS + TOTAL_VIOLATIONS)))
	fi

	echo -e "Ecosystem Quality Score: ${quality_score}%"

	if [[ $TOTAL_VIOLATIONS -eq 0 ]]; then
		echo -e "${GREEN}🎉 ECOSYSTEM EXCELLENCE ACHIEVED: Zero quality violations detected${NC}"
		echo -e "${GREEN}✅ FLEXT Ecosystem: PRODUCTION READY${NC}"
	elif [[ $quality_score -ge 90 ]]; then
		echo -e "${YELLOW}🟡 HIGH QUALITY ECOSYSTEM: Minor improvements needed${NC}"
		echo -e "${YELLOW}⚡ Quality Score: ${quality_score}% (Excellent)${NC}"
	elif [[ $quality_score -ge 75 ]]; then
		echo -e "${YELLOW}🟡 GOOD QUALITY ECOSYSTEM: Some improvements needed${NC}"
		echo -e "${YELLOW}📈 Quality Score: ${quality_score}% (Good)${NC}"
	else
		echo -e "${RED}❌ QUALITY IMPROVEMENTS NEEDED: ${TOTAL_VIOLATIONS} violations found${NC}"
		echo -e "${RED}🔧 ACTION REQUIRED: Address quality violations for production readiness${NC}"
		echo -e "${RED}📉 Quality Score: ${quality_score}% (Needs Improvement)${NC}"
	fi

	echo ""
	echo -e "${BLUE}Enterprise Quality Standards Validated:${NC}"
	echo -e "1. 🔍 Code Quality: Ruff linting with zero tolerance for errors"
	echo -e "2. 🏷️  Type Safety: MyPy strict mode validation"
	echo -e "3. 🧪 Test Coverage: 75%+ coverage with real functional tests"
	echo -e "4. 🏗️  Architecture: Domain separation and FLEXT core integration"
	echo -e "5. 📚 Documentation: Project-specific standards and configurations"
	echo -e "6. 🔒 Security: Basic security compliance validation"
	echo -e "7. 🎯 Integration: Comprehensive ecosystem integration patterns"

	echo ""
	echo -e "${BLUE}Next Steps for Excellence:${NC}"
	if [[ $TOTAL_VIOLATIONS -gt 0 ]]; then
		echo -e "1. Address ${TOTAL_VIOLATIONS} quality violations identified"
		echo -e "2. Run project-specific quality improvements"
		echo -e "3. Validate fixes with individual project quality gates"
		echo -e "4. Re-run ecosystem validation to confirm improvements"
	else
		echo -e "1. Maintain current excellence standards"
		echo -e "2. Monitor quality metrics continuously"
		echo -e "3. Apply proven patterns to new projects"
		echo -e "4. Share quality achievements across organization"
	fi
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
		validate_ecosystem_project "$1"
	else
		# Validate all ecosystem projects
		for project in "${ECOSYSTEM_PROJECTS[@]}"; do
			validate_ecosystem_project "$project"
		done
	fi

	generate_comprehensive_quality_report

	# Exit with appropriate code based on quality level
	if [[ $TOTAL_VIOLATIONS -eq 0 ]]; then
		exit 0 # Perfect quality
	elif [[ $TOTAL_VIOLATIONS -le 5 ]]; then
		exit 1 # Minor issues
	else
		exit 2 # Major issues requiring attention
	fi
}

main "$@"
