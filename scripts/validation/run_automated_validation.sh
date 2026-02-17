#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-validation/SKILL.md

set -euo pipefail

MODE="${1:-quick}"
POLICY_MODE="${FLEXT_POLICY_MODE:-baseline}"
ROOT_DIR="${FLEXT_VALIDATION_ROOT:-.}"
REPORT_DIR="${FLEXT_VALIDATION_REPORT_DIR:-.sisyphus/reports/validation}"
PYDANTIC_POLICY_MODE="${FLEXT_PYDANTIC_POLICY_MODE:-baseline}"
AUTO_FIX_PYDANTIC="${FLEXT_PYDANTIC_AUTO_FIX:-false}"

mkdir -p "$REPORT_DIR"
SUMMARY_FILE="$REPORT_DIR/scripts-validation--txt--automated-validation-summary.txt"
FAILED_STEPS=()

if [[ "$MODE" != "quick" && "$MODE" != "full" ]]; then
  echo "Usage: $0 [quick|full]"
  exit 2
fi

echo "=== FLEXT AUTOMATED VALIDATION ==="
echo "Mode: $MODE"
echo "Policy mode: $POLICY_MODE"
echo "Pydantic policy mode: $PYDANTIC_POLICY_MODE"
echo "Auto-fix pydantic: $AUTO_FIX_PYDANTIC"
echo "Root: $ROOT_DIR"
echo "Report dir: $REPORT_DIR"

run_step() {
  local step=$1
  local cmd=$2
  local log_file=$3
  printf '\n--- %s ---\n' "$step"
  if eval "$cmd" >"$log_file" 2>&1; then
    echo "PASS: $step"
    echo "PASS|$step|$log_file" >>"$SUMMARY_FILE"
  else
    echo "FAIL: $step"
    echo "FAIL|$step|$log_file" >>"$SUMMARY_FILE"
    FAILED_STEPS+=("$step")
    tail -n 40 "$log_file" || true
    return 1
  fi
}

run_step_allow_fail() {
  local step=$1
  local cmd=$2
  local log_file=$3
  if ! run_step "$step" "$cmd" "$log_file"; then
    return 0
  fi
}

: >"$SUMMARY_FILE"

run_step_allow_fail "Policy gate" "scripts/validation/enforce_no_dict_no_any.sh --mode $POLICY_MODE --root '$ROOT_DIR'" "$REPORT_DIR/scripts-validation--log--policy-gate.log"
if [[ "$AUTO_FIX_PYDANTIC" == "true" ]]; then
  run_step_allow_fail "Pydantic auto-fix" "scripts/validation/fix_pydantic_v2_violations.sh --root '$ROOT_DIR'" "$REPORT_DIR/scripts-validation--log--pydantic-autofix.log"
fi
run_step_allow_fail "Pydantic v2 skill gate" "scripts/validation/enforce_pydantic_v2_skill.sh --mode $PYDANTIC_POLICY_MODE --root '$ROOT_DIR'" "$REPORT_DIR/scripts-validation--log--pydantic-policy-gate.log"
run_step_allow_fail "Shell syntax" "bash -n scripts/validation/enforce_no_dict_no_any.sh && bash -n scripts/validation/enforce_pydantic_v2_skill.sh && bash -n scripts/validation/fix_pydantic_v2_violations.sh && bash -n scripts/validation/run_automated_validation.sh && bash -n scripts/validate_all_projects.sh" "$REPORT_DIR/scripts-validation--log--shell-syntax.log"

if [[ "$MODE" == "quick" ]]; then
  printf '\nQuick validation completed\n'
  if [[ ${#FAILED_STEPS[@]} -eq 0 ]]; then
    exit 0
  fi
  printf 'Quick mode failed steps: %s\n' "${FAILED_STEPS[*]}"
  exit 1
fi

run_step_allow_fail "Workspace validator" "scripts/validate_all_projects.sh" "$REPORT_DIR/scripts-validation--log--workspace-validator.log"

if [[ -x "scripts/validate_mypy_all.sh" ]]; then
  run_step_allow_fail "Mypy all" "scripts/validate_mypy_all.sh" "$REPORT_DIR/scripts-validation--log--mypy-all.log"
else
  echo "SKIP: Mypy all (scripts/validate_mypy_all.sh not found)"
  echo "SKIP|Mypy all|not_found" >>"$SUMMARY_FILE"
fi

if [[ -x "scripts/analyze_pyright_all_projects.sh" ]]; then
  run_step_allow_fail "Pyright all" "scripts/analyze_pyright_all_projects.sh" "$REPORT_DIR/scripts-validation--log--pyright-all.log"
else
  echo "SKIP: Pyright all (scripts/analyze_pyright_all_projects.sh not found)"
  echo "SKIP|Pyright all|not_found" >>"$SUMMARY_FILE"
fi

printf '\nFull validation completed\n'
if [[ ${#FAILED_STEPS[@]} -eq 0 ]]; then
  exit 0
fi

printf 'Failed steps: %s\n' "${FAILED_STEPS[*]}"
echo "See summary: $SUMMARY_FILE"
exit 1
