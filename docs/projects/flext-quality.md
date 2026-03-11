# FLEXT Quality

<!-- TOC START -->

- [Status & metrics](#status-metrics)
- [Quick start](#quick-start)
- [Architecture & patterns](#architecture-patterns)
- [Quality & compliance](#quality-compliance)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT Quality (v0.9.9) is the centralized code quality analysis framework for the FLEXT ecosystem. It runs static analysis, metrics collection, reporting, and quality gates so every other project can validate architecture, tests, and security through a common protocol.

## Status & metrics

- **Version**: 0.9.9; 1.0.0 release prep focuses on accessibility/integration fixes
- **Python**: 3.13+ only
- **Tests**: ~250 total (unit, integration, CLI); running `make test` is currently blocked by `flext-core` import issues (FlextModels.BaseModel missing)
- **Coverage**: 96% target per README, but automated coverage gates cannot run until the import blockers are resolved
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + coverage + docstring checks) is blocked by import/accessibility errors; lint/type/security commands individually succeed
- **Type safety**: Pyrefly/MyPy strict modes are enforced; zero `Any`/`cast`/`# type: ignore` allowed
- **Security**: Bandit and pip-audit scans configured; pipeline currently defers final auditing until the FlextCore dependency stabilizes

## Quick start

```bash
git clone https://github.com/flext-sh/flext-quality.git
cd flext-quality
make setup
make check      # lint + type-check are expected to pass
make validate   # currently blocked until FlextModels imports are available
```

```python
from flext_quality import FlextQualityService

service = FlextQualityService()
result = service.create_project(
    name="my_project",
    project_path="/src/my_project",
    _min_coverage=80.0,
    _max_complexity=10,
)

if result.is_success:
    project = result.value
    print(project.name, project.min_coverage)

from flext_quality import FlextQualityCodeAnalyzer  # accessible via direct import

analyzer = FlextQualityCodeAnalyzer("/src/my_project")
analyzer.analyze_project()
```

## Architecture & patterns

- **Facade**: `FlextQualityService`/`FlextQualityCliService` expose CLI status/check/validate commands balanced with the registry-based rules engine.
- **Core layers**: Tier 0 (`constants`, `typings`, `protocols`); Tier 1 (`models`, `utilities`); Tier 2 (`integrations`, `rules`, `hooks`, `rules.engine`); Tier 3 (`api`, `services`, `cli`, `mcp`). Import discipline ensures lower tiers never depend on higher ones.
- **Rules engine**: YAML-driven ACA (Architecture/command Analysis) registry with 11 categories, providing consistent patterns for dangerous commands, type verification, and code quality violations plus hooks for Claude integrations.
- **Integration**: depends on `flext-core` (r, FlextContainer, FlextModels), connects to `flext-cli` for consistent output, and feeds `flext-web` dashboards once the CLI stabilizes.

## Quality & compliance

- **Validation commands**: `make lint`, `make type-check`, `make security`, `make check`, `make validate`, `make quality-analysis`, `make report`, `make diagnose`.
- **Zero-tolerance policy**: No `Any`, no `cast`, no `TYPE_CHECKING`, no exception-based results anywhere; all APIs return `r[T]` (r alias `r`).
- **Testing**: Unit + integration + CLI tests exist, but `pytest` runs fail because FlextModels.BaseModel isn’t accessible; these failures are noted in the README and block `make validate`.
- **Security**: Bandit + pip-audit configured, plus `flext-quality` supplies hooks/validators to enforce dangerous-command detection, type rules, and architecture compliance in other workspaces.

## Resources & references

- [Project README](../../flext-quality/README.md) for status, architecture, and roadmap
- [Project AGENTS.md](../../flext-quality/AGENTS.md) for zero-tolerance directives and command guidance
- `flext-quality/docs/` for getting started, architecture, guides, and troubleshooting (mirrors doc comments in README)
- `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` once blocked gates reopen
- Related projects: `flext-core`, `flext-cli`, `flext-web`, `flext-observability`, `flext-quality/rules`, Singer-based `flext-tap-*` / `flext-target-*`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-quality/issues>
- Discussions: <https://github.com/flext-sh/flext-quality/discussions>
- Follow `docs/standards/README.md`, the workspace AGENTS.md, and the central portal checklist before touching docs or code so the portal stays accurate.
