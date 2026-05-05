---
name: lib-pydantic-settings
description: Pydantic ConfigDict and singleton settings patterns across FLEXT subprojects. Use when editing settings.py models, env bindings, or configuration validation behavior.

---

# Lib Pydantic Settings

**Reviewed**: 2026-05-05 | **Scope**: FlextSettingsBase + Pydantic-2 mutation API + rule-3 isolation

## Scope

- Core canonical implementation: `flext-core/src/flext_core/_settings/base.py` (FlextSettingsBase)
  and `flext-core/src/flext_core/settings.py` (FlextSettings root composition)
- Governance: `AGENTS.md` §2.6 Settings Law + plan
  `~/.claude/plans/temos-varios-erros-de-serialized-fountain.md`
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

- `flext-core`: defines `FlextSettings` root + `FlextSettingsBase` Pydantic-2
  base with `fetch_global` / `clone` / `update_global` / `validate_overrides`
  / `clone_for_injection` / `reset_for_testing` / `resolve_env_file`.
- All project subclasses inherit `FlextSettingsBase` (NOT `FlextSettings`)
  to honour rule-3 isolation: project subclasses MUST NOT inherit root
  concrete fields (`app_name`, `version`, `debug`, `log_level`,
  `database_url`, dispatcher_*, etc.). Each project owns its own copies
  if it actually uses those fields.

## References

- `AGENTS.md` §2.6 Settings Law — canonical governance source
- `flext-core/src/flext_core/_settings/base.py`: FlextSettingsBase (BaseSettings
  subclass with per-class singleton + Pydantic-2 mutation API)
- `flext-core/src/flext_core/settings.py`: FlextSettings root facade
- `flext-core/src/flext_core/_protocols/settings.py`: minimal `p.Settings`
  protocol (operations-only, no concrete fields)
- `pydantic-settings>=2.10.1`

## Rules

- All project settings classes MUST inherit `FlextSettingsBase` — never
  `FlextSettings` (root), never `BaseSettings` directly, never `BaseModel`.
- Always define `model_config = m.SettingsConfigDict(env_prefix="FLEXT_<PROJECT>_", extra="ignore")`.
  Each project owns its own env_prefix; never reuse the root `FLEXT_` prefix.
- All field defaults MUST come from `c.*` constants — no hardcoded values.
- Singleton via `FlextSettingsBase.__new__()` only — never custom singleton patterns.
- Use `cls.fetch_global()` to read; `cls.update_global(**overrides)` to mutate
  (replaces `cls._instance` via `model_copy(update=…)` + revalidation, propagates).
- Use `instance.clone()` (deep-copy + re-validation) when a service/container
  needs an isolated snapshot at construction time.
- Use `cls.reset_for_testing()` (or `cls.reset_instance()`) for test isolation.
- Use `cls.validate_overrides(**kwargs)` as a typo guard before update.

## Forbidden Patterns

- `os.environ`, `os.getenv`, `environ.get()` in `src/` code — use FlextSettingsBase env resolution.
- `BaseSettings` (pydantic_settings) as direct settings base class — use `FlextSettingsBase`.
- `FlextSettings` (root) as project subclass base — use `FlextSettingsBase`.
- `m.Value` or `BaseModel` as settings base — use `FlextSettingsBase`.
- `@FlextSettings.auto_register("<ns>")` — namespace registry is being phased out;
  consumers must call `FlextXSettings.fetch_global()` directly.
- Custom `_global_instance` / `get_or_create_global()` singleton — inherited.
- Hardcoded defaults (`"utf-8"`, `30`, `True`) — use `c.*` constants.
- `apply_override(...)` / `setattr(settings, …)` / custom `__setattr__` —
  use Pydantic-2 native `update_global(**overrides)` instead.
- Module-level singletons (`api = FlextApi()`) — use `cls.fetch_global()` or DI.
- `class Config:` (Pydantic v1) — use `m.SettingsConfigDict`.

## Instructions

Canonical project subclass:

```python
from __future__ import annotations

from typing import Annotated, ClassVar

from flext_core import FlextSettingsBase
from flext_<project> import c, m, u


class Flext<Project>Settings(FlextSettingsBase):
    """Validated runtime settings for <project>."""

    model_config: ClassVar[m.SettingsConfigDict] = m.SettingsConfigDict(
        env_prefix="FLEXT_<PROJECT>_",
        extra="ignore",
        validate_assignment=True,
    )

    # Project-specific fields ONLY — no inherited root fields (rule-3 isolation).
    base_url: Annotated[str, u.Field(description="Service base URL")] = c.<Project>.DEFAULT_BASE_URL
    timeout: Annotated[float, u.Field(description="Request timeout")] = c.<Project>.DEFAULT_TIMEOUT
```

If a project genuinely uses root-style fields (e.g. `app_name`, `version`,
`debug`, `log_level`), declare them locally with project-specific defaults:

```python
class FlextWebSettings(FlextSettingsBase):
    app_name: Annotated[str, u.Field(...)] = c.Web.DEFAULT_APP_NAME
    version: Annotated[str, u.Field(...)] = c.Web.DEFAULT_VERSION_STRING
```

Mutation contract (Pydantic-2 native — no `setattr`, no `__setattr__`):

```python
# Read shared singleton (mutations propagate via update_global).
settings = FlextLdifSettings.fetch_global()

# Mutate the singleton globally — replaces cls._instance via model_copy(update=…).
FlextLdifSettings.update_global(dn_max_length=512)

# Snapshot for an isolated container/service lifetime (rule 2).
snapshot = settings.clone(dn_max_length=2048)
```

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

1. Inherit `FlextSettingsBase` — never `FlextSettings`/`BaseSettings`/`BaseModel`.
2. Define `model_config = m.SettingsConfigDict(env_prefix="FLEXT_<PROJECT>_", extra="ignore")`.
3. Declare ONLY project-specific fields (rule-3 isolation; redeclare root-like
   fields locally if genuinely needed).
4. Use `c.*` constants for all defaults.
5. Use `@u.model_validator(mode="after")` for cross-field validation.
6. Run `make check CHECK_GATES=lint,pyrefly` + `make test` to verify.

## Examples

Good — FlextSettingsBase isolation:

```python
from __future__ import annotations

from typing import Annotated, ClassVar

from flext_core import FlextSettingsBase
from flext_auth import c, m, u


class FlextAuthSettings(FlextSettingsBase):
    model_config: ClassVar[m.SettingsConfigDict] = m.SettingsConfigDict(
        env_prefix="FLEXT_AUTH_",
        extra="ignore",
        validate_assignment=True,
    )
    secret_key: Annotated[str, u.Field(description="JWT signing secret")] = c.Auth.DEFAULT_SECRET
    algorithm: Annotated[str, u.Field(description="JWT algorithm")] = c.Auth.DEFAULT_ALG
```

Bad — inheriting root FlextSettings:

```python
class FlextAuthSettingsBad(FlextSettings):
    """WRONG — inherits 8+ root mixins (Core/Database/Dispatcher/...)
    contaminating FlextAuthSettings with `app_name`, `database_url`,
    `dispatcher_timeout_seconds`, etc. Violates rule-3 isolation."""
```

Bad — os.environ bypass:

```python
import os

def from_env_bad(prefix: str) -> str:
    """WRONG — bypasses Pydantic env resolution."""
    return os.environ.get(f"{prefix}KEY", "")
```

## Verification

- `make check CHECK_GATES=lint,pyrefly` per project — zero errors.
- `pytest flext-core/tests/unit/test_settings.py` — singleton + clone +
  update_global + validate_overrides + clone_for_injection contract.
- Workspace-wide audit: zero matches for forbidden patterns:
  - `sg run --pattern '@FlextSettings.auto_register($N)' --lang python .`
  - `sg run --pattern 'class Flext$X$Settings(FlextSettings)' --lang python -p '*/settings.py'`
  - `sg run --pattern 'apply_override' --lang python .`
  - `sg run --pattern 'def __setattr__($$$)' --lang python -p '*/settings.py'`
