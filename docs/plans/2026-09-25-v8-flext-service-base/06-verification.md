# 06 — Verification

<!-- TOC START -->

- [1. Proofs per slice](#1-proofs-per-slice)
- [2. End-to-end proof (after S5)](#2-end-to-end-proof-after-s5)
- [3. Final sweeps (through gates and the graph, never a grep over a projection)](#3-final-sweeps-through-gates-and-the-graph-never-a-grep-over-a-projection)

<!-- TOC END -->

Every proof is recorded on the slice bead with command, cwd, exit code and decisive
output. A green gate never replaces a runtime proof. Slices that delete code also record
the LOC delta and zero uses outside the owner for every deleted symbol.

## 1. Proofs per slice

| Slice | Runtime proof (public API)                                                                                                                                                                                                                                                                                                                                                                                                               | Gates                                                                    | Non-breakage                                                                    |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| S0    | Fleet validation workspace `make setup` exit 0 at the root and per member; baseline recorded; plan and ADR-019 (Proposed) merged                                                                                                                                                                                                                                                                                                         | Superproject gates                                                       | —                                                                               |
| S1    | Non-conforming port raises `ValidationError` on construction and assignment; subscripted port type rejected at class creation; service `model_json_schema()` works and lists only data; port service `fetch_global()` raises; hook read through `p.RuntimeBootstrapProvider`; unknown source raises; `unwrap()` carries `__cause__`; no `getattr` or `model_copy(update=)` on the runtime path; dead options deleted with zero-use proof | Selector-free `make gen` ×2 (fixed point), `fix`, `fmt`, `check`, `test` | The 11 members of S1, handler consumers, every member suite versus the baseline |
| S2    | `scope()` still works (LOGGER regression); duplicate, empty and reserved names raise; auto-register without a module raises; bridge deleted with zero-use proof                                                                                                                                                                                                                                                                          | Same                                                                     | Core suite; auth, observability, target-ldap, plugin                            |
| S3    | Discovery lists exactly a real service's operations; every invalid shape fails with operation, annotation, module and fix; `execute`/`track` excluded; `TYPE_CHECKING`-only import yields the fix message                                                                                                                                                                                                                                | Same                                                                     | Core suite (no class-creation effect)                                           |
| S4    | `isinstance(real_service, p.Service)` is True                                                                                                                                                                                                                                                                                                                                                                                            | Same, in the 7 members and the core                                      | The 7 members                                                                   |
| S5    | Real Typer app: valid command exit 0 with the rendered result; invalid input non-zero with the validation cause; input-less operation; `--help` without adapter or configured environment                                                                                                                                                                                                                                                | Same, in flext-cli                                                       | flext-infra, meltano, quality, web, oracle-oic                                  |
| S6    | `settings_type` `None` raises `TypeError`; a port service runs in `isolated_test_runtime(build=…)` with a real adapter; settings fixture without `getattr`                                                                                                                                                                                                                                                                               | Same, in flext-tests                                                     | Every member suite                                                              |
| S7    | `codegen new` scaffold in `tmp_path` passes `make check`; detection rules and the fixed `ban-skip-validation` pass `ast-grep test`; per-member detection report; NS-LAYOUT requires no empty facade; the core without skeletons passes `make check`; the superproject regenerates its `__init__.py`                                                                                                                                      | Same, in flext-infra, flext-core and the superproject                    | Whole workspace                                                                 |
| S8/S9 | Every site has a failure-path test that went from red to green                                                                                                                                                                                                                                                                                                                                                                           | Same                                                                     | Consumers of each symbol, from the graph                                        |
| S10   | ADR-019 accepted; gitlinks at merged tips; superproject `make gen` fixed point; adoption beads created                                                                                                                                                                                                                                                                                                                                   | Superproject gates                                                       | —                                                                               |

## 2. End-to-end proof (after S5)

In the fleet validation workspace with members at merged tips:

1. an executable `flext-core` example (`examples/`, run by the suite) declares a
   `@runtime_checkable` port, a real adapter (file system in the fixture's temporary
   directory) and a service with one request operation and one input-less operation;
2. the root composes it by constructor (pure DI, the only composition path);
3. `flext-cli` `service_routes(Service, provide=…)` registers the routes on an app built
   by `create_app_with_common_params`;
4. through `execute_app` and `finalize_result`: a valid command exits 0 with the
   rendered result, an invalid one exits non-zero with the validation cause, and
   `--help` works without adapters;
5. a non-conforming adapter fails at composition with `ValidationError`.

Recorded on the epic `flext-4jtcb`.

## 3. Final sweeps (through gates and the graph, never a grep over a projection)

| Sweep                                                                 | Expected                                                                        |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `SkipValidation` in the core (including the `Annotated` form)         | Zero on ports and runtime seeds; any remainder justified in writing with a bead |
| `getattr` defaults and `model_copy(update=)` on the core runtime path | 0                                                                               |
| Skeleton facades and no-op `main()` in `flext-core`                   | 0 (D1 = A)                                                                      |
| Duplicate command builder in `flext-cli`                              | 0                                                                               |
| Superproject `make gen`                                               | Fixed point                                                                     |
| Epic beads                                                            | Closed with four sources; adoption beads created with counted backlog           |
| Lanes, worktrees and PRs in scope                                     | 0 open                                                                          |
