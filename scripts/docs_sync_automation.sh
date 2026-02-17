#!/usr/bin/env bash
# Owner-Skill: .claude/skills/scripts-maintenance/SKILL.md
set -euo pipefail

ROOT_DIR="."
APPLY=false
DO_COMMIT=false

for arg in "$@"; do
  case "$arg" in
  --apply)
    APPLY=true
    ;;
  --commit)
    DO_COMMIT=true
    ;;
  --root=*)
    ROOT_DIR="${arg#*=}"
    ;;
  *) ;;
  esac
done

python3 scripts/docs_maintenance_audit.py --root "$ROOT_DIR" --output docs_audit_report.md --format markdown

if [ "$APPLY" = true ]; then
  python3 scripts/docs_link_fixer.py --root "$ROOT_DIR" --apply
  python3 scripts/docs_toc_generator.py --root "$ROOT_DIR" --apply
else
  python3 scripts/docs_link_fixer.py --root "$ROOT_DIR"
  python3 scripts/docs_toc_generator.py --root "$ROOT_DIR"
fi

if [ "$DO_COMMIT" = true ]; then
  git add -A
  if ! git diff --cached --quiet; then
    git commit -m "docs: apply automated documentation sync"
  fi
fi

echo "docs_sync_complete apply=$APPLY commit=$DO_COMMIT"
