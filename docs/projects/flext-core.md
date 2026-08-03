# FLEXT Core

FLEXT Core is the typed foundation library of the FLEXT platform. It provides the railway-oriented result contract
(`r[T]`), the canonical short-alias facades (`c`, `m`, `t`, `p`, `u`, `r`, `s`, `e`, `x`, `d`, `h`), the DI container,
the CQRS dispatcher, and the shared Pydantic models, protocols, and utilities that every downstream `flext-*` project
builds on. Package description: "Enterprise Foundation Framework — Modern Python 3.13 + Clean Architecture".

## Status & health

- **Version**: 0.20.0-dev (current development cycle)
- **Python**: 3.13+ only
- **Quality gate**: `make check PROJECT=flext-core` (Ruff + type checks) and `make val` for the full pipeline
- **Role**: root of the dependency chain; no runtime dependency on any other `flext-*` package (stdlib-first design)

### Quality signals

- Strict typing enforced by project policy: no `Any`, no bare `object`, no `cast` shortcuts
- Facets `c`/`t`/`p`/`m` are declaration-only; behavior lives in `u`, `cli`, `api`, `base`, and `services/*` (see root
  `AGENTS.md` U17)
- Config and settings are validated singletons (`config.<Ns>.*`, `settings.<Ns>.*`) consumed directly — no proxies or
  forwarding accessors
- Generated documentation and module maps live under `flext-core/docs/api-reference/`

## Quick start

```bash
pip install flext-core
```

```python
from flext_core import FlextDispatcher, p, r


class CreateUserHandler:
    def handle(self, message: p.Routable) -> p.Result[str]:
        return r[str].ok(f"created:{message.username}")


dispatcher = FlextDispatcher()
registered = dispatcher.register_handler(CreateUserHandler())
assert registered.is_success
```

The dispatcher routes a message to the registered handler whose declared `message_type` matches, and every fallible step
returns `r[T]` so callers chain with `.map`/`.flat_map` instead of raising. More bootstrap examples live in `flext-
core/examples/` (`ex_01_flext_result.py` through dispatcher and settings walkthroughs).

## Architecture & modules

`src/flext_core/` is organized in strict tiers; lower tiers never import higher ones.

- **Foundation**: `constants.py`, `typings.py`, `protocols.py` (+ `_constants/`, `_typings/`, `_protocols/` split files)
  — shared constants, type aliases, and protocol hierarchies.
- **Domain**: `models.py` (`_models/`), `exceptions.py` (`_exceptions/`) — Pydantic v2 models and the exception
  taxonomy; models are declaration-only.
- **Runtime & DI**: `container.py` (`_container_parts/`), `context.py`, `runtime.py`, `service.py`, `settings`
  (`_settings.py`) — `FlextContainer` DI wiring, structured logging, and the validated settings singleton.
- **Application**: `dispatcher.py`, `registry.py`, `handlers.py`, `decorators.py`, `mixins.py` — CQRS dispatch, handler
  registry, and the mixin/decorator toolkit.
- **Entry point**: `__init__.py` exports the facade classes (`FlextResult`, `FlextDispatcher`, `FlextContainer`,
  `FlextModels`, …) plus the short aliases `c`, `m`, `t`, `p`, `u`, `r`, `s`, `e`, `x`, `d`, `h` and the
  `config`/`settings` singletons.

### Key architectural patterns

- **`r[T]` railway contract**: `FlextResult` with `r[T].ok(value)` / `r[T].fail(error)`; every fallible public path
  returns a result instead of raising.
- **Facade aliases**: one canonical alias per responsibility (`m` models, `u` utilities, `p` protocols, …); downstream
  projects subclass these via MRO to compose their own facades.
- **Lazy exports**: `lazy.py` (`build_lazy_import_map`, `install_lazy_exports`) keeps `import flext_core` cheap while
  exposing the full surface.
- **DI container**: `FlextContainer` auto-registers core services (settings, logger, context) and shields consumers from
  `dependency-injector` internals.

## Testing & quality

- `make check PROJECT=flext-core`: Ruff linting plus type checks (pyrefly/mypy)
- `make test PROJECT=flext-core`: pytest suite (see `reports/pytest/` for the latest run evidence)
- `make val`: full validation pipeline; consult `reports/coverage-scan-*` for the current coverage snapshot rather than
  trusting any fixed number in docs
- Tests exercise only the public surface (facade aliases and exported classes), per the workspace testing law in
  `AGENTS.md` (U16)

## Resources

- [Project README](../../flext-core/README.md) (auto-generated module map and operation flow)
- [Workspace AGENTS.md](../../AGENTS.md) — FLEXT engineering law (U2–U18)
- `flext-core/examples/` — runnable examples for results, settings, logging, and dispatching
- `flext-core/docs/api-reference/` — generated API documentation
- Reports: `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-core/issues>
- Keep this page aligned with the workspace governance in root `AGENTS.md` and `docs/GOVERNANCE.md` when proposing doc
  changes.
