# Skill Automation Pattern

This guide defines the standard way to create reusable automation skills in this repository.

## Goal

Create automations that are reproducible, script-first, and enforceable by CI-style commands.

## Required Outputs

For each new automation family, deliver all items below:

1. One skill: `.claude/skills/<automation-name>/SKILL.md`
2. One checker script: `scripts/validation/<checker>.sh`
3. One orchestrator script: `scripts/validation/<orchestrator>.sh`
4. One docs page in `docs/guides/`
5. One baseline/report artifact path under `.sisyphus/`

## Standard Script Contract

Checker scripts must support policy modes:

```bash
scripts/validation/<checker>.sh --mode baseline --root .
scripts/validation/<checker>.sh --mode strict --root .
```

Orchestrator scripts must support execution depth:

```bash
scripts/validation/<orchestrator>.sh quick
scripts/validation/<orchestrator>.sh full
```

## Standard Skill Contract

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
2. Build checker script with machine-readable output.
3. Add baseline mode for no-regression enforcement.
4. Add strict mode for zero-violation enforcement.
5. Build orchestrator for quick/full runs.
6. Wire automation into `scripts/validate_all_projects.sh`.
7. Write or update skill doc with exact commands.
8. Add or update a docs guide in `docs/guides/`.
9. Run quick validation and integrated validation.

## Example (Current Pattern)

Current repository implementation for dict-to-pydantic enforcement:

- Skill: `.claude/skills/flext-dict-to-pydantic-plan/SKILL.md`
- Checker: `scripts/validation/enforce_no_dict_no_any.sh`
- AST rules: `scripts/validation/ast-grep-no-dict.yml`
- Orchestrator: `scripts/validation/run_automated_validation.sh`
- Baseline: `.sisyphus/baselines/policy_gate_baseline.json`
- Report: `.sisyphus/reports/policy_gate_latest.json`

## Verification Commands

```bash
bash -n scripts/validation/enforce_no_dict_no_any.sh
bash -n scripts/validation/run_automated_validation.sh
scripts/validation/run_automated_validation.sh quick
scripts/validate_all_projects.sh
```

## Adoption Rule

For future automation work, do not introduce manual-only procedures. Ship scripts + skill + docs together in the same change.
