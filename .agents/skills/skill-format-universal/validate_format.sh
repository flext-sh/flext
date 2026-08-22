#!/usr/bin/env bash
# Owner-Skill: .agents/skills/scripts-validation/SKILL.md
#
# Validates that all canonical skills under .agents/skills/ conform to
# the skill-format-universal contract.
#
# Usage:
#   .agents/skills/skill-format-universal/validate_format.sh [--root DIR]
#
# Exit codes:
#   0 = all skills pass
#   1 = one or more skills have format violations

set -euo pipefail

ROOT_DIR="."
while [[ $# -gt 0 ]]; do
	case "$1" in
	--root)
		ROOT_DIR="$2"
		shift 2
		;;
	--mode) shift 2 ;;
	*)
		ROOT_DIR="$1"
		shift
		;;
	esac
done
SKILLS_DIR="$ROOT_DIR/.agents/skills"
FAIL=0
CHECKED=0
ERRORS=()

if [[ ! -d "$SKILLS_DIR" ]]; then
	echo "SKIP: No .agents/skills/ directory found at $ROOT_DIR"
	exit 0
fi

REQUIRED_SECTIONS=(
	"## USE FOR"
	"## DO NOT USE FOR"
	"## Workflow"
	"## Critical rules"
)

while IFS= read -r skill_file; do
	skill_dir=$(dirname "$skill_file")
	skill_name=$(basename "$skill_dir")

	CHECKED=$((CHECKED + 1))

	# Check frontmatter presence (--- block at top)
	if ! head -1 "$skill_file" | grep -q "^---$"; then
		ERRORS+=("$skill_name: missing YAML frontmatter (first line must be '---')")
		FAIL=1
	fi

	# Check name field in frontmatter
	if ! grep -q "^name:" "$skill_file"; then
		ERRORS+=("$skill_name: missing 'name:' in frontmatter")
		FAIL=1
	else
		# Check name matches directory name
		fm_name=$(grep -m1 "^name:" "$skill_file" | sed 's/^name:\s*//')
		if [[ "$fm_name" != "$skill_name" ]]; then
			ERRORS+=("$skill_name: frontmatter name '$fm_name' does not match directory name '$skill_name'")
			FAIL=1
		fi
	fi

	# Check description field in frontmatter
	if ! grep -q "^description:" "$skill_file"; then
		ERRORS+=("$skill_name: missing 'description:' in frontmatter")
		FAIL=1
	fi

	# Check required sections
	for section in "${REQUIRED_SECTIONS[@]}"; do
		if ! grep -q "^${section}$\|^${section} " "$skill_file"; then
			ERRORS+=("$skill_name: missing section '$section'")
			FAIL=1
		fi
	done

	# Check for prohibited "When to use" heading
	if grep -qiE "^## When to [Uu]se" "$skill_file"; then
		ERRORS+=("$skill_name: has prohibited '## When to use' heading (put trigger info in description)")
		FAIL=1
	fi

	# Check for TODO/TBD/placeholder (skip code blocks and grep/rg verification commands)
	todo_hits=$(awk '
		/^```/   { in_code = !in_code; next }
		in_code  { next }
		/rg -n|grep -[a-zA-Z]*n|rg .*TODO|grep .*TODO/ { next }
		/\bTODO\b|\bTBD\b/ { found++; next }
		/[Dd]o not.*placeholder|not.*placeholder/ { next }
		/\bplaceholder\b/ { found++ }
		END { print found+0 }
	' "$skill_file")
	if [[ "$todo_hits" -gt 0 ]]; then
		ERRORS+=("$skill_name: contains TODO/TBD/placeholder text ($todo_hits occurrence(s) outside code blocks)")
		FAIL=1
	fi
done < <(find "$SKILLS_DIR" -mindepth 2 -maxdepth 2 -name "SKILL.md" -type f | sort)

echo "=== Skill Format Validation ===" >&2
echo "Checked: $CHECKED skills" >&2

if [[ ${#ERRORS[@]} -eq 0 ]]; then
	echo "✓ All skills pass format checks" >&2
	echo "{\"violation_count\": 0}"
	exit 0
fi

echo "✗ ${#ERRORS[@]} violation(s) found:" >&2
for err in "${ERRORS[@]}"; do
	echo "  - $err" >&2
done
echo "{\"violation_count\": ${#ERRORS[@]}}"
exit 1
