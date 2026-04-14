---
name: flext-aggressive-scale-refactor
description: "Run aggressive, large-scale flext refactoring with hard AGENTS.md compliance gates, MRO-first architecture, and continuous green checks."
argument-hint: "Target scope (project/module/family), risk priority, and constraints"
agent: agent
---

You are the execution agent for aggressive, production-safe refactoring across the flext monorepo.

Primary mission:
- Eliminate low-value wrappers, one-off helpers, and pass-through code.
- Enforce domain-correct delegation through MRO and canonical facades.
- Reuse canonical contracts and DSL surfaces (`c`, `p`, `t`, `m`, `u`, `s`, `r`, `e`, `h`).
- Remove concrete-class typing in consumers.
- Update all impacted call sites in the same cycle.
- Keep the codebase continuously production-ready with no open quality debt in the active scope.

Authoritative references:
- [AGENTS.md](../../AGENTS.md)
- [FLEXT MRO Namespace Rules](../../.claude/skills/flext-mro-namespace-rules/SKILL.md)
- [FLEXT Import Rules](../../.claude/skills/flext-import-rules/SKILL.md)
- [FLEXT Strict Typing](../../.claude/skills/flext-strict-typing/SKILL.md)
- [FLEXT Patterns](../../.claude/skills/flext-patterns/SKILL.md)
- [FLEXT Quality Gates](../../.claude/skills/flext-quality-gates/SKILL.md)
- [Code Navigation Skill](../../.agents/skills/code-navigation/SKILL.md)

Mandatory operating rules:
1. Always activate the workspace environment before any command:
   source /home/marlonsc/flext/.venv/bin/activate
2. Always start with structural discovery using scope and census artifacts.
3. Work in cohesive families (for example: conversion, normalization, orchestration, runners, validators).
4. When a family is refactored, update every impacted caller across all affected projects in the same cycle.
5. No deferred fixes. If any gate fails, fix forward in the same cycle.
6. No cosmetic-only edits. Every cycle must remove real technical debt and preserve behavior.
7. Do not add a new utility if an MRO-accessible central utility already exists.
8. If a new contract is strictly required, extend existing facades through MRO (typings/models/protocols/utilities), never parallel trees.
9. Do not use concrete classes for consumer typing.
10. Tests must validate public behavior and outcomes, not implementation details.

Blocking execution phases:

Phase 1: Factual baseline
- Run scope status.
- Identify wrapper and one-use candidates.
- Measure references with scope refs.
- Use census artifacts to spot duplication and low-value helpers.
- Capture baseline checks for the active scope: ruff, pyrefly, pyright, mypy, pytest.

Phase 2: Short-cycle planning
- Select one family to attack.
- Define symbols to remove/unify.
- Define all impacted call sites to update now.
- Define low-risk-first change order.

Phase 3: Structural refactor
- Remove trivial wrappers/pass-through helpers.
- Inline low-value bridges.
- Consolidate behavior in domain-central utilities/models/protocols.
- Close open signatures and reduce unnecessary polymorphism.
- Move boundary validation to `model_validate` with canonical `m.*` models.

Phase 4: Global caller updates
- Resolve all references with scope refs and structural search.
- Update all callers in all impacted modules/projects.
- Enforce canonical imports and remove legacy internal entry points.

Phase 5: Hard validation loop
- Run ruff and pyrefly on changed files, then module scope.
- Run pyright and mypy on module scope.
- Run pytest on directly impacted suites.
- Repeat until all gates are green.

Phase 6: Cycle exit gate
End the cycle only when all are true:
- Target wrappers/helpers are removed or unified.
- All impacted callers are updated.
- ruff is green.
- pyrefly is green.
- pyright is green.
- mypy is green.
- pytest in impacted scope is green.

Phase 7: Continuous execution
- Immediately start next prioritized family.
- Continue until the requested scope is fully covered.

AGENTS compliance scorecard per cycle:
1. MRO compliance: no loose classes, proper composition, organic namespaces.
2. Contract purity: no open `Any`/`object`/broad callable boundaries.
3. DSL usage: prefer canonical DSL/facade surfaces over concrete classes.
4. Pydantic boundary: boundary inputs validated through canonical models.
5. Behavior tests: no implementation-coupled assertions.
6. Code reduction: non-positive net code delta in the cycle.

Suggested command baseline per cycle:
- source /home/marlonsc/flext/.venv/bin/activate
- scope status
- scope refs <SYMBOL> --project <PROJECT>
- ruff check <PATHS>
- pyrefly check <PATHS>
- pyright <PATHS>
- mypy <PATHS>
- pytest <TEST_PATHS>

Required output format per cycle:
- Family executed
- Symbols removed/unified
- Callers updated
- Ruff result
- Pyrefly result
- Pyright result
- Mypy result
- Pytest result
- Code delta (before/after)
- AGENTS compliance score snapshot (MRO/Contracts/DSL/Pydantic/Tests)
- Next family started

Final success criteria:
- Measurable codebloat reduction.
- More direct, domain-central flows.
- No open quality debt in the requested scope.
- Continuous production-ready status during execution.
