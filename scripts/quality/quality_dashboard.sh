#!/bin/bash
# FLEXT Ecosystem Quality Dashboard
# Provides comprehensive overview of quality metrics across all FLEXT projects
# Usage: ./scripts/quality_dashboard.sh

set -euo pipefail

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m' # No Color

print_header() {
	echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
	echo -e "${BLUE}║               FLEXT ECOSYSTEM QUALITY DASHBOARD             ║${NC}"
	echo -e "${BLUE}╠══════════════════════════════════════════════════════════════╣${NC}"
	echo -e "${BLUE}║ Date: $(date +"%Y-%m-%d %H:%M:%S")                                        ║${NC}"
	echo -e "${BLUE}║ Scope: Complete FLEXT ecosystem quality overview            ║${NC}"
	echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
	echo ""
}

print_section() {
	echo -e "${CYAN}▓▓▓ $1 ▓▓▓${NC}"
}

run_domain_separation_validation() {
	print_section "DOMAIN SEPARATION COMPLIANCE"
	echo "Running comprehensive domain separation validation..."

	if ./scripts/domain_separation_validator.sh >/dev/null 2>&1; then
		echo -e "${GREEN}✅ DOMAIN SEPARATION: FULLY COMPLIANT${NC}"
		echo -e "   All projects follow proper domain boundaries"
	else
		echo -e "${RED}❌ DOMAIN SEPARATION: VIOLATIONS DETECTED${NC}"
		echo -e "   Run: ./scripts/domain_separation_validator.sh for details"
	fi
	echo ""
}

run_singer_protocol_validation() {
	print_section "SINGER PROTOCOL COMPLIANCE"
	echo "Validating Singer protocol implementation across tap/target projects..."

	if ./scripts/singer_protocol_validator.sh >/dev/null 2>&1; then
		echo -e "${GREEN}✅ SINGER PROTOCOL: FULLY COMPLIANT${NC}"
		echo -e "   All Singer projects meet protocol specifications"
	else
		echo -e "${RED}❌ SINGER PROTOCOL: COMPLIANCE ISSUES${NC}"
		echo -e "   Run: ./scripts/singer_protocol_validator.sh for details"
	fi
	echo ""
}

run_ecosystem_quality_validation() {
	print_section "ECOSYSTEM QUALITY GATES"
	echo "Comprehensive quality validation across all FLEXT projects..."

	local validation_result
	validation_result=$(./scripts/ecosystem_quality_validator.sh 2>&1 | grep -E "Quality Score:|ECOSYSTEM|violations" | tail -3)

	echo "$validation_result"
	echo ""
}

check_individual_project_status() {
	print_section "HIGH-IMPACT PROJECT STATUS"

	local critical_projects=("flext-core" "flext-db-oracle" "flext-tap-oracle" "flext-target-oracle" "client-a-oud-mig")

	echo -e "${WHITE}Project Status Overview:${NC}"
	echo "┌─────────────────────┬─────────────┬───────────────┬─────────────┐"
	echo "│ Project             │ Source      │ Tests         │ Status      │"
	echo "├─────────────────────┼─────────────┼───────────────┼─────────────┤"

	for project in "${critical_projects[@]}"; do
		if [[ -d $project ]]; then
			local src_files
			local test_files
			local status

			src_files=$(find "$project/src" -name "*.py" 2>/dev/null | wc -l || echo "0")
			test_files=$(find "$project/tests" -name "*.py" 2>/dev/null | wc -l || echo "0")

			if [[ $src_files -gt 0 && $test_files -gt 0 ]]; then
				status="${GREEN}✅ Active${NC}"
			elif [[ $src_files -gt 0 ]]; then
				status="${YELLOW}⚠️  No Tests${NC}"
			else
				status="${RED}❌ Missing${NC}"
			fi

			printf "│ %-19s │ %11s │ %13s │ %-19s │\n" "$project" "$src_files" "$test_files" "$status"
		else
			printf "│ %-19s │ %11s │ %13s │ %-19s │\n" "$project" "N/A" "N/A" "${RED}❌ Missing${NC}"
		fi
	done

	echo "└─────────────────────┴─────────────┴───────────────┴─────────────┘"
	echo ""
}

display_quality_recommendations() {
	print_section "QUALITY IMPROVEMENT RECOMMENDATIONS"

	echo -e "${WHITE}Based on current ecosystem analysis:${NC}"
	echo ""
	echo -e "${CYAN}🎯 Immediate Actions:${NC}"
	echo "   1. Run individual project quality gates: make validate"
	echo "   2. Address domain separation violations if detected"
	echo "   3. Ensure Singer protocol compliance for tap/target projects"
	echo "   4. Maintain 75%+ test coverage across all active projects"
	echo ""
	echo -e "${CYAN}🚀 Excellence Initiatives:${NC}"
	echo "   1. Apply proven flext-core patterns to other projects"
	echo "   2. Establish continuous quality monitoring"
	echo "   3. Document architectural decisions and patterns"
	echo "   4. Share quality achievements across development teams"
	echo ""
}

display_commands_reference() {
	print_section "QUALITY VALIDATION COMMANDS"

	echo -e "${WHITE}Use these commands for detailed quality analysis:${NC}"
	echo ""
	echo -e "${CYAN}Ecosystem-wide Validation:${NC}"
	echo "   ./scripts/domain_separation_validator.sh      - Domain boundaries"
	echo "   ./scripts/singer_protocol_validator.sh        - Singer compliance"
	echo "   ./scripts/ecosystem_quality_validator.sh      - Overall quality"
	echo ""
	echo -e "${CYAN}Project-specific Quality Gates:${NC}"
	echo "   cd [project] && make validate                  - Complete validation"
	echo "   cd [project] && make test                      - Test execution"
	echo "   cd [project] && make lint                      - Code quality"
	echo "   cd [project] && make type-check                - Type safety"
	echo ""
	echo -e "${CYAN}Development Workflow:${NC}"
	echo "   make format                                    - Auto-format code"
	echo "   make fix                                       - Auto-fix issues"
	echo "   make coverage                                  - Coverage analysis"
	echo ""
}

main() {
	print_header

	# Change to flext workspace directory
	if [[ ! -d "/home/marlonsc/flext" ]]; then
		echo -e "${RED}Error: FLEXT workspace not found at /home/marlonsc/flext${NC}"
		exit 1
	fi

	cd "/home/marlonsc/flext"

	# Run comprehensive quality dashboard
	run_domain_separation_validation
	run_singer_protocol_validation
	run_ecosystem_quality_validation
	check_individual_project_status
	display_quality_recommendations
	display_commands_reference

	echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
	echo -e "${BLUE}║          FLEXT ECOSYSTEM QUALITY DASHBOARD COMPLETE         ║${NC}"
	echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
}

main "$@"
