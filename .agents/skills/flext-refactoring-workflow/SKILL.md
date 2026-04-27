---
name: flext-refactoring-workflow
description: Step-by-step refactoring workflow with quality gates, make targets, and commit discipline for the FLEXT monorepo. Use when refactoring a module, extracting mixins, decomposing classes exceeding the 200-line cap, migrating legacy patterns to current MRO/facade conventions, or cleaning up import boundary violations.

---

# FLEXT Refactoring Workflow

**Reviewed**: 2026-04-26 | **Scope**: Refactor flow under AGENTS.md §0.0 ZERO TOLERANCE TABLE.

## Hard Start Card (mandatory)

Hard line: one offender, one primitive, one proof chain; no helper/proxy/alias, no pass-through `__init__`, no zero-test pytest, no ambiguous output.

Ultra-short enforcement:

1. One offender.
2. Origin first, helper last.
3. True option bag -> one `model_validate(kwargs)`; fixed-shape signature -> explicit typed params + one `model_validate({...})`.
4. No manual kwargs normalization.
5. No magic literals if `c.*` exists.
6. `ruff` -> `pyrefly` immediately after first edit.
7. No raw output, no done.

Fast brief: search before write, origin before helper, model before manual kwargs, constants before inline literals, delete before add.

No-excuse mini card:

1. One offender.
2. No helper-first patches.
3. Validate real option bags once with `model_validate(kwargs)`; keep fixed-shape params explicit and validate one packed payload.
4. No magic literals when `c.*` exists.
5. `ruff` -> `pyrefly` before anything else.
6. No raw output, no done.

Failure signature (stop immediately): helper-first patch, manual kwargs normalization, guessed import origin, or positive LOC refactor.
Kill order: reuse origin -> validate once with Pydantic -> propagate -> gate.

Two-second start:

1. `qlty` first.
2. One offender.
3. Origin before helper.
4. `ruff` -> `pyrefly` after first edit.

Execution header (mandatory before first patch):

`OFFENDER=<file:line>; PRIMITIVE=<Annotated|validator|TypeAdapter|Discriminator|RootModel|TypeIs|match>; PROPAGATE=<scope/sg cmd>; GATE1=ruff <file>; GATE2=pyrefly <file>; TEST=<pytest target>`

Missing one field = no patch.

1. Smell first. `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json`
2. One offender + full caller chain only. No parallel edits.
3. Search before write. Reuse before create. Delete before extend.
4. If a canonical origin method/class already exists, use it directly; local helper duplication is invalid.
5. Structural propagation uses `sg`; manual grep rewrites are invalid.
6. Pydantic2/Python3.13 first (`TypeAdapter`, `Annotated`, validators, `computed_field`, `TypeIs`, `Self`, `@override`, `match/case`).
7. Prefer declarative model creation via `Model(**kwargs)`, `model_validate(...)`, and `model_copy(update=...)` over manual dict assembly or field-by-field mutation.
7.1 Manual/inplace kwargs validation (`pop/get/if` chains) is forbidden when one canonical Pydantic validation path can own the payload.
8. Do not create a local helper/envelope/spec class just to reduce a smell when an existing centralized origin or parent method already exists.
9. Net LOC must be negative.
10. Validate now: `ruff` -> `pyrefly` -> focused `pytest` -> affected `make check`.
11. Shared contract changed = propagate now, not later.
12. Empty/corrupted SARIF is invalid; rerun `qlty smells` before selecting offender.
13. A cycle is valid only with offender + caller audit + gate + raw output evidence.
14. If target file is in a sub-project, run status and gates in that sub-project context.
15. Ralph-loop iterations must update `ralph-progress.md` before the next offender.
16. Constants-first: no new inline magic string/number in runtime code when a `c.*` origin exists.
17. Real `**kwargs` must be validated through canonical Pydantic paths (`model_validate`, typed input models, or `TypeAdapter`) instead of manual key/type checks or inplace coercion.
17.1 Fixed-shape APIs do not become `**kwargs` bags to quiet `function-parameters`; keep explicit typed params and validate one packed payload with `model_validate({...})`.
18. Import origin is part of the refactor contract: if a facade import would re-enter lazy loading or duplicate an owner primitive, use the owner-origin import or existing parent method instead. Guessing the import source is invalid.
19. If a patch begins by adding a helper, assume it is wrong until two proofs exist: zero reusable origin hits and zero applicable Pydantic/Python deletion primitives.
20. Addition-heavy first passes are presumptively wrong. Re-search before continuing unless the added code eliminates at least 8x more duplicated code in the same cycle.

## Brutal Self-Critique Gate (mandatory)

Before first patch, write one short paragraph with:

1. Last recurring failure you are at risk of repeating.
2. The exact stop-rule that blocks it.
3. The exact Pydantic2/Python3.13 primitive replacing custom code.
4. The propagation command and first gate command.

Missing one item = no patch.

Short memory: the common failure is helper-first refactoring. The correction is always the same: grep the owning origin, validate kwargs with one typed model, delete manual normalization, then patch.

## 20s Context Load (mandatory)

State these before first patch:

1. Selected offender and exact file:line pair.
2. SSOT primitive being reused.
3. First gate command after edit.
4. Propagation command for callers.

If any item is missing, do not edit.

## First Paragraph Contract (mandatory)

State one short paragraph before editing with:

1. Selected offender file:line.
2. Exact SSOT primitive replacing the duplicate/custom path.
3. First post-edit gate command.
4. Caller propagation command.

If any field is missing, the cycle is invalid.

## Recurrence Kill-Switches (mandatory)

- Syntax break after first patch: stop and restore a minimal clean file before continuing.
- Any new helper/proxy/wrapper/compat alias: delete immediately in the same cycle.
- Contract changed without caller propagation: task invalid.
- Refactor with non-negative LOC delta: task invalid.
- Smell run skipped before edit: task invalid.
- Root-only validation evidence for sub-project target: task invalid.
- Wrong origin import causing lazy recursion or duplicate owner behavior: delete the patch and re-route to the owning primitive.

## Execution Plan Floor

`SMELL -> SEARCH -> DELETE -> COLLAPSE -> REPLACE with Pydantic2/Py3.13 -> PROPAGATE -> VALIDATE`

## Optimization Loop (mandatory when debt remains)

1. `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json`
2. Choose one `src/` offender (randomized if needed).
3. Refactor offender + usage chain with MRO + Pydantic2/Python3.13 first.
4. Validate touched scope (`ruff`, `pyrefly`, focused `pytest`).
5. Repeat until the current lane has no high-value unresolved offenders.

Completion rule: no "done" claim while unresolved `src/` offenders remain for the active lane.

Hard stop condition:

1. Selected-smell queue for the active lane is empty.
2. Each resolved smell has propagation evidence + green gate output.
3. Partial completion claims while queue is non-empty are invalid.

> **READ FIRST**: `AGENTS.md` §0.0 (the 18-rule ZERO TOLERANCE TABLE). Every rule below is a SPECIALIZATION of that table. Conflict between this skill and §0.0 → §0.0 wins.

## Scope

- End-to-end refactoring under §0.0 (SEARCH → REUSE → DELETE → COMPOSE-VIA-MRO → USE-PYDANTIC2/PY3.13 → only-then-EDIT).
- Tier-ordered sequencing, gate discipline, cross-project propagation.

## References

- `AGENTS.md`
- `base.mk`
- `Makefile`
- `ruff-shared.toml`
- `pyproject.toml`
- `.agents/skills/flext-scope-bootstrap/SKILL.md`

## Rules (specialization of §0.0)

- §0.0#1 SEARCH FIRST: grep `flext-{core,cli,infra,tests}/src` BEFORE writing.
- §0.0#2 NET-LOC < 0: every task `(deleted - added) > 0`. Report `LOC delta: -X (+Y, -Z)` + pyrefly delta + enforcement-warning delta. Delta ≥ 0 = TASK REJECTED.
- §0.0#3 8× DUPLICATION GATE on any new mixin/helper. Cite the multiplier in the commit.
- §0.0#4 MRO mixin into lowest existing facade. Standalone classes outside facade-composed tree FORBIDDEN.
- §0.0#5 Pydantic 2 + Python 3.13 patterns BEFORE writing custom code (TypeAdapter, RootModel, computed_field, discriminated unions, Annotated[T, Field], model_validator, ConfigDict, type X = …, TypeIs, match/case, @override/@final/Self, generic params, `cached_property`). Any custom code that an existing P2/Py3.13 feature replaces = DELETE.
- §0.0#6 forbidden constructs (pass-through wrappers, pass-through `__init__`, compat aliases, Any, cast(), os.environ in src/, model_rebuild(), unjustified noqa/type:ignore, hasattr(_priv), get_*/set_*/is_* accessors).
- Refactor in dependency-tier order; never break architecture directionality.
- Structural propagation: `ast-grep` (sg) for rewrites, `scope` for blast radius, Serena for symbol-aware ops (after `serena project health-check`).
- Zero debt steady state: ruff/pyrefly/enforcement/pytest must be ZERO across affected projects before task is complete (pre-existing failures count).

## Instructions

- Baseline current state before edits with `make check` and `make test`.
- If Scope is missing, stale, or misconfigured, follow `flext-scope-bootstrap` before starting blast-radius analysis.
- Apply smallest safe batch per file/tier and verify immediately.
- Expand validation scope whenever shared contracts/types are touched.

## Workflow

1. Baseline: run the 3 pre-edit commands from `AGENTS.md` §0.0.
2. Blast radius: use `scope`/`sg`/`grep` to map callers before first edit.
3. Deletion pass: remove wrappers, compat aliases, dead code, duplicated fields/methods first.
4. Reduction pass: replace remaining custom code with Pydantic 2 / Python 3.13 primitives.
5. MRO pass: collapse surviving duplication into the lowest existing facade.
6. Validate after each edited file.
7. Run widened project gates for shared changes.
8. Commit immediately after green gates.

## Examples

```bash
# Baseline + focused refactor cycle
make PROJECT=flext-core check
make PROJECT=flext-core test

# Validate dependent projects when shared APIs change
make PROJECTS="flext-core flext-auth flext-cli" check
```

## Verification

- `make check`
- `make test`
- `make val`
- `make PROJECT=<name> check`
- `make PROJECTS="proj-a proj-b" check`

## Fast Execution Contract

1. Read path skills: `rules-*` + typing/import skills for touched files.
2. Baseline the lane: `make check PROJECT=<affected>`.
3. Execute one offender loop only:
   - `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json`
   - select one offender + caller chain
   - delete duplicate/custom path via native Pydantic/Python primitive
   - propagate with `sg`
   - validate touched files (`ruff`, `pyrefly`, focused `pytest`)
4. If contract/signature/type changed, widen to affected projects with `make check PROJECTS="..."`.
5. Completion is valid only with raw command output + exit code and negative LOC delta.

## Hard Stops

- No smell run before edit -> invalid cycle.
- Non-negative LOC in refactor cycle -> invalid cycle.
- Shared contract changed without propagation proof -> invalid cycle.
- Any suppression (`type: ignore`, `noqa`, pyrefly ignore) as shortcut -> invalid cycle.
- Same failure twice -> stop and rewrite smallest clean block.
