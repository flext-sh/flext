---
name: flext-agent-strict-rules
description: Mandatory rules for all coding agents — simple runtime aliases only (never u.Aliases.* for c,m,r,t,u,p,d,e,h,s,x), correct typing for narrowing (isinstance/TypeGuard, never type()), dismantle polymorphic code into centralized Pydantic v2 models, no loose methods. Apply across all projects (32+); use multiple agents in parallel for speed; lint-clean, no warnings/errors.
---

# Flext Agent Strict Rules (Mandatory)

**Scope**: All coding agents working in this repository.  
**Authority**: AGENTS.md §3 Code Law, §9 Agent Instructions. This skill expands and enforces them.

## Scope

- Mandatory guardrails for coding agents across all FLEXT projects.
- Runtime alias discipline, strict typing, polymorphic-model centralization, and validation integrity.

## References

- `AGENTS.md`
- `.claude/skills/flext-strict-typing/SKILL.md`
- `.claude/skills/flext-import-rules/SKILL.md`
- `.claude/skills/flext-patterns/SKILL.md`

## Rules

- Apply axiomatic typing and fallibility contracts uniformly to all namespaces.
- Use simple runtime aliases only; remove non-runtime alias indirection.
- Protocol contracts belong in `p`; composed reusable aliases belong in `t`; domain models belong in `m`.
- Never annotate with concrete classes when a canonical structural protocol or composed alias already expresses the contract.
- Dismantle polymorphic branching into centralized Pydantic v2 contracts.
- Enforce fix-forward git discipline and structural search/replace policy.
- Enforce abstraction boundaries in `examples/` and `scripts/` exactly as `src/` (no direct imports of abstracted third-party libraries outside owning domain).
- In runtime `src/` code, prefer `e.fail_*`, `r.fail_op`, and `r.fail_exc`; avoid ad-hoc `r.fail("...")` except explicit structured passthrough cases.

## Instructions

- Read impacted modules fully before changes and reuse existing contracts via MRO.
- If a consumer is too concrete, refine the shared contract in the ancestor facade first and keep the leaf project thin.
- Prefer ast-grep structural operations for broad migrations.
- Verify with required quality gates before claiming completion.

## Workflow

1. Identify which strict-rule cluster applies to the change.
2. Apply canonical pattern without introducing compatibility layers.
3. Update all impacted call sites/contracts.
4. Validate and record evidence.

## Examples

Good:

```python
from flext_core import p, r


def normalize_logger(owner: p.HasLogger) -> r[p.Logger]:
    return r[p.Logger].ok(owner.logger)
```

Why good: consumes the canonical public contract through `p.*` and keeps the return flow on `r[T]`.

Bad:

```python
def normalize_logger(owner: FlextLogger) -> FlextLogger:
    return owner
```

Why bad: pins the contract to a concrete implementation even though the public structural protocol is the real boundary.

## Verification

- `make check`
- `make test`
- `rg -n "type\(.*\) is|type\(.*\) ==" --glob "**/*.py"`


## 0. AXIOMATIC Type Purity (Absolute — No Exception — No Negotiation)

These rules are **AXIOMATIC**. They cannot be violated, deferred, exempted, or worked around under ANY circumstance. They apply to ALL `src/`, `tests/`, and `examples/` across ALL 33 projects.

- **`Any` is TOTALLY FORBIDDEN**: Never use `Any` in type annotations, function signatures, return types, variable types, examples, or generated code. Replace with explicit Pydantic models (`m.*`) and Protocol contracts (`p.*`) from project facades.
- **`t.NormalizedValue` is TOTALLY FORBIDDEN**: Never use `t.NormalizedValue` as a type annotation. Use explicit domain models and protocol contracts only.
- **`Mapping[str, Any]` is TOTALLY FORBIDDEN**: Replace with explicit model contracts (for example `m.<Domain>.InputModel`, `m.<Domain>.OutputModel`) and protocol boundaries (`p.*`).
- **`| None` is INLINE-ONLY — NEVER in type definitions**: `| None` is ONLY permitted INLINE at usage sites when `None` carries **distinct business/domain semantics** (e.g., "not configured" vs "empty string"). Gratuitous `| None` when a non-None default exists is FORBIDDEN. When default is `""`, type is `str`, NOT `str | None`. `| None` MUST NEVER appear in type alias definitions in `typings.py` — type aliases are ALWAYS non-nullable. Consumers add `| None` inline when business requires it (e.g., `field: t.Scalar | None = Field(default=None)`). If a type alias bakes in `| None`, it is a violation.
- **Type narrowing is RESTRICTED**: `isinstance`, `TypeGuard`, `TypeIs` are ONLY permitted when required by actual business logic. Never introduce type narrowing gratuitously to handle `None`/union types that should not exist in the first place.
- **ALL types come from `typings.py`**: Every type annotation in the codebase must use types defined in or imported through `FlextTypes` (`t.*`). Do not invent ad-hoc type annotations that duplicate what `typings.py` already provides.
- **Inline composed types are TOTALLY FORBIDDEN in ALL code**: Raw unions like `t.Primitives`, `Mapping[str, str | int | None]`, `Sequence[str | int]` written inline in `src/`, `tests/`, or `examples/` of ANY project are FORBIDDEN. Define composition inside centralized model contracts and reference them via `m.*`/`p.*`.
- **Duplicating type definitions is TOTALLY FORBIDDEN**: Re-declaring `ScalarValue`, `ConfigMap`, `ContainerValue`, or any type alias that already exists in the MRO chain is FORBIDDEN. Every subproject must reuse inherited contracts and explicit model/protocol definitions.
- **Compatibility aliases for types are TOTALLY FORBIDDEN**: No `MyModel = m.Domain.InputModel`, no `ConfigAlias = m.Settings.ConfigModel`, no `OutputAlias = m.Domain.OutputModel`, no `X = Y` renaming of any type contract.
- **Scope: ALL 33 projects, ALL directories, NO exceptions**: These rules apply uniformly to `src/`, `tests/`, and `examples/` across every project in the portfolio. No project, no directory, no file is exempt. Tests and examples MUST demonstrate the exact same strict typing discipline as production code. There is no "test-only" or "example-only" relaxation.
- **`r` (`r`) is MANDATORY for ALL fallible operations** function that can fail, raise, or return "not found" MUST return `r[T]` — never `T | None`, never a bare exception, never an ad-hoc error dict. The `r` alias (`from flext_core import r`) is MANDATORY at all usage sites — never spell out `r`. `r` exists to ELIMINATE `| None` return types and manual `try/except` in the business layer. Composition operators (`map`, `flat_map`, `lash`, `value_or`) MUST replace imperative `if result is None` / `try/except` chains. Only pure predicates (`-> bool`), `__init__` constructors, and trivially infallible getters may deviate — each deviation MUST be justified in a code comment.
- **Compatibility wrappers, legacy code, and validation fallbacks are TOTALLY FORBIDDEN and ABOMINABLE**: No `def legacy_method(): return new_method()` wrappers. No `try: new_way() except: old_way()` fallbacks. No keeping dead code "for compatibility". No `OldName = NewName` aliases. Legacy code is DELETED and replaced with the canonical pattern on contact. There is no grace period, no deprecation path, no "we'll remove it later".
- **AXIOMATIC Git Immutability — NEVER ROLLBACK, ALWAYS FIX FORWARD**: `git checkout <file>`, `git reset`, `git revert`, `git stash pop/apply`, and ANY operation that discards, overwrites, or rolls back committed or staged work by ANY agent is TOTALLY FORBIDDEN. Every change made by any agent in this repository MUST be accepted, improved, standardized, and fixed forward. If a previous agent's change is wrong, the ONLY permitted response is a NEW forward commit that corrects it. Stash operations that discard another agent's work are FORBIDDEN. `git checkout --theirs` is ONLY permitted during a rebase conflict on a file you do NOT own — and ONLY to accept the other agent's version (never to discard it). The correct response to broken code is ALWAYS: read it, understand it, fix it forward, commit the fix. There is no rollback. There is no undo. There is only forward. Violation of this rule is an EXTREME FAULT equivalent to destroying another agent's work.
- **AXIOMATIC ast-grep Supremacy — NEVER sed/find/custom scripts for code**: `mcp_ast_grep_search` / `mcp_ast_grep_replace` (MCP tools) are the SOLE mechanism for finding and rewriting code patterns. When MCP tools are available, they MUST be used first. When unavailable, the CLI `sg` command is the mandatory fallback. `grep`/`ripgrep` are ONLY permitted for plain-text content search (log lines, comments, string literals) — NEVER for locating code structure, symbols, imports, or type annotations. `find` is TOTALLY FORBIDDEN for locating code or information — use `glob` patterns or `ast-grep` instead. Custom Python/shell scripts written ad-hoc to fix, rewrite, or transform code are TOTALLY FORBIDDEN. `sed`, `awk`, and inline shell pipelines for code transformation are TOTALLY FORBIDDEN. The correct workflow: (1) `mcp_ast_grep_search` to locate all pattern instances, (2) `mcp_ast_grep_replace` (or `sg --rewrite`) to apply the transformation atomically, (3) verify with `make check`. Writing a one-off script to "fix" code is an EXTREME FAULT — it bypasses AST awareness, produces brittle text-level rewrites, and cannot be reviewed or audited.

- **AXIOMATIC — PEP 695 in `typings.py` follows AGENTS.md, and runtime narrowing stays out of alias syntax**: Type aliases in `typings.py` follow the canonical `type X = ...` rule from AGENTS.md. Because these aliases are annotation-only, runtime narrowing MUST use the canonical `u.is_*()` helpers or equivalent public guard utilities — never `isinstance(val, t.SomeAlias)`, never subclassing from a type alias, and never local compatibility syntax that creates a parallel type doctrine.
- **Every module MUST use a single nested class with MRO inheritance**: All domain logic MUST be organized into a nested class hierarchy. The most base class MUST inherit from Pydantic v2 `BaseModel` (or FLEXT base models like `FlextModels.ArbitraryTypesModel`, `FlextModels.FrozenModel`). Loose functions, standalone classes without MRO lineage, and modules without a nested class facade are FORBIDDEN. Subprojects MUST inherit from the parent project's facade class to cascade namespaces via MRO.
- **ALL code MUST be "Pydantic v2 way" EXTENSIVELY — USE, USE, USE Pydantic v2 features**: Every class extends `BaseModel` (or FLEXT base models) via MRO. `Field()` for ALL declarations with `description`, `title`, `examples`, `json_schema_extra` documenting business rules. `SecretStr`/`SecretBytes` for secrets. `ConfigDict(...)` for settings — standalone `*Config` classes FORBIDDEN (use `BaseSettings`/`ConfigDict`). Minimize custom `@field_validator`/`@model_validator` — prefer built-in constraints (`Field(ge=0)`, `StringConstraints()`, `Literal`, `constr`). FORBIDDEN in models: initialization helpers, unnecessary `@property`, simple getters/setters, line-reduction wrappers, pass-through methods — USE Pydantic built-ins (`@computed_field`, `model_post_init`, `PrivateAttr`). Enums/Mappings/Literals from `constants.py` (`c.*`), settings from `settings.py` (`s.*`). JSON via `model_dump_json()`, `model_validate_json()`, `TypeAdapter`. Internal state via `PrivateAttr` — never bare `self._x`. Nested classes MAY have business logic methods but ALL properties MUST use `Field()`/`PrivateAttr`. `models.py`/`_models/` for model definitions ONLY. If not using a Pydantic v2 feature, REVIEW and USE it; if not needed, use a simpler base and USE it fully.
- **Tests MUST follow the EXACT SAME rules as production code**: Test files are NOT exempt from ANY typing, Pydantic v2, r, or architectural rule. Test fixtures use `Field()`, typed models, `r[T]` returns. Test data uses `t.*` types. No "test-only" relaxation exists.
- **Every change MUST be INTEGRAL and pass ALL 4 linters**: Code is ONLY accepted after passing ruff, mypy, pyright, and pyrefly with ZERO errors, ZERO warnings. No partial fixes, no "fix later". ALL impacted references across the ENTIRE codeset MUST be immediately updated using ast-grep (`sg`) search-and-replace. After any type/model/signature change: (1) `sg` find-and-replace ALL references across all 33 projects, (2) `make check` on every affected project, (3) verify ZERO errors from all 4 linters. A change that breaks ANY linter in ANY project is REJECTED.
- **Linter suppression comments are FORBIDDEN without triple justification**: `# type: ignore`, `# noqa`, `# pyright: ignore`, `# pyrefly: ignore`, `# mypy: ignore` require ALL of: (1) well-founded technical explanation with REAL, verifiable internet citations (official docs, GitHub issues, PEPs), (2) explicit business necessity in the same comment, (3) per-line ONLY — never per-file, never per-module, never in settings. Global suppression rules are TOTALLY FORBIDDEN. The correct response to a linter error is to FIX THE CODE, not silence the linter.

---

## 1. Simple Runtime Aliases Only (Mandatory — No Exception)

- **Forbidden**: Never use `u.Aliases.constants()`, `.models()`, `.result()`, `.typings()`, `.protocols()`, `.utilities()`, `.decorators()`, `.exceptions()`, `.handlers()`, `.service_base()`, or `.mixins()` to define package-level aliases. Remove any such usage totally.
- **Required**: Use **simple runtime aliases only**: direct assignment to the facade class (e.g. `c = FlextConstants`, `m = FlextModels`, `r = r`, `t = FlextTypes`, `u = FlextUtilities`, `p = FlextProtocols`, `d = d`, `e = e`, `h = h`, `s = s`, `x = x`). No alias registry; no staticmethod layer for defining c, m, r, t, u, p, d, e, h, s, x.
- **Access**: Through the **project's runtime alias only**, preserving the organic namespace path produced by MRO. Call sites use paths such as `u.Infra.parse_semver`, `c.Tests.ERR_OK_FAILED`, and `m.TargetOracle.ExecuteResult`; facades MUST NOT flatten nested domain-local classes back to the root.
- **Rule**: One namespace per project. No duplicate alias assignments; no compatibility aliases (`LegacyX = NewX`). Remove all non-runtime aliases and loose (pass-through) methods; use canonical names and direct methods only.
- **Invalid instructions** text that says "resolve via MRO registry (u.Aliases)" or "use u.Aliases" is **wrong**. Remove it. Access is through the **project runtime alias only** (e.g. `m`, `c`, `r`, `t`, `u`, `p`, `d`, `e`, `h`, `s`, `x`) and must preserve the organic MRO namespace path.

---

## 2. No Loose Aliases or Pass-Through Methods

- **Remove** alias that only renames another symbol (e.g. `FactoryDiscovery = FactoryDecoratorsDiscovery`, `FlextModelsBase = FlextModelsBase`, `cast_direct = staticmethod(...)`). Call sites must use the canonical name.
- **Remove**: Methods that only delegate with no added behavior (e.g. `def foo(self): return Bar.baz(self)`). Call `Bar.baz` (or the canonical method) directly.
- **Rule**: Direct methods and single canonical names only. No wrappers that only forward.

---

## 3. Type Narrowing — Use `isinstance` or `TypeGuard`, Never `type()` for Narrowing

- **Forbidden**: Using `type(x) is T` or `type(x) == T` for the purpose of type narrowing in production code. Type checkers do not narrow on `type()`; they do on `isinstance()` and `TypeGuard`. Swapping `isinstance` for `type()` is forbidden.
- **Required**: Use correct typing for type narrowing: `isinstance(x, T)` or a `TypeGuard` so that after the check the type checker knows the type. For Pydantic models and structured data, prefer `model_validate` / `model_validate_json` so validation and type are centralized.
- **Exception**: AST or other code that intentionally requires exact type identity (e.g. `type(node) is ast.Call`) may keep `type()` only when the goal is exact class identity and no narrowing is needed in the same block; prefer `isinstance(node, ast.Call)` where narrowing is desired.
- **Rule**: Use correct typing to avoid type-narrowing failures. Never replace `isinstance` with `type()`.

---

## 4. Polymorphic Code → Centralized Pydantic v2 Models

- **Goal**: Dismantle polymorphic functions and methods into a single contract. Replace multiple branches on type/union with one (or a small set of) Pydantic v2 model(s) that define shape and validation.
- **Use**: Discriminated unions (`Literal` discriminator), `Field`, `model_validator`, `field_validator`, `model_validate`, `model_validate_json`. One entry point for validation; avoid long `if isinstance(...)` chains over many types.
- **Avoid**: Ad-hoc `Union[A, B, C]` handling with repeated `isinstance` in function bodies. Prefer overloads or a single validated model.
- **Rule**: Maximum use of centralized models with Pydantic v2 validation; minimal ad-hoc type branching.

---

## 5. Scale and Parallelism (all projects, strict)

- **Scope**: Apply these rules across **all projects** (flext-core, flext-cli, flext-api, flext-ldif, flext-ldap, flext-meltano, tap/target/dbt variants, etc.). Follow workspace governance in `AGENTS.md` plus project-local governance files when present.
- **Parallelism**: Use multiple agents in parallel at maximum scale (e.g. one agent per project or per report section) to complete refactors as fast as possible. Each agent: one project or one report section; minimal, verifiable changes; run `make check` and `make test` for touched project.
- **Quality**: Lint-clean with no warnings or errors; stability; remove all unnecessary code. Do not defer violations without explicit operator approval (AGENTS.md §8).
- **Checklist**: `.reports/EXECUTION-CHECKLIST-aliases-typing-polymorphic.md` — apply in order; validate after each batch.

---

## 6. Verification

- After edits: run the relevant `make check` / `make test` for the touched project. No claims of completion without executable evidence.
- **Reports** (apply in order; use multiple agents in parallel for scale):
  - `.reports/non-runtime-aliases-and-loose-methods.md` — remove listed aliases and loose methods; use canonical names at call sites.
  - `.reports/typing-violations-report.md` — replace `type()` / `__class__` with `isinstance` or TypeGuard.
  - `.reports/polymorphic-refactor-targets.md` — refactor polymorphic functions to centralized Pydantic v2 models.
- **Checklist**: `.reports/EXECUTION-CHECKLIST-aliases-typing-polymorphic.md`.
- **Zero Tolerance**: No `model_rebuild()`, no `inline imports`, no `try-except ImportError`, and no `cast()` outside `flext-core` result internals.

---

## 8. Zero Tolerance for "Hacks" (Mandatory — No Exception)

- **Forbidden: `model_rebuild()`**: Strictly prohibited in ALL code (src, tests, scripts). You must resolve type references at definition time by fixing import order or using protocol-based decoupling.
- **Forbidden: `inline imports`**: Strictly prohibited inside any function, method, or class body. All imports MUST be at the top of the module.
- **Forbidden: `lazy imports`**: Strictly prohibited inside any function or class. The ONLY exception is module-level `__getattr__` in `__init__.py` for package-level optimization.
- **Forbidden: `try-except ImportError`**: Strictly prohibited for handling optional dependencies. Define clear architecture tiers and use protocols to bridge external dependencies.
- **Forbidden: `cast()`**: Prohibited in all project code. Use `isinstance`, `TypeGuard`, or model-refinement to satisfy the type checker. Exception: Only allowed in foundational core implementation (e.g., `result.py`) where generics are physically impossible to satisfy without it.
- **Forbidden: Dynamic Evaluation**: `eval()`, `exec()`, and architectural `getattr()`/`setattr()` are strictly prohibited. Architecture must be static and analyzable.

---

## 9. Mandatory Agent Instructions (Non-Negotiable)


1. **Typing (AXIOMATIC)**: `Any`, `t.NormalizedValue`, and `Mapping[str, Any]` are **TOTALLY FORBIDDEN** in type annotations, function signatures, return types, examples, and generated code. Use **exclusively** `t.*` contracts from `typings.py`. `| None` in type unions (`X | None`) is ONLY permitted when `None` carries distinct business/domain semantics (e.g., "not configured" vs "empty string"). Type narrowing (`isinstance`, `TypeGuard`) is ONLY permitted when required by business logic — never introduced gratuitously. `r` (`r`) is MANDATORY for all fallible operations — `T | None` return types and manual `try/except` in business logic are FORBIDDEN when `r[T]` can express the same intent.
2. **Contract ownership (AXIOMATIC)**: Structural protocols live in `protocols.py` and are consumed through `p.*`. Reusable composed aliases live in `typings.py` and are consumed through `t.*`. Domain carriers live in `models.py` and are consumed through `m.*`. Do not place protocol-shaped contracts in `t`, and do not annotate with concrete classes when `p.*` or `t.*` already covers the contract.
3. **Polymorphism**: Dismantle **ALL** polymorphic function/method modes: replace branching across 3+ types with **centralized Pydantic v2 models** (discriminated unions, `Field`, `@field_validator`, `@model_validator`). Maximize centralized models with Pydantic v2 validation; minimize ad-hoc type branching.
4. **Aliases**: **ONLY** simple runtime aliases (e.g., `c = FlextConstants`, `m = FlextModels`, `x = x`). **NEVER** use `u.Aliases` or any alias registry; remove all such usage completely. Access through the project namespace only and preserve the organic MRO path instead of flattening nested symbols back to the facade root.
5. **Removal**: Remove all non-runtime aliases and loose pass-through methods; use only direct methods and canonical names. Enforce runtime alias usage.
6. **Scale**: Use **multiple agents in parallel at scale** (one agent per project or per report section) to apply refactors as fast as possible across all 33 projects. Each agent: one project or one section; minimal and verifiable changes; run `make check` and `make test` on the touched project.
7. **Quality**: Code MUST be free of ruff and pyright warnings/errors; stable; remove unnecessary code. Do NOT alter established patterns from SKILLS and AGENTS.md; surgical changes only; never break business functionality.
8. **Hacks (Zero Tolerance)**: **NEVER** use `model_rebuild()`, `inline imports`, `cast()` (except in core `result.py`), `eval`/`exec`, or `try-except ImportError`. Everything MUST be resolved via architecture, MRO, protocols, and correct top-level declaration order.
9. **Legacy/Compatibility (Zero Tolerance — ABOMINABLE)**: Simple compatibility wrappers, non-business validation fallbacks, legacy code of ANY kind, and `OldName = NewName` compatibility aliases are TOTALLY FORBIDDEN. Legacy code is DELETED and replaced with the canonical pattern immediately. No grace period, no deprecation path.
10. **Module Structure (AXIOMATIC)**: Every module MUST organize domain logic into a single nested class hierarchy using MRO inheritance from Pydantic v2 `BaseModel` (or FLEXT base models). Loose functions and standalone classes without MRO lineage are FORBIDDEN. Subprojects MUST inherit from the parent project's facade class.
11. **Pydantic v2 Way (AXIOMATIC — USE EXTENSIVELY)**: Every class extends `BaseModel` via MRO. `Field()` with `description`/`title`/`examples`/`json_schema_extra` for ALL fields. Minimize custom validators — prefer built-in constraints. FORBIDDEN: `*Config` classes (use `BaseSettings`/`ConfigDict`), initialization helpers, unnecessary `@property`, simple getters/setters, wrappers. USE Pydantic built-ins: `@computed_field`, `model_post_init`, `PrivateAttr`, `TypeAdapter`. Enums/Literals from `c.*`, settings from `s.*`. Internal state via `PrivateAttr`. `models.py`/`_models/` for models ONLY. If not using a feature — REVIEW and USE it.
12. **Tests = Production Discipline (AXIOMATIC)**: Tests MUST demonstrate the EXACT SAME strict typing, Pydantic v2, r, and architectural discipline as production code. No "test-only" relaxation of any rule.
13. **Integral Changes (AXIOMATIC)**: Every change MUST pass ALL 4 linters (ruff, mypy, pyright, pyrefly) with ZERO errors. ALL impacted references across ALL 33 projects MUST be immediately updated via ast-grep (`sg`) search-and-replace. Run `make check` on every affected project. A change that breaks ANY linter in ANY project is REJECTED.
14. **No Linter Suppressions (AXIOMATIC)**: `# type: ignore`, `# noqa`, `# pyright: ignore`, `# pyrefly: ignore`, `# mypy: ignore` are FORBIDDEN without: (1) real internet citations proving unavoidability, (2) business necessity in the comment, (3) per-line only. Global suppressions in settings files are TOTALLY FORBIDDEN. Fix the code, never silence the linter.
15. **ast-grep Supremacy (AXIOMATIC)**: `mcp_ast_grep_search` / `mcp_ast_grep_replace` (MCP) are the SOLE mechanism for code search and structural replacement. CLI `sg` is the mandatory fallback when MCP is unavailable. `grep`/`ripgrep` for plain-text only (never code structure). `find` TOTALLY FORBIDDEN for code location — use `glob` or `ast-grep`. Custom scripts, `sed`, `awk`, shell pipelines for code transformation are TOTALLY FORBIDDEN. Workflow: (1) `mcp_ast_grep_search` → (2) `mcp_ast_grep_replace` or `sg --rewrite` → (3) `make check`. Writing a one-off script to fix code is an EXTREME FAULT.
16. **Git Immutability (AXIOMATIC)**: `git checkout <file>`, `git reset`, `git revert`, `git stash pop/apply` to discard any agent's work are TOTALLY FORBIDDEN. Every change MUST be accepted, improved, and fixed forward via a new commit. `git checkout --theirs` ONLY during rebase conflict on a file you do NOT own. Violation = EXTREME FAULT.
17. **Commit-After-Validation (AXIOMATIC)**: Immediately after ANY validation passes (linters, tests, `make check`, any quality gate), ALL pending changes across ALL touched projects MUST be committed and pushed — without delay, without waiting, without asking permission. Sequence: validation passes → `git add -A` (every project with changes) → `git commit` → `git pull --rebase` → `git push` → confirm clean `git status`. Uncommitted work after a passing validation is a VIOLATION. Unpushed work is LOST WORK — it does not exist.
18. **Full Context Evaluation Before Every Change (AXIOMATIC)**: Before ANY code change, the agent MUST: (1) read and fully understand ALL existing code in the affected module — its patterns, MRO chain, dependencies, base classes, and existing contracts; (2) maximize reuse of existing library code, base classes, utilities, and type contracts — never reinvent, duplicate, or shadow what already exists; (3) apply changes uniformly across ALL namespaces — `src/`, `tests/`, AND `examples/` — every namespace is in scope, no namespace is exempt; (4) produce the most correct, complete, lint-free implementation using advanced code patterns, strong typing, full Pydantic v2 discipline, and the full power of the existing architecture. Simplifications, bypasses, mocks, fallbacks, stubs, TODOs, hardcoded values, and placeholder logic are TOTALLY FORBIDDEN in any committed code. Every change is final, complete, and production-grade from the first commit. Agents that skip context evaluation, ignore existing patterns, or produce partial implementations are in violation.
