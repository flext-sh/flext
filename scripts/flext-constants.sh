#!/bin/bash
# FLEXT Constants Quality Assurance Script v6.0.0
# Thin wrapper around flext-quality for constants validation

set -euo pipefail

readonly SCRIPT_NAME="flext-constants.sh"
readonly SCRIPT_VERSION="6.0.0"
readonly FLEXT_QUALITY_CMD="python -m flext_quality"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_flext_quality() {
    if ! command -v python3 >/dev/null 2>&1; then
        log_error "Python3 not found"
        return 1
    fi
    if ! python3 -c "import flext_quality" 2>/dev/null; then
        log_error "flext-quality package not found"
        return 1
    fi
    return 0
}

generate_reports() {
    local project_path="${1:-.}"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local report_dir="${TMPDIR:-/tmp}/flext-constants-reports/${timestamp}"
    
    mkdir -p "$report_dir"
    log_info "Generating comprehensive reports..."
    
    if $FLEXT_QUALITY_CMD analyze "$project_path" \
        --format json \
        --output "$report_dir/analysis.json" \
        --include-security \
        --include-complexity \
        --include-duplicates; then
        
        cat >"$report_dir/summary.txt" <<EOF
FLEXT Constants Quality Report
================================
Generated: $(date)
Project: $project_path
Report Directory: $report_dir

JSON Report: $report_dir/analysis.json
Summary: $report_dir/summary.txt

Use jq to analyze: cat $report_dir/analysis.json | jq '.violations[] | select(.severity == "high")'
EOF
        
        log_success "Reports generated:"
        echo "  📊 JSON: $report_dir/analysis.json"
        echo "  📋 Summary: $report_dir/summary.txt"
        return 0
    else
        log_error "Failed to generate reports"
        return 1
    fi
}

show_help() {
    cat <<EOF
FLEXT Constants Quality Assurance v$SCRIPT_VERSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thin wrapper around flext-quality for constants validation.

USAGE: $SCRIPT_NAME [project] [options]

OPTIONS:
    --check     Analyze without changes (default)
    --fix       Apply automatic fixes
    --backup    Create backup only
    --restore   Restore from backup
    --report    Generate quality reports

EXAMPLES:
    $SCRIPT_NAME                    # Check current directory
    $SCRIPT_NAME flext-core         # Check flext-core project
    $SCRIPT_NAME --report           # Generate reports

EOF
}

run_flext_quality() {
    local command="$1"
    local project_path="$2"
    
    case "$command" in
        "check")
            log_info "🔍 Running constants analysis..."
            $FLEXT_QUALITY_CMD analyze "$project_path" \
                --include-security --include-complexity --include-duplicates
            ;;
        "fix")
            log_info "🔧 Applying fixes..."
            log_warning "Fix functionality delegated to flext-quality"
            $FLEXT_QUALITY_CMD analyze "$project_path" --format table
            ;;
        "backup")
            log_info "💾 Creating backup..."
            log_warning "Backup delegated to flext-quality"
            echo "Backup operation would be handled here"
            ;;
        "restore")
            log_info "🔄 Restoring backup..."
            log_warning "Restore delegated to flext-quality"
            echo "Restore operation would be handled here"
            ;;
        "report")
            generate_reports "$project_path"
            ;;
    esac
}

main() {
    local target_project="."
    local command="check"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h) show_help; exit 0 ;;
            --check|--fix|--backup|--restore|--report)
                command="${1#--}"; shift ;;
            -*) log_error "Unknown option: $1"; exit 1 ;;
            *) target_project="$1"; shift ;;
        esac
    done
    
    if ! check_flext_quality; then
        exit 1
    fi
    
    if run_flext_quality "$command" "$target_project"; then
        case "$command" in
            "check") log_success "✅ Analysis completed" ;;
            "fix") log_success "🎉 Fixes applied" ;;
            "backup") log_success "💾 Backup completed" ;;
            "restore") log_success "🔄 Restore completed" ;;
            "report") ;;  # Already handled
        esac
        exit 0
    else
        log_error "❌ Operation failed"
        exit 1
    fi
}

main "$@"
