<!-- TOC START -->

- [Scope](#scope)
  - [Subproject Usage Map](#subproject-usage-map)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---

name: lib-pydantic-settings
description: Pydantic SettingsConfigDict and singleton config patterns across FLEXT subprojects. Trigger when editing settings.py models, env bindings, or configuration validation behavior.

---

## Scope

- Core canonical implementation: `flext-core/src/flext_core/settings.py`
- Broad usage surface: `flext-*/src/*/settings.py`
- Representative consumers:
  - `flext-cli/src/flext_cli/settings.py`
  - `flext-meltano/src/flext_meltano/settings.py`
  - `flext-quality/src/flext_quality/settings.py`
  - `flext-api/src/flext_api/settings.py`
  - `flext-dbt-oracle/src/flext_dbt_oracle/settings.py`
- Dependency pinning: `flext-core/pyproject.toml`

### Subproject Usage Map

- `flext-core`: defines `FlextSettings` singleton + protocol integration + `AutoConfig` helper.
- `flext-cli`: `FlextCliSettings(FlextSettings)` with `SettingsConfigDict(env_prefix="FLEXT_CLI_", ...)`.
- `flext-meltano`: `FlextMeltanoSettings(FlextSettings)` with strict env-bound configuration.
- `flext-quality`: `FlextQualitySettings(FlextSettings)` for hook/rule/MCP settings.
- `flext-api`: `FlextApiSettings(BaseSettings)` with `FlextSettings.auto_register("api")`.
- `flext-dbt-oracle`: `FlextDbtOracleSettings(FlextSettings.AutoConfig)` for auto-configured namespace settings.

## References

- `AGENTS.md` — canonical governance source
- `flext-core/src/flext_core/settings.py`: `class FlextSettings`, `model_config`, `_instances`, `_lock`, `validate_configuration`, `AutoConfig`
- `flext-core/src/flext_core/_utilities/configuration.py`: env-file compatibility notes for `SettingsConfigDict`
- `flext-cli/src/flext_cli/settings.py`: real namespaced settings extension
- `flext-meltano/src/flext_meltano/settings.py`: extended SettingsConfigDict usage
- `flext-api/src/flext_api/settings.py`: direct `BaseSettings` subclass pattern in subproject
- `flext-core/pyproject.toml`: `pydantic-settings>=2.10.1`
- `https://docs.pydantic.dev/latest/concepts/pydantic_settings/`
- `https://github.com/pydantic/pydantic-settings`

## Rules

- Always use `SettingsConfigDict` for settings models; do not use legacy `class Config`.
- Always define `env_prefix` explicitly in each settings class.
- Keep env parsing conventions explicit (`env_nested_delimiter`, `env_file`, `case_sensitive`, `extra`).
- Keep singleton semantics thread-safe when implementing global configuration (`_instances` + `_lock`).
- Use `@model_validator(mode="after")` for cross-field consistency checks.
- Preserve source priority assumptions unless intentionally overridden:
  - init kwargs > environment variables > dotenv/env_file > secrets > field defaults
- Keep `validate_assignment=True` in settings where runtime mutation safety matters.
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, `cast()`, and `inline imports`. Wait for definition time or use Protocol decoupling.
## Instructions

- Use these canonical declarations as baseline:

```python
# flext-core/src/flext_core/settings.py

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

class FlextSettings(p.ProtocolSettings, p.Settings, FlextRuntime):
    _instances: ClassVar[Mapping[type[BaseSettings], BaseSettings]] = {}
    _lock: ClassVar[threading.RLock] = threading.RLock()

    model_config = SettingsConfigDict(
        env_prefix=c.ENV_PREFIX,
        env_nested_delimiter=c.ENV_NESTED_DELIMITER,
        env_file=u.resolve_env_file(),
        env_file_encoding=c.DEFAULT_ENCODING,
        case_sensitive=False,
        extra=c.EXTRA_IGNORE,
        validate_assignment=True,
    )
```

```python
# key declarations in flext-core settings
@model_validator(mode="after")
def validate_configuration(self) -> Self: ...


class AutoConfig(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        extra="forbid",
    )
```

- Preserve real field patterns from `FlextSettings` for compatibility:
  - `app_name: str`
  - `version: str`
  - `debug: bool`
  - `trace: bool`
  - `log_level: c.LogLevel`
  - `database_url: str`
  - `database_pool_size: int`
- Import pattern to prefer in settings files:
  - `from pydantic_settings import BaseSettings, SettingsConfigDict`
  - `from pydantic import Field, model_validator` (and related validators).

## Workflow

1. Inspect nearest `settings.py` and match local project conventions.
2. Ensure `model_config = SettingsConfigDict(...)` is present and explicit.
3. Keep namespace-level env prefix stable (for example `FLEXT_CLI_`, `FLEXT_MELTANO_`).
4. Preserve/introduce post-init validation with `@model_validator(mode="after")` where cross-field constraints exist.
5. For globally shared settings, keep singleton lock/registry thread-safe.
6. Verify no new legacy `class Config` blocks are introduced.

## Examples

Good:

```python
model_config = SettingsConfigDict(
    env_prefix="FLEXT_CLI_",
    env_file=u.resolve_env_file(),
    env_file_encoding="utf-8",
    extra="ignore",
)
```

Why good: explicit env namespace and dotenv resolution keep runtime behavior predictable.

Bad:

```python
class Config:
    env_prefix = "FLEXT_CLI_"
```

Why bad: legacy Pydantic v1 configuration style conflicts with project standard using `SettingsConfigDict`.

Good:

```python
@model_validator(mode="after")
def validate_configuration(self) -> Self:
    if self.trace and not self.debug:
        raise ValueError("Trace mode requires debug mode")
    return self
```

Why good: enforces cross-field invariants at model boundary.

Bad:

```python
def set_trace_mode(self, enabled: bool) -> None:
    self.trace = enabled
    # no invariant check against debug
```

Why bad: allows invalid state mutation when assignment validation/invariants are bypassed.

Good:

```python
_instances: ClassVar[Mapping[type[BaseSettings], BaseSettings]] = {}
_lock: ClassVar[threading.RLock] = threading.RLock()
```

Why good: thread-safe singleton storage for globally shared settings model.

## Verification

Make gates:

- `make check PROJECT=flext-core CHECK_GATES=type` — type-check settings models
- `make test PROJECT=flext-core` — settings singleton and validation tests
- `make validate PROJECT=flext-core` — complexity + docstring gates

Pattern checks:

- `rg -n "class FlextSettings|_instances: ClassVar\[dict\[type\[BaseSettings\], BaseSettings\]\]|_lock: ClassVar\[threading\.RLock\]|model_config = SettingsConfigDict\(" flext-core/src/flext_core/settings.py`
- `rg -n "@model_validator\(mode=\"after\"\)|class AutoConfig\(BaseModel\)|ConfigDict\(" flext-core/src/flext_core/settings.py`
- `rg -n "class .*Settings|SettingsConfigDict\(" --glob "**/settings.py" flext-core flext-*`
- `rg -n "class Config:" --glob "**/settings.py" flext-core flext-*`
- `rg -n "pydantic-settings>=2\.10\.1" flext-core/pyproject.toml`
