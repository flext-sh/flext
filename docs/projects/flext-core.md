# FLEXT Core


<!-- TOC START -->
- [Status & health](#status-health)
  - [Quality signals](#quality-signals)
- [Quick start](#quick-start)
- [Architecture & modules](#architecture-modules)
  - [Key architectural patterns](#key-architectural-patterns)
- [Testing & quality](#testing-quality)
- [Resources](#resources)
- [Support & issues](#support-issues)
<!-- TOC END -->

FLEXT Core is the dispatcher-centric foundation library for the FLEXT platform. It delivers railway-oriented error handling, context-aware dependency injection, CQRS dispatching, and domain primitives that every downstream project reuses.

## Status & health

- **Version**: 0.10.0 (December 2025)
- **Python**: 3.13+ only
- **Tests**: 2 820 passing (see `reports/pytest` artifacts)
- **Coverage**: 81.41% (`reports/coverage-scan-*` snapshot)
- **Quality gate**: `make validate` (runs Ruff, Pyrefly, Bandit, `make test`, coverage, docstring checks)

### Quality signals

- Ruff: zero violations
- Pyrefly (Pyright-based): zero errors with strict mode
- Bandit: zero high/medium findings
- Type safety: all modules import `flext_core.typings` aliases (no `Any`, no `TYPE_CHECKING`, no `cast`, no `# type: ignore`)

## Quick start

```bash
pip install flext-core
```

```python
from flext_core import FlextContainer, FlextDispatcher, FlextResult

container = FlextContainer.get_global()
dispatcher = FlextDispatcher()

def handler(value: str) -> FlextResult[str]:
    if "@" not in value:
        return FlextResult[str].fail("invalid email")
    return FlextResult[str].ok(value.upper())

dispatcher.register_handler(str, handler)
result = dispatcher.dispatch("user@example.com")
assert result.is_success
```

The project ships CLI helpers inside `examples/` and `docs/QUICK_START.md` for more realistic bootstraps.

## Architecture & modules

FLEXT Core follows strict layering so that lower tiers never import higher tiers.

- **Tier 0 (Foundation)**: `constants.py`, `typings.py`, `protocols.py` define shared constants, centralized type aliases, and protocol hierarchies.
- **Tier 1 (Domain facades)**: `models.py`, `utilities.py`, `_models/`, `_utilities/` expose Pydantic models, helpers, and short alias facades (`m`, `u`).
- **Tier 2 (Runtime + DI)**: `container.py`, `context.py`, `decorators.py`, `runtime.py`, `service.py` build the `FlextContainer`, `FlextRuntime`, and the structured logging/context bridge.
- **Tier 3 (Application)**: `dispatcher.py`, `registry.py`, `handlers.py`, `services/` compose the CQRS dispatcher, handler registry, and auto-registered services.

### Key architectural patterns

- **FlextResult[T]**: the railway result for success/failure chaining (`r[T]` alias) and monadic helpers.
- **Dependency injection bridge**: `FlextRuntime` + `FlextContainer` re-export `Provide`/`inject`, auto-register the core services (`config`, `logger`, `context`), and shield projects from `dependency-injector` details.
- **Protocol-first**: all interfaces accept `flext_core.protocols` namespaced types, zero `TYPE_CHECKING`, zero circular imports.
- **Short-alias discipline**: `r`, `t`, `c`, `m`, `p`, `u`, `e`, `x`, `d`, `h` for succinct runtime code.

## Testing & quality

- `make check`: Ruff linting + Pyrefly type-checks
- `make test`: pytest suite with ~2 820 tests
- `make validate`: full pipeline (`make check`, `make format-check`, `make complexity`, `make docstring-check`, `make security`, `make test`)
- `pyproject.toml`/`ruff-shared.toml` enforce ZERO tolerance for `Any`, `cast`, `TYPE_CHECKING`, and ensure `PYI042` is ignored only for short aliases.

## Resources

- [Project README](../../flext-core/README.md)
- [CLAUDE guidelines](../../flext-core/CLAUDE.md)
- `docs/QUICK_START.md`, `docs/architecture/overview.md`, `docs/api-reference/` inside `flext-core`
- `examples/` demonstrating dispatchers, processors, and DTOs
- Reports: `reports/coverage-scan-20260202_144808`, `reports/lint-output/*`, `reports/pytest/*`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-core/issues>
- Use the `docs/standards/` checklist when proposing doc changes so this brief stays consistent with the engineering portal.
