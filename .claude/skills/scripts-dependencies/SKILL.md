---
name: scripts-dependencies
description: Dependency management scripts — analysis, consolidation, discovery, caching, and synchronization. Use when editing scripts/dependencies/.
---

# Scripts Dependencies

## Scope

- `scripts/dependencies/analyze_dependencies.py`
- `scripts/dependencies/consolidate_dependencies.py`
- `scripts/dependencies/dependency_cache.py`
- `scripts/dependencies/discover_missing_deps.py`
- `scripts/dependencies/__init__.py`
- `scripts/dependencies/sync_dependencies.py`

## References

- `.claude/skills/rules-scripts/SKILL.md`
- `Makefile` (`deps-all` target)

## Rules

- Dependency scripts must not modify lockfiles without explicit `--apply` flag.
- Analysis output must go to `.sisyphus/reports/` via artifact naming contract.
- All scripts must be runnable from repo root.

## Instructions

- When adding dependency analysis, follow the pattern in `analyze_dependencies.py`.
- When modifying sync logic, ensure idempotency.
- Use `scripts/common.py:discover_projects` for project enumeration.

## Workflow

1. Identify the dependency concern (missing, outdated, conflicting).
2. Create or modify the script under `scripts/dependencies/`.
3. Test with `--help` and dry-run mode.
4. Verify with `python -m compileall scripts/dependencies`.

## Examples

Good:

```bash
python scripts/dependencies/analyze_dependencies.py --output .sisyphus/reports/scripts-dependencies--json--analysis-latest.json
```

Why good: Artifact naming, structured output, non-interactive.

Bad:

```bash
pip install --upgrade $(cat requirements.txt)
```

Why bad: No analysis, no structured output, destructive.

## Verification

- `python -m compileall scripts/dependencies`
- `python scripts/dependencies/analyze_dependencies.py --help`
- `rg "Owner-Skill:.*scripts-dependencies" scripts/dependencies`

## Scripts

| Path | Purpose | Invocation |
|------|---------|------------|
| `scripts/dependencies/__init__.py` | Package marker | — |
| `scripts/dependencies/analyze_dependencies.py` | Analyze project dependencies | `python scripts/dependencies/analyze_dependencies.py` |
| `scripts/dependencies/consolidate_dependencies.py` | Consolidate duplicate dependencies | `python scripts/dependencies/consolidate_dependencies.py` |
| `scripts/dependencies/dependency_cache.py` | Dependency caching utilities | `python scripts/dependencies/dependency_cache.py` |
| `scripts/dependencies/discover_missing_deps.py` | Discover missing dependencies | `python scripts/dependencies/discover_missing_deps.py` |
| `scripts/dependencies/sync_dependencies.py` | Sync dependencies across projects | `python scripts/dependencies/sync_dependencies.py` |
