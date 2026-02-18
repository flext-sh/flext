---
name: scripts-maintenance
description: Maintenance and git scripts — health checks, workspace status, git cleanup, and operational tooling. Use when editing scripts/maintenance/ or scripts/git/.
---

# Scripts Maintenance

## Scope

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
- `scripts/docs_link_fixer.py`
- `scripts/docs_maintenance_audit.py`
- `scripts/docs_sync_automation.sh`
- `scripts/docs_toc_generator.py`
- `scripts/markdown_lint_workspace.py`
- `scripts/maintenance/check_workspace_hygiene.py`
- `scripts/maintenance/check_dependabot_config.py`
- `scripts/maintenance/check_poetry_health.py`

## References

- `.claude/skills/rules-scripts/SKILL.md`

## Rules

- Maintenance scripts must be safe to run repeatedly (idempotent).
- Destructive operations (cleanup, deletion) must require explicit `--apply` or `--force` flag.
- Health checks must exit 0 on healthy, 1 on unhealthy.
- Git scripts must not force-push or rewrite history without explicit flag.

## Instructions

- When adding maintenance scripts, ensure they report status without modifying state by default.
- When modifying git cleanup, verify it respects protected branches.
- Use `scripts/common.py:discover_projects` for workspace-wide operations.

## Workflow

1. Identify the maintenance concern.
2. Create or modify the script under `scripts/maintenance/` or `scripts/git/`.
3. Test with `--help` and `--dry-run` first.
4. Verify with `python -m compileall scripts/maintenance scripts/git`.

## Examples

Good:

```bash
python scripts/maintenance/health_check_service.py
python scripts/git/git_ultimate_cleanup.py --dry-run
```

Why good: Safe defaults, explicit opt-in for destructive actions.

Bad:

```bash
git clean -fdx  # directly in script without guard
```

Why bad: Destructive without confirmation or dry-run.

## Verification

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
| `scripts/docs_link_fixer.py` | Fix documentation links | `python scripts/docs_link_fixer.py` |
| `scripts/docs_maintenance_audit.py` | Documentation maintenance audit | `python scripts/docs_maintenance_audit.py` |
| `scripts/docs_sync_automation.sh` | Documentation sync automation | `bash scripts/docs_sync_automation.sh` |
| `scripts/docs_toc_generator.py` | Documentation TOC generator | `python scripts/docs_toc_generator.py` |
| `scripts/markdown_lint_workspace.py` | Lint markdown workspace-wide | `python scripts/markdown_lint_workspace.py` |
| `scripts/maintenance/check_workspace_hygiene.py` | Workspace cleanliness validation | `python scripts/maintenance/check_workspace_hygiene.py` |
| `scripts/maintenance/check_dependabot_config.py` | Dependabot config standardization | `python scripts/maintenance/check_dependabot_config.py` |
| `scripts/maintenance/check_poetry_health.py` | Poetry lock health and outdated deps | `python scripts/maintenance/check_poetry_health.py` |
