# Stabilization runbook — checkpoint 0.12.0

<!-- TOC START -->

- [(a) Canonical cycle](#a-canonical-cycle)
- [(b) Central Beads contract](#b-central-beads-contract)
- [(c) Integration](#c-integration)
- [(d) Active exterminations](#d-active-exterminations)
- [(e) Checkpoint 2026-09-20 — engine, cli floor and fleet (flext-v4fmn)](#e-checkpoint-2026-09-20-engine-cli-floor-and-fleet-flext-v4fmn)
- [(f) Checkpoint 2026-09-21 — SSOT budget extermination, tracker audit, integration campaign](#f-checkpoint-2026-09-21-ssot-budget-extermination-tracker-audit-integration-campaign)

<!-- TOC END -->

The dated status and checkpoints below are historical evidence, not current runtime,
queue, ownership, or gate receipts. Current execution follows the branch-matched law
and the active Bead; historical selectors and manual repair approaches do not override
the canonical cycle.

> **Status (2026-09-20):** `make gen` reaches a green fixed point across the fleet
> (32/32; landed fixes: 31 `config/workspace.yaml` identity manifests, bare-deps render
> in the root workspace, journal recovery #780, lazy `d/e/h/r/x` exports restored in the
> flext-infra root). Global stability is not proven yet: the namespace campaign remains
> (~2600 NS-STRUCT/NS-IMPORT findings — chosen route: ast-grep rules for the mechanical
> classes in `flext-infra/codemod/rules/` + manual waves per repo for the structural
> ones), runtime-census 1/repo (ENFORCE-079 + `extra="forbid"`), and findings in new
> flext-infra code. `flext-uno8m` holds the per-repo map; `flext-itpd1.3` coordinates
> recovery under `flext-itpd1`; sibling workstreams `flext-itpd1.2` (documentation) and
> `flext-itpd1.4` (Make machinery) keep their scopes. Beads holds live state; this
> document maintains the versioned contract. Local plans are session context: approved
> use does not authorize copying or publishing them, nor selection by newest filename.

## (a) Canonical cycle

The [FLEXT router](../../.agents/commands/flext-law.md) selects the execution
owners; [root AGENTS.md](../../AGENTS.md) supplies member command routing and
connectivity applicability. Apply those owners to the current slice. Reuse a
valid, exclusively owned environment; provisioning is conditional on its actual
state. Source generation and structural migration are required when the change
reaches their owned surfaces, not as a speculative rewrite of unrelated code.

Establish the changed public behavior, validate the complete affected contract
through native gates and prove the required generation fixed point. A later
source edit or integration merge invalidates affected receipts. Each bounded
slice can progress with its own truthful evidence; final fleet closure requires
the declared root/member population green on the integrated composition. A slice
receipt never supplies a fleet receipt.

Protected analyzer policy remains at the fleet tooling owner. The recorded
`prop-decorator` and `call-arg` ruling is resolved with its current specific
authorization; it never grants another exception. Repair a regression by
preserving current work and fixing its cause forward, rather than restoring a
historical source tree.

## (b) Central Beads contract

The selected tracker owns identity, current work and evidence. Use its native
route in the declared environment and verify access to the assigned item before
mutation. A central store does not require a local replacement database.
[Execution context](../../flext-infra/docs/guides/execution-context.md) describes
the generated activation boundary. Gas City orchestration and tracker suspension
are separate facts; this runbook does not activate either service.

## (c) Integration

Follow the global Git and phase-admission owners for review, gates, fast-forward
publication, non-rewriting integration and post-merge proof. Administrative merge
is used only under current explicit authorization; an example in an old runbook
does not grant it. Current assignment determines worker/coordinator permissions.

Land producer and consumer slices in their dependency order, validating each
supported intermediate composition. Publish member commits on their configured
integration branches before advancing superproject gitlinks. The selected Bead
retains exact source, integration and runtime receipts; none implies another.

## (d) Active exterminations

Resolve current defects from the active Bead and native findings. The dated
checkpoints below retain historical measurements, paths and interventions only.
Their selectors, rollback language, version pins and task assignments are not
current instructions. The command owner governs today's operations and locks.

## (e) Checkpoint 2026-09-20 — engine, cli floor and fleet (flext-v4fmn)

State verified after the dedicated agent cycle (evidence: bead `flext-v4fmn`,
`flext-1tcsp`):

- **Codegen engine**: conform execute composes `FlextInfraCodegenConformPlan` + roles
  mixin; `misc.py` defers the `execute` import to `TYPE_CHECKING` (breaking the
  execute→plan→misc→execute cycle); `.state` cleanup tolerates persistent residents
  (lease lock + lazy-init receipts); direct `FlextInfraConfigModels` import in
  `workspace.py`.
- **cli**: floor `click>=8.3.3,<8.4` restored (meltano cap; sources: codegen SSOT +
  projection + root `constraint-dependencies` where applicable).
- **Fleet**: 27 members with converged and landed renders; `setup`/`gen`
  fixed-point/`fix`/`fmt` green across the fleet; the flext-tests payload accepts
  `GenericAlias`/`UnionType`/`TypeAliasType` as textual atoms.
- **Pending (tracked)**: namespace/census structural wave (ast-grep rules through
  `make mod`, post-integration — bead `flext-1tcsp`); ai-hub ghost daemon
  (`aihub-yr5ft`); ai-hub services package split (`aihub-30jaq`).

## (f) Checkpoint 2026-09-21 — SSOT budget extermination, tracker audit, integration campaign

State verified in the 2026-09-21 session (evidence: epic `flext-49quw`, artifacts
`.beads/artifacts/reval260921/`, CSV ledger):

- **SSOT budget zombie exterminated**: merge `2d2a5b8ba` had resurrected the `budget:`
  block of `config/codegen.yaml` that cutover `265346e77` had killed
  (model+YAML+template). Removal landed through `5bb83e45c`; the model remains without
  `CodegenGateBudgetSpec` at tip `34765a1ee` — do NOT resurrect it without an explicit
  operator order (universal law; the `5bb83e45c` message declares the opposite intent
  and stays rejected).
- **`_models/codegen.py` shim restored**: the migration to the `_codegen/` package was
  complete (7-line shim re-exporting `FlextInfraCodegen`); the pre-migration monolith
  (`FlextInfraModelsCodegen`, 36 duplicated classes) came back through the same merge
  and was returned to the migration's end state.
- **Non-importable stems guards**: `02_api_usage.py` (has `__all__`) disproved the
  "numbered script publishes nothing" assumption; `isidentifier()` at the two lazy-init
  planner injection points (`_lazy_init_planner_aliases.py`,
  `_lazy_init_planner_exports.py`), landed in `34765a1ee`. flext-web gen green.
- **Tracker audit (`reval260921`)**: baseline 3,470 entities / 473 active; opening
  gates: clean graph, 0 duplicates (unbounded scan), 6 branch orphans, 3 cross-tracker
  deps. Batch 1: 4 stagnant claims → open, `flext-co1th` SUPERSEDED by `flext-cu85s`.
  Batch 2 (F3): `flext-czzns` and `flext-v1xzd` DONE with proven ancestry; relinks
  yirgp/cyplp/pwmej; `flext-38p39` on hold (arms proof pending). Orphans 6→4. Read-only
  analysis waves: C1 complete; A/B1/B2 redo (rate limit); C2/D in progress.
- **Dolt hygiene**: branch `list` (accidentally created by an agent) dropped with hash
  proof identical to `main`. Topology documented by the operator: integration branch
  `0.12.0-dev` is the real line; the DB `main` is future production propagation.
- **Integration campaign**: 15 open PRs mapped through the compare API — only root
  `#257` is pure-ahead with live content (21 unique patches, cherry proof 0 on base); CI
  fails the "gen fixed point" on a dirty post-gen tree → requires a convergence commit
  before the no-ff merge. The other 14 are diverged (behind 5–180 commits); today's
  residue-PRs (#786/#787/#182) belong to active lanes. Protected ladder
  (fix→fmt→gen→check→test) with `SELECTED_PROJECTS` and an anti-collision guard running
  on flext-infra.
