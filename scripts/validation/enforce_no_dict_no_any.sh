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
AST_FILE="$TMP_DIR/ast_dict.jsonl"
KEYED_FILE="$TMP_DIR/keyed_violations.json"

rg_collect "$DICT_RG_FILE" "(?x)\\btyping\\.Dict\\b|\\bDict\\[|\\bdict\\[|\\bisinstance\\([^)]*,\\s*dict\\)|\\bdefault_factory\\s*=\\s*dict\\b|\\.dict\\(|parse_obj\\(|parse_raw\\("
rg_collect "$ANY_RG_FILE" "(?x)\\bAny\\b|\\bobject\\b|\\bcast\\s*\\(|type:\\s*ignore|pyright:\\s*ignore|\\#\\s*noqa"

SG_SCAN_OK="false"
if command -v sg >/dev/null 2>&1; then
  if sg scan \
    --rule "scripts/validation/ast-grep-no-dict.yml" \
    --json=stream \
    --no-ignore hidden \
    "${SG_GLOBS[@]}" \
    "$ROOT_DIR" >"$AST_FILE" 2>"$TMP_DIR/sg.stderr"; then
    SG_SCAN_OK="true"
  else
    SG_SCAN_OK="true"
  fi
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

python3 - "$DICT_RG_FILE" "$ANY_RG_FILE" "$AST_FILE" "$KEYED_FILE" <<'PY_KEYED'
import json, sys
from pathlib import Path

dict_file, any_file, ast_file, out_file = sys.argv[1:5]
violations = []

def parse_rg_line(line, group):
    parts = line.split(":", 2)
    if len(parts) >= 3:
        return {"file": parts[0], "line": int(parts[1]), "group": group,
                "key": f"{group}:{parts[0]}:{parts[1]}"}
    return None

for line in Path(dict_file).read_text().splitlines():
    v = parse_rg_line(line, "dict_legacy")
    if v:
        violations.append(v)

for line in Path(any_file).read_text().splitlines():
    v = parse_rg_line(line, "any_object_cast_ignore")
    if v:
        violations.append(v)

ast_path = Path(ast_file)
if ast_path.exists() and ast_path.stat().st_size > 0:
    for line in ast_path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
            file = obj.get("file", "")
            start = obj.get("range", {}).get("start", {})
            line_no = start.get("line", 0)
            rule_id = obj.get("ruleId", "unknown")
            violations.append({
                "file": file, "line": line_no, "group": "ast_dict_rules",
                "ruleId": rule_id,
                "key": f"ast:{rule_id}:{file}:{line_no}"
            })
        except json.JSONDecodeError:
            continue

keys = sorted({v["key"] for v in violations})
Path(out_file).write_text(json.dumps({
    "scan_succeeded": True,
    "violation_count": len(violations),
    "unique_keys": len(keys),
    "keys": keys,
    "counts": {
        "dict_legacy": sum(1 for v in violations if v["group"] == "dict_legacy"),
        "any_object_cast_ignore": sum(1 for v in violations if v["group"] == "any_object_cast_ignore"),
        "ast_dict_rules": sum(1 for v in violations if v["group"] == "ast_dict_rules"),
    }
}, indent=2) + "\n")
PY_KEYED

write_report_json() {
  python3 - "$KEYED_FILE" "$REPORT_FILE" "$MODE" "$ROOT_DIR" "$DICT_COUNT" "$ANY_COUNT" "$AST_COUNT" "$TOTAL_COUNT" "$SG_SCAN_OK" <<'PY_REPORT'
import json, sys
from pathlib import Path

keyed_file, report_file, mode, root, dict_c, any_c, ast_c, total_c, sg_ok = sys.argv[1:10]
keyed = json.loads(Path(keyed_file).read_text()) if Path(keyed_file).exists() else {}

report = {
    "mode": mode,
    "root": root,
    "scan_succeeded": keyed.get("scan_succeeded", sg_ok == "true"),
    "counts": {
        "dict_legacy": int(dict_c),
        "any_object_cast_ignore": int(any_c),
        "ast_dict_rules": int(ast_c),
        "total": int(total_c),
    },
    "unique_keys": keyed.get("unique_keys", 0),
    "keys": keyed.get("keys", []),
}
Path(report_file).write_text(json.dumps(report, indent=2) + "\n")
PY_REPORT
}

write_baseline_json() {
  python3 - "$KEYED_FILE" "$BASELINE_FILE" "$DICT_COUNT" "$ANY_COUNT" "$AST_COUNT" "$TOTAL_COUNT" <<'PY_BASELINE'
import json, sys
from pathlib import Path

keyed_file, baseline_file, dict_c, any_c, ast_c, total_c = sys.argv[1:7]
keyed = json.loads(Path(keyed_file).read_text()) if Path(keyed_file).exists() else {}

baseline = {
    "counts": {
        "dict_legacy": int(dict_c),
        "any_object_cast_ignore": int(any_c),
        "ast_dict_rules": int(ast_c),
        "total": int(total_c),
    },
    "unique_keys": keyed.get("unique_keys", 0),
    "keys": keyed.get("keys", []),
}
Path(baseline_file).write_text(json.dumps(baseline, indent=2) + "\n")
PY_BASELINE
}

extract_baseline_count() {
  local key=$1
  if [[ ! -f "$BASELINE_FILE" ]]; then
    echo 0
    return
  fi
  local value
  value=$(
    python3 - <<PY
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
  head -n "$limit" "$file"
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

  if [[ -f "$BASELINE_FILE" ]]; then
    NEW_KEYS=$(
      python3 - "$KEYED_FILE" "$BASELINE_FILE" <<'PY_KEYDIFF'
import json, sys
from pathlib import Path
keyed_file, baseline_file = sys.argv[1:3]
current_keys = set(json.loads(Path(keyed_file).read_text()).get("keys", []))
baseline_keys = set(json.loads(Path(baseline_file).read_text()).get("keys", []))
new_keys = current_keys - baseline_keys
fixed_keys = baseline_keys - current_keys
print(f"{len(new_keys)}|{len(fixed_keys)}")
PY_KEYDIFF
    )
    NEW_COUNT="${NEW_KEYS%%|*}"
    FIXED_COUNT="${NEW_KEYS##*|}"
    echo "Key-based: new=$NEW_COUNT fixed=$FIXED_COUNT"
    if [[ "$NEW_COUNT" -gt 0 ]]; then
      FAILED=1
      echo "Key-based regression: $NEW_COUNT new violations introduced"
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
  print_samples "Top AST hits (JSONL)" "$AST_FILE" 10
  exit 1
fi

echo "Policy gate passed"
