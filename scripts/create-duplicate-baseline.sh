#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-architecture/SKILL.md
# =============================================================================
# FLEXT Duplicate Code Baseline Generator
# =============================================================================
# Creates a baseline of duplicate code pair counts for all FLEXT projects.
# Used by the duplicate-code-detector hook to block edits that increase duplication.
#
# Usage: ./create-duplicate-baseline.sh [--update PROJECT_NAME]
# =============================================================================

set -euo pipefail

FLEXT_DIR="${HOME}/flext"
BASELINE_FILE="${FLEXT_DIR}/.duplicate-code-baseline"
# Read threshold from constants (aggressive: 0.65)
SIMILARITY_THRESHOLD="0.65"
MIN_FILE_SIZE="100"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Get duplicate pair count for a project using Python
get_duplicate_count() {
	local project_path="$1"
	local src_dir="${project_path}/src"

	if [[ ! -d $src_dir ]]; then
		echo "0"
		return
	fi

	# Use Python for accurate line-based comparison
	python3 <<EOF
from pathlib import Path

src_dir = Path("$src_dir")
threshold = $SIMILARITY_THRESHOLD
min_size = $MIN_FILE_SIZE

# Collect Python files
files = {}
for py_file in src_dir.rglob("*.py"):
    if "__pycache__" in str(py_file) or ".venv" in str(py_file):
        continue
    try:
        content = py_file.read_text(encoding="utf-8")
        if len(content.strip()) > min_size:
            files[py_file] = set(content.splitlines())
    except Exception:
        continue

# Count duplicate pairs
count = 0
file_list = list(files.keys())
for i, f1 in enumerate(file_list):
    for f2 in file_list[i+1:]:
        lines1, lines2 = files[f1], files[f2]
        if lines1 and lines2:
            shared = len(lines1 & lines2)
            total = max(len(lines1), len(lines2))
            if shared / total > threshold:
                count += 1

print(count)
EOF
}

# Update single project baseline
update_project() {
	local project_name="$1"
	local project_path="${FLEXT_DIR}/${project_name}"

	if [[ ! -d $project_path ]]; then
		log_warning "Project not found: $project_name"
		return 1
	fi

	local count
	count=$(get_duplicate_count "$project_path")

	# Update or add entry in baseline file
	if grep -q "^${project_name}:" "$BASELINE_FILE" 2>/dev/null; then
		sed -i "s/^${project_name}:.*/${project_name}:${count}/" "$BASELINE_FILE"
	else
		echo "${project_name}:${count}" >>"$BASELINE_FILE"
	fi

	log_success "${project_name}: ${count} duplicate pairs"
}

# Generate full baseline
generate_baseline() {
	log_info "Generating duplicate code baseline for all FLEXT projects..."
	echo "# FLEXT Duplicate Code Baseline - $(date)" >"$BASELINE_FILE"
	echo "# Format: project_name:duplicate_pair_count" >>"$BASELINE_FILE"
	echo "# Threshold: ${SIMILARITY_THRESHOLD} (${SIMILARITY_THRESHOLD}00% line similarity)" >>"$BASELINE_FILE"
	echo "" >>"$BASELINE_FILE"

	local total=0

	# Process all flext-* projects
	for project in "${FLEXT_DIR}"/flext-*/; do
		if [[ -d $project ]]; then
			local name
			name=$(basename "$project")
			local count
			count=$(get_duplicate_count "$project")
			echo "${name}:${count}" >>"$BASELINE_FILE"
			log_success "${name}: ${count}"
			total=$((total + count))
		fi
	done

	# Process client-a-oud-mig if exists
	if [[ -d "${FLEXT_DIR}/client-a-oud-mig" ]]; then
		local count
		count=$(get_duplicate_count "${FLEXT_DIR}/client-a-oud-mig")
		echo "client-a-oud-mig:${count}" >>"$BASELINE_FILE"
		log_success "client-a-oud-mig: ${count}"
		total=$((total + count))
	fi

	echo ""
	log_info "Total duplicate pairs across all projects: ${total}"
	log_success "Baseline saved to: ${BASELINE_FILE}"
}

# Main
case "${1:-}" in
--update)
	if [[ -z ${2:-} ]]; then
		echo "Usage: $0 --update PROJECT_NAME"
		exit 1
	fi
	update_project "$2"
	;;
--help | -h)
	echo "Usage: $0 [--update PROJECT_NAME]"
	echo ""
	echo "Options:"
	echo "  --update PROJECT_NAME  Update baseline for a specific project"
	echo "  --help, -h             Show this help"
	echo ""
	echo "Without options, generates baseline for all FLEXT projects."
	echo ""
	echo "Configuration:"
	echo "  SIMILARITY_THRESHOLD: ${SIMILARITY_THRESHOLD} (80% line overlap)"
	echo "  MIN_FILE_SIZE: ${MIN_FILE_SIZE} characters"
	;;
*)
	generate_baseline
	;;
esac
