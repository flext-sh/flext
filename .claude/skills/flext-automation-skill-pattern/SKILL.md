<!-- TOC START -->
- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---
name: flext-automation-skill-pattern
description: Canonical pattern for creating reusable automation skills with script-first validation, baseline/strict enforcement modes, and companion docs. Use for future automation work that must be repeatable across the repo.
---

# Flext Automation Skill Pattern

## Scope

- `.claude/skills/**/SKILL.md`
- `scripts/validation/`
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
- Prefer `ast-grep` for checks/fixes; use `custom` scripts only when AST cannot express the rule.
- Place `custom` scripts in the owning skill directory, not in `scripts/core`.

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
3. Run standardized gate on target project with `make validate PROJECT=<name>`.
4. Verify with `make validate PROJECT=<name> FIX=1` when autofix is needed.
5. Update skill SKILL.md and docs with exact command contract.
6. Run `make validate PROJECTS="proj-a proj-b"` for integration scope.
7. Use root `make validate` as the workspace gate entrypoint.

## Examples

Good:

```bash
make validate PROJECT=flext-core
make validate PROJECT=flext-core FIX=1
```

Why good: reproducible, non-interactive, and tied to artifacts.

Bad:

```text
Run checks manually and document expected output in chat only.
```

Why bad: no reusable command surface and no persisted evidence.

## Verification

- `make validate PROJECT=<name>`
- `make validate PROJECT=<name> FIX=1`
- `make validate PROJECTS="proj-a proj-b"`
- `rg -n "## Scope|## References|## Rules|## Instructions|## Workflow|## Examples|## Verification" .claude/skills/flext-automation-skill-pattern/SKILL.md`
