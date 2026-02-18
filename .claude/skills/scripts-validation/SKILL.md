---
name: scripts-validation
description: Validation scripts — policy gates, automated checks, ast-grep enforcement, and the validation orchestrator. Use when editing scripts/validation/ or scripts/validate_all_projects.sh.
---

# Scripts Validation

## Scope

- `scripts/validation/run_automated_validation.sh` — thin wrapper around `skill_validate.py --all`
- `scripts/core/skill_validate.py`
- `scripts/validate_all_projects.sh`
- `.claude/skills/*/rules.yml`
- `.claude/skills/*/rules/*.yml`
- `.claude/skills/*/baseline.json`

## References

- `.claude/skills/flext-automation-skill-pattern/SKILL.md`
- `.claude/skills/flext-quality-gates/SKILL.md`
- `Makefile`

## Rules

- All validation is data-driven via `rules.yml` files inside each skill folder.
- The generic runner `scripts/core/skill_validate.py` discovers and executes rules.
- Baselines are stored in each skill folder as `baseline.json` (git-tracked).
- Reports are `report.json` (git-ignored, transient).
- All validators must be non-interactive and exit with clear status codes (0=pass, 1=fail, 2=usage, 3=infra).

## Instructions

- When adding a new validation gate, create a `rules.yml` in the relevant skill folder.
- The orchestrator `scripts/validation/run_automated_validation.sh` auto-discovers all skills — no wiring needed.
- Use `python3 scripts/core/skill_validate.py --skill <name> --update-baseline` to initialize baselines.
- Use `--mode strict` for zero-tolerance enforcement, `--mode baseline` for ratchet-only.

## Workflow

1. Identify the validation invariant to enforce.
2. Add rules to the relevant skill's `rules.yml` (type: ast-grep, ripgrep, or custom).
3. Place ast-grep rule files in the skill's `rules/` directory.
4. Run `python3 scripts/core/skill_validate.py --skill <name> --update-baseline` to set baseline.
5. Run `python3 scripts/core/skill_validate.py --all` to verify integration.

## Examples

Good:

```bash
python3 scripts/core/skill_validate.py --skill flext-strict-typing --mode baseline
python3 scripts/core/skill_validate.py --all
scripts/validation/run_automated_validation.sh
```

Why good: Data-driven, reproducible, non-interactive, baseline-aware.

Bad:

```bash
grep -r "dict" . | wc -l
```

Why bad: No baseline comparison, no structured output, no gate behavior.

## Verification

- `bash -n scripts/validation/run_automated_validation.sh`
- `bash -n scripts/validate_all_projects.sh`
- `python3 scripts/core/skill_validate.py --all`
- `scripts/validation/run_automated_validation.sh`

## Scripts

| Path | Purpose | Invocation |
|------|---------|------------|
| `scripts/validation/run_automated_validation.sh` | Thin orchestrator wrapper | `scripts/validation/run_automated_validation.sh` |
| `scripts/core/skill_validate.py` | Generic skill runner (auto-discovers rules.yml) | `python3 scripts/core/skill_validate.py --all` |
| `scripts/validate_all_projects.sh` | Workspace-wide validation across all projects | `bash scripts/validate_all_projects.sh` |
