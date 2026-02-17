#!/bin/bash
# Owner-Skill: .claude/skills/scripts-validation/SKILL.md

set -euo pipefail

ROOT_DIR="."
MODE="${FLEXT_PYDANTIC_POLICY_MODE:-baseline}"
UPDATE_BASELINE="false"
BASELINE_FILE=".sisyphus/baselines/scripts-validation--json--pydantic-v2-policy-baseline.json"
REPORT_FILE=".sisyphus/reports/scripts-validation--json--pydantic-v2-policy-latest.json"
BASELINE_STRATEGY="${FLEXT_PYDANTIC_BASELINE_STRATEGY:-total}"

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

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

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
  --globs '!**/docs/**'
)

echo "=== Pydantic v2 Skill Policy Gate ==="
echo "Mode: $MODE"
echo "Root: $ROOT_DIR"

if ! command -v sg >/dev/null 2>&1; then
  echo "Error: ast-grep (sg) is required for pydantic skill policy gate"
  exit 2
fi

SG_ALL="$TMP_DIR/sg_all.jsonl"
sg scan \
  --rule "scripts/validation/ast-grep-pydantic-v2.yml" \
  --json=stream \
  --no-ignore hidden \
  "${SG_GLOBS[@]}" \
  "$ROOT_DIR" >"$SG_ALL" 2>"$TMP_DIR/sg.stderr" || true

extract_count() {
  local rule_id=$1
  python - <<PY
from pathlib import Path
import json
file_path = Path("$SG_ALL")
count = 0
if file_path.exists() and file_path.stat().st_size > 0:
    for line in file_path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("ruleId") == "$rule_id":
            count += 1
print(count)
PY
}

MODEL_REBUILD_COUNT=$(extract_count ban-model-rebuild-call)
DICT_V1_COUNT=$(extract_count ban-pydantic-v1-dict)
PARSE_OBJ_COUNT=$(extract_count ban-pydantic-v1-parse-obj)
PARSE_RAW_COUNT=$(extract_count ban-pydantic-v1-parse-raw)
JSON_V1_COUNT=$(extract_count ban-pydantic-v1-json)
FROM_ORM_COUNT=$(extract_count ban-pydantic-v1-from-orm)
VALIDATOR_COUNT=$(extract_count ban-pydantic-v1-validator-decorator)
ROOT_VALIDATOR_COUNT=$(extract_count ban-pydantic-v1-root-validator-decorator)
TOTAL_COUNT=$((MODEL_REBUILD_COUNT + DICT_V1_COUNT + PARSE_OBJ_COUNT + PARSE_RAW_COUNT + JSON_V1_COUNT + FROM_ORM_COUNT + VALIDATOR_COUNT + ROOT_VALIDATOR_COUNT))

write_report_json() {
  cat >"$REPORT_FILE" <<EOF
{
  "mode": "$MODE",
  "root": "$ROOT_DIR",
  "counts": {
    "model_rebuild": $MODEL_REBUILD_COUNT,
    "v1_dict": $DICT_V1_COUNT,
    "v1_parse_obj": $PARSE_OBJ_COUNT,
    "v1_parse_raw": $PARSE_RAW_COUNT,
    "v1_json": $JSON_V1_COUNT,
    "v1_from_orm": $FROM_ORM_COUNT,
    "v1_validator": $VALIDATOR_COUNT,
    "v1_root_validator": $ROOT_VALIDATOR_COUNT,
    "total": $TOTAL_COUNT
  }
}
EOF
}

write_baseline_json() {
  cat >"$BASELINE_FILE" <<EOF
{
  "counts": {
    "model_rebuild": $MODEL_REBUILD_COUNT,
    "v1_dict": $DICT_V1_COUNT,
    "v1_parse_obj": $PARSE_OBJ_COUNT,
    "v1_parse_raw": $PARSE_RAW_COUNT,
    "v1_json": $JSON_V1_COUNT,
    "v1_from_orm": $FROM_ORM_COUNT,
    "v1_validator": $VALIDATOR_COUNT,
    "v1_root_validator": $ROOT_VALIDATOR_COUNT,
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
}

print_samples() {
  local title=$1
  local rule_id=$2
  local limit=$3
  python - <<PY
from pathlib import Path
import json
path = Path("$SG_ALL")
matches = []
if path.exists() and path.stat().st_size > 0:
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("ruleId") == "$rule_id":
            file = obj.get("file", "")
            start = obj.get("range", {}).get("start", {})
            line_no = start.get("line", 0)
            text = obj.get("text", "").strip().replace("\n", " ")
            matches.append(f"{file}:{line_no}:{text}")
print("$title: " + str(len(matches)))
for row in matches[:$limit]:
    print(row)
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

echo "Summary: model_rebuild=$MODEL_REBUILD_COUNT v1_dict=$DICT_V1_COUNT v1_parse_obj=$PARSE_OBJ_COUNT v1_parse_raw=$PARSE_RAW_COUNT v1_json=$JSON_V1_COUNT v1_from_orm=$FROM_ORM_COUNT v1_validator=$VALIDATOR_COUNT v1_root_validator=$ROOT_VALIDATOR_COUNT total=$TOTAL_COUNT"
echo "Report: $REPORT_FILE"

FAILED=0
if [[ "$MODE" == "strict" ]]; then
  if [[ "$TOTAL_COUNT" -gt 0 ]]; then
    FAILED=1
  fi
else
  BASE_REBUILD=$(extract_baseline_count model_rebuild)
  BASE_DICT=$(extract_baseline_count v1_dict)
  BASE_PARSE_OBJ=$(extract_baseline_count v1_parse_obj)
  BASE_PARSE_RAW=$(extract_baseline_count v1_parse_raw)
  BASE_JSON=$(extract_baseline_count v1_json)
  BASE_FROM_ORM=$(extract_baseline_count v1_from_orm)
  BASE_VALIDATOR=$(extract_baseline_count v1_validator)
  BASE_ROOT_VALIDATOR=$(extract_baseline_count v1_root_validator)
  BASE_TOTAL=$((BASE_REBUILD + BASE_DICT + BASE_PARSE_OBJ + BASE_PARSE_RAW + BASE_JSON + BASE_FROM_ORM + BASE_VALIDATOR + BASE_ROOT_VALIDATOR))

  if [[ "$BASELINE_STRATEGY" == "per_group" ]]; then
    if [[ "$MODEL_REBUILD_COUNT" -gt "$BASE_REBUILD" || "$DICT_V1_COUNT" -gt "$BASE_DICT" || "$PARSE_OBJ_COUNT" -gt "$BASE_PARSE_OBJ" || "$PARSE_RAW_COUNT" -gt "$BASE_PARSE_RAW" || "$JSON_V1_COUNT" -gt "$BASE_JSON" || "$FROM_ORM_COUNT" -gt "$BASE_FROM_ORM" || "$VALIDATOR_COUNT" -gt "$BASE_VALIDATOR" || "$ROOT_VALIDATOR_COUNT" -gt "$BASE_ROOT_VALIDATOR" ]]; then
      FAILED=1
    fi
  else
    if [[ "$TOTAL_COUNT" -gt "$BASE_TOTAL" ]]; then
      FAILED=1
    fi
  fi

  echo "Baseline strategy: $BASELINE_STRATEGY"
  echo "Baseline: model_rebuild=$BASE_REBUILD v1_dict=$BASE_DICT v1_parse_obj=$BASE_PARSE_OBJ v1_parse_raw=$BASE_PARSE_RAW v1_json=$BASE_JSON v1_from_orm=$BASE_FROM_ORM v1_validator=$BASE_VALIDATOR v1_root_validator=$BASE_ROOT_VALIDATOR"
  echo "Delta: model_rebuild=$((MODEL_REBUILD_COUNT - BASE_REBUILD)) v1_dict=$((DICT_V1_COUNT - BASE_DICT)) v1_parse_obj=$((PARSE_OBJ_COUNT - BASE_PARSE_OBJ)) v1_parse_raw=$((PARSE_RAW_COUNT - BASE_PARSE_RAW)) v1_json=$((JSON_V1_COUNT - BASE_JSON)) v1_from_orm=$((FROM_ORM_COUNT - BASE_FROM_ORM)) v1_validator=$((VALIDATOR_COUNT - BASE_VALIDATOR)) v1_root_validator=$((ROOT_VALIDATOR_COUNT - BASE_ROOT_VALIDATOR)) total=$((TOTAL_COUNT - BASE_TOTAL))"
fi

if [[ "$FAILED" -eq 1 ]]; then
  echo "Pydantic v2 policy gate failed"
  print_samples "Top model_rebuild violations" ban-model-rebuild-call 10
  print_samples "Top v1 .dict violations" ban-pydantic-v1-dict 10
  print_samples "Top v1 parse_obj violations" ban-pydantic-v1-parse-obj 10
  print_samples "Top v1 parse_raw violations" ban-pydantic-v1-parse-raw 10
  print_samples "Top v1 .json violations" ban-pydantic-v1-json 10
  print_samples "Top v1 from_orm violations" ban-pydantic-v1-from-orm 10
  print_samples "Top v1 @validator violations" ban-pydantic-v1-validator-decorator 10
  print_samples "Top v1 @root_validator violations" ban-pydantic-v1-root-validator-decorator 10
  exit 1
fi

echo "Pydantic v2 policy gate passed"
