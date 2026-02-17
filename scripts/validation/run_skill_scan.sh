#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-validation/SKILL.md
set -euo pipefail

ROOT_DIR="${1:-.}"
SKILLS_DIR=".claude/skills"
REPORT_FILE=".sisyphus/reports/scripts-validation--json--skill-scan-latest.json"

mkdir -p "$(dirname "$REPORT_FILE")"

if ! command -v sg >/dev/null 2>&1; then
  echo "Error: ast-grep (sg) required"
  exit 2
fi

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

echo "=== SKILL-DRIVEN AST-GREP SCAN ==="
echo "Root: $ROOT_DIR"
echo "Skills dir: $SKILLS_DIR"

PACK_INDEX=0
TOTAL_VIOLATIONS=0

: >"$TMP_DIR/packs.jsonl"

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_file="$skill_dir/SKILL.md"
  [[ -f "$skill_file" ]] || continue

  while IFS= read -r line; do
    pack_path="${line#*ASTGREP_SCAN_PACK: }"
    pack_path="${pack_path% -->}"
    pack_path="$(echo "$pack_path" | xargs)"

    [[ -f "$pack_path" ]] || {
      echo "WARN: Pack not found: $pack_path (from $skill_file)"
      continue
    }

    skill_name="$(basename "$skill_dir")"
    echo "Scanning: $skill_name -> $pack_path"

    SCAN_OUT="$TMP_DIR/scan_${PACK_INDEX}.jsonl"
    PACK_INDEX=$((PACK_INDEX + 1))

    if sg scan \
      --rule "$pack_path" \
      --json=stream \
      --no-ignore hidden \
      "${SG_GLOBS[@]}" \
      "$ROOT_DIR" >"$SCAN_OUT" 2>"$TMP_DIR/sg_${PACK_INDEX}.stderr"; then
      true
    fi

    PACK_COUNT=0
    if [[ -s "$SCAN_OUT" ]]; then
      PACK_COUNT=$(wc -l <"$SCAN_OUT" | tr -d ' ')
    fi
    TOTAL_VIOLATIONS=$((TOTAL_VIOLATIONS + PACK_COUNT))

    echo "{\"skill\":\"$skill_name\",\"pack\":\"$pack_path\",\"violations\":$PACK_COUNT}" >>"$TMP_DIR/packs.jsonl"
    echo "  -> $PACK_COUNT violations"
  done < <(grep '<!-- ASTGREP_SCAN_PACK:' "$skill_file" 2>/dev/null || true)
done

python3 - "$TMP_DIR/packs.jsonl" "$REPORT_FILE" "$PACK_INDEX" "$TOTAL_VIOLATIONS" <<'PY_REPORT'
import json, sys
from pathlib import Path

packs_file, report_file, pack_count, total_v = sys.argv[1:5]
packs = []
packs_path = Path(packs_file)
if packs_path.exists() and packs_path.stat().st_size > 0:
    for line in packs_path.read_text().splitlines():
        if line.strip():
            packs.append(json.loads(line))

report = {
    "packs_scanned": int(pack_count),
    "total_violations": int(total_v),
    "packs": packs,
}
Path(report_file).write_text(json.dumps(report, indent=2) + "\n")
PY_REPORT

echo ""
echo "=== SCAN COMPLETE ==="
echo "Packs scanned: $PACK_INDEX"
echo "Total violations: $TOTAL_VIOLATIONS"
echo "Report: $REPORT_FILE"

if [[ "$TOTAL_VIOLATIONS" -gt 0 ]]; then
  exit 1
fi
