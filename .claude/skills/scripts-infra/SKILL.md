---
name: scripts-infra
description: Shared script infrastructure — bash/python libraries, core runner/registry, artifact naming, config utilities, and Makefile helpers. Use when editing scripts/lib/, scripts/core/, scripts/config/, scripts/makefiles/, or scripts/common.py.
---

# Scripts Infra

## Scope

- `scripts/lib/common.sh`
- `scripts/lib/message_formatter.sh`
- `scripts/lib/runtime_detector.sh`
- `scripts/lib/artifact_naming.sh`
- `scripts/core/script_runner.py`
- `scripts/core/script_registry.py`
- `scripts/core/artifact_naming.py`
- `scripts/core/check_script_skill_ownership.py`
- `scripts/core/check_script_artifact_naming.py`
- `scripts/core/__init__.py`
- `scripts/common.py`
- `scripts/config/load_staging_config.py`
- `scripts/config/setup_workspace_links.py`
- `scripts/config/standardize_pyproject.py`
- `scripts/config/__init__.py`
- `scripts/makefiles/simplify_makefiles.py`

## References

- `.claude/skills/rules-scripts/SKILL.md`
- `.claude/skills/flext-automation-skill-pattern/SKILL.md`
- `.sisyphus/plans/scripts-skill-standardization.md`
- `Makefile`

## Rules

- Shared libraries must be non-interactive by default; interactive helpers require explicit opt-in via `--interactive`.
- Every script owned by this skill must have `# Owner-Skill: .claude/skills/scripts-infra/SKILL.md` in its header.
- Artifact output must follow the `<skill>--<kind>--<slug>.<ext>` naming contract.
- Python scripts must use `pathlib.Path` exclusively (no `os.path`).
- Bash scripts must use `set -euo pipefail` and `#!/usr/bin/env bash`.

## Instructions

- When modifying shared libs, verify all downstream scripts still work.
- When adding a new helper function, add it to the appropriate shared lib (bash → `scripts/lib/`, python → `scripts/core/`).
- When editing config scripts, ensure they can run from any CWD.
- Keep `scripts/core/` as the canonical location for cross-cutting Python infrastructure.

## Workflow

1. Identify the shared lib or infra file to modify.
2. Check which scripts source/import it via `rg 'source.*common.sh' scripts/` or `rg 'from.*core.*import' scripts/`.
3. Apply minimal change.
4. Run `bash -n` on modified bash files, `python -m compileall scripts/core` for Python.
5. Run `python scripts/core/check_script_skill_ownership.py` to verify ownership markers.

## Examples

Good:

```bash
source "$SCRIPT_DIR/lib/common.sh"
source "$SCRIPT_DIR/lib/artifact_naming.sh"
local report_path
report_path=$(artifact_path "reports" "scripts-validation" "json" "policy-gate-latest")
```

Why good: Uses shared lib for artifact naming, deterministic path construction.

Bad:

```bash
REPORT=".sisyphus/reports/my_report.json"
```

Why bad: Hardcoded path bypasses artifact naming contract.

## Verification

- `bash -n scripts/lib/common.sh`
- `bash -n scripts/lib/artifact_naming.sh`
- `python -m compileall scripts/core`
- `python scripts/core/check_script_skill_ownership.py`
- `rg "Owner-Skill:.*scripts-infra" scripts/lib scripts/core scripts/common.py scripts/config scripts/makefiles`

## Scripts

| Path | Purpose | Invocation |
|------|---------|------------|
| `scripts/lib/common.sh` | Bash shared lib: root discovery, project discovery, helpers | `source scripts/lib/common.sh` |
| `scripts/lib/message_formatter.sh` | Bash shared lib: colorized messaging | `source scripts/lib/message_formatter.sh` |
| `scripts/lib/runtime_detector.sh` | Bash shared lib: runtime environment detection | `source scripts/lib/runtime_detector.sh` |
| `scripts/lib/artifact_naming.sh` | Bash helper: artifact naming contract | `source scripts/lib/artifact_naming.sh` |
| `scripts/core/__init__.py` | Package marker | — |
| `scripts/core/script_runner.py` | Central script executor | `python scripts/core/script_runner.py <name>` |
| `scripts/core/script_registry.py` | Script discovery and metadata | (imported by script_runner) |
| `scripts/core/artifact_naming.py` | Python helper: artifact naming contract | `from scripts.core.artifact_naming import artifact_path` |
| `scripts/core/check_script_skill_ownership.py` | Ownership validator (hard gate) | `python scripts/core/check_script_skill_ownership.py` |
| `scripts/core/check_script_artifact_naming.py` | Artifact naming validator | `python scripts/core/check_script_artifact_naming.py` |
| `scripts/common.py` | Python shared utils: workspace/project discovery | `from scripts.common import discover_projects` |
| `scripts/config/__init__.py` | Package marker | — |
| `scripts/config/load_staging_config.py` | Load staging environment config | `python scripts/config/load_staging_config.py` |
| `scripts/config/setup_workspace_links.py` | Setup workspace symlinks | `python scripts/config/setup_workspace_links.py` |
| `scripts/config/standardize_pyproject.py` | Standardize pyproject.toml files | `python scripts/config/standardize_pyproject.py` |
| `scripts/makefiles/simplify_makefiles.py` | Simplify project Makefiles | `python scripts/makefiles/simplify_makefiles.py` |
