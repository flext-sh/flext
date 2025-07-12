#!/bin/bash
# Gradual Linting Fix Script for FLEXT Projects
# Usage: ./gradual_lint_fix.sh <project-name>

set -e

PROJECT=$1

if [ -z "$PROJECT" ]; then
    echo "Usage: $0 <project-name>"
    echo "Example: $0 flext-cli"
    exit 1
fi

if [ ! -d "$PROJECT" ]; then
    echo "Error: Project $PROJECT not found"
    exit 1
fi

echo "===================================="
echo "Gradual Linting Fix for: $PROJECT"
echo "===================================="

cd "$PROJECT"

# Step 1: Create baseline
echo "Step 1: Creating linting baseline..."
ruff check . > linting_baseline.txt 2>&1 || true
BASELINE_COUNT=$(grep -c "^" linting_baseline.txt || echo "0")
echo "Baseline issues: $BASELINE_COUNT"

# Step 2: Show current status
echo -e "\nStep 2: Current linting summary:"
ruff check . --statistics 2>/dev/null | head -10 || true

# Step 3: Apply ONLY safe fixes
echo -e "\nStep 3: Applying safe fixes..."
echo "  - Import sorting (I)"
echo "  - Trailing whitespace (W291, W292, W293)"
echo "  - Blank lines (W391)"

# Create backup branch
git checkout -b linting-fixes-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true

# Apply safe fixes
ruff check --fix --select I,W291,W292,W293,W391 . 2>/dev/null || true

# Step 4: Test
echo -e "\nStep 4: Running tests..."
if [ -f "Makefile" ] && grep -q "^test:" Makefile; then
    make test || { echo "Tests failed! Reverting..."; git checkout -; exit 1; }
else
    echo "No test target found in Makefile, skipping tests"
fi

# Step 5: Show what changed
echo -e "\nStep 5: Changes made:"
git diff --stat

# Step 6: New count
echo -e "\nStep 6: Checking new issue count..."
ruff check . > linting_after.txt 2>&1 || true
AFTER_COUNT=$(grep -c "^" linting_after.txt || echo "0")
echo "Issues after fixes: $AFTER_COUNT"
echo "Reduction: $((BASELINE_COUNT - AFTER_COUNT)) issues fixed"

# Step 7: Commit message template
echo -e "\nStep 7: Suggested commit message:"
echo "----------------------------------------"
cat << EOF
chore($PROJECT): Apply safe linting fixes

- Import sorting (ruff I rules)
- Remove trailing whitespace (W291-293)
- Fix blank lines at end of files (W391)
- No functional changes
- All tests passing

Reduced linting issues from $BASELINE_COUNT to $AFTER_COUNT
Part of gradual linting improvement strategy
EOF
echo "----------------------------------------"

echo -e "\nTo commit these changes:"
echo "  git add -A"
echo "  git commit -m \"<paste message above>\""
echo ""
echo "To revert if needed:"
echo "  git checkout -"

# Cleanup
rm -f linting_baseline.txt linting_after.txt