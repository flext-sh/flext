<!-- TOC START -->

- [§1 Identity](#1-identity)
- [§2 Architecture Law](#2-architecture-law)
  - [2.1 Dependency Flow & Layers](#21-dependency-flow--layers)
  - [2.2 Facades & Namespaces](#22-facades--namespaces)
  - [2.3 Inheritance & Composition](#23-inheritance--composition)
  - [2.4 Governance Anti-Patterns](#24-governance-anti-patterns)
  - [2.5 Service Facade Pattern](#25-service-facade-pattern-apipy--basepy--services)
  - [2.6 Settings Law](#26-settings-law)
  - [2.7 Library Abstraction Boundaries](#27-library-abstraction-boundaries)
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
- **Reviewed**: 2026-04-06.
- **Stack Baseline**: Python 3.13+, Pydantic v2, Ruff, Pyrefly, Poetry, Make.
- **No Shadow Policies**: Agent-specific settings are pointers only. No policy duplication exists outside this file.

## §2 Architecture Law

### 2.1 Dependency Flow & Layers
- **Inward Flow**: Dependency flow is inward only (`L3 -> L2 -> L1 -> L0`). Reverse imports are FORBIDDEN.
- **Layer Breakdown**: `L3` = Orchestration, `L2` = Domain/Infrastructure, `L1` = Foundation/Bridge, `L0` = Contracts.
- **Infrastructure Bridging**: Bridge external infra through runtime/container boundaries, NEVER via direct framework imports.
- **Platform Chains**: `Core -> Cli -> Meltano -> Integration` (orchestration), `Core -> Web -> Api -> Auth` (API layer).

### 2.2 Facades, Namespaces & Naming Patterns
- **One Facade Rule**: Each public facade module defines exactly ONE primary facade class plus ONE canonical alias.
- **Facade Class Naming**: `src/` facades MUST use `Flext<Project><Tier>`. `tests/` facades MUST use `TestsFlext<Project><Tier>`. `examples/` facades MUST use `ExamplesFlext<Project><Tier>`. `scripts/` facades MUST use `ScriptsFlext<Project><Tier>`. Legacy patterns such as `Flext<Project>Test<Tier>`, `FlextTest<Project><Tier>`, and `{Flext<Project>}{Examples|Scripts}<Tier>` are migration debt only and MUST NOT be copied into new work.
- **Private Mixin Naming**: Classes under `_models/`, `_utilities/`, `_protocols/`, and similar private trees MUST keep the project prefix and append only the module concern (e.g. `FlextInfraUtilitiesImportNormalizer`, `tk`).
- **Canonical API & Aliases**: Namespace aliases are the STRICT canonical public API surfaces. You must always use them (`m.MyModel`, `c.MY_CONST`), never the direct classes.
  - `m` = Models (`Flext*Models`)
  - `c` = Constants (`Flext*Constants`)
  - `t` = Types (`Flext*Types`)
  - `u` = Utilities (`Flext*Utilities`)
  - `p` = Protocols (`Flext*Protocols`)
  - `h` = Helpers (`Flext*Helpers` - mostly test/infra)
  - `s` = Services (`Flext*Services`)
- **Organic Namespace Access**: Call sites MUST keep the namespace path produced by MRO (`u.Infra.parse_semver`, `c.Tests.ERR_OK_FAILED`, `m.TargetOracle.ExecuteResult`). Facades MUST NOT flatten nested domain-local classes back onto the facade root with class-level alias assignments.
- **Alias Import Sources**: In `src/` code, `c`, `p`, `t`, `m`, `u` come from `flext_core` or the project's own package (MRO-extended). In `tests/`, `examples/`, and `scripts/`, these aliases MUST be imported from the local MRO package: `from tests import c, m, p, t, u`, `from examples import c, m, t`, etc. NEVER import `c`, `p`, `t`, `u` from a sibling project (e.g., `from flext_target_oracle import t` in test code is FORBIDDEN). Operational aliases (`r`, `e`, `h`, `d`, `s`, `x`) come from `flext_core` or the project's extended package.
- **Strict Boundaries**: Domain boundaries are strict (e.g. `oracle-wms != db-oracle`, `ldap != ldif`).
- **Export Discipline**: `__init__.py` files are exports-only. They must ONLY contain type hints, `__all__`, and the native `__getattr__` module-level lazy load strategy. **These files are AUTO-GENERATED**. You must NEVER edit them manually. Run `make gen` to regenerate lazy initialization exports.

### 2.3 MRO Inheritance & Namespace Composition
- **Single Namespaced Classes (Production & Tests)**: For both production and test infrastructure, you must create exactly ONE local namespaced class per tier (models, constants, helpers, etc.). All domain logic, constants, and methods MUST reside inside this single class.
- **Single Root Nested Namespace**: A `src/` facade root defines exactly one local domain namespace class (e.g. `class Infra:`, `class Tests:`). A `tests/` facade root defines exactly one local project-domain namespace whose test-only branch lives under `.Tests`. No other local top-level nested namespace classes are permitted in the facade.
- **The MRO Cascade & Exhaustive Composition**: Cross-project composition MUST use inheritance via MRO symmetrically across all components. Furthermore, within a project, a top-level facade class MUST strictly compose ALL of its domain-specific subclasses.
  *(Example: `class FlextCoreModels(FlextCoreBaseModels, FlextCoreCQRSModels, FlextCoreSettingsModels): pass` and similarly for `FlextCoreUtilities` composing all `_utilities` subclasses. Loose disconnected subclasses are FORBIDDEN).*
- **Subdirectory Composition Only via MRO**: Private files in `_models/`, `_utilities/`, `_protocols/`, and similar trees define mixin classes only. The public facade composes them directly in its inheritance list. Manual flat wrapper nesting such as `class Docker(tk): pass` inside the facade namespace is STRICTLY FORBIDDEN.
- **Internal Namespaces & Elimination of Loose Objects**: Do not duplicate parent variables. Loose module-level objects or functions outside this class are STRICTLY FORBIDDEN. They must be absorbed into the namespace class as attributes/methods or consumed directly from base classes.
- **Integration Projects** (`tap|target|dbt`): Composed of one platform and one domain via inheritance (e.g., `class FlextTapLdapProtocols(FlextMeltanoProtocols, FlextLdapProtocols): pass`).
- **Naming & Location Patterns**: Classes must be placed in specific locations (e.g., `models.py` or `_models/`) and follow the `Flext<Role><Domain><Facade>` pattern (e.g. `FlextCoreModels`, `FlextTestInfraHelpers`, `FlextTapLdapProtocols`). Test classes must also match the domain they are testing. The integration class name MUST NOT contain the "Meltano" prefix.
- **Test Hierarchy Strictness**: In tests, the MRO hierarchy operates in two axes: test tools + domain under test. The test class MUST compose `FlextTests<Tier>` with the project's own `Flext<Project><Tier>` to gain both testing utilities and the full application context transparently.

### 2.4 Governance Anti-Patterns
- **No Private Imports**: Public contracts MUST be consumed from package facades and root exports only.
- **No Backward-Compat Aliases**: Backward-compatibility alias layers (e.g. `LegacyX = NewX`) and namespace shadowing are FORBIDDEN. You must NEVER re-assign parent aliases.
- **No Facade Mirrors**: Public facade modules (e.g. `core.py`, `client.py`) must NEVER duplicate code from `_utilities/` or `_models/` internals. Implementation lives in `_utilities/`; the public module is a thin re-export stub:
  ```python
  """Re-export from internal module."""
  from __future__ import annotations
  from <package>._utilities.<module> import <Symbol1>, <Symbol2>
  __all__: list[str] = ["Symbol1", "Symbol2"]
  ```
  If `qlty smells` reports `identical-code` between a public file and its `_utilities/` counterpart, replace the public file with a re-export immediately.

*For full MRO matrix, architecture layers, and anti-patterns logic, consult skills:* `flext-mro-namespace-rules`, `flext-architecture-layers`, `flext-patterns`, `rules-flext-core`, `rules-src`.

### 2.5 Service Facade Pattern (`api.py` + `base.py` + `services/`)

Projects that provide a main service class (e.g., FlextCli, FlextLdif, FlextObservability) MUST follow the **MRO service facade pattern**:

- **`api.py`** — The single entry-point class `Flext<Project>` composing ALL service mixins via MRO inheritance. Only infrastructure (factory methods, Constants, model aliases) is defined locally. All domain behavior comes from mixins.
- **`base.py`** — `Flext<Project>ServiceBase(s[T], ABC)` providing typed settings access. All mixins inherit from this base.
- **`services/`** — One file per concern, one mixin class per file. Each mixin provides a single domain responsibility (e.g., tracing, metrics, health). Auto-generated `__init__.py` via `make gen`.

```
flext-<project>/src/flext_<project>/
├── api.py                   # Flext<Project> MRO facade
├── base.py                  # Flext<Project>ServiceBase
├── constants.py             # c = Flext<Project>Constants
├── models.py                # m = Flext<Project>Models
├── protocols.py             # p = Flext<Project>Protocols
├── typings.py               # t = Flext<Project>Types
├── utilities.py             # u = Flext<Project>Utilities
├── settings.py              # Flext<Project>Settings
└── services/
    ├── __init__.py           # AUTO-GENERATED
    ├── <concern_a>.py        # Flext<Project><ConcernA>Mixin
    ├── <concern_b>.py        # Flext<Project><ConcernB>Mixin
    └── ...
```

```python
# api.py — MRO facade (canonical example)
class FlextObservability(
    FlextObservabilityContextMixin,
    FlextObservabilityMetricsMixin,
    FlextObservabilityTracingMixin,
    FlextObservabilityHealthMixin,
    # ... all service mixins
    FlextObservabilityServiceBase,
):
    """All domain methods come from mixins via MRO."""
```

```python
# base.py — typed service base
class FlextObservabilityServiceBase(s[t.Dict], ABC):
    @property
    @override
    def settings(self) -> FlextObservabilitySettings:
        return FlextSettings.get_global().get_namespace(
            "observability", FlextObservabilitySettings
        )
```

**Rules**:
1. **No standalone service classes** — every service class MUST be a mixin on the facade.
2. **No re-export stubs for services** — access is via the facade (`FlextObservability().method()`), not individual class import.
3. **One concern per mixin** — each `services/*.py` file defines ONE mixin class.
4. **MRO field conflicts** — the facade MUST declare shared fields (`_logger`, `_container`) to shadow inherited duplicates.
5. **No public accessor prefixes on service facades** — public `get_*`, `set_*`, and `is_*` methods/properties are FORBIDDEN. Local deterministic derivation MUST become fields or `@computed_field`; external boundary reads MUST use domain verbs such as `fetch_*` or `resolve_*`; state mutation MUST use validated model assignment, `model_copy(update=...)`, or a domain verb such as `configure`, `apply`, or `update`.
6. **Service runtime state is centralized** — each service concern MUST flow through one central `m.<Domain>.*State` or `m.<Domain>.*Status` model instead of spreading round-trips through many small carrier models, dict conversions, and ad-hoc type narrowing.

**Reference implementations**: `flext-cli/src/flext_cli/`, `flext-ldif/src/flext_ldif/`, `flext-observability/src/flext_observability/`.

### 2.6 Settings Law

- **Mandatory Inheritance**: ALL settings classes MUST inherit `FlextSettings`. Using `m.Value`, `BaseSettings`, `BaseModel`, or custom singleton patterns for configuration is FORBIDDEN.
- **ConfigDict Required**: Every settings class MUST define `model_config = ConfigDict(env_prefix="FLEXT_<PROJECT>_", extra="ignore")`.
- **Env Prefix Convention**: `FLEXT_` (core), `FLEXT_CLI_` (cli), `FLEXT_MELTANO_` (meltano), `FLEXT_API_` (api), `FLEXT_AUTH_` (auth), `ORACLE_` (db-oracle), `FLEXT_<ROLE>_<DOMAIN>_` (integration projects).
- **Constants as Defaults**: ALL field defaults MUST come from `c.*` constants. Hardcoded strings, numbers, or booleans as defaults are FORBIDDEN.
- **No os.environ Access**: `os.environ`, `os.getenv`, `environ.get()` in `src/` code is PROHIBITED. Use FlextSettings env resolution or `c.*` constants. Tests are exempt.
- **Singleton via Base**: Use `FlextSettings.__new__()` singleton. Custom `_global_instance`, manual locks, or class-level instance caches are FORBIDDEN.
- **Namespace Registration**: Use `@FlextSettings.auto_register("<namespace>")` for namespace access via `FlextSettings.get_namespace()`.
- **MRO Composition**: Integration projects (tap/target/dbt) MUST use dual-inheritance for settings, same as models: `FlextTargetOracleSettings(FlextMeltanoSettings, FlextDbOracleSettings)`.
- **Auto-MRO Env Sources**: `settings_customise_sources` in FlextSettings base auto-resolves parent env prefixes from MRO. Leaf class env_prefix takes priority, parent prefixes are fallbacks.

### 2.7 Library Abstraction Boundaries

- **Mandatory Abstraction Enforcement**: Libraries abstracted by any flext project (dependency_injector, structlog, rich, typer, tomlib, rope, etc.) MUST NOT be used directly outside that project's `src/` domain.
- **Scope**: Applies to all external usage (other projects' `src/`, `tests/`, `examples/`, `scripts/`, typings, constants, annotations).
- **Access Pattern**: Always use public abstractions from the originating library: `m.*` (models), `c.*` (constants), `t.*` (types), `u.*` (utilities), `p.*` (protocols), `r[T]` (result container).
- **Cross-Project Abstraction**: If project A abstracts pydantic, project B must access pydantic through A's public contracts (`m.`, `c.`, `t.`, etc.), never via direct `from pydantic import ...`.
- **No Bare Framework Imports in Consumers**: `from pydantic import ...`, `from dependency_injector import ...`, `from structlog import ...` in project code outside flext-core are FORBIDDEN if the framework is abstracted by flext-core.
- **Testing Exemption**: In test code under `tests/`, use local test façades and helpers; if direct third-party imports are unavoidable for test scaffolding, document the exception with a technical justification comment.
- **No Example/Script Exemption**: `examples/` and `scripts/` are NOT exempt from abstraction boundaries. Direct imports of abstracted libraries are forbidden there unless the code lives inside the owning abstraction project `src/` domain.
- **Core Abstraction Inventory**: flext-core abstracts: pydantic v2, dependency_injector, structlog, returns (`r[T]`), orjson, pyyaml, and foundational contracts. All other projects must use flext-core abstractions for these.
- **Enforcement**: Use `ruff` with import rules (e.g., flake8-noqa, import-order rules) and grep audits to detect violations. Suppress only with documented technical justification.

## §3 Code Law

### 3.1 Architecture & Code Structure
- **MVI 200-LINE CAP (SUPREME LAW)** module, class, method, or function >200 **code lines** is a violation. Line count is measured via `tokei` (logical LOC only — blank lines, comments, and docstrings are excluded from the count). Refactor immediately using strict OO composition and canonical MRO architecture. Decompose into explicit contracts and reusable domain components—never use compression hacks. **FORBIDDEN approaches to meet the cap**: removing blank lines, removing or compressing docstrings, style/formatting changes that reduce line count, and arbitrary code splits without domain decomposition. Only genuine OO decomposition via MRO inheritance, facade extraction to `_models/`/`_utilities/` subdirectories, and domain responsibility separation are valid.
  - **VALID code reduction** (actively encouraged): deleting dead/unused code, removing unnecessary helpers and pass-through wrappers (`def old(): return new()`), removing proxy functions/classes, removing backward-compat aliases (`LegacyX = NewX`), and replacing inline composed type annotations (`str | t.Numeric`) with canonical `t.*` contracts from `typings.py`. These eliminate real architectural violations and are the preferred first step before OO decomposition.
- **Pydantic v2 Mastery**: Every class MUST extend Pydantic v2 `BaseModel` (or FLEXT base models) via MRO. Fully utilize `Field()`, `model_config = ConfigDict(...)`, `PrivateAttr()`, and built-in constraints. Standalone `*Settings` classes, unnecessary `@property`, manual `self._x` assignments, line-reduction wrappers, and public `get_*`/`set_*`/`is_*` accessors are FORBIDDEN.
- **Accessor Naming Law**: Values already present in object state or derived locally MUST be exposed as fields or `@computed_field`; mutations MUST occur through validated model state or a domain verb; boolean outcomes/statuses MUST use noun/adjective names such as `success`, `failure`, `expired`, `configured`, `connected`, or `healthy`.
- **MRO Inheritance Hierarchy**: Domain logic must reside in a single nested class hierarchy. Subprojects inherit from the parent project's facade class to cascade namespaces. Loose functions or standalone classes without MRO lineage are FORBIDDEN. They MUST be absorbed into the namespace classes or used via existing base classes.
- **Utility & Helper Generalization (`u.*`)**: All shared helpers MUST strictly flow through the `u.*` utilities namespace. Do not duplicate logic. Use and enhance the lowest-level function available, systematically generalizing existing code rather than creating new redundant functions.
- **Centralize Polymorphic Code**: Dismantle polymorphic functions branching on type unions. Use centralized Pydantic v2 models with discriminated unions and validation.
- **Centralized Runtime Contracts**: Inputs, outputs, runtime state, and status snapshots MUST flow through central `m.*` models. Eliminate avoidable dict round-trips, ad-hoc conversion helpers, and non-essential type narrowing between service boundaries.

### 3.2 Types & Contracts
- **Strict Contracts Only**: `Any`, bare `t.RecursiveContainer`, and `Mapping[str, Any]` are TOTALLY FORBIDDEN across all code. Use `t.*` contracts exclusively (`t.Scalar`, `t.Container`, `t.ConfigMap`, etc.). Duplicate type definitions or compatibility aliases (`MyScalar = t.Scalar`) are FORBIDDEN. Use modern Python typing syntax (`X | Y`).
  - **Exception: Intentional Generic Types** - `t.RecursiveContainerMapping` and `t.RecursiveContainerMapping` ARE permitted ONLY in these contexts:
    1. **Type aliases** (in `typings.py`): `type ProjectSettings = t.RecursiveContainerMapping` with docstring explaining intent
    2. **Test fixtures** (in `conftest.py` and test support): Dynamic test data with unknown structure
    3. **Validation/Rule engines**: Return types for unstructured violations (e.g., `r[Sequence[t.RecursiveContainerMapping]]`)
    4. **Configuration transformers**: Methods that accept/return dynamic configuration from external sources (YAML, JSON)
    - **All other uses are FORBIDDEN**. Use `t.RecursiveContainer` or specific Pydantic models instead.
- **PEP 695 Canonical (Python 3.13+)**: ALL type aliases in `typings.py` must use `type X = ...` syntax. These create `TypeAliasType` objects—using them in `isinstance()` crashes at runtime and is FORBIDDEN. Runtime narrowing MUST use `u.is_*()` functions instead.
- **Type Narrowing**: NEVER use `type(x) is T` or `type(x) == T` to narrow types. Use `isinstance(x, T)` or `TypeGuard`. Avoid gratuitous narrowings for types that shouldn't exist. `cast()` is completely forbidden outside `flext-core` result internals.
- **Nullability and Unions**:
  - `| None` is ONLY permitted inline at usage sites when business semantics require it (e.g., "not configured"). Never bake it into aliases.
  - Inline composed type annotations (e.g., `str | int`) are FORBIDDEN in application code.
- **`t.Container` Exclusivity**: `type Container = t.Container`. `BaseModel` is TOTALLY FORBIDDEN inside `t.Container`. If both are needed, use explicit `t.Container | BaseModel`.

### 3.3 Failures & Error Handling
- **`r[T]` for Fallible Operations** function that can fail MUST return `r[T]`. `T | None`, bare exceptions, and ad-hoc error dicts are FORBIDDEN. The `r` alias is mandatory.
- **Result Outcome Naming**: `r[T]` carriers and result-like protocols/models MUST expose `success`/`failure`, never `is_success`/`is_failure`. Type-guard helpers MUST use non-`is_` names such as `successful_result` and `failed_result`.
- **DSL-First Failure Construction**: In application/runtime flows, prefer centralized DSL helpers (`e.fail_*`, `r.fail_op`, `r.fail_exc`, and `s.fail_*` helpers) over ad-hoc `r.fail("...")` string construction. Direct `r.fail(...)` is reserved for primitive result internals, test scaffolding, or cases requiring explicit `error_data` passthrough.
- **Runtime Strictness**: In `src/` runtime paths, ad-hoc `r.fail(...)` is forbidden unless preserving structured `error_data` from an external boundary. Default to `e.fail_*`, `r.fail_op`, or `r.fail_exc`.
- **No Exceptions as Control Flow**: Bare `try/except` in business logic is FORBIDDEN when `r` composition (`map`/`flat_map`/`lash`) can handle the flow. Bare `except:` is universally forbidden. Catch explicit exceptions.

### 3.4 Tools, Modules & Environment
- **Imports Rules**:
  - `from **future** import annotations

from collections.abc import Mapping, Sequence` MUST be the first import in every Python module.
  - `typing.TYPE_CHECKING` is ALLOWED ONLY for type-only imports and `__init__.py` lazy loading. Autogenerated `__init__.py` files MUST preserve the lazy-export pattern.
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
- **Alias Usage**: Use the same canonical aliases for test infrastructure components: `from tests import c, t, p, m, u`.
- **Test Facade Naming**: Test facades MUST use the `TestsFlext<Project><Tier>` pattern. Legacy `Flext<Project>Test<Tier>` and `FlextTest<Project><Tier>` forms are migration targets only.
- **Test Namespaced Classes & MRO**: Test infrastructure MUST follow the single namespaced class structure using MRO. Test namespaces must compose with `TestsFlext` and the project's own namespace (e.g., `class TestsFlextInfraConstants(FlextCoreConstants, FlextTestsConstants)`), defining the test-only branch under `<Domain>.Tests`.
- **Centralized Fixtures & Conftests**: All fixtures and `conftest.py` configurations MUST be centralized within the `tests.infra` MRO structure. Ad-hoc loose mocks or fixtures spread around test scripts are STRICTLY FORBIDDEN. Rely on canonical helpers (`h`) and shared centralized fixtures over recreating isolated objects.
- **Absolute Strictness**: Tests MUST demonstrate the exact same strict typing (`r[T]`), Pydantic v2 execution, and architectural discipline as production code. "Test-only" relaxation or bypassing validators is FORBIDDEN.
- **Behavior-Only Test Contract**: Tests MUST assert public, observable behavior of modules, facades, and services — never their private implementation details. Assertions against internal warning text, stack trace fragments, private helper names, local alias spellings (`p`, `m`, etc.), exact internal class names, MRO shape, or other non-contract internals are FORBIDDEN unless that exact surface is itself the explicit public contract being tested. When a test fails because internals were refactored but behavior is unchanged, the test is wrong and MUST be rewritten to assert stable external behavior instead.
- **No Test Accessor Leakage**: Tests MUST exercise the canonical public contract after migration — fields, `@computed_field`, public verbs, and `r` outcomes (`success`/`failure`) only. Tests that reach into legacy getters/setters/predicates or rely on transitional naming are violations.

### 3.7 Associated Skills
- **Namespace/MRO Law**: `flext-mro-namespace-rules`
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
- **No Same-Project Cross-Facade Runtime Imports**: Public same-project facade files (`constants.py`, `models.py`, `protocols.py`, `typings.py`, `utilities.py`) MUST NOT import sibling public facades or aliases at runtime. Use direct private-class imports from `_models/*` / `_utilities/*` or MRO inheritance instead. The only standing runtime exception is `FlextRuntime` inside `flext-core`.
- **Abstraction Boundary Enforcement (SUPREME LAW)**: Libraries abstracted by a flext project MUST NOT be imported directly outside that project's `src/` domain. Core-abstracted libraries (pydantic, dependency_injector, structlog, returns, orjson, pyyaml) are FORBIDDEN in consumers (`tests/`, `examples/`, `scripts/`, other projects' `src/`). Use public abstractions from the originating library (`m.*`, `c.*`, `p.*`, `t.*`, `u.*`, `r[T]`) instead. This applies equally to runtime code, typing annotations, and constants.
- **Facade Import Matrix**:
  - `typings.py` may reference same-project `p` and `m` ONLY under `TYPE_CHECKING`.
  - `protocols.py` may reference same-project `t` and `m` ONLY under `TYPE_CHECKING`.
  - `models.py` may reference same-project `t` and `p` ONLY under `TYPE_CHECKING`.
  - `constants.py` may import same-project runtime symbols when genuinely required.
  - `utilities.py`, `_models/*`, and `_utilities/*` may import private classes directly across private modules to break cycles, but MUST NOT hop through sibling public facades.
- **Circular Import Resolution (CRITICAL)**:
  - **Root Cause**: Circular imports arise when modules at the same tier (e.g., `_protocols/base.py` and `_protocols/result.py`) reference each other, or when TIER 0.5 modules need types from TIER 1+.
  - **Correct Solution** (NO workarounds):
    1. **Use `from **future** import annotations

from collections.abc import Mapping, Sequence`** — Converts ALL type hints to forward references (strings). This allows type hints to reference types not yet imported.
    2. **Use`TYPE_CHECKING` ONLY for type-only imports** — When a module needs a type in annotations but importing it would create a cycle, use `TYPE_CHECKING`:
       ```python
       from **future** import annotations

from collections.abc import Mapping, Sequence
       from typing import TYPE_CHECKING

       if TYPE_CHECKING:
           from flext_core import FlextProtocolsResult


       def validate(self) -> FlextProtocolsResult.Result[bool]:  # Works! String at runtime
           ...
       ```
    3. **Import concrete submodules, NOT `flext_core`** — In internal modules (`_protocols/`, `_models/`, `_typings/`), import from sibling submodules or foundation modules directly:
       ```python
       # ✓ CORRECT
       from flext_core import FlextProtocolsBase
       from flext_core import t

       # ✗ WRONG — causes lazy-load cycles
       from flext_core import FlextProtocolsBase, t
       ```
    4. **Trust lazy loading in `__init__.py`** — The `__init__.py` lazy-load system (via `lazy_getattr`) properly sequences module initialization to break cycles. Do NOT use workarounds like `model_rebuild()`, string annotations, or `t.RecursiveContainer`/`Any` types.
  - **FORBIDDEN Workarounds**:
    - ✗ Using `model_rebuild()` — indicates root-cause unresolved
    - ✗ Using string type hints like `"FlextProtocolsResult.Result[bool]"` — use TYPE_CHECKING instead
    - ✗ Using `t.RecursiveContainer` or `Any` as catch-all types — use precise `t.*` contracts
    - ✗ Reordering `__init__.py` imports or relying on "order of initialization" — architecture must NOT depend on load order
  - **Verification**: Run `make gen` without timeout or errors. Imports should resolve cleanly via `python -c "from flext_core._protocols.* import *"`.
  - *Detailed matrix & exceptions*: See skill `flext-import-rules`.

## §5 Make Contract

- **Primary Entrypoint**: Automation entrypoint is `make` for multi-gate workflows. Bare tool commands (`ruff check`, `pyrefly check`, `pyright`, `mypy`, `pytest`) are allowed for single-file checks — they are auto-proxied through RTK for token savings. Never use `.venv/bin/` prefixed paths.
- **Workspace Verbs**: `boot check scan fmt docs test val types clean gen mod up sync`.
- **Project Verbs** (`base.mk`): `boot check scan fmt docs test val clean`.
- **Git Verbs**: Use `make` for Git operations: `make stat`, `make save MESSAGE="..."`, `make push`, `make tag`, `make pr`.
- **Advanced Make Options**: Use the provided selectors to target scenarios directly instead of writing custom bash loops. Examples: `make check PROJECT=flext-core FILE=src/foo.py CHECK_GATES=pyright`, `make test MATCH=test_container FAIL_FAST=1`, `make check CHANGED_ONLY=1`.
- **Selectors**: `PROJECT`, `PROJECTS`, `CHECK_GATES`, `VALIDATE_GATES`, `PYTEST_ARGS`, `FIX`, `JOBS`, `FAIL_FAST`, `FILE`, `FILES`, `CHANGED_ONLY`, `MATCH`, `RUFF_ARGS`, `PYRIGHT_ARGS`, `CHECK_ONLY`, `VERBOSE`.
- **File Targeting** (`check`/`test`/`format`): `FILE=<path>` or `FILES="a.py b.py"` runs only on those files (fast-path, bypasses `flext_infra check run`). `CHANGED_ONLY=1` auto-discovers git-modified `.py` files.
- **Test Shortcuts**: `MATCH=<expr>` is an alias for pytest `-k <expr>`. `FAIL_FAST=1` adds `-x`. `VERBOSE=1` adds `-vv -s`.
- **Lint Shortcuts**: `RUFF_ARGS="--select E501"` passes extra args to ruff. `PYRIGHT_ARGS="--level basic"` passes extra args to pyright. `CHECK_ONLY=1` on format/check runs without writing (dry-run).
- **Scope Controls** (Workspace): `VALIDATE_SCOPE=project|workspace`, optional `DEPS_REPORT=0`.
- **No Bypasses**: Strictness is mandatory. `SKIP_*` bypass toggles in the contract are FORBIDDEN.
- **Exit Codes**: `0` pass, `1` policy failure, `2` usage/settings error, `3` infra/runtime error.
- **Validation**: Policy/automation edits MUST run `make val VALIDATE_SCOPE=workspace` before claiming completion.
- **Reports**: Must be factual, machine-readable when produced, and include explicit executable next actions.
- *Verb semantics & thresholds*: See skill `flext-quality-gates`.

## §6 Quality Gates

- **Environments**: Workspace `.venv` is mandatory. System Python/pip usage is FORBIDDEN. Project-local `.venv` is fallback-only when workspace `.venv` is missing.
- **Preflight**: Before workspace loops, ensure root `.venv` exists and remove project `.venv` drift. In fallback mode, run `make boot` before loops.
- **`pyproject.toml` Generation**: Files must follow Poetry 2.x + PEP 621/639 constraints. New packages MUST be managed via `poetry add` and `poetry remove`. Furthermore, you must run `make mod` and `make up` to regenerate, consolidate dependencies, and format the toml files before lock/install. Manually hacking dependency tables is FORBIDDEN.
- **Coverage**: Source of truth is purely `[tool.coverage.report] fail_under` in each project's `pyproject.toml`. No Makefile constants, no `--cov-fail-under` flags.
- **No Silent Failures**: Constructs like `2>/dev/null` or `|| true` on mandatory gates are FORBIDDEN.
- *Gate details & matrix*: See skill `flext-quality-gates`.

## §7 Skill System

- **Authority**: Skills are authoritative detail documents. This file (`AGENTS.md`) is the supreme law surface framing them.
- **Load Order**: Touched-path `rules-*` skill first, supporting skills second. Afterwards, load only minimal skills needed for the change.
- **Mandatory Usage**: Do not implement rules from memory. Do not claim skill usage without reading the `SKILL.md`.
- **Mapping**: Baseline maps must be respected (`flext-core->rules-flext-core`, `src->rules-src`, `tests->testing-patterns`, etc.).
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
- **Runtime Aliases**: `c`, `p`, `t`, `m`, `u` are declared via MRO in each layer (`src/`, `tests/`, `examples/`, `scripts/`). In test code: `from tests import c, m, p, t, u`. In examples: `from examples import ...`. NEVER import aliases across project boundaries (e.g., `from flext_target_oracle import t` in tests is FORBIDDEN). Operational aliases (`r`, `e`, `h`, `d`, `s`, `x`) come from `flext_core` or the project's extended package.
- **No Loose Aliases**: Remove compatibility aliases entirely. Constants belong in `c`, protocols in `p`, typings in `t`, models in `m`, utilities/helpers in `u`. Never maintain these concerns outside their canonical namespace.
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
- **A3**: Model, Settings, Service, Validation, ValidatorSpec
- **A4**: Result, Result, VariadicCallable, ResourceFactory, Log, Logger, Metadata
- **A5**: Context, RuntimeBootstrapOptions, DI, Handler, RegisterableService, ServiceFactory
- *Lines 1-236 & 1289+ are strictly FROZEN for behavioral changes. Performance-only caching additions (ClassVar cache fields, lazy-load wrappers) are permitted per the FROZEN file exception above, limited to method bodies — function/method signatures and class declarations within the frozen range MUST NOT be altered.*

### 10.3 Execution Phases
- **Phase 0 (SOLO)**: Agent 4 completes Wave 0 (`RuntimeResult.__slots__` + `r.fail()` + `p.Result`) and PUSHES. All others BLOCKED.
- **Phase 1**: Agent 4 continues + Agent 5 starts (containers, decorators, etc). A5 must `git pull --rebase` first.
- **Phase 2**: Agent 1 (Dispatcher) + Agent 3 (Service) start. Must `git pull --rebase` first.
- **Phase 3**: Agent 2 (Registry) starts. Must `git pull --rebase` first.
- **Phase 4 (Consumers)**: All agents work on their assigned consumer projects IN PARALLEL.

### 10.4 Lint Scoping & Quality
- **During parallel work**: Agents run linters ONLY on modified files using bare commands (`ruff check <file>`, `pyrefly check <file>`, `pyright <file>`, `mypy <file>`). RTK auto-proxies for token savings.
- **At phase boundaries**: Agents run FULL project lint (`cd <project> && make check`) before pushing.
- **Before Phase 4**: ALL agents run full `flext-core` lint and verify ZERO errors. No `# type: ignore`.

### 10.5 Git & Session Hygiene
- **Always Rebase**: `git pull --rebase` before EVERY push. NEVER use basic `git pull`.
- **Never Force Push**: NEVER `git push --force` to main/master.
- **Conflict Resolution**: Conflict in YOUR file → resolve manually. Conflict in ANOTHER agent's file → `git checkout --theirs <file>`.
- **Cross-Session Deduplication**: Before spawning new tasks, verify no other agent is working on the same scope via `.sisyphus/plans/` and `git log --oneline -20`. Merge overlapping plans rather than creating duplicates.
