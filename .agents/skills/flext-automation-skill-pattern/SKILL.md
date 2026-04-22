---
name: flext-automation-skill-pattern
description: Canonical pattern for creating reusable automation skills with script-first validation, baseline/strict enforcement modes, and companion docs. Use when building new automation skills that must be repeatable across the FLEXT repo, or when standardizing existing ad-hoc automation into a testable skill.

---

# Flext Automation Skill Pattern

## Scope

- `.agents/skills/**/SKILL.md`
- `scripts/validation/`
- `docs/guides/`
- `.agents/skills/*/baseline.json`
- `.agents/skills/*/report.json`

## References

- `AGENTS.md` — canonical governance source
- `.agents/skills/skill-format-universal/SKILL.md`
- `.agents/skills/flext-quality-gates/SKILL.md`
- `docs/guides/skill-automation-pattern.md`
- `scripts/core/skill_validate.py` — generic skill runner (auto-discovers `.agents/skills/*/rules.yml`)

## Rules

- Ship automation as code first, docs second.
- Every skill must support `baseline` and `strict` modes via `rules.yml`.
- The generic runner auto-discovers all skills — no orchestrator wiring needed.
- Every run must emit machine-readable report artifacts (`report.json`).
- Skills must provide concrete verification commands.
- Prefer `ast-grep` for checks/fixes; use `custom` scripts only when AST cannot express the rule.
- Place `custom` scripts in the owning skill directory, not in `scripts/core`.
- Automation skills that govern refactoring, routing, or validation should encode mandatory tool usage and zero-debt closure, not optional best-effort behavior.

## Instructions

- Create the skill folder under `.agents/skills/<name>/` using canonical sections from `skill-format-universal`.
- Define detection rules in `rules.yml` (ast-grep, ripgrep, or custom types).
- Place ast-grep rule files in `rules/` subdirectory within the skill folder.
- For custom checks, implement scripts inside the skill folder that output JSON `{"violation_count": N}`.
- Skills are auto-discovered by `scripts/core/skill_validate.py` — no orchestrator wiring needed.
- Publish companion guidance in `docs/guides/skill-automation-pattern.md`.
- When the skill governs broad or structural work, document Scope freshness, Serena setup, `ast-grep` usage, MCP applicability, and the required zero-debt exit condition.

## Workflow

1. Define the invariant (policy or quality behavior).
2. Create `rules.yml` with detection rules (ast-grep, ripgrep, or custom).
3. Run standardized gate on target project with `make val PROJECT=<name>`.
4. Verify with `make val PROJECT=<name> FIX=1` when autofix is needed.
5. Update skill SKILL.md and docs with exact command contract.
6. Run `make val PROJECTS="proj-a proj-b"` for integration scope.
7. Use root `make val` as the workspace gate entrypoint.

## Examples

Good:

```bash
make val PROJECT=flext-core
make val PROJECT=flext-core FIX=1
```

Why good: reproducible, non-interactive, and tied to artifacts.

Bad:

```text
Run checks manually and document expected output in chat only.
```

Why bad: no reusable command surface and no persisted evidence.

## Verification

- `make val PROJECT=<name>`
- `make val PROJECT=<name> FIX=1`
- `make val PROJECTS="proj-a proj-b"`
- `rg -n "## Scope|## References|## Rules|## Instructions|## Workflow|## Examples|## Verification" .agents/skills/flext-automation-skill-pattern/SKILL.md`
