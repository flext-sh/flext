# ADR-019 — Service Contract: Protocol Ports, Explicit Composition Root, Typed Operations

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
- [Rejected alternatives](#rejected-alternatives)
- [Verification contract](#verification-contract)
- [0.13 unified planning reconciliation (documentation only)](#013-unified-planning-reconciliation-documentation-only)

<!-- TOC END -->

- **Status:** PROPOSED — operator-approved plan V8, 2026-09-25; amended 2026-09-26 (pure
  DI definitive, S2b removed); becomes ACCEPTED when slices S1–S10 land with post-merge
  proof
- **Date:** 2026-09-25 (amended 2026-09-26)
- **Contract amendment, 2026-10-18:** request annotations use structural `p`/`t`
  contracts; the concrete validation model is declared once in existing handler
  metadata. Registry/handler migration is tracked in `flext-4jtcb.7`; this amendment
  does not claim that the migration or its integrated validation is complete.
- **Integrated so far (verified census 2026-09-30, code-level):** S1 — `flext-core` #499,
  merge `d65ba487f`, with the kernel fixes #502 `5ce5919a6` (enforcement), #503
  `2401cb21b` (lazy initialization), #504 `8de52fa6b` (`u.process` fail-loud).
  S2–S6 are also in the code (S7–S10 open, per epic `flext-itpd1.11`): truthful
  container (one `_registrations` bookkeeping, one
  private write path, empty/duplicate/reserved names raise `e.ValidationError`, reserved
  names out of `has`/`names`/`drop`, caller-unresolved `shared` raises, no
  `provide`/`wire` bridge — `src/flext_core/container.py`); lazy operations
  (`u.service_operations` + frozen `m.ServiceOperation`); truthful `p.Service`
  (`@runtime_checkable`, real surface inherited once, only `execute` added); derived CLI
  (`cli.service_routes(service_type, *, provide)` with `m.Cli.EmptyRequest` and
  execution-time `provide`); test base port path (`isolated_test_runtime(build=…)`);
  templates `api.py.j2`/`cli.py.j2`/`services/ping.py.j2` with the kernel free of fake
  facades (D1). Pending: S8/S9 fail-loud — at least `u.dump` via `unwrap_or`
  (`_utilities/model.py:71`, adversarial correction 10) — and S10 closure.
- **Target line:** FLEXT `0.12.0-dev`, forward baseline `0.13.0`
- **Scope:** `flext-core` (service base, container, operations), `flext-cli` (derived
  CLI), `flext-tests` (service test base), `flext-infra` (scaffold templates, detection
  rules, NS-LAYOUT), and every member and consumer that adopts the contract.
- **Complements:** ADR-005 (config/settings SSOT), ADR-006 (Singer thin drivers keep
  `Service().cli_main`), ADR-010 (facade roles), ADR-014 (canonical `cli.py main` and
  `api.py` composition-root singleton), ADR-015 (consumption law), ADR-018 (generator
  declarations).
- **Plan:**
  [`docs/plans/2026-09-25-v8-flext-service-base/`](../../plans/2026-09-25-v8-flext-service-base/00-index.md)
- **Tracking:** epic `flext-itpd1.11`, which absorbed epic `flext-4jtcb` (slices
  `flext-4jtcb.1`–`.12`; `.9`, the former S2b, is superseded by the 2026-09-26 pure-DI
  ruling). The transport surface (Decision 13) is epic `flext-itpd1.11.8`.
- **Amendment, 2026-10-24 (operator orders):** Decision 5 becomes the single transport
  contract (CLI, HTTP, Singer) derived from core operations. Decision 6 follows the
  ruling "core = composition root without a locator". Decision 13 is new. Old public
  signatures follow the deprecated-signature window (root `AGENTS.md`, tracker memory
  `operator-ruling-2026-10-24-deprecated-signature-window`).

## Context

`FlextService` is already a Pydantic model (`FlextService(x)`,
`x = FlextMixins(m.ArbitraryTypesModel)`), but measured on `flext-core` `c47ea7d79` its
contract was not true:

- runtime dependencies were typed `Annotated[p.X | None, SkipValidation]`, so nothing
  validated them, and `model_json_schema()` raised for every service;
- `fetch_global()` builds `cls()` with no arguments, so a service with a required
  dependency could not exist, and consumers reached collaborators through hidden
  singletons, contradicting flext-law ("dependencies … are provided explicitly by
  `api`");
- the per-project settings hook `runtime_bootstrap_options` is implemented by about 40
  bases but declared nowhere and read through `getattr` probes;
- `isinstance(service, p.Service)` was `False`, because `p.Service` declared members no
  service implements;
- `r.unwrap()` dropped the carried exception, and 42 fail-soft sites turned failures
  into defaults;
- `FlextContainer.bind/factory/resource` silently ignored duplicates and empty names;
- the kernel carried hand-written `api.py`/`cli.py`/`base.py` skeletons and a no-op
  console script only to satisfy the NS-LAYOUT gate. Measured 2026-10-24: 10 members
  carry a placeholder `main()` that returns 0 (api, auth, core, db-oracle, grpc, ldap,
  ldif, observability, oracle-wms, plugin), and 76 hand-written `ResultCommandRoute`
  constructions in 7 repositories duplicate what operation discovery derives.

The operator asked for `FlextService` to be the essential base that provides a typed API
and an automatic CLI for every member (plan V7), with fakes removed and real wiring.

## Decision

1. **Ports.** A dependency is a `@runtime_checkable` Protocol in `p` (extending
   `p.Base`, minimal capability). A service field declares it as
   `name: t.Port[p.X] = m.Field(exclude=True, description=…)`, where
   `t.Port[P]` supplies an instance-validation schema excluded from JSON Schema.
   Pydantic validates it by `isinstance` on construction and assignment, preserving
   the supplied instance. Current annotation support also resolves aliases, generic
   origins and concrete classes; it does not recursively validate generic arguments.
   This runtime support does not replace Protocol-based dependency declarations.
2. **Composition root — pure DI, definitive.** `api.py` is the only place that
   constructs adapters and port-bearing services, by constructor injection.
   `fetch_global()` remains only for port-free services. There is no Protocol-keyed
   container and no `FlextService.compose(container)` (operator ruling 2026-09-26; the
   conditional slice S2b is removed). The container stays a truthful registry of named
   infrastructure (S2), never a port resolver.
3. **Truthful runtime.** The settings hook is read through `p.RuntimeBootstrapProvider`
   (no new base method, so no fleet-wide `@override` sweep); runtime seeds are
   `t.Port[p.X | None]`; validated construction replaces `model_copy(update=)`;
   `unwrap()` chains the carried exception; the container rejects duplicate, empty and
   reserved registrations.
4. **Operations are the API.** A public instance method declared below `FlextService`
   takes nothing or one structural request Protocol, returns `p.Result[...]` and
   has a docstring. Request-taking operations declare their concrete Pydantic input
   model once with `@h.handler(command=m.Namespace.Request)`. The signature uses
   `p.Namespace.Request` or its `t` alias, never the concrete model as a type.
   `u.service_operations(Service)` discovers the original callable and its model
   metadata lazily, without `eval` or class-creation checks. Missing, ambiguous or
   incompatible metadata fails; there is no fallback to concrete annotations.
   Amendment 2026-10-24: an input-less operation may carry metadata
   (`@h.handler(command=None, default=True)`); `@h.query` marks a read-only
   operation; `m.ServiceOperation` records `public_name`, `kind`, `default` and the
   `output` type derived from `p.Result[X]`. The request Protocols are generated from
   the models by flext-infra, never hand-mirrored. The accepted 2026-10-28
   [model and service protocol projection](018-generator-declarations.md#model-and-service-protocol-projection)
   contract owns generation of the service's own structural callable surface and
   its request protocols, tracked by `flext-vjj1s.8`. It preserves the runtime
   operation metadata, schema binding and authored DI ports described here;
   projection is not a substitute for their real runtime acceptance.
5. **One transport contract (amended 2026-10-24).** Operations are the only public
   surface a transport serves. Adapters derive everything from
   `u.service_operations` and never take a hand-kept route, command or option list:
    - CLI: `flext-cli` exposes `cli.run(source)` and `cli.entry(source)`; a member's
      console script is `main = cli.entry(<facade>)` in `api.py`. Typer and Click are
      private to `flext-cli`.
    - HTTP: `flext-web` exposes `web.application(source)` and
      `web.serve(source, request)`; queries map to GET with query-parameter models,
      commands to POST bodies. FastAPI, Starlette and uvicorn are private to
      `u.Web`/`t.Web`.
    - Singer/dbt: `flext-meltano` bases drive `singer_sdk` through its programmatic API
      (`Tap.invoke`, `Target.invoke`, discovery, sync), never through Click `main()`;
      connectors keep only `api.py`.
    - Input is parsed once (`u.invoke_operation`), `--help` and schema rendering build no
      adapter, and failures leave with their original cause, mapped to an exit status or
      HTTP status by one table per transport over `c.ErrorCode`.
   `cli.service_routes` and the route models stay as deprecated pass-throughs until
   their census reaches zero.
6. **No fake facades (operator decision D1 = A).** An unused `api.py`, `cli.py`,
   `base.py` or console script is not created merely to satisfy layout. NS-LAYOUT
   derives when a project must provide `api.py`
   (it composes services) and `cli.py` (it declares a console script and operations).
   Amendment 2026-10-24 supersedes the earlier blanket removal of kernel `api.py`:
   core retains its real consumed composition root without a locator (bead
   `flext-itpd1.11.3`); a transport receives the composed facade, never resolves
   services by name. This target does not certify current runtime compliance.
7. **Consumers first.** A base contract contracts only after every consumer declared
   what it uses; every base slice revalidates its consumers before merge.
8. **Execution law for every slice.** Module size follows the owning project's typed
   `loc_cap.max_lines` declaration; this ADR does not freeze a separate numeric cap.
   Refactors remove confirmed duplication while preserving behavior.
   Every diagnostic, generation, fix, format, check and
   test runs through a selector-free root Make verb of the lane (`make gen`, `make fix`,
   `make fmt`, `make check`, `make tests`); no selector, filter or raw tool is evidence.
   A red has no "foreign" category: every red in a slice's blast radius is fixed at its
   owner (in its own small PR when it lives in another repository) before the slice
   lands; it is never narrowed, skipped or suppressed.
9. **Services are Pydantic consumers by MRO.** Each project's `base.py` specializes
   `s`; domain services inherit it and their model-owned port options. Requests,
   outputs, state and port fields belong to `m`, capabilities to `p`, aliases to
   `t`, and pure helpers to `u`. Services do not duplicate constructors, singleton
   logic, settings cloning or validation. Port-bearing services are constructed at
   the API root with every dependency supplied, not through `fetch_global()` or
   `with_settings()` that reconstructs a class without its required ports.
10. **One registry and dispatch owner.** `FlextRegistry` consumes an explicitly
    supplied runtime. `FlextDispatcher` owns atomic handler registration and
    immutable execution snapshots. Discovery receives an explicit module and
    preserves the original callable, payload and Result. Re-registering the same
    handler is idempotent; a different handler cannot overwrite a command route.
    Distinct event subscribers fan out in registration order and stop on failure,
    without promising rollback of effects already executed. Plugin payloads retain
    identity; removal deletes real storage before ownership bookkeeping. Separate
    API instances share a registry only when composition explicitly injects it.
11. **No unsupported-policy success.** Handler metadata may order discovery by
    priority, never authorize command replacement. Timeout and middleware are
    rejected when the selected executor cannot implement them; defaults must not
    silently request an unsupported policy. This is not permission to build another
    executor in a consumer.
12. **Results compose; they are not reimplemented.** Return an existing Result
    directly when its contract already fits. Use `map` for pure value changes,
    `flat_map` for Result-producing operations and `from_failure` when changing
    payload type while preserving failure code, data and exception. Keep explicit
    control flow when a combinator's exception behavior differs from the boundary.
    Do not stringify failures or turn them into defaults. Parse once at ingress and
    serialize once at transport egress; owned models remain models between services.
13. **Transport surface (2026-10-24).** `m.ServiceSurface` describes a facade as
    operations plus sub-service groups, which are model fields with `exclude=True`, so
    there is no registry or list of groups. `u.provide_service` builds the facade at
    the `api.py` root with its injected infrastructure. Consumers never import a
    transport library (Typer, Click, FastAPI, Starlette, uvicorn, singer_sdk); a
    flext-infra catalog rule reports every such import. Work is tracked in epic
    `flext-itpd1.11.8`.

## Consequences

- The 217 existing services without ports keep their behavior; adoption is one bead and
  one PR per member, guided by `07-sessions-guide.md` and counted by the `flext-infra`
  detection rules.
- `flext-infra` scaffolds (`codegen new`) emit the contract; `ban-skip-validation` also
  matches the `Annotated[..., t.SkipValidation]` form.
- Documentation: `flext-core/docs/guides/service-patterns.md` becomes the fleet service
  guide; stale DI documents are deleted; generated guides are fixed at their root
  source.

## Rejected alternatives

- A `FlextCliFactory` class or any CLI builder inside `flext-core` — the kernel may not
  import `flext-cli`, and `flext-cli` already owns the Pydantic-to-Typer builder.
- Declaring the settings hook as a method of `x` — it would force `@override` on 39
  overrides in about 30 repositories (pyrefly `missing-override-decorator`).
- Checking operation shape at class creation — existing public methods (for example in
  `flext-ldap`) would break imports fleet-wide.
- An auto-migration rule `SkipValidation → t.Port` — no dependency outside the kernel
  uses `SkipValidation`; detection rules target the real adoption backlog instead.
- A Protocol-keyed container with `compose(container)` (former S2b) — it adds a second
  composition path beside the constructor, needs abstract-type keys that the three type
  checkers disagree on, and gives no capability pure DI lacks.

## Verification contract

- Every slice: runtime proof through the public API, `make gen` twice with a fixed
  point, `make fix`, `make fmt`, `make check` and `make test` (selector-free; the
  incremental testmon selection is the verb's own), and consumer revalidation before
  merge.
- End to end after S5: a service with a port and a real adapter is composed at the root,
  `service_routes` builds a real Typer app, a valid command exits 0 and renders the
  result, an invalid one exits non-zero with the validation cause, `--help` needs no
  adapter, and a non-conforming adapter fails at composition.
- Transport (Decision 13): golden argv and `--help` through `cli.run`; real HTTP through
  the flext-tests client; Singer goldens for `--about`, `--discover`, `--catalog`,
  `--state`, `--test` and stdin; every installed console script runs outside the
  checkout; importing a facade loads no transport library.
- Closure: this ADR moves to ACCEPTED with the merged SHAs and receipts of S1–S10.

## 0.13 unified planning reconciliation (documentation only)

- Disposition for the unified 0.13 plan: Keep proposed; reconcile current API/base, pure
  DI, metadata and namespace.
- This note records planning reconciliation only. It does not change the ADR's recorded
  maturity, implementation status, or acceptance evidence.
- Future 0.13 API/ecosystem migration remains gated by `flext-ik359` (publication
  `flext-1wjg1` plus separate authorization) and approval of the documented contracts
  and consumer migration matrix. Current 0.12 validation, bug fixes and documentation
  continue under their owners; the ADR's proposal/status is unchanged.
