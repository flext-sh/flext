# Engineering SOP — Pre-PR Readiness, Test Performance, and Test Quality

<!-- TOC START -->

- [Scope and authority](#scope-and-authority)
- [1. Development lifecycle](#1-development-lifecycle)
- [2. PR readiness gate](#2-pr-readiness-gate)
- [3. Test performance](#3-test-performance)
- [4. Test quality and architecture](#4-test-quality-and-architecture)
- [5. Evidence contract](#5-evidence-contract)
- [Related](#related)

<!-- TOC END -->

This SOP is the operational checklist a change passes before it becomes a pull request
and again before it merges. It binds every lane in this workspace. It adds no rule that
contradicts the root `AGENTS.md`, the owning ADR, or the operator's newest instruction;
where they differ, those win.

## Scope and authority

- Behavior authority: the running system, the official external contract, and the real
  consumer. Tests confirm behavior; they never define it.
- Change authority: the operator's request, then the active Bead, then the owning
  architecture record.
- Execution authority: the canonical Make/CLI surface only. A broken verb is repaired at
  its owner and rerun through the same surface.

## 1. Development lifecycle

**Fix, Forward, Adopt, Collaborate.**

1. **Fix at the cause.** Reproduce through the canonical entry point, bind the failing
   artifact to its revision, and prove the mechanism (debug, trace, profile) before
   editing. A hypothesis guides investigation; it is never a trial patch.
2. **Forward only.** Preserve compatible work from every actor. Never stash, reset,
   restore, revert, rebase, or force-push shared work. Repair the canonical owner and
   move on.
3. **Adopt current state.** Treat every current authorized change as owned input
   regardless of provenance. Re-read the tree, attribute intent, and integrate.
4. **Collaborate.** Announce material findings, blockers, and integration state to
   affected participants. One active integration candidate per lane.
5. **One slice at a time.** `gen → fmt → fix → mod → check → tests`, then runtime proof,
   commit, push, merge. A phase never starts while another is incomplete.
6. **RCA gate.** A red gate found mid-slice is fixed in the same slice at its owner. No
   new feature starts on a known-defective base.

## 2. PR readiness gate

A change is submission-ready only when every item is true. Anything false means the
change stays on its lane.

| Gate               | Requirement                                                                     |
| ------------------ | ------------------------------------------------------------------------------- |
| Scope              | One subject, one reviewable unit, beginning to end, no bundled drive-bys        |
| Cause              | Root cause identified and repaired at its canonical owner                       |
| No workaround      | No fallback, shim, suppression, allowlist, hardcode, or dual path               |
| Generated surfaces | Regenerated from source, not hand-edited; idempotent                            |
| Lint/format        | Clean on `src/`, `tests/`, `examples/`, `scripts/`                              |
| Types              | Single type checker clean across the governed population                        |
| Tests              | Green, deterministic, within the time budget, no selection weakening            |
| Runtime            | The real public path exercised, not only unit assertions                        |
| Docs               | Affected docs, ADRs, Beads, and skills updated in the same change               |
| Diff               | Net-neutral or negative; every added line has a current consumer                |
| Evidence           | Exact command, working directory, exit status, decisive output recorded         |
| Remote             | Lane merged forward from integration tip, conflicts resolved, no conflict block |
| CI                 | Required checks green on the exact head that will merge                         |

Merge discipline: merge commit only, on the exact green head, one subject per PR. A
merge needing elevated privileges runs only with explicit operator authorization.

## 3. Test performance

Targets: whole suite under 240 s; slow tests at most 20 s each; any other test under 2 s.
Do not raise a limit to make a test fit; remove the latency or split the case.

1. **Measure first.** Capture a duration profile before editing; locate the hot path.
2. **Reuse construction.** Build shared values once in `conftest.py` or a typed fixture;
   never rebuild an expensive object per test.
3. **Share canonical objects.** Use the project's `c/t/p/m/u` facades and typed fixtures
   instead of ad-hoc literals; one owner per constant.
4. **Centralize fixtures.** One unified `conftest.py`, typed fixtures in
   `tests/fixtures/`, no per-module copies.
5. **Isolate infrastructure.** Session-scoped setup for expensive resources; function
   scope only for what must be fresh. A run cleans up its own artifacts.
6. **Standardize patterns.** Dynamic, table-driven cases over duplicated bodies; loops
   over copy-paste; a single loop source.
7. **Select incrementally.** Use the native incremental selection with its persistent
   database; never force a full rerun to hide latency, and never delete coverage to go
   faster.
8. **Re-measure after.** The optimization is accepted only when the same measurement
   drops and the suite stays green.

## 4. Test quality and architecture

**Behavior-driven, public-surface only.**

1. **Public interfaces.** Tests import through package roots and facades. A test that
   reaches into a private module encodes an implementation detail and is a defect.
2. **Never freeze configuration.** Expected values owned by config/settings are read
   from the same typed source production reads, or proven by a generator round trip. A
   test that breaks on a legitimate config change is a test defect.
3. **No mocks of owned code.** Mocking, patching, or re-declaring policy values to force
   a pass is prohibited. Exercise the real object.
4. **Prune shallow tests.** A test with no assertion, or asserting only that a call
   returns (truthiness, not-a-throw), or asserting construction internals, is deleted
   or replaced with a behavioral assertion.
5. **Ban implementation-detail tests.** A test whose subject is a private helper name, a
   call sequence, a message string used only internally, or a module's internal state is
   not a contract test. Identify by: does a reasonable refactor with identical public
   behavior break it? If yes, delete or rewrite at the public boundary.
6. **One behavior, one test.** Name the behavior, not the function. Assert observable
   outcome and typed error semantics.
7. **Coverage follows behavior.** Coverage is an outcome of exercising the real path; it
   is never a target that justifies implementation-shaped tests.

## 5. Evidence contract

Every claim carries command, working directory, exit status, and the decisive output
line. A green subset is not a green suite. A passing unit test is not runtime proof. An
outdated generated file is not evidence either way. Claims without evidence are
withdrawn, not softened.

## Related

- `AGENTS.md` (workspace law and the Rig and Lane Contract)
- `docs/standards/testing.md`, `docs/standards/development.md`
- ADR-029 (one complete cycle), ADR-032 (host admission for heavy gates)
