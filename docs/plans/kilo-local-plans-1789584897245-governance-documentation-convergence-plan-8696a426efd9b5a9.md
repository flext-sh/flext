# FLEXT Governance and Documentation Convergence Plan

<!-- TOC START -->

- [Outcome](#outcome)
- [Lessons Incorporated](#lessons-incorporated)
  - [Planning baseline — 2026-09-17](#planning-baseline-2026-09-17)
- [Authority and Ownership Map](#authority-and-ownership-map)
- [Coordination Contract](#coordination-contract)
- [Ordered Plan](#ordered-plan)
  - [Phase 0 — Elect the Cursor and Freeze Duplicate Work](#phase-0-elect-the-cursor-and-freeze-duplicate-work)
  - [Phase 1 — Build the Source/Projection Inventory](#phase-1-build-the-sourceprojection-inventory)
  - [Phase 2 — Land the Provider-Neutral Governance Bundle](#phase-2-land-the-provider-neutral-governance-bundle)
  - [Phase 3 — Repair and Land the AI Hub Projector](#phase-3-repair-and-land-the-ai-hub-projector)
  - [Phase 4 — Reconcile FLEXT Maintained Sources](#phase-4-reconcile-flext-maintained-sources)
  - [Phase 5 — Repair Documentation Generators and Publication Authorization](#phase-5-repair-documentation-generators-and-publication-authorization)
  - [Phase 6 — Regenerate the Fleet in an Exclusive Window](#phase-6-regenerate-the-fleet-in-an-exclusive-window)
  - [Phase 7 — Reconcile Beads and Durable Memory](#phase-7-reconcile-beads-and-durable-memory)
  - [Phase 8 — Validate, Review, Land, and Re-Prove](#phase-8-validate-review-land-and-re-prove)
- [Failure and Recovery Rules](#failure-and-recovery-rules)
- [Acceptance Checklist](#acceptance-checklist)
- [Explicit Non-Goals](#explicit-non-goals)

<!-- TOC END -->

## Outcome

Converge the current FLEXT governance and documentation corpus without turning session
plans into authority, editing generated projections, mixing unrelated repository work,
or invalidating authenticated generation with concurrent writers.

This plan is a bounded child of the `0.12.0-dev` stabilization program. It owns only
documentation/governance authority and projection convergence. Runtime modernization
remains owned by `flext-5fxu6.4`; live execution state for this plan remains in Gas City
Bead `flext-itpd1.2`.

It supersedes the documentation/governance/projection portions of
`.kilo/plans/2026-09-16-flext-infra-continuation-plan.md`; that older plan continues to
describe the flext-infra runtime modernization dependency. Neither local plan replaces
the live Bead cursor.

Completion requires:

- one explicit owner for every maintained or generated surface;
- current behavior, accepted decisions, proposals, and historical evidence clearly
  separated;
- provider-neutral governance landed in `~/agents`, project routing reduced to
  branch-matched deltas, and AI Hub projections reproduced from those owners;
- documentation generators fixed before their outputs are regenerated;
- two-pass generation and deployment fixed points executed without active source
  writers;
- native documentation, link, static, test, and runtime gates green on merged SHAs;
- Beads and durable memories containing no duplicate execution owner or transient
  generated-file fact.

## Lessons Incorporated

The previous execution exposed planning defects that this plan forbids:

1. Four near-identical P0 documentation Beads were created by parallel sessions. One
   tracker owner must be elected before delegation.
2. `make gen` completed once across 32 repositories, then failed because
   `docs_collection.py` changed during authenticated verification. A later `make docs`
   failed because `_conform/execute.py` changed during its atomic snapshot. Generation
   cannot share a window with source writers.
3. Files labelled generated had no identified generator owner. A generated marker is
   invalid until source, renderer, transaction, pruning behavior, and fixed-point test
   are named.
4. Workspace-local `.kilo/plans` were temporarily promoted into published recovery docs.
   Gas City Beads owns live state; versioned runbooks own durable recovery; local plans
   are dated evidence only.
5. Hand-written docs copied command counts and selectors (`make val`, `PROJECT=`,
   `WHAT=`) that drifted from `make help`. Active docs must link to or derive from the
   live public surface rather than duplicate it.
6. A root docs run reached a publication boundary with no authorized
   `config/plan-collection.yaml`. Missing publication authorization must fail closed;
   ignored/private plans may not be used as a convenient source.
7. Cross-repository changes accumulated before any repository reached its own landing
   boundary. Each physical owner needs an independently reviewable PR and merged-SHA
   proof.

### Planning baseline — 2026-09-17

| Repository/surface      | Current evidence                                                                                                                                                                           | Consequence                                                                                                                 |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `~/agents`              | reconciled `dev` commits are ahead of `origin/dev`; setup/audit/check/runtime/test-full are green, but concurrent untracked `tools/sync_governance.py` claims a forbidden second projector | preserve AI Hub as sole projector; remove the foreign script after contribution review, then review/land/publish the bundle |
| AI Hub                  | active `aihub-gvw99` documentation/projector reconciliation and existing addendum                                                                                                          | compose with it; do not create a second projector plan                                                                      |
| FLEXT root              | maintained-doc/local-law WIP plus generated effects in all member worktrees                                                                                                                | classify by owner; no root aggregate commit                                                                                 |
| flext-infra             | docs generator WIP overlaps active runtime changes                                                                                                                                         | source edits may proceed only on disjoint paths; validation waits for writer lease                                          |
| root docs transaction   | `make docs` blocked by absent plan-publication authorization                                                                                                                               | implement explicit disabled state, never private-plan ingestion                                                             |
| fleet generation        | first pass completed; second pass invalidated by concurrent `docs_collection.py` change                                                                                                    | current outputs are untrusted adoption input, not fixed-point proof                                                         |
| plan collection residue | untracked `config/plan-collection.yaml`, `docs/plans/collection-*`, and `docs/plans/kilo-local-plans-*` may bridge ignored session plans into publishable docs                             | quarantine from staging immediately; prune only through the repaired docs transaction                                       |

## Authority and Ownership Map

| Surface                                                 | Canonical owner                                                              | Projection/consumer                                                           | Rule                                                                                           |
| ------------------------------------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Provider-neutral rules, skills, commands, agents, evals | `~/agents` GovernanceBundle                                                  | installed provider homes and project projections                              | Project-specific FLEXT detail is forbidden here.                                               |
| Project discovery and provider projection               | `~/ai-hub` manifests, models, templates, projector                           | `.github`, `.claude`, `.gemini`, `.kilo`, `.kilocode`, peer instruction files | AI Hub is the sole projector; generated files carry markers and are never edited in consumers. |
| FLEXT branch-matched domain law                         | `flext/.agents/provider.toml`, router, `flext-law`, `flext-law` command      | FLEXT members/standalone consumers                                            | Contains only the FLEXT delta over `~/agents`.                                                 |
| Hand-written FLEXT docs and ADRs                        | `flext/docs/**` maintained sources                                           | MkDocs site and readers                                                       | Describe current reality or label target/proposal/history explicitly.                          |
| API/catalog/MkDocs projections                          | `flext-infra` typed docs models, renderers, templates, transactions          | root/member generated docs and `mkdocs.yml`                                   | Renderer owner and stale-file pruning are mandatory.                                           |
| Documentation knowledge index                           | `flext-infra` docs inventory renderer                                        | `docs/knowledge-index.md`                                                     | Indexes maintained pages; it does not invent CRG topology.                                     |
| CRG communities/reports                                 | code-review-graph raw generator plus an AI Hub typed publication transaction | `docs/architecture/communities/**`, `crg-reports/**`                          | Publish only after graph freshness proof; no manual copy and no flext-infra CRG import.        |
| Execution state                                         | Gas City Beads                                                               | agents/operators                                                              | No Markdown queue or local/embedded tracker.                                                   |
| Durable project memory                                  | `bd remember`; Kilo memory only where the client explicitly requires it      | future sessions                                                               | Store stable decisions, never current line numbers, counts, ports, or WIP SHAs.                |
| Session evidence                                        | `.kilo/plans/**`, reports, logs                                              | current session/handoff                                                       | Never published as durable authority or collected without explicit authorization.              |

`~/.agents` resolves to `~/agents`; they are one authority, not two bundles to reconcile
independently.

Any surface not classifiable in this table blocks editing and generation until a child
Bead records its owner.

## Coordination Contract

1. `flext-itpd1.2` is the sole documentation/governance parent. Relate or supersede
   duplicates only after transferring their unique evidence and children.
2. Every implementation child owns one physical repository and a disjoint path set.
   Research agents may overlap; implementation agents may not.
3. Before every effect, record the repository, branch, HEAD, expected dirty paths,
   owner, first red gate, and stop condition in the child Bead.
4. The coordinator alone starts generation, deployment, fleet propagation, and landing.
5. A writer lease is required for `make gen`, `make docs`, or `make deploy`:
   - the coordinator owns one generation-wave child Bead;
   - that child has `until` dependencies on every active Bead touching an authenticated
     source and records their landed candidate SHAs;
   - all thematic writers are landed or explicitly release their paths after unique
     contributions are adopted;
   - live status matches the declared expected path set;
   - authenticated source inputs are unchanged for the whole command;
   - any `atomic source changed`/`authenticated state changed` result stops the wave and
     names the competing owner; it is never retried unchanged.
6. Unknown or concurrent changes are adopted fix-forward. No reset, restore, stash,
   rebase, clean, force-push, or blanket regeneration is allowed.
7. Generated-output commits contain only outputs attributable to the recorded owner
   change. Unrelated concurrent files and gitlinks are excluded.

## Ordered Plan

### Phase 0 — Elect the Cursor and Freeze Duplicate Work

1. Read `flext-itpd1.2`, `flext-itpd1.2.1`, `flext-bzwz7.1`, `flext-3rld2`, and
   `flext-5fxu6.4.28` from Gas City.
2. Keep `flext-itpd1.2` as the parent because it is attached to the stabilization epic
   and contains the current execution evidence.
3. Transfer unique children/evidence, relate live concurrent slices, and supersede only
   idle exact duplicates.
4. Record cross-repository dependencies rather than creating a second FLEXT owner:
   - `~/agents` governance landing;
   - AI Hub `aihub-gvw99` projector reconciliation;
   - flext-infra `flext-bzwz7.1` generator/fixed-point repair;
   - publication authorization `flext-itpd1.2.1`.
5. Add an `until` dependency from the generation-wave child to the `flext-5fxu6.4` slice
   that eliminates the divergent runtime ownership between `codegen/conform.py` and
   `_conform/*`. The documentation PR does not perform that cutover, but no `gen/docs`
   fixed-point claim is valid while both owners or their writers remain active.
6. Mark untracked plan-collection config/manifests/projections as quarantined paths in
   the parent Bead. They may be inspected as evidence but never staged, published, or
   used as authority; removal is owned by Phase 5's transaction.
7. Publish a path ownership table in the parent Bead before resuming writers.

**Exit:** one parent cursor, no unowned child, and no two implementation agents assigned
to the same file or generator transaction.

### Phase 1 — Build the Source/Projection Inventory

For every active documentation/governance **family** (path pattern + producer), record
the following once and list only exceptions per file:

- class: maintained source, generated projection, historical evidence, runtime receipt,
  or orphan;
- canonical repository/path and responsible Bead;
- producer command and template/model/schema where generated;
- consumers and deployment destinations;
- pruning behavior and fixed-point test;
- whether it is safe to publish.

Mandatory inventories:

- `~/agents`: rules, skills, commands, agents, ADRs, evals, package data;
- AI Hub: projection manifests/templates, installed bundle, global/provider homes,
  project-local override declarations;
- FLEXT: `AGENTS.md`, local `.agents`, peer-tool files, ADRs, standards, guides, project
  pages, runbooks, plans;
- flext-infra: docs contracts/renderers/templates, API/catalog/MkDocs outputs, knowledge
  index, plan collection;
- CRG: graph SHA, wiki/community/report producer and output set;
- all 31 members: generated docs and gitlink state.

An orphan is not edited in place. Either assign and implement its owner with a public
test, or remove the false generated claim and classify it as maintained source.

**Exit:** zero unknown generated markers and a complete source→projection map.

### Phase 2 — Land the Provider-Neutral Governance Bundle

Owner: `~/agents`.

1. Review the reconciled commits currently ahead of `origin/dev`; confirm all previous
   conflict markers and duplicate identities are absent.
2. Prove `GovernanceBundle.load()` and the CRG semantic suite contain exactly the
   required happy, ambiguous/edge, and should-not-trigger roles.
3. Require provider-neutral composition:
   - mandatory invariants in rules;
   - conditional procedures in skills;
   - invocation grammar only in commands;
   - discovery metadata in agents/config;
   - specialization expressed as `extends:` DAGs, never copied bodies.
4. Confirm scope-nav is retired without shim and CRG is the sole graph route.
5. Confirm Gas City/fix-forward/runtime laws are generic where appropriate and contain
   no FLEXT-specific paths or Bead IDs.
6. Reject the concurrent `tools/sync_governance.py` projector after comparing its unique
   contribution. Do not add `make gen`, projection templates, or deployment ownership to
   `~/agents`; transfer any reusable typed planning requirement to the AI Hub projector
   Bead, then remove the duplicate route.
7. Run the native `make help`-declared audit/static/mod-check/waza/duplication/
   runtime/test gates, commit explicit paths, push, review, merge, and rerun on merged
   `dev`.
8. Publish/install the merged bundle version before any consumer projection.

**Current evidence:** `make setup`, `make audit`, `make check`, `make runtime`, and
`make test-full` exited 0; 35 tests passed, Waza validated 132 suites, and isolated
artifacts loaded 244 resources. This is not landing proof because the commits are ahead
of `origin/dev` and the competing projector script is unresolved.

**Exit:** merged provider-neutral bundle and an installed runtime whose version,
resource root, inventories, and digests match the merged source.

### Phase 3 — Repair and Land the AI Hub Projector

Owner: AI Hub Bead `aihub-gvw99`; compose with its existing documentation addendum
rather than duplicate it.

1. Adopt current AI Hub WIP and reconcile its active PR/lane before editing overlapping
   projector or hook files.
2. Make the installed GovernanceBundle, not the `~/agents` checkout, the runtime
   projection input.
3. Classify every target as global projection, project projection, or explicit local
   override. Unmanaged copies are adopted or retired transactionally.
4. Generate concise peer-tool pointers to project `AGENTS.md` plus only required
   provider bootstrap. Do not copy CRG or universal governance bodies into each file.
5. Add deterministic generated markers, source provenance, and pruning for all managed
   provider surfaces.
6. Resolve config contradictions at typed owners (`config/mcp.yaml`, workspace
   association, provider manifests); eliminate hardcoded checkout roots.
7. Own the transaction that publishes current CRG wiki/report outputs into declared
   project documentation destinations, including generated markers, provenance, and
   pruning. The CRG tool creates raw artifacts; AI Hub publishes them without making
   project runtimes import CRG.
8. Run `make setup`, `make gen` twice, native checks/tests/docs/build, and the public
   isolated projector test/dry-run owned by AI Hub. Do not deploy into FLEXT or global
   homes while downstream source writers are active.
9. Land AI Hub independently and prove the projector runtime from the merged SHA.
   Fleet/global deployment moves to Phase 6's exclusive window.

**Exit:** one installed bundle produces deterministic global and project surfaces; no
consumer file is a copied authority.

### Phase 4 — Reconcile FLEXT Maintained Sources

Owner: root FLEXT documentation/local-law slice.

1. Reduce the local provider to router + branch-matched FLEXT delta. Correct tracker
   examples to `direnv exec <repo> bd ...`; `gc` is used only for city
   lifecycle/endpoint operations.
2. Keep active resume authority in Gas City and versioned runbooks. Remove published
   links that promote ignored `.kilo` plans.
3. For each ADR:
   - preserve the accepted decision;
   - add an explicit implementation-status block when rollout is partial;
   - distinguish current `make mod` behavior from the planned separate `ast` verb/tree;
   - never cite target architecture as current runtime evidence.
4. Replace copied command counts/selectors with `make help` ownership. Active docs must
   contain no `make val`, `PROJECT=`, public `WHAT=`, or direct tool route. Historical
   releases/audits/plans retain exact historical commands and are clearly labelled
   historical.
5. Correct stable architecture facts only from live owners: config/settings access,
   `c/t/p/m/u` and operational facades, generated Make ownership, project inventory, and
   current partial thin-driver rollout.
6. Make examples syntactically valid and public-boundary based. Config-owned values come
   from typed production owners, not literals.
7. Validate all internal links and MkDocs navigation before projection.

**Exit:** maintained docs agree with current runtime/accepted decisions, all proposals
are labelled, and historical evidence remains intact but non-operative.

### Phase 5 — Repair Documentation Generators and Publication Authorization

Owner: flext-infra children `flext-bzwz7.1` and `flext-itpd1.2.1`.

1. Complete typed owners for root/member MkDocs config, repository identity,
   version/project metadata, API/catalog pages, knowledge index, and stale-file pruning.
2. Root navigation discovers all maintained docs; it is not a fixed three-page list.
   Repository labels derive from the same typed URL contract as links.
3. Keep CRG generation outside flext-infra runtime. The knowledge index links to present
   CRG artifacts but does not invent communities or import CRG.
4. Make plan collection an explicit deny-by-default contract. For the FLEXT root,
   declare the typed disabled state with zero sources; absence of a file must not
   ambiguously mean either disabled or misconfigured. Enabling later requires separately
   approved providers, adapters, destinations, and pruning. It must never self-source
   `docs/plans`, ingest ignored `.kilo` plans, or publish private session inventories
   merely to green the gate. Existing versioned `docs/plans` entries remain labelled
   historical evidence until a separate retention decision; they are not a live queue.
5. Replace the quarantined hand-written config with the reviewed typed disabled source,
   then transactionally prune generated manifests, `incoming/` payloads, and Kilo-plan
   projections. The generated-files manifest must prove the deletions; no manual
   filesystem cleanup or blanket staging is valid.
6. Add public behavior tests for source discovery, repository identity, metadata/version
   derivation, pruning, link/navigation completeness, publication authorization, and
   second-run stability. Exercise the public contracts backed by
   `PlanCollectionTimestamp`, `PlanCollectionSource`, `PlanCollectionConfig`,
   `PlanCollectionRevision`, and the docs-collection facade rather than private helper
   order.
7. Run the flext-infra docs/runtime gate only in an exclusive writer window.

**Exit:** every generated doc has a typed producer and pruning policy;
unauthorized/private plans remain unpublished; flext-infra docs generation is
byte-stable.

### Phase 6 — Regenerate the Fleet in an Exclusive Window

Coordinator-only phase after Phases 2–5 are merged or frozen at approved candidate SHAs.

1. Classify the outputs left by the earlier invalidated generation wave as adoption
   input, not fixed-point evidence. Preserve useful diffs for comparison but let the
   final merged generator re-derive every managed byte.
2. Capture status and expected dirty paths in root plus every member.
3. Update CRG and record graph SHA before regenerating graph-owned artifacts.
4. Run root `make gen` once; classify every effect by producer and repository.
5. Reject any effect outside the ownership inventory or any banned artifact (`uv.lock`,
   `mise.lock`, `exclude-newer`).
6. Run root `make gen` again without intervening writers. Require exit 0 and no
   additional effect.
7. Run root `make docs`; then run `make gen` once more to prove docs did not reintroduce
   drift.
8. From merged AI Hub projector and installed bundle SHAs, run `make deploy` twice while
   all provider/project source owners are frozen. Require the second deployment to have
   zero effects and classify every destination.
9. Regenerate CRG raw wiki/reports through the documented CRG generator on the recorded
   current graph SHA, then publish/prune project pages through the merged AI Hub
   transaction. Manual copying is invalid evidence.
10. Commit each member's attributable generated outputs in that member only. Validate
    and land member commits before updating root gitlinks.
11. Before each root gitlink update, prove the member worktree is clean, its HEAD is the
    merged integration SHA, and the proposed gitlink equals that exact SHA. Dirty-status
    annotations are diagnostics, never gitlink values.
12. Update root gitlinks last; never stage all dirty submodules or unrelated WIP.

**Stop conditions:** any live source mutation, lock timeout, missing producer,
unexpected gitlink, generated projection requiring a manual patch, or second-run effect
stops the whole wave.

**Exit:** fixed point across all declared members, clean per-repository generated
commits, and root gitlinks referencing landed member SHAs.

### Phase 7 — Reconcile Beads and Durable Memory

1. Preserve `flext-itpd1.2` as the only parent execution cursor.
2. Relate or supersede duplicates only after their unique notes, dependencies, and
   children are transferred.
3. Store stable ownership decisions in `bd remember`; do not store current counts, line
   numbers, ports, WIP SHAs, or gate results as durable memory.
4. Reconcile explicitly requested Kilo project memory with the same stable facts; remove
   contradictions rather than maintaining two variants.
5. Update each repository Bead with exact commit/PR/merge/runtime evidence.
6. Run `bd lint` and fix completeness at the owning issue without inventing reproduction
   steps for non-bugs.

**Exit:** no duplicate active owner, no stale closed issue presented as live, and memory
describes only durable architecture/governance decisions.

### Phase 8 — Validate, Review, Land, and Re-Prove

Execute per repository in dependency order: `~/agents` → AI Hub → flext-infra → FLEXT
members → root gitlinks.

For each repository:

1. merge the current integration tip into the lane with `--no-ff`;
2. rerun the public lifecycle declared by its `make help`, stopping at first causal
   failure;
3. require docs/link checks, generated fixed points, static gates, tests, build, and
   applicable deployment/runtime proof;
4. use CRG change/risk/affected-flow review on the candidate SHA;
5. stage explicit paths, commit one owner-coherent slice, push, review, and merge by
   merge commit;
6. rerun affected gates on the merged SHA and verify the installed/deployed runtime
   where the repository owns it;
7. record evidence and close only the completed child.

A parent closes only after every child is merged, root gitlinks are current, consumer
projections converge, and all repositories are clean against their integration remotes.

## Failure and Recovery Rules

- **Concurrent authenticated source change:** stop; record path and writer; wait for
  that owner to land or release the path; never retry unchanged.
- **Generated file with no producer:** block publication; assign a producer or
  reclassify the file before editing.
- **Missing plan-collection configuration:** keep `make docs` red until the typed
  explicit-disabled state is implemented, or until separately approved sources/adapters
  exist; no self-source or private-session shortcut.
- **Quarantined plan projection:** any attempt to stage `config/plan-collection.yaml`,
  `docs/plans/collection-*`, or `docs/plans/kilo-local-plans-*` before Phase 5's
  provenance-safe transaction is a hard veto.
- **Projection differs from source:** fix model/config/template/projector, then
  regenerate; never patch the output.
- **Doc contradicts runtime:** prove runtime via public command, then correct the
  maintained source or label the content as proposal/history.
- **Duplicate Bead:** transfer unique state to the elected owner, relate active
  concurrent work, then supersede only the idle duplicate.
- **Cross-repo red gate:** stop at that repository; do not advance downstream
  projections or gitlinks.
- **Historical command is obsolete:** retain it only inside clearly historical evidence;
  active instructions use the current public surface.
- **Graph/source disagreement:** source wins; rebuild the graph before generated
  architecture claims.

## Acceptance Checklist

- one Gas City parent owns the program and every child has a physical repository/path
  scope;
- `~/agents` is merged, published, installed, and green through its native gates;
- `~/agents` contains no projector or `make gen`; AI Hub is the sole
  projection/deployment owner;
- AI Hub projection/deploy is deterministic on the installed bundle and has no copied
  universal authority;
- local FLEXT provider contains only branch-matched delta and correct Gas City/CRG
  routes;
- all active ADRs/docs distinguish current, accepted target, proposal, and history;
- active docs contain no retired `make val`, selector-based `PROJECT=`/`WHAT=`,
  scope-nav, alternate tracker, or banned artifact guidance;
- every generated document has a named source, generator, pruning rule, and public
  fixed-point test;
- plan collection is explicitly disabled with zero sources until an approved provider
  exists, and never ingests private `.kilo` evidence by convenience;
- root/member `make gen` reaches a clean second pass in an exclusive writer window;
- `make docs` and subsequent `make gen` do not reintroduce drift;
- CRG pages match a recorded current graph SHA and obsolete pages are pruned;
- each repository lands independently with explicit paths, PR/CI evidence, merge commit,
  merged-SHA revalidation, and clean status;
- root gitlinks move only after member landings;
- every moved gitlink equals a clean member's merged integration HEAD;
- Beads and durable memories contain no duplicate authority or transient generated fact.

## Explicit Non-Goals

- Do not combine the flext-infra god-module/runtime rewrite into the documentation PR.
- Do not rewrite historical plans/releases to make their old commands look current.
- Do not publish private session plans merely because a docs gate expects a source.
- Do not make flext-infra depend on code-review-graph.
- Do not redesign third-party forks or impose FLEXT law on them.
- Do not claim fleet convergence from one successful generation pass or from a dirty
  tree.
