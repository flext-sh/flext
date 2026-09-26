# 01 — Evidence

<!-- TOC START -->

- [1. Service and runtime in flext-core](#1-service-and-runtime-in-flext-core)
- [2. Container](#2-container)
- [3. flext-core fail-soft inventory](#3-flext-core-fail-soft-inventory)
- [4. flext-cli](#4-flext-cli)
- [5. flext-infra](#5-flext-infra)
- [6. flext-tests](#6-flext-tests)
- [7. Consumer blast radius](#7-consumer-blast-radius)
- [8. Documentation and governance](#8-documentation-and-governance)
- [9. CI, lanes and fleet state](#9-ci-lanes-and-fleet-state)
- [10. Sibling plans that need the same base](#10-sibling-plans-that-need-the-same-base)

<!-- TOC END -->

Measured on 2026-09-25 at the `0.12.0-dev` tips (`flext-core` `c47ea7d79`). Sources:
five read-only survey agents, runtime spikes in the workspace environment (Python
3.13.15, Pydantic 2.13.5, pydantic-core 2.46.5), direct reading, `gh` and `bd`.

## 1. Service and runtime in flext-core

- `service.py:31` `class FlextService[TDomainResult = p.Base](x)`; config `:34-42`
  (`strict`, `arbitrary_types_allowed`, `extra="forbid"`, `validate_assignment`).
  `fetch_global()` (`:54-69`) builds `cls()` with no arguments; `with_settings()`
  (`:78-85`) returns `cls(runtime_settings=settings.clone())`; `execute()` (`:87-93`)
  raises `NotImplementedError`.
- `mixins.py:20` `FlextMixins(m.ArbitraryTypesModel)` is `x`; `runtime_settings`
  (`:30-38`) and `initial_context` (`:47-55`) are
  `Annotated[p.X | None, t.SkipValidation]`; the runtime is built lazily by
  `u.build_service_runtime(self)` (`:151-157`).
- `_models/service.py`: `ServiceRuntime` (`:31-75`) and `RuntimeBootstrapOptions`
  (`:77-187`) skip validation on every dependency; `validate_wire_packages` (`:177-187`)
  replaces an invalid list with `None`.
- `_utilities/model_options.py:20-76` reads the source through `getattr` probes (`:38`,
  `:42-57`, `:58-64`); only one test declares the probed `runtime_dispatcher` /
  `runtime_registry` attributes (`tests/unit/test_service_bootstrap.py:38,141,156`).
- `_utilities/model_runtime.py:95-103` turns dispatcher failure into `None`; `:233` uses
  `getattr(runtime_container, "context", None)`. Callers of `build_service_runtime`:
  `mixins.py:156`, `registry.py:148`, `examples/ex_11_flext_service.py:72,95-96`.
- `runtime_bootstrap_options()` is implemented by about 40 bases (`src/*/base.py`,
  `tests/base.py`, `flext_tests/base.py:71-74`) and declared nowhere in the core.
- `_protocols/service.py:117-170` `p.Service` declares `service_info`, `valid`,
  `validate_business_rules`, `ok`, `fail_op`; `FlextService` implements none.
- `_result/unwrap.py:18-22` raises `RuntimeError(msg)` without `from`.
- `p.RuntimeBootstrapOptions` exists
  (`_protocols/_context_parts/flextprotocolscontext_part_03.py:21`); `t.InstanceOf` and
  `t.SkipValidation` exist; there is no `Port` symbol.

Runtime measurements:

| Check                                                                                                  | Result                                          |
| ------------------------------------------------------------------------------------------------------ | ----------------------------------------------- |
| `isinstance(service, p.Service)`                                                                       | **False**                                       |
| `FlextSettings` / `FlextContext` / `FlextContainer` satisfy `p.Settings` / `p.Context` / `p.Container` | True                                            |
| `model_json_schema()` of any `FlextService` subclass                                                   | raises `PydanticInvalidForJsonSchema`           |
| `@runtime_checkable` Protocol field with `arbitrary_types_allowed`                                     | validated by `isinstance`                       |
| `type Port[P] = Annotated[P, SkipJsonSchema()]`                                                        | validates and leaves the JSON Schema            |
| `Field(exclude=True)` inside the alias                                                                 | ignored with `UnsupportedFieldAttributeWarning` |

## 2. Container

- `container.py:83-91` global singleton via `__new__`; `:175-214` string resolution;
  `:301-304`, `:316-321`, `:355-361` `bind`/`factory`/`resource` silently `return self`
  on an empty or duplicate name; `:570-596` `shared(auto_register_factories=True)` does
  nothing when the caller module is unresolved; `:598-610` the scan skips non-callables;
  `:253-263` `_internal_registrations` only tracks services (the LOGGER factory is
  re-registered by `scope()`).
- Only `flext-core` calls `bind`/`resolve` (14 sites). Three members set
  `_container_type = FlextContainer`; `flext_plugin/api.py:30` builds
  `FlextContainer()`.

## 3. flext-core fail-soft inventory

120 `except` clauses: 42 genuine fail-soft, 6 lose the cause, 72 legitimate.

- V7 items confirmed: CQRS pagination (`_models/cqrs.py:122-129`); registry `getattr`
  (`registry.py:374-381`, with `:196-209`); mapper `""`
  (`mapper_access_part_02.py:81-82`, `mapper.py:98`); handler `None`
  (`flexthandlers_part_07.py:130-138`); context `{}` (`context_state.py:38-46`);
  beartype sentinel loss (`beartype_engine.py:98-99` and visitors); metadata `"0.0.0"`
  (`_utilities/project_metadata.py:55-62`). "Container owner None" does not exist.
- Also genuine: `dispatcher.py:58-80` (`publish` returns `ok(True)`), `:117-120`
  (`continue`), `checker_part_02.py:84-93` (fail-open), `registry.py:120-129`,
  `:325-332`, `:473-485`, `context_lifecycle.py:97-138`, `context_crud.py:103-107`,
  `parser_coerce.py:99-107`, `conversion.py:88-108`, `parser_targets_part_02.py:45-63`,
  `logging_config_part_01.py:140-146`, `_decorators/_railway.py:143-185` and `:46-53`,
  `_utilities/model.py:69-71` (`u.dump` via `unwrap_or`).
- Beartype sites belong to the live lane `flext-edcqq`
  (`~/fleet-closure-lanes/core-regen/flext-core`, uncommitted since 2026-09-25 11:29Z,
  no file overlap with this plan).

## 4. flext-cli

- Typer on Click; only `_utilities/framework.py:12-15` imports them.
- `FlextCliCli`: `create_app_with_common_params` (`part_02:63`), `register_command`,
  `execute_app(app, *, prog_name, args=None) -> p.Result[bool]` (`part_04:17-22`),
  `model_command(model_cls, handler, settings=None)` (`part_03:26-48`, options from
  `model_fields`, skipping `exclude=True`), `register_result_routes` (`part_05:131`),
  `finalize_result` (`part_05:139`). Route model `m.Cli.ResultCommandRoute`
  (`_models/_base/flextclimodelsbase_part_03.py:108-133`).
- Dead duplicate builder `_utilities/model_commands.py:36-152` (test-only consumer).
- Fail-soft: `part_02:27-29`, `options_part_02:32-37`, `services/cli_params.py:32-38`,
  `part_03:75-80`; annotation resolver falls back to `str` (`part_01:70-72`); the
  executor never prints `result.value` (`part_05:91-103`); `_ModelCommand` lets
  `ValidationError` escape (`part_01:44-46`).
- The `flext-cli` console script is a no-op stub (`cli.py:8-11`).
- There is no `refactor` in `flext-cli`; the owner is `flext-infra refactor`
  (`services/cli_routes_refactor.py:37-137`: `apply-renames` with `--csv`, `--roots` and
  `--apply`, `propagate-signatures`, `mod`, …), exposed by `make mod`.
- Consumers of `register_result_*`: flext-infra, flext-meltano, flext-quality,
  flext-web, flext-oracle-oic.

## 5. flext-infra

- Scaffold templates `templates/project/base/src/{api,cli,base}.py.j2` and
  `services/ping.py.j2` (`config/codegen.yaml:2111-2130,2172-2176`) apply only to
  `codegen new`; `make gen` never writes `src/*`.
- NS-LAYOUT demands `base`/`api`/`cli` plus `services/`
  (`validate/namespace_validator.py:161-182`); that is why the kernel carries
  hand-written skeletons (WIP `6b96c31a2`, `bd5e961d0`) and a no-op console script
  (`pyproject.toml:52`).
- Gates: registry `_constants/check.py:48-97`; `silent-failure` and `tier-whitelist`
  block; suspensions in `config/codegen.yaml:348-363` (duplication, codemod, boundary,
  namespace, runtime-census).
- Codemod: 127 rule files, 173 ids; `ban-skip-validation`
  (`pydantic-boundary.yml:30-53`) exempts `flext_core` and misses the
  `Annotated[..., t.SkipValidation]` form; `make mod` runs `ast-grep test` on fixtures
  before applying.
- Locks: members read the core through their lock; only the lock verb declared by the
  lane's `make help` (`deps` on the current `flext-core` Makefile) refreshes it.

## 6. flext-tests

`FlextTestsServiceBase` (`base.py:15-74`): `test_settings_type` falls back to
`FlextTestsSettings` on `None` (`:21-23`); `isolated_test_runtime` (`:53-69`) calls
`fetch_global()`; `_fixtures/settings.py:46-48` substitutes the core `s` via `getattr`.
Matchers: `tm.that` (`_utilities/_matchers/_that.py:549`), `tm.ok`/`tm.fail`
(`_utilities/_matchers/_result.py`).

## 7. Consumer blast radius

217 service subclasses in `src`; 150 `execute(self)`; 31 service-type `fetch_global()`
calls (mostly the `api.py` singleton); `SkipValidation` 26 in the core and 1 in infra; 9
direct `runtime_settings=` sites (OIC/WMS); 3 bases redeclare `__init__` for settings;
15 no-op `main()`; 5 skeleton facades; 7 hand-rolled singletons; 17 sub-protocols of
`p.Service` in 7 members (flext-web implements and calls `validate_business_rules`).

## 8. Documentation and governance

- ADRs 001–010, 014–018 exist; ADR-019 is next.
- flext-law `SKILL.md:43-47`: dependencies are provided explicitly by `api`; no string,
  reflection, service-locator or hidden-singleton resolution.
- `flext-core/docs/guides/service-patterns.md` is the canonical guide (silent on ports
  and roots); `dependency_injector_prompt.md` and
  `improvements/dependency-injection-audit.md` are stale;
  `architecture/overview.md:98-100` is wrong about `bind`; `using-flext-core.md` is
  generated from the root `docs/guides/`.
- Root contradictions: `settings-config-canonical-pattern.md:165-167` versus
  flext-law:44-45, and `:163` versus ADR-005:87-88.

## 9. CI, lanes and fleet state

- `flext-core` integration CI is red at `c47ea7d79` (run 36085803677): `silent-failure`
  5 (lane `flext-edcqq`) and `runtime-census` 166 (suspended; campaign
  `flext-0in0k.26`).
- Superproject `ec666f2c25` records gitlinks for 27 members that are not ancestors of
  the members' `0.12.0-dev` tips (`[WIP] … phase-1 wave` commits on
  `fix/phase1-wave-20260924`); a fresh workspace `make setup` fails at
  `_builtin_setup_submodules`. Recorded on `flext-itpd1.3`.
- Running `make` inside a member of a workspace demands a member-local `.venv`
  (`flext-x8gn6`); fleet validation therefore uses the root verbs, which orchestrate all
  32 projects with the workspace environment.
- The operator shell exports `VIRTUAL_ENV`/`UV_PROJECT_ENVIRONMENT` pointing at the
  primary checkout; every lane verb runs under
  `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT`.

## 10. Sibling plans that need the same base

- ai-hub plan v3, operator decision 4: ports as validated Pydantic fields, container
  resolution by Protocol, duplicate registration fails (phase 1.1, epic `aihub-5j4cw`).
- cosmos plan v13, step A0.5: `t.Port[P]`, a composition constructor,
  `CredentialsDirectorySource`, a DI guide. S1–S3 deliver the common part; the
  credentials source stays a candidate for a later base slice.
