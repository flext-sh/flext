---
name: flext-agent-strict-rules
description: Mandatory rules for all coding agents — simple runtime aliases only (never FlextRuntime.Aliases.* for c,m,r,t,u,p,d,e,h,s,x), correct typing for narrowing (isinstance/TypeGuard, never type()), dismantle polymorphic code into centralized Pydantic v2 models, no loose methods. Apply across all projects (32+); use multiple agents in parallel for speed; lint-clean, no warnings/errors.
---

# Flext Agent Strict Rules (Mandatory)

**Scope**: All coding agents working in this repository.  
**Authority**: CLAUDE.md §3 Code Law, §9 Agent Instructions. This skill expands and enforces them.


## 0. AXIOMATIC Type Purity (Absolute — No Exception — No Negotiation)

These rules are **AXIOMATIC**. They cannot be violated, deferred, exempted, or worked around under ANY circumstance. They apply to ALL `src/`, `tests/`, and `examples/` across ALL 33 projects.

- **`Any` is TOTALLY FORBIDDEN**: Never use `Any` in type annotations, function signatures, return types, variable types, examples, or generated code. Replace with `t.*` contracts from `typings.py` (`t.GeneralValueType`, `t.ScalarValue`, `t.ConfigMap`, `t.Dict`, `t.JsonValue`, etc.).
- **`object` is TOTALLY FORBIDDEN**: Never use `object` as a type annotation. Replace with the specific `t.*` type that matches the semantic intent (e.g., `t.GeneralValueType` for general-purpose values).
- **`dict[str, Any]` is TOTALLY FORBIDDEN**: Use `t.ConfigMap`, `t.Dict`, `t.ServiceMap`, or `Mapping[str, t.GeneralValueType]` depending on the semantic context.
- **`| None` is INLINE-ONLY — NEVER in type definitions**: `| None` is ONLY permitted INLINE at usage sites when `None` carries **distinct business/domain semantics** (e.g., "not configured" vs "empty string"). Gratuitous `| None` when a non-None default exists is FORBIDDEN. When default is `""`, type is `str`, NOT `str | None`. `| None` MUST NEVER appear in type alias definitions in `typings.py` — type aliases are ALWAYS non-nullable. Consumers add `| None` inline when business requires it (e.g., `field: t.ScalarValue | None = Field(default=None)`). If a type alias bakes in `| None`, it is a violation.
- **Type narrowing is RESTRICTED**: `isinstance`, `TypeGuard`, `TypeIs` are ONLY permitted when required by actual business logic. Never introduce type narrowing gratuitously to handle `None`/union types that should not exist in the first place.
- **ALL types come from `typings.py`**: Every type annotation in the codebase must use types defined in or imported through `FlextTypes` (`t.*`). Do not invent ad-hoc type annotations that duplicate what `typings.py` already provides.
- **Inline composed types are TOTALLY FORBIDDEN in ALL code**: Raw unions like `str | int | float | bool`, `dict[str, str | int | None]`, `list[str | int]` written inline in `src/`, `tests/`, or `examples/` of ANY project are FORBIDDEN. All composed types MUST be defined in `flext-core/typings.py` (or MRO-inherited `FlextTypes`) and referenced via `t.*`. Only `flext-core/typings.py` defines the raw unions; consumers use `t.ScalarValue`, `t.GeneralValueType`, etc. No inline union composition anywhere.
- **Duplicating type definitions is TOTALLY FORBIDDEN**: Re-declaring `ScalarValue`, `ConfigMap`, `JsonValue`, or any type alias that already exists in the `FlextTypes` MRO chain is FORBIDDEN — even inside the subproject's own `FlextTypes` nested classes. Every subproject MUST inherit `FlextTypes` via MRO (`class FlextTapLdapTypes(FlextMeltanoTypes): ...`) and use the inherited `t.*` contracts. One definition, one source of truth, always inherited via MRO.
- **Compatibility aliases for types are TOTALLY FORBIDDEN**: No `MyScalar = t.ScalarValue`, no `ConfigDict = t.ConfigMap`, no `AnyValue = t.GeneralValueType`, no `X = t.Y` renaming of any kind. Reference `t.*` directly at every usage site. No indirection, no local re-exports, no renaming. Not even "convenience" aliases.
- **Scope: ALL 33 projects, ALL directories, NO exceptions**: These rules apply uniformly to `src/`, `tests/`, and `examples/` across every project in the portfolio. No project, no directory, no file is exempt. Tests and examples MUST demonstrate the exact same strict typing discipline as production code. There is no "test-only" or "example-only" relaxation.
- **`FlextResult` (`r`) is MANDATORY for ALL fallible operations**: Any function that can fail, raise, or return "not found" MUST return `r[T]` — never `T | None`, never a bare exception, never an ad-hoc error dict. The `r` alias (`from flext_core import r`) is MANDATORY at all usage sites — never spell out `FlextResult`. `FlextResult` exists to ELIMINATE `| None` return types and manual `try/except` in the business layer. Composition operators (`map`, `flat_map`, `lash`, `value_or`) MUST replace imperative `if result is None` / `try/except` chains. Only pure predicates (`-> bool`), `__init__` constructors, and trivially infallible getters may deviate — each deviation MUST be justified in a code comment.
- **Compatibility wrappers, legacy code, and validation fallbacks are TOTALLY FORBIDDEN and ABOMINABLE**: No `def legacy_method(): return new_method()` wrappers. No `try: new_way() except: old_way()` fallbacks. No keeping dead code "for compatibility". No `OldName = NewName` aliases. Legacy code is DELETED and replaced with the canonical pattern on contact. There is no grace period, no deprecation path, no "we'll remove it later".
- **Every module MUST use a single nested class with MRO inheritance**: All domain logic MUST be organized into a nested class hierarchy. The most base class MUST inherit from Pydantic v2 `BaseModel` (or FLEXT base models like `FlextModels.ArbitraryTypesModel`, `FlextModels.FrozenModel`). Loose functions, standalone classes without MRO lineage, and modules without a nested class facade are FORBIDDEN. Subprojects MUST inherit from the parent project's facade class to cascade namespaces via MRO.
- **ALL code MUST be "Pydantic v2 way" EXTENSIVELY — USE, USE, USE Pydantic v2 features**: Every class extends `BaseModel` (or FLEXT base models) via MRO. `Field()` for ALL declarations with `description`, `title`, `examples`, `json_schema_extra` documenting business rules. `SecretStr`/`SecretBytes` for secrets. `ConfigDict(...)` for config — standalone `*Config` classes FORBIDDEN (use `BaseSettings`/`ConfigDict`). Minimize custom `@field_validator`/`@model_validator` — prefer built-in constraints (`Field(ge=0)`, `StringConstraints()`, `Literal`, `constr`). FORBIDDEN in models: initialization helpers, unnecessary `@property`, simple getters/setters, line-reduction wrappers, pass-through methods — USE Pydantic built-ins (`@computed_field`, `model_post_init`, `PrivateAttr`). Enums/Mappings/Literals from `constants.py` (`c.*`), config from `settings.py` (`s.*`). JSON via `model_dump_json()`, `model_validate_json()`, `TypeAdapter`. Internal state via `PrivateAttr` — never bare `self._x`. Nested classes MAY have business logic methods but ALL properties MUST use `Field()`/`PrivateAttr`. `models.py`/`_models/` for model definitions ONLY. If not using a Pydantic v2 feature, REVIEW and USE it; if not needed, use a simpler base and USE it fully.
- **Tests MUST follow the EXACT SAME rules as production code**: Test files are NOT exempt from ANY typing, Pydantic v2, FlextResult, or architectural rule. Test fixtures use `Field()`, typed models, `r[T]` returns. Test data uses `t.*` types. No "test-only" relaxation exists.
- **Every change MUST be INTEGRAL and pass ALL 4 linters**: Code is ONLY accepted after passing ruff, mypy, pyright, and pyrefly with ZERO errors, ZERO warnings. No partial fixes, no "fix later". ALL impacted references across the ENTIRE codeset MUST be immediately updated using ast-grep (`sg`) search-and-replace. After any type/model/signature change: (1) `sg` find-and-replace ALL references across all 33 projects, (2) `make check` on every affected project, (3) verify ZERO errors from all 4 linters. A change that breaks ANY linter in ANY project is REJECTED.
- **Linter suppression comments are FORBIDDEN without triple justification**: `# type: ignore`, `# noqa`, `# pyright: ignore`, `# pyrefly: ignore`, `# mypy: ignore` require ALL of: (1) well-founded technical explanation with REAL, verifiable internet citations (official docs, GitHub issues, PEPs), (2) explicit business necessity in the same comment, (3) per-line ONLY — never per-file, never per-module, never in config. Global suppression rules are TOTALLY FORBIDDEN. The correct response to a linter error is to FIX THE CODE, not silence the linter.

---

## 1. Simple Runtime Aliases Only (Mandatory — No Exception)

- **Forbidden**: Never use `FlextRuntime.Aliases.constants()`, `.models()`, `.result()`, `.typings()`, `.protocols()`, `.utilities()`, `.decorators()`, `.exceptions()`, `.handlers()`, `.service_base()`, or `.mixins()` to define package-level aliases. Remove any such usage totally.
- **Required**: Use **simple runtime aliases only**: direct assignment to the facade class (e.g. `c = FlextConstants`, `m = FlextModels`, `r = FlextResult`, `t = FlextTypes`, `u = FlextUtilities`, `p = FlextProtocols`, `d = FlextDecorators`, `e = FlextExceptions`, `h = FlextHandlers`, `s = FlextService`, `x = FlextMixins`). No alias registry; no staticmethod layer for defining c, m, r, t, u, p, d, e, h, s, x.
- **Facade pattern**: Each facade (e.g. FlextUtilities) MUST expose **staticmethod aliases from external subclasses** so call sites have **one flat namespace** (e.g. `u.foo`, `u.bar`). No subdivision of namespaces (no `u.Mapper.foo` at call sites). Subprojects: access **only** via that project's namespace (`from flext_cli import m, u` then `m.Foo`, `u.parse`).
- **Access**: Through the **project's runtime alias only**, with no subdivision. Subprojects define nested classes for organization then **class-level aliases at the facade root** so call sites use `m.Foo`, `m.Bar`. Aliases and namespaces follow the **MRO protocol only**. Use direct methods; runtime helpers come from **x** (FlextMixins) via MRO.
- **Rule**: One namespace per project. No duplicate alias assignments; no compatibility aliases (`LegacyX = NewX`). Remove all non-runtime aliases and loose (pass-through) methods; use canonical names and direct methods only.
- **Invalid instructions**: Any text that says "resolve via MRO registry (FlextRuntime.Aliases)" or "use FlextRuntime.Aliases" is **wrong**. Remove it. Access is through the **project runtime alias only** (e.g. `m`, `c`, `r`, `t`, `u`, `p`, `d`, `e`, `h`, `s`, `x`); MRO protocol only; **no** alias registry or staticmethod layer.

---

## 2. No Loose Aliases or Pass-Through Methods

- **Remove**: Any alias that only renames another symbol (e.g. `FactoryDiscovery = FactoryDecoratorsDiscovery`, `FlextModelsBase = FlextModelFoundation`, `cast_direct = staticmethod(...)`). Call sites must use the canonical name.
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

- **Scope**: Apply these rules across **all projects** (flext-core, flext-cli, flext-api, flext-ldif, flext-ldap, flext-meltano, tap/target/dbt variants, etc.). Follow each project's standards (CLAUDE.md, per-project CLAUDE.md).
- **Parallelism**: Use multiple agents in parallel at maximum scale (e.g. one agent per project or per report section) to complete refactors as fast as possible. Each agent: one project or one report section; minimal, verifiable changes; run `make check` and `make test` for touched project.
- **Quality**: Lint-clean with no warnings or errors; stability; remove all unnecessary code. Do not defer violations without explicit operator approval (CLAUDE.md §8).
- **Checklist**: `.reports/EXECUTION-CHECKLIST-aliases-typing-polymorphic.md` — apply in order; validate after each batch.

---

## 6. Verification

- After edits: run the relevant `make check` / `make test` for the touched project. No claims of completion without executable evidence.
- **Reports** (apply in order; use multiple agents in parallel for scale):
  - `.reports/non-runtime-aliases-and-loose-methods.md` — remove listed aliases and loose methods; use canonical names at call sites.
  - `.reports/typing-violations-report.md` — replace `type()` / `__class__` with `isinstance` or TypeGuard.
  - `.reports/polymorphic-refactor-targets.md` — refactor polymorphic functions to centralized Pydantic v2 models.
- **Checklist**: `.reports/EXECUTION-CHECKLIST-aliases-typing-polymorphic.md`.
- **Zero Tolerance**: No `model_rebuild()`, no `inline imports`, no `cast()`, no `try-except ImportError`.

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


1. **Typing (AXIOMATIC)**: `Any`, `object`, and `dict[str, Any]` are **TOTALLY FORBIDDEN** in type annotations, function signatures, return types, examples, and generated code. Use **exclusively** `t.*` contracts from `typings.py`. `| None` in type unions (`X | None`) is ONLY permitted when `None` carries distinct business/domain semantics (e.g., "not configured" vs "empty string"). Type narrowing (`isinstance`, `TypeGuard`) is ONLY permitted when required by business logic — never introduced gratuitously. `FlextResult` (`r`) is MANDATORY for all fallible operations — `T | None` return types and manual `try/except` in business logic are FORBIDDEN when `r[T]` can express the same intent.
2. **Polymorphism**: Dismantle **ALL** polymorphic function/method modes: replace branching across 3+ types with **centralized Pydantic v2 models** (discriminated unions, `Field`, `@field_validator`, `@model_validator`). Maximize centralized models with Pydantic v2 validation; minimize ad-hoc type branching.
3. **Aliases**: **ONLY** simple runtime aliases (e.g., `c = FlextConstants`, `m = FlextModels`, `x = FlextMixins`). **NEVER** use `FlextRuntime.Aliases` or any alias registry; remove all such usage completely. Facades expose **staticmethod aliases of external subclasses** into a single flat namespace; subprojects: access **ONLY** within the project namespace.
4. **Removal**: Remove all non-runtime aliases and loose pass-through methods; use only direct methods and canonical names. Enforce runtime alias usage.
5. **Scale**: Use **multiple agents in parallel at scale** (one agent per project or per report section) to apply refactors as fast as possible across all 33 projects. Each agent: one project or one section; minimal and verifiable changes; run `make check` and `make test` on the touched project.
6. **Quality**: Code MUST be free of ruff and pyright warnings/errors; stable; remove unnecessary code. Do NOT alter established patterns from SKILLS and CLAUDE.md; surgical changes only; never break business functionality.
7. **Hacks (Zero Tolerance)**: **NEVER** use `model_rebuild()`, `inline imports`, `cast()` (except in core `result.py`), `eval`/`exec`, or `try-except ImportError`. Everything MUST be resolved via architecture, MRO, protocols, and correct top-level declaration order.
8. **Legacy/Compatibility (Zero Tolerance — ABOMINABLE)**: Simple compatibility wrappers, non-business validation fallbacks, legacy code of ANY kind, and `OldName = NewName` compatibility aliases are TOTALLY FORBIDDEN. Legacy code is DELETED and replaced with the canonical pattern immediately. No grace period, no deprecation path.
9. **Module Structure (AXIOMATIC)**: Every module MUST organize domain logic into a single nested class hierarchy using MRO inheritance from Pydantic v2 `BaseModel` (or FLEXT base models). Loose functions and standalone classes without MRO lineage are FORBIDDEN. Subprojects MUST inherit from the parent project's facade class.
10. **Pydantic v2 Way (AXIOMATIC — USE EXTENSIVELY)**: Every class extends `BaseModel` via MRO. `Field()` with `description`/`title`/`examples`/`json_schema_extra` for ALL fields. Minimize custom validators — prefer built-in constraints. FORBIDDEN: `*Config` classes (use `BaseSettings`/`ConfigDict`), initialization helpers, unnecessary `@property`, simple getters/setters, wrappers. USE Pydantic built-ins: `@computed_field`, `model_post_init`, `PrivateAttr`, `TypeAdapter`. Enums/Literals from `c.*`, config from `s.*`. Internal state via `PrivateAttr`. `models.py`/`_models/` for models ONLY. If not using a feature — REVIEW and USE it.
11. **Tests = Production Discipline (AXIOMATIC)**: Tests MUST demonstrate the EXACT SAME strict typing, Pydantic v2, FlextResult, and architectural discipline as production code. No "test-only" relaxation of any rule.
12. **Integral Changes (AXIOMATIC)**: Every change MUST pass ALL 4 linters (ruff, mypy, pyright, pyrefly) with ZERO errors. ALL impacted references across ALL 33 projects MUST be immediately updated via ast-grep (`sg`) search-and-replace. Run `make check` on every affected project. A change that breaks ANY linter in ANY project is REJECTED.
13. **No Linter Suppressions (AXIOMATIC)**: `# type: ignore`, `# noqa`, `# pyright: ignore`, `# pyrefly: ignore`, `# mypy: ignore` are FORBIDDEN without: (1) real internet citations proving unavoidability, (2) business necessity in the comment, (3) per-line only. Global suppressions in config files are TOTALLY FORBIDDEN. Fix the code, never silence the linter.
