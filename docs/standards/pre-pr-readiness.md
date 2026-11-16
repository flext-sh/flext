# Pre-PR Readiness SOP

<!-- TOC START -->

- [Scope and authority](#scope-and-authority)
- [1. Lifecycle and core principles](#1-lifecycle-and-core-principles)
  - [1.1 Fix, forward, adopt, collaborate](#11-fix-forward-adopt-collaborate)
  - [1.2 Root cause analysis mandate](#12-root-cause-analysis-mandate)
  - [1.3 PR readiness policy](#13-pr-readiness-policy)
- [2. Test suite optimization](#2-test-suite-optimization)
  - [2.1 Measure before optimizing](#21-measure-before-optimizing)
  - [2.2 conftest constructors](#22-conftest-constructors)
  - [2.3 Shared c, t, p, m, u objects](#23-shared-c-t-p-m-u-objects)
  - [2.4 Centralized configuration and fixtures](#24-centralized-configuration-and-fixtures)
  - [2.5 Isolated infrastructure](#25-isolated-infrastructure)
  - [2.6 Dynamic, standardized test patterns](#26-dynamic-standardized-test-patterns)
  - [2.7 Centralized constants, loops, and fixtures](#27-centralized-constants-loops-and-fixtures)
  - [2.8 Latency elimination](#28-latency-elimination)
  - [2.9 Performance regression protection](#29-performance-regression-protection)
- [3. Test quality and architecture](#3-test-quality-and-architecture)
  - [3.1 Behavior-driven standard](#31-behavior-driven-standard)
  - [3.2 Shallow-test pruning](#32-shallow-test-pruning)
  - [3.3 Implementation-detail prohibition](#33-implementation-detail-prohibition)
  - [3.4 Assertion quality](#34-assertion-quality)
- [4. Pre-PR checklist](#4-pre-pr-checklist)
- [5. Evidence record](#5-evidence-record)
- [6. Roles, exceptions, and escalation](#6-roles-exceptions-and-escalation)
- [7. Adoption plan](#7-adoption-plan)
- [Related](#related)

<!-- TOC END -->

This SOP is the pre-Pull Request gate for every FLEXT repository and every agent or
session working in them. It composes, and never replaces, the root `AGENTS.md`,
`.agents/skills/flext-law/SKILL.md`, ADR-029, ADR-032, and the
[worker lane contract](../ways-of-working/worker-lane-contract.md). Where this
document and a higher authority differ, the higher authority wins.

Normative terms: MUST and MUST NOT are mandatory; SHOULD is expected and a deviation
needs a recorded reason on the active Bead.

## Scope and authority

- Applies to the superproject, every member repository, worktrees, and external
  consumers such as ai-hub.
- One Bead owns the slice; one lane branch and one worktree carry it; one pull
  request closes it against the declared integration branch.
- Beads is execution truth. A report, a commit, or a green local run is not delivery.
- The operator's newest instruction outranks this SOP. No agent grants itself an
  exception that the operator did not authorize.

## 1. Lifecycle and core principles

### 1.1 Fix, forward, adopt, collaborate

- **Fix** at the canonical owner. Repair the cause, not the symptom, and never add a
  fallback, shim, suppression, or second execution path to obtain green.
- **Forward**. Never reset, revert, stash, or discard another actor's work. Re-read
  the live tree, absorb the integration tip with `git merge --no-ff`, and resolve
  conflicts without losing WIP.
- **Adopt** compatible work already committed elsewhere through `git cherry-pick -x`
  or `git merge --no-ff`, recording source SHA, scope, and authorization on the
  Bead. Never copy raw WIP, caches, environments, or generated projections.
- **Collaborate**. Claim one Bead, declare the lane, notify the coordinator, and do
  not open a duplicate lane for the same owner. A real blocker is routed to its
  owner, not worked around.
- Keep exactly one active slice per lane. Complete its full cycle before starting
  another: generation, repair, formatting, checks, tests, public runtime proof,
  commit, push, review, merge.

### 1.2 Root cause analysis mandate

No repair may start before the failure mechanism is established from measured facts.

1. Reproduce through the canonical entry point; record command, working directory,
   exit status, source revision, and the first decisive output.
2. Identify the failing boundary: source owner, installed artifact, consumer,
   configuration, or environment.
3. Establish the mechanism with debug, diagnostics, tracing, or profiling at the
   measured owner. Hypotheses guide investigation and are never proof.
4. Name the owner and repair it there. Rerun the original failing boundary against
   the new candidate.
5. Record the cause, evidence, fix, and re-exercise result on the Bead.

A different error, a smaller finding count, or a narrower passing check is not
resolution. Trial patches, guard relaxation, changed tests that encode the defect,
and "probably flaky" dismissals without evidence are prohibited.

### 1.3 PR readiness policy

A pull request is ready only when all of the following are true:

- It carries exactly one Bead and merges the fresh integration tip with `--no-ff`.
- The RCA record exists and the original failure is re-exercised green.
- `make gen` reaches its fixed point; `make fix` and `make fmt` are no-ops.
- Checks are zero-finding at the required phase, with full `make check` when the
  changed scope requires it.
- Tests pass with no unexpected skips, warnings, empty collection, or suppressed
  failures, and the suite runtime did not regress.
- The changed public behavior has real runtime proof, not only unit evidence.
- The diff is scoped to the Bead, contains no generated projection edited by hand,
  no new suppression, and no secret.
- CI is green on the exact head SHA, an independent review is recorded, and the
  coordinator merges it as a merge commit. Administrative merge requires explicit
  operator authorization and never waives native gates, CI, or post-merge proof.

Known reds deferred to "later", `[WIP]` pull requests, and conflicted pull requests
are not ready. A lane that cannot merge green within its session is split, not
extended.

## 2. Test suite optimization

Tests are product evidence. Optimization removes cost without reducing coverage,
isolation, determinism, or assertion strength.

### 2.1 Measure before optimizing

- `make tests` is the native incremental Testmon selection and is the default.
- `make tests-full` executes the complete applicable population once without
  Testmon and produces suite wall-time evidence.
- Timing and timeout policy lives in the typed `flext-infra` tooling SSOT and its
  runner. Never restate, duplicate, or locally override those values.
- Capture the baseline on unchanged inputs, on the same host admission context, and
  compare against the same command and scope. Report absolute and percentage delta.
- Optimization follows the [performance profiling standard](performance-profiling.md):
  profile the measured hot path first, then change its owner, then re-measure.

### 2.2 conftest constructors

- Each package has one authored `conftest.py`. It constructs shared objects and
  exposes typed fixtures; test modules do not repeat bootstrap, settings, container,
  or client setup.
- Fixtures are factories by default. Session or module scope is allowed only for
  immutable values derived from typed config whose lifetime cannot leak state.
- Mutable singletons reset through the `flext_tests` plugin and its fixtures
  (`reset_settings`, `test_runtime`) instead of ad-hoc teardown code.
- `autouse` exists only for isolation, never for expensive setup. A heavy fixture
  must be requested explicitly by the tests that need it.
- `conftest.py` reaches only public facades. It never imports private modules or
  duplicates production wiring.

### 2.3 Shared c, t, p, m, u objects

- Import the canonical letters from the public package root and compose test facades
  by the MRO in the [testing standard](testing.md#test-facade-mro). Do not redeclare
  aliases, protocols, models, or constants per test module.
- Share immutable constants, typed models, and parsed configuration through typed
  owners instead of rebuilding them for every test.
- Build payloads with the shared `flext_tests` builders. Do not copy a builder body
  into a test module.
- Sharing is a performance device, not a semantic one. Shared objects remain
  read-only or are reset between items; a test never depends on mutation left by a
  previous test.

### 2.4 Centralized configuration and fixtures

- Expected values come from the same typed config or settings owner the consumer
  reads. Tests never freeze today's configured scalar, path, endpoint, or default.
- Declare scenario data once, in `tests/fixtures/`, and parametrize from it. No
  second copy inside a test module.
- Declare behavior-affecting template, resource, and environment inputs in the
  workspace manifest so Testmon invalidates correctly. Never clear or replace its
  database.
- Keep tier deltas only where the layout requires them (`unit`, `integration`,
  `e2e`). Do not fork a second parallel fixture tree.

### 2.5 Isolated infrastructure

- Every test owns its temporary directories and artifacts; nothing writes into the
  checkout.
- Allocate unique ports, schemas, prefixes, and resource names per test and per
  worker. Never assume a host-global service instance.
- Heavy services belong to the `integration` or `e2e` tier behind a lifecycle
  fixture with an explicit readiness probe and complete teardown.
- Connectivity tests skip only under the root `AGENTS.md` policy when the declared
  environment is absent or unreachable. A skip proves nothing about the service.
- No test depends on execution order, shared rows, or state written by another item.
  Every item is safe under parallel workers.
- Reuse of a bounded service is allowed only when state isolation is proven; it is
  never a reason to leak state or to serialize the suite.

### 2.6 Dynamic, standardized test patterns

- One parametrized test per contract, driven by a typed case table with stable ids.
  Do not duplicate near-identical test functions or loop assertions that cannot name
  the failing case.
- Keep the canonical `Tests<Unit>` nesting and one naming scheme across the package.
- Derive ids and expected values from typed data, never from hand-kept parallel
  strings.
- Every case exercises a distinct outcome or boundary. Duplicate cases are removed,
  not accommodated with weaker assertions.

### 2.7 Centralized constants, loops, and fixtures

- Scenario data, expected values, and magic strings are declared once at their
  canonical owner and consumed by reference.
- Loops iterate typed collections and assert a named case per iteration; a loop is
  never a substitute for a missing parametrized case.
- Fixtures compose. A fixture that copies another fixture's setup is deleted and the
  consumer reuses the original.

### 2.8 Latency elimination

- No `time.sleep`. Wait on a declared readiness condition with a bounded deadline
  owned by `u`, and fail loudly on timeout.
- No retry-as-stabilization. A flaky item is a defect and is repaired at its owner.
- Avoid per-test process spawns, network round-trips, package installs, migrations,
  and full application bootstrap when a narrower real provider proves the contract.
- Keep collection linear and import cost lazy. No import-time I/O, scanning, or
  global registration work.
- Caching is allowed only with typed, explicit invalidation and proven identical
  behavior. Hidden caches, `lru_cache` service locators, and cross-test memoization
  are prohibited.
- Profile before optimizing; an unmeasured micro-optimization is not admitted.

### 2.9 Performance regression protection

- `make tests-full` wall time on the same host class and candidate must not increase
  beyond measurement noise. An increase caused by the change is repaired at its
  owner or justified on the Bead with profile evidence.
- The following are prohibited as cost reduction: deleting coverage, deselecting
  cases, relaxing timeouts, clearing Testmon, converting failures to skips, and
  weakening assertions.
- When the repair falls outside the slice, file a performance Bead with the profile
  and the measured owner, and keep the slice mergeable without the regression.

## 3. Test quality and architecture

### 3.1 Behavior-driven standard

- Tests exercise public entry points only: `api.py` and the canonical `c, t, p, m, u`
  surfaces. Assertions observe returned models, protocol contracts, emitted errors,
  and persisted public state.
- One contract per test. The name states the observable behavior, not the function
  name or the internal step order.
- A test failure must be caused by the behavior it names, never by fixture setup,
  collection order, or a shared mutable object.
- Runtime behavior is established from the official contract and the real consumer
  before the test encodes it. Tests confirm behavior; they never define it.

### 3.2 Shallow-test pruning

A test is shallow when deleting it leaves the named behavior unverified. It proves a
construction, an import, or a type existence, not an outcome.

Signals:

- no meaningful assertion, or an assertion on a value the fixture just created;
- only `is not None`, truthiness, or "did not raise" with no contract consequence;
- an exact duplicate of another test with a different name;
- a smoke path already covered by a stronger behavioral test;
- it cannot fail for any plausible regression in the owner it names.

Procedure:

1. Inventory the shallow candidates per repository and name the intended contract.
2. Keep the strongest test per contract and delete the weaker duplicates.
3. If the scenario is real but tested at the wrong boundary, rewrite it through the
   public facade; do not delete the scenario.
4. Delete only when no distinct contract remains, and record the rationale and the
   coverage reconciliation on the Bead and pull request.
5. Never prune to make CI green, and never remove connectivity, security, or
   regression coverage without an equal or stronger replacement.

Behavior, not coverage percentage, is the acceptance target.

### 3.3 Implementation-detail prohibition

Signals:

- imports from private modules or submodule paths below the package root;
- private attribute access, `hasattr` and `getattr` probing, or module attribute
  reaching;
- `mock`, `patch`, `monkeypatch` mutation, or fake service chains;
- assertions on call order, call count, internal state snapshots, or private class
  construction;
- assertions on log text unless the log record is a declared public contract.

Protocol:

1. Name the public outcome the test intends to protect.
2. Replace the internal observation with the public result, model, or protocol.
3. If a helper is legitimately needed, add it once to its canonical owner (`u` or a
   typed fixture) and consume it from there.
4. If no public observable exists, the test is not admissible. Redesign the public
   surface or delete the test; never widen access or suppress the finding.

No suppression, inline ignore, or local allowlist resolves an implementation-detail
test. The owner is repaired.

### 3.4 Assertion quality

- Use `tm` matchers and `FlextResult` combinators. Assert the typed outcome, not raw
  truthiness.
- Expected values come from the typed SSOT, never from a copied literal.
- No tautologies, no assertions that restate an input, and no failure message that
  omits the observed and expected values.
- Each assertion protects a distinct consequence; redundant assertions are removed.

## 4. Pre-PR checklist

Run in order from the workspace or worktree root. Heavy verbs are never parallel.

1. **Scope**: one Bead claimed, lane branch declared, no duplicate lane, and the
   integration tip absorbed.

    ```bash
    git fetch origin 0.12.0-dev
    git merge --no-ff origin/0.12.0-dev
    git merge-base --is-ancestor origin/0.12.0-dev HEAD
    ```

2. **RCA**: cause, mechanism, owner, failing entrypoint, and re-exercise result are
   on the Bead.
3. **Generation**: `make gen` reaches its fixed point; `make fix` and `make fmt`
   produce no diff.
4. **Static gates**: `make check CHECK_PHASE=primary` while iterating, then
   `make check` for the full changed scope. Zero findings; no new suppression.
5. **Tests**: `make tests` for the affected scope. Run `make tests-full` when the
   suite or its timing changed, and record wall time. No unexpected skip, warning,
   empty selection, or retry.
6. **Runtime**: prove the changed public behavior through the real consumer or
   entrypoint, with command, working directory, exit status, and decisive output.
7. **Diff hygiene**: review `git status`, `git diff`, and the staged stat; explicit
   paths only; no generated projection edited by hand, no secret, no unrelated file.
8. **Pull request**: one Bead, one subject, the RCA and evidence in the body, a green
   head SHA, and no conflict. Request independent review.
9. **Integration**: the coordinator merges the reviewed green head as a merge commit
   and reruns the boundary on the merged revision.
10. **Closure**: Bead evidence updated, post-merge proof recorded, lane retired only
    with ancestry and content preservation proof.

A pull request opened before these gates is a draft or is not opened.

## 5. Evidence record

Every claim names its candidate identity and scope. Record on the Bead:

- command, working directory, exit status, and the decisive output line;
- source revision, installed dependencies, and checker policy identity;
- scope counts: executed, reported, deselected, excluded, skipped, and inventory;
- suite wall time before and after when tests changed;
- the runtime proof and the exact artifact or revision it exercised.

A local green run, a cache hit, a formatter-only pass, a skipped connectivity item, or
an older passing count transferred to new source is not completion evidence.

## 6. Roles, exceptions, and escalation

- The worker implements one Bead, runs the boundary, and reports evidence. The worker
  never merges, closes the Bead, or retires the lane.
- The reviewer checks behavior, RCA, test quality, latency, and scope. Review never
  waives a native gate.
- The coordinator owns integration, merge authority, closures, and lane retirement.
- Administrative merge is allowed only with explicit operator authorization after
  every required check is green.
- The only standing test exceptions are the connectivity prerequisite skip and the
  deprecated-signature window defined by root `AGENTS.md`. Neither authorizes a
  weakening of assertions, coverage, or isolation.
- Anything else that would relax a gate is an operator decision, presented with the
  original requirement, evidence, alternative, and impact.

## 7. Adoption plan

1. Publish this SOP and link it from the standards index, testing standard, and
   testing guide.
2. Apply the checklist to every open lane and pull request, starting with the rig
   root lane, and record the outcome on the owning Beads.
3. Add the checklist reference to the pull request template and review route through
   the owning generator, never by hand-editing a projection.
4. Run a per-repository shallow-test census and prune by the rule in section 3.2,
   with runtime measurements before and after.
5. Track suite wall time, unexpected skips, first-submission green rate, and pruned
   shallow tests as the program metrics.

## Related

- `AGENTS.md` — workspace engineering law
- `.agents/skills/flext-law/SKILL.md` — FLEXT architecture law
- [Worker lane contract](../ways-of-working/worker-lane-contract.md)
- [ADR-029](../architecture/adr/029-always-working-one-complete-cycle.md) — one
  complete cycle per slice
- [ADR-032](../architecture/adr/032-host-wide-heavy-gate-admission.md) — host
  admission and run limits
- [Testing standard](testing.md)
- [Development standard](development.md)
- [Performance profiling standard](performance-profiling.md)
- [Testing guide](../guides/testing.md)
- [Using flext-tests](../guides/using-flext-tests.md)
