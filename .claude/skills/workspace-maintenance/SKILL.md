---
name: workspace-maintenance
description: Workspace-wide maintenance automation — hygiene checks, dependabot config standardization, poetry health, and security enforcement across all submodules.
---

# Workspace Maintenance

## Scope

- `scripts/maintenance/check_workspace_hygiene.py`
- `scripts/maintenance/check_dependabot_config.py`
- `scripts/maintenance/check_poetry_health.py`

## References

- `.claude/skills/rules-scripts/SKILL.md`
- `.claude/skills/scripts-maintenance/SKILL.md`

## Rules

- All checks must be idempotent and safe by default (read-only unless `--apply`).
- Mutations (cleanup, lock updates) require explicit `--apply` flag.
- Scripts must discover `flext-*` projects with `pyproject.toml` for workspace iteration.
- Reports output to `.sisyphus/reports/workspace-maintenance--json--<slug>.json`.
- Exit 0 = all checks pass, exit 1 = violations found.
- Each script must be standalone (stdlib + PyYAML only, no flext_core imports).

## Instructions

- When adding a new workspace check, create a `check_<concern>.py` under `scripts/maintenance/`.
- Add the `# Owner-Skill: .claude/skills/workspace-maintenance/SKILL.md` marker on line 2.
- Follow the gate contract pattern: `argparse`, `dataclass` violations, JSON report, `sys.exit(main())`.
- Register the new script in this skill's Scope and Scripts table.
- Use the project discovery pattern: iterate `flext-*` dirs with `pyproject.toml` present.

## Workflow

1. Identify the maintenance concern (hygiene, dependabot, poetry, security).
2. Run the relevant checker with `--help` first, then default (dry-run) mode.
3. Review the JSON report in `.sisyphus/reports/` or the ANSI terminal output.
4. If fixes are needed, re-run with `--apply` to mutate state.

## Examples

Good:

```bash
python scripts/maintenance/check_workspace_hygiene.py
python scripts/maintenance/check_dependabot_config.py --json
python scripts/maintenance/check_poetry_health.py --apply
```

Why good: Safe defaults, explicit opt-in for mutations, structured output available.

Bad:

```bash
git clean -fdx  # directly without guard
poetry update   # in root without per-project isolation
```

Why bad: Destructive without confirmation, no per-project isolation or reporting.

## Verification

- `python -m compileall scripts/maintenance/check_workspace_hygiene.py scripts/maintenance/check_dependabot_config.py scripts/maintenance/check_poetry_health.py`
- `python scripts/maintenance/check_workspace_hygiene.py --help`
- `python scripts/maintenance/check_dependabot_config.py --help`
- `python scripts/maintenance/check_poetry_health.py --help`

## Scripts

| Path | Purpose | Invocation |
|------|---------|------------|
| `scripts/maintenance/check_workspace_hygiene.py` | Workspace cleanliness validation | `python scripts/maintenance/check_workspace_hygiene.py` |
| `scripts/maintenance/check_dependabot_config.py` | Dependabot config standardization | `python scripts/maintenance/check_dependabot_config.py` |
| `scripts/maintenance/check_poetry_health.py` | Poetry lock health and outdated deps | `python scripts/maintenance/check_poetry_health.py` |
