# Plan: Standardize Settings, Logging, and Services (v2)

## Goal
Eliminate settings duplication across `models.py` and `settings.py`, canonicalize logging, and align services — all via deletion + MRO composition, never via new wrappers.

## Brutal Preflight

1. **Recurring failure risk**: Creating a new base mixin or abstract class to "share" fields between models and settings.
2. **Stop-rule**: AGENTS.md §0.0R item 4 — "New helper/proxy/wrapper/carrier model without zero-origin proof is invalid."
3. **Primitive**: Delete duplicate; settings lives ONLY in `settings.py`; models gets an alias or nothing.
4. **Propagation**: `grep -rn 'FlextDbtOracleSettings' flext-dbt-oracle/src`; `sg` for callers.
5. **Gate**: `ruff check <file>` + `pyrefly check <file>` + `pytest flext-dbt-oracle/tests/`.

## Current State

### Settings Duplication (SSOT Violation)

| Project | `models.py` | `settings.py` | Issue |
|---------|-------------|---------------|-------|
| `flext-dbt-oracle` | `FlextDbtOracleSettings(m.Value)` with ~30 fields | `FlextDbtOracleSettings(FlextSettings, m.DbtOracle...)` with same ~30 fields | **Exact byte-a-byte duplication** |
| `flext-dbt-oracle-wms` | `FlextDbtOracleWmsSettings(FlextSettings)` | `FlextDbtOracleWmsSettings(FlextSettings)` | **Same name, same registry ns** — last import wins silently |

Root cause: Settings defined in `models.py` AND `settings.py`. This violates namespace separation: `m.*` = models, `s.*` = settings. A settings class is NOT a model; it is a `BaseSettings` singleton.

## Canonical Pattern

```python
# settings.py — SOLE owner of the settings schema
@FlextSettings.auto_register("dbt_oracle")
class FlextDbtOracleSettings(FlextSettings):
    model_config = ConfigDict(env_prefix="FLEXT_DBT_ORACLE_", extra="ignore")
    oracle_host: Annotated[str, u.Field(description="Oracle host")] = (
        c.DbtOracle.DEFAULT_HOST
    )
    ...


# models.py — NO concrete settings class. If consumers need type reference:
class FlextDbtOracleModels(...):
    class DbtOracle:
        # Alias only, zero duplication
        FlextDbtOracleSettings = flext_dbt_oracle.settings.FlextDbtOracleSettings
```

**Rule**: `FlextSettings` is the ONLY base for all settings. Never inherit `m.Value`, `BaseModel`, or any concrete model class alongside `FlextSettings`. Settings fields live in exactly one file: `settings.py`.

## Phase 1: Kill Settings Duplication

### 1.1 `flext-dbt-oracle`
- **Delete** `FlextDbtOracleModels.DbtOracle.FlextDbtOracleSettings` from `models.py` (~180 LOC)
- **Verify** `settings.py` already has identical fields (it does)
- **Add alias** in `models.py` only if `grep` proves callers use `m.DbtOracle.FlextDbtOracleSettings`
- **Propagate** any broken imports

### 1.2 `flext-dbt-oracle-wms`
- **Delete** `FlextDbtOracleWmsModels.DbtOracleWms.FlextDbtOracleWmsSettings` from `models.py`
- **Verify** `settings.py` has the canonical class
- **Check registry** — ensure `auto_register("dbt-oracle-wms")` is only in `settings.py`

### 1.3 Audit remaining projects
```bash
grep -rn "class .*Settings(" flext-*/src/flext_*/models.py
```
Any hit = candidate for deletion.

## Phase 2: Logging Canonicalization (Mechanical)

**Rule**: Every module uses `logger = u.create_module_logger(__name__)` at top-level.
- No `structlog.get_logger()` directly.
- No `logging.getLogger()` directly.
- Bootstrap calls `u.configure_structlog()` once.

Script: `grep -rn "structlog.get_logger\|logging.getLogger" flext-*/src/` → report + auto-fix.

## Phase 3: Services — Remove Accessor Methods

**Rule**: Services inherit `FlextService[T]` (alias `s[T]`). No `get_`, `set_`, `is_` methods.
- Use `computed_field` for derived state exposed to consumers.
- Use `model_copy(update=...)` for mutations.
- Use `PrivateAttr` for internal runtime state.

Script: `grep -rn "def get_\|def set_\|def is_" flext-*/src/flext_*/services/` → report.

## Phase 4: MRO Namespace Guard

Verify every project has exactly one `Flext<Project>Settings` in `settings.py` and zero in `models.py`.

## First Edit

**Offender**: `flext-dbt-oracle/src/flext_dbt_oracle/models.py:196`
**Primitive**: Delete duplicated `FlextDbtOracleSettings` class; replace with alias if referenced.
**Propagation**: `grep -rn "FlextDbtOracleSettings" flext-dbt-oracle/src/`
**Gate1**: `ruff check flext-dbt-oracle/src/flext_dbt_oracle/models.py`
**Gate2**: `pyrefly check flext-dbt-oracle/src/flext_dbt_oracle/models.py`
**Test**: `pytest flext-dbt-oracle/tests/`
