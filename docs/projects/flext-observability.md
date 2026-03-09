# FLEXT Observability

<!-- TOC START -->

- [Status & metrics](#status-metrics)
- [Quick start](#quick-start)
- [Architecture snapshot](#architecture-snapshot)
- [Key features](#key-features)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT Observability (v0.9.0) is the platform-wide monitoring, metrics, tracing, and alerting foundation. The architecture is complete, but the quality pipeline remains blocked by a `flext-core` import issue, so status calls out the blockers while still describing the ready entities, services, and instruments the project ships.

## Status & metrics

- **Version**: 0.9.0 (architecture complete, quality checks blocked)
- **Tests**: 481 functions across 40 files, currently failing because of import errors; quality validation cannot run until `flext-core` exports are unblocked
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + coverage + docstring checks) is blocked by the import failure noted in the README
- **Coverage**: 100% architecture target (currently blocked)
- **Type safety**: Pyrefly strict mode + MyPy strict mode are configured to read-level discipline (zero `Any`, no `TYPE_CHECKING`, no `cast`, no `# type: ignore`)
- **Security**: Bandit + pip-audit gates defined but not executed until the `flext-core` dependency stabilizes

## Quick start

```bash
git clone https://github.com/flext-sh/flext-observability.git
cd flext-observability
poetry install
make setup
make check
```

```python
from flext_observability import (
    flext_create_metric,
    flext_create_trace,
    flext_monitor_function,
)

metric = flext_create_metric("cpu_usage", 42.0, "percent")
trace = flext_create_trace("order.process", "processing")


@flext_monitor_function("data.work")
def work(data):
    return data


work("payload")
```

## Architecture snapshot

- **Layers**: clean architecture stack (Domain → Application → Infrastructure) with tiered modules that never import upward. `constants.py`, `typings.py`, `protocols.py` stay isolated from higher tiers.
- **Modules**: `entities/` (FlextMetric, FlextTrace, FlextAlert, FlextHealthCheck, FlextLogEntry), `services/`, `decorators/`, `api.py` (factory functions), and `integration/` modules for Prometheus/Grafana/OTLP planning.
- **Integration**: The project integrates with `flext-core` (FlextResult, container, context, decorators, logger), `flext-cli` (command helpers), and downstream services (API, Auth, Web) via shared instrumentation helpers.
- **Decorators**: `flext_monitor_function` automatically instruments functions for metrics/traces/log entries, and the pattern is ready to extend to distributed tracing (Jaeger/OTLP) once the blocking issue is resolved.

## Key features

- Domain models for every observability signal (metrics, traces, alerts, health checks, log entries) with Pydantic v2 validation.
- Services that record metrics, traces, alerts, and health checks through FlextResult-based APIs.
- Monitoring decorators, instrumentation utilities, and configuration hints for OpenTelemetry and Prometheus.
- Pre-built test suite (481 functions) organized by unit/integration/monitoring, currently unable to run due to `flext-core` import compatibility.
- Clear next steps: instrumentation stack integration, correlation IDs, distributed tracing, and SLA/SLO dashboards.

## Resources & references

- [Project README](../../flext-observability/README.md)
- [AGENTS guidance](../../flext-observability/AGENTS.md) with zero-tolerance rules and quality gate steps
- `flext-observability/docs/` for docs, architecture, guides, and troubleshooting
- Reports: `reports/pytest/*`, `reports/lint-output/*`, `reports/coverage-scan/*` (when the pipeline unblocks)
- Related projects: `flext-core`, `flext-cli`, `flext-api`, `flext-auth`, `flext-ldap`, `flext-ldif`, `flext-quality`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-observability/issues>
- Discussions: <https://github.com/flext-sh/flext-observability/discussions>
- Follow `docs/standards/README.md` and the workspace-level AGENTS when altering the architecture or docs so this brief stays accurate.
