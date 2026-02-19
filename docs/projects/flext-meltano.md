# FLEXT Meltano


<!-- TOC START -->
- [Status & health](#status-health)
- [Quick start](#quick-start)
- [Architecture snapshot](#architecture-snapshot)
- [Key features](#key-features)
- [Resources](#resources)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT Meltano is the enterprise Meltano integration and orchestration foundation for FLEXT pipelines. It delivers Singer protocol compliance, Meltano project management, plus plugin scaffolding and production automation so every downstream project reuses the same ELT controls.

## Status & health

- **Version**: 0.9.0 — Production-capable, delivery in progress (tests currently blocked)
- **Python**: 3.13+ only
- **Quality gates**: `make lint` (Ruff), `make type-check` (Pyrefly), `make security` (Bandit) pass; `make test` and coverage remain blocked as noted in the README
- **Coverage**: in-flight; the README currently marks the coverage gate as blocked while other signals run green
- **Type discipline**: 100% MyPy compliance, zero `Any`, `cast`, or `# type` ignores; all flows rely on `FlextResult[T]` and strict typing
- **Documentation**: full docs live under `flext-meltano/docs/` (architecture, config, guides, troubleshooting)

## Quick start

```bash
git clone https://github.com/flext-sh/flext.git
cd flext-meltano
poetry install
make setup
```

```bash
make check         # lint + type-check
make validate      # lint + type + security + test (blocks noted in README)
make docs
dbt deps
dbt run
dbt docs serve --port 8080
```

## Architecture snapshot

- **Layered stack**: Plugin Layer (scaffolding + lifecycle helpers) → Protocol Layer (Singer tap/target frameworks) → Orchestration Layer (workflow engine, executor) → Integration Layer (Meltano/Meltano projects). Foundation services (`flext-core`, `flext-cli`, `flext-quality`) underpin every layer.
- **Core services**: `FlextMeltanoService` (plugin discovery, lifecycle), `FlextMeltanoAdapter` (Singer tap/target execution), `FlextMeltanoExecutor` (pipeline orchestration with conditional logic, parallelism, state, retries).
- **Configuration**: `meltano.yml` templates plus Flext-specific YAML bridging (pipelines, quality thresholds). `FlextMeltanoService.discover_plugins` and `FlextMeltanoAdapter.run_pipeline` weave Singer taps and targets into production flows.
- **Integration**: Works with `flext-core`, `flext-cli`, `flext-meltano` plugin registry, and Singer-based `flext-tap-*`/`flext-target-*` packages; zero custom Singer/DBT code outside of this project per CLAUDE.

## Key features

- Complete Singer protocol support (tap/target frameworks, schema discovery, state management, incremental sync, batch processing).
- Plugin development toolkit with scaffolding, dependency resolution, automatic docs, and discovery/validation pipelines.
- Workflow engine supporting multi-pipeline orchestration, resource pooling, conditional logic, monitoring, and failure recovery.
- Docker/Kubernetes deployment recipes, Meltano docs generation (`dbt docs generate` + `dbt docs serve`), and instrumentation tasks baked into `make` scripts.
- Quality automation triggered by `make validate`/`make docs` plus `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` artifacts.

## Resources

- [Project README](../../flext-meltano/README.md)
- [Project CLAUDE](../../flext-meltano/CLAUDE.md) for zero-tolerance rules (no custom Singer/DBT code, registry-driven flows)
- `flext-meltano/docs/` for architecture, configuration, development, integration, troubleshooting, and guides
- Related `reports/` artifacts: `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*`
- Related projects: `flext-core`, `flext-cli`, `flext-quality`, `flext-dbt-*`, `flext-plugin`, and Singer-based taps/targets

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-meltano/issues>
- Discussions: <https://github.com/flext-sh/flext-meltano/discussions>
- Follow `docs/standards/README.md` and `CLAUDE.md` before changing code or docs so this entry stays aligned with the portal.
