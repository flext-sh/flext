---
name: flext-automation-skill-pattern
description: Canonical pattern for creating reusable automation skills with script-first validation, baseline/strict enforcement modes, and companion docs. Use for future automation work that must be repeatable across the repo.
---

# Flext Automation Skill Pattern

## Scope

- `.claude/skills/**/SKILL.md`
- `scripts/validation/`
- `scripts/validate_all_projects.sh`
- `docs/guides/`
- `.sisyphus/baselines/`
- `.sisyphus/reports/`

## References

- `.claude/skills/skill-format-universal/SKILL.md`
- `.claude/skills/flext-quality-gates/SKILL.md`
- `docs/guides/skill-automation-pattern.md`
- `scripts/validation/enforce_no_dict_no_any.sh`
- `scripts/validation/run_automated_validation.sh`

## Rules

- Ship automation as code first, docs second.
- Every checker script must support `baseline` and `strict` modes.
- Every automation family must expose `quick` and `full` orchestrator entrypoints.
- Every run must emit machine-readable report artifacts.
- Skills must provide concrete verification commands.

## Instructions

- Create the skill using canonical sections from `skill-format-universal`.
- Implement checker scripts in `scripts/validation/` with non-interactive flags.
- Implement one orchestrator script that runs the checker plus required gates.
- Wire the orchestrator/checker into `scripts/validate_all_projects.sh` when relevant.
- Publish companion guidance in `docs/guides/skill-automation-pattern.md`.

## Workflow

1. Define the invariant (policy or quality behavior).
2. Build checker script with baseline/strict behavior.
3. Add report output under `.sisyphus/reports/` and baseline under `.sisyphus/baselines/`.
4. Build orchestrator script for quick/full validation.
5. Update skill and docs with exact command contract.
6. Run quick validation and integrated validation before completion.

## Examples

Good:

```bash
scripts/validation/enforce_no_dict_no_any.sh --mode baseline --root .
scripts/validation/run_automated_validation.sh quick
```

Why good: reproducible, non-interactive, and tied to artifacts.

Bad:

```text
Run checks manually and document expected output in chat only.
```

Why bad: no reusable command surface and no persisted evidence.

## Verification

- `bash -n scripts/validation/enforce_no_dict_no_any.sh`
- `bash -n scripts/validation/run_automated_validation.sh`
- `scripts/validation/run_automated_validation.sh quick`
- `rg -n "## Scope|## References|## Rules|## Instructions|## Workflow|## Examples|## Verification" .claude/skills/flext-automation-skill-pattern/SKILL.md`
