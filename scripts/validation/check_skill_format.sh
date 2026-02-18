#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-validation/SKILL.md
#
# Validates that all canonical skills under .claude/skills/ conform to
# the skill-format-universal contract.
#
# Usage:
#   scripts/validation/check_skill_format.sh [--root DIR]
#
# Exit codes:
#   0 = all skills pass
#   1 = one or more skills have format violations

set -euo pipefail

ROOT_DIR="${1:-.}"
SKILLS_DIR="$ROOT_DIR/.claude/skills"
FAIL=0
CHECKED=0
ERRORS=()

if [[ ! -d "$SKILLS_DIR" ]]; then
	echo "SKIP: No .claude/skills/ directory found at $ROOT_DIR"
	exit 0
fi

REQUIRED_SECTIONS=(
	"## Scope"
	"## References"
	"## Rules"
	"## Instructions"
	"## Workflow"
	"## Examples"
	"## Verification"
)

for skill_dir in "$SKILLS_DIR"/*/; do
	[[ -d "$skill_dir" ]] || continue
	skill_name=$(basename "$skill_dir")
	skill_file="$skill_dir/SKILL.md"

	if [[ ! -f "$skill_file" ]]; then
		ERRORS+=("$skill_name: MISSING SKILL.md")
		FAIL=1
		continue
	fi

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

	# Check for TODO/TBD/placeholder
	if grep -qiE "\bTODO\b|\bTBD\b|\bplaceholder\b" "$skill_file"; then
		ERRORS+=("$skill_name: contains TODO/TBD/placeholder text")
		FAIL=1
	fi
done

echo "=== Skill Format Validation ==="
echo "Checked: $CHECKED skills"

if [[ ${#ERRORS[@]} -eq 0 ]]; then
	echo "✓ All skills pass format checks"
	exit 0
fi

echo "✗ ${#ERRORS[@]} violation(s) found:"
for err in "${ERRORS[@]}"; do
	echo "  - $err"
done
exit 1
