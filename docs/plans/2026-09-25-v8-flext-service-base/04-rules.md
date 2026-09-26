# 04 — Rules that apply at every step

<!-- TOC START -->

- [1. Authority and decisions](#1-authority-and-decisions)
- [2. Execution](#2-execution)
- [3. FLEXT code](#3-flext-code)
- [4. Tests](#4-tests)
- [5. Commands and environment](#5-commands-and-environment)
- [6. Git and landing](#6-git-and-landing)
- [7. Codemods and generated files](#7-codemods-and-generated-files)
- [8. Documentation](#8-documentation)
- [9. Tracker](#9-tracker)
- [10. Concurrency](#10-concurrency)
- [11. V7 laws R1–R11](#11-v7-laws-r1r11)
- [12. New V8 laws](#12-new-v8-laws)

<!-- TOC END -->

## 1. Authority and decisions

1. Authority order: newest operator request, orchestration contract, Beads, ADRs,
   skills, docs, defaults.
2. D-ASK: on doubt or conflict, stop and ask one precise question; a conflict between
   two operator orders is presented side by side with numbers.
3. Settled decisions are not reopened: D1 = A (2026-09-25); D3 = pure DI, definitive, no
   S2b (2026-09-26); D2 is asked when infra adoption starts; decision 4 of the ai-hub
   plan v3; module limit 200 logical lines (2026-09-26, supersedes D-CAP 1000); D-SET
   (`config.<Ns>`/`settings.<Ns>`), D-CI, D-VENV, admin merge authorized when the
   touched gates are green.
4. An exception to a rule exists only with explicit operator authorization recorded on a
   bead.

## 2. Execution

1. Truth: a done/green/resolved claim carries command, cwd, exit code and decisive
   output.
2. Fail loud: the first failure propagates with traceback and cause; no fallback, retry,
   normalization or partial execution.
3. Preflight before effects; atomic effects; causal subprocess failures (no `|| true`).
4. Zero residue: rewire consumers and delete the superseded code, test, doc, config and
   alias in the same change.
5. Red is red: warnings, skips, empty output, zero collection, missing tools and
   normalized failures are red.

## 3. FLEXT code

1. Facade chain `c → t → p → m → u`; reverse imports only under `TYPE_CHECKING`.
2. One top-level class per module with its facade letter in its own `__all__`; nothing
   loose (ADR-018).
3. Declaration layers are data only; behavior lives in `u`, `base.py`, `services/`,
   `api.py`, `cli.py`.
4. Pydantic 2 only through `m/t/p/u/r/e`; every model extends an `m.*` preset; no
   `model_rebuild`; no `SkipValidation` without the owner's written justification;
   external data enters through `model_validate`/`model_validate_json`.
5. Strict typing: no `Any`/`object`; `T | None`; `t.*` aliases and `p.*` protocols;
   PEP 695.
6. `flext-core` enriches existing modules before creating new ones; every module stays
   within 200 logical lines, with net-negative LOC on refactors.
7. Fewer public APIs: extend a method with a keyword parameter before adding a method;
   monomorphic returns.
8. Generated files change only through `make gen`.
9. One writable owner per fact; no hardcoded list duplicating a derivable source.

## 4. Tests

1. Public facades and observable behavior only; no mocks, patches, monkeypatching,
   fakes, private access or implementation-shape assertions.
2. Test adapters are real: `tmp_path` file systems, real processes, containerized
   services through `flext_tests/docker.py`.
3. `tm` matchers and `u.Tests.assert_*`; one `TestsFlext*` class per module; typed
   fixtures; the unified conftest.
4. No frozen config/settings values; expectations come from the typed SSOT or from the
   fixture input.
5. Every cured site gets a failure-path test (both must-trigger and must-not-trigger).
6. `make test` always runs testmon and must select the slice's tests; zero execution
   proves nothing.

## 5. Commands and environment

1. Only selector-free root Make verbs of the lane (`setup`, `upg`, `gen`, `mod`, `fix`,
   `fmt`, `check`, `test`, `build`, `docs`). No Make selector, file filter,
   environment-dispatched sub-operation or raw `pytest`, `ruff`, `pyrefly`, `mypy` or
   `uv`; a missing operation is a missing verb, repaired at the Make/codegen owner.
2. Every lane verb runs as `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT make <verb>`.
3. Shell guard: one command per call, at most one `&&` and one `|`, no `;`, no `$(...)`,
   no `cd` into another checkout (`git -C`, `env -C`).
4. Long output goes to `~/tmp/v8/<slice>/<name>.log`; long commands run as background
   tasks whose completion evidence is read before dependent work.
5. mypy runs only with the project memory cap.
6. Diagnosis uses the canonical verb or the code-review graph (with a fresh `status`),
   never a grep over a generated projection.

## 6. Git and landing

1. One worktree per slice, `~/flext-work/v8-<slice>/<repo>`, on a branch from a freshly
   fetched `origin/0.12.0-dev`; never implement in the primary checkout.
2. Stage explicit paths only; partition this slice's changes from concurrent work before
   committing.
3. Forbidden: `reset`, `stash`, `rebase`, `checkout --`, `restore`, `clean`,
   `push --force`.
4. English commit messages with the session's `Co-Authored-By` trailer; `[WIP]`
   checkpoints are published; a `[WIP]` commit never heads a merge.
5. `make check && git push -u origin <branch>` (R1); PR against `0.12.0-dev`; CI on the
   exact head; every review thread resolved.
6. Merge commit (`gh pr merge --merge`, `--admin` authorized with the touched gates
   green); never squash or rebase.
7. Divergence: `git merge --no-ff origin/0.12.0-dev` into the lane, resolve hunk by
   hunk, revalidate.
8. After merge: fetch, prove on the merged SHA, and retire the lane only after
   `git merge-base --is-ancestor` against a fresh fetch.

## 7. Codemods and generated files

1. A repeated pattern becomes a rule in
   `flext-infra/src/flext_infra/codemod/rules/<id>.yml` with a fixture
   `codemod/tests/<id>-test.yml`, a snapshot, and `ast-grep test` in the same commit
   (R10); reuse the catalog first; prefer the most general rule that still constrains
   its receiver.
2. Manual edits only for unique cases, with the reason recorded.
3. A checkpoint commit before any `make mod`; scoped commits after it.
4. "generated findings require canonical generator repair" means the generator is the
   target.
5. `make gen` twice reaches a fixed point.

## 8. Documentation

1. Docs, docstrings and examples change in the same commit as the behavior.
2. Generated guides (`using-flext-*.md`) are fixed at their root source
   (`flext/docs/guides/`).
3. Versioned artifacts are written in English.
4. ADR-019 records the decision; `service-patterns.md` records the how.

## 9. Tracker

1. Beads through `direnv exec /home/marlonsc/flext bd …`; check `bd context --json`
   before mutations.
2. Claim before effects; update at every slice boundary.
3. A newly observed red gets a bead (or a comment on its owner) in the same turn.
4. Closure with four-source evidence (registered state, git, measured reality,
   integrated code); reasons DONE, SUPERSEDED or OBSOLETE.
5. Inventories that support a conclusion use `--limit 0`.

## 10. Concurrency

1. Concurrent work is input: adopt and fix forward; never discard.
2. Do not touch the files of lane `flext-edcqq` (beartype and enforcement in the core);
   if it is still idle when S9 starts, ask whether to adopt it.
3. Before S7, cross-check open `flext-infra` PRs (#865, #861, #858) and active
   worktrees.
4. One slice at a time per repository; slices in different repositories may run in
   parallel when independent.
5. Abandonment is never presumed.

## 11. V7 laws R1–R11

R1 (`check && push` in one shell), R2 (single pass per file), R4 (inspect every non-zero
exit), R6 (gate = local check with `CI=Y` plus a runtime probe), R7 (consumers
revalidated per slice, reinforced by R19), R8 (superseded 2026-09-26: a red has no
"foreign" category; every red in the blast radius is fixed at its owner), R9 (check PRs
and origin before implementing), R10 (codemod rule lands with `ast-grep test`), R11
(mechanical cures are never manual), plus: serial per repository; never `0.20.0-dev`,
dolt, `dev` or `main`; content conflicts are asked.

## 12. New V8 laws

| Law | Content                                                                                                                                              |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| R12 | A service dependency is `t.Port[p.X]` with `exclude=True` and a plain Protocol class; runtime seeds `t.Port[p.X \| None]` are the only typed absence |
| R13 | Only `api.py` builds adapters and port-bearing services, by constructor (pure DI, definitive); building an adapter performs no I/O                   |
| R14 | A public service method is an operation shaped as in `03-contract.md` §5; discovery is lazy, never at class creation                                 |
| R15 | A member CLI comes from `service_routes(Class, provide=…)`; `--help` builds no adapter; Singer connectors keep ADR-006                               |
| R16 | A service reads no global `settings`/`config`                                                                                                        |
| R17 | Consumers first: a base contract contracts only after each consumer declared what it uses                                                            |
| R18 | No skeleton facade and no no-op `main()`; a layer file exists only with real content (D1 = A)                                                        |
| R19 | Every base slice proves its affected consumers before merge, in the fleet validation workspace                                                       |
| R20 | Every `r.fail` carries its source exception; every `unwrap` chains the cause                                                                         |
| R21 | A base expansion never forces a fleet sweep as a side effect; new contracts enter through structural Protocols or together with the fleet codemod    |
| R22 | Never build an object that must be validated through `model_copy(update=)`                                                                           |
