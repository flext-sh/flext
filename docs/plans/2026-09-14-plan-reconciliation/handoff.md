---
title: Critical audit and resumption contract
updated_at: 2026-09-14T21:55:00Z
source: Operator requests, repository owners, Beads, native command evidence
work_item: flext-ro6mj.1
---

# Verdict

The requested outcome has not been delivered. Useful source changes and WIP
checkpoints exist, but no demonstrated end-to-end cycle takes a real plan and
its annexes through collection, projection, semantic reconciliation, Beads/ADRs,
reviewed integration, and idempotent recollection. Infrastructure work must not
be reported as a percentage of corpus completion.

This audit concerns the approved plan and the implementation performed in this
effort, not a completed reading of the entire historic FLEXT corpus. Evidence
below distinguishes direct observations, earlier command results, worker
reports, and remaining hypotheses. No closed Bead was reopened or closed merely
from a source-code reading during this audit.

## Authority and requested behavior

The [approved plan](../2026-09-14-plan-reconciliation.md) remains the product
contract. Success is a simple prompt, “Reconcilie os planos do FLEXT até
terminar”, invoking a reusable workflow distributed through AI Hub. Its source
is `agents`; FLEXT owns project configuration; `flext-infra` owns the collector,
generation and existing transaction/refactoring engines.

The operator progressively made these constraints explicit:

1. Consolidate all plans into `~/docs/plans`, with full annexes/research in
   same-basename directories, ISO timestamps and documented precedence.
2. Revalidate all open and closed Beads against implementation and documentation.
   Reconcile one plan through integration before another; newest first in the
   ascending index, and dependency owners before project consumers.
3. Preserve the oldest ADR identity within a decision scope; incorporate newer
   decisions inplace and annotate changes immediately below affected passages.
   Newer duplicate text becomes consultation links, not a competing authority.
4. Automate collection through `custom.mk` and `make docs`; update skills,
   commands and rules at their owners, distributed through AI Hub.
5. Fixed Make effects, no operator-supplied APPLY switch or replacement selector.
   Integrity validation remains mandatory; deleting the editing tool named
   `apply_patch` or blindly renaming domain vocabulary is not this requirement.
6. Separate FLEXT worktree, direnv, rapid WIP publication, no force-push/rebase,
   and eventual reviewed no-ff integration. Preserve original and concurrent WIP.
7. Facade composition belongs in the generator. Necessary structural moves
   use advanced Rope through the existing loop/callbacks and all consumers.
8. After a serialization detour was authorized, the operator explicitly restored
   automation as priority. Preserve that WIP; do not treat it as the core outcome.
9. Latest request pauses implementation for this critical handoff and requires
   preserving and publishing current work as WIP with PRs, not merging it green.

The approved storage choice is versioned FLEXT `docs/plans` plus automatic home
projection, not a new home Git repository. Historical provider material is
evidence, not governing instruction. Entire private transcripts must not enter
Git, PR bodies, logs, or this handoff.

Related records are evidence, not a replacement mandate: `flext-uqji` concerns
the historical plan migration; `flext-im2my` concerns open-Bead normalization;
`flext-5mgye` and `flext-xeg9x` were closed as obsolete by the fixed-Make change.
In particular, do not revive `flext-xeg9x`'s old request to propagate an APPLY=N
mode: that contradicts the operator's later fixed-effect direction. Its closed
state does not prove today's complete docs workflow. `cosmos-e286z` tracks the
paused external consumer cut and remains in progress.

## Requirement-to-evidence assessment

| Required outcome | What exists | What remains unproven or absent |
| --- | --- | --- |
| Automatic source collection | Typed collector, provenance, revision and file-plan owners | Root `config/plan-collection.yaml` absent; complete provider adapters absent |
| All providers and annexes | Files/same-basename companions; Claude/Poolside parser sources | Codex, VS Code, Kimi schemas/adapters; OpenCode wiring; linked external annex traversal |
| Temporal ordering | Original timestamp and UTC separated; unresolved precision explicit | Real corpus ordering and conflict adjudication; no invented timestamp allowed |
| Safe home projection | External participants, leases, exact snapshots, absent-parent witnesses | Real first import, edits, interruption recovery, second-run convergence |
| Usable `make docs` | Root pre-docs hook and thin script committed | Configuration, generated launcher, CLI/template contract and all native gates |
| AI Hub propagation | Typed resource policy and binary/mode publication changes | Producer integration before consumer refresh; installed wheel/sdist fidelity and live propagation |
| One-prompt sequential workflow | `plan-reconciliation` skill and `/reconcile-plans` command sources | Real activation, one-plan integration and interrupted resumption |
| All Beads reconciled | Active epic/task updated, all-status revalidation procedure | Exhaustive open/closed sweep and four independent sources per adjudication |
| Plans/ADRs consolidated | Approved semantics and limited owner documentation amendments | No completed corpus-wide semantic deduplication or linked-plan retirement proof |
| Rope propagation | Callback and guarded replacement sources written | Last `make mod` failed before callback; necessary callsites remain unmigrated |
| Integration of complete increment | Multiple published checkpoints and Draft PRs | No green native round, independent approval or post-merge proof for this increment |

## Deep critique of execution

### Blocker: implementation risk displaced the user-visible slice

The work expanded across transaction capabilities, Rope/codemod repair, package
resource schemas, parser redesign, SDK resource gates, and serialization. Some
are legitimate prerequisites: external publication requires explicit authority,
and dropping generated findings invalidated the codemod receipt. The failure
was not identifying those defects; it was carrying many unvalidated cuts at
once without first establishing the smallest controlled end-to-end plan cycle.
The late absence of root configuration is decisive: the advertised entrypoint
cannot yet execute its basic input contract.

Correction: freeze new abstractions, map each open cut to a current consumer and
acceptance failure, and finish producers before consumers. Do not start another
corpus plan or unrelated repair campaign. Required red gates remain real defects,
but every repair must state its causal link and bounded stop condition.

### Blocker: source discovery was mistaken for adapter readiness

Finding a provider directory or writing a pure parser does not authenticate a
session, establish project association, include every annex, or safely publish
derived content. `private-inventory` correctly fails rather than claiming
coverage, but it is still an incomplete adapter. Several schemas were not proven
on real native artifacts. Same-basename discovery omits linked research elsewhere.

Correction: configure every source family from topology and provider metadata;
exercise the exact parser/adapter contract on private controlled data. Retain
causal failures and coverage evidence without emitting raw transcripts. Cache
identity must include adapter/driver/schema version, not just unchanged bytes.
Prove source renames, overlapping roots, attachment links and retired revisions
cannot duplicate or revive an already adjudicated plan.

### Blocker: cross-repository contracts were changed out of landing order

AI Hub now consumes `SkillRecord.resources`, while its dependency is still
`agents-governance` from `agents@dev`; the corresponding producer is on a WIP
branch. Source agreement across two checkouts is not installed compatibility.
Likewise, docs generation removed a request effect flag while the Make template
still passes `mode=--apply` to mutable docs actions. Direct source inspection
found that residue; no successful canonical invocation disproved the mismatch.

Correction: validate and integrate the producer, refresh consumers using native
dependency/setup/generation paths, and validate installed artifacts before
deployment. Do not use editable imports, PYTHONPATH, handwritten projections or
test changes that freeze incorrect defaults to disguise the broken boundary.

### Major: safety machinery is written but not demonstrated

Exact bytes/mode/identity comparisons, external leases and absent-parent witnesses
are justified for home publication. They also expand the critical failure
surface. Tests were written, not run, for several new paths. Per-file guarded
publication must not be described as aggregate atomicity without recovery proof.
The new ast-grep publisher needs coincident insertion/overlap tests and must not
silently omit a generated finding or accept stale snapshots.

Correction: establish real CLI/YAML ingress, controlled first publication and
unchanged second run; then concurrent edit, symlink/traversal, missing ancestor,
interruption, recovery and failed-publication residue tests through native
owners. Do not expose the operator's home corpus to an unproven transaction.

### Major: historical gate and PR evidence became stale

Earlier `agents` checks passed before parser/resource-policy changes. AI Hub's
67 passing tests did not reach the new publisher tests. A merged old PR does not
mean later commits on the same branch were merged. Fresh inspection found both
Infra PR728 and AI Hub PR773 merged while subsequent work still needed new PRs.
Root gitlinks also differ from member checkouts after integration absorption.

Correction: bind every claim to SHA, cwd, exact command, exit and scope. Fetch
before ancestry proof, preserve all member work, and never blindly commit older
member gitlinks over a newer integrated root. WIP publication and reviewed
functional integration are different outcomes.

### Major: the active task became a multi-repository mega-lane

`flext-ro6mj.1` accumulated collection, fixed Make, governance distribution,
transaction repair, resource packaging and inherited migrations. A long note
stream preserved evidence but did not make a short independently landable unit.
The epic's older design still described a different order than the amended plan.

Correction: align Beads design with the approved automation-first order and
retain one active intent. At resumption, partition proven owner boundaries into
reviewable prerequisite work under the same epic, without inventing duplicate
trackers or falsely closing the active acceptance contract. Do not mass-change
historic Beads based on this audit; their four-source verification remains work.

### Major: orchestration needs stronger boundaries

Parallel workers usefully found owner defects and preserved WIP, but concurrent
producer/consumer editing made test applicability and checkpoint ownership hard
to follow. Additional script-resource gates exposed genuine MCP/Anthropic/
Playwright failures; those are not evidence that the requested collector works.
No exclusion or suppression should hide them, and fixing them must not silently
become a new framework project.

Correction: main owns one dependency graph, gate window and merge decision.
Workers receive disjoint paths and a concrete stop condition. Reviews report
what was actually executed, not merely tests added. Preserve another actor's
work in separate attributed-as-adopted WIP when necessary.

## Retain these sound choices

Keep the approved storage and sequencing decisions; source-owned generators;
the existing transaction and callback loop rather than a second publisher;
explicit external destination authority; private transcript boundaries; honest
unresolved timestamps; all-status Beads verification; oldest scoped ADR identity;
and Draft WIP preservation without force-push. Do not restart from scratch or
delete working changes because the overall increment remains incomplete.

## Implementation cursor and source map

Primary worktree: `/home/marlonsc/flext-worktrees/plan-reconciliation`, branch
`feature/plan-reconciliation`. Infra member: `fix/plan-reconciliation-make-contract`.
Original `/home/marlonsc/flext` must not receive implementation edits. Earlier
read-only evidence found its root at `0.12.0-dev`, but Infra had moved to
`fix/docs-renderer-contract`; the earlier statement “all 32 currently on dev”
is no longer established. Re-read, cooperate, and preserve, never reset.

Canonical owners and exact investigation entrypoints:

- Root `custom.mk`, `scripts/docs/collect_plans.py`, `config/workspace.yaml`;
  missing collection configuration is the first visible functional gap.
- Infra `_models/docs_collection.py`, `_utilities/docs_collection*.py`,
  `docs/collector.py`, `docs/generator.py`, and `services/cli_routes_validate.py`.
- Infra `codegen/codegen_transaction.py`, `mise_artifacts_workspace.py`,
  `_mise_artifacts_{files,journal,verification,recovery}.py`, `_codegen_staging.py`.
- Infra `_utilities/codegen_path_cutover.py`, `rope_runtime_refactors.py`,
  `_protocols/rope_runtime.py`, `codemod/{semantic_apply,batch_apply,batch_gates,
  batch_replacements}.py`. Last mod failure preceded Rope; do not claim cutover.
- Infra `_utilities/docs_contract.py`: `docs_workspace_contract` hardcodes
  `FLEXT Workspace`; root artifacts use it for standalone AI Hub. Reuse the
  metadata owner rather than modifying the consumer's expected title.
- `agents/skills/tool/plan-reconciliation/` and its procedure/input-contract;
  `commands` reconciliation entry; `skills/tool/beads-reval/`; Claude/Poolside
  parser resources and session-resume callers.
- `agents/config/skills.json`, `src/agents_governance/{catalog,skill_resources}.py`,
  `tools/python_resources_gate.py`; `tools/artifact_gate.py` is still unchanged.
- AI Hub governance mapper/bundle/projection planner and accepted-artifact
  publisher; ADR-0008 amendment. New resource tests lack a completed native run.
- Paused migration: flext-tests native Payload model/protocols/consumers and
  `docs/guides/native-payload.md`; core TOML aliases; CLI atomic file helper;
  earlier Cosmos consumer annotation work. Preserve separately and revalidate;
  no fleet serialization completion claim.

## Native evidence ledger for this handoff only

This is an immutable audit snapshot, not another tracker. Detailed earlier
evidence remains in `flext-ro6mj.1` notes and native reports.

| Cwd | Exact command | Exit and decisive scope |
| --- | --- | --- |
| FLEXT worktree | `direnv exec . make status` | 0; environment/Git only, not collection |
| FLEXT worktree | `direnv exec . make check` | 2; 32 completed, 0 passed, 32 failed, earlier snapshot |
| FLEXT worktree | `direnv exec . make audit` | 2; latest session68939 reached 32 repositories, generated differences |
| FLEXT worktree | `direnv exec . make mod` | 2; session69763 expected 3 ast-grep errors, receipt contained 4; before Rope |
| agents | `direnv exec . make check` | Earlier 0 invalidated by later changes; latest47706 exit2, 13 resource Pyright errors |
| agents | `direnv exec . make test-full` | Earlier 0, 10 passed; not rerun after final parser/resource changes |
| agents | `direnv exec . make setup` | 0; installed Pyright1.1.414, not overall gate proof |
| agents | `direnv exec . make fmt` | 0; formatting only |
| AI Hub | `direnv exec . make test` | 2; session35894, 1456 collected, 67 passed, 2 failed before new publisher tests |

AI Hub report: `.reports/tests/20260914T212449.338947Z-3105774/junit.xml`.
Failures were textual import-purity policy and metadata-derived docs title.
Review the existing AST/cold-import architecture test before changing a textual
test; do not simply allowlist a forbidden dependency. The attempted purity/doc
patch was not applied. Current source may have changed since the failed run.

Latest ast-grep repair preserves generated findings and forwards documented
UTF-8 replacements through the guarded publisher; tests are written but unrun.
Latest agents failures include missing MCP/Anthropic/Playwright development
dependencies and lifecycle/message typing; no suppression was introduced.
Artifact packaging does not yet prove binary/mode fidelity. The resource policy
also needs scrutiny for duplicate identities and mutable override exposure.

## Ordered resumption contract

1. Read this package and Beads, inspect current Git/PR state, and preserve all
   WIP. No new lane or tracker. Confirm the active task remains `flext-ro6mj.1`.
2. Audit the exact producer/consumer dependency graph. Stabilize `agents`
   resources: declared development requirements, actual SDK types, CLI parser
   tests and installed wheel/sdist bytes/mode proof. Run native checks and full
   tests; integrate only after independent review. Do not add production skills
   solely to carry artificial test fixtures.
3. Refresh AI Hub through its native dependency path; validate resource create,
   rename, removal, foreign-file preservation, two concurrency windows and
   installed execution. Correct standalone docs at Infra's metadata owner and
   preserve the existing import-boundary architecture tests. No deploy before
   staged real-consumer proof.
4. Stabilize Infra's transaction and docs contract. Resolve the pending codemod
   receipt repair through `direnv exec . make mod`; generated findings are
   blockers at their generator, never permission for direct facet edits. Prove
   every necessary Rope callback consumer is propagated. Reconcile Make callers
   with the new fixed-effect CLI, then regenerate through `make gen`.
5. Supply topology-derived collection configuration and finish authenticated
   adapters for every source family. Validate CLI/YAML types, annex traversal,
   revision/version identity and retirement anti-reimport. Do not replace absent
   adapter support with manual export prerequisites or successful empty results.
6. Exercise a controlled real plan plus annexes through the canonical `make docs`
   path: initial import, existing canonical/home edits, failure/recovery and
   unchanged second run. Guard incoming provenance against generic docs rewriting.
7. Reconcile that same plan semantically: full reading; integrated code, history,
   measured reality and registered Beads; inplace oldest ADR edits; docs and
   governance links. Native gates, review, merge commit, post-merge proof and
   Bead evidence are prerequisites to proceeding to another plan.
8. Only then traverse the complete inventory newest-first, projects dependency-
   first, with one active plan. Include unmatched and closed Beads. Final
   recollection must expose no pending revision before epic closure.

Do not run broad repeated gates while files are being edited without a gate
window. Do not widen into the paused serialization campaign unless a concrete
native acceptance failure requires its owner correction. No completion claim
from a Draft PR, test count, source search, package build, or another actor's merge.

## Publication receipts

WIP preservation is authorized even with red functional gates; it is not merge
approval. Root PR242 and agents PR148 are Draft/WIP. AI Hub's new PR774 preserves
commits not included by old PR773. Infra's old PR728 was already merged; subsequent
checkpoint requires its own Draft PR. Final SHAs, PRs and remaining Git state are
recorded in the publication amendment below and the active Bead, after pushes
complete. No private provider data was collected or published by this handoff.

Publication amendment (2026-09-14):

| Repository | Preserved checkpoint | PR / integration target |
| --- | --- | --- |
| FLEXT root | Handoff `a6f9be8985`; subsequent WIP records the exact member snapshot | [242](https://github.com/flext-sh/flext/pull/242), `0.12.0-dev` |
| flext-infra | `df262eb228a9fefb76b0332515d9559523ddd241` | [733](https://github.com/flext-sh/flext-infra/pull/733), `0.12.0-dev` |
| flext-cli | `9336a7cd20be2672fda7bc31fab88dacb9b9af89` | [169](https://github.com/flext-sh/flext-cli/pull/169), `0.12.0-dev` |
| flext-core | `9c08b68b1b36d2f952bbbc14c4b401e7b94635c0` | [475](https://github.com/flext-sh/flext-core/pull/475), `0.12.0-dev` |
| flext-tests | `a0a0ddb532f3fcca085fc6c1aa274f00bd9bf683` | [111](https://github.com/flext-sh/flext-tests/pull/111), `0.12.0-dev` |
| agents | `db4cdaa55c5a91d03f399ddd8da8fdc40db9a767`, then `14210a111013568502dbe307ff1eb413fed7d3e7` | [148](https://github.com/datacosmos-br/agents/pull/148), `dev` |
| AI Hub | `4d34b263e783e957c73d96bdc5936de486992a1f`, includes resource cut `8068298d1` | [774](https://github.com/datacosmos-br/ai-hub/pull/774), `dev` |
| Cosmos GitOps | `5494ef755ad86f76c0091fc4c0f262507905a5f2`, includes annotations `64ff6a545` | [175](https://github.com/datacosmos-br/cosmos-gitops/pull/175), `develop` |

The root gitlink checkpoint is an explicit as-is preservation of the separate
worktree, not a claim that its member tips contain the newest integration tips.
Before eventual merge, reabsorb each fresh integration base with no-ff, validate
and roll up the resulting published gitlinks. Never promote this snapshot by
blindly replacing newer integration pointers. The original checkout and broad
unrelated Cosmos superproject WIP were not staged or modified by this handoff.

All listed PRs were observed Draft/WIP; none was merged by this handoff. Agents
checkpoint `14210a111` separately preserves previously shared `wip-beads.sh`
changes without attributing their authorship or correctness to this task. AI Hub
PR773's merge did not contain the later resource cut: fresh ancestry returned1;
therefore PR774 was necessary. Infra PR728 likewise does not replace PR733.
Cosmos GitOps was already published and clean; no new write was necessary.
Its checks included skipped native CI/merge-guard, not full acceptance.

Preservation checks are intentionally bounded: Infra's commit and fast-forward
push returned0, but its cached diff check returned2 for one trailing blank line
in `tests/unit/codemod/test_batch_replacements.py`. This defect was preserved in
the requested as-is WIP, not hidden or described as a green check. Earlier source
checks predated that new untracked file. No hooks were bypassed.
