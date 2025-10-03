#!/bin/bash
#
# Restore Git Remotes After filter-repo
#
# git-filter-repo removes remotes by default. This script restores them
# based on the .gitmodules configuration file.
#
# Usage: ./git_restore_remotes.sh
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

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  Restoring Git Remotes                                    ║${NC}"
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

cd "$WORKSPACE_ROOT"

# Restore main repo remote
echo -e "${BLUE}📍 Restoring main repository remote...${NC}"
MAIN_REMOTE="git@github.com:flext-sh/flext.git"

if git remote get-url origin >/dev/null 2>&1; then
    echo -e "${YELLOW}  Remote 'origin' already exists, updating URL...${NC}"
    git remote set-url origin "$MAIN_REMOTE"
else
    git remote add origin "$MAIN_REMOTE"
fi

echo -e "${GREEN}  ✅ Main repo: $MAIN_REMOTE${NC}"
echo ""

# Restore submodule remotes
echo -e "${BLUE}🔗 Restoring submodule remotes...${NC}"
echo ""

# Parse .gitmodules and restore remotes
if [ -f ".gitmodules" ]; then
    # Extract submodule paths and URLs
    git config -f .gitmodules --get-regexp '\.path$' | while read -r key path; do
        # Get the submodule name from the key
        submodule_name=$(echo "$key" | sed 's/^submodule\.\(.*\)\.path$/\1/')

        # Get the URL for this submodule
        url=$(git config -f .gitmodules "submodule.$submodule_name.url")

        # Check if submodule directory exists and has .git
        if [ -d "$path" ] && ([ -d "$path/.git" ] || [ -f "$path/.git" ]); then
            echo -e "${CYAN}  Processing: $path${NC}"

            cd "$path"

            # Add or update remote
            if git remote get-url origin >/dev/null 2>&1; then
                git remote set-url origin "$url"
                echo -e "${YELLOW}    Updated: $url${NC}"
            else
                git remote add origin "$url"
                echo -e "${GREEN}    Added: $url${NC}"
            fi

            cd "$WORKSPACE_ROOT"
        else
            echo -e "${YELLOW}  ⚠️  Skipping $path (not initialized)${NC}"
        fi
    done

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ REMOTES RESTORED${NC}"
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""

    echo -e "${CYAN}📊 Summary:${NC}"
    echo "  Main repository: $(git remote get-url origin 2>/dev/null || echo 'Not set')"
    echo ""
    echo "  Active submodules with remotes:"

    git config -f .gitmodules --get-regexp '\.path$' | while read -r key path; do
        if [ -d "$path" ] && ([ -d "$path/.git" ] || [ -f "$path/.git" ]); then
            remote_url=$(cd "$path" && git remote get-url origin 2>/dev/null || echo "No remote")
            if [ "$remote_url" != "No remote" ]; then
                echo "    ✅ $path"
            fi
        fi
    done

else
    echo -e "${RED}❌ .gitmodules file not found!${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Verify remotes: git remote -v"
echo "  2. Check submodule remotes: git submodule foreach 'git remote -v'"
echo "  3. Push to GitHub: git push origin --force --all"
echo "  4. Push tags: git push origin --force --tags"
echo ""
