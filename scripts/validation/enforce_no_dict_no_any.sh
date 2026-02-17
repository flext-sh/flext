#!/bin/bash

set -euo pipefail

ROOT_DIR="."
MODE="${FLEXT_POLICY_MODE:-baseline}"
UPDATE_BASELINE="false"
BASELINE_FILE=".sisyphus/baselines/policy_gate_baseline.json"
REPORT_FILE=".sisyphus/reports/policy_gate_latest.json"
BASELINE_STRATEGY="${FLEXT_POLICY_BASELINE_STRATEGY:-total}"

while [[ $# -gt 0 ]]; do
  case "$1" in
  --root)
    ROOT_DIR="$2"
    shift 2
    ;;
  --mode)
    MODE="$2"
    shift 2
    ;;
  --baseline-file)
    BASELINE_FILE="$2"
    shift 2
    ;;
  --report-file)
    REPORT_FILE="$2"
    shift 2
    ;;
  --update-baseline)
    UPDATE_BASELINE="true"
    shift
    ;;
  --baseline-strategy)
    BASELINE_STRATEGY="$2"
    shift 2
    ;;
  *)
    ROOT_DIR="$1"
    shift
    ;;
  esac
done

if [[ "$MODE" != "strict" && "$MODE" != "baseline" ]]; then
  echo "Invalid --mode '$MODE' (expected strict|baseline)"
  exit 2
fi

if [[ "$BASELINE_STRATEGY" != "total" && "$BASELINE_STRATEGY" != "per_group" ]]; then
  echo "Invalid --baseline-strategy '$BASELINE_STRATEGY' (expected total|per_group)"
  exit 2
fi

mkdir -p "$(dirname "$REPORT_FILE")" "$(dirname "$BASELINE_FILE")"

RG_COMMON=(
  --hidden
  --glob '*.py'
  --glob '!**/.git/**'
  --glob '!**/.venv/**'
  --glob '!**/venv/**'
  --glob '!**/.mypy_cache/**'
  --glob '!**/.ruff_cache/**'
  --glob '!**/.pytest_cache/**'
  --glob '!**/__pycache__/**'
  --glob '!**/.tox/**'
  --glob '!**/dist/**'
  --glob '!**/build/**'
)

SG_GLOBS=(
  --globs '**/*.py'
  --globs '!**/.git/**'
  --globs '!**/.venv/**'
  --globs '!**/venv/**'
  --globs '!**/.mypy_cache/**'
  --globs '!**/.ruff_cache/**'
  --globs '!**/.pytest_cache/**'
  --globs '!**/__pycache__/**'
  --globs '!**/.tox/**'
  --globs '!**/dist/**'
  --globs '!**/build/**'
)

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "=== POLICY GATE: no-dict no-any no-legacy ==="
echo "Mode: $MODE"
echo "Root: $ROOT_DIR"

rg_collect() {
  local output_file=$1
  local pattern=$2
  rg -n "$pattern" "${RG_COMMON[@]}" "$ROOT_DIR" >"$output_file" || true
}

DICT_RG_FILE="$TMP_DIR/dict_legacy.txt"
ANY_RG_FILE="$TMP_DIR/any_object_cast_ignore.txt"
AST_FILE="$TMP_DIR/ast_dict.txt"

rg_collect "$DICT_RG_FILE" "(?x)\\btyping\\.Dict\\b|\\bDict\\[|\\bdict\\[|\\bisinstance\\([^)]*,\\s*dict\\)|\\bdefault_factory\\s*=\\s*dict\\b|\\.dict\\(|parse_obj\\(|parse_raw\\("
rg_collect "$ANY_RG_FILE" "(?x)\\bAny\\b|\\bobject\\b|\\bcast\\s*\\(|type:\\s*ignore|pyright:\\s*ignore|\\#\\s*noqa"

if command -v sg >/dev/null 2>&1; then
  sg scan \
    --rule "scripts/validation/ast-grep-no-dict.yml" \
    --json=stream \
    --no-ignore hidden \
    "${SG_GLOBS[@]}" \
    "$ROOT_DIR" >"$AST_FILE" 2>"$TMP_DIR/sg.stderr" || true
else
  : >"$AST_FILE"
  echo "Warning: ast-grep not found; AST checks skipped"
fi

count_lines() {
  local file=$1
  if [[ -s "$file" ]]; then
    wc -l <"$file" | tr -d ' '
  else
    echo 0
  fi
}

DICT_COUNT=$(count_lines "$DICT_RG_FILE")
ANY_COUNT=$(count_lines "$ANY_RG_FILE")
AST_COUNT=$(count_lines "$AST_FILE")
TOTAL_COUNT=$((DICT_COUNT + ANY_COUNT + AST_COUNT))

write_report_json() {
  cat >"$REPORT_FILE" <<EOF
{
  "mode": "$MODE",
  "root": "$ROOT_DIR",
  "counts": {
    "dict_legacy": $DICT_COUNT,
    "any_object_cast_ignore": $ANY_COUNT,
    "ast_dict_rules": $AST_COUNT,
    "total": $TOTAL_COUNT
  }
}
EOF
}

write_baseline_json() {
  cat >"$BASELINE_FILE" <<EOF
{
  "counts": {
    "dict_legacy": $DICT_COUNT,
    "any_object_cast_ignore": $ANY_COUNT,
    "ast_dict_rules": $AST_COUNT,
    "total": $TOTAL_COUNT
  }
}
EOF
}

extract_baseline_count() {
  local key=$1
  if [[ ! -f "$BASELINE_FILE" ]]; then
    echo 0
    return
  fi
  local value
  value=$(
    python - <<PY
import json
from pathlib import Path
path = Path("$BASELINE_FILE")
if not path.exists():
    print(0)
else:
    data = json.loads(path.read_text())
    print(int(data.get("counts", {}).get("$key", 0)))
PY
  )
  echo "$value"
}

print_samples() {
  local title=$1
  local file=$2
  local limit=$3
  if [[ ! -s "$file" ]]; then
    echo "$title: 0"
    return
  fi
  echo "$title: $(count_lines "$file")"
  python - <<PY
from pathlib import Path
lines = Path("$file").read_text().splitlines()
for line in lines[:$limit]:
    print(line)
PY
}

write_report_json

if [[ "$UPDATE_BASELINE" == "true" ]]; then
  write_baseline_json
  echo "Baseline updated: $BASELINE_FILE"
fi

if [[ "$MODE" == "baseline" && ! -f "$BASELINE_FILE" ]]; then
  write_baseline_json
  echo "Baseline initialized: $BASELINE_FILE"
fi

echo "Summary: dict_legacy=$DICT_COUNT any_object_cast_ignore=$ANY_COUNT ast_dict_rules=$AST_COUNT total=$TOTAL_COUNT"
echo "Report: $REPORT_FILE"

FAILED=0
if [[ "$MODE" == "strict" ]]; then
  if [[ "$TOTAL_COUNT" -gt 0 ]]; then
    FAILED=1
  fi
else
  BASE_DICT=$(extract_baseline_count dict_legacy)
  BASE_ANY=$(extract_baseline_count any_object_cast_ignore)
  BASE_AST=$(extract_baseline_count ast_dict_rules)
  BASE_TOTAL=$((BASE_DICT + BASE_ANY + BASE_AST))
  if [[ "$BASELINE_STRATEGY" == "per_group" ]]; then
    if [[ "$DICT_COUNT" -gt "$BASE_DICT" || "$ANY_COUNT" -gt "$BASE_ANY" || "$AST_COUNT" -gt "$BASE_AST" ]]; then
      FAILED=1
    fi
  else
    if [[ "$TOTAL_COUNT" -gt "$BASE_TOTAL" ]]; then
      FAILED=1
    fi
  fi
  echo "Baseline strategy: $BASELINE_STRATEGY"
  echo "Baseline: dict_legacy=$BASE_DICT any_object_cast_ignore=$BASE_ANY ast_dict_rules=$BASE_AST"
  echo "Delta: dict_legacy=$((DICT_COUNT - BASE_DICT)) any_object_cast_ignore=$((ANY_COUNT - BASE_ANY)) ast_dict_rules=$((AST_COUNT - BASE_AST)) total=$((TOTAL_COUNT - BASE_TOTAL))"
fi

if [[ "$FAILED" -eq 1 ]]; then
  echo "Policy gate failed"
  print_samples "Top dict/legacy hits" "$DICT_RG_FILE" 10
  print_samples "Top Any/object/cast/ignore hits" "$ANY_RG_FILE" 10
  print_samples "Top AST hits" "$AST_FILE" 10
  exit 1
fi

echo "Policy gate passed"
