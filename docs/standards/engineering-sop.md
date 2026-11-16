# Engineering SOP — Pre-PR Readiness, Test Performance, and Test Quality

<!-- TOC START -->

- [Scope and authority](#scope-and-authority)
- [1. Development lifecycle](#1-development-lifecycle)
- [2. PR readiness gate](#2-pr-readiness-gate)
- [3. Test performance](#3-test-performance)
- [4. Test quality and architecture](#4-test-quality-and-architecture)
- [5. Pre-PR checklist](#5-pre-pr-checklist)
- [6. Evidence contract](#6-evidence-contract)
- [7. Roles, exceptions, and escalation](#7-roles-exceptions-and-escalation)
- [8. Adoption](#8-adoption)
- [Related](#related)

<!-- TOC END -->

This SOP is the operational checklist a change passes before it becomes a pull request
and again before it merges. It binds every lane in this workspace. It adds no rule that
contradicts the root `AGENTS.md`, the owning ADR, or the operator's newest instruction;
where they differ, those win. Normative terms: MUST and MUST NOT are mandatory; SHOULD
is expected and a deviation needs a recorded reason on the active Bead.

## Scope and authority

- Behavior authority: the running system, the official external contract, and the real
  consumer. Tests confirm behavior; they never define it.
- Change authority: the operator's newest instruction, then global governance and the
  topic-owning ADR, then root and member law, then the active Bead as execution state.
- Execution authority: the canonical Make/CLI surface only. A broken verb is repaired at
  its owner and rerun through the same surface.
- Beads is execution truth. A report, a commit, or a green local run is not delivery.
- One owner per rule. This SOP is the only pre-PR SOP; a second document restating it
  is a duplicate owner and is removed in favor of this one.

## 1. Development lifecycle

**Fix, Forward, Adopt, Collaborate.**

1. **Fix at the cause.** Reproduce through the canonical entry point, bind the failing
   artifact to its revision, and prove the mechanism (debug, trace, profile) before
   editing. A hypothesis guides investigation; it is never a trial patch.
2. **Re-exercise the original failure.** After the repair, rerun the same entry point on
   the new candidate. A different error, a smaller finding count, or a narrower passing
   check is not resolution.
3. **Forward only.** Preserve compatible work from every actor. Never stash, reset,
   restore, revert, rebase, or force-push shared work. Repair the canonical owner and
   move on.
4. **Adopt current state.** Treat every current authorized change as owned input
   regardless of provenance. Re-read the tree, attribute intent, and integrate.
5. **Collaborate.** Announce material findings, blockers, and integration state to
   affected participants. One active integration candidate per lane.
6. **One slice at a time.** `gen → fmt → fix → mod → check → tests`, then runtime proof,
   commit, push, merge. A phase never starts while another is incomplete.
7. **RCA gate.** A red gate found mid-slice is fixed in the same slice at its owner. No
   new feature starts on a known-defective base.
8. **Lane discipline.** One Bead, one branch, one worktree, one pull request. The
   worker implements and reports; the coordinator merges, closes, and retires.

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

A change is not ready when any of these is true:

- a known red is deferred to "later" or expected to be repaired after merge;
- the pull request is conflicted or behind the integration tip;
- it adds a suppression, an exclusion, a skip, or a policy change without authorization;
- the only proof is a unit test, a cache hit, or a formatter-only pass;
- the suite wall time increased without a recorded owner-level profile and justification;
- the diff includes unrelated files or a generated projection edited by hand.

A lane that cannot merge green within its session is split, not extended.

## 3. Test performance

The timeout ladder, per-item slow bound, and run deadline are policy-owned by the shared
[canonical commands rule](https://github.com/datacosmos-br/agents/blob/dev/rules/workflow/canonical-commands.md)
and applied by the typed `flext-infra` tooling SSOT and its runner. Read them from that
owner; never restate, duplicate, or raise a limit to make a test fit. Remove the latency
or split the case.

1. **Measure first.** Capture a duration profile before editing; locate the hot path.
2. **Reuse construction.** Build shared values once in `conftest.py` or a typed fixture;
   never rebuild an expensive object per test. A fixture is a factory by default;
   session or module scope is reserved for immutable, config-derived values.
3. **Share canonical objects.** Use the project's `c/t/p/m/u` facades and typed fixtures
   instead of ad-hoc literals; one owner per constant. Share read-only values, reset
   mutable singletons through the `flext_tests` plugin and its fixtures.
4. **Centralize fixtures.** One unified `conftest.py`, typed fixtures in
   `tests/fixtures/`, no per-module copies. `autouse` exists only for isolation.
5. **Isolate infrastructure.** Each test owns its temporary directories, ports, and
   namespaces. Expensive services belong to the integration or e2e tier behind a
   lifecycle fixture with a readiness probe and complete teardown. No ordering
   dependency and no state leaked between items.
6. **Standardize patterns.** Dynamic, table-driven cases over duplicated bodies; loops
   over copy-paste; a single loop source; every case names a distinct outcome.
7. **Select incrementally.** Use the native incremental selection with its persistent
   database; never force a full rerun to hide latency, and never delete coverage to go
   faster.
8. **Re-measure after.** The optimization is accepted only when the same measurement
   drops and the suite stays green.
9. **Do not game the budget.** Deleting tests, deselecting cases, relaxing timeouts,
   clearing Testmon, converting failures to skips, and weakening assertions are
   prohibited as cost reduction. A flaky item is a defect, never a retry or a sleep.
10. **Protect the baseline.** Suite wall time on the same host class and candidate MUST
    NOT increase beyond measurement noise. An increase caused by the change is repaired
    at its owner or justified on the Bead with profile evidence. When the repair is
    outside the slice, file a performance Bead and keep the slice mergeable.

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

### 4.1 Shallow-test pruning procedure

A test is shallow when it does not verify the named behavior: it proves a construction,
an import, or a type existence, not an outcome, and deleting it changes no behavioral
coverage.

1. Inventory candidates and name the contract each intends to protect.
2. Keep the strongest test per contract and delete weaker duplicates.
3. If the scenario is real but tested at the wrong boundary, rewrite it through the
   public facade; do not delete the scenario.
4. Delete only when no distinct contract remains, and record the rationale and the
   coverage reconciliation on the Bead and pull request.
5. Never prune to make CI green, and never remove connectivity, security, or regression
   coverage without an equal or stronger replacement.

### 4.2 Implementation-detail protocol

Detection signals:

- imports from private modules or submodule paths below the package root;
- private attribute access, `hasattr` and `getattr` probing, or module attribute
  reaching;
- `mock`, `patch`, `monkeypatch` mutation, or fake service chains;
- assertions on call order, call count, internal state snapshots, or private class
  construction;
- assertions on log text unless the log record is a declared public contract.

Repair protocol:

1. Name the public outcome the test intends to protect.
2. Replace the internal observation with the public result, model, or protocol.
3. If a helper is legitimately needed, add it once to its canonical owner (`u` or a
   typed fixture) and consume it from there.
4. If no public observable exists, the test is not admissible. Redesign the public
   surface or delete the test; never widen access or suppress the finding.

### 4.3 Assertion quality

- Use `tm` matchers and `FlextResult` combinators; assert the typed outcome, never raw
  truthiness.
- Expected values come from the typed SSOT, never from a copied literal.
- No tautologies, no assertion that restates an input, and no failure message that
  omits the observed and expected values.
- Each assertion protects a distinct consequence; redundant assertions are removed.

## 5. Pre-PR checklist

Run in order from the workspace or worktree root. A lane never starts two heavy verbs at
once; cross-lane concurrency is owned by the host admission queue.

1. **Scope and lane.** One Bead claimed, lane declared, integration tip absorbed.

    ```bash
    git fetch origin 0.12.0-dev
    git merge --no-ff origin/0.12.0-dev
    git merge-base --is-ancestor origin/0.12.0-dev HEAD
    ```

2. **Cause.** The RCA record names cause, mechanism, owner, failing entrypoint, and the
   re-exercise result on the Bead.
3. **Generation and repair.** `make gen` twice with no diff on the second run, then
   `make fmt`, `make fix`, and `make mod`, each clean. No generated projection is edited
   by hand.
4. **Static gates.** `make check CHECK_PHASE=primary` while iterating, then `make check`
   for the complete workspace scope; no file or changed-only selector. Zero findings, no
   new suppression.
5. **Tests.** `make tests` runs the native Testmon selection over the complete applicable
   population; `make tests-full` is the alternative complete run without Testmon and
   without a preliminary incremental run. Use one of them as the declared evidence, with
   no unexpected skip, warning, empty selection, or retry; record wall time when timing
   changed.
6. **Runtime.** Prove the changed public behavior through the real consumer or
   entrypoint, with command, working directory, exit status, and decisive output.
7. **Diff hygiene.** Review `git status`, `git diff`, and the staged stat; explicit paths
   only; no generated projection edited by hand, no secret, no unrelated file.
8. **Pull request.** One Bead, one subject, RCA and evidence in the body, green head,
   no conflict, independent review requested.
9. **Integration.** The coordinator merges the reviewed green head and reruns the
   boundary on the merged revision.
10. **Closure.** Bead evidence updated, post-merge proof recorded, lane retired only with
    ancestry and content preservation proof.

## 6. Evidence contract

Every claim carries command, working directory, exit status, and the decisive output
line. A green subset is not a green suite. A passing unit test is not runtime proof. An
outdated generated file is not evidence either way. Claims without evidence are
withdrawn, not softened.

Also record:

- the candidate identity: source revision, installed dependencies, checker policy;
- the scope counts: executed, reported, deselected, excluded, skipped, inventory;
- suite wall time before and after when tests changed;
- the runtime proof and the exact artifact or revision it exercised.

A local cache hit, a formatter-only pass, a skipped connectivity item, or an older
passing count transferred to new source is not completion evidence.

## 7. Roles, exceptions, and escalation

- The worker implements one Bead, runs the boundary, and reports evidence. The worker
  never merges, closes the Bead, or retires the lane.
- The reviewer checks behavior, cause, test quality, latency, and scope. Review never
  waives a native gate.
- The coordinator owns integration, merge authority, closures, and lane retirement.
- Administrative merge is allowed only when review is the sole missing requirement, every
  required check is green on the exact head, and the operator authorized it.
- The standing test exceptions are the connectivity prerequisite skip, the
  deprecated-signature window, and the test-idiom rules explicitly justified per rule in
  root `AGENTS.md`. The `make upg` lock guard is the one explicit operator exception: a
  lock-write precondition, not a test exception. None of them weakens assertions,
  coverage, isolation, or the performance baseline.
- Lane mechanics, the review route, and retirement are owned by the
  [worker lane contract](../ways-of-working/worker-lane-contract.md); this section states
  only the SOP-level split.
- Any other relaxation is an operator decision, presented with the original
  requirement, evidence, alternative, and impact.

## 8. Adoption

1. Apply this checklist to every open lane and pull request, recording the outcome on
   the owning Bead.
2. Use it directly in review today. When a pull request template is declared in the
   repository, reference the SOP through that template's owning generator; no template
   exists yet.
3. Run a per-repository shallow-test census and prune by section 4.1, with wall-time
   measurements before and after.
4. Track suite wall time, unexpected skips, first-submission green rate, and pruned
   shallow tests as program metrics.

## Related

- `AGENTS.md` (workspace law and the Rig and Lane Contract)
- [Worker lane contract](../ways-of-working/worker-lane-contract.md)
- [Testing standard](testing.md), [development standard](development.md)
- [Performance profiling standard](performance-profiling.md)
- [Testing guide](../guides/testing.md), [using flext-tests](../guides/using-flext-tests.md)
- [ADR-029](../architecture/adr/029-always-working-one-complete-cycle.md) (one complete
  cycle), [ADR-032](../architecture/adr/032-host-wide-heavy-gate-admission.md) (host
  admission for heavy gates)
