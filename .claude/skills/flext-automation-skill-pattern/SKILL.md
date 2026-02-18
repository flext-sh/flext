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
- `.claude/skills/*/baseline.json`
- `.claude/skills/*/report.json`

## References

- `.claude/skills/skill-format-universal/SKILL.md`
- `.claude/skills/flext-quality-gates/SKILL.md`
- `docs/guides/skill-automation-pattern.md`
- `scripts/core/skill_validate.py` — generic skill runner (auto-discovers `.claude/skills/*/rules.yml`)

## Rules

- Ship automation as code first, docs second.
- Every skill must support `baseline` and `strict` modes via `rules.yml`.
- The generic runner auto-discovers all skills — no orchestrator wiring needed.
- Every run must emit machine-readable report artifacts (`report.json`).
- Skills must provide concrete verification commands.

## Instructions

- Create the skill folder under `.claude/skills/<name>/` using canonical sections from `skill-format-universal`.
- Define detection rules in `rules.yml` (ast-grep, ripgrep, or custom types).
- Place ast-grep rule files in `rules/` subdirectory within the skill folder.
- For custom checks, implement scripts inside the skill folder that output JSON `{"violation_count": N}`.
- Skills are auto-discovered by `scripts/core/skill_validate.py` — no orchestrator wiring needed.
- Publish companion guidance in `docs/guides/skill-automation-pattern.md`.

## Workflow

1. Define the invariant (policy or quality behavior).
2. Create `rules.yml` with detection rules (ast-grep, ripgrep, or custom).
3. Initialize baseline with `python3 scripts/core/skill_validate.py --skill <name> --update-baseline`.
4. Verify detection with `python3 scripts/core/skill_validate.py --skill <name>`.
5. Update skill SKILL.md and docs with exact command contract.
6. Run `python3 scripts/core/skill_validate.py --all` to verify integration.

## Examples

Good:

```bash
python3 scripts/core/skill_validate.py --skill flext-strict-typing
python3 scripts/core/skill_validate.py --all
```

Why good: reproducible, non-interactive, and tied to artifacts.

Bad:

```text
Run checks manually and document expected output in chat only.
```

Why bad: no reusable command surface and no persisted evidence.

## Verification

- `python3 scripts/core/skill_validate.py --list-skills`
- `python3 scripts/core/skill_validate.py --all`
- `rg -n "## Scope|## References|## Rules|## Instructions|## Workflow|## Examples|## Verification" .claude/skills/flext-automation-skill-pattern/SKILL.md`
