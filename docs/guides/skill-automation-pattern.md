# Skill Automation Pattern

This guide defines the standard way to create reusable automation skills in this repository.

## Goal

Create automations that are reproducible, script-first, and enforceable by CI-style commands.

## Required Outputs

For each new automation family, deliver all items below:

1. One skill folder: `.agents/skills/<automation-name>/` containing:
   - `SKILL.md` — canonical skill document
   - `rules.yml` — detection rules (ast-grep, ripgrep, or custom)
   - `rules/` — ast-grep rule files (if any)
   - `baseline.json` — violation baseline (auto-generated)
2. One docs page in `docs/guides/` (if cross-cutting)

## Standard Skill Contract

Skills are validated by the canonical workspace service:

```bash
make val VALIDATE_SCOPE=workspace
```

`flext-infra` owns discovery, typed manifest parsing, rule execution, baselines,
reports, and stable exit mapping. A skill folder does not own a CLI or scanner.

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
2. Create `rules.yml` with detection rules (ast-grep, ripgrep, or custom).
3. Place ast-grep rule files in skill `rules/` directory.
4. Register the rule with the typed enforcement catalog and generate its baseline
   through the canonical `flext-infra` validation service.
5. Write or update skill doc with exact commands.
6. Add or update a docs guide in `docs/guides/` (if cross-cutting).
7. Run `make val VALIDATE_SCOPE=workspace` to verify integration.

## Example (Current Pattern)

Current repository implementation uses **declarative skill packages**. Each skill
folder owns documentation, `rules.yml`, structural rule assets, and fixtures. Typed
discovery, execution, baselines, and reports remain in `flext-infra` and are reached
through the Make dispatcher.

**Dict/Any Policy Gate**:

- Skill: `.agents/skills/flext-strict-typing/SKILL.md`
- Rules: `.agents/skills/flext-strict-typing/rules.yml` (10 rules: 8 ast-grep + 2 ripgrep)
- AST rules: `.agents/skills/flext-strict-typing/rules/*.yml`
- Baseline: `.agents/skills/flext-strict-typing/baseline.json`

**Pydantic v2 Policy Gate**:

- Skill: `.agents/skills/lib-pydantic-v2/SKILL.md`
- Rules: `.agents/skills/lib-pydantic-v2/rules.yml` (8 ast-grep rules)
- AST rules: `.agents/skills/lib-pydantic-v2/rules/*.yml`
- Baseline: `.agents/skills/lib-pydantic-v2/baseline.json`

**Generic runner**:

- `flext-infra` validation services — discover typed skill/rule contracts and are
  consumed through the workspace Make dispatcher.

## Verification Commands

```bash
make val VALIDATE_SCOPE=workspace
```

## Adoption Rule

For future automation work, do not introduce manual-only procedures. Ship scripts + skill + docs together in the same change.
