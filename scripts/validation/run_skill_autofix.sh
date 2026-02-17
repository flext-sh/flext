#!/bin/bash
set -euo pipefail

ROOT_DIR="."
FIX_MODE="safe"
DRY_RUN="false"
APPLY="false"
REPORT_FILE=".sisyphus/reports/autofix_latest.json"
SKILLS_DIR=".claude/skills"
DEGRADED="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
  --root)
    ROOT_DIR="$2"
    shift 2
    ;;
  --mode)
    FIX_MODE="$2"
    shift 2
    ;;
  --dry-run)
    DRY_RUN="true"
    shift
    ;;
  --apply)
    APPLY="true"
    shift
    ;;
  --report-file)
    REPORT_FILE="$2"
    shift 2
    ;;
  --degraded)
    DEGRADED="true"
    shift
    ;;
  *)
    ROOT_DIR="$1"
    shift
    ;;
  esac
done

if [[ "$FIX_MODE" != "safe" && "$FIX_MODE" != "risky" ]]; then
  echo "Invalid --mode '$FIX_MODE' (expected safe|risky)"
  exit 2
fi

if [[ "$DRY_RUN" == "false" && "$APPLY" == "false" ]]; then
  echo "Specify --dry-run or --apply"
  exit 2
fi

for tool in sg python3 ruff; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Error: $tool required"
    exit 2
  fi
done

for tool in mypy pyright pyrefly; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    if [[ "$DEGRADED" == "false" ]]; then
      echo "Error: $tool not found. Use --degraded to skip."
      exit 2
    fi
  fi
done

mkdir -p "$(dirname "$REPORT_FILE")"

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

METRICS_SCRIPT="scripts/validation/collect_file_metrics.py"

echo "=== SKILL-DRIVEN AUTO-FIX ==="
echo "Root: $ROOT_DIR"
echo "Mode: $FIX_MODE"
echo "Dry-run: $DRY_RUN"
echo "Apply: $APPLY"

collect_fix_packs() {
  local mode_filter="$1"
  local packs=()
  for skill_dir in "$SKILLS_DIR"/*/; do
    local skill_file="$skill_dir/SKILL.md"
    [[ -f "$skill_file" ]] || continue

    local autofix_mode=""
    autofix_mode=$(grep '<!-- AUTOFIX_MODE:' "$skill_file" 2>/dev/null | head -1 | sed 's/.*AUTOFIX_MODE: *//;s/ *-->.*//' || true)

    if [[ "$mode_filter" == "safe" && "$autofix_mode" != "safe" ]]; then
      continue
    fi

    while IFS= read -r line; do
      local pack_path="${line#*ASTGREP_FIX_PACK: }"
      pack_path="${pack_path% -->}"
      pack_path="$(echo "$pack_path" | xargs)"
      [[ -f "$pack_path" ]] && packs+=("$pack_path")
    done < <(grep '<!-- ASTGREP_FIX_PACK:' "$skill_file" 2>/dev/null || true)
  done
  echo "${packs[@]}"
}

FIX_PACKS=$(collect_fix_packs "$FIX_MODE")

if [[ -z "$FIX_PACKS" ]]; then
  echo "No fix packs found for mode=$FIX_MODE"
  echo '{"packs":[],"candidates":[],"accepted":[],"rejected":[],"project_rejections":[]}' >"$REPORT_FILE"
  exit 0
fi

echo "Fix packs: $FIX_PACKS"

find_candidate_files() {
  local pack=$1
  sg scan --rule "$pack" --json=stream --no-ignore hidden "${SG_GLOBS[@]}" "$ROOT_DIR" 2>/dev/null |
    python3 -c "
import sys, json
files = set()
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        obj = json.loads(line)
        f = obj.get('file', '')
        if f:
            files.add(f)
    except json.JSONDecodeError:
        continue
for f in sorted(files):
    print(f)
" || true
}

detect_project() {
  local filepath="$1"
  local first_dir="${filepath%%/*}"
  if [[ -d "$first_dir" && ("$first_dir" == flext-* || "$first_dir" == client-a-* || "$first_dir" == flexcore) ]]; then
    echo "$first_dir"
  else
    echo "__root__"
  fi
}

DEGRADED_FLAG=""
if [[ "$DEGRADED" == "true" ]]; then
  DEGRADED_FLAG="--degraded"
fi

backup_name_for() {
  local filepath="$1"
  echo "$TMP_DIR/backup_$(echo "$filepath" | sed 's|/|__|g')"
}

collect_before_metrics() {
  local file="$1"
  local project="$2"
  python3 "$METRICS_SCRIPT" --file "$file" --project-dir "$project" $DEGRADED_FLAG 2>/dev/null || true
}

: >"$TMP_DIR/candidates.txt"
: >"$TMP_DIR/accepted.jsonl"
: >"$TMP_DIR/rejected.jsonl"
: >"$TMP_DIR/project_rejections.jsonl"

for pack in $FIX_PACKS; do
  echo ""
  echo "--- Finding candidates: $pack ---"
  find_candidate_files "$pack" >>"$TMP_DIR/candidates.txt"
done

sort -u "$TMP_DIR/candidates.txt" >"$TMP_DIR/candidates_unique.txt"
CANDIDATE_COUNT=$(wc -l <"$TMP_DIR/candidates_unique.txt" | tr -d ' ')
echo "Unique candidate files: $CANDIDATE_COUNT"

if [[ "$DRY_RUN" == "true" ]]; then
  echo ""
  echo "=== DRY-RUN REPORT ==="
  echo "Would process $CANDIDATE_COUNT files"

  python3 - "$TMP_DIR/candidates_unique.txt" "$REPORT_FILE" <<'PY_DRYRUN'
import json, sys
from pathlib import Path

cands = Path(sys.argv[1]).read_text().splitlines()
cands = [c for c in cands if c.strip()]
report = {
    "mode": "dry-run",
    "candidate_count": len(cands),
    "candidates": cands,
    "accepted": [],
    "rejected": [],
    "project_rejections": [],
}
Path(sys.argv[2]).write_text(json.dumps(report, indent=2) + "\n")
PY_DRYRUN

  echo "Report: $REPORT_FILE"
  exit 0
fi

declare -A PROJECT_BEFORE_TOTALS
declare -A PROJECT_AFTER_TOTALS
declare -A PROJECT_FILES

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

while IFS= read -r candidate; do
  [[ -z "$candidate" ]] && continue
  [[ -f "$candidate" ]] || continue

  project=$(detect_project "$candidate")

  echo ""
  echo "Processing: $candidate (project: $project)"

  BEFORE_METRICS=$(collect_before_metrics "$candidate" "$project")
  BEFORE_TOTAL=$(echo "$BEFORE_METRICS" | python3 -c "
import sys, json
total = 0
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        obj = json.loads(line)
        c = obj.get('count', 0)
        if c >= 0: total += c
    except: continue
print(total)
" 2>/dev/null || echo "0")

  cp "$candidate" "$TMP_DIR/backup_$(basename "$candidate")"

  for pack in $FIX_PACKS; do
    sg scan --rule "$pack" --update-all --no-ignore hidden "${SG_GLOBS[@]}" "$candidate" 2>/dev/null || true
  done

  if cmp -s "$candidate" "$TMP_DIR/backup_$(basename "$candidate")"; then
    echo "  No changes made"
    continue
  fi

  AFTER_METRICS=$(collect_before_metrics "$candidate" "$project")
  AFTER_TOTAL=$(echo "$AFTER_METRICS" | python3 -c "
import sys, json
total = 0
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        obj = json.loads(line)
        c = obj.get('count', 0)
        if c >= 0: total += c
    except: continue
print(total)
" 2>/dev/null || echo "0")

  echo "  Before: $BEFORE_TOTAL -> After: $AFTER_TOTAL"

  if [[ "$AFTER_TOTAL" -lt "$BEFORE_TOTAL" ]]; then
    echo "  ACCEPTED (metrics improved)"
    echo "{\"file\":\"$candidate\",\"project\":\"$project\",\"before\":$BEFORE_TOTAL,\"after\":$AFTER_TOTAL,\"status\":\"accepted\"}" >>"$TMP_DIR/accepted.jsonl"

    PROJECT_BEFORE_TOTALS["$project"]=$((${PROJECT_BEFORE_TOTALS["$project"]:-0} + BEFORE_TOTAL))
    PROJECT_AFTER_TOTALS["$project"]=$((${PROJECT_AFTER_TOTALS["$project"]:-0} + AFTER_TOTAL))
    PROJECT_FILES["$project"]="${PROJECT_FILES["$project"]:-} $candidate"
  else
    echo "  REJECTED (metrics did not improve)"
    REJ_BAK="${candidate}.rej-${TIMESTAMP}.bak"
    REJ_REPORT="${candidate}.rej-${TIMESTAMP}.rej"

    cp "$candidate" "$REJ_BAK"

    cat >"$REJ_REPORT" <<REJEOF
File: $candidate
Timestamp: $TIMESTAMP
Before total: $BEFORE_TOTAL
After total: $AFTER_TOTAL
Delta: $((AFTER_TOTAL - BEFORE_TOTAL))

Before metrics:
$BEFORE_METRICS

After metrics:
$AFTER_METRICS
REJEOF

    cp "$TMP_DIR/backup_$(basename "$candidate")" "$candidate"
    echo "  Restored original, created $REJ_BAK and $REJ_REPORT"
    echo "{\"file\":\"$candidate\",\"project\":\"$project\",\"before\":$BEFORE_TOTAL,\"after\":$AFTER_TOTAL,\"status\":\"rejected\",\"rej_bak\":\"$REJ_BAK\",\"rej_report\":\"$REJ_REPORT\"}" >>"$TMP_DIR/rejected.jsonl"
  fi
done <"$TMP_DIR/candidates_unique.txt"

echo ""
echo "=== PROJECT-LEVEL SAFETY CHECK ==="

for project in "${!PROJECT_BEFORE_TOTALS[@]}"; do
  P_BEFORE="${PROJECT_BEFORE_TOTALS[$project]}"
  P_AFTER="${PROJECT_AFTER_TOTALS[$project]}"

  echo "Project $project: before=$P_BEFORE after=$P_AFTER"

  if [[ "$P_AFTER" -ge "$P_BEFORE" ]]; then
    echo "  PROJECT REJECTION: $project metrics worsened or unchanged (before=$P_BEFORE, after=$P_AFTER)"
    echo "  Rolling back all accepted files in $project..."

    for accepted_file in ${PROJECT_FILES[$project]}; do
      [[ -z "$accepted_file" ]] && continue
      backup_name="$TMP_DIR/backup_$(basename "$accepted_file")"
      if [[ -f "$backup_name" ]]; then
        REJ_BAK="${accepted_file}.rej-${TIMESTAMP}.bak"
        REJ_REPORT="${accepted_file}.rej-${TIMESTAMP}.rej"

        cp "$accepted_file" "$REJ_BAK"

        cat >"$REJ_REPORT" <<REJEOF
File: $accepted_file
Timestamp: $TIMESTAMP
Reason: Project-level rejection ($project aggregate worsened)
Project before total: $P_BEFORE
Project after total: $P_AFTER

REJEOF

        cp "$backup_name" "$accepted_file"
        echo "  Rolled back: $accepted_file"
      fi
    done

    echo "{\"project\":\"$project\",\"before\":$P_BEFORE,\"after\":$P_AFTER,\"files_rolled_back\":\"${PROJECT_FILES[$project]}\"}" >>"$TMP_DIR/project_rejections.jsonl"
  else
    echo "  Project $project OK (improved)"
  fi
done

python3 - "$TMP_DIR/accepted.jsonl" "$TMP_DIR/rejected.jsonl" "$TMP_DIR/project_rejections.jsonl" "$REPORT_FILE" <<'PY_FINAL'
import json, sys
from pathlib import Path

def read_jsonl(path):
    result = []
    p = Path(path)
    if p.exists() and p.stat().st_size > 0:
        for line in p.read_text().splitlines():
            if line.strip():
                try:
                    result.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return result

accepted_f, rejected_f, proj_rej_f, report_f = sys.argv[1:5]

report = {
    "mode": "apply",
    "accepted": read_jsonl(accepted_f),
    "rejected": read_jsonl(rejected_f),
    "project_rejections": read_jsonl(proj_rej_f),
    "summary": {
        "accepted_count": len(read_jsonl(accepted_f)),
        "rejected_count": len(read_jsonl(rejected_f)),
        "project_rejections_count": len(read_jsonl(proj_rej_f)),
    }
}
Path(report_f).write_text(json.dumps(report, indent=2) + "\n")
PY_FINAL

echo ""
echo "=== AUTO-FIX COMPLETE ==="
echo "Report: $REPORT_FILE"

python3 -c "
import json
from pathlib import Path
r = json.loads(Path('$REPORT_FILE').read_text())
s = r.get('summary', {})
print(f\"Accepted: {s.get('accepted_count', 0)}\")
print(f\"Rejected: {s.get('rejected_count', 0)}\")
print(f\"Project rejections: {s.get('project_rejections_count', 0)}\")
"
