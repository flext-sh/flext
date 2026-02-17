#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
# =============================================================================
# FLEXT Monorepo - Shared Functions Library
# =============================================================================
# Source this file in other scripts: source "$(dirname "$0")/lib/common.sh"
# =============================================================================

set -euo pipefail

# =============================================================================
# COLORS AND FORMATTING
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

# =============================================================================
# OUTPUT FUNCTIONS
# =============================================================================

info() {
	echo -e "${BLUE}i${NC} $1"
}

success() {
	echo -e "${GREEN}✓${NC} $1"
}

warn() {
	echo -e "${YELLOW}!${NC} $1"
}

error() {
	echo -e "${RED}x${NC} $1" >&2
}

header() {
	echo ""
	echo -e "${BOLD}${CYAN}$1${NC}"
	echo -e "${DIM}$(printf '%.0s─' $(seq 1 ${#1}))${NC}"
}

box() {
	local title="$1"
	local width=66
	local padding=$(((width - ${#title} - 2) / 2))
	echo "╔$(printf '%.0s═' $(seq 1 $width))╗"
	printf "║%*s%s%*s║\n" $padding "" "$title" $((width - padding - ${#title})) ""
	echo "╚$(printf '%.0s═' $(seq 1 $width))╝"
}

# =============================================================================
# INPUT FUNCTIONS
# =============================================================================

# Prompt with options - returns the selected option number
# Usage: choice=$(select_option "Question?" "Option 1" "Option 2" "Option 3")
select_option() {
	local prompt="$1"
	shift
	local options=("$@")
	local default=1

	echo ""
	echo -e "${CYAN}${prompt}${NC}"
	for i in "${!options[@]}"; do
		if [[ $i -eq 0 ]]; then
			echo -e "  ${BOLD}[$((i + 1))]${NC} ${options[$i]} ${DIM}(default)${NC}"
		else
			echo -e "  [$((i + 1))] ${options[$i]}"
		fi
	done

	local choice
	read -p "  Escolha [1]: " choice
	choice="${choice:-$default}"

	# Validate input
	if [[ ! $choice =~ ^[0-9]+$ ]] || [[ $choice -lt 1 ]] || [[ $choice -gt ${#options[@]} ]]; then
		choice=$default
	fi

	echo "$choice"
}

# Prompt for Y/n confirmation
# Usage: if confirm "Continue?"; then ...; fi
# Usage: if confirm "Continue?" "n"; then ...; fi  # default to no
confirm() {
	local prompt="$1"
	local default="${2:-Y}"
	local hint="Y/n"

	if [[ ${default,,} == "n" ]]; then
		hint="y/N"
	fi

	local answer
	read -p "$(echo -e "${CYAN}${prompt}${NC} [${hint}]: ")" answer
	answer="${answer:-$default}"

	[[ ${answer,,} =~ ^y ]]
}

# Prompt for a value with optional default
# Usage: value=$(prompt_value "Enter name" "default_value")
prompt_value() {
	local prompt="$1"
	local default="${2:-}"
	local value

	if [[ -n $default ]]; then
		read -p "$(echo -e "${CYAN}${prompt}${NC} [${default}]: ")" value
		echo "${value:-$default}"
	else
		read -p "$(echo -e "${CYAN}${prompt}${NC}: ")" value
		echo "$value"
	fi
}

# Prompt for a secret (no echo)
# Usage: password=$(prompt_secret "Enter password")
prompt_secret() {
	local prompt="$1"
	local value

	read -s -p "$(echo -e "${CYAN}${prompt}${NC}: ")" value
	echo "" # New line after hidden input
	echo "$value"
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

# Check if a command exists
# Usage: require_command "jq" "Install with: sudo apt install jq"
require_command() {
	local cmd="$1"
	local install_hint="${2:-}"

	if ! command -v "$cmd" &>/dev/null; then
		error "Required command not found: $cmd"
		if [[ -n $install_hint ]]; then
			echo -e "  ${DIM}$install_hint${NC}"
		fi
		exit 1
	fi
}

# Check if we're in the flext root directory
require_flext_root() {
	if [[ ! -f "pyproject.toml" ]] || [[ ! -d ".flext" ]]; then
		error "Not in FLEXT root directory"
		echo -e "  ${DIM}Run this command from ~/flext${NC}"
		exit 1
	fi
}

# Check if a project exists
project_exists() {
	local project="$1"
	[[ -d "./$project" ]]
}

# Check if a project is registered as external
is_external_project() {
	local project="$1"
	jq -e ".projects[\"$project\"]" .flext/external-projects.json &>/dev/null
}

# =============================================================================
# PROJECT MANAGEMENT FUNCTIONS
# =============================================================================

# Get the workspace root directory
get_workspace_root() {
	local dir="$PWD"
	while [[ $dir != "/" ]]; do
		if [[ -f "$dir/pyproject.toml" ]] && [[ -d "$dir/.flext" ]]; then
			echo "$dir"
			return 0
		fi
		dir="$(dirname "$dir")"
	done
	return 1
}

# List all projects (submodules + external)
list_all_projects() {
	local projects=()

	# Submodules from .gitmodules
	if [[ -f ".gitmodules" ]]; then
		while IFS= read -r line; do
			if [[ $line =~ path\ =\ (.+) ]]; then
				projects+=("${BASH_REMATCH[1]}")
			fi
		done <.gitmodules
	fi

	# External projects
	if [[ -f ".flext/external-projects.json" ]]; then
		local external
		external=$(jq -r '.projects | keys[]' .flext/external-projects.json 2>/dev/null || true)
		for p in $external; do
			projects+=("$p")
		done
	fi

	printf '%s\n' "${projects[@]}" | sort -u
}

# List only external projects
list_external_projects() {
	if [[ -f ".flext/external-projects.json" ]]; then
		jq -r '.projects | keys[]' .flext/external-projects.json 2>/dev/null || true
	fi
}

# Get project info from external-projects.json
get_project_info() {
	local project="$1"
	local field="$2"
	jq -r ".projects[\"$project\"].$field // empty" .flext/external-projects.json 2>/dev/null
}

# =============================================================================
# VERSION MANAGEMENT FUNCTIONS
# =============================================================================

# Get version from pyproject.toml
get_version() {
	local project_path="${1:-.}"
	local pyproject="$project_path/pyproject.toml"

	if [[ -f $pyproject ]]; then
		grep -E '^version\s*=' "$pyproject" | head -1 | sed 's/.*=\s*"\([^"]*\)".*/\1/'
	fi
}

# Bump version (major, minor, patch)
bump_version() {
	local version="$1"
	local bump_type="$2"

	IFS='.' read -r major minor patch <<<"$version"

	case "$bump_type" in
	major)
		echo "$((major + 1)).0.0"
		;;
	minor)
		echo "$major.$((minor + 1)).0"
		;;
	patch)
		echo "$major.$minor.$((patch + 1))"
		;;
	*)
		echo "$version"
		;;
	esac
}

# =============================================================================
# GIT FUNCTIONS
# =============================================================================

# Check if there are uncommitted changes
has_changes() {
	local path="${1:-.}"
	! git -C "$path" diff --quiet HEAD 2>/dev/null ||
		! git -C "$path" diff --cached --quiet 2>/dev/null ||
		[[ -n "$(git -C "$path" ls-files --others --exclude-standard 2>/dev/null)" ]]
}

# Get current branch
get_current_branch() {
	local path="${1:-.}"
	git -C "$path" rev-parse --abbrev-ref HEAD 2>/dev/null
}

# List projects with changes
list_changed_projects() {
	local projects
	projects=$(list_all_projects)

	for project in $projects; do
		if [[ -d $project ]] && has_changes "$project"; then
			echo "$project"
		fi
	done
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Run command with spinner
run_with_spinner() {
	local msg="$1"
	shift
	local cmd=("$@")

	local spin='-\|/'
	local i=0

	printf "${CYAN}%s${NC} " "$msg"

	"${cmd[@]}" &
	local pid=$!

	while kill -0 $pid 2>/dev/null; do
		i=$(((i + 1) % 4))
		printf "\r${CYAN}%s${NC} ${spin:i:1}" "$msg"
		sleep 0.1
	done

	wait $pid
	local status=$?

	if [[ $status -eq 0 ]]; then
		printf "\r${GREEN}✓${NC} %s\n" "$msg"
	else
		printf "\r${RED}x${NC} %s\n" "$msg"
	fi

	return $status
}

# Ensure jq is available (required for JSON operations)
ensure_jq() {
	require_command "jq" "Install with: sudo pacman -S jq (Arch) or sudo apt install jq (Ubuntu)"
}

# Ensure poetry is available
ensure_poetry() {
	require_command "poetry" "Install with: curl -sSL https://install.python-poetry.org | python3 -"
}

# =============================================================================
# FLEXT QUALITY INTEGRATION
# =============================================================================
# Shell wrappers for flext-quality Python library
# Provides: validation, backup, daemon health checks

# Count lint + type errors in a file
# Usage: errors=$(flext_count_errors "/path/to/file.py")
flext_count_errors() {
	local file="$1"
	python3 -c "
from flext_quality.tools.validation import FlextQualityValidationTools
v = FlextQualityValidationTools()
r = v.count_errors('$file')
print(r.value if r.is_success else -1)
" 2>/dev/null || echo "-1"
}

# Count only ruff errors in a file
# Usage: errors=$(flext_count_ruff_errors "/path/to/file.py")
flext_count_ruff_errors() {
	local file="$1"
	python3 -c "
from flext_quality.tools.validation import FlextQualityValidationTools
v = FlextQualityValidationTools()
r = v.count_ruff_errors('$file')
print(r.value if r.is_success else -1)
" 2>/dev/null || echo "-1"
}

# Count only mypy errors in a file
# Usage: errors=$(flext_count_mypy_errors "/path/to/file.py")
flext_count_mypy_errors() {
	local file="$1"
	python3 -c "
from flext_quality.tools.validation import FlextQualityValidationTools
v = FlextQualityValidationTools()
r = v.count_mypy_errors('$file')
print(r.value if r.is_success else -1)
" 2>/dev/null || echo "-1"
}

# Backup a file before modification
# Usage: backup_id=$(flext_backup "/path/to/file.py")
flext_backup() {
	local file="$1"
	python3 -c "
from flext_quality.tools.backup import BackupManager
b = BackupManager()
r = b.backup_file('$file')
print(r.value if r.is_success else 'ERROR')
" 2>/dev/null || echo "ERROR"
}

# Restore a file from backup
# Usage: result=$(flext_restore "backup-abc123")
flext_restore() {
	local backup_id="$1"
	python3 -c "
from flext_quality.tools.backup import BackupManager
b = BackupManager()
r = b.restore_file('$backup_id')
print('OK' if r.is_success else 'ERROR')
" 2>/dev/null || echo "ERROR"
}

# Check quality daemon status (ruff, mypy)
# Usage: status=$(flext_daemon_status) # Returns JSON
flext_daemon_status() {
	local workspace="${1:-$FLEXT_ROOT}"
	python3 -c "
import json
from flext_quality.tools.health import HealthCheckService
h = HealthCheckService('$workspace')
r = h.check_daemons()
print(json.dumps(r.value) if r.is_success else '{}')
" 2>/dev/null || echo "{}"
}

# =============================================================================
# INITIALIZATION
# =============================================================================

# Auto-detect workspace root if sourced from subdirectory
if [[ ${BASH_SOURCE[0]} != "${0}" ]]; then
	# Being sourced
	FLEXT_ROOT="${FLEXT_ROOT:-$(get_workspace_root 2>/dev/null || echo "$PWD")}"
	export FLEXT_ROOT
fi
