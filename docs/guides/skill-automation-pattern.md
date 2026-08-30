# Skill Automation Pattern

<!-- TOC START -->
- [Goal](#goal)
- [Required Outputs](#required-outputs)
- [Standard Skill Contract](#standard-skill-contract)
- [Standard Skill Format](#standard-skill-format)
- [Implementation Checklist](#implementation-checklist)
- [Example (Current Pattern)](#example-current-pattern)
- [Verification Commands](#verification-commands)
- [Adoption Rule](#adoption-rule)
<!-- TOC END -->

This guide defines the standard way to create reusable automation skills in this repository.

## Goal

Create automations that are reproducible, script-first, and enforceable by CI-style commands.

## Required Outputs

For each new automation family, deliver all items below:

1. One skill folder: `.agents/skills/<automation-name>/` containing:
   - `SKILL.md` — canonical skill document
   - static enforcement rules are DATA in `flext-infra/config/enforcement/*.yaml`
     (Pydantic-2-validated), evaluated by the shared rope-semantic engine — NOT
     per-skill `rules.yml`, NOT ast-grep/ripgrep/bespoke detector files (LAW1/LAW2)
   - `baseline.json` — violation baseline (auto-generated)
2. One docs page in `docs/guides/` (if cross-cutting)

## Standard Skill Contract

Skills are validated by the generic runner:

```bash
python3 scripts/core/skill_validate.py --skill <name>
python3 scripts/core/skill_validate.py --skill <name> --mode strict
python3 scripts/core/skill_validate.py --skill <name> --update-baseline
```

The runner auto-discovers all skills:

```bash
python3 scripts/core/skill_validate.py --all
```

## Standard Skill Format

The skill must follow the canonical format from `skill-format-universal` and include:

- Concrete paths under `## Scope`
- Existing anchors under `## References`
- Enforceable behaviors under `## Rules`
- Copyable commands under `## Instructions`
- Ordered execution in `## Workflow`
- Good/Bad examples under `## Examples`
- Executable checks under `## Verification`

## Implementation Checklist

1. Define the invariant (policy or quality requirement).
2. Declare the rule as Pydantic-2-validated DATA in `flext-infra/config/enforcement/*.yaml`
   (closed operator set over the rope-semantic fact base); NEVER Python rule logic, ast-grep,
   or a per-skill `rules/` directory. `flext-core` holds runtime/beartype rules only.
3. Initialize baseline with `python3 scripts/core/skill_validate.py --skill <name> --update-baseline`.
4. Write or update skill doc with exact commands.
5. Add or update a docs guide in `docs/guides/` (if cross-cutting).
6. Run `python3 scripts/core/skill_validate.py --all` to verify integration.

## Example (Current Pattern)

Current repository implementation routes ALL static enforcement rules to
`flext-infra/config/enforcement/*.yaml` as Pydantic-2-validated data, evaluated by the shared
rope-semantic engine (`ctx.rope_project`; `ast`/`ast-grep`/`get_ast` banned per LAW2). Skills
document intent and point at the config SSOT; they do not own rule data or detector code.
The generic runner `scripts/core/skill_validate.py` discovers and executes everything.

**Dict/Any Policy Gate**:

- Skill: `.agents/skills/flext-strict-typing/SKILL.md` (documents intent; points at config SSOT)
- Rules: declared as data in `flext-infra/config/enforcement/*.yaml`, evaluated rope-semantically

**Pydantic v2 Policy Gate**:

- Skill: `.agents/skills/lib-pydantic-v2/SKILL.md` (documents intent; points at config SSOT)
- Rules: declared as data in `flext-infra/config/enforcement/*.yaml`, evaluated rope-semantically

**Generic runner**:

- `scripts/core/skill_validate.py` — runs the rope-semantic engine over the rules declared in `flext-
  infra/config/enforcement/*.yaml`

## Verification Commands

```bash
python3 scripts/core/skill_validate.py --list-skills
python3 scripts/core/skill_validate.py --skill flext-strict-typing
python3 scripts/core/skill_validate.py --skill lib-pydantic-v2
python3 scripts/core/skill_validate.py --all
```

## Adoption Rule

For future automation work, do not introduce manual-only procedures. Ship scripts + skill + docs together in the same
change.
