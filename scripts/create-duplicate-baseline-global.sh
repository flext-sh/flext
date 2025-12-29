#!/usr/bin/env bash
################################################################################
# FLEXT Global Workspace Duplicate Code Baseline Generator
#
# Generates baseline of cross-project duplicate code pairs following SOLID.
# Detects duplicates ACROSS all projects (flext-*) with tier-based consolidation.
#
# Usage: ./create-duplicate-baseline-global.sh
#
# Output: ~/.duplicate-code-baseline-global
################################################################################

set -euo pipefail

FLEXT_DIR="${HOME}/flext"
BASELINE_FILE="${FLEXT_DIR}/.duplicate-code-baseline-global"

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
# Generate global baseline
################################################################################
generate_baseline() {
    log_info "Generating global workspace duplicate baseline..."

    # Use Python to run workspace analysis
    python3 << 'PYTHON_SCRIPT'
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path.home() / "flext" / "flext-quality" / "src"))

from flext_quality.plugins.duplication_plugin import FlextDuplicationPlugin

plugin = FlextDuplicationPlugin()
result = plugin.check_workspace(Path.home() / "flext")

if result.is_failure:
    print(f"Error: {result.error}", file=sys.stderr)
    sys.exit(1)

data = result.value

# Generate baseline file
baseline = f"""# FLEXT Global Workspace Duplicate Code Baseline
# Generated: {Path.home() / ".flext-last-analysis-time"}
# Format: Cross-project duplication analysis with SOLID consolidation targets
# Threshold: 0.65 (65% line similarity)
# Analysis Type: Global workspace-wide (all projects compared)
#
# This baseline tracks code duplication ACROSS projects and suggests
# tier-based consolidation following SOLID/DRY/SRP principles.
#
# Tier Hierarchy (consolidation always moves UP the tier):
# Tier 0 (Foundation):     flext-core
# Tier 1 (Direct deps):    flext-cli, flext-observability
# Tier 2+ (Other deps):    All other projects

[SUMMARY]
total_projects = {data.total_projects}
total_cross_project_duplicates = {data.total_duplicates}
analysis_timestamp = {Path.home() / "flext"}

[CONSOLIDATION_ANALYSIS]
# Top duplication sources (consolidation targets)
"""

    # Group duplicates by consolidation target
    targets = {}
    for dup in data.duplicates:
        target = dup.consolidation_target
        if target not in targets:
            targets[target] = []
        targets[target].append((dup.file1_project, dup.file2_project, dup.similarity))

    # Sort by frequency
    for target in sorted(targets.keys(), key=lambda t: len(targets[t]), reverse=True)[:5]:
        deps = targets[target]
        baseline += f"\n# {target}: {len(deps)} duplicate pairs\n"
        for proj1, proj2, sim in sorted(set(deps), key=lambda x: x[2], reverse=True)[:3]:
            baseline += f"#   {proj1} <-> {proj2}: {sim:.1%}\n"

    baseline += """
[QUALITY_GATE]
# When duplicates increase, consolidation is REQUIRED
max_increase_tolerance = 5
consolidation_target_priority = [
  "flext-core",
  "flext-cli",
  "flext-observability",
]
"""

    print(baseline)

PYTHON_SCRIPT

    log_success "Global baseline generated"
}

# Main execution
generate_baseline > "$BASELINE_FILE" 2>&1 || {
    log_error "Failed to generate baseline"
    exit 1
}

log_success "Baseline saved to: $BASELINE_FILE"
