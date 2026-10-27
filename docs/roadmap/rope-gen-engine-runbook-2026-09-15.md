# Runbook — Rope-Gen Engine (owner, taxonomy, findings flow, resume)

<!-- TOC START -->

- [1. Owner → responsibility](#1-owner-responsibility)
- [2. Findings taxonomy (ONE vocabulary, engine + gates + receipts)](#2-findings-taxonomy-one-vocabulary-engine-gates-receipts)
- [3. Findings flow (one detector, one consumer)](#3-findings-flow-one-detector-one-consumer)
- [4. Transaction loop per repository](#4-transaction-loop-per-repository)
- [5. Resume procedure (new session)](#5-resume-procedure-new-session)
- [5b. Historical resume context (2026-09-15, proven — preserved as evidence)](#5b-historical-resume-context-2026-09-15-proven-preserved-as-evidence)

<!-- TOC END -->

- **Status:** Active, versioned runbook; recovery ownership updated 2026-09-17,
  publication recovery aligned with ADR-014 §4 on 2026-10-26, and execution
  consolidation reconciled on 2026-10-27. Fleet stability is
  unproved; this document is not a green runtime receipt.
- **Date:** 2026-09-15
- **Tracking:** Gas City Bead `flext-itpd1.3` coordinates the current recovery cycle
  under `flext-itpd1`. Sibling owners are `flext-itpd1.2` (documentation) and
  `flext-itpd1.4` (Make machinery). Beads owns live execution state; local plans remain
  session context, not a second queue or publication input.
- **Law:** ADR-014 §3b (rope-in-gen), ADR-010 §3b (alignment), render purity law
- **Beads:** engine = `flext-crd1y` (discovered-from `flext-5fxu6.4`); loc-cap =
  `flext-471ws`; journal lock = `flext-fkfmu`; mission tests = `flext-wjozx` /
  `flext-c4k44` These concrete owner references preserve investigation provenance; their
  current status and dependencies require coordinator reconciliation in Beads.

## 1. Owner → responsibility

| Concern                                                       | Owner                                                                                                                                   | Hard rule                                                                         |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Generated projections (`__init__`, lazy-init exports, facets) | `make gen` (flext-infra codegen)                                                                                                        | change canonical sources; preserve and reconcile authored WIP before regeneration |
| Auto-fixable findings (rel-import self-import, etc.)          | `make fix` (rope via engine)                                                                                                            | fix corrects, never suppresses                                                    |
| Reporting of remaining findings                               | `make check`                                                                                                                            | detectors never disabled; no silent success                                       |
| Ad-hoc structural moves                                       | `make mod`                                                                                                                              | consumes the same Rope primitives; one engine                                     |
| Config/rules surface                                          | `flext-infra/src/flext_infra/config/codegen.yaml` and the owning typed rule configuration                                                | rules-as-data; no exception that hides an in-scope defect                         |
| Render inputs                                                 | SSOT + templates + PINS only                                                                                                            | any environment input in render = P0 defect                                       |
| Landing                                                       | coordinator: reviewed merge commits into the verified integration branch, expected `0.12.0-dev`; members published before root gitlinks | no administrative bypass; local green or mergeability is not integrated proof     |

## 2. Findings taxonomy (ONE vocabulary, engine + gates + receipts)

| Code                      | Meaning                                              | Level                                                                                                        | Behavior            |
| ------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------- |
| `GEN-W001`                | sibling part without `__all__`                       | gen emits warn; fix auto-fills from public surface union; check reports                                      | warn → auto-fixable |
| `GEN-W002`                | module imports itself through absolute self path     | fix relativizes (scope = declared table; flext-core overlay is a declared exception; lazy facets are exempt) | warn → auto-fixable |
| `GEN-W003`                | module outside its family layout                     | check reports; move via mod                                                                                  | report              |
| `GEN-W004`                | format/header drift on generated facet               | fix restores rendered shape                                                                                  | warn → auto-fixable |
| `GEN-W005`                | runtime SCC cycle in imports (SCC solver)            | check reports; root cause at owner                                                                           | report              |
| `GEN-E001`                | stale `__all__` (export declared, absent in sibling) | gen FAILS LOUD                                                                                               | error               |
| siblings symbol collision | same public name in two parts of one family          | gen FAILS LOUD                                                                                               | error               |

## 3. Findings flow (one detector, one consumer)

1. Engine stages read typed rules (Pydantic models parsed once via `u.Cli.yaml_*`).
2. `gen` emits warnings into the single per-repo receipt (findings + timings).
3. `fix` consumes the declared fixable findings through their existing native owners.
   Dependent projections reuse the owning semantic engine and publisher; no public
   verb invokes another public verb recursively. A separate canonical generation
   run proves the resulting fixed point.
4. `check` reports the remainder; the invocation stays red while findings remain.
5. New rule = typed section in `config/codegen.yaml` / `rules/*.yaml` — never an ad-hoc
   detector class.

## 4. Transaction loop per repository

```
snapshot (input-CAS, authenticated)
 → plan EVERYTHING (pyproject, templates, mise, lazy-init, docs) — ONE rope project per
 repo
 → publish through the existing owner, with its actual authenticated guarantees
  → single receipt (findings + timings)
```

- Failure mid-publication (gen **and** fix): follow ADR-014 §4, which supersedes the
  former permission to undo an invocation's published effects. Preserve the first
  failure, authenticated inputs and actual effect receipt for authorized forward
  correction. Prove recovery through the real public publication contract.
  The historical journal reference `flext-fkfmu` remains pending reconciliation;
  it does not authorize another journal or recovery path.
- Race handling: preserve the first failed receipt, coordinate writers, adopt compatible
  input changes and rerun only after reconciliation. Never hide a CAS failure through
  retry or proceed with unresolved findings. Reset, restore, stash, rebase and
  force-push of shared work are forbidden.

## 5. Resume procedure (new session)

> **Execution ownership updated 2026-09-17.** `flext-itpd1.3` owns recovery ordering,
> serialized gates, integration and closure. Workers deliver bounded repairs and
> evidence; they never merge or close Beads. Follow the explicitly approved recovery
> scope, never the newest local filename. Approval to use a private plan does not
> authorize copying or publishing it.

1. Read coordinator Bead `flext-itpd1.3`, the assigned owner Bead and this runbook.
   Reconcile historical receipts against the current candidate.
2. Inventory current tips, registered worktrees and pending changes; never assume peer
   lanes are absent or exclude existing work by its directory name.
3. Use the rig environment and the current tracker contract in the
   [stabilization runbook](../ways-of-working/stabilization-checkpoint-0.12.md). The
   coordinator owns semantic Beads updates and records command, cwd, exit, decisive
   output and candidate identity.
4. Preserve all WIP; implement only the explicitly assigned owner paths after fresh
   inspection. Coordinate overlapping changes instead of discarding them.
5. In the coordinator's serialized window, follow the current root lifecycle:
   `make setup` → `make gen` → `make fmt` → `make fix` → `make mod` → `make check` →
   `make tests`, plus applicable build, public runtime and native documentation/link
   validation. Source admission covers every governed repository and code tier before
   native incremental Testmon admission. Prove repeated gen/fix/fmt are no-op,
   exit-zero runs after the final relevant mutation; do not force a second full test
   pass or substitute historical receipts.
6. Stay in the current recovery cycle until the entire fleet has warning-free,
   finding-free integrated receipts. Owner repairs remain in that cycle; no historical
   exception or successful partial gate authorizes closure.
7. Publish members before root gitlinks and revalidate on the integrated SHAs. Later
   mutations invalidate affected receipts. The recovery does not authorize an unrelated
   release or tag; closure belongs to the coordinator after proof.

### Implementation reconciliation

Older plans and receipts are evidence, not parallel implementation contracts. Resolve
each topic through its newest accepted ADR and active source owner before changing
code. A documented target is not proof that the running implementation meets it.

For each repair, inventory the actual entry point, implementation, consumers and
generated projections. Keep one productive implementation and one publication route.
Remove superseded zero-consumer branches rather than adding another detector,
compatibility facade, parser, source cache or recovery path. Distinct required
operations may share a helper, but moving duplicate behavior behind two names does
not complete consolidation. Preserve source identity, intended MRO, native failure
propagation and authenticated publication while completing the consumer cutover.

Re-exercise the original failing boundary after consolidation, then the complete
declared workspace scope. Record unresolved findings in the active Bead; neither a
smaller finding count nor an isolated successful project closes the fleet cycle.

## 5b. Historical resume context (2026-09-15, proven — preserved as evidence)

The following is a dated report, not current runtime evidence or permission to resume
its old commands. Current ownership and lifecycle above supersede its execution
instructions.

- Reported flext-infra tip `c3f574807` (0.12.0-dev); `_conform` stale drift adopted via
  tip; `_models/_config` split (13 untracked + 2 M) ready to land through gen ×2 with
  parity probe 107/107 dunders vs `pre_config.json` (scratch snapshots intact).
- The historical session reported `bd`/`rg` shim problems. That report does not
  authorize bypassing the current rig environment or canonical command surface.
