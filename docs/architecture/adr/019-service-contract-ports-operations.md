# ADR-019 — Service Contract: Protocol Ports, Explicit Composition Root, Typed Operations

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
- [Rejected alternatives](#rejected-alternatives)
- [Verification contract](#verification-contract)

<!-- TOC END -->

- **Status:** PROPOSED — operator-approved plan V8, 2026-09-25; amended 2026-09-26 (pure
  DI definitive, S2b removed); becomes ACCEPTED when slices S1–S10 land with post-merge
  proof
- **Date:** 2026-09-25 (amended 2026-09-26)
- **Integrated so far:** S1 — `flext-core` #499, merge `d65ba487f`. Supporting kernel
  fixes on the same line: #502 `5ce5919a6` (enforcement), #503 `2401cb21b` (lazy
  initialization), #504 `8de52fa6b` (`u.process` fail-loud).
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
- **Tracking:** epic `flext-4jtcb` (slices `flext-4jtcb.1`–`.12`; `.9`, the former S2b,
  is superseded by the 2026-09-26 pure-DI ruling).

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
  console script only to satisfy the NS-LAYOUT gate; 15 members carry no-op `main()`.

The operator asked for `FlextService` to be the essential base that provides a typed API
and an automatic CLI for every member (plan V7), with fakes removed and real wiring.

## Decision

1. **Ports.** A dependency is a `@runtime_checkable` Protocol in `p` (extending
   `p.Base`, minimal capability). A service field declares it as
   `name: t.Port[p.X] = m.Field(exclude=True, description=…)`, where
   `t.Port[P] = Annotated[P, SkipJsonSchema()]`. Pydantic validates it by `isinstance`
   on construction and assignment. The port type must be a plain Protocol class.
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
   that takes nothing or one Pydantic request model, returns `p.Result[...]` and has a
   docstring is an operation. `u.service_operations(Service)` discovers them lazily,
   without `eval` and without class-creation checks, and fails loudly on malformed ones.
5. **Derived CLI.** `flext-cli` turns operations into commands with
   `cli.service_routes(Service, provide=…)` over the existing `register_result_routes`;
   `--help` builds no adapter; invalid input leaves as `e.fail_validation` with the
   original cause and a non-zero exit.
6. **No fake facades (operator decision D1 = A).** The kernel has no `api.py`, `cli.py`,
   `base.py` or console script; NS-LAYOUT derives when a project must provide `api.py`
   (it composes services) and `cli.py` (it declares a console script and operations).
7. **Consumers first.** A base contract contracts only after every consumer declared
   what it uses; every base slice revalidates its consumers before merge.
8. **Execution law for every slice.** Modules stay within 200 logical lines, with
   net-negative LOC on refactors. Every diagnostic, generation, fix, format, check and
   test runs through a selector-free root Make verb of the lane (`make gen`, `make fix`,
   `make fmt`, `make check`, `make test`); no selector, filter or raw tool is evidence.
   A red has no "foreign" category: every red in a slice's blast radius is fixed at its
   owner (in its own small PR when it lives in another repository) before the slice
   lands; it is never narrowed, skipped or suppressed.

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
- Closure: this ADR moves to ACCEPTED with the merged SHAs and receipts of S1–S10.
