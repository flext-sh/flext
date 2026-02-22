<!-- TOC START -->
- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
- [Scripts](#scripts)
<!-- TOC END -->

---
name: scripts-maintenance
description: Maintenance services — health checks, workspace status, git cleanup, and operational tooling. Use when using flext_infra.maintenance or editing scripts/maintenance/ or scripts/git/.
---

# Scripts Maintenance

## Scope

- `flext_infra.maintenance` module — Maintenance services (Python module in flext-core)
  - `flext_infra.maintenance.python_version.PythonVersionEnforcer`
- Legacy scripts (deprecated):
  - `scripts/maintenance/health_check_service.py`
  - `scripts/maintenance/__init__.py`
  - `scripts/maintenance/workspace_status.py`
  - `scripts/git/git_ultimate_cleanup.py`
  - `scripts/cleanup_local_venvs.sh`
  - `scripts/cleanup_project_makefiles.py`
  - `scripts/clean_git_ignored_files.py`
  - `scripts/create_aggressive_gitignore.py`
  - `scripts/merge_aggressive_gitignore.py`
  - `scripts/add_missing_clean_targets.py`
  - `scripts/update_clean_targets.py`
  - `scripts/documentation/fix.py`
  - `scripts/documentation/audit.py`
  - `scripts/documentation/build.py`
  - `scripts/documentation/generate.py`
  - `scripts/documentation/validate.py`
  - `scripts/documentation/readme_standardizer.py`
  - `scripts/maintenance/check_workspace_hygiene.py`
  - `scripts/maintenance/check_dependabot_config.py`
  - `scripts/maintenance/check_poetry_health.py`

## References

- `flext-core/src/flext_infra/maintenance/` — Module source
- `.claude/skills/rules-scripts/SKILL.md`
- `docs/architecture/adr/README.md`

## Rules

- Maintenance scripts must be safe to run repeatedly (idempotent).
- Destructive operations (cleanup, deletion) must require explicit `--apply` or `--force` flag.
- Health checks must exit 0 on healthy, 1 on unhealthy.
- Git scripts must not force-push or rewrite history without explicit flag.

## Instructions

- When adding maintenance scripts, ensure they report status without modifying state by default.
- When modifying git cleanup, verify it respects protected branches.
- Use `flext_infra.discovery.DiscoveryService` for workspace-wide operations.

## Workflow

1. Identify the maintenance concern.
2. Create or modify the script under `scripts/maintenance/` or `scripts/git/`.
3. Test with `--help` and `--dry-run` first.
4. Verify script compiles: `python -m compileall scripts/maintenance scripts/git`.
5. Run standard gates: `make check PROJECT=<name>` and `make clean PROJECT=<name>`.

## Examples

Good (Make verbs for standard gates):

```bash
make check
make validate
make clean
```

Good (direct scripts for maintenance utilities without Make targets):

```bash
python scripts/maintenance/health_check_service.py
python scripts/git/git_ultimate_cleanup.py --dry-run
```

Why good: Make verbs for standard workflow; safe defaults and explicit opt-in for maintenance scripts.

Bad:

```bash
git clean -fdx  # directly in script without guard
```

Why bad: Destructive without confirmation or dry-run.

## Verification

Make gates (primary):

- `make check PROJECT=flext-core` — lint + format + type + security
- `make clean PROJECT=flext-core` — verify clean targets work
- `make validate VALIDATE_SCOPE=workspace` — workspace-level inventory validation

Script-level checks (internal):

- `python -m compileall scripts/maintenance scripts/git`
- `python scripts/maintenance/workspace_status.py --help`
- `rg "Owner-Skill:.*scripts-maintenance" scripts/maintenance scripts/git`

## Scripts

| Path | Purpose | Invocation |
|------|---------|------------|
| `scripts/maintenance/__init__.py` | Package marker | — |
| `scripts/maintenance/health_check_service.py` | Health check service | `python scripts/maintenance/health_check_service.py` |
| `scripts/maintenance/workspace_status.py` | Workspace status report | `python scripts/maintenance/workspace_status.py` |
| `scripts/git/git_ultimate_cleanup.py` | Git cleanup utility | `python scripts/git/git_ultimate_cleanup.py --dry-run` |
| `scripts/cleanup_local_venvs.sh` | Clean local venvs | `bash scripts/cleanup_local_venvs.sh` |
| `scripts/cleanup_project_makefiles.py` | Clean project makefiles | `python scripts/cleanup_project_makefiles.py` |
| `scripts/clean_git_ignored_files.py` | Clean git-ignored files | `python scripts/clean_git_ignored_files.py` |
| `scripts/create_aggressive_gitignore.py` | Create aggressive gitignore | `python scripts/create_aggressive_gitignore.py` |
| `scripts/merge_aggressive_gitignore.py` | Merge aggressive gitignore | `python scripts/merge_aggressive_gitignore.py` |
| `scripts/add_missing_clean_targets.py` | Add missing clean targets | `python scripts/add_missing_clean_targets.py` |
| `scripts/update_clean_targets.py` | Update clean targets | `python scripts/update_clean_targets.py` |
| `scripts/documentation/fix.py` | Documentation fix phase (links + TOC) | `make docs DOCS_PHASE=fix FIX=1` |
| `scripts/documentation/audit.py` | Documentation audit phase | `make docs DOCS_PHASE=audit` |
| `scripts/documentation/build.py` | Documentation build phase | `make docs DOCS_PHASE=build` |
| `scripts/documentation/generate.py` | Documentation generate phase | `make docs DOCS_PHASE=generate` |
| `scripts/documentation/validate.py` | Documentation validate phase | `make docs DOCS_PHASE=validate` |
| `scripts/documentation/readme_standardizer.py` | README standardization automation | `make docs` |
| `scripts/maintenance/check_workspace_hygiene.py` | Workspace cleanliness validation | `python scripts/maintenance/check_workspace_hygiene.py` |
| `scripts/maintenance/check_dependabot_config.py` | Dependabot config standardization | `python scripts/maintenance/check_dependabot_config.py` |
| `scripts/maintenance/check_poetry_health.py` | Poetry lock health and outdated deps | `python scripts/maintenance/check_poetry_health.py` |
