#!/bin/bash

echo "=== FLEXT ECOSYSTEM QA COMMAND VALIDATION ==="
echo "Checking all 33 FLEXT projects for mandatory QA commands"
echo ""

# Define all FLEXT projects
FLEXT_PROJECTS=(
	flext-api flext-auth flext-cli flext-core flext-db-oracle
	flext-dbt-ldap flext-dbt-ldif flext-dbt-oracle flext-dbt-oracle-wms
	flext-grpc flext-ldap flext-ldif flext-meltano flext-observability
	flext-oracle-oic-ext flext-oracle-wms flext-plugin flext-quality
	flext-tap-ldap flext-tap-ldif flext-tap-oracle flext-tap-oracle-oic
	flext-tap-oracle-wms flext-target-ldap flext-target-ldif
	flext-target-oracle flext-target-oracle-oic flext-target-oracle-wms
	flext-tools flext-web client-a-oud-mig client-b-meltano-native flexcore
)

COMPLIANT_PROJECTS=()
NON_COMPLIANT_PROJECTS=()
MISSING_MAKEFILE=()

# Check each project
for project in "${FLEXT_PROJECTS[@]}"; do
	echo "Checking project: $project"

	if [ ! -d "$project" ]; then
		echo "  ❌ Project directory not found: $project"
		NON_COMPLIANT_PROJECTS+=("$project:missing_directory")
		continue
	fi

	if [ ! -f "$project/Makefile" ]; then
		echo "  ❌ Missing Makefile: $project"
		MISSING_MAKEFILE+=("$project")
		NON_COMPLIANT_PROJECTS+=("$project:missing_makefile")
		continue
	fi

	# Check for required QA commands
	makefile="$project/Makefile"
	has_validate=$(grep -q "^\.PHONY:.*validate" "$makefile" && echo "yes" || echo "no")
	has_check=$(grep -q "^\.PHONY:.*check" "$makefile" && echo "yes" || echo "no")
	has_lint=$(grep -q "^\.PHONY:.*lint" "$makefile" && echo "yes" || echo "no")
	has_type_check=$(grep -q "^\.PHONY:.*type-check" "$makefile" && echo "yes" || echo "no")
	has_test=$(grep -q "^\.PHONY:.*test" "$makefile" && echo "yes" || echo "no")

	# Check if this is a Go project
	is_go_project="no"
	if [ -f "$project/go.mod" ]; then
		is_go_project="yes"
	fi

	# Check command implementations based on project type
	if [[ $is_go_project == "yes" ]]; then
		# Go project - check for Go-specific tools
		has_golangci=$(grep -q "golangci-lint" "$makefile" && echo "yes" || echo "no")
		has_go_vet=$(grep -q "go vet" "$makefile" && echo "yes" || echo "no")
		has_go_test=$(grep -q "go test.*-cover" "$makefile" && echo "yes" || echo "no")

		echo "    Commands: validate=$has_validate check=$has_check lint=$has_lint type-check=$has_type_check test=$has_test"
		echo "    Tools (Go): golangci=$has_golangci go_vet=$has_go_vet go_test_coverage=$has_go_test"

		# Determine compliance for Go projects
		if [[ $has_validate == "yes" && $has_check == "yes" && $has_lint == "yes" &&
			$has_type_check == "yes" && $has_test == "yes" && $has_golangci == "yes" &&
			$has_go_vet == "yes" && $has_go_test == "yes" ]]; then
			echo "  ✅ COMPLIANT: All mandatory QA commands present (Go project)"
			COMPLIANT_PROJECTS+=("$project")
		else
			echo "  ❌ NON-COMPLIANT: Missing mandatory QA commands (Go project)"
			NON_COMPLIANT_PROJECTS+=("$project:missing_commands")
		fi
	else
		# Python project - check for Python-specific tools
		has_ruff=$(grep -q "ruff check" "$makefile" && echo "yes" || echo "no")
		has_pyrefly=$(grep -q "pyrefly check" "$makefile" && echo "yes" || echo "no")
		has_pytest_cov=$(grep -q "pytest.*--cov.*--cov-fail-under" "$makefile" && echo "yes" || echo "no")

		echo "    Commands: validate=$has_validate check=$has_check lint=$has_lint type-check=$has_type_check test=$has_test"
		echo "    Tools (Python): ruff=$has_ruff pyrefly=$has_pyrefly pytest_cov=$has_pytest_cov"

		# Determine compliance for Python projects
		if [[ $has_validate == "yes" && $has_check == "yes" && $has_lint == "yes" &&
			$has_type_check == "yes" && $has_test == "yes" && $has_ruff == "yes" &&
			$has_pyrefly == "yes" && $has_pytest_cov == "yes" ]]; then
			echo "  ✅ COMPLIANT: All mandatory QA commands present (Python project)"
			COMPLIANT_PROJECTS+=("$project")
		else
			echo "  ❌ NON-COMPLIANT: Missing mandatory QA commands (Python project)"
			NON_COMPLIANT_PROJECTS+=("$project:missing_commands")
		fi
	fi
	echo ""
done

echo "=== SUMMARY ==="
echo "Total projects checked: ${#FLEXT_PROJECTS[@]}"
echo "Compliant projects: ${#COMPLIANT_PROJECTS[@]}"
echo "Non-compliant projects: ${#NON_COMPLIANT_PROJECTS[@]}"
echo "Missing Makefile: ${#MISSING_MAKEFILE[@]}"
echo ""

echo "✅ COMPLIANT PROJECTS:"
for project in "${COMPLIANT_PROJECTS[@]}"; do
	echo "  - $project"
done
echo ""

echo "❌ NON-COMPLIANT PROJECTS:"
for project in "${NON_COMPLIANT_PROJECTS[@]}"; do
	echo "  - $project"
done
echo ""

echo "📝 PROJECTS MISSING MAKEFILE:"
for project in "${MISSING_MAKEFILE[@]}"; do
	echo "  - $project"
done
