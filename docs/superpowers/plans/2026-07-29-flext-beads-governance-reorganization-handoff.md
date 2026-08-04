<!-- HISTORICAL / SUPERSEDED — 2026-08-04 -->
> **Status: historical / superseded.** Live execution SSOT is Beads (`mro-z89e` and children),
> not this plan. Do not treat tool versions, worktree paths, `bd` versions, `rtk` mandates,
> or active-leaf IDs in this file as current law. Prefer branch-matched
> `.agents/skills/flext-law/SKILL.md` and the active Bead.
> Superseded by Governance and Reality Repair (`mro-z89e.35`).

# FLEXT Beads Governance Reorganization — Autonomous Handoff Plan

> Status: intentionally not executed by the author of this handoff.
> This document preserves the original Beads-only plan so another orchestrator
> can execute it after the P0 `bd`/Mise hotfix. Live execution state, evidence,
> dependencies, and closure must be recorded in Beads, not maintained here.

## Outcome

Reorganize the FLEXT Beads graph into one precise, resumable, multi-session
control plane whose issues alone tell any agent:

- what FLEXT owns and what AI Hub merely distributes;
- which canonical owner must change;
- which internal and external projects consume the change;
- which divergence or overlay each consumer needs;
- which GitFlow branch, pull request, commit, validation phase, and promotion
  state belongs to the work;
- what was proved, what remains, and the exact next action.

This lane changes Beads semantics only. It does not implement source,
configuration, workflow, Make, CI, documentation, branch, pull request, or
worktree changes. Those mutations belong to implementation Beads created or
linked by this reorganization.

## Root Epic Theme and Authority

Canonical epic theme:

`FLEXT — Generated, self-contained conformity for workspaces, standalone projects, and external references`

The root program must remain in the FLEXT ledger. `flext-infra` owns generic
FLEXT build and delivery behavior: Make, conform, generated project roots,
Mise, direnv, `.envrc`, workspace/standalone classification, Beads
provisioning, developer tools, formatting, linting, type gates, CI generation,
and release propagation. `flext-core` and `flext-cli` remain the SSOT for their
respective runtime and CLI domains. AI Hub owns only universal agent law,
skills, orchestration, discovery, and distribution; it must never duplicate a
FLEXT implementation.

Use `mro-z89e` as the candidate surviving FLEXT control-program epic and
`mro-z89e.2` as the candidate `flext-infra` engine lane. Confirm both against
the live `bd 1.1.2` ledger before changing them. If live evidence identifies a
newer canonical survivor, preserve history by superseding these candidates
into that survivor rather than creating a parallel program.

## Preconditions

Execution starts only after all of the following are true:

1. The canonical executable is upstream `github:gastownhall/beads` release
   `1.1.2`, provisioned through the FLEXT Mise/setup contract.
2. The FLEXT ledger is recovered into the supported shared-Dolt schema with
   prefix `mro`; the old embedded or development-schema ledger is retained as
   a verified backup, not used as live authority.
3. `bd doctor`, `bd status`, and a backup sync succeed on the live ledger.
4. The executor captures the current root epic, all descendants, duplicate
   candidates, dependency edges, external references, open branches, pull
   requests, worktrees, and active assignees before the first mutation.
5. Concurrent implementation agents have bounded ownership. This lane may
   update semantic Beads content, but must not steal an active implementation
   issue or rewrite evidence produced by its worker.

If any precondition fails, create or update one P0 recovery Bead and stop the
graph mutation. Do not use schema-skew bypasses, JSONL as the sync protocol, an
embedded database, or a custom Beads build.

## Inviolable Graph Rules

1. One outcome has one owner. Duplicate epics are superseded, never left as
   competing active authorities.
2. History is preserved. “Remove” means `bd supersede` or a documented merge
   into a survivor; no issue history is physically deleted.
3. Parent/child expresses decomposition. `blocks` expresses executable order.
   `discovered-from` preserves provenance. Cross-project references that cannot
   be represented as valid Dolt dependencies are reciprocal typed references
   in both Beads, never illegal cross-database edges.
4. A Bead may not be active without an observable outcome, owner repository,
   priority, issue type, acceptance contract, validation route, next action,
   and stop condition.
5. No Bead may claim a branch, PR, commit, release, project status, or gate
   result that was not verified from the real surface. Unknown data is recorded
   as unresolved with the exact discovery command.
6. GitFlow is explicit:
   `feature/*`, `bugfix/*`, or `hotfix/*` → validation on `develop` →
   application of the same validated artifact to production. A new commit after
   validation returns the issue to the validation phase.
7. Every branch and PR is related to exactly one implementation Bead. Every
   implementation Bead records its branch, base, target, PR URL/number, head
   SHA, validation SHA, and promotion status.
8. FLEXT-managed first-party projects are exhaustive checklist entries.
   Third-party forks, mirrors, vendored trees, and content-only submodules are
   explicitly excluded and must not receive FLEXT mutations or quality gates.
9. Divergences are represented as config-owned overlays, with an owner,
   rationale, affected projects, validation, and removal condition. Duplicate
   behavior outside the canonical generator is forbidden.
10. Warnings are defects. No warning is waived, suppressed, or converted into
    a non-blocking note when it indicates a root-cause problem.

## Target Graph

The target is a small hierarchy with explicit execution order:

| Level | Canonical responsibility | Required content |
| --- | --- | --- |
| Root program epic | FLEXT 0.12.0 development-to-production conformity | Scope, authority boundaries, global definition of done, fleet register, release sequence |
| Engine epic/lane | `flext-infra` generators and canonical Make surface | SSOT owners, generated projections, RED/GREEN/surface contracts, affected consumers |
| Domain owner links | `flext-core` and `flext-cli` changes required by the engine | Typed API/CLI contracts without duplicated infrastructure |
| Internal rollout epic | Every first-party FLEXT repository and workspace | One child/register entry per project, divergence, branch/PR/SHA, gates, status |
| External rollout epic | Independent consumers outside the FLEXT workspace | Reciprocal Bead reference, overlay, compatibility contract, branch/PR/SHA, validation |
| GitFlow promotion epic | Validated development artifact promoted unchanged | develop validation, production application, rollback evidence, release closure |
| Governance/audit lane | Staleness, duplicate ownership, broken references | Re-runnable graph checks and exact remediation |

The existing `mro-wkii.17.41` topology/conform feature and `mro-d9d5`
idempotent `make setup` bug are implementation authorities to link beneath the
engine lane, not duplicate. Re-read their live fields and descendants before
deciding whether they remain children, blockers, or discovered implementation
work.

## Consolidation Ledger

The following identifiers came from the pre-hotfix audit and are candidates,
not permission to mutate blindly. Resolve their current `mro-*` IDs, status,
parents, children, dependencies, and notes with `bd 1.1.2` first.

| Candidate | Intended action | Preservation rule |
| --- | --- | --- |
| `rysa`, `ek42`, `47r7` | Consolidate competing conform/generation epics into the surviving FLEXT engine epic | Move unique children and evidence first; supersede only after no unique scope remains |
| `m8xq.8` | Split the portion that invades generic conform ownership from its project-specific remainder | Keep domain-specific work under its original owner; link generic work to the engine |
| `zl4a.5`, `zl4a.5.1` | Re-parent Make/resolver defects out of the AWX/Teleport program | Preserve discovery provenance and link the consumer impact back to AWX/Teleport |
| `ai-hub-67xi` | Already reported superseded by `ai-hub-raur.7.4` | Verify only; do not repeat the mutation |
| timeout duplicates | Already reported consolidated into `ai-hub-7lyn.3.1.7.6` | Verify survivor contains every unique acceptance condition |
| `ai-hub-t449.10` | Reported owner of universal governance contract | Keep universal law there; link FLEXT, do not copy FLEXT implementation details into it |
| `raur.1` | Candidate surviving workspace-state execution slice | Absorb valid intent from `tael`, `mb90`, and `o13c` only after confirming they are truly duplicate or obsolete |
| `tael`, `mb90`, `o13c` | Candidate superseded workspace contracts | Preserve any unique consumer/evidence; remove obsolete “same branch for every submodule” assumptions |
| `5u5z` | Candidate owner for external dependencies | Verify authority, then move only external-consumer relationships |
| `qtka` | Candidate owner for GitFlow validation | Verify authority, then centralize validation/promotion semantics without owning implementations |
| `raur` | Candidate historical incident owner | Retain incident evidence only; no live implementation ownership |

For every candidate, the executor records a before/after graph snapshot and a
reason. A survivor must receive unique description, design, acceptance,
dependencies, evidence, and links before the duplicate is superseded.

## Required Content of Every Executable Bead

Each active epic and implementation Bead must be self-sufficient and contain:

1. **Identity:** outcome-oriented title; repository/database namespace; issue
   type; priority; assignee or explicit unassigned owner.
2. **Problem reality:** current observed behavior, exact divergence, canonical
   expected behavior, and why the gap matters.
3. **Authority:** canonical config/schema/generator/API owner; generated
   projections and consumers; explicit no-duplicate/no-customization rule.
4. **Scope:** included projects, paths, surfaces, branches, and explicit
   exclusions, especially third-party repositories.
5. **Topology classification:** workspace root, attached first-party member,
   independent standalone project, external consumer, or excluded content-only
   dependency.
6. **Execution contract:** ordered small slices, one Bead/branch/worktree/PR per
   independently mergeable change; root-Make commands; RED→GREEN→real-surface
   evidence expected from the implementation worker.
7. **GitFlow state:** branch class, branch name, base, target, PR, head SHA,
   validated SHA, develop result, production result, and whether a later commit
   invalidated validation.
8. **Dependencies:** parent, blockers, provenance, related external Beads, and
   why each relation exists.
9. **Fleet checklist:** one row per affected internal and external project,
   with divergence/overlay, status, branch/PR/SHA, gate evidence, and next
   action.
10. **Evidence ledger:** command, cwd, timestamp, exit code, decisive output,
    tested scope, generated-idempotence result, and real-surface artifact.
11. **Resume token:** last completed atomic action, live blocker, exact next
    command, mutable files/Beads to re-read, and stop condition.
12. **Closure:** proof that no required project is missing, every dependency is
    resolved, the validated artifact reached the intended environment, and all
    reciprocal references agree.

## Internal Project Register

Derive the authoritative list from `config/workspace.yaml` and the live git
topology; never freeze a remembered list as SSOT. The root epic must contain a
generated-at-a-point-in-time execution register for:

- the FLEXT superproject/workspace root;
- `flext-core`, `flext-cli`, `flext-infra`, and `flext-tests`;
- every first-party platform, domain, Singer tap/target, and dbt member declared
  by the workspace SSOT;
- every independent first-party FLEXT project discovered by AI Hub that is not
  attached to the workspace.

Each row records classification, repository namespace, owning Bead,
development branch, GitFlow branch/PR, current SHA, conformity/setup status,
manual divergence, config overlay, required gates, and production application
status. A row may only be marked complete from repository-specific evidence.

Submodules that are third-party forks, mirrors, vendored sources, or content
references appear in an exclusion register with the reason and the config
owner that prevents conform, lint, format, setup, CI, and release mutation.

## External Consumer Register

For every independent project that consumes FLEXT infrastructure:

1. Create or identify an implementation Bead in that project's own Dolt
   database.
2. Add a reciprocal reference from the FLEXT rollout Bead to the external Bead
   and back, including repository, database namespace, issue ID, relation type,
   and expected artifact/version.
3. Record whether the project is standalone, an external workspace, or an
   excluded third-party source.
4. Record its divergence and config overlay; an overlay is allowed only when
   automatic topology inference cannot express the legitimate difference.
5. Record branch, base, target, PR, head SHA, validated SHA, required Make
   gates, `make setup` result, and promotion status.
6. Never use unsupported cross-database dependency edges. Reciprocal references
   plus an orchestrator validation Bead are the coordination mechanism.

The rollout epic cannot close while any external register row has an unknown
owner, missing reciprocal reference, unvalidated overlay, or unverified
production state.

## Execution Waves

### Wave 0 — Recover and Freeze the Semantic Baseline

Back up and validate the shared-Dolt ledger; inventory the complete graph and
active writers; resolve all candidate aliases after schema recovery; attach the
before-state evidence to the root program. No graph mutation occurs until this
baseline is reproducible.

### Wave 1 — Establish the Single FLEXT Program

Enrich the surviving root and engine epics with authority, topology,
exclusions, GitFlow, fleet registers, evidence, resume token, and closure
contract. Link—not copy—the universal AI Hub governance Bead and the canonical
`flext-core`/`flext-cli` domain owners.

### Wave 2 — Consolidate and Re-parent

Process one duplicate family at a time. Move unique children and relations,
merge unique semantic content, validate that no active work became orphaned,
then supersede the empty duplicate. Re-parent misplaced Make/conform/resolver
defects to the engine and preserve consumer-impact links to their former
programs.

### Wave 3 — Build the Internal Rollout Register

Enumerate every first-party project from the topology SSOT. Create or enrich one
project-control Bead per repository that has actual rollout work. Attach
branch/PR/SHA and manual-divergence state. Link all controls to the engine
artifact and order them by blockers, not by arbitrary repository order.

### Wave 4 — Build Reciprocal External Controls

Discover independent consumers through AI Hub. Create or enrich their local
Beads, add reciprocal references, classify legitimate overlays, and create one
FLEXT orchestration/control row for each. Explicitly exclude third-party
repositories.

### Wave 5 — Normalize GitFlow and Promotion Reality

For each implementation lane, verify branch class and real remote state.
Represent the order as implementation → develop validation → production
application of the exact validated SHA/artifact. Create missing validation or
promotion Beads only when the work is genuinely absent; never create ceremony
duplicates.

### Wave 6 — Validate and Synchronize

Run the supported Beads integrity, lint, stale/orphan, cycle, blocked/ready,
epic-status, Dolt status, backup, and remote sync surfaces. Re-read every
modified Bead after sync. Verify reciprocal external references and every
branch/PR/SHA claim. Attach exact evidence and leave one unambiguous next action
for any intentionally open lane.

## Validation Contract

The reorganization is accepted only when all conditions are binary true:

- one active FLEXT root program and one active generic infrastructure engine
  own the declared scope;
- all duplicate candidates are either proven distinct or superseded with their
  unique history preserved;
- no active implementation issue is orphaned, cyclic, multiply owned, or
  missing an executable next action;
- every first-party internal project has an explicit rollout or explicit
  not-applicable row;
- every independent external consumer has reciprocal Bead references and its
  own local execution issue;
- every third-party fork/content-only source is excluded from mutation and
  gates;
- every implementation lane records GitFlow branch, PR, head/validated SHA,
  develop validation, and production application state;
- every warning discovered by supported Beads diagnostics has a root-cause
  correction or an active blocking Bead;
- the shared-Dolt database validates, is backed up, synchronized, and re-read
  successfully using canonical `bd 1.1.2`;
- another agent can resume any open lane using only its Bead and linked
  authorities, without reconstructing intent from chat history.

## Stop Condition

Stop immediately when the live Beads graph satisfies the validation contract,
the shared-Dolt remote is synchronized, and every open Bead contains an exact
resume token. Do not proceed into implementation, branch mutation, PR changes,
worktree cleanup, or source/config edits from this lane.

## Handoff Starting Point

The P0 `bd`/Mise failure interrupted this plan before semantic execution.
Historical audit data identified the candidates above, but the supported
`bd 1.1.2` ledger must be recovered and queried again before they are acted
upon. Treat current live Beads data as authoritative after recovery; treat this
document and old checkpoints as intent and provenance only.
