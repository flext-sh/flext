# Stabilization runbook — checkpoint 0.12.0

<!-- TOC START -->

- [Current authoritative decisions](#current-authoritative-decisions)
  - [ADR-028 Decision Links](#adr-028-decision-links)
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

## Current authoritative decisions

The common contract reconciled on 2026-10-25 is recorded in `flext-itpd1.17`.
The three recovered Claude plans and 327 private memory files are dated evidence;
their old execution recipes do not override the decisions below. The consulted Codex
memory store contained no prior entries. Private transcripts and raw memory payloads
remain outside published documentation.

The Bead now records the original session identifiers, captured plan locators,
interaction boundaries and UTF-8 text digests recovered from the preserved initial
analysis. Two captured plan files differ from their last `ExitPlanMode` payload;
those revisions remain distinct, and the later copies are not presumed approved.
This historical capture has no receipt from the currently required authenticated
session adapter. Identified provenance does not certify a new extraction or close
the reconciliation delivery.

| Current decision | Origin and date | Scope and superseded instruction | Canonical owner |
| --- | --- | --- | --- |
| Preserve member dependency and tool locks; compose the workspace lock | Operator ruling `operator-ruling-2026-10-25-member-locks-uv-mise-upg-guard`, 2026-10-25 | Replaces root-only lock deletion. Only `upg` has the editable-checkout/gitlink consistency guard; ordinary work accepts shared WIP. The guard is an accepted target until implementation is proven. | [ADR-030](../architecture/adr/030-member-locks-composition-upg-guard.md) |
| Mark deprecated signatures until all consumers migrate | Operator ruling `operator-ruling-2026-10-24-deprecated-signature-window`, 2026-10-24 | Replaces immediate public-signature deletion. Delegation retains no old implementation; removal requires the complete external and fleet census. New DI-only boundaries still apply. | [ADR-028 Decision 7](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-7) and the canonical global zero-residue rule |
| Preserve shared work and publish complete green slices | Current operator shared-worktree contract and no-incomplete-pushes order, 2026-10-24/25 | Replaces clean-tree admission, rollback and incomplete working-branch publication. Only the ADR-030 upgrade guard requires its scoped committed state. | Root [AGENTS.md](../../AGENTS.md), [ADR-029](../architecture/adr/029-always-working-one-complete-cycle.md), and global fix-forward/Git owners |
| Static enforcement belongs to Infra | Operator order `operator-order-2026-10-25-core-static-enforce-off`, 2026-10-25 | Replaces import/definition-time static enforcement in Core. This is the required boundary, not a claim that migration is complete. | [ADR-028 Decision 5](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-5); Infra enforcement owner, tracked by `flext-43iz8` |
| Inject generic capabilities and isolate dialects | Operator DI/dialect and maximum-decoupling orders, 2026-10-25 | Replaces server-name registries, concrete client construction in services and library-named consumer contracts. Preserve the validated external ACL receiver exception until semantic/golden proof. | [ADR-028 Decision 15](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-15), [Decision 16](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-16), composition roots and the receiver's scoped law |
| Reuse native analysis and refactoring through existing adapters | Operator native-tool and generalized-rule orders, reaffirmed 2026-10-25 | Replaces duplicate parses, indexes and walkers where native equivalence is proven. Native model availability alone proves neither dynamic identity nor Python C3 correctness. Count and consolidate rules without narrowing coverage. | [ADR-028 Decision 17](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17); implementation and proof remain in [Infra execution context, Workspace snapshot and analysis engine](https://github.com/flext-sh/flext-infra/blob/0.12.0-dev/docs/guides/execution-context.md#workspace-snapshot-and-analysis-engine) and `flext-1engx.15`. [Decision 18](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-18) is implemented through the shared rule guide. ADR-014 and ADR-017 are subordinate where their older implementation text conflicts. |
| Align authorities before code and validate embedded code | Operator docs-first/embedded-code orders, 2026-10-25 | Read memory, AGENTS, docs, ADRs, rules, skills and Beads before implementation. Markdown/docstring code receives the same applicable native source gates. Proposed ADRs remain proposals. | Canonical global documentation owners and each project's documentation generator |
| Prove global Ruff, Pyrefly and Pytest acceptance before advancing | Direct operator order extended to Pytest, 2026-10-26 | No advance with any Ruff, Pyrefly or Pytest error. Evaluate the complete declared scope, preserve strict typing from its origin, and repair the causal owner. Pytest always uses Testmon and its persistent external database; repeated whole-suite runs and deadline inflation do not repair slowness. A configured project result, filtered input set or interrupted evaluation does not prove global acceptance. | Current native checker, Testmon and scope owners; execution evidence in `flext-itpd1.17` and consumer Beads |
| Preserve derived lazy package exports on every Python edit | Direct operator order, 2026-10-26 | Inspect the module's `__all__`, its owning `__init__.py` and the canonical generator before changing Python. Keep lazy imports derived from those exports; do not hand-maintain a competing index. Unit-test modules are exempt from this package-export requirement, not from lint or typing. | Topic-owning accepted facade/generation ADRs, each package's export declarations and the existing generator |

### ADR-028 Decision Links

| Decision | Corresponding current-decision ledger section |
| --- | --- |
| [ADR-028 Decision 5](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-5) | [Current authoritative decisions](#current-authoritative-decisions): Static enforcement belongs to Infra |
| [ADR-028 Decision 7](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-7) | [Current authoritative decisions](#current-authoritative-decisions): Mark deprecated signatures until all consumers migrate |
| [ADR-028 Decisions 15–16](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-15) | [Current authoritative decisions](#current-authoritative-decisions): Inject generic capabilities and isolate dialects |
| [ADR-028 Decisions 17–18](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17) | [Current authoritative decisions](#current-authoritative-decisions): Reuse native analysis and refactoring through existing adapters |

Provider-neutral skills, roles, rules and evaluations are authored in `~/agents/`
and projected through the existing publisher. FLEXT contributes its local delta;
its 60-second verb deadline and subsecond loading contract are not global defaults.
The stabilization owner supplies the integrated runtime/toolchain/CI matrix before the
long refactor is admitted. Consumer evidence supplements that matrix; it cannot replace
the producer handoff or close the neutral ACL epic `flext-ejsdr`.

The 2026-10-26 Ruff, Pyrefly and Pytest prerequisite covers the workspace root,
declared members and consumers in the active scope, each under its own native
configuration and dependency origins. Record the elected universe and account for
exclusions before claiming global acceptance. Missing project rows or hidden
first-party fixtures leave this prerequisite unproven even when the completed rows
report zero diagnostics. Evaluate Ruff and Pyrefly first, then complete the
remaining required `check` gates, including Mypy, before admitting Pytest through
its same-scope green-check receipt. Those checks and their repairs belong to this
prerequisite; they are not a later phase blocked by the tests they must admit.
Keep setup changes and the deferred refactor pending until the global prerequisite
is satisfied.
Keep each tool's raw exit and findings distinct from its gate verdict. An
authenticated, identity-specific exception is recorded as that explicit
disposition; a gate that accepts it does not establish zero native findings.
Do not broaden or remove the exception policy to manufacture a zero count.
Reuse the originating strict contracts. Extend, improve or generalize them at their
canonical owner when needed, then propagate the change to consumers; do not create
local replacement contracts to obtain a passing checker result.
Pytest retains the same canonical external Testmon database across successful and
failed runs. Record collection, selection, execution and deselection separately;
an integrity-checked cache hit with complete accounting is a cache hit, not a
claim that tests ran and passed. Incremental dependency selection preserves the
global declared inventory, including its applicable external and slow tests;
it does not authorize narrowing markers or dropping the check admission guard.
Profile slow collection, fixtures and execution before changing their owners;
never remove Testmon, reset its database or raise
the deadline to obtain acceptance.

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

Align the authorities above, provision only when required, and exercise the real public
consumer before static gates and tests. Resolve operations from the current native
root Make catalog. The approved slice sequence is `gen` → `fmt` → `fix` → `mod` →
`check` → `tests`, followed by applicable build and integrated consumer proof. Explicit
generation convergence and documentation operations use their current declared owner;
historical `test`, `docs` or selector spellings do not establish an available command.
The bounded `flext-0029c` public-CLI route follows the exception in root AGENTS.md.

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
lint or type gates. Code changes made to work around either diagnostic are regressions.
Review their causal hunks and correct them through the existing policy and regression
owners, preserving shared work and proving the real consumer. The source contract and authorization
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
- Endpoint identity repair belongs to the city owner for the selected rig through its
  authorized native route; it is not a routine worker action.
- Never initialize an embedded database/manual port (source:
  `flext-infra/docs/guides/execution-context.md`)
- Resolve orchestration activation from its current owner; invoke `gc status` only when
  that surface is selected and permitted. Orchestration suspension and tracker suspension
  are independent: do not invoke suspended or unselected orchestration to establish
  tracker availability, reactivate it, or create a substitute ledger.

## (c) Integration

**Top priority: the working branch tracks current integration.** Every increment must
deliver working behavior and keep the root, the 31 members, and the shared environment
green. Preserving WIP means adopting it and fixing its defects; no failure is accepted
as pre-existing or hidden behind exclusions.

Before starting an increment and before publishing it, resolve each repository's
integration branch from its current canonical declaration and branch-matched law,
including `.gitmodules` for attached members. Refresh remote references and absorb the
verified integration ref through `git merge --no-ff`, resolving each conflict with
review of both sides' features. A base change invalidates the affected receipts. Do not
accumulate features on a branch far from integration.

The coordinator mandatorily performs the integration of every increment: complete
implementation, real runtime, applicable native lint, type, test, documentation and
build gates, green required CI on the exact PR head, a GitHub PR merged administratively
into the verified integration branch, and post-merge proof. A local merge, pushed branch,
draft PR, or source-only report is not delivery. The next increment only starts after that
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
   repository-specific integration branch, with the applicable review and green CI.
3. Publish members before updating the root gitlinks. Push fast-forward; divergence
   requires absorption through merge and revalidation, never rebase or force-push.
4. Revalidate gates, generation convergence, and runtime on the published integrated
   SHA; a local checkpoint or test does not prove fleet stability.
5. The coordinator records in the Bead the command, cwd, exit, decisive output, SHAs,
   and review/CI/runtime receipts; it closes only obligations with delivered proof.

Delivery of a validated slice does not establish global fleet stabilization or close
unrelated phase obligations.

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
  (lease lock + lazy-init receipts); direct `FlextInfraModelsConfig` import in
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
