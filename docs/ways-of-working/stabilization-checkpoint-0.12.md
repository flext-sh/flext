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

```bash
make setup
make gen
make mod
make gen
make gen
make fix
make fmt
make check
make test
make build
```

One failure → fix the verb owner; no timeout inflation; no testmon removal. Run the
verbs without selectors at the active workspace root. Documentation corrections follow
this same cycle. Validate changed behavior through the applicable real public consumer
before tests, and complete native documentation, executable-example, and link
validation; a docs-only receipt does not replace the required gates. Prove that
repeated `make gen`, `make fix`, and `make fmt` leave the same final candidate unchanged
and exit zero. An overlapping edit, regeneration, or
integration-base change invalidates the affected receipts and requires renewed
convergence and validation. Generation convergence alone does not prove convergence of
the complete configured docs lifecycle. Residual warnings and findings block closure.
Do not start another cycle before proving the whole fleet green on the integrated and
published SHAs.

Pydantic 2 and the Mypy `pydantic.mypy` plugin are mandatory. The operator's scoped
exception suspends only `prop-decorator` and `call-arg`; it does not waive the remaining
lint or type gates. Code changes made to work around either diagnostic are regressions
and must be reverted surgically after causal-hunk review and real-consumer validation,
by the existing policy and regression owners. The source contract and authorization
are recorded in `flext-2guq8`; generated configurations
must reflect their canonical policy owner rather than being patched at consumers.

## (b) Central Beads contract

- Rig-store commands run through the selected repository's generated environment:
  `direnv exec <repo> bd ...`. City-store commands use the configured city scope
  through `direnv exec <city-root> gc bd --city <city-root> ...`; never infer an endpoint
  from another rig.
- Activation comes from the generated `.envrc`/`.envrc.local` (AGENTS_GAS_CITY_ROOT +
  the city publication port + the rig metadata database)
- Inspect configured identity with `direnv exec <repo> bd context --json`. Before
  effects, verify access to the assigned Bead through that same selected environment,
  for example `direnv exec <repo> bd show <assigned-bead> --json`. Configuration
  discovery alone does not prove database connectivity or current task ownership.
- Endpoint identity repair belongs to the city owner through the authorized
  `gc rig set-endpoint flext --inherit` route; it is not a routine worker action.
- Never initialize an embedded database/manual port (source:
  `flext-infra/docs/guides/execution-context.md`)
- Resolve effective orchestration through `gc status`. Orchestration suspension and
  tracker suspension are independent; retain a selected available tracker, never
  reactivate orchestration or create a substitute ledger to continue repository work.

## (c) Integration

**Top priority: the working branch tracks current integration.** Every increment must
deliver working behavior and keep the root, the 31 members, and the shared environment
green. Preserving WIP means adopting it and fixing its defects; no failure is accepted
as pre-existing or hidden behind exclusions.

Before starting an increment and before publishing it, refresh the remote references and
absorb `origin/0.12.0-dev` through a `--no-ff` merge, resolving each conflict with
review of both sides' features. A base change invalidates the affected receipts. Do not
accumulate features on a branch far from integration.

The coordinator mandatorily performs the integration of every increment: complete
implementation, local fleet lint, type, test, documentation and build gates, real
runtime, CI on the exact PR head, a GitHub PR merged administratively into the verified
integration branch, and post-merge proof. A local merge, pushed branch, draft PR, or
source-only report is not delivery. The next increment only starts after that
composition is green. Administrative authorization replaces only the independent
approval; it keeps every gate. While the tracker runtime is suspended, do not create
another tracker and do not declare phase closure.

For cross-repository changes, order the commits by the producer/consumer contract and
validate every intermediate composition before landing it. Do not rely on simultaneous
merges. Publish member commits before the root gitlinks; prove the final composition on
the published integrated SHA as well.

1. Workers deliver bounded repairs and evidence; they do not merge or close Beads. The
   coordinator maintains dependencies, integration decisions, and the serialized window
   of generation, environment, and gates.
2. Preserve WIP and review scoped commits (explicit paths, never `git add -A`);
   deliver through a GitHub PR merged with an administrative merge commit into the
   verified integration branch, expected `0.12.0-dev`, with the applicable review and CI.
3. Publish members before updating the root gitlinks. Push fast-forward; divergence
   requires absorption through merge and revalidation, never rebase or force-push.
4. Revalidate gates, generation convergence, and runtime on the published integrated
   SHA; a local checkpoint or test does not prove fleet stability.
5. The coordinator records in the Bead the command, cwd, exit, decisive output, SHAs,
   and review/CI/runtime receipts; it closes only obligations with delivered proof.

## (d) Active exterminations

Retired selectors and substitute local Beads databases remain prohibited. The former
lockfile-extermination instruction is historical, not permission to delete current
managed locks. Toolchain and dependency locks change through `make upg` at their
canonical owner; `make setup` consumes and reconciles the declared toolchain. Never
hand-edit or discard locks, replace the selected tracker, or bypass a failing owner.

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
