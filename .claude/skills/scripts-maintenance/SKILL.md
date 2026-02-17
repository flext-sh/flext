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
