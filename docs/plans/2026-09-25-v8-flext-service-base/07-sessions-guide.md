# 07 — Mini-guide: refactoring with FLEXT, CA and DI on the base libraries

<!-- TOC START -->

- [0. Before you start](#0-before-you-start)
- [1. What each library gives you](#1-what-each-library-gives-you)
- [2. Layout of an `internal_flext` project](#2-layout-of-an-internal_flext-project)
- [3. CA and DI recipe](#3-ca-and-di-recipe)
- [4. Refactoring fast without breaking](#4-refactoring-fast-without-breaking)
- [5. Failures](#5-failures)
- [6. Anti-patterns to remove](#6-anti-patterns-to-remove)
- [7. Adoption PR checklist](#7-adoption-pr-checklist)
- [8. Where to record](#8-where-to-record)

<!-- TOC END -->

For sessions that migrate FLEXT members (ldap, ldif, meltano, taps, targets, dbt, web,
auth, …) and external consumers declared `internal_flext` (for example ai-hub and
cosmos-\*), using `flext-core`, `flext-cli`, `flext-tests` and `flext-infra`. The
normative contract is `03-contract.md`; the laws are `04-rules.md`. This is the
practical path: what to use, in which order, with which tool.

## 0. Before you start

1. **Check your project kind.** FLEXT layout and laws apply only to `internal_flext`. An
   `internal` project or a `third_party_fork` follows its own contract or its upstream.
2. **Check what is available:**

   | Piece | Where | Available |
   |---|---|---|
   | `c/t/p/m/u` and `r/e/x/h/d/s`, `FlextService`, `FlextContainer`, `settings`/`config` | flext-core | Today |
   | Protocol-typed field validated by `isinstance` | Any service | Today (service JSON Schema fails until S1) |
   | `t.Port[P]`, validated runtime seeds, hook read through `p.RuntimeBootstrapProvider`, `unwrap` with cause | flext-core | After S1 |
   | Truthful container (duplicate and empty names fail, reserved names) | flext-core | After S2 |
   | Protocol-keyed container and `FlextService.compose(container)` | flext-core | After S2b, only if its typing spike passes |
   | `u.service_operations(Service)`, `m.ServiceOperation` | flext-core | After S3 |
   | Truthful `p.Service` | flext-core | After S4 |
   | Declarative routes `m.Cli.ResultCommandRoute`, `register_result_routes` | flext-cli | Today |
   | `cli.service_routes(Service, provide=…)` (lazy derived CLI) | flext-cli | After S5 |
   | Typed `FlextTestsServiceBase`, `isolated_test_runtime(build=…)` for port services | flext-tests | After S6 |
   | Contract scaffold, adoption detection rules, derived NS-LAYOUT | flext-infra | After S7 |

3. **Work in your own lane:** `~/flext-work/<slug>/<repo>` on a branch from
   `origin/<integration>`, then `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make setup`.
   Never in the primary checkout.
4. **Read the lane's `make help`:** it lists the verbs that apply there (`setup`, `gen`,
   `mod`, `fix`, `fmt`, `check`, `test`, `build`, `docs`, and the lock verb).

## 1. What each library gives you

### flext-core (base; every project depends on it)

- Declarations `c` (constants), `t` (aliases), `p` (protocols and ports), `m`
  (Pydantic 2 models with presets), `u` (utilities). Access only through these
  letters; never `import pydantic` outside the core.
- Results and errors: `r[T].ok(v)`, `r[T].fail(msg, exception=exc)`,
  `r[T].fail_op(operation, exc)`; factories `e.fail_validation`, `e.fail_not_found`,
  `e.fail_operation`, `e.fail_type_mismatch`.
- Service `s` (`FlextService[T]`) with `settings`, `context`, `container`, `logger`,
  `track()` from its runtime.
- Config and settings: `from <package> import config, settings`, then `config.<Ns>.*`
  (facts) and `settings.<Ns>.*` (knobs).
- `FlextContainer`: used only at the root (`api.py`).

### flext-cli (transport; CLI and file I/O)

- Facade `cli` (`from flext_cli import cli`) and `FlextCli`.
- App and commands: `cli.create_app_with_common_params(name=…, help_text=…)`,
  `cli.register_result_routes(app, routes)`, `cli.execute_app(app, prog_name=…)` returning
  `p.Result[bool]`, `cli.finalize_result(result) -> int`.
- Declarative route: `m.Cli.ResultCommandRoute(name, help_text, model_cls, handler)`
  (live example: `flext_infra/services/cli_routes_refactor.py`).
- Parameters from a model: `cli.model_command(Model, handler)` builds options from the
  fields, skips `exclude=True`, validates with `model_validate`.
- After S5: `cli.service_routes(Service, provide=…)` builds every route from the
  operations.
- `u.Cli.*` utilities for YAML, TOML, JSON, config, tables and output; never import
  Typer, Click or Rich directly.

### flext-tests (tests; every suite depends on it)

- The project's `tests/base.py`: `class TestsFlext<X>ServiceBase(FlextTestsServiceBase)`
  with the classmethod `runtime_bootstrap_options` returning the project's test settings.
  The core does not declare it as a base method, so no `@override` is required.
- Port services in tests: build them with real adapters (pure DI) or, after S6, pass the
  constructor to `isolated_test_runtime(build=…)`; `fetch_global()` cannot build them.
- Matchers `tm.that(value, eq=…, has=…, lacks=…)`, `tm.ok(result)`, `tm.fail(result, …)`;
  helpers `u.Tests.assert_success`/`assert_failure`.
- Plugin fixtures: `clean_container`, `settings`, `settings_factory`, `test_runtime`,
  `reset_settings`; isolation with `Service.isolated_test_runtime(**overrides)`.
- Real containerized services for integration tests: `flext_tests/docker.py`.

### flext-infra (build machinery; never a runtime dependency)

- Make cycle: `setup → gen → mod → gen → gen → fix → fmt → check → test → build`.
- Generated files (`__init__.py` lazy exports, facets, `pyproject`): only through
  `make gen`.
- `make check` gates: lint, types, `silent-failure`, `tier-whitelist`, namespace and
  more; suspensions live in `config/codegen.yaml` (`make.check_gate_suspensions`).
- Mass refactoring: rules in `flext-infra/src/flext_infra/codemod/rules/<id>.yml` with a
  fixture `codemod/tests/<id>-test.yml`, applied by `make mod`;
  `flext-infra refactor apply-renames --csv <old,new.csv> --roots <dir>…` (checks without
  `--apply`, writes with it); also `propagate-signatures`, `modernize-pydantic`,
  `census`.
- New projects: `codegen new`; after S7 the scaffold follows the contract.

## 2. Layout of an `internal_flext` project

```text
src/<package>/
├── __init__.py                 # GENERATED (make gen): lazy exports; never edit
├── constants.py typings.py protocols.py models.py utilities.py   # generated facets
├── _constants/ _typings/ _protocols/ _models/ _utilities/        # declarations (data only)
├── _settings.py _config.py     # namespace settings and config
├── base.py                     # class Flext<X>ServiceBase(s[...]) + s = … (runtime hook)
├── services/                   # use cases (one per file; one top-level class)
├── adapters/                   # port implementations (concrete infrastructure)
├── api.py                      # composition root (only if services are composed)
└── cli.py                      # transport (only with a console script and operations)
```

## 3. CA and DI recipe

1. **Inventory** without editing: `code-review-graph status --json` (then `update --brief`
   if stale) and `impact` on the services you will touch; list hand-rolled singletons,
   `settings or X.fetch_global()`, `SkipValidation` and no-op `main()`.
2. **Ports:** for each external dependency of a use case, declare in `_protocols/` a
   `@runtime_checkable class <Port>(p.Base, Protocol)` with the minimal consumed
   capability, published as `p.<Ns>.<Port>`.
3. **Models:** request and response of every operation in `_models/`, on an `m.*` preset
   (strict at the boundary); never a `dict` as a contract.
4. **Services:** `class Flext<X><Case>(s[m.<Ns>.<Result>])`; import `p`, `t` and `m` **at
   runtime** in the service module (Pydantic resolves annotations at class creation;
   `model_rebuild` is forbidden); dependencies as
   `name: t.Port[p.<Ns>.<Port>] = m.Field(exclude=True, description=…)` with a plain
   Protocol class (before S1, annotate with `p.<Ns>.<Port>` and the same `m.Field`); each
   public method is an operation
   `def verb(self, request: m.<Ns>.<Req>) -> p.Result[m.<Ns>.<Res>]` with a one-line
   docstring; no global `settings`/`config` reads, no other service's `fetch_global()`.
5. **Adapters** in `adapters/`: implement the ports with the project's owned libraries
   (tier-whitelist); receive settings through the constructor; no I/O at construction.
6. **Root (`api.py`):** `class Flext<X>(<services>)` as the MRO facade and
   `<alias> = Flext<X>(port=Adapter(settings=settings.<Ns>))` (pure DI); a shared adapter
   is a variable passed to several constructors; `container.bind` plus `compose` only
   exist if S2b passes.
7. **CLI (`cli.py`, template `cli.py.j2`: a `Flext<X>Cli` class plus `main()`):**
   today a tuple of `m.Cli.ResultCommandRoute` with
   `cli.register_result_routes(app, routes)`;
   after S5 `cli.register_result_routes(app, cli.service_routes(Flext<X>, provide=…))`
   (routes from the class; instance only when a command runs; `--help` builds no
   adapter); `main()` returns
   `cli.finalize_result(cli.execute_app(app, prog_name=…))`; Singer connectors keep
   ADR-006.
8. **Tests** through public facades: build the service with **real** adapters
   (`tmp_path`, real process, containerized service through the harness); assert with
   `tm`: happy path, failure with its cause, non-conforming port raising
   `ValidationError`; no frozen config values.
9. **Gates and landing:** the full Make cycle, PR, CI, merge commit, proof on the merged
   SHA; your own consumers revalidated before merge.

## 4. Refactoring fast without breaking

- **Countable backlog (after S7):** `flext-infra` detection rules list, per member,
  infrastructure built inside services, `PrivateAttr(default_factory=<facade>)`,
  `settings or X.fetch_global()` and hand-rolled singletons.
- **Repeated pattern:** one ast-grep rule with a fixture, applied by `make mod`; reuse the
  catalog; prefer the most general rule; checkpoint commit first.
- **Symbol renames:** an `old,new` CSV, `flext-infra refactor apply-renames --csv …
  --roots …` to check, the same with `--apply`, then revalidate.
- **Signature changes:** `flext-infra refactor propagate-signatures` with its YAML rules.
- **Contract contraction:** consumers first (R17): each consumer declares what it uses,
  merges, and only then the base shrinks.
- **Diverging generated file:** fix the generator or template and run `make gen` twice;
  never edit the projection.
- **Locks:** a consumer sees a new base only after refreshing its lock with the lock verb
  from its `make help`, in its own PR.

## 5. Failures

- Inside a service: `return r[T].fail("…", exception=exc)` or an `e.fail_*` factory,
  always with the cause. Outside a result: raise the typed `e.*` exception `from exc`.
- Never `except …: return None/""/{}/[]/default/r.ok(...)`, `contextlib.suppress`
  around an owner call, `unwrap_or(sentinel)` to hide a failure,
  `getattr(x, "member", default)` on a typed member, or "log and continue".

## 6. Anti-patterns to remove

| Anti-pattern | Replacement |
|---|---|
| `SkipValidation` on a dependency | `t.Port[p.X]` with `exclude=True` |
| `settings or X.fetch_global()`; `__init__` redeclared for settings | The base's `runtime_bootstrap_options` hook plus injection by the root |
| Hand-rolled singleton (`fetch_instance`, `_instance`) | One instance in `api.py` |
| A service calling `OtherService.fetch_global()` | An injected port |
| Infrastructure built inside a service (`FlextApi(runtime_settings=…)` in a method, `PrivateAttr(default_factory=<facade>)`) | A port injected by the root |
| `model_copy(update=)` to build a validated object | Constructor or `model_validate` |
| No-op `main()`, empty facade | A derived CLI, or no file at all (R18) |
| A protocol inheriting members the service does not implement | Declare only what is implemented and consumed |
| Tests with mocks, patches or fakes | Real adapters and public facades |

## 7. Adoption PR checklist

- [ ] Ports in `_protocols/`, `@runtime_checkable`, minimal capability.
- [ ] Services with ports and parameters only; no global reads; no cross `fetch_global`.
- [ ] `api.py` is the only root; `cli.py` derived and real, or absent.
- [ ] Tests through facades with real adapters and failure paths.
- [ ] `make gen` ×2 fixed point, `fix`, `fmt`, `check`, `test`, `build` green in the
  lane.
- [ ] The project's consumers revalidated; lock refreshed when the base changed.
- [ ] Docs and docstrings in the same PR; residue (section 6) removed.
- [ ] Adoption bead closed with four sources; lane retired.

## 8. Where to record

- Base epic: `flext-4jtcb`; each adoption gets its own bead "V8 adoption: <member>"
  linked to the epic.
- Versioned guide: `flext-core/docs/guides/service-patterns.md` (after S1).
- Decision: `docs/architecture/adr/019-service-contract-ports-operations.md`.
- A contract doubt becomes a question to the operator (D-ASK), never a local variant of
  the pattern.
