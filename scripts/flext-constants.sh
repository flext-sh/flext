#!/bin/bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# FLEXT Constants Quality Assurance Script v7.0.0
# Ultra-thin wrapper around flext-quality

set -euo pipefail

readonly SCRIPT_NAME="flext-constants.sh"
readonly SCRIPT_VERSION="7.0.0"
readonly FLEXT_QUALITY_CMD="python -m flext_quality"

# Colors
readonly RED='[0;31m'
readonly GREEN='[0;32m'
readonly YELLOW='[1;33m'
readonly BLUE='[0;34m'
readonly NC='[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1" >&2; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1" >&2; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

show_help() {
	cat <<EOF
FLEXT Constants Quality Assurance v$SCRIPT_VERSION
🚀 Fully automated constants validation for FLEXT projects.

USAGE: $SCRIPT_NAME [project] [options]

MODES:
    AUTO (default)  - Detect project and apply fixes automatically
    --check         - Analyze only (safe mode)
    --report        - Generate detailed reports only

OPTIONS:
    --dry-run       - Show what would be fixed without applying
    --force         - Apply fixes without confirmation
    --quiet         - Minimal output
    --help          - Show this help

EXAMPLES:
    $SCRIPT_NAME                    # Auto-detect and fix current project
    $SCRIPT_NAME flext-core         # Auto-fix specific project
    $SCRIPT_NAME --dry-run          # Preview changes
    $SCRIPT_NAME --report           # Generate reports

EOF
}

# Auto-detect FLEXT project
detect_flext_project() {
	local dir="$1"

	# Check if it's a FLEXT project by looking for common indicators
	if [[ -f "$dir/pyproject.toml" ]] && grep -q "flext" "$dir/pyproject.toml" 2>/dev/null; then
		echo "detected"
		return 0
	fi

	# Check for flext-* directories
	if [[ -d "$dir/flext-core" ]] || [[ -d "$dir/flext-cli" ]] || [[ -d "$dir/flext-quality" ]]; then
		echo "workspace"
		return 0
	fi

	# Check for src/flext_* structure
	if [[ -d "$dir/src" ]] && ls "$dir/src" | grep -q "^flext" 2>/dev/null; then
		echo "detected"
		return 0
	fi

	echo "unknown"
	return 1
}

# Auto mode - detect and fix automatically
run_auto_mode() {
	local target_project="$1"
	local dry_run="$2"
	local force="$3"
	local quiet="$4"

	if [[ $quiet != "true" ]]; then
		log_info "🔍 Analyzing project: $target_project"
	fi

	# Run analysis first
	if [[ $dry_run == "true" ]]; then
		if [[ $quiet != "true" ]]; then
			log_info "📋 Running analysis in dry-run mode..."
		fi
		exec $FLEXT_QUALITY_CMD analyze "$target_project" --format table
	else
		if [[ $quiet != "true" ]]; then
			log_info "🔧 Running full analysis and applying safe fixes..."
		fi
		exec $FLEXT_QUALITY_CMD analyze "$target_project" --format table
	fi
}

main() {
	local target_project="."
	local command="auto"
	local dry_run="false"
	local force="false"
	local quiet="false"

	# Parse arguments with enhanced options
	while [[ $# -gt 0 ]]; do
		case $1 in
		--help | -h)
			show_help
			exit 0
			;;
		--check)
			command="check"
			shift
			;;
		--report)
			command="report"
			shift
			;;
		--dry-run)
			dry_run="true"
			shift
			;;
		--force)
			force="true"
			shift
			;;
		--quiet)
			quiet="true"
			shift
			;;
		-*)
			log_error "Unknown option: $1"
			echo "Use '$SCRIPT_NAME --help' for usage information" >&2
			exit 1
			;;
		*)
			target_project="$1"
			shift
			;;
		esac
	done

	# Auto-detect project if using current directory
	if [[ $target_project == "." ]]; then
		local project_type
		project_type=$(detect_flext_project "$target_project")

		case "$project_type" in
		"detected")
			if [[ $quiet != "true" ]]; then
				log_info "✅ FLEXT project detected in current directory"
			fi
			;;
		"workspace")
			if [[ $quiet != "true" ]]; then
				log_info "🏗️  FLEXT workspace detected - analyzing all projects"
			fi
			;;
		*)
			if [[ $quiet != "true" ]]; then
				log_warning "⚠️  No FLEXT project detected in current directory"
				log_info "💡 Tip: Run from a FLEXT project directory or specify project path"
			fi
			;;
		esac
	fi

	# Validate target exists
	if [[ ! -d $target_project ]]; then
		log_error "Directory not found: $target_project"
		exit 1
	fi

	# Check flext-quality availability
	if ! python3 -c "import flext_quality" 2>/dev/null; then
		log_error "flext-quality not available"
		exit 1
	fi

	# Execute based on command
	case "$command" in
	"auto")
		run_auto_mode "$target_project" "$dry_run" "$force" "$quiet"
		;;
	"check")
		if [[ $quiet != "true" ]]; then
			log_info "🔍 Running constants analysis (safe mode)..."
		fi
		exec $FLEXT_QUALITY_CMD analyze "$target_project" --format table
		;;
	"report")
		if [[ $quiet != "true" ]]; then
			log_info "📊 Generating detailed reports..."
		fi
		exec $FLEXT_QUALITY_CMD analyze "$target_project" --format json
		;;
	esac
}

main "$@"
