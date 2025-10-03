#!/bin/bash
#
# Git History Cruft Removal Script for FLEXT Workspace
#
# This script removes build artifacts, cache files, logs, and other cruft
# from git history across the main repository and all submodules.
#
# CRITICAL: This REWRITES git history - use with extreme caution
#
# Usage: ./git_cleanup_cruft_removal.sh [--test-mode]
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_MODE=false

# Parse arguments
if [ "${1:-}" = "--test-mode" ]; then
    TEST_MODE=true
fi

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  FLEXT Git History Cruft Removal                          ║${NC}"
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

if [ "$TEST_MODE" = true ]; then
    echo -e "${GREEN}🧪 TEST MODE: Creating temporary repository for testing${NC}"
    TEST_DIR="/tmp/flext-cruft-test-$(date +%Y%m%d-%H%M%S)"
    echo -e "${GREEN}   Test location: ${TEST_DIR}${NC}"
    echo ""
else
    echo -e "${RED}⚠️  PRODUCTION MODE: This will PERMANENTLY modify git history${NC}"
    echo -e "${RED}   This operation CANNOT be undone without backups!${NC}"
    echo ""
    read -p "Are you absolutely sure you want to proceed? (yes/NO): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Aborted by user"
        exit 0
    fi
fi

# Define cruft patterns to remove from history
declare -A CRUFT_PATTERNS=(
    # Build artifacts
    ["pyc_files"]="*.pyc"
    ["pycache_dirs"]="__pycache__/"
    ["dist_dirs"]="dist/"
    ["build_dirs"]="build/"
    ["egg_info"]="*.egg-info/"

    # Cache directories
    ["ruff_cache"]=".ruff_cache/"
    ["mypy_cache"]=".mypy_cache/"
    ["pytest_cache"]=".pytest_cache/"
    ["serena_cache"]=".serena/cache/"

    # Coverage reports
    ["coverage_files"]=".coverage"
    ["htmlcov_dirs"]="htmlcov/"
    ["tox_dirs"]=".tox/"

    # Log files
    ["log_files"]="*.log"
    ["meltano_logs"]=".meltano/logs/"

    # Backup files
    ["backup_files"]="*.backup"
    ["bak_files"]="*.bak"
    ["orig_files"]="*.orig"
    ["temp_files"]="*~"
    ["swp_files"]=".*.swp"

    # OS-specific
    ["ds_store"]=".DS_Store"
    ["thumbs_db"]="Thumbs.db"

    # Empty directories
    ["benchmarks"]=".benchmarks/"

    # AI/IDE Configuration and Reports
    ["claude_md"]="CLAUDE*.md"
    ["cursor_dir"]=".cursor/"
    ["serena_dir"]=".serena/"
    ["vscode_dir"]=".vscode/"
    ["idea_dir"]=".idea/"
    ["ai_reports"]="*_report.md"
    ["ai_analysis"]="*_analysis.md"
    ["ai_summary"]="*_summary.md"
)

# Function to create cruft removal script for git-filter-repo
create_cruft_paths_file() {
    local paths_file="$1"

    echo "# Cruft patterns to remove from git history" > "$paths_file"
    echo "# Generated: $(date)" >> "$paths_file"
    echo "" >> "$paths_file"

    for pattern in "${CRUFT_PATTERNS[@]}"; do
        # git-filter-repo uses glob patterns
        echo "glob:$pattern" >> "$paths_file"
    done

    echo "" >> "$paths_file"
    echo "# Generated $(wc -l < "$paths_file") patterns for removal" >> "$paths_file"
}

# Function to analyze cruft in repository
analyze_cruft() {
    local repo_path="$1"

    echo -e "${BLUE}📊 Analyzing cruft in: $repo_path${NC}"

    cd "$repo_path"

    local total_files=0
    local total_size=0

    for name in "${!CRUFT_PATTERNS[@]}"; do
        local pattern="${CRUFT_PATTERNS[$name]}"
        local clean_pattern="${pattern//\*/}"

        # Find matching files
        local count=0
        local size=0

        if [[ "$pattern" == *"/" ]]; then
            # Directory pattern
            count=$(find . -type d -name "${pattern%/}" 2>/dev/null | wc -l)
            size=$(find . -type d -name "${pattern%/}" -exec du -sb {} + 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
        else
            # File pattern
            count=$(find . -type f -name "$pattern" 2>/dev/null | wc -l)
            size=$(find . -type f -name "$pattern" -exec du -sb {} + 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
        fi

        if [ "$count" -gt 0 ]; then
            local size_mb=$(echo "scale=2; $size / 1024 / 1024" | bc)
            echo "  $name: $count items (${size_mb}MB)"
            total_files=$((total_files + count))
            total_size=$((total_size + size))
        fi
    done

    local total_mb=$(echo "scale=2; $total_size / 1024 / 1024" | bc)
    echo -e "${YELLOW}  Total cruft: $total_files items (${total_mb}MB)${NC}"
}

# Function to remove cruft from a repository
remove_cruft_from_repo() {
    local repo_path="$1"
    local repo_name="$(basename "$repo_path")"

    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  Processing: $repo_name${NC}"
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""

    cd "$repo_path"

    # Check if it's a git repository
    if [ ! -d ".git" ]; then
        echo -e "${YELLOW}⚠️  Not a git repository, skipping${NC}"
        return
    fi

    # Analyze cruft before removal
    analyze_cruft "$repo_path"

    # Create paths file for git-filter-repo
    local paths_file="$repo_path/.git/cruft-paths.txt"
    create_cruft_paths_file "$paths_file"

    echo ""
    echo -e "${BLUE}📋 Cruft patterns file created: $paths_file${NC}"
    echo "   Patterns: $(grep -c "^glob:" "$paths_file")"
    echo ""

    # Create backup tag
    local backup_tag="pre-cruft-cleanup-$(date +%Y%m%d-%H%M%S)"
    echo -e "${BLUE}🏷️  Creating backup tag: $backup_tag${NC}"
    git tag "$backup_tag" 2>/dev/null || echo "   Tag already exists, skipping"

    # Run git-filter-repo to remove cruft
    echo ""
    echo -e "${BLUE}🔧 Removing cruft from git history...${NC}"

    if git filter-repo --force \
        --invert-paths \
        --paths-from-file "$paths_file" \
        --mailmap ./.mailmap 2>&1; then

        echo -e "${GREEN}   ✅ Cruft removal completed successfully${NC}"
    else
        echo -e "${RED}   ❌ Cruft removal failed${NC}"
        return 1
    fi

    # Show size reduction
    echo ""
    echo -e "${BLUE}📊 Repository statistics after cleanup:${NC}"
    git count-objects -vH
}

# Main execution
main() {
    if [ "$TEST_MODE" = true ]; then
        # Create test clone
        echo -e "${BLUE}📦 Creating test repository...${NC}"
        git clone "$WORKSPACE_ROOT" "$TEST_DIR"
        cd "$TEST_DIR"

        # Copy scripts
        cp -r "$SCRIPT_DIR" "$TEST_DIR/scripts"

        WORKSPACE_ROOT="$TEST_DIR"
    fi

    cd "$WORKSPACE_ROOT"

    echo -e "${BLUE}🔍 Discovering repositories...${NC}"
    echo ""

    # Process main repository
    echo -e "${CYAN}Main Repository:${NC} $WORKSPACE_ROOT"
    remove_cruft_from_repo "$WORKSPACE_ROOT"

    # Process all submodules
    echo ""
    echo -e "${BLUE}📦 Processing submodules...${NC}"

    if [ -f ".gitmodules" ]; then
        git submodule foreach --quiet 'echo "$path"' | while read -r submodule; do
            local submodule_path="$WORKSPACE_ROOT/$submodule"
            if [ -d "$submodule_path" ]; then
                remove_cruft_from_repo "$submodule_path"
            fi
        done
    fi

    # Final summary
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ CRUFT REMOVAL COMPLETE${NC}"
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""

    if [ "$TEST_MODE" = true ]; then
        echo "Test repository location: ${TEST_DIR}"
        echo ""
        echo "To inspect results:"
        echo "  cd ${TEST_DIR}"
        echo "  git log --oneline | head -20"
        echo "  git count-objects -vH"
        echo ""
        echo "To apply to real repository:"
        echo "  ./scripts/git_cleanup_cruft_removal.sh"
        echo ""
        echo "To clean up test directory:"
        echo "  rm -rf ${TEST_DIR}"
    else
        echo "Backup tags created for recovery"
        echo ""
        echo "Repository size reduction:"
        cd "$WORKSPACE_ROOT"
        git count-objects -vH
        echo ""
        echo "⚠️  Important next steps:"
        echo "  1. Review changes: git log --oneline | head -20"
        echo "  2. Test repository functionality"
        echo "  3. Force push to remote (if needed):"
        echo "     git push origin --force --all"
        echo "     git push origin --force --tags"
        echo ""
        echo "To recover (if needed):"
        echo "  git reset --hard pre-cruft-cleanup-YYYYMMDD-HHMMSS"
    fi
}

# Run main function
main
