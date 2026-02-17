#!/bin/bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# Message Formatter - Consistent messaging for validation scripts
#
# Provides functions for formatting validation output with colors and emojis.
# Enhances readability of validation scripts output.
#
# Usage:
#   source scripts/lib/message_formatter.sh
#   print_header "Validating file.py"
#   print_success "Validation passed"
#   print_error "Validation failed"
#
# Copyright (c) 2025 FLEXT Team. All rights reserved.
# SPDX-License-Identifier: MIT

set -euo pipefail

# ANSI color codes
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly MAGENTA='\033[0;35m'
readonly NC='\033[0m'

# Print header message
print_header() {
	local message="$1"
	echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
	echo -e "${CYAN}$message${NC}"
	echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Print success message
print_success() {
	local message="$1"
	echo -e "${GREEN}✅ $message${NC}"
}

# Print error message
print_error() {
	local message="$1"
	echo -e "${RED}❌ $message${NC}" >&2
}

# Print warning message
print_warning() {
	local message="$1"
	echo -e "${YELLOW}⚠️  $message${NC}"
}

# Print info message
print_info() {
	local message="$1"
	echo -e "${BLUE}ℹ️  $message${NC}"
}

# Print status line (before operation)
print_status() {
	local label="$1"
	local value="$2"
	printf "  ${CYAN}%-30s${NC} %s\n" "$label:" "$value"
}

# Print blocking violation (with red)
print_blocking_violation() {
	local code="$1"
	local line="$2"
	local message="$3"
	echo -e "    ${RED}[$code] L$line: $message${NC}"
}

# Print warning violation (with yellow)
print_warning_violation() {
	local code="$1"
	local line="$2"
	local message="$3"
	echo -e "    ${YELLOW}[$code] L$line: $message${NC}"
}

# Print staging area info
print_staging_info() {
	local backup_id="$1"
	local staging_dir="$2"
	echo -e "\n${MAGENTA}📝 Staging Area Information${NC}"
	echo -e "  ${CYAN}Backup ID:${NC}    $backup_id"
	echo -e "  ${CYAN}Staging Dir:${NC}  $staging_dir"
	echo -e "  ${CYAN}Status:${NC}       Original protected, edits in staging\n"
}

# Print runtime info
print_runtime_info() {
	local runtime="$1"
	local emoji="ℹ️"
	if [[ $runtime == "claude-code" ]]; then
		emoji="🔗"
	elif [[ $runtime == "standalone" ]]; then
		emoji="🎯"
	fi
	echo -e "  ${MAGENTA}${emoji} Runtime:${NC} $runtime"
}

# Print validation summary
print_validation_summary() {
	local ruff_count="$1"
	local mypy_count="$2"
	local total_count=$((ruff_count + mypy_count))

	echo -e "\n${MAGENTA}📊 Validation Summary${NC}"
	if [[ $ruff_count -gt 0 ]]; then
		echo -e "  ${RED}🔴 Ruff errors:${NC} $ruff_count"
	else
		echo -e "  ${GREEN}✅ Ruff errors:${NC} 0"
	fi
	if [[ $mypy_count -gt 0 ]]; then
		echo -e "  ${RED}🔴 MyPy errors:${NC} $mypy_count"
	else
		echo -e "  ${GREEN}✅ MyPy errors:${NC} 0"
	fi
	echo -e "  ${CYAN}Total:${NC} $total_count"
}

# Print section divider
print_divider() {
	echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Export functions
export -f print_header
export -f print_success
export -f print_error
export -f print_warning
export -f print_info
export -f print_status
export -f print_blocking_violation
export -f print_warning_violation
export -f print_staging_info
export -f print_runtime_info
export -f print_validation_summary
export -f print_divider
