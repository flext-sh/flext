<!-- TOC START -->

- [§1 Identity](#1-identity)
- [§2 Architecture Law](#2-architecture-law)
- [§3 Code Law](#3-code-law)
- [§4 Import Law](#4-import-law)
- [§5 Make Contract](#5-make-contract)
- [§6 Quality Gates](#6-quality-gates)
- [§7 Skill System](#7-skill-system)
- [§8 Change Management](#8-change-management)
- [§9 Agent Instructions](#9-agent-instructions-mandatory-for-all-coding-agents)
- [§10 Multi-Agent Parallel Execution Law](#10-multi-agent-parallel-execution-law-mandatory)

<!-- TOC END -->

---
description:
alwaysApply: true
---

# AGENTS.md — Canonical Engineering Law

## §1 Identity

- FLEXT canonical governance file for all coding agents in this repository.
- Reviewed: 2026-02-22.
- Stack baseline: Python 3.13+, Pydantic v2, Ruff, Pyrefly, Poetry, Make.
- `AGENTS.md` defines mandatory law; skills hold detailed implementation guidance.
- Agent-specific configs are pointers only; no policy duplication outside this file.

## §2 Architecture Law

- Dependency flow is inward only: `L3 -> L2 -> L1 -> L0`; reverse imports are forbidden.
- Layer ownership: `L3` orchestration, `L2` domain/infrastructure, `L1` foundation/bridge, `L0` contracts.
- Bridge external infra through runtime/container boundaries, not direct framework imports.
- Public contracts must be consumed from package facades and root exports.
- Namespace aliases are canonical public API surfaces: `m`, `c`, `t`, `u`, `p`, `r`, `d`, `e`, `h`, `s`, `x`. Use simple runtime aliases only (e.g. `c = FlextConstants`, `m = FlextModels` in **init**).
- Cross-project composition MUST use inheritance via MRO across all components symmetrically (`Protocols`, `Models`, `Types`, `Utilities`, `Constants`). Subprojects define exactly ONE internal namespace class and transparently gain access to all parent namespaces via MRO.
- Integration projects (`tap|target|dbt`) MUST compose one platform and one domain via inheritance (e.g., `FlextMeltanoProtocols` + `FlextLdapProtocols`). The integration class name MUST NOT contain the "Meltano" prefix (e.g. `FlextTapLdapProtocols`).
- Domain boundaries are strict: `oracle-wms != db-oracle`, `ldap != ldif`.
- Each public facade module defines exactly one primary facade class plus one canonical alias.
- No backward-compat alias layers (`LegacyX = NewX`) and no namespace shadowing. You must never re-assign parent aliases.
- `__init__.py` files are exports-only: type hints, `__all__`, and native `__getattr__` module-level lazy load strategy.
- For architecture details and composition matrix -> see skill: `flext-architecture-layers`.
- For namespace inheritance and anti-patterns -> see skill: `flext-patterns`.
- For path-level architectural enforcement -> see skills: `rules-flext-core`, `rules-src`.
- Per-tier inheritance lookup table: see skill `flext-architecture-layers` for complete MRO matrix and composition rules by layer.
- L1 Platform Chains: Core→Cli→Meltano→Integration (orchestration), Core→Web→Api→Auth (API layer). Each chain defines clear ownership and composition boundaries.
- Clarification: "exactly ONE internal namespace class" refers to LOCAL namespace class per subproject, not single inheritance. Parent namespaces are accessed transparently via MRO.
- Integration naming: `Flext<Role><Domain><Facade>` pattern (NOT `FlextMeltano<Role>...`). Role is platform (Tap, Target, Dbt), Domain is connector (Ldap, Oracle, Wms), Facade is contract type (Protocols, Models, Types, etc.).

## §3 Code Law

- # MVI|- **AXIOMATIC SUPREME LAW (HIGHEST PRIORITY IN THIS FILE)**: **MVI 200-LINE CAP** is the most important rule of all and overrides implementation preferences. Any module, class, method, or function that grows beyond 200 lines is a violation unless split immediately into smaller cohesive units. Refactoring to remain within this cap MUST maximize **SOLID**, **DRY**, **YAGNI**, **SSOT**, strict **OO** composition, and canonical **MRO** architecture. The rule is mandatory across ALL `src/`, `tests/`, and `examples/` in ALL 33 projects. When line pressure appears, the required action is decomposition into explicit contracts and reusable domain components, never compression hacks. Every decomposition MUST follow FLEXT skills (load relevant `rules-*` first, then supporting skills) and preserve one-source-of-truth contracts and facade-based namespace inheritance.
- **AXIOMATIC** Fallible operations MUST return `r` (`r[T].ok(...)` / `r[T].fail(...)`). The `r` alias is MANDATORY at all usage sites. `r` exists to ELIMINATE `T | None` return types and manual `try/except` in the business layer. Functions that can fail MUST return `r[T]`, NOT `T | None`. Bare `try/except` in business logic is FORBIDDEN when `r` composition (`map`/`flat_map`/`lash`) can express the same flow. Ad-hoc dict envelopes for success/failure are FORBIDDEN. Only extremely rare, well-documented exceptions (e.g., `__init__` constructors, pure predicates) may deviate — and each deviation MUST be justified in a code comment.
- **NEW** `sys.exit` is forbidden outside `__main__.py` entrypoint boundaries.
- **NEW** Bare subprocess calls are forbidden; use standardized command runner abstractions.
- **NEW** `typing.TYPE_CHECKING` is ALLOWED for type-only imports (IDE support, annotations not needed at runtime) and `__init__.py` lazy loading. `TYPE_CHECKING` is FORBIDDEN with Pydantic models (BaseModel subclasses need runtime access) and as a band-aid for circular imports (fix architecture instead). See `flext-import-rules` Rule 8 for full details and examples.
- **NEW** Autogenerated package `__init__.py` files MUST preserve the lazy-export pattern (`TYPE_CHECKING` block + `_LAZY_IMPORTS` + `__getattr__`). Do not replace this pattern with eager cross-module imports in `src/` modules.
- **NEW** **Zero Tolerance for Hacks**: `model_rebuild()`, `eval()`, `exec()`, architectural `getattr()`, inline imports, lazy generic imports, and `try/except ImportError` blocks are TOTALLY FORBIDDEN without exception.
- **NEW** `print()` is forbidden in production paths; use structured logging with `FlextLogger`/structlog.
- `from __future__ import annotations` is mandatory in Python modules.
- Bare `except:` is forbidden; catch explicit exceptions and preserve typed failure boundaries.
- Direct `structlog.get_logger()` usage is forbidden where `FlextLogger` wrappers exist.
- Direct `dependency_injector` wiring in domain/orchestration code is forbidden; use runtime/container bridges.
- **AXIOMATIC** `Any`, bare `object`, and `dict[str, Any]` are TOTALLY FORBIDDEN in ALL type annotations, function signatures, return types, variable annotations, examples, and generated code across ALL 33 projects (`src/`, `tests/`, `examples/`). No exceptions. Use `t.*` contracts from `typings.py` exclusively (`t.Scalar`, `t.Container`, `t.ConfigMap`, `t.Dict`, `t.ServiceMap`, etc.). See skill `flext-strict-typing` Rule 1 for the complete replacement table.
- **AXIOMATIC** `| None` is ONLY permitted INLINE at usage sites when `None` carries distinct business/domain semantics (e.g., "not configured" vs "empty string"). Gratuitous `| None` with non-None defaults is forbidden. When default is `""`, type MUST be `str` not `str | None`. `| None` MUST NEVER be baked into type alias definitions in `typings.py` — type aliases are always non-nullable; consumers add `| None` inline at the usage site when business requires it (e.g., `field: t.Scalar | None = Field(default=None)`). See skill `flext-strict-typing` Rule 14.
- **AXIOMATIC** Type narrowing (`isinstance`, `TypeGuard`, `TypeIs`) is ONLY permitted when required by actual business logic — never introduced gratuitously to handle `None`/union types that should not exist in the first place. If you need type narrowing, first question whether the type union is necessary.
- **AXIOMATIC** Inline composed type annotations (e.g., `str | int | float | bool`, `dict[str, str | int | None]`, `list[str | int]`) are TOTALLY FORBIDDEN in ALL code across ALL 33 projects — `src/`, `tests/`, `examples/`. All composed types MUST be defined in `flext-core/typings.py` (or the project's MRO-inherited `FlextTypes`) and referenced via `t.*`. Only `flext-core/typings.py` may define raw unions; consumers reference canonical contracts such as `t.Scalar`, `t.Container`, `t.ConfigMap`, and model/protocol contracts. No inline union composition anywhere.
- **AXIOMATIC** Duplicating type definitions that already exist in `typings.py` (or inherited via MRO `FlextTypes`) is TOTALLY FORBIDDEN across ALL 33 projects. Every subproject MUST inherit its `FlextTypes` via MRO (`class FlextTapLdapTypes(FlextMeltanoTypes): ...`) and use the inherited `t.*` contracts. Re-declaring `ScalarValue`, `ConfigMap`, `ContainerValue`, `GeneralValueType`, `JsonValue`, `Serializable`, or any type alias that already exists in the MRO chain is forbidden — even in the subproject's own `typings.py` nested classes. One definition, one source of truth, always inherited via MRO.
- **AXIOMATIC** Compatibility aliases for types (`MyScalar = t.Scalar`, `ConfigDict = t.ConfigMap`, `AnyValue = t.Container`, or any `X = t.Y` renaming) are TOTALLY FORBIDDEN. Reference `t.*` directly at every usage site. No indirection layers, no local re-exports, no renaming aliases for types. Not even "convenience" aliases.
- **AXIOMATIC** These typing rules apply uniformly and without exception to ALL `src/`, `tests/`, and `examples/` directories across ALL 33 projects in the portfolio. No project, no directory, no file is exempt. Tests and examples MUST demonstrate the exact same strict typing discipline as production code. There is no "test-only" or "example-only" relaxation of any typing rule.
- **AXIOMATIC** `r` (`r`) is the SOLE mechanism for expressing fallibility. Any function that can fail, raise, or return "not found" MUST return `r[T]` — never `T | None`, never a bare exception, never an ad-hoc error dict. This rule applies to ALL `src/`, `tests/`, and `examples/` across ALL 33 projects. The `r` alias (`from flext_core import r`) is MANDATORY — never spell out `r` at usage sites. Composition operators (`map`, `flat_map`, `lash`, `value_or`) MUST replace imperative `if result is None` / `try/except` chains in business logic. The only permitted exceptions are pure predicates (`-> bool`), `__init__` constructors, and trivially infallible getters — each MUST be justified. Use `r[T].ok(...)` or `r[T].fail(...)` to construct results.
- **AXIOMATIC** Simple compatibility wrappers, non-business validation fallbacks, legacy code maintenance of ANY kind, and compatibility aliases are TOTALLY FORBIDDEN and ABOMINABLE. No `def legacy_method(): return new_method()` wrappers. No `try: new_way() except: old_way()` fallbacks. No keeping dead code "for compatibility". No `OldName = NewName` aliases. If code is legacy, it is DELETED and replaced with the canonical pattern. There is no grace period, no deprecation path, no "we'll remove it later". Legacy is exterminated on contact.
- **AXIOMATIC** Every module MUST organize its domain logic into a single nested class hierarchy using MRO inheritance. The most base class in the hierarchy MUST ultimately inherit from Pydantic v2 `BaseModel` (or a FLEXT base model like `FlextModels.ArbitraryTypesModel`, `FlextModels.FrozenModel`, etc.). Loose functions, standalone classes without MRO lineage, and modules without a nested class facade are FORBIDDEN. Every subproject module MUST inherit from the parent project's facade class (e.g., `class FlextTapLdapModels(FlextMeltanoModels): ...`) to cascade namespaces via MRO. This applies to ALL `src/`, `tests/`, and `examples/` across ALL 33 projects.
- **AXIOMATIC** ALL code MUST follow "Pydantic v2 way" EXTENSIVELY. Every class MUST extend Pydantic v2 `BaseModel` (or FLEXT base models) via MRO — USE, USE, USE Pydantic v2 features to their fullest; if you are not using a feature, REVIEW and USE it; if you genuinely do not need it, go back to a simpler base model and USE that one fully. `Field()` for ALL field declarations with `description`, `title`, `examples`, `json_schema_extra` documenting business rules — fields are self-documenting contracts, not bare attributes. `SecretStr`/`SecretBytes` for ALL sensitive values. `model_config = ConfigDict(...)` for ALL model configuration — standalone `*Config` classes are TOTALLY FORBIDDEN; use `BaseSettings` or `ConfigDict` instead. Custom `@field_validator`/`@model_validator` MUST be minimized — prefer Pydantic v2 built-in constraints (`Field(ge=0, le=100)`, `Annotated[str, StringConstraints()]`, `Literal`, `constr`, `conint`, pattern constraints) before writing custom validators. Initialization helpers (`def setup()`, `def initialize()`), unnecessary `@property`, simple getters/setters, line-reduction wrappers, and pass-through methods inside model classes are TOTALLY FORBIDDEN — if Pydantic v2 has a built-in mechanism (`@computed_field`, `model_post_init`, `__init_subclass__`, `PrivateAttr`), USE IT.
`Enum`, `Mapping`, and `Literal` values MUST come from `constants.py` (`c.*`), configuration from `settings.py` (`s.*`) — never defined inline. JSON operations MUST use `model_dump_json()`, `model_validate_json()`, `model_dump()`, `TypeAdapter` — never raw `json.loads()`/`json.dumps()`. Internal/private state MUST use `PrivateAttr` (`Field` with `init=False` or Pydantic `PrivateAttr()`) — never bare `self._x = ...` assignments. Nested facade classes in modules MAY contain business logic methods beyond validation, but ALL their internal properties MUST still use `Field()` and `PrivateAttr`. `models.py` / `_models/` directories are for model definitions ONLY — remove business logic, utility functions, and orchestration code that does not belong to the model contract. This applies to ALL `src/`, `tests/`, and `examples/` across ALL 33 projects.
- **AXIOMATIC** Tests MUST demonstrate the EXACT SAME strict typing, Pydantic v2, r, and architectural discipline as production code. Test files are NOT exempt from ANY rule. Test fixtures MUST use `Field()`, typed models, and `r[T]` returns. Test data MUST use `t.*` types. Test assertions on r MUST use `.is_success`/`.is_failure` and `.value`/`.error` — never raw unwrapping. There is NO "test-only" relaxation of any rule. Tests that violate these rules are themselves violations.
- **AXIOMATIC** Every change MUST be INTEGRAL. Code is ONLY accepted after passing ALL 4 linters clean: ruff, mypy, pyright, and pyrefly — with ZERO errors, ZERO warnings. No partial fixes. No "I'll fix it later". No bypassing linter rules. ALL impacted references across the ENTIRE codeset MUST be immediately updated using ast-grep (`sg`) search-and-replace to maintain global consistency. After any type, model, or signature change, the agent MUST: (1) run `sg` to find and replace ALL references across all 33 projects, (2) run `make check` on every affected project, (3) verify ZERO errors from all 4 linters. A change that breaks ANY linter in ANY project is REJECTED. There is no "works in this project" defense — the portfolio is ONE unit.
# HS|- **AXIOMATIC** Linter suppression comments (`# type: ignore`, `# noqa`, `# pyright: ignore`, `# pyrefly: ignore`, `# mypy: ignore`, `typing.cast()`) are FORBIDDEN without ALL of the following: (1) a well-founded technical explanation citing REAL, verifiable internet sources (official docs, GitHub issues, PEPs) proving the suppression is unavoidable, (2) an explicit business necessity documented in the same comment, (3) the suppression MUST be per-line ONLY — never per-file, never per-module, never in configuration. Global suppression rules in `pyproject.toml`, `ruff.toml`, or any config file are TOTALLY FORBIDDEN. Each suppression MUST be individually justified. If a linter flags an error, the CORRECT response is to fix the code — never to silence the linter. Agents that add suppression comments without meeting ALL three criteria are in violation.
# VX|- **AXIOMATIC** Git history is IMMUTABLE and SACRED. `git checkout <file>`, `git reset`, `git revert`, `git stash pop/apply`, and any other operation that DISCARDS, OVERWRITES, or ROLLS BACK committed or staged work by any agent is TOTALLY FORBIDDEN. This applies to ALL agents, ALL sessions, ALL automation, and ALL orchestrators — without exception. Every change made by any agent MUST be accepted, improved, standardized, and fixed forward. If a previous agent's change is wrong, the ONLY permitted response is a NEW forward commit that corrects it. Stash operations (`git stash`, `git stash pop`) that discard another agent's work are FORBIDDEN. `git checkout --theirs` is ONLY permitted during a rebase conflict on a file you do NOT own — and ONLY to accept the other agent's version (never to discard it). The correct response to broken code is ALWAYS: read it, understand it, fix it forward, commit the fix. There is no rollback. There is no undo. There is only forward.
# KA|- **AXIOMATIC** Code search and structural replacement MUST use `ast-grep` (MCP tool `mcp_ast_grep_search` / `mcp_ast_grep_replace`, or CLI `sg`) as the SOLE mechanism for finding and rewriting code patterns across the codebase. When the MCP tool is available, it MUST be used first. When unavailable, the CLI `sg` command is the mandatory fallback. `grep`/`ripgrep` are ONLY permitted for plain-text content search (log lines, comments, string literals) — NEVER for locating code structure, symbols, imports, or type annotations. `find` is TOTALLY FORBIDDEN for locating code or information — use `glob` patterns or `ast-grep` instead. Custom Python/shell scripts written ad-hoc to fix, rewrite, or transform code are TOTALLY FORBIDDEN — every structural code change MUST go through `ast-grep` patterns or direct file edits via the Edit tool. `sed`, `awk`, and inline shell pipelines for code transformation are TOTALLY FORBIDDEN. The correct workflow is: (1) use `mcp_ast_grep_search` to locate all pattern instances, (2) use `mcp_ast_grep_replace` (or `sg --rewrite`) to apply the transformation atomically across all files, (3) verify with `make check`. Writing a one-off script to "fix" code is an EXTREME FAULT — it bypasses AST awareness, produces brittle text-level rewrites, and cannot be reviewed or audited.
# SN|- **AXIOMATIC** Before ANY code change, the agent MUST perform a complete context evaluation: (1) read and fully understand ALL existing code in the affected module — its patterns, its MRO chain, its dependencies, its base classes, and its existing contracts; (2) maximize reuse of existing library code, base classes, utilities, and type contracts already present in the codebase — never reinvent, duplicate, or shadow what already exists; (3) apply changes uniformly and completely across ALL namespaces — `src/`, `tests/`, AND `examples/` — every namespace is in scope, no namespace is exempt, no namespace is an afterthought; (4) produce the most correct, complete, lint-free implementation possible — using advanced code patterns, strong typing, full Pydantic v2 discipline, and the full power of the existing architecture. Simplifications, bypasses, mocks, fallbacks, stubs, TODOs, hardcoded values, and placeholder logic are TOTALLY FORBIDDEN in any committed code. A change that is "good enough for now" is a violation. Every change is final, complete, and production-grade from the first commit. Agents that skip context evaluation, ignore existing patterns, or produce partial implementations are in violation of this law.
- **AXIOMATIC — typings.py IMMUTABLE ALIAS TABLE (NAMED, LOCKED, NO AGENT MAY CHANGE WITHOUT EXPLICIT OPERATOR APPROVAL)**: `type X = ...` (PEP 695 TypeAliasType) creates annotation-only objects — TOTALLY FORBIDDEN as `isinstance()` args, base classes, or in any runtime type-checking context. `X: TypeAlias = ...` (typing.TypeAlias) creates a real UnionType — runtime-safe for `isinstance()`. The two syntaxes are NOT interchangeable. Changing `X: TypeAlias = ...` to `type X = ...` for a non-recursive alias is an EXTREME FAULT that crashes the entire runtime. NAMED ALIAS TABLE (authoritative — DO NOT CHANGE SYNTAX WITHOUT OPERATOR APPROVAL): NON-RECURSIVE → MUST use `X: TypeAlias = ...` (runtime-safe): `Primitives`, `Scalar`, `Container`, `ConfigurationMapping`, `MetadataValue`, `RegisterableService`, `JsonDict`, `FactoryCallable`, `ResourceCallable`, `HandlerCallable`, `HandlerLike`, `RegistrablePlugin`, `ConstantValue`, `FileContent`, `SortableObjectType`, `ConversionMode`, `TypeHintSpecifier`, `GenericTypeArgument`, `MessageTypeSpecifier`, `IncEx`, `TYPE_CHECKING`. RECURSIVE → MUST use `type X = ...` (self-referential, annotation-only, NEVER with isinstance): `GeneralValueType`, `Serializable`, `JsonValue`, `ContainerValue`. These recursive aliases are definition-only and transitional; business/application code MUST prefer Pydantic v2 models + protocols and MUST NOT propagate these aliases through service boundaries. `Validation.*` inner aliases use `type X = Annotated[...]` — annotation-only, never with isinstance, correct as-is.
MANDATORY VERIFICATION GATE — any agent touching typings.py MUST run this before AND after every edit and confirm all lines print PASS: `python3 -c "import importlib,sys; [sys.modules.pop(k) for k in list(sys.modules) if 'flext' in k]; import flext_core; t=flext_core.t; [print('PASS',n) if isinstance('x',getattr(t,n)) else print('FAIL',n) for n in ['Primitives','Scalar','Container','MetadataValue','RegisterableService']]"`. Runtime narrowing MUST go through `u.Guards.is_*()` TypeGuard functions in `guards.py` — NEVER raw `isinstance(value, t.SomeAlias)` at call sites outside `guards.py`. Subclassing a `t.*` alias is FORBIDDEN — use concrete base: `class Foo(Mapping[str, t.Container])` not `class Foo(object)`.
# RV|- **AXIOMATIC** Agents MUST execute ONLY what the assigned task specifies — nothing more, nothing less. Discovering a related issue, smell, or improvement opportunity during task execution does NOT grant permission to fix it. Out-of-scope changes (renaming methods, removing aliases, restructuring protocols, merging methods, changing API surface) committed during a task are TOTALLY FORBIDDEN and constitute an EXTREME FAULT. The ONLY permitted response to a discovered issue is: (1) complete the assigned task exactly as specified, (2) file a new beads issue describing the discovered problem, (3) stop. Agents that expand scope, "clean up while here", or make "obvious improvements" beyond the task boundary are in violation. Every task has a boundary. Stay inside it.
- Use modern Python typing syntax (`X | Y`, built-in generics, `collections.abc` contracts).
- Use Pydantic v2 patterns (`ConfigDict`, `Field`, validators) for model state and validation.
- Root-cause fixes only: no bypasses, no hidden suppressions, no fake-green reports.
- Never claim checks passed without executable evidence.
- For typing law and `r` details -> see skill: `flext-strict-typing`.
- **Type narrowing**: use `isinstance` or `TypeGuard` only; `type(x) is T` for narrowing is forbidden. `cast()` is completely forbidden outside of `flext-core` result internals.
- **CRITICAL: TypeAliasType isinstance trap (Python 3.12+)**: PEP 695 `type X = str | int` creates `TypeAliasType` — `isinstance(val, X)` FAILS at runtime. Non-recursive aliases MUST use `X: TypeAlias = str | int` (creates `UnionType`, isinstance-safe). Recursive aliases MUST use `type` statement but NEVER with `isinstance()` — use `TypeGuard` functions from `guards.py` instead. See `flext-core/AGENTS.md` for complete rules and guards reference.
- **Polymorphic code**: dismantle into centralized Pydantic v2 models (single contract, validation in model).
- For result/logging/DI coding patterns -> see skill: `flext-patterns`.
- `from __future__ import annotations` verification: MUST be present as first import in every Python module (after docstring/license). Verify with: `grep -n 'from __future__ import annotations' <file>`.
- `model_rebuild()` is FORBIDDEN (explicit prohibition). Use Pydantic v2 patterns instead; if you think you need it, fix the model definition or import order instead.
- `_LAZY_IMPORTS` string references MUST match actual class names exactly. Mismatch between string and runtime class causes silent failures.
- Import parent by CLASS NAME for inheritance, never by alias. Example: `from flext_core.protocols import FlextProtocols` (correct), NOT `from flext_core import p` then inherit from `p.FlextProtocols` (wrong).

## §4 Import Law

- Canonical alias imports are mandatory at usage sites: `r,t,c,m,p,u,d,e,h,s,x`. You only ever import the local facade explicitly; parent facades are inherited seamlessly.
- Keep import order: future, stdlib, third-party, first-party, local.
- Within `flext-core`, import concrete submodules (`flext_core.<module>`) not package root.
- From subprojects, consume public API/facade exports; never import private `_` internals.
- Wildcard imports and relative imports are forbidden in governed code.
- No double-assignment of facade aliases (`c/m/p/t/u` assigned once at module bottom).
- Cross-tier imports violating architecture direction are forbidden.
- For full import matrix, exceptions, and enforcement checks -> see skill: `flext-import-rules`.

## §5 Make Contract

- Automation entrypoint is `make`; scripts are implementation details, not primary UX.
- Workspace verbs: `setup check security format docs test validate typings clean`.
- Project verbs (`base.mk`): `setup check security format docs test validate clean`.
- Standard selectors: `PROJECT`, `PROJECTS`, `CHECK_GATES`, `VALIDATE_GATES`, `PYTEST_ARGS`, `FIX`, `JOBS`, `FAIL_FAST`.
- Workspace-only scope controls: `VALIDATE_SCOPE=project|workspace`, optional `DEPS_REPORT=0`.
- Strictness is mandatory: no `SKIP_*` bypass toggles in the contract.
- Exit code contract: `0` pass, `1` policy failure, `2` usage/config error, `3` infra/runtime error.
- Policy/automation/governance edits must run `make validate VALIDATE_SCOPE=workspace` before completion claims.
- Reports must be factual, machine-readable when produced, and include executable next actions for failures.
- For complete verb semantics and thresholds -> see skill: `flext-quality-gates`.

## §6 Quality Gates

- Workspace `.venv` is mandatory when present; system Python/pip usage is forbidden.
- Project-local `.venv` is fallback-only for project-scoped runs when workspace `.venv` is missing.
- Preflight before workspace loops: ensure root `.venv` exists and remove project `.venv` drift.
- In fallback mode, run project `make setup` before check/validate/test loops.
- `make setup` and `make upgrade` must modernize/format `pyproject.toml` before lock/install.
- `pyproject.toml` must follow Poetry 2.x + PEP 621/639 constraints.
- Coverage source of truth is `[tool.coverage.report] fail_under` in each project `pyproject.toml`.
- Forbidden threshold drift: no Makefile threshold constants and no `--cov-fail-under` flags in pytest addopts.
- No silent failure patterns (`2>/dev/null`, `|| true`) on mandatory gates.
- For gate details and verification matrix -> see skill: `flext-quality-gates`.

## §7 Skill System

- Skills are authoritative detail documents; this file is the law surface.
- Load order is mandatory: touched-path `rules-*` skill first, supporting skills second.
- Do not implement from memory when a relevant skill exists.
- Do not claim skill usage without reading the corresponding `SKILL.md`.
- `rules.yml` schema uses flat fix keys only (`fix_auto`, `fix_type`, `fix_file`, `fix_script`, `fix_instruction`, `fix_description`).
- Prefer `type: ast-grep`; use `type: custom` only when AST matching is not viable.
- `fix_auto: true` must point to an executable, real fix mechanism.
- Mandatory mapping baseline: `flext-core->rules-flext-core`, `src->rules-src`, `docs->rules-docs`, `scripts->rules-scripts`, `typings->rules-typings`, `.github->rules-github`, `docker->rules-docker`, `pkg->rules-pkg`, `cmd->rules-cmd`, `examples->rules-examples`.
- After rules skill, load only minimal supporting skills needed for the change.
- For skill format and pointer governance -> see skills: `skill-format-universal`, `flext-docs-pointer-policy`.

## §8 Change Management

- Policy changes land in `AGENTS.md` first, then propagate to skill documents.
- Never ship incomplete work as complete; each claim requires command evidence.
- Keep changes minimal, explicit, root-cause oriented, and verifiable.
- Never alter lint/gate semantics without explicit in-session user approval.
- If governance corrections arise during work, update this file immediately before further implementation.
- **CRITICAL** Deferring, skipping, or exempting any known violation is forbidden without explicit operator authorization in-session. Hiding scope exclusions inside plans or guardrails without operator approval is an extreme fault. When a violation cannot be fixed immediately, the agent must present the violation, explain why, and obtain explicit written approval before marking it deferred.
# WF|- **AXIOMATIC Commit-After-Validation**: Every passing validation (linters, tests, `make check`, any quality gate) MUST be immediately followed by committing ALL pending changes across ALL touched projects and pushing to remote. No delay. No batching for later. No asking permission. Sequence: validation passes → `git add -A` (all projects) → `git commit` → `git pull --rebase` → `git push` → confirm clean `git status`. Uncommitted work after a passing validation is a VIOLATION. Unpushed work is LOST WORK — it does not exist.

## §9 Agent Instructions (Mandatory for All Coding Agents)

- **Runtime aliases (subprojects)**  
  In subprojects, all runtime access MUST use the project namespace only. Use the canonical runtime alias `x` (FlextMixins) for runtime helpers: `x.create_instance`, `x.is_dict_like`, `x.is_list_like`, `x.is_valid_json`, `x.is_valid_identifier`, `x.is_base_model`, `x.normalize_to_general_value`, `x.normalize_to_metadata_value`, `x.is_sequence_type`, `x.safe_get_attribute`, `x.extract_generic_args`, `x.ok`, `x.fail`. Do NOT subdivide namespaces (e.g. avoid `FlextRuntime.Bootstrap.*` or ad-hoc wrappers). Subprojects MUST NOT introduce extra alias layers; use `c`, `m`, `t`, `u`, `p`, `r`, `d`, `e`, `h`, `s`, `x` from the project/facade exports only.

- **No loose aliases or pass-through methods**  
  Remove compatibility aliases (e.g. `LegacyX = NewX`, `.data` for `.value`, `.and_then` for `.flat_map`). Use direct methods and single canonical names. No free-function wrappers that only call a class method; call the class/method directly.

- **Type narrowing (strict)**  
  Use correct typing for type narrowing. Do NOT use `type(x) is T` or `type(x) == T` for narrowing; use `isinstance(x, T)` or `TypeGuard` so the type checker can narrow. Replacing `isinstance` with `type()` is forbidden. Prefer Pydantic `model_validate` / `model_validate_json` for input validation and structured data.

- **Polymorphic code → centralized Pydantic models**  
  Dismantle polymorphic functions and methods: replace multiple branches on type/union with a single contract. Use centralized Pydantic v2 models with validation (discriminated unions, `Field`, `model_validator`, `field_validator`) so that one model (or a small set of models) defines the shape and validation; avoid ad-hoc `if isinstance(...)` chains over many types. Prefer overloads or discriminated unions over loose `Union` handling in function bodies.

- **Scale and parallelism**  
  When refactoring many call sites or modules, use multiple agents or batch passes in parallel (e.g. by package or by rule) to apply these rules consistently and quickly. Each change must remain minimal and verifiable.

- **Skill (mandatory)**  
  For detailed enforcement: see skill **flext-agent-strict-rules** (runtime aliases only, no type() for narrowing, no loose methods, polymorphic code → centralized Pydantic v2 models).
- **Evidence requirements**  
  Every verification claim ("tests pass", "linters clean", "grep found X") MUST include command output proof with command, exit code, and UTC timestamp. Store evidence in `.sisyphus/evidence/` and require machine-readable content (or plain text with explicit command + exit code) so audit can replay the claim.
- **Cross-session deduplication**  
  Check recent commits for already-completed work before starting. Use: `git log --oneline --all --grep='<task-keyword>'` to find prior work. If found, verify completion and skip.
- **.new/swap protocol**  
  For large file modifications (>50 lines changed), create `.new` file first, verify all changes, then swap: `mv file.py file.py.old && mv file.py.new file.py`. Commit both the new file and the swap in one commit.
- **Verify-before-implement**  
  Before starting ANY task, check recent commits: `git log --oneline -20`, `git show HEAD`, and active plans/issues (`.sisyphus/plans/`, beads in-progress). If overlap exists, continue the existing lane instead of duplicating work.
- **Scope discipline**  
  Agent MUST NOT modify files outside task boundary. If a task requires changes to a file owned by another agent, STOP and escalate. READ-ONLY access is allowed; WRITE access is forbidden.

## §10 Multi-Agent Parallel Execution Law (Mandatory)

### §10.1 User's 11 Commandments (The Execution Ritual)

These are UNBREAKABLE LAW for all parallel agent work:

1. **Organize libs first** — Domain monopoly: each module owns its domain exclusively
2. **Minimal skeleton** — Start with interfaces/protocols, optimize structure before implementation
3. **Reconnect one-by-one** — Fix ONE integration at a time, verify before next
4. **Tests last per module** — Update tests AFTER implementation passes static checks
5. **4 linters zero tolerance** — ruff, mypy, pyright, pyrefly MUST all pass, no `# type: ignore`
6. **Stay in lane** — Only touch files in your ownership, READ-ONLY for others
7. **Never rollback** — Fix forward only, no `git revert`, no deprecation shims
8. **Commit frequently** — Every task completion = separate commit + push
9. **.new/.old owned-only** — Use .new/.old pattern ONLY for files you own exclusively
10. **No automation scripts** — Manual changes only, no shell scripts for mass edits
11. **Never rush/ULW** — No ultrawork mode, no batching, perfection over speed

### §10.2 File Ownership Table (flext-core)

Use EXACTLY this ownership matrix:

| File | Owner | Others Allowed |
|------|-------|----------------|
| `dispatcher.py` | Agent 1 | READ only |
| `constants.py` | Agent 1 | READ only |
| `_models/cqrs.py` | Agent 1 | READ only |
| `registry.py` | Agent 2 | READ only |
| `typings.py` | Agent 2 | READ only |
| `service.py` | Agent 3 | READ only |
| `_models/base.py` | Agent 3 | READ only |
| `result.py` | Agent 4 | READ only |
| `exceptions.py` | Agent 4 | READ only (exception: Agent 4 may modify exceptions.py in ANY consumer project for e.BaseError hierarchy) |
| `runtime.py` | Agent 4 | Agent 5 READ only (MRO chain reference) |
| `loggings.py` | Agent 4 | READ only |
| `container.py` | Agent 5 (primary) | Agent 1: dispatcher singleton ADD only; Agent 4: return types only |
| `decorators.py` | Agent 5 | READ only |
| `handlers.py` | Agent 5 | READ only |
| `mixins.py` | Agent 5 | READ only |
| `protocols.py` | SECTION-OWNED (see matrix below) | Each agent: own section ONLY, append at END, NEVER reorder, NEVER auto-format globally |
| `__init__.py` | ❄️ FROZEN | Each agent appends own new exports only |
| `context.py`, `settings.py`, `models.py`, `utilities.py`, `_utilities/*`, `__version__.py` | ❄️ FROZEN | No agent modifies |

**AXIOMATIC Exception**: FROZEN files are unfrozen for annotation-only changes required by AXIOMATIC rules (§3 Code Law). Type annotations, Field() metadata, PrivateAttr declarations, and import additions are permitted. Behavioral changes (logic, algorithms, control flow) remain FROZEN.

**protocols.py Section Ownership Matrix**:

| Section | A1 (Dispatcher) | A2 (Registry) | A3 (Service) | A4 (Result/Exceptions) | A5 (CDH/Mixins) |
|---------|-----------------|---------------|--------------|------------------------|-----------------|
| L1-236 (infra) | ❄️ | ❄️ | ❄️ | ❄️ | ❄️ |
| Context, RuntimeBootstrapOptions, DI | — | — | — | — | ✅ |
| Result, ResultLike | — | — | — | ✅ | — |
| Model, Config, Service, Validation | — | — | ✅ | — | — |
| CommandBus, Middleware, Processor | ✅ | — | — | — | — |
| Handler | — | — | — | — | ✅ |
| Registry | — | ✅ | — | — | — |
| VariadicCallable, ResourceFactory | — | — | — | ✅ | — |
| RegisterableService, ServiceFactory | — | — | — | — | ✅ |
| Log, StructlogLogger, Metadata | — | — | — | ✅ | — |
| ValidatorSpec | — | — | ✅ | — | — |
| L1289+ (metaclass infra) | ❄️ | ❄️ | ❄️ | ❄️ | ❄️ |
| ALL other sections | ❄️ | ❄️ | ❄️ | ❄️ | ❄️ |

### §10.3 Execution Phases (Dependency-Ordered)

Agents MUST execute in this order:

- **Phase 0 (SOLO)**: Agent 4 completes Wave 0 (RuntimeResult.**slots** + r.fail() + p.Result) and PUSHES. ALL other agents BLOCKED until Phase 0 complete.
- **Phase 1**: Agent 4 continues (exception propagation, safe(), chaining) + Agent 5 starts (containers/decorators/handlers/mixins). Agent 5 must `git pull --rebase` before starting.
- **Phase 2**: Agent 1 (Dispatcher) + Agent 3 (Service) start. Both must `git pull --rebase` before starting.
- **Phase 3**: Agent 2 (Registry) starts. Must `git pull --rebase` before starting.
- **Phase 4 (Consumer Projects)**: All agents work on their assigned consumer projects IN PARALLEL.

**Consumer Project Partition (31 projects, zero overlap)**:

| Agent | Projects | Count |
|-------|----------|-------|
| Agent 1 | `algar-oud-mig`, `flexcore`, `flext-api` | 3 |
| Agent 2 | `flext-auth`, `flext-cli`, `flext-db-oracle` | 3 |
| Agent 3 | `flext-grpc`, `flext-ldap`, `flext-ldif`, `flext-meltano` | 4 |
| Agent 4 | `flext-observability`, `flext-oracle-oic`, `flext-oracle-wms`, `flext-plugin`, `flext-quality`, `flext-tap-oracle-wms`, `flext-target-ldif` | 7 |
| Agent 5 | `flext-tap-ldap`, `flext-tap-ldif`, `flext-tap-oracle`, `flext-tap-oracle-oic`, `flext-target-ldap`, `flext-target-oracle`, `flext-target-oracle-oic`, `flext-target-oracle-wms`, `flext-web`, `flext-dbt-ldap`, `flext-dbt-ldif`, `flext-dbt-oracle`, `flext-dbt-oracle-wms`, `gruponos-meltano-native` | 14 |

### §10.4 Lint Scoping

- **During parallel work**: Each agent runs linters (ruff, mypy, pyright, pyrefly) ONLY on files they modified
- **At phase boundaries**: Agent completing a phase runs FULL project lint (`cd flext-core && make check`) before pushing
- **Before Phase 4**: ALL agents run full flext-core lint and verify ZERO errors before touching consumer projects
- **Zero tolerance**: NO `# type: ignore`, NO warnings, NO errors. Fix until clean.

### §10.5 Git Discipline

- **Always rebase**: `git pull --rebase` before EVERY push. NEVER `git pull` without `--rebase`.
- **Never force push**: NEVER `git push --force` to main/master.
# XT|- **Never rollback**: NO `git revert`, NO `git reset`, NO `git checkout <file>` to discard work, NO `git stash pop` to overwrite committed changes. Fix forward ONLY. If you break something, push a fix commit. Every change by every agent is accepted, improved, and fixed forward — never discarded.
- **Conflict resolution**: If conflict in YOUR file → resolve manually. If conflict in ANOTHER agent's file → `git checkout --theirs <file>` (accept their version, work around it).
# YH|- **Commit frequency**: Every task completion = separate commit. Small commits, frequent pushes.
# PF|- **AXIOMATIC Commit-After-Validation**: Immediately after ANY validation passes (linters, tests, `make check`, or any quality gate), the agent MUST commit ALL pending changes across ALL touched projects and push — without delay, without waiting for the next task, without asking permission. The sequence is MANDATORY and NON-NEGOTIABLE: (1) validation passes → (2) `git add -A` in every project with pending changes → (3) `git commit -m "<conventional message>"` → (4) `git pull --rebase` → (5) `git push` → (6) verify `git status` shows clean. This applies to ALL agents, ALL sessions, ALL projects simultaneously. Pending uncommitted work after a passing validation is a VIOLATION. Work that exists only locally and has not been pushed is LOST WORK — it does not exist. There is no "I'll commit later". There is no "commit at the end". Every stable state MUST be immediately persisted to remote.

### §10.6 Plan and Session Hygiene

- **Plan hygiene**: Consolidate overlapping plans before creating new ones. Check `.sisyphus/plans/` for existing plans covering the same scope. Merge tasks into existing plan rather than creating duplicates.
- **Cross-session deduplication protocol**: Before spawning new agents, verify no other agent is working on the same task. Use `git log --oneline -20` and check `.sisyphus/plans/` for active work. If found, coordinate or defer.
