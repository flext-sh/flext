#!/bin/bash
# Quality Gates Validation for FLEXT Workspace
# Validates all Python projects meet PEP compliance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== FLEXT Workspace Quality Gates Validation ===${NC}"
echo "Starting validation at $(date)"
echo ""

# List of all Python projects in workspace
PROJECTS=(
    "flext-core"
    "flext-auth"
    "flext-api"
    "flext-grpc"
    "flext-web"
    "flext-cli"
    "flext-plugin"
    "flext-observability"
    "flext-meltano"
    "flext-ldap"
    "flext-quality"
    "flext-db-oracle"
    "flext-tap-ldap"
    "flext-tap-oracle-oic"
    "flext-tap-oracle-wms"
    "flext-target-ldap"
    "flext-target-oracle"
    "flext-target-oracle-oic"
    "flext-target-oracle-wms"
    "flext-dbt-ldap"
    "flext-oracle-oic-ext"
    "client-a-oud-mig"
    "client-b-meltano-native"
)

# Summary counters
PASSED=0
FAILED=0
SKIPPED=0

# Failed projects list
declare -a FAILED_PROJECTS=()
declare -a LINT_ERRORS=()
declare -a TYPE_ERRORS=()
declare -a TEST_ERRORS=()

echo -e "${YELLOW}Checking for forbidden scripts...${NC}"
FORBIDDEN_SCRIPTS=$(find . -name "fix_*.py" -o -name "temp_*.py" -o -name "migrate_*.py" | grep -v tests/ | grep -v .venv | grep -v __pycache__ | grep -v site-packages || true)
if [ -n "$FORBIDDEN_SCRIPTS" ]; then
    echo -e "${RED}❌ FORBIDDEN SCRIPTS FOUND:${NC}"
    echo "$FORBIDDEN_SCRIPTS"
    echo ""
    echo -e "${RED}These scripts violate CLAUDE.md rules and must be removed!${NC}"
    exit 1
else
    echo -e "${GREEN}✅ No forbidden scripts found${NC}"
fi
echo ""

# Function to validate a single project
validate_project() {
    local project=$1
    echo -e "${YELLOW}=== Validating $project ===${NC}"
    
    if [ ! -d "$project" ]; then
        echo -e "${YELLOW}⚠️  Project directory not found, skipping${NC}"
        ((SKIPPED++))
        echo ""
        return
    fi
    
    cd "$project"
    
    # Check if it's a Python project
    if [ ! -f "pyproject.toml" ] && [ ! -f "setup.py" ]; then
        echo -e "${YELLOW}⚠️  Not a Python project, skipping${NC}"
        cd ..
        ((SKIPPED++))
        echo ""
        return
    fi
    
    # Check if Makefile exists
    if [ ! -f "Makefile" ]; then
        echo -e "${YELLOW}⚠️  No Makefile found, using direct commands${NC}"
        USE_MAKE=false
    else
        USE_MAKE=true
    fi
    
    local project_passed=true
    
    # 1. Lint check
    echo -n "  Lint check... "
    if [ "$USE_MAKE" = true ] && grep -q "^lint:" Makefile 2>/dev/null; then
        if make lint > /tmp/${project}_lint.log 2>&1; then
            echo -e "${GREEN}✅ PASSED${NC}"
        else
            echo -e "${RED}❌ FAILED${NC}"
            LINT_ERRORS+=("$project")
            project_passed=false
        fi
    else
        if poetry run ruff check . > /tmp/${project}_lint.log 2>&1; then
            echo -e "${GREEN}✅ PASSED${NC}"
        else
            echo -e "${RED}❌ FAILED${NC}"
            LINT_ERRORS+=("$project")
            project_passed=false
        fi
    fi
    
    # 2. Type check (if mypy is configured)
    if grep -q "tool.mypy" pyproject.toml 2>/dev/null; then
        echo -n "  Type check... "
        if [ "$USE_MAKE" = true ] && grep -q "^typecheck:" Makefile 2>/dev/null; then
            if make typecheck > /tmp/${project}_type.log 2>&1; then
                echo -e "${GREEN}✅ PASSED${NC}"
            else
                echo -e "${RED}❌ FAILED${NC}"
                TYPE_ERRORS+=("$project")
                project_passed=false
            fi
        else
            if poetry run mypy . > /tmp/${project}_type.log 2>&1; then
                echo -e "${GREEN}✅ PASSED${NC}"
            else
                echo -e "${RED}❌ FAILED${NC}"
                TYPE_ERRORS+=("$project")
                project_passed=false
            fi
        fi
    else
        echo "  Type check... SKIPPED (mypy not configured)"
    fi
    
    # 3. Test check (if tests exist)
    if [ -d "tests" ]; then
        echo -n "  Test check... "
        if [ "$USE_MAKE" = true ] && grep -q "^test:" Makefile 2>/dev/null; then
            if make test > /tmp/${project}_test.log 2>&1; then
                echo -e "${GREEN}✅ PASSED${NC}"
            else
                echo -e "${RED}❌ FAILED${NC}"
                TEST_ERRORS+=("$project")
                project_passed=false
            fi
        else
            if poetry run pytest > /tmp/${project}_test.log 2>&1; then
                echo -e "${GREEN}✅ PASSED${NC}"
            else
                echo -e "${RED}❌ FAILED${NC}"
                TEST_ERRORS+=("$project")
                project_passed=false
            fi
        fi
    else
        echo "  Test check... SKIPPED (no tests directory)"
    fi
    
    # Update counters
    if [ "$project_passed" = true ]; then
        ((PASSED++))
        echo -e "  ${GREEN}✅ Project PASSED all quality gates${NC}"
    else
        ((FAILED++))
        FAILED_PROJECTS+=("$project")
        echo -e "  ${RED}❌ Project FAILED quality gates${NC}"
    fi
    
    cd ..
    echo ""
}

# Validate each project
for project in "${PROJECTS[@]}"; do
    validate_project "$project"
done

# Print summary
echo -e "${YELLOW}=== QUALITY GATES SUMMARY ===${NC}"
echo "Total projects: ${#PROJECTS[@]}"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED${NC}"
echo ""

if [ ${#FAILED_PROJECTS[@]} -gt 0 ]; then
    echo -e "${RED}Failed projects:${NC}"
    for project in "${FAILED_PROJECTS[@]}"; do
        echo "  - $project"
    done
    echo ""
fi

if [ ${#LINT_ERRORS[@]} -gt 0 ]; then
    echo -e "${RED}Projects with lint errors:${NC}"
    for project in "${LINT_ERRORS[@]}"; do
        echo "  - $project (see /tmp/${project}_lint.log)"
    done
    echo ""
fi

if [ ${#TYPE_ERRORS[@]} -gt 0 ]; then
    echo -e "${RED}Projects with type errors:${NC}"
    for project in "${TYPE_ERRORS[@]}"; do
        echo "  - $project (see /tmp/${project}_type.log)"
    done
    echo ""
fi

if [ ${#TEST_ERRORS[@]} -gt 0 ]; then
    echo -e "${RED}Projects with test failures:${NC}"
    for project in "${TEST_ERRORS[@]}"; do
        echo "  - $project (see /tmp/${project}_test.log)"
    done
    echo ""
fi

# Final status
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL QUALITY GATES PASSED!${NC}"
    echo -e "${GREEN}FLEXT workspace is 100% PEP compliant!${NC}"
    exit 0
else
    echo -e "${RED}❌ QUALITY GATES FAILED${NC}"
    echo -e "${RED}$FAILED projects need attention${NC}"
    exit 1
fi