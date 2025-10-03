#!/bin/bash
#
# Git History Cleanup Validator
#
# Validates repositories after history cleanup to ensure quality standards
#
# Usage: ./git_cleanup_validator.sh [--all-repos]

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  FLEXT Git History Cleanup Validator                     ║${NC}"
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Validate a single repository
validate_repo() {
	local repo_path="$1"
	local repo_name=$(basename "$repo_path")

	echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
	echo -e "${BLUE}Validating: ${repo_name}${NC}"
	echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

	if [ ! -d "$repo_path/.git" ]; then
		echo -e "${RED}❌ Not a git repository${NC}"
		return 1
	fi

	cd "$repo_path"

	local issues=0

	# 1. Check for conventional commit messages
	echo -e "${YELLOW}1️⃣  Checking commit message format...${NC}"
	local non_conventional=$(git log --all --format='%s' | grep -v -E "^(feat|fix|docs|style|refactor|perf|test|chore|build|ci|revert)(\(.+\))?:" | head -10)

	if [ -n "$non_conventional" ]; then
		echo -e "${YELLOW}   ⚠️  Found non-conventional commits:${NC}"
		echo "$non_conventional" | head -5 | sed 's/^/      /'
		if [ $(echo "$non_conventional" | wc -l) -gt 5 ]; then
			echo -e "${YELLOW}      ... and more${NC}"
		fi
		issues=$((issues + 1))
	else
		echo -e "${GREEN}   ✅ All commits follow conventional format${NC}"
	fi

	# 2. Check for cruft patterns
	echo -e "${YELLOW}2️⃣  Checking for cruft patterns...${NC}"
	local cruft=$(git log --all --format='%s' | grep -E -i "^(wip|tmp|temp|test|asdf|fix typo|fix lint)$" || true)

	if [ -n "$cruft" ]; then
		echo -e "${RED}   ❌ Found cruft commits:${NC}"
		echo "$cruft" | sed 's/^/      /'
		issues=$((issues + 1))
	else
		echo -e "${GREEN}   ✅ No cruft patterns detected${NC}"
	fi

	# 3. Check author normalization
	echo -e "${YELLOW}3️⃣  Checking author normalization...${NC}"
	local author_count=$(git log --all --format='%aN <%aE>' | sort -u | wc -l)
	echo "   → Unique authors: $author_count"

	local duplicate_authors=$(git log --all --format='%aN' | sort | uniq -d || true)
	if [ -n "$duplicate_authors" ]; then
		echo -e "${YELLOW}   ⚠️  Possible duplicate authors (different emails):${NC}"
		echo "$duplicate_authors" | sed 's/^/      /'
	fi

	# 4. Check for version-only commits
	echo -e "${YELLOW}4️⃣  Checking for bare version commits...${NC}"
	local version_only=$(git log --all --format='%s' | grep -E "^[0-9]+\.[0-9]+\.[0-9]+$" || true)

	if [ -n "$version_only" ]; then
		local count=$(echo "$version_only" | wc -l)
		echo -e "${YELLOW}   ⚠️  Found ${count} bare version commits${NC}"
		echo -e "${YELLOW}      (Should be: chore(release): bump version to X.Y.Z)${NC}"
		issues=$((issues + 1))
	else
		echo -e "${GREEN}   ✅ No bare version commits${NC}"
	fi

	# 5. Check working directory
	echo -e "${YELLOW}5️⃣  Checking working directory...${NC}"
	if git status --porcelain | grep -q .; then
		echo -e "${YELLOW}   ⚠️  Working directory has uncommitted changes${NC}"
		git status --porcelain | head -5 | sed 's/^/      /'
	else
		echo -e "${GREEN}   ✅ Working directory clean${NC}"
	fi

	# 6. Repository statistics
	echo -e "${YELLOW}6️⃣  Repository statistics...${NC}"
	local total_commits=$(git rev-list --all --count)
	local merge_commits=$(git log --all --merges --oneline | wc -l)
	local first_commit=$(git log --all --reverse --format='%h %s' | head -1)

	echo "   → Total commits: $total_commits"
	echo "   → Merge commits: $merge_commits"
	echo "   → First commit: $first_commit"

	# Summary
	echo ""
	if [ $issues -eq 0 ]; then
		echo -e "${GREEN}✅ ${repo_name}: PASSED (0 issues)${NC}"
	else
		echo -e "${YELLOW}⚠️  ${repo_name}: PASSED with warnings (${issues} issues)${NC}"
	fi
	echo ""

	cd "$WORKSPACE_ROOT"
}

# Generate comparison report
generate_comparison_report() {
	echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
	echo -e "${CYAN}║  Generating Comparison Report${NC}"
	echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
	echo ""

	local report_file="${WORKSPACE_ROOT}/git-cleanup-comparison.txt"

	cat >"$report_file" <<'EOF'
FLEXT Git History Cleanup - Before/After Comparison
====================================================

EOF

	# Find backup directory
	local backup_dir=$(ls -dt ~/flext-history-backup-* 2>/dev/null | head -1 || echo "")

	if [ -n "$backup_dir" ]; then
		echo "Backup found: $backup_dir" >>"$report_file"
		echo "" >>"$report_file"

		# Compare main repo
		local backup_commits=$(grep -c "^" "$backup_dir/flext/commit-history.txt" 2>/dev/null || echo "N/A")
		local current_commits=$(cd "$WORKSPACE_ROOT" && git rev-list --all --count)

		cat >>"$report_file" <<EOF
Main Repository:
  Before: $backup_commits commits
  After:  $current_commits commits
  Reduction: $((backup_commits - current_commits)) commits removed

EOF

		# Sample commit messages
		echo "Sample commit messages (first 10):" >>"$report_file"
		(cd "$WORKSPACE_ROOT" && git log --all --format='  - %s' | head -10) >>"$report_file"
		echo "" >>"$report_file"

		# Authors
		echo "Normalized authors:" >>"$report_file"
		(cd "$WORKSPACE_ROOT" && git log --all --format='  - %aN <%aE>' | sort -u) >>"$report_file"
		echo "" >>"$report_file"

	else
		echo "No backup directory found. Skipping comparison." >>"$report_file"
	fi

	echo -e "${GREEN}✅ Comparison report saved: ${report_file}${NC}"
	echo ""
	cat "$report_file"
}

# Main execution
main() {
	if [[ ${1:-} == "--all-repos" ]]; then
		echo -e "${YELLOW}Validating all repositories...${NC}"
		echo ""

		# Validate main repo
		validate_repo "$WORKSPACE_ROOT"

		# Validate submodules
		git submodule status | awk '{print $2}' | while read -r submodule; do
			if [ -d "${WORKSPACE_ROOT}/${submodule}/.git" ]; then
				validate_repo "${WORKSPACE_ROOT}/${submodule}"
			fi
		done

		# Generate comparison report
		generate_comparison_report

	else
		# Validate only current repo
		validate_repo "$WORKSPACE_ROOT"
	fi

	echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
	echo -e "${GREEN}║  ✅ VALIDATION COMPLETE${NC}"
	echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
}

main "$@"
