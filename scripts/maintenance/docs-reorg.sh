#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: docs-reorg.sh [options]

Options:
  --workspace <path>          Workspace root (default: repository root).
  --project <name>            Required. Restrict to one project or "workspace" for root.
  --phases <phases>           Comma-separated doc phases (default: generate,build,audit,validate).
  --run-id <id>               Reuse fixed run identifier.
  --recover-run <id>          Restore docs from .legacy-docs/<id>/<scope>/*.bak and exit.
  --fix                       Pass FIX=1 to docs commands and apply fixer/validator changes.
  --dry-run                   Preview commands without mutating files.
  --help

Examples:
  scripts/maintenance/docs-reorg.sh --project workspace --recover-run 20260624144000
  scripts/maintenance/docs-reorg.sh --project flext-core --phases generate,fix,build,audit,validate --fix
USAGE
}

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUN_ID="$(date +%Y%m%d%H%M%S)"
FIX=0
DRY_RUN=0
PHASES=(generate build audit validate)
PROJECT_FILTER=()
RECOVER_RUN_ID=""

while (($# > 0)); do
  case "$1" in
    --workspace|-w)
      if (($# < 2)); then
        echo "--workspace requires a path" >&2
        exit 1
      fi
      WORKSPACE_ROOT="$2"
      shift 2
      ;;
    --project|-p)
      if (($# < 2)); then
        echo "--project requires a name" >&2
        exit 1
      fi
      if [ "$2" = "workspace" ]; then
        PROJECT_FILTER+=(".")
      else
        PROJECT_FILTER+=("$2")
      fi
      shift 2
      ;;
    --phases)
      if (($# < 2)); then
        echo "--phases requires a value" >&2
        exit 1
      fi
      IFS=',' read -r -a _phases <<< "$2"
      PHASES=("${_phases[@]}")
      shift 2
      ;;
    --run-id)
      if (($# < 2)); then
        echo "--run-id requires a value" >&2
        exit 1
      fi
      RUN_ID="$2"
      shift 2
      ;;
    --recover-run)
      if (($# < 2)); then
        echo "--recover-run requires a run id" >&2
        exit 1
      fi
      RECOVER_RUN_ID="$2"
      shift 2
      ;;
    --fix)
      FIX=1
      if [ "${#PHASES[@]}" -eq 4 ]; then
        PHASES=(generate fix build audit validate)
      fi
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if ! command -v make >/dev/null 2>&1; then
  echo "ERROR: make not found" >&2
  exit 1
fi

if [ ! -f "$WORKSPACE_ROOT/Makefile" ]; then
  echo "ERROR: workspace root does not contain Makefile: $WORKSPACE_ROOT" >&2
  exit 1
fi

project_name_prefix=$(basename "$WORKSPACE_ROOT")

collect_projects() {
  local -a candidates=()
  if [ ${#PROJECT_FILTER[@]} -gt 0 ]; then
    for p in "${PROJECT_FILTER[@]}"; do
      if [ "$p" = "." ]; then
        candidates+=(".")
        continue
      fi
      if [ ! -d "$WORKSPACE_ROOT/$p" ]; then
        echo "WARN: project path not found, skipping: $p" >&2
        continue
      fi
      if [ ! -f "$WORKSPACE_ROOT/$p/Makefile" ]; then
        echo "WARN: project has no Makefile, skipping: $p" >&2
        continue
      fi
      candidates+=("$p")
    done
    if [ "${#candidates[@]}" -ne 1 ]; then
      echo "ERROR: docs-reorg processes exactly one scope per run; use --project <name>." >&2
      exit 1
    fi
    printf '%s\n' "${candidates[@]}"
    return 0
  fi

  echo "ERROR: docs-reorg requires --project <name> or --project workspace." >&2
  exit 1
}

is_generated_managed_file() {
  local scope="$1"
  local rel_path="$2"
  case "$scope" in
    ".")
      case "$rel_path" in
        mkdocs.yml|api-reference/generated/*|projects/generated/*) return 0 ;;
      esac
      ;;
    *)
      case "$rel_path" in
        README.md|index.md|guides/README.md|api-reference/README.md|api-reference/generated/*|mkdocs.yml) return 0 ;;
      esac
      ;;
  esac
  return 1
}

run_phase() {
  local scope_name="$1"
  local phase="$2"
  local phase_log="$3"

  local log_file="$phase_log"
  local cmd=(make _docs DOCS_PHASE="$phase")
  if [ "$scope_name" != "." ]; then
    cmd+=(PROJECT="$scope_name")
  else
    case "$phase" in
      audit|validate)
        cmd=(make workspace-docs-audit)
        ;;
      *)
        if [ "$DRY_RUN" = "1" ]; then
          echo "DRY-RUN: workspace phase '$phase' is handled by docs restore/preservation"
        else
          echo "workspace phase '$phase' is handled by docs restore/preservation" | tee "$log_file"
        fi
        return 0
        ;;
    esac
  fi
  if [ "$FIX" = "1" ]; then
    cmd+=(FIX=1)
  fi

  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY-RUN: (cd $WORKSPACE_ROOT; ${cmd[*]})"
    return 0
  fi

  if ! (cd "$WORKSPACE_ROOT" && "${cmd[@]}" | tee "$log_file"); then
    echo "ERROR: make _docs failed for ${scope_name} phase=${phase}" >&2
    return 1
  fi
}

quarantine_docs() {
  local scope_root="$1"
  local scope_id="$2"
  local scope_legacy="$scope_root/.legacy-docs/$RUN_ID/$scope_id"
  local count=0

  mkdir -p "$scope_legacy"
  local docs_root="$scope_root/docs"

  if [ ! -d "$docs_root" ]; then
    return 0
  fi

  while IFS= read -r -d '' src; do
    rel="${src#$docs_root/}"
    dst="$scope_legacy/$rel.bak"
    mkdir -p "$(dirname "$dst")"
    mv "$src" "$dst"
    count=$((count + 1))
  done < <(find "$docs_root" -type f -print0)

  rm -rf "$docs_root"
  echo "$count"
}

scope_root_for() {
  local scope_name="$1"
  if [ "$scope_name" = "." ]; then
    printf '%s\n' "$WORKSPACE_ROOT"
  else
    printf '%s\n' "$WORKSPACE_ROOT/$scope_name"
  fi
}

scope_id_for() {
  local scope_name="$1"
  if [ "$scope_name" = "." ]; then
    printf '%s\n' "_workspace"
  else
    printf '%s\n' "$scope_name"
  fi
}

restore_target_for() {
  local scope_root="$1"
  local target_rel="$2"
  if [[ "$target_rel" == "mkdocs.yml" ]]; then
    printf '%s\n' "$scope_root/$target_rel"
  else
    printf '%s\n' "$scope_root/docs/$target_rel"
  fi
}

recover_docs() {
  local scope_name="$1"
  local scope_root
  local scope_id
  scope_root="$(scope_root_for "$scope_name")"
  scope_id="$(scope_id_for "$scope_name")"

  local legacy_root="$scope_root/.legacy-docs/$RECOVER_RUN_ID/$scope_id"
  if [ ! -d "$legacy_root" ]; then
    echo "ERROR: recovery source not found: $legacy_root" >&2
    return 1
  fi

  local restored=0
  local skipped=0
  while IFS= read -r -d '' legacy_file; do
    rel="${legacy_file#$legacy_root/}"
    target_rel="${rel%.bak}"
    case "$target_rel" in
      .legacy-docs/*|.reports/*)
        skipped=$((skipped + 1))
        continue
        ;;
    esac
    target="$(restore_target_for "$scope_root" "$target_rel")"
    if [ "$DRY_RUN" = "1" ]; then
      echo "DRY-RUN: restore $legacy_file -> $target"
    else
      mkdir -p "$(dirname "$target")"
      cp "$legacy_file" "$target"
    fi
    restored=$((restored + 1))
  done < <(find "$legacy_root" -type f -name '*.bak' -print0)

  echo "Recovered docs for $scope_name from $RECOVER_RUN_ID: restored=$restored skipped=$skipped"
}

restore_useful_docs() {
  local scope_root="$1"
  local scope_id="$2"
  local scope_type="$3"
  local scope_legacy="$scope_root/.legacy-docs/$RUN_ID/$scope_id"

  local restored=0
  local skipped=0

  if [ ! -d "$scope_legacy" ]; then
    echo "$restored $skipped"
    return 0
  fi

  while IFS= read -r -d '' legacy_file; do
    rel="${legacy_file#$scope_legacy/}"
    target_rel="${rel%.bak}"
    if [ "$target_rel" = "$rel" ]; then
      # Not a migrated file; keep as-is
      target_rel="$rel"
    fi
    case "$target_rel" in
      .legacy-docs/*|.reports/*)
        skipped=$((skipped + 1))
        continue
        ;;
    esac
    target="$(restore_target_for "$scope_root" "$target_rel")"

    if is_generated_managed_file "$scope_type" "$target_rel"; then
      if [ -f "$target" ]; then
        skipped=$((skipped + 1))
        continue
      fi
    fi

    mkdir -p "$(dirname "$target")"
    cp "$legacy_file" "$target"
    restored=$((restored + 1))
  done < <(find "$scope_legacy" -type f -name '*.bak' -print0)

  echo "$restored $skipped"
}

run_project() {
  local scope_name="$1"
  local scope_root
  local scope_id
  scope_root="$(scope_root_for "$scope_name")"
  scope_id="$(scope_id_for "$scope_name")"
  local scope_report_id="$scope_id"
  local report_dir="$scope_root/.reports/docs/doc-reorg"
  local run_dir="$report_dir/$RUN_ID"
  local run_report="$run_dir/${scope_report_id//\//_}.md"
  mkdir -p "$run_dir"

  echo "## Docs reorg run" > "$run_report"
  echo "- Run id: $RUN_ID" >> "$run_report"
  echo "- Scope: $scope_name" >> "$run_report"
  echo "- Root: $scope_root" >> "$run_report"
  echo "" >> "$run_report"

  local phases_ok=1
  local phase_line=""

  local moved_count=0
  if [ -d "$scope_root/docs" ] || [ -e "$scope_root/docs" ]; then
    moved_count="$(quarantine_docs "$scope_root" "$scope_id")"
  fi

  echo "- Quarantine docs files: $moved_count" >> "$run_report"

  if [ "$DRY_RUN" = "0" ]; then
    mkdir -p "$scope_root/docs"
  fi

  local restored_count skipped_count
  read -r restored_count skipped_count < <(restore_useful_docs "$scope_root" "$scope_id" "$scope_name")
  echo "- Restored non-generated docs: $restored_count" >> "$run_report"
  echo "- Skipped managed docs (protected): $skipped_count" >> "$run_report"

  local phase_idx=0
  for phase in "${PHASES[@]}"; do
    phase_idx=$((phase_idx + 1))
    local phase_log="$run_dir/${scope_report_id//\//_}-${phase}.log"
    if run_phase "$scope_name" "$phase" "$phase_log"; then
      phase_line="- ✅ $phase: OK"
    else
      phase_line="- ❌ $phase: FAIL"
      phases_ok=0
      echo "$phase_line" >> "$run_report"
      echo "[ERROR] Docs phase '$phase' failed for $scope_name" >> "$run_report"
      return 1
    fi
    echo "$phase_line" >> "$run_report"
  done

  if [ "${#PHASES[@]}" -gt 0 ] && ! run_phase "$scope_name" "validate" "$run_dir/${scope_report_id//\//_}-validate-final.log"; then
    phases_ok=0
    echo "- ❌ validate-final: FAIL" >> "$run_report"
  else
    echo "- ✅ validate-final: OK" >> "$run_report"
  fi

  return $((1 - phases_ok))
}

FAILED=()
mapfile -t TARGETS < <(collect_projects)
if [ "${#TARGETS[@]}" -eq 0 ]; then
  echo "No targets selected" >&2
  exit 1
fi

if [ -n "$RECOVER_RUN_ID" ]; then
  recover_docs "${TARGETS[0]}"
  exit $?
fi

if run_project "${TARGETS[0]}"; then
  echo "OK: ${TARGETS[0]}"
else
  echo "FAIL: ${TARGETS[0]}"
  FAILED+=("${TARGETS[0]}")
fi

if [ ${#FAILED[@]} -gt 0 ]; then
  echo "Docs reorg completed with failures: ${FAILED[*]}" >&2
  exit 1
fi

echo "Docs reorg completed successfully for ${TARGETS[0]}."
