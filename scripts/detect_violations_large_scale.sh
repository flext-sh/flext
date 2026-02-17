#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-validation/SKILL.md
# detect_violations_large_scale.sh - Workspace-wide FLEXT violation detection

set -euo pipefail

set -uo pipefail # Don't exit on first error in pipes

# Configuration
WORKSPACE_ROOT="${WORKSPACE_ROOT:-/home/marlonsc/flext}"
OUTPUT_FORMAT="${1:-json}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Projects to scan
PROJECTS=(
	"flext-core"
	"flext-api"
	"flext-ldif"
	"flext-ldap"
	"flext-cli"
)

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Output files
OUTPUT_JSON="violations_${TIMESTAMP}.json"
OUTPUT_HUMAN="violations_${TIMESTAMP}.txt"

# Counters
TOTAL_RUFF=0
TOTAL_MYPY=0
TOTAL_ARCH=0

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[⚠]${NC} $1"; }

# ============================================================================
# RUFF VIOLATION DETECTION
# ============================================================================

detect_ruff_violations() {
	local project="$1"
	local project_path="$WORKSPACE_ROOT/$project"

	if [[ ! -d $project_path ]]; then
		return
	fi

	log_info "Scanning ruff violations in $project..."

	# Run ruff check (ignore errors)
	if ruff check "$project_path/src" 2>/dev/null | grep -E "[E0-9]|[W0-9]|[F0-9]" | while read line; do
		echo "$project|$line" >>"$TEMP_DIR/ruff_violations.txt"
		((TOTAL_RUFF++))
	done; then
		true
	fi
}

# ============================================================================
# MYPY VIOLATION DETECTION
# ============================================================================

detect_mypy_violations() {
	local project="$1"
	local project_path="$WORKSPACE_ROOT/$project"

	if [[ ! -d $project_path ]]; then
		return
	fi

	log_info "Scanning mypy violations in $project..."

	# Run mypy from project directory
	(cd "$project_path" && PYTHONPATH=src mypy --strict src/ 2>&1 || true) | while read line; do
		if [[ $line =~ error: ]]; then
			echo "$project|$line" >>"$TEMP_DIR/mypy_violations.txt"
			((TOTAL_MYPY++))
		fi
	done
}

# ============================================================================
# ARCHITECTURE VIOLATION DETECTION
# ============================================================================

detect_architecture_violations() {
	local project="$1"
	local project_path="$WORKSPACE_ROOT/$project"

	if [[ ! -d $project_path ]]; then
		return
	fi

	log_info "Checking architecture violations in $project..."

	# Check Tier 0 files don't import from higher tiers
	local foundation_files=(
		"src/$project/models.py"
		"src/$project/protocols.py"
		"src/$project/utilities.py"
		"src/$project/constants.py"
		"src/$project/typings.py"
	)

	for file in "${foundation_files[@]}"; do
		local full_path="$project_path/$file"
		if [[ -f $full_path ]]; then
			if grep -qE "(from flext_.*\.(services|api|servers) import)" "$full_path" 2>/dev/null; then
				local count=$(grep -cE "(from flext_.*\.(services|api|servers) import)" "$full_path" || echo 0)
				echo "$project|$file|$count violations" >>"$TEMP_DIR/arch_violations.txt"
				TOTAL_ARCH=$((TOTAL_ARCH + count))
			fi
		fi
	done
}

# ============================================================================
# REPORTING
# ============================================================================

generate_human_report() {
	local txt_file="$OUTPUT_HUMAN"

	{
		echo ""
		echo "╔════════════════════════════════════════════════════════════════════════╗"
		echo "║          FLEXT WORKSPACE VIOLATION DETECTION REPORT                    ║"
		echo "╚════════════════════════════════════════════════════════════════════════╝"
		echo ""
		echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
		echo ""
		echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
		echo "📊 SUMMARY"
		echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
		echo ""
		echo "Total Violations:      $((TOTAL_RUFF + TOTAL_MYPY + TOTAL_ARCH))"
		echo "  • Ruff:             $TOTAL_RUFF"
		echo "  • MyPy:             $TOTAL_MYPY"
		echo "  • Architecture:     $TOTAL_ARCH"
		echo ""

		if [[ $TOTAL_RUFF -gt 0 ]]; then
			echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
			echo "🔴 RUFF VIOLATIONS ($TOTAL_RUFF)"
			echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
			if [[ -f "$TEMP_DIR/ruff_violations.txt" ]]; then
				head -20 "$TEMP_DIR/ruff_violations.txt" | cut -d'|' -f1-2 | sort | uniq -c
			fi
			echo ""
		fi

		if [[ $TOTAL_MYPY -gt 0 ]]; then
			echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
			echo "🟠 MYPY VIOLATIONS ($TOTAL_MYPY)"
			echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
			if [[ -f "$TEMP_DIR/mypy_violations.txt" ]]; then
				head -20 "$TEMP_DIR/mypy_violations.txt" | sed 's/|/: /g'
			fi
			echo ""
		fi

		if [[ $TOTAL_ARCH -gt 0 ]]; then
			echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
			echo "🟡 ARCHITECTURE VIOLATIONS ($TOTAL_ARCH)"
			echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
			if [[ -f "$TEMP_DIR/arch_violations.txt" ]]; then
				cat "$TEMP_DIR/arch_violations.txt"
			fi
			echo ""
		fi

		echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
		echo "✅ REMEDIATION STEPS"
		echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
		echo ""
		echo "For Ruff/Code Quality Issues:"
		echo "  1. Use: ./scripts/pre_edit_validate.sh <file_path>"
		echo "  2. Make your edits"
		echo "  3. Run: ./scripts/post_edit_validate.sh <backup_id> <file_path>"
		echo ""
		echo "For MyPy/Type Safety Issues:"
		echo "  • Add proper type annotations (no Any, no cast(), no TYPE_CHECKING)"
		echo "  • Use type aliases from flext_core: c.*, t.*, p.*, m.*, u.*"
		echo ""
		echo "For Architecture Issues:"
		echo "  • Foundation tier (models, protocols, utilities, constants, typings)"
		echo "  • Cannot import from services, api, or servers modules"
		echo ""
		echo ""

	} >"$txt_file"

	log_success "Report: $txt_file"
}

# ============================================================================
# MAIN
# ============================================================================

main() {
	echo ""
	log_info "Starting workspace-wide violation detection..."
	echo ""

	for project in "${PROJECTS[@]}"; do
		detect_ruff_violations "$project"
		detect_mypy_violations "$project"
		detect_architecture_violations "$project"
	done

	echo ""
	log_success "Detection complete"
	echo "  • Ruff violations: $TOTAL_RUFF"
	echo "  • MyPy violations: $TOTAL_MYPY"
	echo "  • Architecture violations: $TOTAL_ARCH"
	echo ""

	case "$OUTPUT_FORMAT" in
	human | txt) generate_human_report ;;
	json)
		echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"ruff\": $TOTAL_RUFF, \"mypy\": $TOTAL_MYPY, \"architecture\": $TOTAL_ARCH}" >"$OUTPUT_JSON"
		log_success "Report: $OUTPUT_JSON"
		;;
	*) generate_human_report ;;
	esac

	echo ""
}

main "$@"
