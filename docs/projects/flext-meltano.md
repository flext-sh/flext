# FLEXT Meltano

FLEXT Meltano is the enterprise data integration platform of FLEXT. It wraps Meltano, the Singer protocol (taps,
targets, streams, sinks), and dbt behind the FLEXT facade and railway discipline, so ELT pipelines are declared,
orchestrated, and executed through one typed surface.

## Status & health

- **Version**: 0.12.0-dev
- **Python**: 3.13+ only
- **Project class**: platform (consumes `flext-core` and `flext-cli`; integrates FLEXT forks of `meltano`, `dbt-core`,
  `dbt-adapters`, and `dbt-common`)
- **Facade**: `from flext_meltano import meltano` — the process-wide `FlextMeltano` singleton
- **CLI**: `flext-meltano` console script (`flext_meltano.cli:main`)
- **Short aliases**: `c`, `m`, `p`, `r`, `t`, `u` plus operational `s`, `d`, `e`, `h`, `x`, `config`, and `settings`

### Quality signals

- Lint, type-check, security, and tests run through the canonical `make` verbs; current status is produced by the gates,
  not restated here.
- Run `make check PROJECT=flext-meltano` (lint + type-check) and `make val` for the full gate chain.

## Quick start

```bash
pip install flext-meltano
```

```python
from flext_meltano import meltano

pipeline = meltano.tap("tap-ldap", host="ldap.example.com")
if pipeline.success:
    result = pipeline.value.execute()
```

`meltano.tap(...)`, `meltano.target(...)`, and `meltano.dbt(...)` return `r[Self]` — a specialized facade instance for
the source, sink, or transformation service — and `.execute()` runs the service through the railway pattern, returning
`r[t.JsonMapping]`. Plugin discovery, project management, and Singer catalog/state handling are exposed on the same
facade.

## Architecture & modules

- **Facade**: `api.py` defines `FlextMeltano`, composed by MRO over the full service stack (service, adapter, bridge,
  executor, project manager, library runner, validators, and the dbt/Singer mixins), and publishes the `meltano`
  singleton.
- **Service layer** (`services/`): `services` (plugin lifecycle), `adapters` (Singer tap/target execution), `executor`
  (pipeline orchestration), `project_service` / `meltano_project_sdk` (Meltano project management), `meltano_plugins` /
  `meltano_plugin_discovery` (plugin registry), `dbt_project` / `dbt_runner` (dbt integration), `singer_catalog`,
  `singer_state`, `singer_sdk`, and `bridge`.
- **Singer abstractions**: `Tap`, `Target`, `Stream`, and `Sink` base types are exported directly so downstream `flext-
  tap-*` / `flext-target-*` packages build on them.
- **Private facets**: `_constants`, `_models`, `_protocols`, `_typings`, `_utilities` back the public `c/m/p/t/u`
  facades; execution parametrization lives under `config/` and is consumed through the SSOT `config` / `settings` access
  form.

### Key architectural patterns

- **MRO facade**: `FlextMeltano` inherits every service and mixin, so the whole platform surface is reachable from the
  single `meltano` singleton with no wrapper classes.
- **Railway everywhere**: plugin discovery, adapter execution, and orchestration all return `r[T]`; failures propagate
  as values, never as control-flow exceptions.
- **Builder DSL**: `tap` / `target` / `dbt` create specialized service facades from the same class, keeping pipeline
  code declarative.
- **Pydantic 2-way models**: plugin metadata, project settings, and pipeline payloads are `m.Meltano.*` models that
  round-trip through `model_validate` / `model_dump`.

## Testing & quality

- `make check PROJECT=flext-meltano` — Ruff + type-check on the project lane.
- `make test PROJECT=flext-meltano` — unit and integration suites through the shared `flext-tests` helpers.
- `make val` — full workspace validation chain (lint, types, security, tests, docs).
- Typing is strict (no `Any`/`object`); all owned payloads are `m.Meltano.*` Pydantic models and all fallible paths
  return `r[T]`.

## Resources

- [Project README](../../flext-meltano/README.md)
- [Project catalog](generated/catalog.md) entry and generated API reference under `docs/api-reference/generated/flext-
  meltano.md`
- Project documentation under `flext-meltano/docs/`
- Related projects: `flext-core`, `flext-cli`, `flext-plugin`, and the Singer-based `flext-tap-*` / `flext-target-*` /
  `flext-dbt-*` families

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-meltano/issues>
- Discussions: <https://github.com/flext-sh/flext-meltano/discussions>
- Follow the workspace `AGENTS.md` and the project's own `AGENTS.md` before proposing doc or code changes so this page
  stays aligned with the portal.
