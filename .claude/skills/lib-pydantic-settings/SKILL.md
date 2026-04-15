---

name: lib-pydantic-settings
description: Pydantic ConfigDict and singleton settings patterns across FLEXT subprojects. Use when editing settings.py models, env bindings, or configuration validation behavior.
triggers:
  - editing settings.py models or env bindings
  - configuring ConfigDict for settings classes
  - implementing singleton settings patterns
  - debugging environment variable resolution
  - adding namespace registration to FlextSettings

---

<!-- TOC START -->

- [Scope](#scope)
  - [Subproject Usage Map](#subproject-usage-map)
- [References](#references)
- [Rules](#rules)
- [Forbidden Patterns](#forbidden-patterns)
- [Instructions](#instructions)
- [MRO Composition](#mro-composition)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

**Reviewed**: 2026-04-05 | **Scope**: MRO composition, auto-MRO env sources, forbidden patterns

## Scope

- Core canonical implementation: `flext-core/src/flext_core/settings.py`
- Governance: `AGENTS.md` §2.6 Settings Law
- Broad usage surface: `flext-*/src/*/settings.py`
- Representative consumers:
  - `flext-cli/src/flext_cli/settings.py`
  - `flext-meltano/src/flext_meltano/settings.py`
  - `flext-quality/src/flext_quality/settings.py`
  - `flext-api/src/flext_api/settings.py`
  - `flext-auth/src/flext_auth/settings.py`
  - `flext-db-oracle/src/flext_db_oracle/settings.py`
- Dependency pinning: `flext-core/pyproject.toml`

### Subproject Usage Map

- `flext-core`: defines `FlextSettings` singleton + `settings_customise_sources` auto-MRO + `AutoConfig` helper.
- `flext-cli`: `FlextCliSettings(FlextSettings)` with `@FlextSettings.auto_register("cli")`.
- `flext-meltano`: `FlextMeltanoSettings(FlextSettings)` with strict env-bound configuration.
- `flext-quality`: `FlextQualitySettings(FlextSettings)` for hook/rule/MCP settings.
- `flext-api`: `FlextApiSettings(FlextSettings)` with `@FlextSettings.auto_register("api")`.
- `flext-auth`: `FlextAuthSettings(FlextSettings)` with `@FlextSettings.auto_register("auth")`.
- `flext-db-oracle`: `FlextDbOracleSettings(FlextSettings)` with `env_prefix="ORACLE_"`.

## References

- `AGENTS.md` §2.6 Settings Law — canonical governance source
- `flext-core/src/flext_core/settings.py`: `FlextSettings`, `settings_customise_sources`, `_normalize_log_level`
- `flext-core/src/flext_core/_utilities/configuration.py`: `resolve_env_file()`
- `pydantic-settings>=2.10.1`

## Rules

- ALL settings classes MUST inherit `FlextSettings` — never `BaseSettings`, `m.Value`, or `BaseModel`.
- Always define `model_config = ConfigDict(env_prefix="FLEXT_<PROJECT>_", extra="ignore")`.
- ALL field defaults MUST come from `c.*` constants — no hardcoded values.
- Use `@FlextSettings.auto_register("<namespace>")` for namespace registration.
- Use `@model_validator(mode="after")` for cross-field consistency checks.
- Singleton via FlextSettings `__new__()` only — no custom singleton patterns.

## Forbidden Patterns

- `os.environ`, `os.getenv`, `environ.get()` in `src/` code — use FlextSettings env resolution
- `m.Value` or `BaseSettings` as settings base class — use `FlextSettings`
- Custom `_global_instance` or `get_or_create_global()` singleton — use inherited `get_global()`
- Hardcoded defaults (`"utf-8"`, `30`, `True`) — use `c.*` constants
- Legacy `class Config:` — use `ConfigDict`
- `model_rebuild()`, `cast()`, inline imports

## Instructions

Canonical base class:

```python
class FlextSettings(BaseSettings):
    model_config = ConfigDict(
        env_prefix=c.ENV_PREFIX,
        env_nested_delimiter=c.ENV_NESTED_DELIMITER,
        env_file=u.resolve_env_file(),
        env_file_encoding=c.DEFAULT_ENCODING,
        case_sensitive=False,
        extra=c.EXTRA_IGNORE,
        validate_assignment=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """Auto-MRO: leaf env_prefix + parent env_prefixes as fallback."""
        sources = [init_settings, env_settings]
        leaf_prefix = cls.model_config.get("env_prefix", "")
        for parent in cls.__mro__:
            cfg = getattr(parent, "model_config", None)
            if (
                isinstance(cfg, dict)
                and (prefix := cfg.get("env_prefix"))
                and prefix != leaf_prefix
            ):
                sources.append(EnvSettingsSource(settings_cls, env_prefix=prefix))
        sources.extend([dotenv_settings, file_secret_settings])
        return tuple(sources)
```

Subproject settings:

```python
from flext_core import FlextSettings
from pydantic_settings import ConfigDict


@FlextSettings.auto_register("api")
class FlextApiSettings(FlextSettings):
    model_config = ConfigDict(env_prefix="FLEXT_API_", extra="ignore")
    base_url: str = c.Api.DEFAULT_BASE_URL
    timeout: t.PositiveTimeout = c.Api.DEFAULT_TIMEOUT
```

## MRO Composition

Integration projects use dual-inheritance for settings, same as models:

```python
class FlextTargetOracleSettings(FlextMeltanoSettings, FlextDbOracleSettings):
    model_config = ConfigDict(env_prefix="FLEXT_TARGET_ORACLE_", extra="ignore")

    # Fields from FlextMeltanoSettings: project_root, config_dir, etc.
    # Fields from FlextDbOracleSettings: host, port, service_name, etc.
    # Own fields:
    batch_size: t.BatchSize = c.TargetOracle.BATCH_SIZE
```

**Auto-MRO env source resolution**: `settings_customise_sources` in FlextSettings base auto-discovers parent env prefixes from MRO. Priority: init > leaf prefix > parent prefixes (MRO order) > dotenv > secrets.

This means `FLEXT_MELTANO_PROJECT_ROOT` works even from `FlextTargetOracleSettings`.

### Env Prefix Convention

| Project | env_prefix |
|---------|-----------|
| flext-core | `FLEXT_` |
| flext-cli | `FLEXT_CLI_` |
| flext-meltano | `FLEXT_MELTANO_` |
| flext-api | `FLEXT_API_` |
| flext-auth | `FLEXT_AUTH_` |
| flext-db-oracle | `ORACLE_` |
| flext-grpc | `FLEXT_GRPC_` |
| flext-observability | `FLEXT_OBSERVABILITY_` |
| Integration | `FLEXT_<ROLE>_<DOMAIN>_` |

## Workflow

1. Inherit `FlextSettings` — never `BaseSettings` or `m.Value`.
2. Define `model_config = ConfigDict(env_prefix="FLEXT_<PROJECT>_", extra="ignore")`.
3. Use `c.*` constants for all field defaults.
4. Add `@FlextSettings.auto_register("<namespace>")` if namespace access needed.
5. Add `@model_validator(mode="after")` for cross-field validation.
6. Run `ruff check` + `pytest` to verify.

## Examples

Good — FlextSettings inheritance with auto-register:

```python
@FlextSettings.auto_register("auth")
class FlextAuthSettings(FlextSettings):
    model_config = ConfigDict(env_prefix="FLEXT_AUTH_", extra="ignore")
    secret_key: str = Field(min_length=c.Auth.SECRET_MIN_LENGTH)
    algorithm: str = c.Auth.DEFAULT_JWT_ALGORITHM
```

Bad — m.Value with custom singleton:

```python
class FlextAuthSettings(m.Value):
    _global_instance: ClassVar[list[...]] = [None]

    def get_or_create_global(cls): ...
```

Why bad: bypasses FlextSettings singleton, no env var support, duplicates singleton logic.

Bad — os.environ bypass:

```python
def from_env(cls, prefix):
    for key in candidates:
        value = os.environ.get(key)
```

Why bad: duplicates Pydantic ConfigDict env resolution. Use `cls()` or `EnvSettingsSource`.

## Verification

- `ruff check flext-*/src/*/settings.py` — zero errors
- `pytest flext-core/tests/ -k settings` — settings tests pass
- No `os.environ` in src/: `rg "os\.environ|os\.getenv" flext-*/src/ --type py`
- All inherit FlextSettings: `rg "class Flext.*Settings\(" flext-*/src/ --type py`
- No m.Value settings: `rg "Settings\(m\.Value\)" flext-*/src/ --type py`
