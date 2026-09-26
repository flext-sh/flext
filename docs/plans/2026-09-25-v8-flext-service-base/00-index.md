# Plan V8 — FLEXT base: FlextService with Protocol ports and typed operations

<!-- TOC START -->

- [How to read](#how-to-read)
- [Context](#context)
- [Scope of this wave](#scope-of-this-wave)
- [Decisions](#decisions)
- [Adversarial review corrections](#adversarial-review-corrections)
- [Slice map](#slice-map)

<!-- TOC END -->

- **Status:** approved by the operator on 2026-09-25; amended 2026-09-26 (pure DI
  definitive with no S2b, 200-line module limit, selector-free root Make, no "foreign"
  red). S0 is PR `flext#274`; S1 is merged (`flext-core` #499, `d65ba487f`).
- **Supersedes:** operator plan V7 (2026-09-25).
- **Decision record:**
  [ADR-019](../../architecture/adr/019-service-contract-ports-operations.md).
- **Tracking:** epic `flext-4jtcb`.

## How to read

| File                   | Content                                                            | Audience            |
| ---------------------- | ------------------------------------------------------------------ | ------------------- |
| `00-index.md`          | Context, scope, decisions, review corrections, slice map           | Operator            |
| `01-evidence.md`       | Everything the survey measured, with file:line                     | Executors, auditors |
| `02-v7-review.md`      | Where V7 would break the architecture, and the correction          | Operator, reviewers |
| `03-contract.md`       | Normative service, port, root, operation, CLI and failure contract | The whole fleet     |
| `04-rules.md`          | Laws that apply at every step                                      | Executors           |
| `05-phases.md`         | What to do in every phase and slice, step by step                  | Executors           |
| `06-verification.md`   | Proofs per slice and end to end                                    | Executors, QA       |
| `07-sessions-guide.md` | Mini-guide for other sessions refactoring with FLEXT, CA and DI    | Other sessions      |

This repository copy is the source of truth. The operator's working copy (Portuguese,
approval projection) lives in `~/.claude/plans/plano-v8-flext-service-base/`.

## Context

V7 asked for `FlextService` to be the essential fleet base: Pydantic DI through ports,
an automatic API and CLI derived from service methods, removal of fake paths, and real
wiring. Five survey agents, runtime spikes on Pydantic 2.13.5, direct reading and an
independent adversarial review confirmed the goal. They also found 16 places where V7,
as written, would break the dependency direction, duplicate existing owners or measure
the wrong thing (`02-v7-review.md`). The operator narrowed the focus to delivering
`flext-core`, `flext-cli`, `flext-tests` and `flext-infra`, defining the base every
project uses, without leaving any project broken.

## Scope of this wave

- **In:** `flext-core` (service contract, truthful container, operations, kernel
  desfake, fake facade removal), `flext-cli` (derived CLI), `flext-tests` (typed service
  test base), `flext-infra` (templates, adoption detection rules, derived NS-LAYOUT),
  and the superproject (ADR-019, this plan, guide sources, gitlinks).
- **Out (later waves, one bead and one PR per member):** adoption by the other 27
  members (V7 F3/F4), infra residuals (V7 F5), gate flips (V7 F6).
- **Invariant:** each slice revalidates its affected consumers before merge (R19).

## Decisions

| Id  | Decision                                                                                                         | State                                                                              |
| --- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| D1  | The kernel has no `api.py`/`cli.py`/`base.py` and no console script; NS-LAYOUT derives when a facade is required | **Decided: A** (operator, 2026-09-25)                                              |
| D2  | `flext-infra` routes that use the service class itself as the request model                                      | Not blocking this wave; asked when infra adoption starts (recommendation: migrate) |
| D3  | Protocol-keyed container and `compose` (decision 4 of the ai-hub plan v3)                                        | **Decided 2026-09-26: pure DI, definitive; no S2b** (operator)                     |

## Adversarial review corrections

1. The settings hook is **not** declared on `x`: that would force `@override` on 39
   overrides in about 30 repositories (pyrefly `missing-override-decorator`). The core
   reads it through `p.RuntimeBootstrapProvider`.
2. `scope()` re-registers the LOGGER factory and `_internal_registrations` only tracks
   services: S2 fixes that bookkeeping and reserves internal names before duplicates
   fail.
3. `model_copy(update=)` bypasses validation (`model_options.py:66,73`,
   `model_runtime.py:251`, `registry.py:140-143`): S1 replaces it with validated
   construction.
4. The `model_json_schema()` proof also needs `settings_type` out of the schema.
5. Optional runtime seeds are `t.Port[p.X | None]`, never `t.Port[p.X] | None`; a
   subscripted or TypeVar port type is rejected at class creation.
6. Runtime options with zero consumers outside the core are deleted after proof, which
   also removes the registrable `SkipValidation`.
7. Operation shape is **not** checked at class creation; discovery is lazy and reads
   annotations without `eval`.
8. The CLI derives routes from the class and gets the instance from a provider at
   execution, so `--help` builds no adapter; one shared empty request model; explicit
   result rendering; the border's `ValidationError` becomes `e.fail_validation` with its
   cause.
9. An auto-migration `SkipValidation → t.Port` would find nothing outside the kernel; S7
   ships countable **detection** rules instead, and fixes `ban-skip-validation` for the
   `Annotated[..., t.SkipValidation]` form.
10. Two missed fail-soft sites join S8: `u.dump` via `unwrap_or`
    (`_utilities/model.py:69-71`) and `registry.py:120-129`.
11. `flext-tests` `isolated_test_runtime` calls `fetch_global()`; S6 adds a path for
    services with ports.
12. New proofs: LOC delta, zero uses outside the owner for every deleted symbol, and
    `--help` without adapters.

## Slice map

| Phase | Slice | Repo                     | Delivery                                                                                                              | Bead             |
| ----- | ----- | ------------------------ | --------------------------------------------------------------------------------------------------------------------- | ---------------- |
| F0    | S0    | all                      | Plan and ADR versioned, fleet validation workspace, beads                                                             | `flext-4jtcb.8`  |
| F1    | S1    | flext-core               | **Merged #499 `d65ba487f`:** `t.Port`, validated runtime seeds, protocol-typed hook, validated construction, cause    | `flext-4jtcb.1`  |
| F1    | S2    | flext-core               | Truthful container: bookkeeping, reserved names, duplicate/empty fail, dead bridge removed                            | `flext-4jtcb.2`  |
| F1    | S3    | flext-core               | Lazy typed operation contract                                                                                         | `flext-4jtcb.3`  |
| F1    | S4    | core + 7 members         | Truthful `p.Service`, consumers first                                                                                 | `flext-4jtcb.10` |
| F2    | S5    | flext-cli                | Lazy `service_routes`, empty model, result rendering, fail-loud params, dedupe                                        | `flext-4jtcb.4`  |
| F2    | S6    | flext-tests              | Typed base, no fallback, port-service runtime path                                                                    | `flext-4jtcb.5`  |
| F2    | S7    | flext-infra → flext-core | Templates, detection rules, `ban-skip-validation` fix, derived NS-LAYOUT; then the core deletes its fake facades (D1) | `flext-4jtcb.6`  |
| F3    | S8    | flext-core               | Fail-loud batch A                                                                                                     | `flext-4jtcb.7`  |
| F3    | S9    | flext-core               | Fail-loud batch B                                                                                                     | `flext-4jtcb.11` |
| F4    | S10   | superproject             | Closure: ADR accepted, guide sources, gitlinks, adoption beads                                                        | `flext-4jtcb.12` |
