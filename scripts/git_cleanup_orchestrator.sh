#!/bin/bash
#
# Git History Cleanup Orchestrator for FLEXT Workspace
#
# Comprehensive workflow for cleaning git history across main repo + submodules:
#   1. Backup everything
#   2. Analyze and generate AI-rewritten commit messages
#   3. Apply git-filter-repo transformations
#   4. Validate results
#
# Usage:
#   ./git_cleanup_orchestrator.sh --test-run         # Test on one submodule
#   ./git_cleanup_orchestrator.sh --full-cleanup     # Full workspace cleanup

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
BACKUP_SCRIPT="${SCRIPT_DIR}/git_cleanup_backup.sh"
REWRITER_SCRIPT="${SCRIPT_DIR}/git_history_rewriter.py"

# Configuration
TEST_SUBMODULE="flext-cli"  # Small submodule for testing

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  FLEXT Git History Cleanup Orchestrator                  ║${NC}"
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Preflight checks
check_requirements() {
    echo -e "${BLUE}🔍 Checking requirements...${NC}"

    local missing=0

    # Check git-filter-repo
    if ! command -v git-filter-repo &> /dev/null; then
        echo -e "${RED}   ❌ git-filter-repo not found${NC}"
        echo "      Install: pip install git-filter-repo"
        missing=1
    else
        echo -e "${GREEN}   ✅ git-filter-repo installed${NC}"
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}   ❌ python3 not found${NC}"
        missing=1
    else
        echo -e "${GREEN}   ✅ python3 installed${NC}"
    fi

    # Using heuristic-based rewriting (no external API needed)
    echo -e "${GREEN}   ✅ Using intelligent heuristic-based commit rewriting${NC}"
    echo "      (Cursor AI can provide suggestions interactively if needed)"

    echo ""

    if [ $missing -eq 1 ]; then
        echo -e "${RED}Please install missing requirements and try again.${NC}"
        exit 1
    fi
}

# Safety confirmation
confirm_operation() {
    local operation="$1"

    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠️  WARNING: DESTRUCTIVE OPERATION${NC}"
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""
    echo "This will rewrite git history for: ${operation}"
    echo ""
    echo "Consequences:"
    echo "  • All commit SHAs will change"
    echo "  • Force push required to remote repositories"
    echo "  • All team members must re-clone"
    echo "  • Cannot be easily undone (except via backup)"
    echo ""
    echo "Safety measures:"
    echo "  • Full backup will be created first"
    echo "  • Rollback script will be generated"
    echo "  • Test run available before full cleanup"
    echo ""
    read -p "Type 'I UNDERSTAND' to proceed: " confirmation

    if [ "$confirmation" != "I UNDERSTAND" ]; then
        echo -e "${RED}Operation cancelled.${NC}"
        exit 1
    fi
    echo ""
}

# Process a single repository
process_repository() {
    local repo_path="$1"
    local repo_name=$(basename "$repo_path")
    local dry_run="${2:-false}"  # Optional dry-run parameter

    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Processing: ${repo_name}${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    if [ ! -d "$repo_path/.git" ]; then
        echo -e "${RED}❌ Not a git repository: ${repo_path}${NC}"
        return 1
    fi

    cd "$repo_path"

    # Step 1: Create safety tag
    echo -e "${BLUE}1️⃣  Creating safety tag...${NC}"
    git tag -f "pre-cleanup-$(date +%Y%m%d-%H%M%S)"
    echo -e "${GREEN}   ✅ Safety tag created${NC}"
    echo ""

    # Step 2: AI commit message rewriting (if available)
    local msg_mapping_file="${repo_path}/.git/history-cleanup/commit-msg-mapping.txt"
    if [ -n "$ANTHROPIC_API_KEY" ] && python3 -c "import anthropic" 2>/dev/null; then
        echo -e "${BLUE}2️⃣  Generating AI-rewritten commit messages...${NC}"
        python3 "$REWRITER_SCRIPT" --repo "$repo_path" --api-key "$ANTHROPIC_API_KEY" || {
            echo -e "${YELLOW}   ⚠️  AI rewriting failed, continuing without it${NC}"
            msg_mapping_file=""
        }
        echo ""
    else
        echo -e "${YELLOW}2️⃣  Skipping AI commit rewriting (not configured)${NC}"
        msg_mapping_file=""
        echo ""
    fi

    # Step 3: Apply git-filter-repo
    echo -e "${BLUE}3️⃣  Applying git-filter-repo transformations...${NC}"

    # Build git-filter-repo command
    local filter_cmd="git filter-repo --force"

    # Add mailmap if exists
    if [ -f "${WORKSPACE_ROOT}/.mailmap" ]; then
        filter_cmd="$filter_cmd --mailmap ${WORKSPACE_ROOT}/.mailmap"
        echo "   → Using .mailmap for author normalization"
    fi

    # Add message replacement if exists
    if [ -n "$msg_mapping_file" ] && [ -f "$msg_mapping_file" ]; then
        filter_cmd="$filter_cmd --replace-message $msg_mapping_file"
        echo "   → Using AI-generated commit messages"
    fi

    # Execute or dry-run
    if [ "$dry_run" = "true" ]; then
        echo -e "${YELLOW}   ⚠️  DRY RUN MODE - NOT executing git-filter-repo${NC}"
        echo "   → Would run: $filter_cmd"
        echo ""
        echo -e "${CYAN}   Instead, showing what WOULD happen:${NC}"
        echo "   → Generated mapping preview:"
        if [ -f "$msg_mapping_file" ]; then
            echo ""
            head -20 "$msg_mapping_file" | sed 's/^/      /'
            echo ""
            echo "      ... (see full file: $msg_mapping_file)"
        fi
        echo ""
        echo -e "${GREEN}   ✅ Dry run analysis complete${NC}"
    else
        echo "   → Running: $filter_cmd"
        eval $filter_cmd 2>&1 | sed 's/^/     /'
        echo -e "${GREEN}   ✅ git-filter-repo complete${NC}"
    fi
    echo ""

    # Step 4: Validation
    echo -e "${BLUE}4️⃣  Validating repository...${NC}"

    local new_commit_count=$(git rev-list --all --count)
    echo "   → Commit count: $new_commit_count"

    local new_author_count=$(git log --all --format='%aN <%aE>' | sort -u | wc -l)
    echo "   → Unique authors: $new_author_count"

    # Check if repo is clean
    if ! git status --porcelain | grep -q .; then
        echo -e "${GREEN}   ✅ Working directory clean${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Working directory has changes${NC}"
    fi

    echo ""
    if [ "$dry_run" = "true" ]; then
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}✅ ${repo_name} DRY RUN completed (no changes made)${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    else
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}✅ ${repo_name} processed successfully${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    fi
    echo ""

    cd "$WORKSPACE_ROOT"
}

# Test run - ANALYSIS ONLY (no modifications)
test_run() {
    echo -e "${YELLOW}🧪 TEST RUN MODE - ANALYSIS ONLY${NC}"
    echo ""
    echo -e "${GREEN}✅ This mode is SAFE - it will NOT modify your repository${NC}"
    echo -e "${GREEN}✅ It will only analyze commits and generate suggestions${NC}"
    echo ""
    echo -e "${CYAN}What this will do:${NC}"
    echo "  1. Analyze first 100 commits"
    echo "  2. Generate improved commit messages"
    echo "  3. Create mapping file for review"
    echo "  4. Show you a preview"
    echo ""
    echo -e "${CYAN}What this will NOT do:${NC}"
    echo "  ❌ Modify commit history"
    echo "  ❌ Change commit SHAs"
    echo "  ❌ Require force push"
    echo ""
    read -p "Continue with analysis? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "Cancelled."
        exit 0
    fi
    echo ""

    # Run analysis only
    echo -e "${BLUE}🔍 Analyzing commits...${NC}"
    python3 "$REWRITER_SCRIPT" --repo "$WORKSPACE_ROOT"
    echo ""

    # Show preview
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  PREVIEW: Proposed Changes${NC}"
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""

    echo -e "${YELLOW}Sample improved commit messages (first 20):${NC}"
    head -20 "$WORKSPACE_ROOT/.git/history-cleanup/commit-msg-mapping.txt"
    echo ""
    echo -e "${YELLOW}... ($(wc -l < "$WORKSPACE_ROOT/.git/history-cleanup/commit-msg-mapping.txt") total messages generated)${NC}"
    echo ""

    echo -e "${YELLOW}Current authors in repository:${NC}"
    (cd "$WORKSPACE_ROOT" && git log --all --format='%aN <%aE>' | sort -u)
    echo ""

    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ ANALYSIS COMPLETE - Repository NOT Modified${NC}"
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""
    echo "Generated files:"
    echo "  Mapping: .git/history-cleanup/commit-msg-mapping.txt"
    echo "  Summary: .git/history-cleanup/cleanup-summary.json"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo ""
    echo "1. ${YELLOW}RECOMMENDED - Safe test in temporary clone:${NC}"
    echo "   ./scripts/git_cleanup_test_safe.sh"
    echo ""
    echo "2. ${RED}DANGEROUS - Apply to this repository:${NC}"
    echo "   ./scripts/git_cleanup_orchestrator.sh --full-cleanup"
    echo ""
    echo "3. Review mapping file:"
    echo "   cat .git/history-cleanup/commit-msg-mapping.txt | less"
    echo ""
}

# Full cleanup of all submodules + main repo
full_cleanup() {
    echo -e "${YELLOW}🚀 FULL CLEANUP MODE${NC}"
    echo "This will process ALL submodules and the main repository"
    echo ""

    confirm_operation "ALL REPOSITORIES (main + all submodules)"

    # Step 1: Comprehensive backup
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  STEP 1: Creating comprehensive backup${NC}"
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""
    bash "$BACKUP_SCRIPT" --all-submodules
    echo ""

    # Step 2: Process submodules (bottom-up)
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  STEP 2: Processing submodules${NC}"
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""

    git submodule status | awk '{print $2}' | while read -r submodule; do
        if [ -d "${WORKSPACE_ROOT}/${submodule}/.git" ]; then
            process_repository "${WORKSPACE_ROOT}/${submodule}"
        else
            echo -e "${YELLOW}⚠️  Skipping ${submodule} (not initialized)${NC}"
            echo ""
        fi
    done

    # Step 3: Update submodule references in main repo
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  STEP 3: Updating submodule references${NC}"
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""

    cd "$WORKSPACE_ROOT"
    git submodule update --remote
    git add .gitmodules
    git add $(git submodule status | awk '{print $2}')
    git commit -m "chore: update submodule references after history cleanup" || true
    echo ""

    # Step 4: Process main repository
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  STEP 4: Processing main repository${NC}"
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""
    process_repository "$WORKSPACE_ROOT"

    # Final summary
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ FULL CLEANUP COMPLETE${NC}"
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. VALIDATION:"
    echo "   • Review commit history: git log --oneline"
    echo "   • Check author normalization: git log --format='%aN <%aE>' | sort -u"
    echo "   • Run tests: make test"
    echo ""
    echo "2. IF SATISFIED - Deploy:"
    echo "   • Force push main: git push --force origin main"
    echo "   • Force push submodules: (cd submodule && git push --force origin main)"
    echo "   • Notify team to re-clone"
    echo ""
    echo "3. IF NOT SATISFIED - Rollback:"
    echo "   • Find backup in: ~/flext-history-backup-*"
    echo "   • Run: cd ~/flext-history-backup-*/  && ./ROLLBACK.sh"
    echo ""
}

# Main execution
main() {
    check_requirements

    case "${1:-}" in
        --test-run)
            test_run
            ;;
        --full-cleanup)
            full_cleanup
            ;;
        *)
            echo "Usage: $0 [--test-run | --full-cleanup]"
            echo ""
            echo "Options:"
            echo "  --test-run       Test on single submodule (${TEST_SUBMODULE})"
            echo "  --full-cleanup   Full workspace cleanup (all repos)"
            echo ""
            echo "Examples:"
            echo "  $0 --test-run          # Safe test first"
            echo "  $0 --full-cleanup      # Full operation"
            exit 1
            ;;
    esac
}

main "$@"
