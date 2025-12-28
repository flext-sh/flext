#!/bin/bash
# =============================================================================
# FLEXT Dead Code Baseline Generator
# =============================================================================
# Creates a baseline of dead code counts for all FLEXT projects.
# Used by the dead-code-detector hook to block edits that increase dead code.
#
# Usage: ./create-dead-code-baseline.sh [--update PROJECT_NAME]
# =============================================================================

set -euo pipefail

FLEXT_DIR="${HOME}/flext"
BASELINE_FILE="${FLEXT_DIR}/.dead-code-baseline"
VULTURE_OPTS="--min-confidence 80 --exclude tests,examples"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Get dead code count for a project
get_dead_code_count() {
    local project_path="$1"
    local src_dir="${project_path}/src"

    if [[ ! -d "$src_dir" ]]; then
        echo "0"
        return
    fi

    cd "$project_path" || { echo "0"; return; }
    local count
    count=$(poetry run vulture "$src_dir" $VULTURE_OPTS 2>/dev/null | wc -l | tr -d '[:space:]')
    # Ensure we return a valid number
    if [[ -z "$count" || ! "$count" =~ ^[0-9]+$ ]]; then
        count=0
    fi
    echo "$count"
}

# Update single project baseline
update_project() {
    local project_name="$1"
    local project_path="${FLEXT_DIR}/${project_name}"

    if [[ ! -d "$project_path" ]]; then
        log_warning "Project not found: $project_name"
        return 1
    fi

    local count
    count=$(get_dead_code_count "$project_path")

    # Update or add entry in baseline file
    if grep -q "^${project_name}:" "$BASELINE_FILE" 2>/dev/null; then
        sed -i "s/^${project_name}:.*/${project_name}:${count}/" "$BASELINE_FILE"
    else
        echo "${project_name}:${count}" >> "$BASELINE_FILE"
    fi

    log_success "${project_name}: ${count} dead code items"
}

# Generate full baseline
generate_baseline() {
    log_info "Generating dead code baseline for all FLEXT projects..."
    echo "# FLEXT Dead Code Baseline - $(date)" > "$BASELINE_FILE"
    echo "# Format: project_name:dead_code_count" >> "$BASELINE_FILE"
    echo "" >> "$BASELINE_FILE"

    local total=0

    # Process all flext-* projects
    for project in "${FLEXT_DIR}"/flext-*/; do
        if [[ -d "$project" ]]; then
            local name
            name=$(basename "$project")
            local count
            count=$(get_dead_code_count "$project")
            echo "${name}:${count}" >> "$BASELINE_FILE"
            log_success "${name}: ${count}"
            total=$((total + count))
        fi
    done

    # Process client-a-oud-mig if exists
    if [[ -d "${FLEXT_DIR}/client-a-oud-mig" ]]; then
        local count
        count=$(get_dead_code_count "${FLEXT_DIR}/client-a-oud-mig")
        echo "client-a-oud-mig:${count}" >> "$BASELINE_FILE"
        log_success "client-a-oud-mig: ${count}"
        total=$((total + count))
    fi

    echo ""
    log_info "Total dead code items across all projects: ${total}"
    log_success "Baseline saved to: ${BASELINE_FILE}"
}

# Main
case "${1:-}" in
    --update)
        if [[ -z "${2:-}" ]]; then
            echo "Usage: $0 --update PROJECT_NAME"
            exit 1
        fi
        update_project "$2"
        ;;
    --help|-h)
        echo "Usage: $0 [--update PROJECT_NAME]"
        echo ""
        echo "Options:"
        echo "  --update PROJECT_NAME  Update baseline for a specific project"
        echo "  --help, -h             Show this help"
        echo ""
        echo "Without options, generates baseline for all FLEXT projects."
        ;;
    *)
        generate_baseline
        ;;
esac
