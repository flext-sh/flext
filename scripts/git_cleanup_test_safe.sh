#!/bin/bash
#
# Safe Test Mode for Git History Cleanup
#
# Creates a temporary clone of the repository for testing,
# so the original repository is NEVER modified during testing.
#
# Usage: ./git_cleanup_test_safe.sh

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
TEST_DIR="/tmp/flext-cleanup-test-$(date +%Y%m%d-%H%M%S)"

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  FLEXT Git History Cleanup - SAFE TEST MODE              ║${NC}"
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""
echo -e "${GREEN}✅ Your original repository will NOT be modified${NC}"
echo -e "${GREEN}✅ Testing in temporary clone: ${TEST_DIR}${NC}"
echo ""

# Create temporary clone
echo -e "${BLUE}📦 Creating temporary clone for testing...${NC}"
git clone "$WORKSPACE_ROOT" "$TEST_DIR"
echo -e "${GREEN}   ✅ Clone created${NC}"
echo ""

# Copy scripts to test directory
echo -e "${BLUE}📋 Copying cleanup scripts...${NC}"
cp -r "$SCRIPT_DIR" "$TEST_DIR/scripts"
cp "$WORKSPACE_ROOT/.mailmap" "$TEST_DIR/" 2>/dev/null || true
echo -e "${GREEN}   ✅ Scripts copied${NC}"
echo ""

# Run analysis (non-destructive)
echo -e "${BLUE}🔍 Running commit analysis...${NC}"
cd "$TEST_DIR"
python3 scripts/git_history_rewriter.py --repo .
echo ""

# Show preview
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  PREVIEW: Proposed Changes${NC}"
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

echo -e "${YELLOW}Sample improved commit messages:${NC}"
head -20 .git/history-cleanup/commit-msg-mapping.txt
echo ""
echo -e "${YELLOW}... ($(wc -l < .git/history-cleanup/commit-msg-mapping.txt) total messages)${NC}"
echo ""

echo -e "${YELLOW}Current authors:${NC}"
git log --all --format='%aN <%aE>' | sort -u
echo ""

# Ask if user wants to apply changes to TEST clone
echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  Apply changes to TEST clone?${NC}"
echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""
echo "This will apply git-filter-repo to the TEMPORARY clone only."
echo "Your original repository at $WORKSPACE_ROOT will NOT be touched."
echo ""
read -p "Apply changes to test clone? (y/n): " apply_test

if [ "$apply_test" = "y" ]; then
    echo ""
    echo -e "${BLUE}🔧 Applying git-filter-repo to test clone...${NC}"

    # Apply changes
    git filter-repo --force \
        --mailmap .mailmap \
        --replace-message .git/history-cleanup/commit-msg-mapping.txt

    echo -e "${GREEN}   ✅ Changes applied to test clone${NC}"
    echo ""

    # Show results
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  RESULTS in Test Clone${NC}"
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""

    echo -e "${YELLOW}Sample new commit messages:${NC}"
    git log --oneline | head -20
    echo ""

    echo -e "${YELLOW}Normalized authors:${NC}"
    git log --all --format='%aN <%aE>' | sort -u
    echo ""

    echo -e "${YELLOW}Repository stats:${NC}"
    echo "  Total commits: $(git rev-list --all --count)"
    echo "  Merge commits: $(git log --all --merges --oneline | wc -l)"
    echo ""
fi

# Final instructions
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ SAFE TEST COMPLETE${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""
echo "Test clone location: ${TEST_DIR}"
echo ""
echo "To inspect the test results:"
echo "  cd ${TEST_DIR}"
echo "  git log --oneline | head -50"
echo "  git log --format='%aN <%aE>' | sort -u"
echo ""
echo "To apply these changes to your REAL repository:"
echo "  1. Review the test results thoroughly"
echo "  2. cd ${WORKSPACE_ROOT}"
echo "  3. Create backup: git tag pre-cleanup-backup"
echo "  4. Run: python3 scripts/git_history_rewriter.py --repo ."
echo "  5. Run: git filter-repo --force --mailmap .mailmap --replace-message .git/history-cleanup/commit-msg-mapping.txt"
echo ""
echo "To clean up test directory:"
echo "  rm -rf ${TEST_DIR}"
echo ""
echo -e "${YELLOW}⚠️  Remember: Your original repository is UNTOUCHED!${NC}"
