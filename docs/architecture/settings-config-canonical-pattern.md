# Canonical Settings & Config Pattern (ADR-005 companion guide)

<!-- TOC START -->
- [1. Law (non-negotiable)](#1-law-non-negotiable)
- [2. Minimal base surface (flext-core)](#2-minimal-base-surface-flext-core)
- [3. Canonical project SETTINGS module — `<project>/settings.py`](#3-canonical-project-settings-module-projectsettingspy)
- [4. Canonical project CONFIG module — `<project>/_config.py`](#4-canonical-project-config-module-projectconfigpy)
- [5. Root export (`<project>/**init**.py`)](#5-root-export-projectinitpy)
- [6. Forbidden (remove on sight)](#6-forbidden-remove-on-sight)
- [7. Propagation checklist (per project)](#7-propagation-checklist-per-project)
<!-- TOC END -->

**Status**: supporting guide | **Scope**: every FLEXT project (`flext-*`, integrations, `ai-hub`)
**SSOT**: [ADR-005](adr/005-config-settings-constants-templates-schemas-ssot.md) defines the
canonical configuration decision. This guide explains its settings/config usage
patterns. Reviewed 2026-07-09.

<!-- mro-wkii.14 (agent: codegen) — errata por pedido vivo (precedencia U1). -->

> **ERRATA (2026-07-10) — supersede parcial por `AGENTS.md` U2–U8.** Por pedido vivo do operador (precedência U1), as
seções §1 ("no MRO composition") e §2 ("`FlextConfig` `extra=\"allow\"`") deste doc estão **SUPERSEDED**. Padrão
vigente: acesso strict `from <pkg> import config`/`settings` →
`config.<Namespace>.<domain>`/`settings.<Namespace>.<domain>` (U2); domínios **modelados**
`frozen=True, extra="forbid"` com `model_validate` na borda, nunca `dict`/`Any`/`object` no consumo (U3); `ConfigProxy`
tipado/lazy em `u.<Namespace>` (U4); MRO para demais config/settings (U5); typing estrito U6; zero helpers/aliases
(U7). Referência viva: `cosmos-main/src/cosmos_main/` (`_constants|_models|_protocols|_utilities/{config,settings}.py`

- `_config.py`/`_settings.py`). Reescrita integral deste doc fica na lane do standardizer (mro-wkii.11).

## 1. Law (non-negotiable)

- `settings` and `config` are **pre-instantiated namespaced singletons**. Import them
  directly and use them directly: `from flext_x import settings, config`.
- Each project subclasses the single base (`FlextSettings` / `FlextConfig`) **directly** —
  there is no `FlextSettingsBase`, no field mixins, no MRO composition.
- Grouped namespaces are **plain Pydantic-2 nested-model Fields** (`settings.Cli.*`), never a
  custom `**getattr**` or a registry.
- Layer-0 purity: `_settings.py` / `_config.py` import **only** stdlib + pydantic /
  pydantic-settings. No import of `c`/`t`/`p`/`m`/`u` or any project module.
- Zero legacy: no `apply_override`, no `config_load`/`u.Cli.config_load`, no namespace
  registry, no `for_context`, no compatibility shims. Removed in the same cycle.

## 2. Minimal base surface (flext-core)

`FlextSettings` (mutable) and `FlextConfig` (frozen) expose ONLY:

| Member | Purpose |
| --- | --- |
| `fetch_global()` | return the per-class singleton (lazy, thread-safe) — the accessor projects call |
| `update_global(**overrides)` | Pydantic-2 `model_copy(update=…)` mutation of the singleton (settings only) |
| `clone(**overrides)` | deep-copy + revalidate for isolated injection snapshots |
| `reset_for_testing()` | drop the singleton slot for test isolation |
| `resolve_env_file(namespace=None)` | `.env` discovery honouring `FLEXT_ENV_FILE` |

Root fields on `FlextSettings` (the only universal ones): `debug`, `trace`, `log_level`,
`timezone`, `async_logging`. `FlextConfig` is **open** (`extra="allow"`, `frozen=True`, zero
declared fields) and auto-loads `config/*.yaml`.

## 3. Canonical project SETTINGS module — `<project>/settings.py`

```python
from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from flext_core import FlextSettings


class FlextXSettings(FlextSettings):
    """Project settings: root fields (debug/trace/log_level/…) + the ``X`` namespace."""

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_X_",  # project-specific env prefix
        extra="ignore",
    )

    class XSettings(
        BaseModel
    ):  # grouped namespace (any project name, e.g. Dcdoc, Cli, Web)
        endpoint: Annotated[str, Field(description="Service endpoint")] = (
            "https://x.local"
        )
        retries: Annotated[int, Field(description="Retry attempts", ge=0)] = 3
        # ...project fields with their own defaults/env via env_nested_delimiter

    if TYPE_CHECKING:  # avoid field-name/type clash (Pydantic-2 gotcha)
        X: XSettings
    else:
        X: XSettings = Field(default_factory=XSettings, description="X namespace.")


# Exported pre-instantiated singleton — ALWAYS this line:
settings = FlextXSettings.fetch_global()```
Consumers: `from flext_x import settings` → `settings.debug` (root) and
`settings.X.endpoint` (namespace group). Env: `FLEXT_X_DEBUG`, `FLEXT_X_X**ENDPOINT`
(nested delimiter `**`).

## 4. Canonical project CONFIG module — `<project>/_config.py`

Identical shape, frozen + open, namespaced the same way:

```python
from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from flext_core import FlextConfig


class FlextXConfig(FlextConfig):
    """Project config: open YAML-loaded (config/*.yaml), frozen, ``X`` namespace."""

    model_config = SettingsConfigDict(
        frozen=True, extra="allow", env_prefix="FLEXT_X_CONFIG_"
    )

    class XConfig(BaseModel):
        rules_path: Annotated[str, Field(description="Rules dir")] = "config/x"

    if TYPE_CHECKING:
        X: XConfig
    else:
        X: XConfig = Field(default_factory=XConfig, description="X config namespace.")


config = FlextXConfig.fetch_global()```
Config files live at `<project root>/config/*.yaml`, auto-globbed + deep-merged (app-owned,
CWD-relative).

## 5. Root export (`<project>/**init**.py`)

`config`/`settings` are emitted into the package root from the module `**all**`
(`**all** = ["FlextXSettings", "settings"]` / `["FlextXConfig", "config"]`). Never hand-edit
the generated `**init**.py`; run `make build WHAT=artifacts` after adding the modules.

## 6. Forbidden (remove on sight)

+ `FlextSettingsBase` and any `FlextSettings{Core,Database,Dispatcher,Infrastructure,DI,Registry,Context}` mixin.
+ `register_namespace` / `auto_register` / `fetch_namespace` / `resolve_namespace_settings` /
  `registered_namespaces` / `_namespace_registry` / settings `**getattr**`.
+ `apply_override`, `for_context`, `clone_for_injection`, `resolve_di_settings_provider`.
+ `u.Cli.config_load` / `config_load_dir` / `schema_validate`, `m.ConfigDocument`,
  `p.ConfigLoader`, `t.Config*`, `u.config_load/merge/env_override`, `c.CONFIG_*`.
+ `def settings(self) -> XSettings: return XSettings.fetch_global()` property overrides —
  use the module singleton `from flext_x import settings` directly, never `self.settings`.
+ Importing `c`/`t`/`p`/`m`/`u` inside `_settings.py` / `_config.py`.

## 7. Propagation checklist (per project)

1. `settings.py`: subclass `FlextSettings` directly, group fields under a nested namespace
   model Field, export `settings = FlextXSettings.fetch_global()`.
2. Add `_config.py` with `FlextXConfig(FlextConfig)` + `config = FlextXConfig.fetch_global()`.
3. Create `config/` dir with `*.yaml` if the project ships declarative params.
4. Delete every forbidden symbol (§6); rewrite `self.settings.*` → `settings.*`.
5. `make build WHAT=artifacts` to publish `config`/`settings` at the package root.
6. `make check` and `make test` green; commit.
