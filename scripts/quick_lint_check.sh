#!/bin/bash
# Owner-Skill: .claude/skills/scripts-validation/SKILL.md
# Quick lint check across all FLEXT projects

echo "=== FLEXT ECOSYSTEM QUICK LINT CHECK ==="
echo "Date: $(date)"
echo ""

PROJECTS=(
	"flext-core"
	"flext-cli"
	"flext-ldif"
	"flext-ldap"
	"client-a-oud-mig"
	"flext-auth"
	"flext-api"
	"flext-web"
	"flext-grpc"
	"flext-observability"
	"flext-quality"
	"flext-meltano"
)

echo "Project                  | Ruff Errors | Status"
echo "------------------------|-------------|--------"

for project in "${PROJECTS[@]}"; do
	if [ ! -d "$project" ]; then
		printf "%-23s | %-11s | %-6s\n" "$project" "N/A" "MISSING"
		continue
	fi

	cd "$project"

	# Count ruff errors
	if command -v ruff >/dev/null 2>&1; then
		ERROR_COUNT=$(ruff check . --output-format=concise 2>&1 | grep -c "^[^[:space:]]" || echo "0")
		if [ "$ERROR_COUNT" -eq 0 ]; then
			STATUS="✅ PASS"
		else
			STATUS="❌ FAIL"
		fi
	else
		ERROR_COUNT="N/A"
		STATUS="NO RUFF"
	fi

	printf "%-23s | %-11s | %-6s\n" "$project" "$ERROR_COUNT" "$STATUS"

	cd ..
done

echo ""
echo "=== DETAILED ANALYSIS FOR FAILED PROJECTS ==="

for project in "${PROJECTS[@]}"; do
	if [ ! -d "$project" ]; then
		continue
	fi

	cd "$project"

	if command -v ruff >/dev/null 2>&1; then
		ERROR_COUNT=$(ruff check . --output-format=concise 2>&1 | grep -c "^[^[:space:]]" || echo "0")
		if [ "$ERROR_COUNT" -gt 0 ]; then
			echo ""
			echo "=== $project ($ERROR_COUNT errors) ==="
			ruff check . --output-format=concise | head -20
			if [ "$ERROR_COUNT" -gt 20 ]; then
				echo "... and $((ERROR_COUNT - 20)) more errors"
			fi
		fi
	fi

	cd ..
done
