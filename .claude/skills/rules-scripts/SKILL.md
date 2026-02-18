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

- Every script MUST have exactly one `# Owner-Skill: .claude/skills/<skill>/SKILL.md` marker in its header (line 2).
- Keep scripts non-interactive by default for CI compatibility; interactive prompts require explicit `--interactive` flag.
- Fail fast with clear error output for validation scripts.
- Bash scripts: `#!/usr/bin/env bash` shebang + `set -euo pipefail`.
- Python scripts: `if __name__ == "__main__": sys.exit(main())` pattern for entrypoints.
- Artifact output must follow `<skill>--<kind>--<slug>.<ext>` naming contract.
- Preserve executable permissions and shebang correctness.
- Keep script behavior deterministic and root-relative.

## Instructions

- When adding a new script, assign it to one of the 7 domain skills (scripts-infra, scripts-validation, scripts-security, scripts-architecture, scripts-testing, scripts-dependencies, scripts-maintenance).
- Add the `# Owner-Skill:` marker and list it in the owning skill's `## Scripts` table.
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

- `make validate-scripts` — runs ownership, bash -n, py_compile, ast-grep, artifact naming
- `python scripts/core/check_script_skill_ownership.py` — ownership validator (hard gate)
- `python scripts/core/check_script_artifact_naming.py` — artifact naming validator
- `python3 scripts/core/skill_validate.py --skill rules-scripts` — interactive prompt detection via skill rules
- `bash -n <file>` for bash, `python -m py_compile <file>` for Python
