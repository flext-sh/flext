---
name: scripts-validation
description: Validation scripts — policy gates, automated checks, ast-grep enforcement, and the validation orchestrator. Use when editing scripts/validation/ and scripts/core/skill_validate.py.
---

# Scripts Validation

## Scope

- `scripts/validation/run_automated_validation.sh` — thin wrapper around `skill_validate.py --all`
- `scripts/core/skill_validate.py`
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
- `rules.yml` fix metadata must use flat keys only; nested `fix:` structures are invalid.
- Supported rule types are `ast-grep` and `custom`.
- Prefer `ast-grep` rules; use `custom` only when AST matching is not applicable.
- `make validate-scripts` must run strict mode (`--mode strict`) and fail on policy violations.
- Custom validators must be implemented inside the owning skill directory.
- Custom validator output must include machine-readable JSON with `{"violation_count": <int>}` for `skill_validate.py` compatibility.

## Instructions

- When adding a new validation gate, create a `rules.yml` in the relevant skill folder.
- Use `make validate-scripts` as the default gate command for session-level validation.
- The orchestrator `scripts/validation/run_automated_validation.sh` auto-discovers all skills — no wiring needed.
- Use `python3 scripts/core/skill_validate.py --skill <name> --update-baseline` to initialize baselines.
- Use `--mode strict` for zero-tolerance enforcement, `--mode baseline` for ratchet-only.

## Workflow

1. Identify the validation invariant to enforce.
2. Add rules to the relevant skill's `rules.yml` (type: ast-grep or custom).
3. Place ast-grep rule files in the skill's `rules/` directory.
4. Run `python3 scripts/core/skill_validate.py --skill <name> --update-baseline` to set baseline.
5. Run `python3 scripts/core/skill_validate.py --all --mode strict` to verify integration.
6. Run `make check-clean` to produce a clean actionable workspace report.

## Examples

Good:

```bash
python3 scripts/core/skill_validate.py --skill flext-strict-typing --mode strict
python3 scripts/core/skill_validate.py --all --mode strict
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
- `python3 scripts/core/skill_validate.py --all --mode strict`
- `scripts/validation/run_automated_validation.sh`
- `make validate-scripts`
- `make check-clean`

## Scripts

| Path | Purpose | Invocation |
|------|---------|------------|
| `scripts/validation/run_automated_validation.sh` | Thin orchestrator wrapper | `scripts/validation/run_automated_validation.sh` |
| `scripts/core/skill_validate.py` | Generic skill runner (auto-discovers rules.yml) | `python3 scripts/core/skill_validate.py --all` |
