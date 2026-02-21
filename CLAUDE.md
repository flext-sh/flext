# CLAUDE.md — Canonical Engineering Rules


<!-- TOC START -->
- [Non-Negotiable Rules](#non-negotiable-rules)
- [Zero-Tolerance Delivery and Integrity Policy](#zero-tolerance-delivery-and-integrity-policy)
- [Namespaced Alias Composition (CRITICAL — Read Every Word)](#namespaced-alias-composition-critical-read-every-word)
  - [Alias Definitions (module-level, mandatory)](#alias-definitions-module-level-mandatory)
  - [Import Rules](#import-rules)
  - [Namespaced Composition (usage pattern)](#namespaced-composition-usage-pattern)
  - [Complete Alias Map (flext-core)](#complete-alias-map-flext-core)
  - [Prohibited Actions](#prohibited-actions)
- [`__init__.py` Rules](#initpy-rules)
- [One Class Per Module](#one-class-per-module)
- [Skill System Contract](#skill-system-contract)
- [Make Automation Contract](#make-automation-contract)
  - [Workspace Verbs (root `Makefile`)](#workspace-verbs-root-makefile)
  - [Project Verbs (per-project `base.mk`)](#project-verbs-per-project-basemk)
  - [Parameters](#parameters)
  - [Exit Code Contract](#exit-code-contract)
  - [Reporting and Artifacts](#reporting-and-artifacts)
  - [Maintenance and standard places](#maintenance-and-standard-places)
- [AST-Grep First and Script Locality](#ast-grep-first-and-script-locality)
- [Typing Supply Chain Rules](#typing-supply-chain-rules)
- [Workspace Virtual Environment](#workspace-virtual-environment)
- [pyproject.toml Hygiene](#pyprojecttoml-hygiene)
  - [Workspace anti-drift gate](#workspace-anti-drift-gate)
- [Required Preflight for Workspace Loops](#required-preflight-for-workspace-loops)
- [Change Management](#change-management)
- [Code Instrumentation Minimum Standard](#code-instrumentation-minimum-standard)
- [Skills Usage Baseline](#skills-usage-baseline)
- [Skill Enforcement and Fast Context Lookup](#skill-enforcement-and-fast-context-lookup)
<!-- TOC END -->

**Reviewed**: 2026-02-18

This file is the canonical source of truth for agent behavior in this repository.
Agent-specific files must reference this file and must not duplicate policy text.

## Non-Negotiable Rules

- No bypasses or workaround paths in validation/fix pipelines.
- No silent failure patterns (`2>/dev/null`, `|| true`, warning-only fallthrough for mandatory gates).
- No suppression-based typecheck escapes (`# pyrefly: ignore`, baselines as permanent suppression, ignore comments).
- Workspace `.venv` is mandatory when it exists. Project-local `.venv` is allowed only as fallback for project-scoped commands when workspace `.venv` is missing. Never use system Python or system pip.
- Every required wave step must be complete before advancing.

## Zero-Tolerance Delivery and Integrity Policy

Absolute prohibitions. Any violation is summarily forbidden and treated as policy failure.

- No code duplication. Reuse or extract shared logic first; duplicate blocks, duplicate adapters, and copy-paste fixes are prohibited. No exceptions.
- No over-engineering. Do not introduce speculative abstractions, premature extensibility, or complexity without an immediate validated need.
- No simplistic under-engineering. Do not deliver partial, fragile, or placeholder implementations that ignore required constraints.
- No rule bypassing. Do not skip mandatory gates, do not fake completion, and do not use hidden suppression paths.
- No lying. Do not claim tests passed, validation succeeded, or behavior works without direct tool evidence. Do not fabricate evidence, conceal failures, or misrepresent scope or status.
- No false reports. Do not emit inaccurate counts, fake green summaries, or reports that hide real failures.
- No unfinished delivery declared as done. A task is complete only after full implementation and required verification evidence.
- No excuse-driven execution. Report blockers with facts, but do not replace required work with justification text.
- No god engineering. God classes, god modules, and all-in-one orchestration blobs that violate separation of concerns are prohibited.

Mandatory engineering posture for all changes:

- Keep it simple where possible, but always correct and complete.
- Keep it SOLID and DRY with explicit contracts and clear boundaries.
- Prefer root-cause fixes over patches, and structural reuse over repetition.
- If correctness and simplicity conflict, preserve correctness and reduce complexity without losing requirements.

Mandatory completion contract:

- Never mark work complete without running the required checks for the touched scope.
- Never present assumptions as facts; if unknown, state unknown and verify.
- Never leave planned mandatory steps incomplete; finish them or explicitly report why completion is blocked.
- Every failure report must include factual evidence and an executable next action.

No invention and no assumptions:

- Never invent files, commands, targets, outputs, test results, coverage, or validation status.
- Never claim a Make target exists without checking the current `Makefile`.
- Never claim a script/skill exists without checking its real path.
- If uncertain, state uncertainty and verify before proposing or concluding.
- Any fabricated claim is a policy failure.

Enforcement:

- On violation, block delivery immediately and treat the result as policy failure.
- On violation, document factual evidence and required remediation before any re-submission.
- No silent override, no hidden waiver, and no merge while a known violation remains open.

Verification obligations before any completion claim:

1. Run required checks for the touched scope (`make check`, `make validate`, or project-specific gates).
2. Keep direct command evidence for every success claim (output and exit status).
3. Include explicit next actions (`TODO: make PROJECT=<name> <target>`) for each failed gate.
4. Re-validate behavior with direct command evidence after each substantive change.
5. Do not mark work complete until steps 1-4 are satisfied for the affected scope.

## Namespaced Alias Composition (CRITICAL — Read Every Word)

Shorthand aliases (`c`, `d`, `e`, `h`, `m`, `p`, `r`, `s`, `t`, `u`, `x`) are the **canonical API surface** of every FLEXT package. They are NOT optional conveniences — they ARE the public interface.

### Alias Definitions (module-level, mandatory)

Each public facade module defines its alias at the bottom of the file:

```python
# In flext_core/constants.py (bottom of file)
c = FlextConstants
__all__ = ["FlextConstants", "c"]

# In flext_core/models.py (bottom of file)
m = FlextModels
__all__ = ["FlextModels", "m"]

# In flext_core/result.py (bottom of file)
r = FlextResult
__all__ = ["FlextResult", "r"]
```

These alias lines MUST exist. Removing them breaks the entire ecosystem.

### Import Rules

Internal imports (within the same package's `src/`):

```python
# CORRECT — always use the alias
from flext_core.constants import c
from flext_core.models import m
from flext_core.result import r

# WRONG — never import the full class name
from flext_core.constants import FlextConstants  # ❌
from flext_core.models import FlextModels        # ❌
```

Cross-package imports (from other packages):

```python
# CORRECT — import alias from package root
from flext_core import c, m, r, t, u, e, h, d, p, s, x

# WRONG — reach into internal modules from outside
from flext_core.result import FlextResult  # ❌
from flext_core.constants import FlextConstants  # ❌
```

Each project exports its own `m`:

```python
from flext_ldif import m   # gives FlextLdifModels
from flext_cli import m    # gives FlextCliModels
from flext_ldap import m   # gives FlextLdapModels
```

### Namespaced Composition (usage pattern)

```python
m.Entry           # model access
r[bool].ok(True)  # result creation
t.GeneralValueType  # type alias
c.Errors.VALIDATION_ERROR  # constant access
e.BaseError       # exception access
```

### Cross-Project Namespace Inheritance (CRITICAL)

Every downstream project **inherits** its parent project's facade class, NOT `FlextModels`/`FlextProtocols` directly. This gives automatic access to all parent namespaces via MRO — no re-declaration, no aliasing, no duplication.

**The pattern applies to ALL aliases: `m`, `c`, `t`, `u`, `p`.**

```python
# flext-target-oracle/src/flext_target_oracle/models.py
from flext_meltano import FlextMeltanoModels
from pydantic import Field

class FlextTargetOracleModels(FlextMeltanoModels):  # ← inherits, NOT FlextModels
    """m.Meltano.* inherited via MRO. m.TargetOracle.* defined here."""

    class TargetOracle:
        """Domain-specific models for Oracle target."""

        class ExecuteResult(FlextMeltanoModels.ArbitraryTypesModel):
            name: str = Field(description="Target name")

m = FlextTargetOracleModels
# m.Meltano.SingerSchemaMessage  → inherited from FlextMeltanoModels
# m.TargetOracle.ExecuteResult   → defined locally
# m.ArbitraryTypesModel          → inherited via chain
```

**Same pattern for protocols, types, utilities, constants:**

```python
# protocols.py
from flext_meltano.protocols import FlextMeltanoProtocols

class FlextTargetOracleProtocols(FlextMeltanoProtocols):
    class TargetOracle:
        class MyProtocol(Protocol): ...

p = FlextTargetOracleProtocols
# p.Meltano.* inherited, p.TargetOracle.* local
```

**Runtime code only imports the local alias:**

```python
from .models import m    # ONLY import needed — gives m.Meltano.*, m.TargetOracle.*
from flext_core import r  # result alias

schema = m.Meltano.SingerSchemaMessage.model_validate(data)
config = m.TargetOracle.ExecuteResult(name="oracle")
result = r[bool].ok(True)
```

**Why inheritance (not assignment or subclass-per-type):**

| Approach | Result |
|----------|--------|
| `Meltano = FlextMeltanoModels.Meltano` | ❌ mypy `name-defined` with `from __future__ import annotations` |
| `class Meltano:` + per-type subclasses | ❌ Invariance errors — `list[SubType]` ≠ `list[ParentType]` |
| `class Meltano(FlextMeltanoModels.Meltano):` | ✅ Works but redundant if parent is inherited |
| `class Models(FlextMeltanoModels):` (top-level) | ✅ **Correct** — clean MRO, zero duplication, exact types |

**Anti-patterns (NEVER do these):**

```python
# ❌ Import separate aliases — creates duplicate surfaces
from flext_meltano import FlextMeltanoModels as m_meltano

# ❌ Assign individual classes — mypy rejects as types
class Meltano:
    SingerSchemaMessage = FlextMeltanoModels.Meltano.SingerSchemaMessage  # not valid-type

# ❌ Inherit FlextModels instead of parent project
class FlextTargetOracleModels(FlextModels):  # loses m.Meltano.* namespace
```

### Workspace Project Dependency Map (CRITICAL — Domain Boundaries)

The workspace contains **distinct domain projects**. Do NOT confuse them. Each serves a different system and has its own models namespace.

#### Domain Layer Projects (provide `m.<Domain>.*` namespaces)

| Project | Models Class | Namespace | Domain | NOT the same as |
|---------|-------------|-----------|--------|-----------------|
| `flext-core` | `FlextModels` | `m.Base`, `m.Entity`, `m.Cqrs`, etc. | Framework primitives | — |
| `flext-meltano` | `FlextMeltanoModels` | `m.Meltano.*` | Singer/Meltano pipeline protocol | — |
| `flext-db-oracle` | `FlextDbOracleModels` | `m.DbOracle.*` | Oracle **Database** connectivity | `flext-oracle-wms` |
| `flext-oracle-wms` | `FlextOracleWmsModels` | `m.OracleWms.*` | Oracle **WMS** (Warehouse Management System) | `flext-db-oracle` |
| `flext-ldap` | `FlextLdapModels` | `m.Ldap.*` | LDAP directory operations | — |
| `flext-ldif` | `FlextLdifModels` | `m.Ldif.*` | LDIF file operations | — |

#### Integration Layer Projects (inherit from domain layers)

Each target/tap/dbt project inherits from the domain layers it **actually uses**:

| Project | Inherits From | Why |
|---------|--------------|-----|
| `flext-target-oracle-wms` | `FlextMeltanoModels, FlextOracleWmsModels` | Singer target loading into Oracle **WMS** |
| `flext-tap-oracle-wms` | `FlextMeltanoModels, FlextOracleWmsModels` | Singer tap extracting from Oracle **WMS** |
| `flext-dbt-oracle-wms` | `FlextMeltanoModels, FlextOracleWmsModels` | DBT transforms for Oracle **WMS** |
| `flext-target-oracle` | `FlextMeltanoModels, FlextDbOracleModels` | Singer target loading into Oracle **Database** |
| `flext-tap-oracle` | `FlextMeltanoModels, FlextDbOracleModels` | Singer tap extracting from Oracle **Database** |
| `flext-dbt-oracle` | `FlextMeltanoModels, FlextDbOracleModels` | DBT transforms for Oracle **Database** |
| `flext-target-ldap` | `FlextMeltanoModels, FlextLdapModels` | Singer target loading into LDAP |
| `flext-tap-ldap` | `FlextMeltanoModels, FlextLdapModels` | Singer tap extracting from LDAP |
| `flext-dbt-ldap` | `FlextMeltanoModels, FlextLdapModels` | DBT transforms for LDAP |
| `flext-target-ldif` | `FlextMeltanoModels, FlextLdifModels` | Singer target writing LDIF files |
| `flext-tap-ldif` | `FlextMeltanoModels, FlextLdifModels` | Singer tap reading LDIF files |
| `flext-dbt-ldif` | `FlextMeltanoModels, FlextLdifModels` | DBT transforms for LDIF |
| `flext-target-oracle-oic` | `FlextMeltanoModels, FlextDbOracleModels` | Singer target for Oracle OIC |
| `flext-tap-oracle-oic` | `FlextMeltanoModels, FlextDbOracleModels` | Singer tap from Oracle OIC |

#### Concrete Inheritance Example

```python
# flext-target-oracle-wms/src/flext_target_oracle_wms/models.py
from flext_meltano.models import FlextMeltanoModels
from flext_oracle_wms.wms_models import FlextOracleWmsModels

class FlextTargetOracleWmsModels(FlextMeltanoModels, FlextOracleWmsModels):
    class TargetOracleWms:
        class WmsTargetConfig(FlextMeltanoModels.ArbitraryTypesModel):
            ...

m = FlextTargetOracleWmsModels
# m.Meltano.SingerSchemaMessage  → from FlextMeltanoModels
# m.OracleWms.Entity             → from FlextOracleWmsModels (NOT FlextDbOracleModels!)
# m.TargetOracleWms.WmsTargetConfig → defined locally
```

#### NEVER Confuse These

| If the project name contains... | It uses... | NOT... |
|---------------------------------|-----------|--------|
| `oracle-wms` | `FlextOracleWmsModels` (Warehouse Management) | `FlextDbOracleModels` (Database) |
| `oracle` (without `-wms`) | `FlextDbOracleModels` (Database) | `FlextOracleWmsModels` (WMS) |
| `ldap` | `FlextLdapModels` | `FlextLdifModels` |
| `ldif` | `FlextLdifModels` | `FlextLdapModels` |

### Complete Alias Map (flext-core)

| Alias | Full Class | Module |
|-------|-----------|--------|
| `c` | `FlextConstants` | `constants.py` |
| `d` | `FlextDecorators` | `decorators.py` |
| `e` | `FlextExceptions` | `exceptions.py` |
| `h` | `FlextHandlers` | `handlers.py` |
| `m` | `FlextModels` | `models.py` |
| `p` | `FlextProtocols` | `protocols.py` |
| `r` | `FlextResult` | `result.py` |
| `s` | `FlextService` | `service.py` |
| `t` | `FlextTypes` | `typings.py` |
| `u` | `FlextUtilities` | `utilities.py` |
| `x` | `FlextMixins` | `mixins.py` |

### Prohibited Actions

- **Never** remove alias definitions (`c = FlextConstants`) from module files.
- **Never** remove alias re-exports from `__init__.py`.
- **Never** replace alias imports with full class name imports.
- **Never** rename or reassign aliases.
- **NEVER** define secondary or backward compatibility aliases (e.g., `m_core = FlextModels`, `User = Auth.User`, `class LegacyModel(NewModel):`). Use exactly one namespace alias (`m`, `c`, `t`, `p`) per file.
- **NEVER** use `__init_subclass__` to warn about subclassing or generate dynamic references. The architecture relies on clean Pydantic v2 inheritance without metaclass magic.
- **NEVER** use `cast()`, `isinstance()` for primitive type conversions, or `Optional`/`dict` for business logic models. Use Pydantic v2 validation via `m.*` models and `FlextResult`.

## `__init__.py` Rules

`__init__.py` files contain **exports only**. No logic, no stubs, no placeholders, no fallbacks, no runtime code.

Allowed content:

```python
# Re-exports and __all__ only
from flext_core.constants import FlextConstants, c
from flext_core.models import FlextModels, m
# ...
__all__ = ["FlextConstants", "c", "FlextModels", "m", ...]
```

Prohibited content:

- Function/method definitions
- Class definitions
- Conditional logic (`if`, `try/except`)
- Stubs or placeholder implementations
- Fallback imports with error suppression
- Any runtime computation

## One Class Per Module

Each public facade module contains exactly one primary class. No multi-class modules. The alias at the bottom refers to that single class.

## Skill System Contract

- Skills are discovered only from `.claude/skills/*/rules.yml`.
- Rule schema uses flat fix keys only: `fix_auto`, `fix_type`, `fix_file`, `fix_script`, `fix_instruction`, `fix_description`.
- Nested `fix:` metadata in `rules.yml` is invalid for `skill_validate.py`/`skill_fix.py` orchestration.
- `fix_auto: true` must resolve to an executable fix mechanism and existing target file/script.
- Prefer `type: ast-grep` rules. Use `type: custom` only when AST-based detection is not applicable.

## Make Automation Contract

All automation runs through Make verbs. Scripts are implementation details behind Make; never recommend ad-hoc script invocations as the primary workflow.

### Workspace Verbs (root `Makefile`)

Allowed verbs only: `setup`, `check`, `security`, `format`, `docs`, `test`, `validate`, `typings`, `clean`.

No extra workspace targets are guaranteed; validate against root `Makefile` before citing any verb.

### Project Verbs (per-project `base.mk`)

Allowed verbs only: `setup`, `check`, `security`, `format`, `docs`, `test`, `validate`, `clean`.

Do not add aliases or secondary verbs in project `base.mk` surfaces. Preflight alignment is mandatory: all standardized project verbs must run under workspace venv enforcement.

### Parameters

Selection parameters (root orchestrator):

| Parameter | Example | Purpose |
|-----------|---------|---------|
| `PROJECT=<name>` | `make check PROJECT=flext-core` | Run for exactly one project |
| `PROJECTS="p1 p2"` | `make test PROJECTS="flext-core flext-ldif"` | Run for a list of projects |

Execution parameters (root orchestrator):

| Parameter | Example | Purpose |
|-----------|---------|---------|
| `FAIL_FAST=1` | `make check FAIL_FAST=1` | Stop on first project failure |
| `JOBS=<n>` | `make test JOBS=4` | Parallelize per-project execution where safe |

Gate parameters (passed through to `base.mk`):

| Parameter | Example | Purpose |
|-----------|---------|---------|
| `CHECK_GATES=lint,format,type,security` | `make check CHECK_GATES=lint,type` | Select which check gates to run |
| `VALIDATE_GATES=complexity,docstring` | `make validate VALIDATE_GATES=complexity` | Select which validate gates to run |
| `PYTEST_ARGS="..."` | `make test PYTEST_ARGS="-x -k auth"` | Pass-through pytest arguments |
| `FIX=1` | `make validate FIX=1` | Enable auto-fix before validation |
| `VERBOSE=1` | `make check VERBOSE=1` | Verbose output |

Workspace-scope parameters (root `Makefile` only):

| Parameter | Values | Purpose |
|-----------|--------|---------|
| `VALIDATE_SCOPE=project\|workspace` | Default: `project` | `project`: per-project validate gates. `workspace`: repository-level inventory/wiring/skill validation |
| `DEPS_REPORT=0` | Omit to enable | Skip writing dependency/typing report after `make upgrade` or `make typings` |

Strictness policy:

- No `SKIP_*` or "disable gate" toggles. Parameters must be selectors and performance toggles only.
- CI must run defaults (full strict behavior). Parameterized selection is for local development convenience.

### Exit Code Contract

- `0` pass
- `1` policy failure
- `2` usage/configuration error
- `3` infrastructure/runtime error

### Reporting and Artifacts

- Validation reports are machine-readable JSON artifacts.
- Dependency and typing reports live under `.reports/dependencies/` (produced by `make upgrade` and `make typings` unless `DEPS_REPORT=0`). Stub supply-chain report: `.reports/validate/stub-supply-chain.json`.
- Workspace validation artifacts (e.g. scripts inventory) must live under `.reports/` when produced by `make validate VALIDATE_SCOPE=workspace`.
- Skill-local reports remain under `.claude/skills/<skill>/report.json` and `.claude/skills/<skill>/fix-report.json`.
- Reports must include explicit next actions (`TODO: make PROJECT=<name> <target>`) for every failed gate.

### Maintenance and standard places

All routine maintenance runs via Make; no ad-hoc script invocations as the primary workflow.

- **Dependency and typing reports**: `make upgrade` (after successful upgrade) and `make typings` (after stub supply-chain) run `detect_runtime_dev_deps.py` and write `.reports/dependencies/detect-runtime-dev-latest.json`. Use `DEPS_REPORT=0` to skip the report step.
- **Standard locations**: Root `Makefile` (verbs and parameters); `base.mk` (per-project verbs); `scripts/dependencies/` (detection scripts, `dependency_limits.toml`); `.reports/dependencies/` (dependency/typing reports); `.reports/validate/` (validation/stub reports). Per-project config stays in each project’s `pyproject.toml` and optional `Makefile` including `base.mk`.

## AST-Grep First and Script Locality

- Prefer `ast-grep` for detection and mechanical rewrites whenever feasible.
- Use `custom` rules only when AST matching cannot express the constraint.
- Custom rule scripts must live inside the owning skill folder (for example, `.claude/skills/<skill>/...`).
- `scripts/core` is reserved for generic orchestrators and shared infra only (`skill_validate.py`, `skill_fix.py`, `stub_supply_chain.py`, and shared helpers).
- Do not add skill-specific fix/validation logic under `scripts/core`.

## Typing Supply Chain Rules

- Manual stubs belong in `typings/`.
- Generated stubs belong in `typings/generated/`.
- Generated stubs are for third-party dependencies only.
- Never generate stubs for internal FLEXT modules (`flext_*`, `flext_*`, `flext_*`).
- Internal missing imports are source/type architecture defects and must be fixed in code, not stubbed.

## Workspace Virtual Environment

The workspace prefers a single shared `.venv` at the repository root. Project-local `.venv` is a fallback mode only when workspace `.venv` is unavailable for project-scoped commands.

- All `pip install`, `python`, and tool invocations must use an active managed venv (`.venv/bin/` in workspace mode, or project `.venv/bin/` in fallback mode).
- Never install packages with system `pip`. System Python is blocked by PEP 668.
- In workspace mode, Poetry uses `POETRY_VIRTUALENVS_CREATE=false` and `POETRY_VIRTUALENVS_IN_PROJECT=false`.
- In fallback mode (workspace `.venv` missing for project-scoped run), Poetry uses project-local `.venv` with in-project creation enabled.
- When workspace `.venv` exists, preflight must remove project-local `.venv` directories.
- Never destructively delete project `.venv` during preflight when workspace `.venv` is missing and fallback mode is active.
- `make setup` and `make upgrade` automatically run `modernize_pyproject.py` + `pyproject-fmt` before lock/install.

## pyproject.toml Hygiene

All `pyproject.toml` files must follow Poetry 2.x + PEP 621 modern standards. `make setup` and `make upgrade` enforce this automatically via `scripts/dependencies/modernize_pyproject.py`.

Required invariants:

- `[project.license]` must be a PEP 639 SPDX string (e.g., `license = "MIT"`), never a table.
- No `License ::` classifiers. License is declared solely via `[project.license]`.
- No test dependencies (`pytest`, `faker`, `factory-boy`, `hypothesis`, `pytest-*`) in `[project.dependencies]`. Test deps belong in `[tool.poetry.group.dev.dependencies]` or `[project.optional-dependencies.test]`.
- No duplicate metadata between `[project]` and `[tool.poetry]`. `name`, `version`, `description`, `authors`, `readme`, `license` must be in `[project]` only.
- `pyproject-fmt` is the canonical formatter for `pyproject.toml` files (except files with `[[tool.pyrefly.sub-config]]` which it corrupts).
- `poetry check` must pass with zero warnings for every project.
- **Coverage source of truth**: `[tool.coverage.report] fail_under` in each project's `pyproject.toml` is the single source of truth for coverage thresholds. No `MIN_COVERAGE` or `COV_DIR` in Makefiles. `base.mk` uses `--cov` which reads from `[tool.coverage]`.
- No `--cov*` flags in `[tool.pytest.ini_options] addopts`. Coverage config is owned by `[tool.coverage]` only.
- Forbidden legacy threshold patterns outside `pyproject.toml`: `--cov-fail-under`, `MIN_COVERAGE`, `MIN_COVERAGE_DEFAULT`.
- `make validate VALIDATE_SCOPE=workspace` must fail fast when forbidden threshold patterns or pyproject drift are detected.

### Workspace anti-drift gate

- Run `make validate VALIDATE_SCOPE=workspace` before completion claims on policy/automation changes.
- Workspace gate executes with workspace `.venv` and includes:
  - scripts inventory generation
  - strict skill validation (`scripts-validation`, `rules-github`, `rules-docker`)
  - `scripts/dependencies/modernize_pyproject.py --audit`

## Required Preflight for Workspace Loops

Before any workspace-wide loop (`make setup`, `make check`, `make security`, `make format`, `make docs`, `make test`, `make validate`, `make typings`, `make clean`):

- Ensure workspace virtualenv exists at `.venv`.
- If missing, fail immediately.
- Ensure no project-local `.venv` directories remain (remove them in preflight).

Before any project-scoped loop (run from inside a project):

- Prefer workspace `.venv` when available.
- If workspace `.venv` is missing, fall back to project-local `.venv`.
- In fallback, require `make setup` in that project before `make check`/`make validate`/`make test`.

## Change Management

- Root-cause fixes only; no temporary mitigation paths.
- Keep changes minimal, explicit, and verifiable.
- Validate behavior with direct command evidence after every change.
- If policy and implementation diverge, update this file first, then sync skill documents.
- Never change lint behavior (rule sets, ignores, severity, or gate semantics) without explicit user discussion and approval in the current session.
- When the user provides a correction that changes governance or workflow policy, record it immediately in `CLAUDE.md` in the relevant section before continuing implementation.

## Code Instrumentation Minimum Standard

- Configure logging once at bootstrap with `FlextRuntime.configure_structlog(...)`.
- Create loggers through `FlextLogger.create_module_logger(__name__)` or `FlextLogger.for_container(...)`.
- Do not use `structlog.get_logger()` directly in project code.
- Bind contextual fields using `FlextLogger.Context` (`bind_global_context`, `scoped_context`, `unbind_global_context`).
- Instrument start/success/failure boundaries of integrations and service operations with structured fields (operation, component, correlation_id, duration_ms, outcome).
- Keep context lifecycle explicit to avoid leakage across requests/jobs.
- For fallible flows, preserve typed boundaries (`FlextResult`) and log at boundary transitions, not with ad-hoc dict envelopes.

Required instrumentation verification:

- `make validate PROJECT=flext-core`
- `make validate PROJECT=flext-core FIX=1` (when automated fixes are required before validation)
- `make validate PROJECTS="flext-core flext-api"` (when instrumentation affects cross-project usage)

## Skills Usage Baseline

- Skills are located under `.claude/skills/*/SKILL.md`.
- List available skills: `ls .claude/skills/*/SKILL.md`.
- Discover skills quickly by name: `rg -n "^name:|^description:" .claude/skills/*/SKILL.md`.
- Start from `CLAUDE.md`, then load path-specific rules skill first (for example `rules-flext-core` for `flext-core/`, `rules-scripts` for `scripts/`).
- After rules skill, load the needed library/pattern skill (`lib-structlog`, `lib-pydantic-v2`, `flext-patterns`, etc.).
- Do not implement from memory when a relevant skill exists; read the skill file first and follow its verification commands.

Minimal skill-driven workflow:

1. Identify touched path.
2. Load matching `rules-*` skill.
3. Load supporting `lib-*`/pattern skills.
4. Implement minimally with reuse-first policy.
5. Run the corresponding Make verbs for touched scope.

## Skill Enforcement and Fast Context Lookup

Strict load order:

- Rules skill first for touched path, always.
- Supporting skills second (`lib-*`, `scripts-*`, `flext-*`, `python-*`).
- No implementation before reading the selected skill files.
- No lib-first flow when a path rules skill exists.

Mandatory path to skill mapping:

- `flext-core/` -> `rules-flext-core` -> `flext-patterns`, `flext-architecture-layers`, `flext-import-rules`, `flext-type-system`, `lib-returns`, `lib-structlog`, `lib-pydantic-v2`, `lib-dependency-injector`
- `scripts/` -> `rules-scripts` -> `scripts-infra`, `scripts-validation`, `scripts-maintenance`, `scripts-testing`, `scripts-architecture`, `scripts-dependencies`, `scripts-security`
- `docs/` -> `rules-docs` -> `flext-docs-pointer-policy`, `skill-format-universal`
- `typings/` -> `rules-typings` -> `flext-strict-typing`, `flext-type-system`, `python-modern-type-syntax`, `python-313-typing`
- `Makefile` and `base.mk` -> `flext-development-workflow`, `flext-quality-gates`, `workspace-maintenance`
- `pkg/` -> `rules-pkg`
- `src/` -> `rules-src`
- `cmd/` -> `rules-cmd`
- `docker/` -> `rules-docker`
- `examples/` -> `rules-examples`
- `.github/` -> `rules-github`

Fast context protocol:

1. Identify touched path and dependency surface.
2. Load the mapped rules skill and read anchors in its references.
3. Load only the minimum supporting skills needed for this change.
4. Reuse nearest in-repo pattern anchors before writing new structure.
5. Validate with current root Make verbs (`make check`, `make validate`, `make test`) or project-level gates in `base.mk`.

Forbidden skill usage behavior:

- Do not skip rules skill for a touched path that has one.
- Do not claim a skill is used without reading its `SKILL.md`.
- Do not cite patterns that are not anchored in referenced files.
- Do not cite non-existent Make verbs; verify with current `Makefile` and `base.mk` first.
