# Flext-Infra Stabilization, Modernization, and Runtime Closure Plan

## Outcome

Deliver `flext-infra` from the latest `0.12.0-dev` integration tip as the single canonical owner of setup, generation, conformance, refactoring, checks, and project scaffolding, with:

- `make setup`, `make gen`, `make mod`, `make fix`, `make fmt`, `make check`, `make test`, `make build`, and applicable docs/audit verbs completing without errors, warnings, hidden skips, or residual changes;
- `make gen`, `make mod`, `make fix`, and `make fmt` reaching a second-run no-op fixed point;
- ProjectNew/conform/lazy-init producing the same tree on the first and subsequent runs;
- the conform god module replaced by the canonical FLEXT MRO facade layout, with one owner for every behavior and no duplicated implementation;
- tests validating public runtime behavior rather than mocks, private methods, implementation details, or config-owned literals;
- the validated candidate merged by no-ff into the current integration tip, propagated through the workspace gitlink and affected first-party consumers, and proven again on the integrated SHA.

## Critical Review of the Previous Plan

The previous plan is rejected as an execution plan for these reasons:

1. It treated CRG as stale. CRG is now current at flext-infra SHA `469b26b4e0b336e78548fef1fdcfca347f9c5d53` on `0.12.0-dev`; all future graph claims must still record the live built-at SHA.
2. It mixed root-workspace and flext-infra tips. Current evidence distinguishes root `0.12.0-dev@676ae7aa3c` from flext-infra `0.12.0-dev@469b26b4e`; the live flext-infra tree must be re-read because the WIP grew from four to five files during planning.
3. It proposed direct pytest/tool invocations and ad-hoc diagnostics. All diagnosis and validation must use public selector-free Make verbs or a documented public CLI. Missing diagnostics become a Make/CLI product defect.
4. It proposed committing the current WIP before runtime proof. The live modified set must first be re-read, classified, adopted, completed, and validated; no commit is justified by intent alone.
5. It treated test failures as isolated assertions before proving the runtime contract. Correct runtime and canonical external contracts decide behavior; tests follow them. A correct runtime invalidates a contradictory test, while an incorrect runtime is fixed at its owner.
6. It postponed c/t/p/m/u centralization until after structural splitting. That would preserve duplication. Shared constants, types, protocols, models, utilities, settings, and config ownership must be corrected before MRO decomposition.
7. It used broad “fix remaining failures” tasks without naming the producer, consumer, failure boundary, or proof. This replacement decomposes the work into independently landable Beads slices.
8. It allowed historical or pre-existing warnings to remain. The current operator instruction supersedes that exception: warnings, cosmetics, legacy residue, and pre-existing violations within the approved first-party scope are red.
9. It did not adjudicate overlapping Beads, PRs, branches, and worktrees. Duplicate tracker items and abandoned contributions must be reconciled by real contribution versus current tip, then adopted fix-forward or superseded.
10. It treated tests and LOC goals as ends. The actual acceptance boundary is a usable runtime and generated standalone project, followed by native gates and integrated-SHA proof.

## Current Evidence and Authorities

### Coordinated position at 2026-09-16 23:33Z

The stopped-session and parallel-lane reconciliation is recorded in:

- [`addenda/2026-09-16-flext-infra-continuation/README.md`](addenda/2026-09-16-flext-infra-continuation/README.md);
- [`addenda/2026-09-16-flext-infra-continuation/01-session-timeline.md`](addenda/2026-09-16-flext-infra-continuation/01-session-timeline.md);
- [`addenda/2026-09-16-flext-infra-continuation/02-contribution-adoption-matrix.md`](addenda/2026-09-16-flext-infra-continuation/02-contribution-adoption-matrix.md);
- [`addenda/2026-09-16-flext-infra-continuation/03-gates-beads-and-conflicts.md`](addenda/2026-09-16-flext-infra-continuation/03-gates-beads-and-conflicts.md);
- [`addenda/2026-09-16-flext-infra-continuation/04-agent-coordination.md`](addenda/2026-09-16-flext-infra-continuation/04-agent-coordination.md).

Current decisions from that reconciliation:

1. Native Claude session `0fed44fb-27b1-44b3-9009-8c70dd364358` ran from 20:40Z to 22:53Z and stopped on a session limit. It primarily advanced the separate `ai-hub wip` automation program and incomplete fleet landings; it did not complete any flext-infra modernization phase.
2. The rope Ruff micro-slice has been absorbed or superseded. Do not replay its `u.validate_value` edits or its rejected SLF001 suppression.
3. The envrc lane contains useful generated-owner and residue-removal work, but its local-ledger backend conflicts with the newer Gas-City-only authority. Preserve only contributions that survive that cutover and current runtime proof.
4. The aeolian test lane is historical: PR #235 is closed and the branch is far behind. Re-derive useful behavior-test changes on the current tip; never merge it wholesale.
5. The live next slice is producer-first: current tip/WIP adjudication, Gas City health + Bead reread, built-in Make verb ownership and lazy-analysis verification, then `make setup` and generation fixed point.

- **Tracker:** Central Gas City Beads only, always through `direnv exec <rig-checkout> bd ...`; no local Beads database and no Markdown task queue.
- **Primary work:** `flext-5fxu6.4` under `flext-5fxu6`, stabilization epic
  `flext-itpd1`, and documentation reconciliation child `flext-itpd1.2`.
- **Related Beads requiring reconciliation:**
  - journal locking: `flext-fkfmu` (`flext-dcge0` is closed history);
  - fake/mock/hardcoded tests: `flext-wjozx` and `flext-c4k44`
    (`flext-9m4gc` is closed lineage);
  - private-function tests: `flext-4v4tf`;
  - conform model error: `flext-bdmdg`;
  - setup/toolchain: `flext-5k9r7`;
  - generation determinism: `flext-3d8bv`;
  - test/codemod budgets: `flext-z4ydq`, `flext-t9q8h`.
- **Current flext-infra WIP at the latest observation:**
  - `config/codegen.yaml`;
  - `src/flext_infra/codegen/_conform/execute.py`;
  - `src/flext_infra/codegen/conform.py`;
  - `src/flext_infra/promoted/executor.py`;
  - `tests/unit/codegen/test_codegen_conform.py`.
- **Latest native test evidence:** `make test` collected 2,626 items and exited `2` after the 600-second hard timeout (`raw_return_code=-15`). Confirmed failures in the changed closure include `test_dependency_surface_excludes_unowned_managed_files`, both `test_new_project_is_complete_and_idempotent` variants, and `test_existing_manifest_converges_to_identical_tree`; deps and pydantic-modernizer failures also occurred before the timeout. Evidence log: `.reports/tests/20260916T191913.760813Z-3830396/pytest.log`.
- **Latest CRG observation:** 9,242 nodes, 82,389 edges, 988 files, 11 flows, 15 test gaps, risk `0.55`, updated on `0.12.0-dev` at `2026-09-16T19:29:23Z`. Rebuild again after WIP adjudication; older 5-gap and 66-gap snapshots are historical only.
- **Confirmed current risks:** duplicated conform implementations, untested high-degree execution methods, non-fixed-point ProjectNew/conform behavior, journal lock contention, setup/toolchain drift, make-mod residue, full-suite timeout with product/test failures, and unresolved lane/PR contributions.
- **Generated-file law:** templates/config/schema/generator are writable owners; generated `__init__.py`, Make surfaces, managed pyproject sections, CI, and other projections are regenerated, never hand-edited.
- **Banned artifacts:** never create or regenerate `uv.lock`, `mise.lock`, or `exclude-newer`.

Historical logs and handoffs select the next investigation; they do not prove the current tree. Every baseline must be rerun from the dedicated lane before a status claim.

## Execution Rules

1. Work in a dedicated flext-infra worktree created from the latest remote `0.12.0-dev` tip. Keep the primary workspace on integration for comparison and gitlink propagation.
2. Before each slice, refresh the integration tip and merge it into the lane with `git merge --no-ff`; never rebase, force-push, reset, restore, stash, clean, or revert shared work.
3. Use `rtk` for shell output economy without bypassing the canonical command, for example `rtk make setup`. Use Gas City Beads through `rtk direnv exec <repo> bd ...`.
4. Use CRG first for scope, callers, tests, impact, and review. Record the graph SHA; rebuild/update whenever the source SHA or adopted WIP changes.
5. Structural changes run through `make mod`. ast-grep/Rope rules belong in their configured SSOT and are exercised by `make mod`; do not run ad-hoc rewrite commands.
6. Each Bead is one small, reviewable, independently green slice. Parallel research is allowed; overlapping implementation owners are integrated serially.
7. No source edit is committed before its public runtime behavior and native gates pass. Commits use explicit paths only.
8. A warning, skip, timeout, missing report, false green, residual diff, or second-run mutation is red.

## Ordered Implementation Plan

### 1. Rehydrate and Adjudicate the Work

1. From the dedicated worktree, use central Gas City Beads to inspect and claim the active canonical Bead; update its intent, exact tip, exclusions, current first red gate, and stop condition.
2. Reconcile duplicate Beads rather than creating new ones:
   - keep `flext-fkfmu` as the live journal-lock owner and preserve the closed
     `flext-dcge0` only as lineage;
   - elect one fleet test-quality owner from `flext-wjozx` / `flext-c4k44`,
     preserving closed `flext-9m4gc` as lineage and retaining `flext-4v4tf` as
     a bounded child if its acceptance is distinct;
   - link setup, deterministic generation, conform model, and budget defects to `flext-5fxu6.4` with explicit dependencies.
3. Inventory relevant worktrees, commits, and PRs, including the rope-modernize lane and PR #743. For each candidate, compare its real hunks and Beads against current `0.12.0-dev`:
   - adopt unique, correct contributions fix-forward;
   - reimplement stale intent at the current owner when direct adoption would restore obsolete architecture;
   - supersede duplicate Beads/branches only after their contribution is present and validated;
   - coordinate live owners through Beads before touching overlapping files.
4. Re-read and classify the live WIP by intent and evidence, including the newly observed `config/codegen.yaml` change and the native Claude edits in flext-core/flext-cli. Use the contribution matrix in the addenda. Preserve compatible work, complete missing paired-owner changes, and reject no hunk solely because its provenance is unknown.
5. Update CRG at the resulting lane SHA, then capture changed functions, impact radius, affected flows, tests, large functions, duplicate candidates, hubs, and bridge nodes.

**Exit:** one authoritative Bead graph, one dedicated lane based on the current integration tip, adopted WIP with no unexplained hunk, and a fresh CRG baseline.

### 2. Establish a Fresh Runtime Baseline

Run the public lifecycle without suppressing output:

1. `rtk make setup`;
2. `rtk make gen` twice;
3. `rtk make mod` twice;
4. `rtk make fix` twice;
5. `rtk make fmt` twice;
6. `rtk make check`;
7. `rtk make test`;
8. `rtk make build`;
9. applicable `make docs` and `make audit` verbs.

For every red verb, record cwd, exact SHA, exit status, first causal error, warnings, elapsed/budget evidence, changed files, and owning Bead. Do not continue past a producer failure into consumer speculation.

Prioritize blockers in producer order:

1. Gas City health and built-in Make verb ownership, including live reread of `flext-5fxu6.4.27`;
2. setup/toolchain ownership, including `flext-5k9r7`, provisioned-versus-invoked uv identity, and banned lock/pin artifacts;
3. codegen transaction isolation, electing the journal/lock Bead and implementing PIN-SHA journal identity plus per-repository locks before concurrent/fleet generation proof;
4. generation fixed point;
5. codemod progress/residue;
6. fix/format fixed point;
7. static/custom gates;
8. test correctness and budget;
9. build/docs/audit.

**Exit:** a current, evidence-backed failure map. Historical failure counts are replaced, not repeated.

The first current test investigation starts from the recorded report rather than launching another blind full run: classify the four named conform failures first, then the deps and pydantic-modernizer tracebacks, fix their canonical producers, and only then rerun the full native verb. The timeout is a red product/test-architecture defect, not permission to raise the 600-second budget.

### 3. Repair Conform, ProjectNew, and Lazy-Init Fixed-Point Behavior

1. Preserve the confirmed Makefile runtime contract from `Makefile.j2`: generated projects bind UV through the provisioned Mise owner (`override UV := ... exec -- uv`), never `UV ?= uv`. Validate this through the generated project runtime; retain the corrected public test only after that proof.
2. Trace ProjectNew’s first write and conform’s second pass as one pipeline. Elect a single writer for every file.
3. Fix lazy-init at its creation owner so newly created Python modules already use the canonical import form. Do not create absolute imports on the first pass and normalize them to relative imports on the second.
4. Make `align_imports` idempotent for already canonical files and ensure `scope=self` publishes only files owned by that phase. Keep the conform-path filter only if ownership analysis proves it is the correct boundary rather than a test-specific exclusion.
5. Unify the three currently divergent pyproject ordering owners:
   - `config/codegen.yaml` marks `tool.flext.namespace` MANAGED through `conflict_sections`, while `tool.flext.docs` is CUSTOM and must survive live overlay;
   - `pyproject.toml.j2` statically places `tool.flext.docs` before `tool.flext.namespace`;
   - `FlextInfraPyprojectModernizerPayloadMixin._reorder_document_inplace` sorts nested `tool` tables alphabetically because `tomlsort.sort_first` governs only top-level groups, while conform uses `tomlkit` round-trip preservation plus Taplo rather than the modernizer reorder path.
     Elect one typed ordering policy for both managed and preserved custom `tool.flext.*` tables, consume it from template rendering and modernization, and make `compose_project_artifact` preserve that canonical result. Do not promote `tool.flext.docs` to managed merely to force order, and do not drop either section or its data.
6. Resolve `flext-bdmdg` at the model owner: remove the nonexistent render-spec reference and use the canonical typed model already owned by `m.Infra`; do not add an alias or compatibility model.
7. Add/replace tests at public boundaries:
   - ProjectNew produces a usable project;
   - conform immediately reports a fixed point against that project;
   - a second conform/gen pass with a live custom `[tool.flext.docs]` and managed `[tool.flext.namespace]` produces zero file changes;
   - generated Make actually selects the provisioned uv runtime;
   - lazy-init leaves canonical imports unchanged.

**Exit:** ProjectNew → conform → lazy-init is byte-stable on the first completed generation cycle, and `make gen` twice is a no-op on the second run.

### 4. Centralize c/t/p/m/u, Config, and Settings Before Moving Code

Using CRG callers/importers/tests and `make mod` discovery, classify every conform-domain symbol:

- immutable identifiers, section names, phase names, and external contract values → `c.Infra` from config-backed owners where configurable;
- reusable precise aliases and adapters → `t.Infra`;
- collaborator boundaries and injected dependencies → `p.Infra`;
- owned payloads, plans, receipts, states, requests, and render contexts → strict Pydantic models under `m.Infra`;
- pure reusable transformations and path/render helpers → `u.Infra`;
- environment/CLI inputs → settings;
- business/generation policy → `config/*.yaml` and typed config;
- orchestration/use cases → conform services/mixins;
- transport → CLI;
- composition only → facade.

Remove local dict/dataclass/Any/object contracts, copied literals, repeated path logic, duplicate render-context assembly, and local helper APIs after consumers use the canonical facade. Models remain behavior-free and fully resolvable without `model_rebuild`.

**Exit:** shared behavior is centralized before file splitting, reverse imports remain `TYPE_CHECKING`-only, and no old/new owner coexistence remains.

### 5. Replace the Conform God Module With the Canonical MRO Facade

1. Use current repository examples to implement the exact strict shape:
   - thin public `codegen/conform.py` facade with composition only;
   - private `codegen/_conform/` package;
   - `_conform/base.py` composing the internal responsibility classes in dependency order;
   - responsibility modules for planning, execution/transaction, rendering/context, validation/fixed-point, and narrowly justified policy groups;
   - generated `_conform/__init__.py` produced only by `make gen`.
2. Never create `_part*` classes or numbered fragments. Each internal module owns one cohesive class/family and stays within the project’s logical-LOC cap.
3. Remove, rather than wrap, duplicated implementations. At minimum, elect one owner for:
   - `plan`;
   - `_execute_managed_locked_prepared`;
   - `_artifact_render_context`;
   - `_project_render_context`;
   - `_complete_governed_plans`;
   - `_plan_existing_templates`.
4. Keep the public class/name/import contract stable only where there is a current consumer. Remove obsolete private compatibility paths in the same slice.
5. After each responsibility extraction:
   - refresh CRG;
   - run `make mod` to propagate the semantic cutover;
   - run `make gen` twice;
   - run the complete native gate set for the slice;
   - land the slice before extracting the next responsibility.
6. Apply the same centralize-then-split method to other changed god modules only when CRG proves they are in the current runtime path or a gate blocks on them. Track each as its own child Bead; do not turn this into an unbounded cosmetic sweep.

**Exit:** `conform.py` is composition-only, every behavior has one private owner, no conform module exceeds the LOC policy, and CRG shows consumers on the new canonical path only.

### 6. Make Duplication and Structural Modernization Product Gates

1. Put every ast-grep/Rope transformation needed for the cutover in the configured `mod` rules SSOT, with detection and rewrite coverage.
2. Route the rules only through `make mod`; require detection, application, semantic rewiring, deletion of superseded owners, and a clean second pass.
3. Ensure jscpd/duplication checking is part of the canonical check surface. If it is absent or cannot express the required zero-duplicate contract, repair that Make/check owner first rather than running a one-off scanner.
4. Require zero duplicated conform implementations and zero newly introduced duplication across the changed closure. Existing duplication encountered in a touched owner is fixed in the same slice or tracked as a blocking child Bead.
5. Re-run CRG dead-code and impact analysis before deletions; graph/source disagreement is investigated, never interpreted as permission to delete.

**Exit:** `make mod` second pass is clean, duplication gate is zero for the changed closure, and superseded code is absent.

### 7. Exterminate Invalid Tests at Public Runtime Boundaries

Reconcile the test-quality Beads and execute bounded slices, starting with flext-infra and then propagating through affected first-party consumers:

1. inventory mocks, fakes, patching, fake subprocess/filesystem behavior, private-symbol calls, implementation-order assertions, copied fixtures, hardcoded config/settings values, and false-green result assertions;
2. delete tests that cannot be expressed as meaningful public behavior; do not preserve them by exposing internals;
3. replace necessary coverage with public `api`/CLI/Make behavior, `tm`, shared `flext-tests` fixtures, and canonical `c/t/p/m/u` contracts;
4. derive expected configurable values from the same typed config/settings owner used by production;
5. validate errors through public result/exception semantics and real process/file boundaries, without mocks;
6. keep immutable external protocol literals only where the external contract, not FLEXT config, owns them;
7. keep the test suite within declared per-test and total budgets by fixing product/test architecture, not by raising timeouts, skipping, or reducing coverage.

Prioritize tests covering high-degree untested paths: managed locked execution, fixed-point validation, render context, plan collection/completion, private-import cutover, and generated-project runtime.

**Exit:** no mock/fake/private/hardcoded-pattern violations in the flext-infra changed closure; the full suite completes within budget and proves public behavior.

### 8. Validate a Real Standalone Consumer

Through the canonical public codegen/Make surface:

1. create a new standalone internal FLEXT project with ProjectNew;
2. prove its generated file tree and configuration identity;
3. run its own `make setup`, `make gen` twice, `make mod` twice, `make fix` twice, `make fmt` twice, `make check`, `make test`, and `make build`;
4. import and execute its public facade/CLI from the built artifact or declared staged runtime;
5. prove no writes escape the owned repository/state roots and no banned locks/pins appear;
6. compare first-generation and post-conform trees byte-for-byte.

If a needed observable has no canonical command, add that command/receipt at the owning product surface, test it, and then use it. Do not use throwaway scripts as evidence.

**Exit:** a generated standalone project works from setup through built runtime and remains byte-stable.

### 9. Full Native Gates and Incremental Landing

For every independently complete Bead slice:

1. update CRG and run change/risk/affected-flow/test-gap review;
2. merge the latest `origin/0.12.0-dev` into the lane with `--no-ff` and resolve by fix-forward adoption;
3. run the full canonical lifecycle from the merged lane;
4. require a clean second pass for generation/mod/fix/fmt and no source/generated drift;
5. commit explicit scoped paths, update Bead evidence, push the lane, and open/update its PR;
6. require CI and review on the exact candidate SHA;
7. merge by merge commit into `0.12.0-dev`—never rebase, squash away required ancestry, or force-push;
8. fetch the merged integration SHA and rerun runtime-critical gates there before closing the Bead.

Do not batch the full god-module rewrite, test extermination, lock redesign, and fleet propagation into one PR. Land each green owner-correct slice in dependency order.

### 10. Propagate and Close the Integration Boundary

1. Update the root workspace gitlink to the merged flext-infra SHA through the canonical workspace generation flow.
2. Run the root workspace lifecycle and affected first-party consumer lifecycles at their latest integration tips. At minimum include consumers exercised by generated Make/conform surfaces and the current stabilization scope (`flext`, `ai-hub`, and `cosmos-main`).
3. Apply fixes at the canonical producer. Regenerate consumers; never patch their generated projections.
4. For each consumer, prove setup, generation fixed point, checks, tests, build/runtime, branch ancestry, and clean git state.
5. Update living docs/ADR/skills only where behavior or authority changed, in the same validated slice and through their canonical owners.
6. Close or supersede Beads only after merged-SHA evidence exists. Record remaining unrelated work as dependencies, not as hidden exceptions.
7. Retire stale branches/worktrees only after their unique contribution and Bead history are present on integration and recovery evidence exists.

**Exit:** merged flext-infra and workspace integration SHAs are runtime-proven, consumer projections converge, all related Beads have truthful status, and no abandoned unique contribution remains.

## Failure and Recovery Rules

- **Setup failure:** stop downstream gates; fix toolchain/config/template owner and rerun setup.
- **Generation drift:** preserve both outputs, identify the single writer, fix its owner, and rerun two-pass generation.
- **Journal lock timeout:** do not delete lock files; identify the owner and complete the per-repository/PIN-keyed lock slice.
- **Codemod detection residue:** keep the gate red; repair rule/discovery/semantic application until the second pass is empty.
- **Test versus runtime conflict:** establish the official/runtime contract first, then fix the incorrect side; never hardcode today’s config to satisfy a test.
- **Concurrent work:** reread live files and adopt compatible intent; notify the owner through Beads and merge forward.
- **Integration divergence:** merge the integration tip into the lane with `--no-ff`, revalidate, and continue; never rebase or force.
- **Timeout or warning:** treat as failure with an owning Bead; never increase budgets or suppress output without a separately approved contract change.

## Acceptance Checklist

The work is complete only when all are true:

- central Gas City Beads reflect the real dependency graph and contain no unresolved duplicate owner for this scope;
- the dedicated lane and final integration commit descend from the current integration tip;
- CRG is current on the reviewed and merged SHAs;
- conform/ProjectNew/lazy-init is first-run canonical and second-run byte-stable;
- conform uses the strict `_conform/` + `base.py` + thin facade MRO shape, with no `_part` modules and no duplicate implementation;
- changed modules comply with the logical-LOC limit after c/t/p/m/u centralization;
- `make setup`, `gen`, `mod`, `fix`, `fmt`, `check`, `test`, `build`, docs, and audit complete without errors, warnings, skips, false greens, or residue;
- gen/mod/fix/fmt second passes are no-ops;
- test quality rules hold for the changed closure and public high-risk paths have behavior coverage;
- a newly generated standalone project completes its own lifecycle and public runtime;
- root workspace and affected first-party consumers converge on the merged flext-infra SHA;
- scoped commits, PR/CI evidence, merge commit, merged-SHA runtime proof, clean trees, and Bead updates are recorded.

## Explicit Non-Goals

- Do not impose FLEXT architecture on third-party forks.
- Do not redesign unrelated product behavior merely to reduce LOC.
- Do not preserve obsolete APIs, tests, or generated output through shims.
- Do not hand-edit generated projections.
- Do not treat a local green lane, passing unit test, or successful build as integration/runtime completion.
