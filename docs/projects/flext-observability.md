# FLEXT Observability

FLEXT Observability is the enterprise monitoring, metrics, and telemetry platform of FLEXT. It models every
observability signal — metrics, traces, alerts, health checks, and log entries — as validated Pydantic entities, and
records them through railway-oriented services, decorators, and instrumentation helpers shared by all downstream FLEXT
projects.

## Status & health

- **Version**: 0.20.0-dev
- **Python**: 3.13+ only
- **Project class**: platform (consumes `flext-core` and `flext-cli`)
- **Facade**: `from flext_observability import observability` — the `FlextObservability` facade class with static
  factory methods
- **Short aliases**: `c`, `m`, `p`, `r`, `t`, `u` plus operational `s`, `d`, `e`, `h`, `x`, and `settings`

### Quality signals

- Lint, type-check, security, and tests run through the canonical `make` verbs; current status is produced by the gates,
  not restated here.
- Run `make check PROJECT=flext-observability` (lint + type-check) and `make check` for the full gate chain.

## Quick start

```bash
pip install flext-observability
```

```python
from flext_observability import flext_monitor_function, observability

metric = observability.flext_metric("cpu_usage", 42.0, "percent")
if metric.success:
    u.Cli.print(metric.value.name, metric.value.value)


@flext_monitor_function(metric_name="data.work")
def work(data: str) -> str:
    return data


work("payload")
```

The `flext_metric`, `flext_trace`, `flext_alert`, `flext_health_check`, and `flext_log_entry` factories return `r[...]`
results wrapping the corresponding entity model. `flext_monitor_function` is exported at the package root and
instruments any callable with execution metrics.

## Architecture & modules

- **Facade**: `api.py` defines `FlextObservability` with nested entity models (`Metric`, `Trace`, `Alert`,
  `HealthCheck`, `LogEntry`), static factory methods, and the singleton services for recording each signal;
  `observability` rebinds the class at the package root.
- **Service layer** (`services/`): `monitoring` (the `FlextObservabilityMonitor` and its `flext_monitor_function`
  decorator), `health`, `logging_integration`, `http_instrumentation`, `http_client_instrumentation`, `performance`,
  `sampling`, `custom_metrics`, `error_handling`, `context`, `advanced_context`, and `fields`.
- **Flat core modules**: `constants.py`, `typings.py`, `protocols.py`, `models.py`, `utilities.py` provide the
  `c/m/p/t/u` facades; execution parametrization lives under `config/` and is consumed through the SSOT `settings`
  access form.

### Key architectural patterns

- **Entities as models**: every signal is a frozen Pydantic model owned by the `m` facet; factories validate inputs with
  `model_validate` before anything is recorded.
- **Railway everywhere**: factories and services return `r[T]`, so instrumentation composes with the rest of the FLEXT
  stack without exceptions as control flow.
- **Decorator instrumentation**: `flext_monitor_function` wraps callables to record execution metrics through the same
  monitor service used directly.
- **Integration-ready**: HTTP client/server instrumentation, logging integration, and sampling services provide the
  hooks downstream projects (API, auth, web) use for shared telemetry.

## Testing & quality

- `make check PROJECT=flext-observability` — Ruff + type-check on the project lane.
- `make test PROJECT=flext-observability` — unit and integration suites through the shared `flext-tests` helpers.
- `make check` — full workspace validation chain (lint, types, security, tests, docs).
- Typing is strict (no `Any`/`object`); all owned payloads are `m.Observability.*` Pydantic models and all fallible
  paths return `r[T]`.

## Resources

- [Project README](../../flext-observability/README.md)
- [Project catalog](generated/catalog.md) entry and generated API reference under `docs/api-reference/generated/flext-
  observability.md`
- Project documentation under `flext-observability/docs/`
- Related projects: `flext-core`, `flext-cli`, `flext-api`, `flext-auth`, `flext-web`, `flext-quality`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-observability/issues>
- Discussions: <https://github.com/flext-sh/flext-observability/discussions>
- Follow the workspace `AGENTS.md` and the project's own `AGENTS.md` before proposing doc or code changes so this page
  stays aligned with the portal.
