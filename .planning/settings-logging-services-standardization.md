# Plan: Standardize Settings, Logging, and Services Across FLEXT Monorepo

## Goal
Bring all 35+ projects into canonical alignment with AGENTS.md §2, §3, pydantic-settings skill, and flext-patterns skill — using Pydantic v2 advanced features, MRO namespace composition, and direct canonical access (no wrappers/aliases).

## Current State Analysis

### Settings
| Project | Inherits From | Issues |
|---------|---------------|--------|
| flext-core | `BaseSettings` | Canonical source — OK |
| flext-web | `FlextSettings` | OK |
| flext-auth | `FlextSettings` | OK |
| gruponos-meltano-native | `FlextSettings` | OK |
| algar-oud-mig | `FlextLdapSettings, FlextCliSettings` | Multi-parent OK (both FlextSettings) |
| flext-dbt-oracle | `FlextSettings, m.DbtOracle.FlextDbtOracleSettings` | **VIOLATION**: inherits concrete model — causes R4/R5 enforcement error |
| flext-dbt-oracle-wms | `FlextSettings` | OK after fixes |
| flext-oracle-oic | `FlextSettings` | OK |
| flext-target-oracle-oic | `FlextSettings` | OK |
| Many others | `FlextSettings` | Mostly OK; some missing descriptions |

**Key Finding**: ~3-5 projects still have settings that inherit from `m.Value` or concrete model classes alongside `FlextSettings`, violating R4/R5.

### Logging
- `flext-core` provides `FlextLogger` + `u.create_module_logger(__name__)` + `u.configure_structlog()`
- Many projects still use direct `structlog.get_logger()` or ad-hoc logging config
- Inconsistent context binding patterns

### Services
- `flext-core` provides `FlextService[T]` (alias `s`)
- Some projects follow `api.py + base.py + services/` pattern correctly (flext-web, algar-oud-mig)
- Others have monolithic service classes or skip the base mixin pattern
- Accessor methods (`get_`, `set_`) still present in some services

## Standardization Plan

### Phase 1: Settings Canonicalization (Automated via Script)

**Rule**: Every settings class MUST:
1. Inherit **only** `FlextSettings` (or other `Flext*Settings` that themselves inherit `FlextSettings`)
2. NEVER inherit `m.Value`, `BaseModel`, or any concrete model class
3. Use `@FlextSettings.auto_register("<ns>")` with project-specific namespace
4. Use `model_config = ConfigDict(env_prefix="FLEXT_<PROJECT>_", extra="ignore")`
5. Define every field with `Annotated[T, u.Field(description="...")]`
6. Source all defaults from `c.*` constants (no hardcoded literals)
7. Use `@u.computed_field` for derived values, `@u.model_validator(mode="after")` for cross-field checks

**Automation**: Write a Python script (`scripts/standardize_settings.py`) that:
- Scans all `*/src/*/settings.py`
- Detects non-`FlextSettings` bases
- Reports violations with exact file/line
- Auto-fixes simple cases (removes `m.Value` base, moves fields from model to settings)

### Phase 2: Logging Canonicalization

**Rule**: Every module MUST:
1. Use `logger = u.create_module_logger(__name__)` at module level
2. Never call `structlog.get_logger()` directly
3. Never configure structlog outside of `u.configure_structlog()` at bootstrap
4. Use `u.bind_global_context()` / `u.clear_global_context()` for request-scoped context

**Automation**: Script (`scripts/standardize_logging.py`) that:
- Greps for `structlog.get_logger` and `logging.getLogger` in `src/`
- Reports direct structlog/logging usage
- Auto-replaces with `u.create_module_logger(__name__)` where safe

### Phase 3: Services Canonicalization

**Rule**: Every service MUST:
1. Inherit from `FlextService[TResult]` (alias `s[TResult]`)
2. Implement `execute() -> p.Result[TResult]`
3. Follow `api.py + base.py + services/` facade pattern when exposing public API
4. NEVER use accessor methods (`get_`, `set_`, `is_`) — use `computed_field`, `model_copy(update=...)`, or direct field access
5. Use `PrivateAttr` for internal state, not custom `__init__` re-declarations

**Automation**: Script (`scripts/standardize_services.py`) that:
- Detects classes inheriting from non-service bases that should be services
- Finds `get_`/`set_` methods on service-like classes
- Reports `api.py` missing `base.py` or `services/` directory

### Phase 4: MRO Namespace Verification

**Rule**: Every project MUST have:
- `Flext<Project>Settings` in `settings.py`
- `Flext<Project>Models` in `models.py` (or `models/`)
- `Flext<Project>Utilities` in `utilities.py`
- `Flext<Project>Constants` in `constants.py`
- `Flext<Project>Protocols` in `protocols.py`
- `Flext<Project>Typings` in `typings.py`
- Test equivalents: `TestsFlext<Project><Tier>` in `tests/`

**Automation**: Script (`scripts/verify_mro_namespace.py`) that:
- Checks each project has all required facade classes
- Verifies naming follows `Flext<Project><Tier>` pattern
- Reports missing or misnamed classes

## Implementation Order

1. **Script infrastructure** — Create the 4 audit/fix scripts in `scripts/standardize/`
2. **Run audit** — Generate full report of all violations across 35 projects
3. **Fix settings violations first** — Highest impact, affects enforcement
4. **Fix logging** — Second priority, touches many files but changes are mechanical
5. **Fix services** — Third, requires more manual review for `get_`/`set_` renames
6. **MRO namespace cleanup** — Final pass, ensure all facades are named correctly

## First Edit Contract

- **Offender**: `flext-dbt-oracle/src/flext_dbt_oracle/settings.py` (R4/R5 violation)
- **Primitive**: Remove concrete model base, use Pydantic `SettingsConfigDict` + `Annotated` fields
- **Propagation**: `sg` / `grep` for `FlextDbtOracleSettings` usages
- **Gate1**: `ruff check flext-dbt-oracle/src/flext_dbt_oracle/settings.py`
- **Gate2**: `pyrefly check flext-dbt-oracle/src/flext_dbt_oracle/settings.py`
- **Test**: `pytest flext-dbt-oracle/tests/`
