#!/bin/bash

set -euo pipefail

ROOT_DIR="."
DRY_RUN="false"
AGGRESSIVE_INSTANCE_METHODS="${FLEXT_PYDANTIC_AUTOFIX_AGGRESSIVE:-false}"

while [[ $# -gt 0 ]]; do
  case "$1" in
  --root)
    ROOT_DIR="$2"
    shift 2
    ;;
  --dry-run)
    DRY_RUN="true"
    shift
    ;;
  --aggressive)
    AGGRESSIVE_INSTANCE_METHODS="true"
    shift
    ;;
  *)
    ROOT_DIR="$1"
    shift
    ;;
  esac
done

if ! command -v sg >/dev/null 2>&1; then
  echo "Error: ast-grep (sg) is required for auto-fix"
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
  --globs '!**/docs/**'
)

UPDATE_FLAG=()
if [[ "$DRY_RUN" == "false" ]]; then
  UPDATE_FLAG=(--update-all)
fi

echo "=== Auto-fix Pydantic v2 Violations ==="
echo "Root: $ROOT_DIR"
echo "Dry-run: $DRY_RUN"
echo "Aggressive instance-method rewrites: $AGGRESSIVE_INSTANCE_METHODS"

rewrite_rule() {
  local label=$1
  local pattern=$2
  local rewrite=$3
  echo "\n--- $label ---"
  sg run \
    --lang python \
    --pattern "$pattern" \
    --rewrite "$rewrite" \
    "${SG_GLOBS[@]}" \
    "${UPDATE_FLAG[@]}" \
    "$ROOT_DIR" || true
}

rewrite_rule "Rewrite .parse_obj() -> .model_validate()" '$MODEL.parse_obj($ARG)' '$MODEL.model_validate($ARG)'
rewrite_rule "Rewrite .parse_raw() -> .model_validate_json()" '$MODEL.parse_raw($ARG)' '$MODEL.model_validate_json($ARG)'
rewrite_rule "Rewrite .from_orm() -> .model_validate()" '$MODEL.from_orm($ARG)' '$MODEL.model_validate($ARG)'

if [[ "$AGGRESSIVE_INSTANCE_METHODS" == "true" ]]; then
  rewrite_rule "Rewrite .dict() -> .model_dump()" '$MODEL.dict($$$ARGS)' '$MODEL.model_dump($$$ARGS)'
  rewrite_rule "Rewrite .json() -> .model_dump_json()" '$MODEL.json($$$ARGS)' '$MODEL.model_dump_json($$$ARGS)'
else
  echo "\nSkipping aggressive rewrites for .dict() and .json() by default"
fi

echo "\nAuto-fix run completed"
