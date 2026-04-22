---
name: lib-pydantic-settings
description: Pydantic ConfigDict and singleton settings patterns across FLEXT subprojects. Use when editing settings.py models, env bindings, or configuration validation behavior.

---

# Lib Pydantic Settings

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
- Use `@u.model_validator(mode="after")` for cross-field consistency checks.
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
from __future__ import annotations

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from flext_core import c, m


class FlextSettings(m.BaseSettings):
    model_config = m.SettingsConfigDict(
        env_prefix="FLEXT_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Auto-MRO: leaf env_prefix + parent env_prefixes as fallback."""
        sources: list[PydanticBaseSettingsSource] = [init_settings, env_settings]
        sources.extend([dotenv_settings, file_secret_settings])
        return tuple(sources)
```

Subproject settings:

```python
from __future__ import annotations

from flext_core import FlextSettings, m


@FlextSettings.auto_register("api")
class FlextApiSettings(FlextSettings):
    model_config = m.SettingsConfigDict(env_prefix="FLEXT_API_", extra="ignore")
    base_url: str
    timeout: float
```

## MRO Composition

Integration projects use dual-inheritance for settings, same as models:

```python
from __future__ import annotations

from flext_core import FlextSettings, m


class FlextTargetOracleSettings(FlextSettings):
    model_config = m.SettingsConfigDict(
        env_prefix="FLEXT_TARGET_ORACLE_", extra="ignore"
    )
    batch_size: int
```

**Auto-MRO env source resolution**: `settings_customise_sources` in FlextSettings base auto-discovers parent env prefixes from MRO. Priority: init > leaf prefix > parent prefixes (MRO order) > dotenv > secrets.

This means `FLEXT_MELTANO_PROJECT_ROOT` works even from `FlextTargetOracleSettings`.

### Env Prefix Convention

| Project             | env_prefix               |
| ------------------- | ------------------------ |
| flext-core          | `FLEXT_`                 |
| flext-cli           | `FLEXT_CLI_`             |
| flext-meltano       | `FLEXT_MELTANO_`         |
| flext-api           | `FLEXT_API_`             |
| flext-auth          | `FLEXT_AUTH_`            |
| flext-db-oracle     | `ORACLE_`                |
| flext-grpc          | `FLEXT_GRPC_`            |
| flext-observability | `FLEXT_OBSERVABILITY_`   |
| Integration         | `FLEXT_<ROLE>_<DOMAIN>_` |

## Workflow

1. Inherit `FlextSettings` — never `BaseSettings` or `m.Value`.
2. Define `model_config = ConfigDict(env_prefix="FLEXT_<PROJECT>_", extra="ignore")`.
3. Use `c.*` constants for all field defaults.
4. Add `@FlextSettings.auto_register("<namespace>")` if namespace access needed.
5. Add `@u.model_validator(mode="after")` for cross-field validation.
6. Run `ruff check` + `pytest` to verify.

## Examples

Good — FlextSettings inheritance with auto-register:

```python
from __future__ import annotations

from flext_core import FlextSettings, m


@FlextSettings.auto_register("auth")
class FlextAuthSettings(FlextSettings):
    model_config = m.SettingsConfigDict(env_prefix="FLEXT_AUTH_", extra="ignore")
    secret_key: str
    algorithm: str
```

Bad — m.Value with custom singleton:

```python
from __future__ import annotations

from flext_core import m


class FlextAuthSettingsBad(m.BaseModel):
    """WRONG — m.Value with custom singleton."""

    secret_key: str = ""
```

Why bad: bypasses FlextSettings singleton, no env var support, duplicates singleton logic.

Bad — os.environ bypass:

```python
from __future__ import annotations

import os


def from_env_bad(prefix: str) -> str:
    """WRONG — bypasses Pydantic env resolution."""
    return os.environ.get(f"{prefix}KEY", "")
```

Why bad: duplicates Pydantic ConfigDict env resolution. Use `cls()` or `EnvSettingsSource`.

## Verification

- `ruff check flext-*/src/*/settings.py` — zero errors
- `pytest flext-core/tests/ -k settings` — settings tests pass
- No `os.environ` in src/: `rg "os\.environ|os\.getenv" flext-*/src/ --type py`
- All inherit FlextSettings: `rg "class Flext.*Settings\(" flext-*/src/ --type py`
- No m.Value settings: `rg "Settings\(m\.Value\)" flext-*/src/ --type py`
