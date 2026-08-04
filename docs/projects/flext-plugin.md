# FLEXT Plugin

FLEXT Plugin is the plugin system of the FLEXT platform. It provides discovery, registration, lifecycle management,
execution, and hot-reload monitoring of plugins through a single railway-oriented service facade, so every FLEXT service
loads and manages extensions the same way.

## Status & health

- **Version**: 0.12.0-dev
- **Python**: 3.13+ only
- **Project class**: platform (consumes `flext-core` and `flext-cli`)
- **Facade**: `from flext_plugin import plugin` — the `FlextPluginApi` service facade class
- **Short aliases**: `c`, `m`, `p`, `r`, `t`, `u` plus operational `s`, `d`, `e`, `h`, `x`, and `settings`

### Quality signals

- Lint, type-check, security, and tests run through the canonical `make` verbs; current status is produced by the gates,
  not restated here.
- Run `make check PROJECT=flext-plugin` (lint + type-check) and `make check` for the full gate chain.

## Quick start

```bash
pip install flext-plugin
```

```python
from flext_plugin import plugin

api = plugin()
result = api.discover_plugins(["./plugins"])
if result.success:
    u.Cli.print(f"{len(result.value)} plugins discovered")

loaded = api.load_plugin("./plugins/my_plugin.py")
```

`FlextPluginApi` follows the FLEXT service facade pattern: no constructor arguments, state via private attributes, and
every public method returning `r[T]`. The same instance covers the full lifecycle — `discover_plugins`,
`register_plugin`, `load_plugin`, `execute_plugin`, `fetch_plugin`, `fetch_plugin_status`, `resolve_plugin_active`,
`list_plugins`, `unregister_plugin`, and the `start_hot_reload` / `stop_hot_reload` watchers.

## Architecture & modules

- **Facade**: `api.py` defines `FlextPluginApi`, a service facade over the platform service (`s` base from `flext-
  core`), and rebinds it as the `plugin` alias at the package root.
- **Platform utilities** (`_utilities/`): `plugin_platform` (the default `PlatformService` implementation), `discovery`
  (plugin scanning), and `implementations` (concrete plugin adapters), wired in through `_build_default_platform`.
- **Flat core modules**: `constants.py`, `typings.py`, `protocols.py`, `models.py`, `utilities.py` provide the
  `c/m/p/t/u` facades; execution parametrization lives under `config/` and is consumed through the SSOT `settings`
  access form.

### Key architectural patterns

- **Service facade**: state lives in `u.PrivateAttr` fields, the platform service is composed (not inherited), and the
  public surface is small and uniform.
- **Railway everywhere**: discovery, loading, execution, and hot-reload control all return `r[T]`; failures propagate as
  values with logged context.
- **Protocol-typed boundaries**: the facade depends on `p.Plugin.PlatformService`, so alternative platform
  implementations can be bound without touching the API.
- **Pydantic 2-way models**: plugin metadata and status payloads are `m.Plugin.*` models that round-trip through
  `model_validate` / `model_dump`.

## Testing & quality

- `make check PROJECT=flext-plugin` — Ruff + type-check on the project lane.
- `make test PROJECT=flext-plugin` — unit and integration suites through the shared `flext-tests` helpers.
- `make check` — full workspace validation chain (lint, types, security, tests, docs).
- Typing is strict (no `Any`/`object`); all owned payloads are `m.Plugin.*` Pydantic models and all fallible paths
  return `r[T]`.

## Resources

- [Project README](../../flext-plugin/README.md)
- [Project catalog](generated/catalog.md) entry and generated API reference under `docs/api-reference/generated/flext-
  plugin.md`
- Project documentation under `flext-plugin/docs/`
- Related projects: `flext-core`, `flext-cli`, `flext-observability`, `flext-meltano`, and the Singer-based `flext-
  tap-*` / `flext-target-*` families

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-plugin/issues>
- Discussions: <https://github.com/flext-sh/flext-plugin/discussions>
- Follow the workspace `AGENTS.md` and the project's own `AGENTS.md` before proposing doc or code changes so this page
  stays aligned with the portal.
