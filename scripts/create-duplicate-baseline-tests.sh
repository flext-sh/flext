#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-architecture/SKILL.md
################################################################################
# FLEXT Test Duplication Baseline Generator
#
# Generates baseline of test code duplication across workspace following SOLID.
# Detects test duplicates (same project, cross-project, vs flext-tests, vs src)
# with tier-based consolidation strategies.
#
# Usage: ./create-duplicate-baseline-tests.sh
#
# Output: ~/.duplicate-code-baseline-tests
################################################################################

set -euo pipefail

FLEXT_DIR="${HOME}/flext"
BASELINE_FILE="${FLEXT_DIR}/.duplicate-code-baseline-tests"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

################################################################################
# Generate test baseline
################################################################################
generate_baseline() {
	log_info "Generating test duplication baseline..."

	# Use Python to run workspace test analysis
	python3 <<'PYTHON_SCRIPT'
from pathlib import Path
from datetime import datetime
from operator import itemgetter
import sys

sys.path.insert(0, str(Path.home() / "flext" / "flext-quality" / "src"))

from flext_quality.plugins.duplication_plugin import FlextDuplicationPlugin

plugin = FlextDuplicationPlugin()
result = plugin.check_workspace_with_tests(Path.home() / "flext")

if result.is_failure:
    print(f"Error: {result.error}", file=sys.stderr)
    sys.exit(1)

data = result.value

# Generate baseline file
baseline = f"""# FLEXT Test Duplication Baseline
# Generated: {datetime.now().isoformat()}
# Format: Test code duplication analysis with SOLID consolidation targets
# Threshold: 0.65 (65% line similarity)
# Analysis Type: Workspace-wide test duplication (tests/ directories)
#
# This baseline tracks test code duplication:
# - Local test duplicates (same project)
# - Cross-project test duplicates
# - Test code duplicating source code logic
# - Test code duplicating flext-tests infrastructure
#
# Consolidation Strategies:
# - extract-to-flext-tests: Move to shared flext-tests (Tier 0)
# - refactor-src: Fix source code to avoid logic duplication
# - unify-locally: Consolidate tests within same project via fixtures
#

[SUMMARY]
total_projects = {data.total_projects}
local_test_duplicates = {data.test_duplicates}
cross_project_test_duplicates = {data.cross_project_test_duplicates}
test_vs_src_duplicates = {data.test_src_duplicates}

[CONSOLIDATION_STRATEGIES]
# Test consolidation targets prioritized by strategy

# Strategy 1: Extract to flext-tests (shared test infrastructure)
extract_to_flext_tests_count = {sum(1 for d in data.duplicates if d.consolidation_strategy == "extract-to-flext-tests")}

# Strategy 2: Refactor source code (eliminate logic duplication)
refactor_src_count = {sum(1 for d in data.duplicates if d.consolidation_strategy == "refactor-src")}

# Strategy 3: Unify locally (project-level fixtures and helpers)
unify_locally_count = {sum(1 for d in data.duplicates if d.consolidation_strategy == "unify-locally")}

[CONSOLIDATION_ANALYSIS]
# Top projects needing test consolidation

"""

# Group by consolidation strategy and target
strategies = {}
for dup in data.duplicates:
    strategy = dup.consolidation_strategy
    if strategy not in strategies:
        strategies[strategy] = []
    strategies[strategy].append(dup)

# Sort each strategy group by similarity
for strategy in ["extract-to-flext-tests", "refactor-src", "unify-locally"]:
    if strategy in strategies:
        dups = strategies[strategy]
        unique_projects = set()
        for d in dups:
            if strategy == "refactor-src":
                unique_projects.add(d.file2_project)
            else:
                unique_projects.add(d.file1_project)

        if unique_projects:
            baseline += f"\n# {strategy.upper()}\n"
            baseline += f"# Projects: {len(unique_projects)}\n"

            # Show top projects by duplicate count
            project_counts = {}
            for d in dups:
                proj = d.file1_project if strategy != "refactor-src" else d.file2_project
                project_counts[proj] = project_counts.get(proj, 0) + 1

            for proj, count in sorted(project_counts.items(), key=itemgetter(1), reverse=True)[:5]:
                baseline += f"#   {proj}: {count} duplicates\n"

baseline += """

[QUALITY_GATE]
# When test duplicates increase, consolidation is REQUIRED
max_local_test_duplicates = 1300
max_cross_project_test_duplicates = 1200
max_test_src_duplicates = 10

# Consolidation priorities (in order)
consolidation_priority = [
  "extract-to-flext-tests",      # Tier 0: Shared infrastructure
  "refactor-src",                 # Fix source code logic issues
  "unify-locally",                # Project-level unification
]
"""

print(baseline)

PYTHON_SCRIPT

	log_success "Test baseline generated"
}

# Main execution
generate_baseline >"$BASELINE_FILE" 2>&1 || {
	log_error "Failed to generate test baseline"
	exit 1
}

log_success "Test baseline saved to: $BASELINE_FILE"
