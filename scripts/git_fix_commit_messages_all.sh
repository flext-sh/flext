#!/bin/bash
#
# Fix Commit Messages for All Repositories
#
# Runs heuristic-based commit message rewriting across
# main repository and all submodules.
#
# Usage: ./git_fix_commit_messages_all.sh
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
REWRITER_SCRIPT="${SCRIPT_DIR}/git_commit_rewriter_cursor.py"

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  FLEXT Commit Message Rewriting (All Repositories)       ║${NC}"
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Check requirements
echo -e "${BLUE}🔍 Checking requirements...${NC}"

if ! command -v git-filter-repo &> /dev/null; then
    echo -e "${RED}   ❌ git-filter-repo not found${NC}"
    echo "      Install: pip install git-filter-repo"
    exit 1
fi
echo -e "${GREEN}   ✅ git-filter-repo installed${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}   ❌ python3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}   ✅ python3 installed${NC}"

if ! command -v cursor-agent &> /dev/null; then
    echo -e "${RED}   ❌ cursor-agent not found${NC}"
    exit 1
fi
echo -e "${GREEN}   ✅ cursor-agent installed${NC}"

if [ ! -f "$REWRITER_SCRIPT" ]; then
    echo -e "${RED}   ❌ git_commit_rewriter_cursor.py not found${NC}"
    exit 1
fi
echo -e "${GREEN}   ✅ git_commit_rewriter_cursor.py found${NC}"

echo -e "${GREEN}   ✅ Using cursor-agent for intelligent commit rewriting${NC}"
echo ""

# Warning
echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  ⚠️  WARNING: This will rewrite git history${NC}"
echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""
echo "This will:"
echo "  • Rewrite commit messages using cursor-agent AI"
echo "  • Change all commit SHAs"
echo "  • Require force push to GitHub"
echo ""
echo "Expected improvements:"
echo "  • '0.9.0' → 'chore(release): bump version to 0.9.0'"
echo "  • '***REMOVED***' → Reconstructed from commit context"
echo "  • 'WIP async' → 'feat(core): implement async execution patterns'"
echo "  • 'fix lint' → 'style: apply code formatting and linting'"
echo ""
read -p "Continue with commit message rewriting? (yes/NO): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi
echo ""

# Function to rewrite commit messages for a repository
rewrite_repo_commits() {
    local repo_path="$1"
    local repo_name="$(basename "$repo_path")"

    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  Processing: $repo_name${NC}"
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""

    cd "$repo_path"

    # Check if it's a git repository
    if [ ! -d ".git" ] && [ ! -f ".git" ]; then
        echo -e "${YELLOW}⚠️  Not a git repository, skipping${NC}"
        return
    fi

    # Create safety tag
    echo -e "${BLUE}1️⃣  Creating safety tag...${NC}"
    local backup_tag="pre-msg-rewrite-$(date +%Y%m%d-%H%M%S)"
    git tag "$backup_tag" 2>/dev/null || echo "   Tag already exists"
    echo -e "${GREEN}   ✅ Safety tag: $backup_tag${NC}"
    echo ""

    # Generate improved commit messages
    echo -e "${BLUE}2️⃣  Generating improved commit messages...${NC}"

    # Ensure history-cleanup directory exists
    local git_dir
    if [ -f ".git" ]; then
        # Submodule - .git is a file pointing to actual git dir
        git_dir="$(cat .git | sed 's/gitdir: //')/.."
    else
        # Main repo - .git is a directory
        git_dir=".git"
    fi

    mkdir -p "$git_dir/history-cleanup"

    # Run the rewriter
    if python3 "$REWRITER_SCRIPT" --repo "$repo_path"; then
        echo -e "${GREEN}   ✅ Commit message mapping generated${NC}"
    else
        echo -e "${RED}   ❌ Failed to generate commit messages${NC}"
        return 1
    fi
    echo ""

    # Apply git-filter-repo with mailmap and message replacement
    echo -e "${BLUE}3️⃣  Applying git-filter-repo...${NC}"

    local msg_mapping_file="$git_dir/history-cleanup/commit-msg-mapping.txt"

    if [ ! -f "$msg_mapping_file" ]; then
        echo -e "${RED}   ❌ Mapping file not found: $msg_mapping_file${NC}"
        return 1
    fi

    echo "   → Messages to rewrite: $(wc -l < "$msg_mapping_file")"

    # Build filter-repo command
    local filter_cmd="git filter-repo --force --replace-message $msg_mapping_file"

    # Add mailmap if exists (check both repo and workspace root)
    if [ -f ".mailmap" ]; then
        filter_cmd="$filter_cmd --mailmap ./.mailmap"
        echo "   → Using local .mailmap"
    elif [ -f "$WORKSPACE_ROOT/.mailmap" ]; then
        filter_cmd="$filter_cmd --mailmap $WORKSPACE_ROOT/.mailmap"
        echo "   → Using workspace .mailmap"
    fi

    # Execute
    echo "   → Running git-filter-repo..."
    if eval $filter_cmd 2>&1 | sed 's/^/      /'; then
        echo -e "${GREEN}   ✅ Commit messages rewritten${NC}"
    else
        echo -e "${RED}   ❌ git-filter-repo failed${NC}"
        return 1
    fi
    echo ""

    # Show sample of new messages
    echo -e "${BLUE}4️⃣  Sample of improved messages:${NC}"
    git log --oneline | head -10 | sed 's/^/   /'
    echo ""

    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ $repo_name: Commit messages improved${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    cd "$WORKSPACE_ROOT"
}

# Main execution
main() {
    cd "$WORKSPACE_ROOT"

    # Process main repository
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  MAIN REPOSITORY${NC}"
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"

    rewrite_repo_commits "$WORKSPACE_ROOT"

    # Process all submodules
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  SUBMODULES${NC}"
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"

    if [ -f ".gitmodules" ]; then
        git submodule foreach --quiet 'echo "$path"' | while read -r submodule; do
            local submodule_path="$WORKSPACE_ROOT/$submodule"
            if [ -d "$submodule_path" ]; then
                rewrite_repo_commits "$submodule_path"
            fi
        done
    fi

    # Final summary
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ COMMIT MESSAGE REWRITING COMPLETE${NC}"
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""

    echo -e "${CYAN}📊 Summary:${NC}"
    echo "  All repositories now have improved commit messages"
    echo "  Safety tags created for recovery"
    echo ""

    echo -e "${YELLOW}⚠️  Important next steps:${NC}"
    echo "  1. Review commit messages: git log --oneline | head -20"
    echo "  2. Restore remotes: ./scripts/git_restore_remotes.sh"
    echo "  3. Force push to GitHub:"
    echo "     git push origin --force --all"
    echo "     git push origin --force --tags"
    echo "     git submodule foreach 'git push origin --force --all && git push origin --force --tags'"
    echo ""

    echo -e "${BLUE}To recover (if needed):${NC}"
    echo "  git reset --hard pre-msg-rewrite-YYYYMMDD-HHMMSS"
    echo ""
}

# Run main function
main
