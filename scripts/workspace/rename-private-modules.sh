#!/usr/bin/env bash
# Use the existing semantic publisher for Python module filename renames.
set -euo pipefail

if (( $# > 1 )) || [[ ${1:-} != '' && ${1:-} != --apply ]]; then
    printf 'Usage: bash %s [--apply]\n' "$0" >&2
    exit 2
fi

root=$(pwd -P)
if [[ ! -f Makefile || ! -f pyproject.toml || -L .venv || ! -x .venv/bin/python ]]; then
    printf 'Run from a FLEXT workspace root with its own physical environment.\n' >&2
    exit 2
fi

manifest=$(mktemp)
targets=$(mktemp)
trap 'rm -f -- "$manifest" "$targets"' EXIT

# The canonical inventory excludes environments, tool state and unrelated worktrees.
"$root/.venv/bin/python" - "$root" > "$manifest" <<'PY'
import os
from pathlib import Path
import sys

from flext_infra import u

for owner in u.Infra.import_project_roots(Path(sys.argv[1])):
    for relative in sorted(u.Infra.ast_grep_scan_targets(owner)):
        path = owner / relative
        if (
            path.suffix == ".py"
            and path.name.startswith("_")
            and not path.name.startswith("__")
            and u.Infra.project_root(path) == owner
        ):
            sys.stdout.buffer.write(os.fsencode(owner) + b"\0" + os.fsencode(path) + b"\0")
PY

conflicts=0
count=0
declare -A owners=() repositories=()
declare -a repository_order=()
occupied() {
    local package=${1%.py}
    [[ -e $1 || -L $1 || -e $package/__init__.py \
        || -e $package/__init__.pyi || -L $package ]]
}

while IFS= read -r -d '' owner && IFS= read -r -d '' source; do
    filename=${source##*/}
    destination=${source%/*}/${filename#_}
    if occupied "$destination"; then
        stem=${filename%.py}
        destination=${source%/*}/${stem#_}_definitions.py
        printf 'Keep existing owner; select %q -> %q\n' "$source" "$destination"
    fi
    if occupied "$destination" || [[ -n ${owners["$destination"]+set} ]]; then
        printf 'Occupied destination: %q -> %q\n' "$source" "$destination" >&2
        conflicts=1
    fi
    owners["$destination"]=$source
    printf '%s\0%s\0%s\0' "$owner" "$source" "$destination" >> "$targets"
    if [[ -z ${repositories["$owner"]+set} ]]; then
        repository_order+=("$owner")
        repositories["$owner"]=1
    fi
    count=$((count + 1))
done < "$manifest"

if (( conflicts )); then
    printf 'No modules renamed. Resolve the reported destination owners first.\n' >&2
    exit 1
fi
if (( count == 0 )); then
    printf 'No single-underscore Python module filenames found.\n'
    exit 0
fi

printf 'Selected %s module filenames in %s repositories.\n' "$count" "${#repository_order[@]}"
for owner in "${repository_order[@]}"; do
    printf 'Plan and validate repository: %s\n' "$owner"
    "$root/.venv/bin/python" - "$root" "$owner" "$targets" "${1:-}" <<'PY'
from pathlib import Path
import sys

from flext_cli import cli
from flext_infra import codemod, infra, m, u

root = Path(sys.argv[1])
owner = Path(sys.argv[2])
paths = tuple(
    root / entry.decode(sys.getfilesystemencoding(), errors="surrogateescape")
    for entry in Path(sys.argv[3]).read_bytes().split(b"\0")
    if entry
)
consumers = tuple(
    project
    for project in u.Infra.import_project_roots(root)
    if not project.is_relative_to(owner) and not owner.is_relative_to(project)
)
engine = codemod.FlextInfraCodemodSemanticApply
with infra.rope_workspace(owner, rope_repository_root=owner) as workspace:
    decisions = []
    for project, path, destination in zip(paths[::3], paths[1::3], paths[2::3], strict=True):
        if project != owner:
            continue
        module = workspace.module(path)
        if module is None:
            raise ValueError(f"Module is outside the governed source inventory: {path}")
        decisions.append(
            m.Infra.SemanticRenameSelection(
                qualified_name=module.module_name,
                replacement_name=destination.stem,
                reason="Remove a module prefix while preserving existing owners",
            )
        )
    plan = engine.build_rename_plan(
        owner,
        workspace,
        m.Infra.SemanticRenameSelections(
            decisions=tuple(decisions), consumer_roots=consumers
        ),
    ).unwrap()

for source, destination in plan.moves:
    cli.display_text(f"{source.relative_to(root)} -> {destination.relative_to(root)}")
engine.publish_candidate(owner, plan, publish=sys.argv[4] == "--apply").unwrap()
cli.display_text(
    "Module renames and generated initializers published."
    if sys.argv[4] == "--apply"
    else "Preview accepted; no module renames published. Use --apply to publish."
)
PY
done
