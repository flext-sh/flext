# FLEXT Plugin

<!-- TOC START -->

- [Status & metrics](#status-metrics)
- [Quick start](#quick-start)
- [Architecture overview](#architecture-overview)
- [Quality & compliance](#quality-compliance)
- [Resources](#resources)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT Plugin (v0.9.0) is the production-grade plugin management platform for the FLEXT ecosystem. It handles discovery, lifecycle, hot reload, sandboxing, and security validation so every FLEXT service can load and manage plugins with a unified architecture.

## Status & metrics

- **Version**: 0.9.0 (production ready, 0.10.0 enhancements planned)
- **Python**: 3.13+
- **Tests**: 339 test methods across unit, integration, and e2e suites; coverage target 90% (currently met per README)
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + coverage + docstring checks) is required before merges
- **Type safety**: MyPy strict mode, zero `Any`, `cast`, or `# type: ignore`; every public surface returns `FlextResult[T]`
- **Security**: Sandbox validation, hot reload monitoring, and watchdog-backed file discovery run inside isolation layers defined by the project’s zero-tolerance CLAUDE rules

## Quick start

```bash
git clone https://github.com/flext-sh/flext.git
cd flext-plugin
make setup
make check
make validate
```

```python
from flext_core import FlextContainer
from flext_plugin import FlextPluginPlatform

container = FlextContainer()
platform = FlextPluginPlatform(container)
result = platform.discover_plugins("./plugins")
if result.is_success:
    print(f"{len(result.unwrap())} plugins discovered")
```

Use the CLI helpers (currently disabled in `__init__.py`) once the command layer completes for v0.10.0.

## Architecture overview

- **Facade layer**: `FlextPluginPlatform` exposes discovery, load/unload, install, enable/disable, and hot-reload commands plus security validation hooks.
- **Service layer**: `FlextPluginService`, `FlextPluginDiscoveryService` encapsulate lifecycle transitions."# TODO".
- **Model layer**: `FlextPluginModels` hosts entity/config/metadata Pydantic models and scoped FlextResult helpers.
- **Infrastructure**: `PluginDiscovery`, `HotReload`, `RealAdapters`, `watchdog` watchers, and sandboxing guardrails; direct imports to `flext-core` (FlextResult, FlextContainer, FlextModels, FlextLogger, FlextDispatcher) ensure consistent design.
- **Clean architecture**: 19 classes, 20 modules, single-class-per-module discipline, 9,767 lines of code respecting layering rules; zero-tolerance `CLAUDE` enforces FlextResult always.

## Quality & compliance

- **Validation commands**: `make lint`, `make type-check`, `make test`, `make coverage`, `make security`, `make validate`, `make check`, `make format`.
- **Coverage goal**: 90% minimum across the plugin stack; tests run via `pytest tests/`, `pytest --cov=flext_plugin`, `pytest -m "not slow"`, etc.
- **Security**: plugin sandboxing, entry point validation, and hot reload watchers all validated by the quality pipeline; zero Ruff/Pyrefly errors allowed.
- **Architecture compliance**: single class per module, no `TYPE_CHECKING`, no `Any`, all operations return `FlextResult`, instrumentation built into `flext-observability` and `flext-cli` once CLI integration finalizes.

## Resources

- [Project README](../../flext-plugin/README.md)
- [Project CLAUDE](../../flext-plugin/AGENTS.md) for zero tolerance policies and command gating
- `docs/getting-started.md`, `docs/architecture.md`, `docs/api-reference.md`, `docs/development.md`, `TODO.md` inside the project for deeper guidance
- Reports: `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` (aligned with the mentioned quality commands)
- Related projects: `flext-core`, `flext-cli`, `flext-observability`, Singer taps/targets in the `flext-tap-*` / `flext-target-*` families

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-plugin/issues>
- Discussions: <https://github.com/flext-sh/flext-plugin/discussions>
- Follow `docs/standards/README.md` and the per-project `CLAUDE` before making doc or code changes so the portal stays accurate.
