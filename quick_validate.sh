#!/bin/bash
# Quick FLEXT Ecosystem Validation
# Fast pattern and structure validation across all projects

WORKSPACE="/home/marlonsc/flext"
REPORT="$WORKSPACE/quick_health_report.md"

echo "# FLEXT Ecosystem Quick Health Report"  > "$REPORT"
echo "**Date**: $(date)" >> "$REPORT"
echo "" >> "$REPORT"

# Project lists
FOUNDATION="flext-core"
INFRASTRUCTURE="flext-api flext-cli flext-auth flext-db-oracle flext-ldap flext-grpc"
DOMAIN="flext-web flext-ldif flext-meltano flext-observability flext-oracle-wms flext-oracle-oic flext-quality flext-plugin"
DBT="flext-dbt-ldap flext-dbt-ldif flext-dbt-oracle flext-dbt-oracle-wms"
TAPS="flext-tap-ldap flext-tap-ldif flext-tap-oracle flext-tap-oracle-oic flext-tap-oracle-wms"
TARGETS="flext-target-ldap flext-target-ldif flext-target-oracle flext-target-oracle-oic flext-target-oracle-wms"
ENTERPRISE="client-a-oud-mig client-b-meltano-native"

check_project() {
    local name=$1
    local path="$WORKSPACE/$name"

    if [ ! -d "$path" ]; then
        echo "| $name | ❌ NOT FOUND | - | - | - |"
        return 1
    fi

    cd "$path"

    # Check pyproject.toml
    local has_pyproject="❌"
    [ -f "pyproject.toml" ] && has_pyproject="✅"

    # Check patterns
    local patterns="⚠️"
    local module="${name/-/_}"

    if [ -f "src/$module/constants.py" ] && \
       [ -f "src/$module/config.py" ] && \
       [ -f "src/$module/models.py" ]; then

        if grep -q "class.*Constants.*FlextConstants" "src/$module/constants.py" 2>/dev/null && \
           grep -q "class.*Config.*FlextConfig" "src/$module/config.py" 2>/dev/null && \
           grep -q "class.*Models.*FlextModels" "src/$module/models.py" 2>/dev/null; then
            patterns="✅"
        else
            patterns="❌"
        fi
    fi

    # Check imports
    local imports="⚠️"
    if python3 -c "import sys; sys.path.insert(0, 'src'); import $module" >/dev/null 2>&1; then
        imports="✅"
    else
        imports="❌"
    fi

    echo "| $name | $has_pyproject | $patterns | $imports | OK |"
}

# Phase 1: Foundation
echo "## Phase 1: Foundation" >> "$REPORT"
echo "" >> "$REPORT"
echo "| Project | PyProject | Patterns | Imports | Status |" >> "$REPORT"
echo "|---------|-----------|----------|---------|--------|" >> "$REPORT"
for proj in $FOUNDATION; do
    check_project "$proj" >> "$REPORT"
done
echo "" >> "$REPORT"

# Phase 2: Infrastructure
echo "## Phase 2: Infrastructure Libraries (6)" >> "$REPORT"
echo "" >> "$REPORT"
echo "| Project | PyProject | Patterns | Imports | Status |" >> "$REPORT"
echo "|---------|-----------|----------|---------|--------|" >> "$REPORT"
for proj in $INFRASTRUCTURE; do
    check_project "$proj" >> "$REPORT"
done
echo "" >> "$REPORT"

# Phase 3: Domain
echo "## Phase 3: Domain Libraries (8)" >> "$REPORT"
echo "" >> "$REPORT"
echo "| Project | PyProject | Patterns | Imports | Status |" >> "$REPORT"
echo "|---------|-----------|----------|---------|--------|" >> "$REPORT"
for proj in $DOMAIN; do
    check_project "$proj" >> "$REPORT"
done
echo "" >> "$REPORT"

# Phase 4: DBT
echo "## Phase 4: DBT Projects (4)" >> "$REPORT"
echo "" >> "$REPORT"
echo "| Project | PyProject | Patterns | Imports | Status |" >> "$REPORT"
echo "|---------|-----------|----------|---------|--------|" >> "$REPORT"
for proj in $DBT; do
    check_project "$proj" >> "$REPORT"
done
echo "" >> "$REPORT"

# Phase 5: Taps
echo "## Phase 5: Singer Taps (5)" >> "$REPORT"
echo "" >> "$REPORT"
echo "| Project | PyProject | Patterns | Imports | Status |" >> "$REPORT"
echo "|---------|-----------|----------|---------|--------|" >> "$REPORT"
for proj in $TAPS; do
    check_project "$proj" >> "$REPORT"
done
echo "" >> "$REPORT"

# Phase 6: Targets
echo "## Phase 6: Singer Targets (5)" >> "$REPORT"
echo "" >> "$REPORT"
echo "| Project | PyProject | Patterns | Imports | Status |" >> "$REPORT"
echo "|---------|-----------|----------|---------|--------|" >> "$REPORT"
for proj in $TARGETS; do
    check_project "$proj" >> "$REPORT"
done
echo "" >> "$REPORT"

# Phase 7: Enterprise
echo "## Phase 7: Enterprise Tools (2)" >> "$REPORT"
echo "" >> "$REPORT"
echo "| Project | PyProject | Patterns | Imports | Status |" >> "$REPORT"
echo "|---------|-----------|----------|---------|--------|" >> "$REPORT"
for proj in $ENTERPRISE; do
    check_project "$proj" >> "$REPORT"
done
echo "" >> "$REPORT"

echo "Quick validation complete. Report: $REPORT"
cat "$REPORT"
