---
name: rules-scripts
description: Rules for automation and maintenance scripts under `scripts/`. Use when editing shell/python scripts that drive validation, cleanup, release, or tooling workflows.
---

# Rules Scripts

## Scope
- `scripts/validate_all_projects.sh`
- `scripts/architecture/`
- `scripts/security/`
- `scripts/testing/`
- `scripts/*.py`
- `scripts/*.sh`

## References
- `scripts/README.md`
- `Makefile`
- `AGENTS.md`

## Rules
- Keep scripts non-interactive by default for CI compatibility.
- Fail fast with clear error output for validation scripts.
- Preserve executable permissions and shebang correctness.
- Keep script behavior deterministic and root-relative.

## Instructions
- Anchor changes to concrete script files, not generic script categories.
- For shell scripts, prefer explicit command checks over implicit assumptions.
- For Python scripts, keep imports and file paths workspace-relative.

```bash
ls -la scripts
```

## Workflow
1. Select target script and its caller(s).
2. Apply minimal behavior change.
3. Run script in representative mode (`--help` or safe validation mode).
4. Verify downstream docs/make targets still align.

## Examples
Good:

```bash
bash scripts/validate_all_projects.sh
```

Why good: explicit validation script invocation with reproducible behavior.

Bad:

```bash
./some_script.sh
```

Why bad: ambiguous path and unclear contract from repository root.

## Verification
- `ls -la scripts`
- `rg -n "^#!/|set -e|set -eu|argparse|if __name__ == '__main__'" scripts/*.sh scripts/*.py || true`
- `rg -n "validate_all_projects" Makefile scripts || true`
- `rg -n "TODO|FIXME" scripts || true`
