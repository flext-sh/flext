<!-- TOC START -->

- [§1 Identity](#1-identity)
- [§2 Architecture Law](#2-architecture-law)
  - [2.1 Dependency Flow & Layers](#21-dependency-flow--layers)
  - [2.2 Facades & Namespaces](#22-facades--namespaces)
  - [2.3 Inheritance & Composition](#23-inheritance--composition)
  - [2.4 Governance Anti-Patterns](#24-governance-anti-patterns)
- [§3 Code Law](#3-code-law)
  - [3.1 Architecture & Code Structure](#31-architecture--code-structure)
  - [3.2 Types & Contracts](#32-types--contracts)
  - [3.3 Failures & Error Handling](#33-failures--error-handling)
  - [3.4 Tools, Modules & Environment](#34-tools-modules--environment)
  - [3.5 Integrity & Change Management](#35-integrity--change-management)
  - [3.6 Test Standardization](#36-test-standardization)
  - [3.7 Associated Skills](#37-associated-skills)
- [§4 Import Law](#4-import-law)
- [§5 Make Contract](#5-make-contract)
- [§6 Quality Gates](#6-quality-gates)
- [§7 Skill System](#7-skill-system)
- [§8 Change Management](#8-change-management)
- [§9 Agent Execution Pre-requisites](#9-agent-execution-pre-requisites)
  - [9.1 Coding Directives for Agents](#91-coding-directives-for-agents)
- [§10 Multi-Agent Parallel Execution Law](#10-multi-agent-parallel-execution-law)
  - [10.1 The 11 Commandments (Execution Ritual)](#101-the-11-commandments-execution-ritual)
  - [10.2 Core File Ownership (`flext-core`)](#102-core-file-ownership-flext-core)
  - [10.3 Execution Phases](#103-execution-phases)
  - [10.4 Lint Scoping & Quality](#104-lint-scoping--quality)
  - [10.5 Git & Session Hygiene](#105-git--session-hygiene)

<!-- TOC END -->

---
description:
alwaysApply: true
---

# AGENTS.md — Canonical Engineering Law

## §1 Identity

- **Supreme Document**: FLEXT canonical governance file for ALL coding agents in this repository. AGENTS.md defines mandatory law; skills hold detailed implementation guidance.
- **Reviewed**: 2026-02-22.
- **Stack Baseline**: Python 3.13+, Pydantic v2, Ruff, Pyrefly, Poetry, Make.
- **No Shadow Policies**: Agent-specific configs are pointers only. No policy duplication exists outside this file.

## §2 Architecture Law

### 2.1 Dependency Flow & Layers
- **Inward Flow**: Dependency flow is inward only (`L3 -> L2 -> L1 -> L0`). Reverse imports are FORBIDDEN.
- **Layer Breakdown**: `L3` = Orchestration, `L2` = Domain/Infrastructure, `L1` = Foundation/Bridge, `L0` = Contracts.
- **Infrastructure Bridging**: Bridge external infra through runtime/container boundaries, NEVER via direct framework imports.
- **Platform Chains**: `Core -> Cli -> Meltano -> Integration` (orchestration), `Core -> Web -> Api -> Auth` (API layer).

### 2.2 Facades, Namespaces & Naming Patterns
- **One Facade Rule**: Each public facade module defines exactly ONE primary facade class plus ONE canonical alias.
- **Canonical API & Aliases**: Namespace aliases are the STRICT canonical public API surfaces. You must always use them (`m.MyModel`, `c.MY_CONST`), never the direct classes.
  - `m` = Models (`Flext*Models`)
  - `c` = Constants (`Flext*Constants`)
  - `t` = Types (`Flext*Types`)
  - `u` = Utilities (`Flext*Utilities`)
  - `p` = Protocols (`Flext*Protocols`)
  - `h` = Helpers (`Flext*Helpers` - mostly test/infra)
  - `s` = Services (`Flext*Services`)
- **Strict Boundaries**: Domain boundaries are strict (e.g. `oracle-wms != db-oracle`, `ldap != ldif`).
- **Export Discipline**: `__init__.py` files are exports-only. They must ONLY contain type hints, `__all__`, and the native `__getattr__` module-level lazy load strategy. **These files are AUTO-GENERATED**. You must NEVER edit them manually. Run `make codegen` to regenerate lazy initialization exports.

### 2.3 MRO Inheritance & Namespace Composition
- **Single Namespaced Classes (Production & Tests)**: For both production and test infrastructure, you must create exactly ONE local namespaced class per tier (models, constants, helpers, etc.). All domain logic, constants, and methods MUST reside inside this single class.
- **The MRO Cascade & Exhaustive Composition**: Cross-project composition MUST use inheritance via MRO symmetrically across all components. Furthermore, within a project, a top-level facade class MUST strictly compose ALL of its domain-specific subclasses.
  *(Example: `class FlextCoreModels(FlextCoreBaseModels, FlextCoreCQRSModels, FlextCoreSettingsModels): pass` and similarly for `FlextCoreUtilities` composing all `_utilities` subclasses. Loose disconnected subclasses are FORBIDDEN).*
- **Internal Namespaces & Elimination of Loose Objects**: Do not duplicate parent variables. Loose module-level objects or functions outside this class are STRICTLY FORBIDDEN. They must be absorbed into the namespace class as attributes/methods or consumed directly from base classes.
- **Integration Projects** (`tap|target|dbt`): Composed of one platform and one domain via inheritance (e.g., `class FlextTapLdapProtocols(FlextMeltanoProtocols, FlextLdapProtocols): pass`).
- **Naming & Location Patterns**: Classes must be placed in specific locations (e.g., `models.py` or `_models/`) and follow the `Flext<Role><Domain><Facade>` pattern (e.g. `FlextCoreModels`, `FlextTestInfraHelpers`, `FlextTapLdapProtocols`). Test classes must also match the domain they are testing. The integration class name MUST NOT contain the "Meltano" prefix.
- **Test Hierarchy Strictness**: In tests, the MRO hierarchy operates in two axes: test tools + domain under test. The test class MUST compose `FlextTests<Tier>` with the project's own `Flext<Project><Tier>` to gain both testing utilities and the full application context transparently.

### 2.4 Governance Anti-Patterns
- **No Private Imports**: Public contracts MUST be consumed from package facades and root exports only.
- **No Backward-Compat Aliases**: Backward-compatibility alias layers (e.g. `LegacyX = NewX`) and namespace shadowing are FORBIDDEN. You must NEVER re-assign parent aliases.

*For full MRO matrix, architecture layers, and anti-patterns logic, consult skills:* `flext-architecture-layers`, `flext-patterns`, `rules-flext-core`, `rules-src`.

## §3 Code Law

### 3.1 Architecture & Code Structure
- **MVI 200-LINE CAP (SUPREME LAW)** module, class, method, or function >200 lines is a violation. Refactor immediately using strict OO composition and canonical MRO architecture. Decompose into explicit contracts and reusable domain components—never use compression hacks.
- **Pydantic v2 Mastery**: Every class MUST extend Pydantic v2 `BaseModel` (or FLEXT base models) via MRO. Fully utilize `Field()`, `model_config = ConfigDict(...)`, `PrivateAttr()`, and built-in constraints. Standalone `*Config` classes, unnecessary `@property`, manual `self._x` assignments, and line-reduction wrappers are FORBIDDEN.
- **MRO Inheritance Hierarchy**: Domain logic must reside in a single nested class hierarchy. Subprojects inherit from the parent project's facade class to cascade namespaces. Loose functions or standalone classes without MRO lineage are FORBIDDEN. They MUST be absorbed into the namespace classes or used via existing base classes.
- **Utility & Helper Generalization (`u.*`)**: All shared helpers MUST strictly flow through the `u.*` utilities namespace. Do not duplicate logic. Use and enhance the lowest-level function available, systematically generalizing existing code rather than creating new redundant functions.
- **Centralize Polymorphic Code**: Dismantle polymorphic functions branching on type unions. Use centralized Pydantic v2 models with discriminated unions and validation.

### 3.2 Types & Contracts
- **Strict Contracts Only**: `Any`, bare `object`, and `dict[str, Any]` are TOTALLY FORBIDDEN across all code. Use `t.*` contracts exclusively (`t.Scalar`, `t.Container`, `t.ConfigMap`, etc.). Duplicate type definitions or compatibility aliases (`MyScalar = t.Scalar`) are FORBIDDEN. Use modern Python typing syntax (`X | Y`).
- **PEP 695 Canonical (Python 3.13+)**: ALL type aliases in `typings.py` must use `type X = ...` syntax. These create `TypeAliasType` objects—using them in `isinstance()` crashes at runtime and is FORBIDDEN. Runtime narrowing MUST use `u.is_*()` functions instead.
- **Type Narrowing**: NEVER use `type(x) is T` or `type(x) == T` to narrow types. Use `isinstance(x, T)` or `TypeGuard`. Avoid gratuitous narrowings for types that shouldn't exist. `cast()` is completely forbidden outside `flext-core` result internals.
- **Nullability and Unions**:
  - `| None` is ONLY permitted inline at usage sites when business semantics require it (e.g., "not configured"). Never bake it into aliases.
  - Inline composed type annotations (e.g., `str | int`) are FORBIDDEN in application code.
- **`t.Container` Exclusivity**: `type Container = Scalar | Path`. `BaseModel` is TOTALLY FORBIDDEN inside `t.Container`. If both are needed, use explicit `t.Container | BaseModel`.

### 3.3 Failures & Error Handling
- **`r[T]` for Fallible Operations** function that can fail MUST return `r[T]`. `T | None`, bare exceptions, and ad-hoc error dicts are FORBIDDEN. The `r` alias is mandatory.
- **No Exceptions as Control Flow**: Bare `try/except` in business logic is FORBIDDEN when `r` composition (`map`/`flat_map`/`lash`) can handle the flow. Bare `except:` is universally forbidden. Catch explicit exceptions.

### 3.4 Tools, Modules & Environment
- **Imports Rules**:
  - `from __future__ import annotations` MUST be the first import in every Python module.
  - `typing.TYPE_CHECKING` is ALLOWED ONLY for type-only imports and `__init__.py` lazy loading, NEVER with Pydantic models. Autogenerated `__init__.py` files MUST preserve the lazy-export pattern.
  - `_LAZY_IMPORTS` string references MUST match real class names exactly.
  - Import parent components by CLASS NAME (e.g. `from flext_core import FlextProtocols`), never by assigned alias.
- **Command & Output Abstractions**: Bare `subprocess` calls, `sys.exit` outside `__main__.py`, direct `dependency_injector` wiring, and `print()` in production are FORBIDDEN. Use provided abstractions and `FlextLogger`.
- **Zero Hacks**: `model_rebuild()`, `exec()`, `eval()`, direct architectural `getattr()`, inline imports, and fallback `try/except ImportError` blocks are TOTALLY FORBIDDEN.

### 3.5 Integrity & Change Management
- **Context Evaluation**: Read and fully understand existing code, MRO chains, and base classes BEFORE changing code. Maximize reuse. Simplifications, TODOs, mocks, and stubs are FORBIDDEN.
- **AST-Grep Required**: Structural code changes/renames across the codebase MUST use `ast-grep` (`sg`). Ad-hoc python/shell scripts, `sed`, and `awk` for code transformations are TOTALLY FORBIDDEN.
- **Integral Changes**: After any type, model, or signature change, you MUST update all references across all 33 projects to maintain global consistency.
- **Linter Zero Tolerance**: Code must pass ALL 4 linters (ruff, mypy, pyright, pyrefly) with ZERO errors/warnings. Suppressions (`# type: ignore`) are FORBIDDEN unless accompanied by a verifiable technical explanation and business necessity, restricted to a single line.
- **Evidence Required**: Never claim checks passed without executable evidence.
- **Stay In Scope**: Execute ONLY the assigned task. Out-of-scope cleanups or "obvious improvements" are FORBIDDEN. If found, file a new `beads` issue.
- **Legacy Extermination**: Legacy maintenance, non-business validation fallbacks, compatibility wrappers (`def old(): return new()`), and deprecation shims are ABOMINABLE. Delete and replace immediately. Fix forward.
- **Git is IMMUTABLE**: Rolling back is FORBIDDEN. `git checkout <file>`, `git reset`, `git revert`, and `git stash pop/apply` to OVERWRITE/DISCARD work is forbidden. Fix issues forward.

### 3.6 Test Standardization
- **Unified Test Namespace**: Tests MUST strictly consume utilities, constants, types, and models from the central test infrastructure (`tests.infra`). Direct imports from `flext_core` or `flext_infra` into `tests/unit` codebase are FORBIDDEN if an equivalent exists in `tests.infra`.
- **Alias Usage**: Use the same canonical aliases for test infrastructure components: `from tests.infra import c, t, p, m, u, h, s`.
- **Test Namespaced Classes & MRO**: Test infrastructure MUST follow the single namespaced class structure using MRO. Test namespaces must compose with `FlextTests` and the project's own namespace (e.g., `class FlextTestInfraConstants(FlextCoreConstants, FlextTestsConstants)`), defining specific Test namespaces per project.
- **Centralized Fixtures & Conftests**: All fixtures and `conftest.py` configurations MUST be centralized within the `tests.infra` MRO structure. Ad-hoc loose mocks or fixtures spread around test scripts are STRICTLY FORBIDDEN. Rely on canonical helpers (`h`) and shared centralized fixtures over recreating isolated objects.
- **Absolute Strictness**: Tests MUST demonstrate the exact same strict typing (`r[T]`), Pydantic v2 execution, and architectural discipline as production code. "Test-only" relaxation or bypassing validators is FORBIDDEN.

### 3.7 Associated Skills
- **Type Law & Result Patterns**: `flext-strict-typing`
- **Result/Logging/DI Patterns**: `flext-patterns`

## §4 Import Law

- Canonical alias imports are mandatory at usage sites: `r,t,c,m,p,u,d,e,h,s,x`. You only ever import the local facade explicitly; parent facades are inherited seamlessly.
- **Dependency Order**: Future, stdlib, third-party, first-party, local.
- **`flext-core` Imports**: Import concrete submodules (`flext_core.<module>`), NOT the package root.
- **Subproject Imports**: Consume public API/facade exports; NEVER import private `_` internals.
- **Forced Patterns**: Wildcard imports and relative imports are FORBIDDEN in governed code.
- **Aliases**: No double-assignment of facade aliases (`c/m/p/t/u` are assigned once at module bottom).
- **Direction**: Cross-tier imports violating architecture direction are FORBIDDEN.
- *Detailed matrix & exceptions*: See skill `flext-import-rules`.

## §5 Make Contract

- **Primary Entrypoint**: Automation entrypoint is always `make`. Raw scripts or direct tool commands (e.g., `pytest`, `ruff check`, `mypy`) are FORBIDDEN. You must exclusively use `make` targets to run tooling.
- **Workspace Verbs**: `setup check security format docs test validate typings clean codegen modernize upgrade`.
- **Project Verbs** (`base.mk`): `setup check security format docs test validate clean`.
- **Git Verbs**: Use `make` for Git operations: `make status`, `make commit MESSAGE="..."`, `make push`, `make tag`, `make pr`.
- **Advanced Make Options**: Use the provided selectors to target scenarios directly instead of writing custom bash loops. Examples: `make check PROJECT=flext-core`, `make test PYTEST_ARGS="-k my_test"`, `make validate VALIDATE_SCOPE=workspace`.
- **Selectors**: `PROJECT`, `PROJECTS`, `CHECK_GATES`, `VALIDATE_GATES`, `PYTEST_ARGS`, `FIX`, `JOBS`, `FAIL_FAST`.
- **Scope Controls** (Workspace): `VALIDATE_SCOPE=project|workspace`, optional `DEPS_REPORT=0`.
- **No Bypasses**: Strictness is mandatory. `SKIP_*` bypass toggles in the contract are FORBIDDEN.
- **Exit Codes**: `0` pass, `1` policy failure, `2` usage/config error, `3` infra/runtime error.
- **Validation**: Policy/automation edits MUST run `make validate VALIDATE_SCOPE=workspace` before claiming completion.
- **Reports**: Must be factual, machine-readable when produced, and include explicit executable next actions.
- *Verb semantics & thresholds*: See skill `flext-quality-gates`.

## §6 Quality Gates

- **Environments**: Workspace `.venv` is mandatory. System Python/pip usage is FORBIDDEN. Project-local `.venv` is fallback-only when workspace `.venv` is missing.
- **Preflight**: Before workspace loops, ensure root `.venv` exists and remove project `.venv` drift. In fallback mode, run `make setup` before loops.
- **`pyproject.toml` Generation**: Files must follow Poetry 2.x + PEP 621/639 constraints. New packages MUST be managed via `poetry add` and `poetry remove`. Furthermore, you must run `make modernize` and `make upgrade` to regenerate, consolidate dependencies, and format the toml files before lock/install. Manually hacking dependency tables is FORBIDDEN.
- **Coverage**: Source of truth is purely `[tool.coverage.report] fail_under` in each project's `pyproject.toml`. No Makefile constants, no `--cov-fail-under` flags.
- **No Silent Failures**: Constructs like `2>/dev/null` or `|| true` on mandatory gates are FORBIDDEN.
- *Gate details & matrix*: See skill `flext-quality-gates`.

## §7 Skill System

- **Authority**: Skills are authoritative detail documents. This file (`AGENTS.md`) is the supreme law surface framing them.
- **Load Order**: Touched-path `rules-*` skill first, supporting skills second. Afterwards, load only minimal skills needed for the change.
- **Mandatory Usage**: Do not implement rules from memory. Do not claim skill usage without reading the `SKILL.md`.
- **Mapping**: Baseline maps must be respected (`flext-core->rules-flext-core`, `src->rules-src`, `tests->rules-tests`, etc.).
- **Rule Definitions**: `rules.yml` schema uses flat fix keys only. Prefer `type: ast-grep`; use `type: custom` only when AST matching is completely unviable. `fix_auto: true` must map to an executable real fix mechanism.
- *Skill format policies*: See skills `skill-format-universal`, `flext-docs-pointer-policy`.

## §8 Change Management

- **Policy Workflow**: Policy changes land in `AGENTS.md` first, then propagate to skill documents.
- **Complete Work**: Never ship incomplete work as complete. Each claim REQUIRES command evidence. Changes must be minimal, explicit, root-cause oriented, and verifiable.
- **No Unapproved Bypass**: Altering lint/gate semantics or deferring/skipping a violation is FORBIDDEN without explicit in-session user approval.
- **Correct Governance**: If governance corrections arise during work, update this file immediately before further implementation.
- **Commit-After-Validation**: Every passing validation MUST be immediately accompanied by a `git add -A` → `git commit` → `git pull --rebase` → `git push` sequence. Uncommitted or unpushed work is LOST WORK.

## §9 Agent Execution Pre-requisites

- **Verify Before Implement**: Check recent commits (`git log --oneline -20`) and active task trackers to prevent duplication. Cross-session deduplication is critical.
- **Scope Discipline**: DO NOT modify files outside the specific task boundary. If blocked, escalate instead of silently rewriting external dependencies.
- **Scale and Parallelism**: Refactoring many call sites or modules across the portfolio should utilize multiple batched passes to retain focus and verifiability.
- **`.new/.old` Swap Protocol**: For massive file modifications (>50 lines changed), create a `.new` file, verify changes, then execute `mv file.py file.py.old && mv file.py.new file.py`. Commit both in one transaction.

### 9.1 Coding Directives for Agents
- **Runtime Aliases**: Subprojects MUST use their own namespace aliases ONLY (e.g., `x` for FlextMixins / runtime helpers: `x.ok`, `x.is_base_model`, etc.). Do NOT subdivide namespaces or introduce extra wrapper layers.
- **No Loose Aliases**: Remove compatibility aliases entirely.
- **Narrowing Enforced**: No `type(x) == T`. Use `isinstance(x, T)` or `TypeGuard` properly. Prefer Pydantic validation functions where structured data is involved.
- **Evidence Requirement**: "Tests pass", "linters clean" claims MUST include command output proof (with exit code and UTC timestamp) so the audit logic can replay the claim. Store evidence in `.sisyphus/evidence/`.

## §10 Multi-Agent Parallel Execution Law

### 10.1 The 11 Commandments (Execution Ritual)
UNBREAKABLE LAW for all parallel agent work:
1. **Organize libs first**: Domain monopoly—each module owns its domain exclusively.
2. **Minimal skeleton**: Start with interfaces/protocols. Optimize structure before implementation.
3. **Reconnect one-by-one**: Fix ONE integration at a time, verify before moving to the next.
4. **Tests last per module**: Update tests AFTER implementation passes static checks.
5. **Zero Tolerance Linters**: Ruff, mypy, pyright, pyrefly MUST all pass. No `# type: ignore`.
6. **Stay in Lane**: Only touch files in your ownership. READ-ONLY for others.
7. **Never Rollback**: Fix forward only. No `git revert`, no deprecation shims.
8. **Commit Frequently**: Every task completion = separate commit + push.
9. **`.new/.old` Owned-Only**: Use the `.new/.old` pattern ONLY for files you own exclusively.
10. **No Automation Scripts**: Manual changes only. No shell scripts for mass edits.
11. **Never Rush/ULW**: No ultrawork mode, no batched giant commits. Perfection over speed.

### 10.2 Core File Ownership (`flext-core`)
**Ownership Matrix**:
| Category | Primary Owner | Read-Only For Others |
|----------|---------------|----------------------|
| **Agent 1** | `dispatcher.py`, `constants.py`, `_models/cqrs.py` | All other agents |
| **Agent 2** | `registry.py`, `typings.py` | All other agents |
| **Agent 3** | `service.py`, `_models/base.py` | All other agents |
| **Agent 4** | `result.py`, `exceptions.py`, `runtime.py`, `loggings.py` | All other agents |
| **Agent 5** | `container.py`, `decorators.py`, `handlers.py`, `mixins.py` | All other agents |
| **FROZEN** | `context.py`, `settings.py`, `models.py`, `utilities.py`, `_utilities/*`, `__version__.py` | NO AGENT MODIFIES |

*Exception*: FROZEN files may be unfrozen ONLY for: (a) annotation additions (typing, `Field()`, imports), or (b) **performance-only caching changes** — adding `ClassVar` cache fields, wrapping instantiations in lazy-load patterns, and adding env-variable configuration toggles — provided the change is isomorphic (same inputs → same outputs), passes all linters and tests, and runs as single-agent work (not parallel). Behavioral logic changes beyond (a) and (b) remain frozen.

**`protocols.py` Section Split**:
- Sections must be appended strictly at the end of their respective ownership blocks.
- **A1**: CommandBus, Middleware, Processor
- **A2**: Registry
- **A3**: Model, Config, Service, Validation, ValidatorSpec
- **A4**: Result, ResultLike, VariadicCallable, ResourceFactory, Log, Logger, Metadata
- **A5**: Context, RuntimeBootstrapOptions, DI, Handler, RegisterableService, ServiceFactory
- *Lines 1-236 & 1289+ are strictly FROZEN for behavioral changes. Performance-only caching additions (ClassVar cache fields, lazy-load wrappers) are permitted per the FROZEN file exception above, limited to method bodies — function/method signatures and class declarations within the frozen range MUST NOT be altered.*

### 10.3 Execution Phases
- **Phase 0 (SOLO)**: Agent 4 completes Wave 0 (`RuntimeResult.__slots__` + `r.fail()` + `p.Result`) and PUSHES. All others BLOCKED.
- **Phase 1**: Agent 4 continues + Agent 5 starts (containers, decorators, etc). A5 must `git pull --rebase` first.
- **Phase 2**: Agent 1 (Dispatcher) + Agent 3 (Service) start. Must `git pull --rebase` first.
- **Phase 3**: Agent 2 (Registry) starts. Must `git pull --rebase` first.
- **Phase 4 (Consumers)**: All agents work on their assigned consumer projects IN PARALLEL.

### 10.4 Lint Scoping & Quality
- **During parallel work**: Agents run linters ONLY on modified files.
- **At phase boundaries**: Agents run FULL project lint (`cd flext-core && make check`) before pushing.
- **Before Phase 4**: ALL agents run full `flext-core` lint and verify ZERO errors. No `# type: ignore`.

### 10.5 Git & Session Hygiene
- **Always Rebase**: `git pull --rebase` before EVERY push. NEVER use basic `git pull`.
- **Never Force Push**: NEVER `git push --force` to main/master.
- **Conflict Resolution**: Conflict in YOUR file → resolve manually. Conflict in ANOTHER agent's file → `git checkout --theirs <file>`.
- **Cross-Session Deduplication**: Before spawning new tasks, verify no other agent is working on the same scope via `.sisyphus/plans/` and `git log --oneline -20`. Merge overlapping plans rather than creating duplicates.
