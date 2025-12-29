#!/usr/bin/env bash
################################################################################
# FLEXT Duplication Analysis Tool
#
# Helps identify and understand code/test duplication with consolidation guidance.
#
# Usage: ./analyze-duplication.sh [project] [type] [action]
#
# Examples:
#   ./analyze-duplication.sh flext-ldif src analyze
#   ./analyze-duplication.sh flext-api both consolidation
#   ./analyze-duplication.sh all src summary
################################################################################

set -euo pipefail

FLEXT_DIR="${HOME}/flext"
QUALITY_DIR="${FLEXT_DIR}/flext-quality"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Parse arguments
PROJECT="${1:-all}"
ANALYSIS_TYPE="${2:-src}"
ACTION="${3:-analyze}"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "FLEXT Duplication Analysis"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Project: $PROJECT"
echo "Type:    $ANALYSIS_TYPE"
echo "Action:  $ACTION"
echo ""

################################################################################
# HELPER: Analyze workspace with Python plugin
################################################################################
analyze_workspace() {
    local project="${1:-all}"
    local analysis_type="${2:-src}"

    python3 << PYTHON_SCRIPT
import sys
from pathlib import Path

sys.path.insert(0, str(Path("${QUALITY_DIR}/src")))

try:
    from flext_quality.plugins.duplication_plugin import FlextDuplicationPlugin

    plugin = FlextDuplicationPlugin()
    flext_dir = Path("${FLEXT_DIR}")

    if "$analysis_type" == "tests":
        result = plugin.check_workspace_with_tests(flext_dir)
    else:
        result = plugin.check_workspace(flext_dir)

    if result.is_failure:
        print(f"Error: {result.error}", file=sys.stderr)
        sys.exit(1)

    data = result.value

    # Filter by project if specified
    if "$project" != "all":
        if "$analysis_type" == "tests":
            duplicates = [d for d in data.duplicates
                         if "$project" in d.file1_project or "$project" in d.file2_project]
        else:
            duplicates = [d for d in data.duplicates
                         if "$project" in d.file1_project or "$project" in d.file2_project]
    else:
        duplicates = list(data.duplicates)

    # Output in structured format for bash parsing
    print(f"TOTAL_PROJECTS={data.total_projects}")
    print(f"TOTAL_DUPLICATES={len(duplicates)}")
    if hasattr(data, 'test_duplicates'):
        print(f"LOCAL_TEST_DUPES={data.test_duplicates}")
        print(f"CROSS_TEST_DUPES={data.cross_project_test_duplicates}")

    # Group by consolidation target
    by_target = {}
    for dup in duplicates:
        target = dup.consolidation_target
        if target not in by_target:
            by_target[target] = []
        by_target[target].append(dup)

    for target in sorted(by_target.keys()):
        print(f"TARGET={target}:{len(by_target[target])}")

    # Show samples
    for i, dup in enumerate(duplicates[:10]):
        print(f"DUP_{i}={dup.file1_project}:{dup.file1_path}|{dup.file2_project}:{dup.file2_path}|{dup.similarity:.1%}")

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
}

################################################################################
# ACTION: Analyze (show duplicated files)
################################################################################
action_analyze() {
    log_info "Analyzing duplicates in $PROJECT ($ANALYSIS_TYPE)..."
    echo ""

    # Run analysis
    analysis=$(analyze_workspace "$PROJECT" "$ANALYSIS_TYPE" 2>/dev/null || echo "")

    if [[ -z "$analysis" ]]; then
        log_error "Failed to analyze duplicates"
        exit 1
    fi

    # Parse output
    eval "$analysis"

    echo "Found ${TOTAL_DUPLICATES:-0} duplicate pairs"
    echo ""
    echo "Duplicates by consolidation target:"
    echo ""

    # Show consolidation targets
    while IFS='=' read -r key value; do
        if [[ "$key" == "TARGET" ]]; then
            target=$(echo "$value" | cut -d: -f1)
            count=$(echo "$value" | cut -d: -f2)
            case "$target" in
                flext-core)
                    echo -e "  ${GREEN}→${NC} $target: $count duplicates (Tier 0 - Foundation)"
                    ;;
                flext-tests)
                    echo -e "  ${GREEN}→${NC} $target: $count duplicates (Tier 0 - Test Infrastructure)"
                    ;;
                flext-cli|flext-observability)
                    echo -e "  ${CYAN}→${NC} $target: $count duplicates (Tier 1 - Direct Dependencies)"
                    ;;
                *)
                    echo -e "  ${YELLOW}→${NC} $target: $count duplicates (Tier 2+ - Domain/Integration)"
                    ;;
            esac
        fi
    done <<< "$analysis"

    echo ""
    echo "Sample duplicates:"
    echo ""

    # Show sample duplicates
    sample_count=0
    while IFS='=' read -r key value; do
        if [[ "$key" == "DUP_"* ]]; then
            proj1=$(echo "$value" | cut -d'|' -f1 | cut -d: -f1)
            path1=$(echo "$value" | cut -d'|' -f1 | cut -d: -f2-)
            proj2=$(echo "$value" | cut -d'|' -f2 | cut -d: -f1)
            path2=$(echo "$value" | cut -d'|' -f2 | cut -d: -f2-)
            sim=$(echo "$value" | cut -d'|' -f3)

            echo "  [$((sample_count + 1))] ${sim} similar"
            echo "      $proj1: $path1"
            echo "      $proj2: $path2"
            echo ""

            ((sample_count++))
            if [[ $sample_count -ge 5 ]]; then
                break
            fi
        fi
    done <<< "$analysis"
}

################################################################################
# ACTION: Consolidation (show consolidation strategy)
################################################################################
action_consolidation() {
    log_info "Consolidation strategy for $PROJECT ($ANALYSIS_TYPE)..."
    echo ""

    case "$ANALYSIS_TYPE" in
        src)
            echo "Source Code Consolidation Strategy"
            echo "═══════════════════════════════════════════════════════════════════"
            echo ""
            echo "RULE: Apply SOLID/DRY/SRP - Consolidate UP the tier hierarchy"
            echo ""
            echo "Tier Structure:"
            echo "  Tier 0 (Foundation)"
            echo "    ├─ flext-core: Foundation patterns, utilities, base classes"
            echo "    └─ Consolidation target: YES - all source duplicates here"
            echo ""
            echo "  Tier 1 (CLI/Observability)"
            echo "    ├─ flext-cli: CLI-specific patterns"
            echo "    ├─ flext-observability: Observability patterns"
            echo "    └─ Consolidation target: MAYBE - if shared CLI/observability pattern"
            echo ""
            echo "  Tier 2+ (Domain/Integration)"
            echo "    ├─ flext-ldif, flext-ldap, flext-api, etc"
            echo "    └─ Consolidation target: NO - consolidate UP to Tier 0/1"
            echo ""
            echo "Consolidation Patterns:"
            echo "  Pattern A: Shared utility function"
            echo "    Location: flext-core/utilities.py"
            echo "    Use: from flext_core import u  # utilities"
            echo ""
            echo "  Pattern B: Base class or Protocol"
            echo "    Location: flext-core/models.py"
            echo "    Use: inheritance or Protocol implementation"
            echo ""
            echo "  Pattern C: Established FLEXT pattern"
            echo "    Location: FlextResult, FlextService, FlextContainer"
            echo "    Use: Follow flext-core architecture"
            ;;
        tests)
            echo "Test Code Consolidation Strategy"
            echo "═══════════════════════════════════════════════════════════════════"
            echo ""
            echo "RULE: All test infrastructure consolidates to flext-core/src/flext_tests"
            echo ""
            echo "Consolidation Targets:"
            echo "  ${GREEN}[PRIMARY]${NC} flext-core/src/flext_tests"
            echo "    ├─ Shared test fixtures (@pytest.fixture)"
            echo "    ├─ Test factories and builders"
            echo "    ├─ Base test classes"
            echo "    └─ Common test utilities"
            echo ""
            echo "Consolidation Patterns:"
            echo "  Pattern A: Extract to flext-tests (Recommended)"
            echo "    When: Test fixtures, factories, base classes"
            echo "    Action: Move to flext-core/src/flext_tests/"
            echo "    Result: Import in all projects"
            echo ""
            echo "  Pattern B: Unify locally with conftest"
            echo "    When: Tests in same project share patterns"
            echo "    Action: Create conftest.py with @pytest.fixture"
            echo "    Result: Reduce local duplication"
            echo ""
            echo "  Pattern C: Parametrize tests"
            echo "    When: Tests do same thing with different inputs"
            echo "    Action: Use @pytest.mark.parametrize"
            echo "    Result: Consolidate N tests into 1"
            ;;
        both)
            echo "Source + Test Consolidation Strategy"
            echo "═══════════════════════════════════════════════════════════════════"
            echo ""
            echo "Analyze source and tests together to eliminate duplication across layers"
            echo ""
            log_info "Running separate analyses..."
            echo ""

            ANALYSIS_TYPE="src" action_consolidation
            echo ""
            echo "───────────────────────────────────────────────────────────────────"
            echo ""
            ANALYSIS_TYPE="tests" action_consolidation
            ;;
    esac

    echo ""
}

################################################################################
# ACTION: Recommend Fix (show refactoring patterns)
################################################################################
action_fix() {
    log_info "Recommended fixes for $PROJECT ($ANALYSIS_TYPE)..."
    echo ""

    case "$ANALYSIS_TYPE" in
        src)
            echo "Source Code Refactoring Patterns"
            echo "═══════════════════════════════════════════════════════════════════"
            echo ""
            echo "Pattern A: Extract to Shared Utility"
            echo "─────────────────────────────────────"
            echo ""
            echo "Before (Duplicated in 3+ files):"
            echo "  def process_ldif_entry(entry):"
            echo "      # 30 lines of processing logic"
            echo "      return processed"
            echo ""
            echo "After (In flext-core/utilities.py):"
            echo "  class LdifUtilities(FlextService[LdifEntry]):"
            echo "      def process_entry(self, entry: LdifEntry) -> FlextResult[LdifEntry]:"
            echo "          # 30 lines of processing logic"
            echo "          return self._success(processed)"
            echo ""
            echo "Usage:"
            echo "  from flext_core import u  # utilities"
            echo "  result = u.LdifUtilities().process_entry(entry)"
            echo ""
            echo "Pattern B: Use Protocol or Base Class"
            echo "──────────────────────────────────────"
            echo ""
            echo "Before (Duplicated method in 3+ classes):"
            echo "  class LdifEntry:"
            echo "      def validate(self): ..."
            echo "  class LdapEntry:"
            echo "      def validate(self): ...  # DUPLICATE"
            echo ""
            echo "After (Protocol in flext-core/models.py):"
            echo "  class Validatable(Protocol):"
            echo "      def validate(self) -> FlextResult[None]: ..."
            echo ""
            echo "Usage:"
            echo "  class LdifEntry(Validatable):"
            echo "      def validate(self) -> FlextResult[None]: ..."
            echo ""
            echo "Pattern C: Use Established FLEXT Pattern"
            echo "─────────────────────────────────────────"
            echo ""
            echo "Common patterns in flext-core:"
            echo "  • FlextResult[T] - Railway-oriented error handling"
            echo "  • FlextService[T] - Base class for business logic"
            echo "  • FlextContainer - Dependency injection"
            echo "  • Protocols - Type-safe interfaces without inheritance"
            echo ""
            echo "Instead of:"
            echo "  def get_config():"
            echo "      try: return load_config()"
            echo "      except: return None"
            echo ""
            echo "Use:"
            echo "  from flext_core import r"
            echo "  def get_config() -> r.FlextResult[Config]:"
            echo "      return r.FlextResult.success(load_config())"
            ;;
        tests)
            echo "Test Code Refactoring Patterns"
            echo "═══════════════════════════════════════════════════════════════════"
            echo ""
            echo "Pattern A: Extract Fixtures to flext-tests"
            echo "──────────────────────────────────────────"
            echo ""
            echo "Before (Duplicated in flext-ldif/tests/ AND flext-ldap/tests/):"
            echo "  # flext-ldif/tests/conftest.py"
            echo "  @pytest.fixture"
            echo "  def sample_entry():"
            echo "      return LdifEntry(dn='cn=test', attrs={...})"
            echo ""
            echo "  # flext-ldap/tests/conftest.py"
            echo "  @pytest.fixture"
            echo "  def sample_entry():  # DUPLICATE!"
            echo "      return LdifEntry(dn='cn=test', attrs={...})"
            echo ""
            echo "After (In flext-core/src/flext_tests/):"
            echo "  # flext-core/src/flext_tests/fixtures.py"
            echo "  @pytest.fixture"
            echo "  def sample_entry():"
            echo "      return LdifEntry(dn='cn=test', attrs={...})"
            echo ""
            echo "Usage (in all projects):"
            echo "  from flext_tests.fixtures import sample_entry"
            echo "  def test_something(sample_entry):"
            echo "      assert process(sample_entry) == expected"
            echo ""
            echo "Pattern B: Unify Locally with conftest"
            echo "────────────────────────────────────────"
            echo ""
            echo "Before (Duplicated in test_entry.py, test_parser.py):"
            echo "  # test_entry.py"
            echo "  def test_parse_entry():"
            echo "      client = create_ldif_client()  # Setup"
            echo "      # test code"
            echo ""
            echo "  # test_parser.py"
            echo "  def test_parse_complex():"
            echo "      client = create_ldif_client()  # Duplicate setup!"
            echo "      # test code"
            echo ""
            echo "After (In conftest.py):"
            echo "  @pytest.fixture"
            echo "  def ldif_client():"
            echo "      return create_ldif_client()"
            echo ""
            echo "Usage:"
            echo "  def test_parse_entry(ldif_client):"
            echo "      # test code - client already set up"
            echo ""
            echo "  def test_parse_complex(ldif_client):"
            echo "      # test code - client already set up"
            echo ""
            echo "Pattern C: Parametrize Similar Tests"
            echo "────────────────────────────────────"
            echo ""
            echo "Before (5 separate tests):"
            echo "  def test_validate_simple(): ..."
            echo "  def test_validate_complex(): ..."
            echo "  def test_validate_empty(): ..."
            echo "  def test_validate_invalid(): ..."
            echo ""
            echo "After (1 parametrized test):"
            echo "  @pytest.mark.parametrize('entry,expected', ["
            echo "      (simple_entry(), True),"
            echo "      (complex_entry(), True),"
            echo "      (empty_entry(), False),"
            echo "      (invalid_entry(), False),"
            echo "  ])"
            echo "  def test_validate(entry, expected):"
            echo "      assert validate(entry) == expected"
            ;;
    esac

    echo ""
    echo "Next steps:"
    echo "  1. Choose pattern above that matches your duplication"
    echo "  2. Implement the consolidation"
    echo "  3. Remove the duplicated code"
    echo "  4. Run: make test    (verify tests pass)"
    echo "  5. Retry your edit   (baseline updates automatically)"
    echo ""
}

################################################################################
# ACTION: Summary (high-level statistics)
################################################################################
action_summary() {
    log_info "Workspace duplication summary..."
    echo ""

    # Read baseline files
    if [[ -f "${FLEXT_DIR}/.duplicate-code-baseline" ]]; then
        echo "Source Code Duplication Summary"
        echo "───────────────────────────────────────────────────────────────"
        grep -A20 "^\[SUMMARY\]" "${FLEXT_DIR}/.duplicate-code-baseline" 2>/dev/null || \
            echo "  No summary available (regenerate with create-duplicate-baseline.sh)"
        echo ""
    fi

    if [[ -f "${FLEXT_DIR}/.duplicate-code-baseline-global" ]]; then
        echo "Cross-Project Duplication Summary"
        echo "───────────────────────────────────────────────────────────────"
        grep -A30 "^\[CONSOLIDATION_ANALYSIS\]" "${FLEXT_DIR}/.duplicate-code-baseline-global" 2>/dev/null | head -20 || \
            echo "  No summary available (regenerate with create-duplicate-baseline-global.sh)"
        echo ""
    fi

    if [[ -f "${FLEXT_DIR}/.duplicate-code-baseline-tests" ]]; then
        echo "Test Duplication Summary"
        echo "───────────────────────────────────────────────────────────────"
        grep -A10 "^\[SUMMARY\]" "${FLEXT_DIR}/.duplicate-code-baseline-tests" 2>/dev/null || \
            echo "  No summary available (regenerate with create-duplicate-baseline-tests.sh)"
        echo ""
    fi

    echo ""
    echo "To regenerate baselines:"
    echo "  ${CYAN}./scripts/create-duplicate-baseline.sh${NC}"
    echo "  ${CYAN}./scripts/create-duplicate-baseline-global.sh${NC}"
    echo "  ${CYAN}./scripts/create-duplicate-baseline-tests.sh${NC}"
    echo ""
}

################################################################################
# MAIN
################################################################################

case "$ACTION" in
    analyze)
        action_analyze
        ;;
    consolidation)
        action_consolidation
        ;;
    fix)
        action_fix
        ;;
    summary)
        action_summary
        ;;
    *)
        echo "Invalid action: $ACTION"
        echo ""
        echo "Valid actions:"
        echo "  analyze         - Show duplicated files and pairs"
        echo "  consolidation   - Show consolidation strategy"
        echo "  fix             - Show refactoring patterns"
        echo "  summary         - Show workspace statistics"
        echo ""
        exit 1
        ;;
esac

echo ""
log_success "Analysis complete. Need more help? Run: /duplication-analysis"
echo ""
