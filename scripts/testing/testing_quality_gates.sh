#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-testing/SKILL.md
# testing_quality_gates.sh - Validate testing standards across FLEXT ecosystem
#
# Usage: ./scripts/testing_quality_gates.sh [options]
# Options:
#   --core-only     Validate only core infrastructure projects
#   --project NAME  Validate specific project only
#   --fix          Attempt to fix common issues automatically
#   --verbose      Show detailed output
#
# Exit codes:
#   0 - All validations passed
#   1 - Critical validation failures found
#   2 - Warning-level issues found

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
REQUIRED_MARKERS=("unit" "integration" "slow" "oracle" "performance" "smoke" "e2e")
CORE_PROJECTS=("flext-core" "flext-api" "flext-cli" "flext-auth")

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
VERBOSE=false
CORE_ONLY=false
SPECIFIC_PROJECT=""
FIX_ISSUES=false
EXIT_CODE=0

# Function to log messages
log_info() {
	echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
	echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
	echo -e "${YELLOW}⚠️  $1${NC}"
	if [ $EXIT_CODE -eq 0 ]; then
		EXIT_CODE=2
	fi
}

log_error() {
	echo -e "${RED}❌ $1${NC}"
	EXIT_CODE=1
}

log_verbose() {
	if [ "$VERBOSE" = true ]; then
		echo -e "${NC}   $1${NC}"
	fi
}

# Function to show usage
usage() {
	echo "FLEXT Testing Quality Gates Validator"
	echo ""
	echo "Usage: $0 [options]"
	echo ""
	echo "Options:"
	echo "  --core-only     Validate only core infrastructure projects"
	echo "  --project NAME  Validate specific project only"
	echo "  --fix          Attempt to fix common issues automatically"
	echo "  --verbose      Show detailed output"
	echo "  --help         Show this help message"
	echo ""
	echo "Examples:"
	echo "  $0                           # Validate all projects"
	echo "  $0 --core-only              # Validate only core projects"
	echo "  $0 --project flext-core     # Validate specific project"
	echo "  $0 --fix --verbose          # Fix issues with detailed output"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
	case $1 in
	--core-only)
		CORE_ONLY=true
		shift
		;;
	--project)
		SPECIFIC_PROJECT="$2"
		shift 2
		;;
	--fix)
		FIX_ISSUES=true
		shift
		;;
	--verbose)
		VERBOSE=true
		shift
		;;
	--help)
		usage
		exit 0
		;;
	*)
		echo "Unknown option: $1"
		usage
		exit 1
		;;
	esac
done

# Function to check if a project has pytest configuration
check_pytest_config() {
	local project=$1
	local pyproject_file="$project/pyproject.toml"

	log_verbose "Checking pytest configuration in $pyproject_file"

	if [ ! -f "$pyproject_file" ]; then
		log_error "$project: Missing pyproject.toml"
		return 1
	fi

	if ! grep -q '\[tool\.pytest\.ini_options\]' "$pyproject_file" 2>/dev/null; then
		if [ "$FIX_ISSUES" = true ]; then
			log_info "$project: Adding basic pytest configuration"
			cat >>"$pyproject_file" <<'EOF'

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--tb=short",
    "-ra",
    "--maxfail=1",
]
markers = [
    "unit: Unit tests (default)",
    "integration: Integration tests",
    "slow: Slow tests",
    "oracle: Oracle database tests",
    "performance: Performance tests",
    "smoke: Smoke tests",
    "e2e: End-to-end tests",
]
EOF
			log_success "$project: Added basic pytest configuration"
		else
			log_error "$project: Missing pytest configuration in pyproject.toml"
			return 1
		fi
	else
		log_verbose "$project: pytest configuration found"
	fi

	return 0
}

# Function to check required markers
check_markers() {
	local project=$1
	local pyproject_file="$project/pyproject.toml"
	local missing_markers=()

	log_verbose "Checking required markers in $project"

	for marker in "${REQUIRED_MARKERS[@]}"; do
		if ! grep -q "\"$marker:" "$pyproject_file" 2>/dev/null; then
			missing_markers+=("$marker")
		fi
	done

	if [ ${#missing_markers[@]} -gt 0 ]; then
		if [ "$FIX_ISSUES" = true ]; then
			log_info "$project: Adding missing markers: ${missing_markers[*]}"
			# Note: This is a simplified fix - in practice, you'd want more sophisticated marker addition
			log_warning "$project: Missing markers require manual addition: ${missing_markers[*]}"
		else
			log_warning "$project: Missing standard markers: ${missing_markers[*]}"
		fi
		return 1
	else
		log_verbose "$project: All required markers found"
	fi

	return 0
}

# Function to check test directory structure
check_test_structure() {
	local project=$1

	log_verbose "Checking test directory structure in $project"

	# Check tests directory exists
	if [ ! -d "$project/tests" ]; then
		if [ "$FIX_ISSUES" = true ]; then
			log_info "$project: Creating tests directory structure"
			mkdir -p "$project/tests/unit"
			mkdir -p "$project/tests/integration"
			touch "$project/tests/__init__.py"
			touch "$project/tests/conftest.py"
			cat >"$project/tests/conftest.py" <<'EOF'
"""Test configuration for project."""

import pytest


@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {"test": "data"}
EOF
			log_success "$project: Created basic test directory structure"
		else
			log_error "$project: Missing tests/ directory"
			return 1
		fi
	else
		log_verbose "$project: tests/ directory found"
	fi

	# Check conftest.py exists
	if [ ! -f "$project/tests/conftest.py" ]; then
		log_warning "$project: Missing tests/conftest.py (recommended for fixtures)"
	else
		log_verbose "$project: conftest.py found"
	fi

	return 0
}

# Function to check test dependencies
check_test_dependencies() {
	local project=$1
	local pyproject_file="$project/pyproject.toml"

	log_verbose "Checking test dependencies in $project"

	local required_deps=("pytest" "pytest-cov")
	local missing_deps=()

	for dep in "${required_deps[@]}"; do
		if ! grep -q "\"$dep" "$pyproject_file" 2>/dev/null; then
			missing_deps+=("$dep")
		fi
	done

	if [ ${#missing_deps[@]} -gt 0 ]; then
		log_warning "$project: Missing recommended test dependencies: ${missing_deps[*]}"
		return 1
	else
		log_verbose "$project: Required test dependencies found"
	fi

	return 0
}

read_fail_under() {
	local project=$1
	local pyproject_file="$project/pyproject.toml"

	if [ ! -f "$pyproject_file" ]; then
		return 1
	fi

	python3 - "$pyproject_file" <<'PY'
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

path = Path(sys.argv[1])
data = tomllib.loads(path.read_text(encoding="utf-8"))
report = data.get("tool", {}).get("coverage", {}).get("report", {})
value = report.get("fail_under")
if value is None:
    raise SystemExit(1)
print(value)
PY
}

# Function to run tests and check coverage
run_tests() {
	local project=$1

	log_verbose "Running tests for $project"

	cd "$project"

	# Check if Poetry is available
	if ! command -v poetry &>/dev/null; then
		log_error "$project: Poetry not available for running tests"
		cd - >/dev/null
		return 1
	fi

	# Check if dependencies are installed
	if [ ! -f "poetry.lock" ]; then
		log_warning "$project: No poetry.lock found, installing dependencies"
		poetry install --quiet 2>/dev/null || {
			log_error "$project: Failed to install dependencies"
			cd - >/dev/null
			return 1
		}
	fi

	# Run tests
	log_info "$project: Running tests..."
	if poetry run pytest tests/ --tb=short -q 2>/dev/null; then
		log_success "$project: Tests passed"
	else
		# Try without coverage if that was the issue
		if poetry run pytest tests/ --tb=short -q --no-cov 2>/dev/null; then
			log_warning "$project: Tests passed but coverage reporting failed"
		else
			log_error "$project: Tests failed"
			cd - >/dev/null
			return 1
		fi
	fi

	if ! fail_under="$(read_fail_under "$project")"; then
		log_error "$project: Missing [tool.coverage.report].fail_under in pyproject.toml"
		cd - >/dev/null
		return 1
	fi

	if poetry run python -m coverage report >/dev/null 2>&1; then
		log_verbose "$project: Coverage threshold gate passed (fail_under=$fail_under)"
	else
		log_error "$project: Coverage threshold gate failed (fail_under=$fail_under)"
		cd - >/dev/null
		return 1
	fi

	cd - >/dev/null
	return 0
}

# Function to validate a single project
validate_project() {
	local project=$1
	local project_path="$WORKSPACE_ROOT/$project"

	if [ ! -d "$project_path" ]; then
		log_error "Project $project not found at $project_path"
		return 1
	fi

	echo ""
	log_info "Validating $project..."

	cd "$WORKSPACE_ROOT"

	local validation_passed=true

	# Check pytest configuration
	if ! check_pytest_config "$project"; then
		validation_passed=false
	fi

	# Check required markers
	if ! check_markers "$project"; then
		validation_passed=false
	fi

	# Check test directory structure
	if ! check_test_structure "$project"; then
		validation_passed=false
	fi

	# Check test dependencies
	if ! check_test_dependencies "$project"; then
		validation_passed=false
	fi

	# Run tests (optional, can be disabled for speed)
	if [ "$VERBOSE" = true ]; then
		if ! run_tests "$project"; then
			validation_passed=false
		fi
	fi

	if [ "$validation_passed" = true ]; then
		log_success "$project: All validations passed"
	else
		log_error "$project: Validation failures detected"
	fi

	return $validation_passed
}

# Main execution
main() {
	echo "🧪 FLEXT Testing Quality Gates Validation"
	echo "========================================"
	echo "Workspace: $WORKSPACE_ROOT"
	echo "Date: $(date)"
	echo ""

	cd "$WORKSPACE_ROOT"

	local projects_to_validate=()

	# Determine which projects to validate
	if [ -n "$SPECIFIC_PROJECT" ]; then
		projects_to_validate=("$SPECIFIC_PROJECT")
		log_info "Validating specific project: $SPECIFIC_PROJECT"
	elif [ "$CORE_ONLY" = true ]; then
		projects_to_validate=("${CORE_PROJECTS[@]}")
		log_info "Validating core infrastructure projects only"
	else
		# Find all flext-* projects
		while IFS= read -r -d '' project; do
			project=$(basename "$project")
			projects_to_validate+=("$project")
		done < <(find . -maxdepth 1 -name "flext-*" -type d -print0)

		# Add other known projects
		for other_project in "client-a-oud-mig" "client-b-meltano-native"; do
			if [ -d "$other_project" ]; then
				projects_to_validate+=("$other_project")
			fi
		done

		log_info "Validating all FLEXT projects (${#projects_to_validate[@]} found)"
	fi

	# Validate projects
	local total_projects=${#projects_to_validate[@]}
	local failed_projects=0

	for project in "${projects_to_validate[@]}"; do
		if ! validate_project "$project"; then
			((failed_projects++))
		fi
	done

	echo ""
	echo "📊 VALIDATION SUMMARY"
	echo "===================="
	echo "Total projects: $total_projects"
	echo "Passed: $((total_projects - failed_projects))"
	echo "Failed: $failed_projects"

	if [ $failed_projects -eq 0 ]; then
		log_success "All testing quality gates passed!"
		EXIT_CODE=0
	else
		log_error "$failed_projects project(s) failed validation"
		EXIT_CODE=1
	fi

	if [ $EXIT_CODE -eq 2 ]; then
		log_warning "Validation completed with warnings"
	fi

	echo ""
	log_info "For detailed testing standards, see: FLEXT_TESTING_STANDARDS.md"

	exit $EXIT_CODE
}

# Execute main function
main "$@"
