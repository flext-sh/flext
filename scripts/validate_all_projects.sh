#!/bin/bash
# Comprehensive validation script for all FLEXT projects
# Runs ruff, mypy, pyrefly, and pytest across all projects

set -e

echo "=== FLEXT ECOSYSTEM VALIDATION REPORT ==="
echo "Date: $(date)"
echo ""

echo "=== GLOBAL POLICY GATE ==="
POLICY_MODE="${FLEXT_POLICY_MODE:-baseline}"
FLEXT_POLICY_MODE="$POLICY_MODE" \
  ./scripts/validation/enforce_no_dict_no_any.sh --mode "$POLICY_MODE" --root .
echo "✅ Global policy gate: PASSED"
echo ""

echo "=== PYDANTIC V2 SKILL POLICY GATE ==="
PYDANTIC_POLICY_MODE="${FLEXT_PYDANTIC_POLICY_MODE:-baseline}"
FLEXT_PYDANTIC_POLICY_MODE="$PYDANTIC_POLICY_MODE" \
  ./scripts/validation/enforce_pydantic_v2_skill.sh --mode "$PYDANTIC_POLICY_MODE" --root .
echo "✅ Pydantic v2 skill policy gate: PASSED"
echo ""

PROJECTS=(
  "flext-core"
  "flext-cli"
  "flext-ldif"
  "flext-ldap"
  "client-a-oud-mig"
  "flext-auth"
  "flext-api"
  "flext-web"
  "flext-grpc"
  "flext-observability"
  "flext-quality"
  "flext-meltano"
  "flext-db-oracle"
  "flext-dbt-ldap"
  "flext-dbt-ldif"
  "flext-dbt-oracle"
  "flext-dbt-oracle-wms"
  "flext-tap-ldap"
  "flext-tap-ldif"
  "flext-tap-oracle"
  "flext-tap-oracle-oic"
  "flext-tap-oracle-wms"
  "flext-target-ldap"
  "flext-target-ldif"
  "flext-target-oracle"
  "flext-target-oracle-oic"
  "flext-target-oracle-wms"
  "flext-oracle-oic"
  "flext-oracle-wms"
  "flext-plugin"
)

TOTAL_PROJECTS=${#PROJECTS[@]}
PASSED_PROJECTS=0
FAILED_PROJECTS=0

for project in "${PROJECTS[@]}"; do
  echo ""
  echo "=== PROJECT: $project ==="

  if [ ! -d "$project" ]; then
    echo "❌ Directory $project not found - SKIPPING"
    ((FAILED_PROJECTS++))
    continue
  fi

  cd "$project"

  PROJECT_PASSED=true

  # Check if Makefile exists and has validate target
  if [ -f "Makefile" ] && grep -q "^validate:" Makefile; then
    echo "Running make validate..."
    if make validate 2>&1; then
      echo "✅ make validate: PASSED"
    else
      echo "❌ make validate: FAILED"
      PROJECT_PASSED=false
    fi
  else
    # Manual checks
    echo "Running manual validation..."

    # Ruff check
    if command -v ruff >/dev/null 2>&1; then
      echo "Running ruff check..."
      if ruff check . --output-format=concise 2>&1; then
        echo "✅ ruff check: PASSED"
      else
        echo "❌ ruff check: FAILED"
        PROJECT_PASSED=false
      fi
    fi

    # Mypy check
    if command -v mypy >/dev/null 2>&1; then
      echo "Running mypy..."
      if mypy . 2>&1; then
        echo "✅ mypy: PASSED"
      else
        echo "❌ mypy: FAILED"
        PROJECT_PASSED=false
      fi
    fi

    # Pyrefly check (if available)
    if command -v pyrefly >/dev/null 2>&1; then
      echo "Running pyrefly..."
      if pyrefly check . 2>&1; then
        echo "✅ pyrefly: PASSED"
      else
        echo "❌ pyrefly: FAILED"
        PROJECT_PASSED=false
      fi
    fi

    # Test check
    if [ -f "Makefile" ] && grep -q "^test:" Makefile; then
      echo "Running make test..."
      if timeout 300 make test 2>&1; then
        echo "✅ make test: PASSED"
      else
        echo "❌ make test: FAILED"
        PROJECT_PASSED=false
      fi
    elif [ -d "tests" ]; then
      echo "Running pytest..."
      if timeout 300 python -m pytest tests/ -v --tb=short 2>&1; then
        echo "✅ pytest: PASSED"
      else
        echo "❌ pytest: FAILED"
        PROJECT_PASSED=false
      fi
    fi
  fi

  cd ..

  if [ "$PROJECT_PASSED" = true ]; then
    ((PASSED_PROJECTS++))
  else
    ((FAILED_PROJECTS++))
  fi

done

echo ""
echo "=== VALIDATION SUMMARY ==="
echo "Total Projects: $TOTAL_PROJECTS"
echo "Passed: $PASSED_PROJECTS"
echo "Failed: $FAILED_PROJECTS"
echo "Success Rate: $((PASSED_PROJECTS * 100 / TOTAL_PROJECTS))%"

if [ $FAILED_PROJECTS -eq 0 ]; then
  echo "🎉 ALL PROJECTS PASSED VALIDATION!"
  exit 0
else
  echo "⚠️  SOME PROJECTS NEED FIXES"
  exit 1
fi
