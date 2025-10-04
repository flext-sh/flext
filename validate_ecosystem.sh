#!/bin/bash
# FLEXT Ecosystem Validation Script
# Validates all 31 projects for quality gates compliance

set -e

WORKSPACE_DIR="/home/marlonsc/flext"
REPORT_FILE="$WORKSPACE_DIR/ecosystem_health_report.md"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "# FLEXT Ecosystem Health Report" > "$REPORT_FILE"
echo "**Generated**: $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Counters
TOTAL_PROJECTS=0
PASSED_PROJECTS=0
FAILED_PROJECTS=0

# Phase 1: Foundation - flext-core
echo "## Phase 1: Foundation Library" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

validate_project() {
    local project_name=$1
    local project_path="$WORKSPACE_DIR/$project_name"

    TOTAL_PROJECTS=$((TOTAL_PROJECTS + 1))

    echo -e "\n${YELLOW}Validating $project_name...${NC}"
    echo "### $project_name" >> "$REPORT_FILE"

    if [ ! -d "$project_path" ]; then
        echo -e "${RED}❌ Project not found${NC}"
        echo "- **Status**: ❌ NOT FOUND" >> "$REPORT_FILE"
        FAILED_PROJECTS=$((FAILED_PROJECTS + 1))
        return 1
    fi

    cd "$project_path"

    # Check if it's a Python project
    if [ ! -f "pyproject.toml" ]; then
        echo -e "${YELLOW}⚠️  Not a Python project (skipping)${NC}"
        echo "- **Status**: ⚠️ NOT PYTHON PROJECT" >> "$REPORT_FILE"
        return 0
    fi

    local has_errors=0

    # Lint check
    echo -n "  Checking lint... "
    if make lint > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        echo "- **Lint**: ✅ PASS" >> "$REPORT_FILE"
    else
        echo -e "${RED}❌${NC}"
        echo "- **Lint**: ❌ FAIL" >> "$REPORT_FILE"
        has_errors=1
    fi

    # Pattern compliance check
    echo -n "  Checking patterns... "
    local pattern_ok=1

    if [ -f "src/${project_name/-/_}/constants.py" ]; then
        if grep -q "class.*Constants.*FlextConstants" "src/${project_name/-/_}/constants.py" 2>/dev/null; then
            echo -n "C"
        else
            pattern_ok=0
        fi
    fi

    if [ -f "src/${project_name/-/_}/config.py" ]; then
        if grep -q "class.*Config.*FlextConfig" "src/${project_name/-/_}/config.py" 2>/dev/null; then
            echo -n "o"
        else
            pattern_ok=0
        fi
    fi

    if [ -f "src/${project_name/-/_}/models.py" ]; then
        if grep -q "class.*Models.*FlextModels" "src/${project_name/-/_}/models.py" 2>/dev/null; then
            echo -n "M"
        else
            pattern_ok=0
        fi
    fi

    if [ $pattern_ok -eq 1 ]; then
        echo -e " ${GREEN}✅${NC}"
        echo "- **Patterns**: ✅ PASS (Constants/Config/Models inheritance)" >> "$REPORT_FILE"
    else
        echo -e " ${RED}❌${NC}"
        echo "- **Patterns**: ❌ FAIL (inheritance broken)" >> "$REPORT_FILE"
        has_errors=1
    fi

    # Import check
    echo -n "  Checking imports... "
    if python3 -c "import sys; sys.path.insert(0, 'src'); import ${project_name/-/_}" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        echo "- **Imports**: ✅ PASS" >> "$REPORT_FILE"
    else
        echo -e "${RED}❌${NC}"
        echo "- **Imports**: ❌ FAIL" >> "$REPORT_FILE"
        has_errors=1
    fi

    echo "" >> "$REPORT_FILE"

    if [ $has_errors -eq 0 ]; then
        PASSED_PROJECTS=$((PASSED_PROJECTS + 1))
        return 0
    else
        FAILED_PROJECTS=$((FAILED_PROJECTS + 1))
        return 1
    fi
}

# Phase 1: Foundation
echo -e "\n${YELLOW}=== PHASE 1: FOUNDATION ===${NC}"
validate_project "flext-core"

# Phase 2: Infrastructure Libraries
echo -e "\n${YELLOW}=== PHASE 2: INFRASTRUCTURE LIBRARIES ===${NC}"
echo "" >> "$REPORT_FILE"
echo "## Phase 2: Infrastructure Libraries" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for project in flext-api flext-cli flext-auth flext-db-oracle flext-ldap flext-grpc; do
    validate_project "$project"
done

# Phase 3: Domain Libraries
echo -e "\n${YELLOW}=== PHASE 3: DOMAIN LIBRARIES ===${NC}"
echo "" >> "$REPORT_FILE"
echo "## Phase 3: Domain Libraries" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for project in flext-web flext-ldif flext-meltano flext-observability flext-oracle-wms flext-oracle-oic flext-quality flext-plugin; do
    validate_project "$project"
done

# Phase 4: DBT Projects
echo -e "\n${YELLOW}=== PHASE 4: DBT PROJECTS ===${NC}"
echo "" >> "$REPORT_FILE"
echo "## Phase 4: DBT Transformation Projects" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for project in flext-dbt-ldap flext-dbt-ldif flext-dbt-oracle flext-dbt-oracle-wms; do
    validate_project "$project"
done

# Phase 5: Singer Taps
echo -e "\n${YELLOW}=== PHASE 5: SINGER TAPS ===${NC}"
echo "" >> "$REPORT_FILE"
echo "## Phase 5: Singer Tap Projects" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for project in flext-tap-ldap flext-tap-ldif flext-tap-oracle flext-tap-oracle-oic flext-tap-oracle-wms; do
    validate_project "$project"
done

# Phase 6: Singer Targets
echo -e "\n${YELLOW}=== PHASE 6: SINGER TARGETS ===${NC}"
echo "" >> "$REPORT_FILE"
echo "## Phase 6: Singer Target Projects" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for project in flext-target-ldap flext-target-ldif flext-target-oracle flext-target-oracle-oic flext-target-oracle-wms; do
    validate_project "$project"
done

# Phase 7: Enterprise Tools
echo -e "\n${YELLOW}=== PHASE 7: ENTERPRISE TOOLS ===${NC}"
echo "" >> "$REPORT_FILE"
echo "## Phase 7: Enterprise Tools" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for project in client-a-oud-mig client-b-meltano-native; do
    validate_project "$project"
done

# Summary
echo "" >> "$REPORT_FILE"
echo "## Summary" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "- **Total Projects**: $TOTAL_PROJECTS" >> "$REPORT_FILE"
echo "- **Passed**: $PASSED_PROJECTS" >> "$REPORT_FILE"
echo "- **Failed**: $FAILED_PROJECTS" >> "$REPORT_FILE"
echo "- **Success Rate**: $(echo "scale=2; $PASSED_PROJECTS * 100 / $TOTAL_PROJECTS" | bc)%" >> "$REPORT_FILE"

echo -e "\n${GREEN}=== VALIDATION COMPLETE ===${NC}"
echo -e "Total: $TOTAL_PROJECTS | Passed: ${GREEN}$PASSED_PROJECTS${NC} | Failed: ${RED}$FAILED_PROJECTS${NC}"
echo -e "\nReport saved to: $REPORT_FILE"

cd "$WORKSPACE_DIR"
