# FLEXT 0.12.0-dev Governance, Beads, Documentation, and Fleet Convergence

| Field | Value |
| --- | --- |
| Status | **Approved and executing** |
| Program key | `flext-012-conform-beads-docs` |
| Canonical integration branch | `0.12.0-dev` |
| Canonical workspace | Active root worktree for `flext` |
| Reused program umbrella | `mro-z89e` |
| Technical engine | `mro-wkii.17` |
| Root + 31 certification cohort | `mro-z89e.1`–`mro-z89e.32` |
| Stabilization/readiness | `mro-p68a` |
| Release boundary | `mro-e9j0` (tracked, not authorized for publication or promotion by this plan) |
| Primary execution truth | Beads, synchronized through its Dolt remote |
| Universal authority | `~/.agents` |
| FLEXT domain authority | The versioned FLEXT root governance on `0.12.0-dev` |
| Distribution owner | AI Hub, driven by canonical config, models, and templates |

This document is the durable execution handoff for the program. It replaces
earlier draft assumptions attached to this path, including the obsolete
requirements to pin Beads to an older schema-incompatible release, downgrade a
schema, use a noncanonical multi-branch hierarchy, or treat planning as the
terminal outcome. The operator has approved the plan and started the program.
Every session resumes from the live Beads graph and this contract; neither a
chat transcript nor an agent's memory is an execution authority.

## 1. Program outcome

The program establishes one canonical FLEXT control plane that works, without
project-specific bypasses, in all of these environments:

- the FLEXT superproject workspace;
- every first-party FLEXT subproject when dispatched from the workspace;
- every first-party FLEXT subproject when cloned and used standalone;
- external workspaces that consume the published FLEXT conventions;
- AI Hub distribution of universal and project governance;
- documentation generation, validation, publication, and WAZA conformance;
- Beads provisioning, namespace selection, graph governance, and durable
  multi-session execution;
- strict Python public surfaces, including generated simple `__init__.py`
  modules, automated lazy public exports, and lazy MRO/OO facades.

The canonical owner is changed once, all consumers are migrated atomically, and
the superseded implementation is removed in the same delivery cycle. A passing
special case is not success. Success means the generic owner supports every
declared topology and every affected consumer is proven through its canonical
Make surface.

## 2. Intent card

### Requested outcome

Reorganize FLEXT governance, Beads, documentation, generated project surfaces,
and fleet rollout into a self-directing program whose Beads remain sufficient
for execution across agents and sessions. The first priority is the governance
foundation: global law, FLEXT law, local scope law, and canonical AI Hub
propagation.

### Active workspace and branch

All FLEXT source work uses the active root workspace/worktree and branch
`0.12.0-dev`. Every slice begins by refreshing that branch with a fast-forward
pull and integrating live shared work fix-forward. Work is never based on
`main`, `0.20.0-dev`, an unrelated feature branch, or a historical worktree.

### Active Beads

The program does not create another umbrella epic. It reuses `mro-z89e` as the
approved program umbrella and coordinates four existing, non-competing
authorities:

- `mro-wkii.17` owns the typed technical engine and provider cutover;
- `mro-z89e` owns program governance and rollout, while its existing
  `.1`–`.32` cohort owns certification for the FLEXT root plus 31 governed
  projects;
- `mro-p68a` owns stabilization and readiness evidence;
- `mro-e9j0` owns the release boundary, but this approved program does not
  authorize a tag, artifact publication, release, or production promotion.

The program key `flext-012-conform-beads-docs` is recorded as shared metadata on
the participating epics and leaves. Existing Bead identities are preserved
whenever they still represent one valid intent. Re-parenting and dependency
corrections are preferred over duplicate creation.

### Current phase

Phase P0 is governance convergence. No later phase may redefine global, FLEXT,
or local authority while P0 is unresolved.

### Observable stop condition

The program stops only when:

1. the three-layer governance contract is canonical and propagated;
2. the live Beads graph matches the graph in this document and passes hygiene;
3. setup, conform, generation, documentation, and checks work generically from
   the root Make dispatcher in workspace and standalone modes;
4. the documentation intake is exhausted one source file at a time;
5. all first-party FLEXT projects have been rolled out and validated;
6. external consumers have explicit callback Beads and validated integration;
7. every required commit is fast-forward pushed on `0.12.0-dev`;
8. readiness evidence is handed to `mro-p68a` and the unauthorized release
   boundary is left explicitly gated in `mro-e9j0`;
9. Beads records the exact final evidence and contains no unowned program WIP.

### Preserved work

All dirty, untracked, committed, and concurrent work in the active root and its
first-party subprojects is input to fix-forward integration. It is never reset,
restored, cleaned, stashed, overwritten, or blamed. Mutable files are re-read
immediately before editing, and each commit contains explicit owned paths.

### Explicit exclusions

- Third-party fork submodules are topology references, not FLEXT-managed
  projects. FLEXT automation must not mutate, lint, format, generate, configure,
  commit, or push them.
- Fork participation is declared in `config/` only when a FLEXT tool needs a
  bounded reference to them. Such configuration may exclude them from scans or
  describe a read-only integration edge; it may not duplicate tool behavior.
- Dolt and GitHub-owned technical refs are not normalized as development
  branches.
- Historical plans, archives, backups, caches, generated projections, and tool
  homes are evidence, not live authority.
- Files and WIP owned by the parallel documentation feature lane are excluded
  from Bead/feature/branch/worktree/PR reassociation and from source mutation in
  the current reorganization slice. This durable plan, P0 governance, FLEXT
  governance skills, and their AI Hub propagation remain in scope. The
  documenter lane continues independently and consumes only landed canonical
  behavior.

## 3. Inviolable execution rules

1. Work is root-cause, source-first, and fix-forward.
2. Beads is the execution truth for scope, status, dependencies, evidence, and
   resumption.
3. One Bead represents one reviewable, independently green slice that fits
   within a session with margin.
4. One implementation Bead owns one repository, one branch, and one worktree.
5. The orchestrator owns semantic Beads operations, sequencing, integration,
   acceptance, and closure. Workers implement bounded, disjoint slices.
6. No old-and-new coexistence, fallback, shim, compatibility route, suppression,
   hardcode, duplicated generator, or hand-edited projection survives a cutover.
7. Config, settings, schemas, and generators own configurable facts. Tests and
   examples consume those owners; they never freeze today's values.
8. All setup, conform, code generation, documentation, formatting, linting,
   typing, testing, and validation run through the root Make dispatcher.
9. A missing or broken canonical Make verb is repaired at its FLEXT Infra owner
   before work continues; it is never bypassed with a direct tool command.
10. Every source commit is small, explicit-path, rebased by integration through
    fast-forward pull rather than history rewriting, and pushed immediately.
11. No force push, amend, destructive checkout, reset, clean, or stash is part
    of this program.
12. All code, comments, docstrings, templates, generated documentation, ADRs,
    skills, and Bead execution contracts are written in English.

## 4. P0 — canonical governance foundation

P0 is the mandatory first delivery. Its purpose is to remove duplicated law and
make authority resolution deterministic in a workspace, a standalone project,
and an external consumer.

### 4.1 Three-layer authority model

Governance has exactly three composable layers:

1. **Universal layer — `~/.agents`.** This is the sole universal authority for
   inviolable engineering rules and reusable global skills. AI Hub distributes
   and configures this layer but does not compete with it.
2. **FLEXT layer — root `AGENTS.md` and FLEXT routing skills.** This layer adds
   only FLEXT domain architecture, canonical Make commands, facade rules,
   project topology, required gates, and stricter delivery constraints. It
   imports or composes universal skills; it does not copy their implementation.
3. **Scope layer — project or directory `AGENTS.md`.** This layer adds only
   domain-specific scope, public surfaces, canonical owners, and additional
   acceptance requirements. It points to the FLEXT layer and never republishes
   either universal or FLEXT law.

The newest explicit operator instruction remains supreme. Below it, universal
law is resolved before the FLEXT overlay, and the FLEXT overlay is resolved
before local additions. A lower layer may strengthen a rule for its scope but
may not weaken, shadow, fork, or restate a higher-layer implementation.

### 4.2 FLEXT governance skills

The governance skills on `0.12.0-dev` are reorganized around composition:

- global `inviolable-rules`, `make-check`, and `verification-loop` remain the
  reusable fail-closed execution, command-selection, evidence, and completion
  contracts;
- FLEXT is the sole semantic owner of the versioned project-local
  `.agents/skills/flext-law/SKILL.md`; AI Hub may project it but may not author
  or duplicate it in the global catalog;
- project `flext-context-routing` detects FLEXT context and selects the exact
  global generic paths plus the exact branch-matched local `flext-law`;
- the duplicated local `flext-inviolable-rules` implementation is removed;
- the duplicate AI Hub/global `flext-law` projection is removed by the AI Hub
  owner, leaving no unqualified same-name alternative;
- detailed FLEXT architecture remains in the concise versioned FLEXT delta and
  canonical references, never copied into generic global skills;
- generated skill projections carry ownership markers and are changed only at
  the AI Hub or FLEXT generator source that owns them.

Before mutation, search resolves the existing owner, provider manifest,
consumers, generated projections, and overlap. A skill with a canonical
equivalent is consolidated into that equivalent rather than forked. The final
surface has one owner per rule and one routing path per context.

### 4.3 Canonical `AGENTS.md` forms

AI Hub owns templates for three generated forms:

#### FLEXT workspace root

The root form contains:

- the managed universal import or managed universal block, with provenance and
  an integrity marker;
- the FLEXT domain overlay;
- workspace topology and root Make dispatch rules;
- Beads and fix-forward delivery contracts;
- links to canonical ADRs and standards.

#### First-party FLEXT member

The member form contains:

- a generated pointer to the workspace root when used inside the superproject;
- a version-pinned pointer to the root governance on the same branch or release
  when used standalone;
- only the member's domain scope, owners, and additional gates;
- no copied universal block and no copied FLEXT architecture chapter.

The standalone pointer is pinned to the same branch or tag as the package. It
must never silently resolve to `main`.

#### Non-FLEXT project or external consumer

The external form contains:

- the managed universal layer;
- its own project overlay;
- an explicit dependency or integration link to published FLEXT conventions
  only when the project actually consumes FLEXT;
- no implication that FLEXT owns unrelated project governance.

All three forms are generated from typed configuration and templates. Managed
regions are idempotent, local overlay regions are preserved, and the generator
fails closed on ambiguous ownership or an unrecognized layout.

### 4.4 AI Hub propagation

AI Hub delivers the governance model through its canonical inventory, typed
models, templates, and deployment service:

1. inventory classifies every known project as universal-only, FLEXT root,
   first-party FLEXT member, external FLEXT consumer, independent project, or
   excluded third-party fork;
2. typed config selects an `AGENTS.md` profile and the permitted local overlay;
3. a single generator renders managed agent instructions and skill routing;
4. conform detects drift without mutating excluded repositories;
5. publication updates all declared projects deterministically;
6. a second generation produces no diff;
7. WAZA validates authority, links, skill metadata, examples, and publication
   readiness through Make.

AI Hub may distribute `~/.agents`, but the distributed universal content remains
owned by `~/.agents`. FLEXT owns FLEXT semantics. Scope projects own only their
local additions. Template conditionals select profiles; they do not duplicate
full governance implementations.

### 4.5 P0 acceptance

P0 is complete only when:

- the canonical owner of every governance rule and skill is documented;
- duplicate FLEXT governance skill implementations are consolidated;
- all three `AGENTS.md` profiles are generated from one canonical mechanism;
- AI Hub inventory classifies every targeted project and every excluded fork;
- workspace and standalone FLEXT resolution select the same versioned law;
- generated output is idempotent;
- `make docs` performs the complete project documentation pipeline, including
  WAZA and executable snippet validation;
- root Make checks pass for every changed repository;
- the Bead contains exact commands, working directories, exit codes, decisive
  output, generated-path evidence, and manual resolution QA;
- each repository commit is pushed before the next repository rollout begins.

## 5. Beads runtime and schema policy

The program uses the newest schema-compatible official upstream `bd`, managed by
mise and the canonical environment setup. At planning time, the observed usable
binary was built from upstream main commit
`423afdcb2813e36b2bc4c96b07e0fc3516a34495` and operated with schema version 61.
That observation is evidence for resumption, not a permanent product constant.

The following policies are binding:

- release `1.1.2` is not selected merely because it is a numbered release; it
  does not own the current schema requirement;
- the Dolt schema is never downgraded to accommodate an older executable;
- schema skew is never ignored;
- setup resolves the configured official upstream selector, verifies that the
  executable understands the live schema, and exposes it through mise, direnv,
  the project virtual environment, and Make;
- tests validate selector resolution, provenance, capability, and
  schema-compatible behavior from typed config; they do not assert the observed
  commit SHA or current schema number as a frozen literal;
- Beads is provisioned automatically for superprojects with first-party
  submodules and for explicitly configured independent projects;
- the default Beads namespace is derived from the canonical project name;
- a config overlay may map an existing exceptional namespace, but may not
  implement a second provisioning path;
- `.beads/issues.jsonl` is a passive export, never a sync or mutation protocol;
- Dolt pull precedes semantic graph mutation and Dolt push follows each
  validated semantic batch.

## 6. Canonical Beads graph

### 6.1 Program topology

The program uses existing authorities rather than nesting every concern under a
new umbrella:

```text
P0 governance: global law -> FLEXT overlay -> scope overlay
                         \-> AI Hub canonical propagation

mro-z89e     [reused program umbrella and rollout authority]
  -> P0 governance and documentation program coordination
  -> existing .1-.32 certification cohort
  -> integrated root + 31 certification

mro-wkii.17  [technical engine tracked by the program]
  -> typed topology and capabilities
  -> conform, Make, toolchain, CI, and tracker projection
  -> provider cutover and fixed point

mro-p68a     [stabilization and readiness]
  -> compatibility and operational readiness evidence

mro-e9j0     [release boundary]
  -> consumes engine, certification, readiness, and convergence evidence
  -> no publication, tag, or promotion without a later explicit operator order
```

`mro-wkii.17` and `mro-z89e` are not competing owners. The first produces the
provider contract; the second coordinates the program and certifies adoption
through its existing project-control cohort. `mro-p68a` certifies readiness.
`mro-e9j0` preserves release mechanics and the formal decision boundary without
authorizing release execution.

### 6.2 Technical engine — `mro-wkii.17`

`mro-wkii.17` is normalized as the technical epic:

> **FLEXT 0.12 Generated Repository Control Plane — typed topology, conform,
> Make, managed toolchain, CI, tracker integration, and zero-legacy cutover**

Its provider scope ends at a landed and tested internal contract on
`0.12.0-dev`; root + 31 rollout evidence remains outside it.

| Existing Bead | Exclusive technical responsibility |
| --- | --- |
| `mro-wkii.17.35` | Typed topology/capability manifest and schema |
| `mro-wkii.17.41` | Bounded technical subepic for repository roles, conform surfaces, and tracker integration |
| `mro-wkii.17.36` | Canonical dispatcher and help contract |
| `mro-wkii.17.37` | Config-owned test runtime and performance |
| `mro-wkii.17.37.6` | Managed isolated environment and executable resolution, only under `.37` |
| `mro-wkii.17.42` | Strict repeatable CLI normalization |
| `mro-wkii.17.43` | Root-local dispatch, locking, and worktree behavior |

After the live duplicate audit, `mro-wkii.17.41` owns only these missing
technical slices:

1. restrictive typed repository-role classifier;
2. Beads/mise/direnv project projection consuming the AI Hub-provisioned tool;
3. generated operational surfaces, linked to existing Make, CI, provenance, and
   setup owners rather than duplicating them;
4. workspace/member/standalone/external/fork topology and overlay matrix;
5. provider cutover, removal of legacy routes, real-consumer proof, and
   second-apply fixed point.

Existing setup and surface Beads, including `mro-d9d5.2`, `mro-to59`,
`mro-shxw`, `mro-pd8f.1`, `mro-pd8f.2`, `mro-jk1p`, `mro-sw2l.1`,
`mro-e9j0.7`, `mro-johh`, `mro-ydhf.1`, `mro-fi91`, `mro-bqt3.2`,
`mro-mwx1.1`, and `mro-re80.10`, are tracked or made exact dependencies after
live intent verification. No `.17.41` child reimplements an active owner.

### 6.3 Program rollout and certification — `mro-z89e`

`mro-z89e` is retained as:

> **FLEXT 0.12.0-dev — Canonical Governance, Conform, Documentation, and Fleet
> Convergence**

It is the reused program umbrella and rollout authority, not a second technical
engine. Its existing `.1`–`.32` cohort remains the root + 31 certification
surface. `mro-z89e.2` remains the `flext-infra` certification control and tracks
the technical result of `mro-wkii.17`.

The existing 32 controls are preserved; another project-control cohort is not
created:

| Control | Governed project |
| --- | --- |
| `mro-z89e.1` | FLEXT root |
| `mro-z89e.2` | `flext-infra` |
| `mro-z89e.3` | `flext-api` |
| `mro-z89e.4` | `flext-auth` |
| `mro-z89e.5` | `flext-cli` |
| `mro-z89e.6` | `flext-core` |
| `mro-z89e.7` | `flext-db-oracle` |
| `mro-z89e.8` | `flext-dbt-ldap` |
| `mro-z89e.9` | `flext-dbt-ldif` |
| `mro-z89e.10` | `flext-dbt-oracle` |
| `mro-z89e.11` | `flext-dbt-oracle-wms` |
| `mro-z89e.12` | `flext-grpc` |
| `mro-z89e.13` | `flext-ldap` |
| `mro-z89e.14` | `flext-ldif` |
| `mro-z89e.15` | `flext-meltano` |
| `mro-z89e.16` | `flext-observability` |
| `mro-z89e.17` | `flext-oracle-oic` |
| `mro-z89e.18` | `flext-oracle-wms` |
| `mro-z89e.19` | `flext-plugin` |
| `mro-z89e.20` | `flext-quality` |
| `mro-z89e.21` | `flext-tap-ldap` |
| `mro-z89e.22` | `flext-tap-ldif` |
| `mro-z89e.23` | `flext-tap-oracle` |
| `mro-z89e.24` | `flext-tap-oracle-oic` |
| `mro-z89e.25` | `flext-tap-oracle-wms` |
| `mro-z89e.26` | `flext-target-ldap` |
| `mro-z89e.27` | `flext-target-ldif` |
| `mro-z89e.28` | `flext-target-oracle` |
| `mro-z89e.29` | `flext-target-oracle-oic` |
| `mro-z89e.30` | `flext-target-oracle-wms` |
| `mro-z89e.31` | `flext-tests` |
| `mro-z89e.32` | `flext-web` |

Each control is an inventory and certification owner. It records project
identity, namespace, remote, path, `0.12.0-dev` branch, repository role, Beads
ledger owner, overlay justification, immutable exclusions, generated surface
state, provider prerequisites, bounded defect children, first and second apply,
Make gates, real-consumer QA, and Git/PR/Dolt evidence. The control does not
become a mega implementation lane.

### 6.4 Readiness and release boundary

`mro-p68a` remains the stabilization/readiness program. It aggregates provider,
integration, compatibility, and operational evidence without owning publication
or consumer-side mutations. `mro-p68a.42` is reused as the bounded
rollout-readiness and callback aggregator when its live contract still matches;
`mro-p68a.38.1` remains the read-only compatibility registry and
`mro-p68a.38.2` remains provider compatibility documentation.

`mro-e9j0` remains the release-boundary epic. Its existing technical children
retain version/tag SSOT, trusted workflow, multi-platform CI, runtime-cycle
removal, public bootstrap, and branch/worktree/gitlink convergence ownership.
This plan may reconcile their descriptions and dependencies, but it may not
publish an RC, create a tag, change a production release, or promote anything.
Those actions require a later explicit operator authorization.

### 6.5 Existing Bead disposition

| Existing Bead or range | Approved disposition |
| --- | --- |
| `mro-wkii.17` | Retain and normalize as the technical engine epic. |
| `mro-wkii.17.41` | Normalize as the bounded repository-role/conform/tracker technical subepic. |
| `mro-z89e` | Retain as the reused program umbrella and rollout authority. |
| `mro-z89e.1`–`.32` | Retain as the existing root + 31 certification controls. |
| `mro-z89e.2.1` | Move to `mro-whri` when its live intent confirms lazy MRO work. |
| `mro-whri` | Reuse as the strict architecture, code-generation, lazy-export, and MRO owner after overlap reconciliation. |
| `mro-1o6t` | Retain as documentation/governance; use matching governance leaves for P0 without mutating parallel feature-documentation WIP. |
| `mro-1o6t.1` and matching live children | Reuse for P0 where intent matches; split FLEXT and AI Hub implementation by repository. |
| `mro-p68a` and `mro-p68a.42` | Retain for readiness and callback aggregation. |
| `mro-e9j0` and `mro-e9j0.6` | Retain as release and convergence boundaries; do not execute publication or promotion. |
| `mro-bqt3`, `mro-whri`, `mro-xpdh` | Retain as distinct CI/validation, architecture, and test-architecture programs. |

After live content absorption, the intended consolidation candidates are:

| Origin | Canonical survivor or result |
| --- | --- |
| `mro-wkii.17.39`, `mro-5qfa` | Repository-role classifier under `mro-wkii.17.41` |
| `mro-y2c6` | `mro-jk1p` |
| `mro-ydhf.33` | `mro-z89e.32` |
| `mro-qr7g` | Provider owner `mro-fi91`, with rollout proof in `.1`–`.32` |
| `mro-p68a.34`, `mro-qb4y.8.4` | Generated-surfaces/provider-cutover slices under `mro-wkii.17.41` |
| `mro-wkii.17.33` | Split uniquely between `mro-e9j0.6` and `mro-bqt3` |

After destination-ledger verification, the intended reassociations are:

| Bead | Canonical destination |
| --- | --- |
| `mro-z89e.2.1` | `mro-whri`, when its live intent confirms strict lazy MRO/facade work |
| `mro-ydhf.1.1` | `mro-wkii.17.37`, when its live intent confirms test-runtime/performance ownership |
| `mro-re80.7` | AI Hub tracker execution, retaining a FLEXT callback for the provider contract |
| `mro-eznu` | Cosmos Main tracker, retaining only the FLEXT provider defect in FLEXT |
| `ai-hub-6doo.6` | AI Hub ledger; it is never imported into the FLEXT hierarchy |

A cross-tracker reassociation preserves content and notes when supported,
removes invalid local dependency rows, recreates only valid destination-ledger
relationships, and closes the source with an exact moved-to callback. It does
not move consumer implementation into FLEXT or provider implementation into a
consumer.

The former `0.20` routes `mro-377y`, `mro-jnm1`, and `mro-sltx` are historical
evidence only. Still-valid acceptance is absorbed into the `0.12.0-dev` owner,
then the duplicate implementation route is retired. No source work, branch
promotion, or validation runs on `0.20.0-dev`.

`mro-pd8f` is not superseded wholesale: gitlink/baseline scope belongs with the
convergence cohort, `.1`/`.2` setup scope belongs with the engine, and the
parent drains only after every unique child has an owner.

Historical candidate IDs are not removal authority by themselves. Before
superseding an issue, the orchestrator reads its live title, description,
status, parent, dependencies, comments, assignee, and evidence. Two issues are
duplicates only when they have the same canonical owner, outcome, affected
consumers, and acceptance boundary. A duplicate is linked to the survivor,
annotated with the consolidation reason and evidence preserved, then superseded
through `bd`; it is never physically deleted.

### 6.6 External callbacks

Known consumer-side callbacks are revalidated and reused:

| Consumer | Known callback Bead |
| --- | --- |
| AI Hub | `ai-hub-raur.7.3` |
| Cosmos Main | `cosmos-main-rysa.2` |
| Cosmos Docgen | `bd-bky5.5` |
| MCB | `mcb-o96i.9.1` |

FLEXT provides the exact `0.12.0-dev` provider commit or an already-authorized
immutable artifact identity, compatibility notes, and the canonical consumer
validation contract. The consumer returns its Bead, commit, command, working
directory, exit status, decisive output, validated identity, and any discovered
provider defect. Cross-tracker coordination uses notes and callbacks, not
invented local dependency types or direct consumer mutation.

### 6.7 Dependency semantics

The graph uses relationships consistently:

- parent/child means decomposition of the same outcome;
- blocks means the target cannot start or complete before the dependency;
- tracks means an epic or certification control consumes another Bead's
  independently owned result;
- discovered-from records provenance, not sequencing;
- related records useful non-blocking context;
- native supersede records canonical consolidation;
- external callback links connect a FLEXT capability to consumer-owned rollout
  work without transferring ownership of the consumer.

An epic is an aggregate and cannot be claimed as an implementation lane. Ready
work consists of leaf Beads whose blockers are resolved.

## 7. Autonomous Bead contract

Every executable leaf Bead is complete enough for a new worker with no chat
history. It contains these fields:

### Identity and ownership

- stable semantic key and concise outcome title;
- type, priority, parent epic, and relationship provenance;
- owning repository, canonical branch, dedicated worktree, and assignee;
- canonical implementation owner and all affected consumers.

### Reality and scope

- current observed behavior with dated evidence;
- the divergence from the canonical contract;
- exact in-scope paths or generated surfaces;
- explicit exclusions, especially third-party forks and unrelated WIP;
- concurrent writers, shared mutable files, and integration risk.

### Design and cutover

- root cause;
- source-of-truth file, model, schema, config, template, or generator;
- target architecture and dependency direction;
- consumer inventory;
- atomic migration order: create canonical support, migrate all consumers with
  structural search, remove the superseded implementation, regenerate, and
  validate;
- rollback is fix-forward through a new correction, never reintroduction of the
  old path.

### Acceptance and evidence

- observable behavior acceptance;
- exact canonical Make commands and expected scope;
- manual public-surface QA;
- idempotence proof when generation is involved;
- required documentation and ADR updates in the same change;
- commit and push evidence;
- command, working directory, exit status, decisive output, and bounded scope
  for each gate.

### Resume capsule

The last comment or structured note records:

- phase and last completed atomic step;
- live branch/worktree and last pushed commit;
- files changed and files currently dirty;
- last green and red Make commands;
- exact blocker, if one exists;
- next single action and its stop condition;
- dependency changes or decisions made during the session.

The resume capsule is updated before delegation, compaction, interruption, or
handoff. It transfers context; it never replaces evidence or changes the
approved intent.

### 7.1 Mandatory lane inventory and reassociation

Before semantic reorganization or implementation resumes, the orchestrator
builds a live, bounded inventory from canonical Git, Beads, and GitHub state.
Every active or dirty unit must resolve this chain:

```text
Bead <-> feature outcome <-> repository <-> 0.12.0-dev base
     <-> implementation branch <-> worktree <-> owned paths/WIP
     <-> commits <-> remote branch <-> PR and CI, when a PR exists
```

The inventory records:

| Field | Required meaning |
| --- | --- |
| Bead | One executable leaf with live owner, phase, and stop condition |
| Feature | The single behavior or governance outcome represented by the Bead |
| Repository | One owning Git repository; cross-repository work is split into callbacks |
| Base | Current remote `0.12.0-dev` SHA used for the lane |
| Branch | One implementation branch mapped to the Bead, or direct authorized integration work |
| Worktree | One real path containing that branch and no second mutation lane |
| Owned paths | Exact files/generated surfaces the lane may change |
| Preserved WIP | Dirty and untracked paths, provenance, overlap, and integration treatment |
| Commits | Ordered local SHAs and their explicit path scope |
| Remote | Last confirmed pushed SHA and ahead/behind relation |
| PR/CI | PR identity, review state, checks, and merge relation when applicable |
| Next action | One canonical command or mutation with an observable result |

Reassociation is mandatory when any part is missing or contradictory. The
orchestrator does not infer ownership from a branch name alone and does not
create a new lane merely because old WIP exists. It re-reads the feature,
preserves every hunk, associates it with the matching live Bead, and either
continues that lane or creates one bounded discovered-from leaf. Duplicate
branches/worktrees are drained through fix-forward integration, not deletion or
history rewriting.

An `in_progress` Bead without one live feature, branch/worktree, owner, and next
action is normalized before new implementation starts. A branch or worktree
with relevant WIP and no Bead is associated with the canonical survivor before
the WIP is touched. A PR and its commits remain evidence of the same feature;
they never become a competing tracker.

`mro-e9j0.6` is the canonical live registry for this branch/worktree/PR/WIP
convergence. It records the complete association matrix and drains duplicate or
detached lanes without taking semantic ownership away from the feature Bead.
`mro-re80` remains the reusable worktree-lifecycle capability owner. Candidate
duplicates such as `mro-p68a.37` and `mro-l078` are superseded only after their
unique content and evidence have been copied into `mro-e9j0.6` or the matching
feature Bead.

### 7.2 Parallel documentation feature exclusion

The already active parallel documentation feature is deliberately outside the
reassociation and source-mutation boundary of this slice. Its Beads, branch,
worktree, PR, commits, and dirty paths are inventoried as preserved concurrent
state but are not re-parented, superseded, claimed, rewritten, or folded into a
new implementation lane here.

This exclusion does not remove these items from the approved program:

- this durable handoff document;
- P0 governance authority;
- FLEXT governance skills;
- the canonical `AGENTS.md` profiles;
- AI Hub propagation of governance;
- documentation standards and later intake/rollout work after the parallel
  feature lands or provides an explicit callback.

The documenter may audit landed behavior continuously, but it does not perform
semantic Beads mutation and it does not edit files owned by an active technical
lane.

### 7.3 Lane roles and serialization

| Lane role | Ownership |
| --- | --- |
| Tracker orchestrator | Singular owner of graph mutation, reassociation, deduplication, evidence review, and closure |
| AI Hub governance/tooling callback | Universal distribution and managed-tool provisioning in the AI Hub repository |
| FLEXT governance lane | Versioned FLEXT overlay, routing skills, and root/member governance contracts |
| Technical engine lane | One bounded `mro-wkii.17` or `.17.41` implementation leaf |
| Certification lane | One `mro-z89e.1`–`.32` project control and its bounded defect child |
| Documenter | Standing read/audit lane aligned with landed behavior; no semantic tracker mutation |
| Governance/CI helper | Read-only or disjoint generated-CI analysis; no closure authority |

Only one project mutation slice is executed at a time. Read-only dependency,
AST, CRG, MCP, governance, and documentation audits may assist concurrently,
but two workers do not edit the same repository, feature, generated owner, or
phase. The next project starts only after the current project is green,
committed, pushed, and evidenced.

## 8. Generic setup and conform control plane

`make setup` is repaired at the FLEXT Infra owner as a generic capability, not a
workspace-specific patch. It must:

- detect root workspace, first-party member, standalone clone, external
  consumer, and excluded fork from canonical config and repository reality;
- provision Python, mise tools, direnv, virtual environments, Beads, and managed
  root surfaces without product-specific shell branches;
- derive project identity and Beads namespace from typed topology;
- permit only bounded config overlays for truly independent projects or legacy
  namespace mapping;
- avoid scanning, linting, generating, or mutating excluded fork repositories;
- generate workspace and standalone CI from one FLEXT Infra conform owner;
- preserve explicit project overlays without duplicating common CI behavior;
- operate idempotently and explain its selected topology through a canonical
  Make diagnostic;
- work from external workspaces without assuming a hardcoded FLEXT filesystem
  path.

The root Make dispatcher is the only execution surface for setup, conform,
generation, docs, checks, and tests. Missing diagnostics are added as Make
verbs or `WHAT=` modes at the canonical owner and covered before being used as
evidence.

## 9. Strict generated Python surfaces

Generated Python package roots use one canonical strict pattern:

- `__init__.py` is simple, uniform, and generated;
- public exports are derived automatically from the canonical API/export model;
- imports are lazy and preserve the required MRO/OO facade composition;
- a package's `base.py` imports the short facade aliases from its upstream owner
  and re-exports the package surface;
- the root package exports from `base.py` lazily;
- a short canonical alias such as `s` remains `s`; aliases such as `core_s` are
  prohibited;
- alternative, custom, eager, compatibility, and bypass import routes are
  migrated and removed;
- higher-to-lower facade imports follow the canonical layer order, while reverse
  type relationships remain type-checking-only;
- all consumers are found and migrated with AST-based structural search;
- the generated result is validated for import behavior, public API, MRO,
  performance-relevant laziness, and idempotence.

The generator, not each generated module, owns this change. Generated files are
never hand-edited.

## 10. Documentation intake and publication

### 10.1 Scratch intake

The Markdown source collection is moved out of `~/Downloads` into a unique
scratch directory outside every Git worktree. The misspelled `~/Donwloads` is
not treated as an alternate authority. The move is performed through a
canonical Make docs-intake mode so it is reproducible, bounded, and recorded.

The planning inventory observed 73 Markdown files: 32 apparently FLEXT-related,
13 associated with nonmember external or fork projects, and 28 research or
reference files. These counts are a discovery snapshot. The canonical intake
verb re-inventories the live source before moving it and records provenance in
the owning Bead without turning scratch metadata into project authority.

Scratch characteristics:

- absolute location outside the workspace and every subproject;
- a unique program/date segment;
- source name, intake classification, and disposition metadata;
- no automatic publication;
- no mutation of external/fork repositories;
- retention until every file has a recorded disposition.

### 10.2 One source file at a time

Each intake file is evaluated independently:

1. identify its claims and intended project;
2. verify useful claims against current code, config, ADRs, and public behavior;
3. reject stale, duplicated, noncanonical, or unsupported claims;
4. assign accepted knowledge to its canonical owner;
5. update the relevant README, ADR, standard, skill reference, API documentation,
   Python docstring, example, or publication page in the same project slice;
6. run the complete project documentation pipeline;
7. record disposition and evidence in the Bead;
8. commit and push that project before advancing.

A scratch document is evidence, never an owner. Content is not copied wholesale,
and one file is not used to justify a fleet-wide claim.

### 10.3 Documentation standard

The documentation program establishes:

- answer-first READMEs with supported setup and real public examples;
- ADRs for durable decisions, with supersession links and no duplicate decision
  owner;
- compact routing skills that link to canonical references;
- strict English docstrings for public behavior and non-obvious invariants;
- executable Markdown and docstring snippets that consume config/settings SSOT;
- a project-wide terminology, heading, link, code-fence, and provenance style;
- one publication layout conforming to FLEXT and WAZA requirements;
- docs generated only from canonical code/config/schema owners;
- removal or supersession of stale documentation in the same slice.

`make docs` always runs the complete documentation pipeline for the selected
project. It builds, checks links, validates snippets and docstrings, validates
ADRs and skills, runs WAZA, checks publication shape, and detects generated
drift. Narrow `WHAT=` diagnostics may exist for iteration, but they never replace
the final unqualified `make docs`.

## 11. Execution waves

### Wave P0 — governance authority and propagation

1. Record the program key on the existing participating epics and create or
   reuse two repository-specific P0 leaves: FLEXT governance and AI Hub
   propagation.
2. Resolve current global, FLEXT, and local governance owners and consumers.
3. Consolidate FLEXT governance skills over global skills.
4. Implement the three canonical `AGENTS.md` profiles.
5. Implement AI Hub typed inventory, templates, generation, and conform.
6. Propagate, prove idempotence, run complete docs and quality gates, commit, and
   push each repository.

### Wave P1 — Beads runtime, lane reality, and schema health

1. Make setup select and verify the latest official schema-compatible `bd`.
2. Normalize namespace and provisioning behavior for workspace and standalone
   projects.
3. Inventory every Bead, feature, branch, worktree, PR, commit, remote SHA, and
   dirty path participating in the program.
4. Reassociate every active unit into a one-Bead/one-feature/one-repository
   lane, preserving the parallel documentation feature exclusion.
5. Re-audit claims, issue types, parents, dependencies, callbacks, schema, Dolt
   health, ready work, and blocked work with the live runtime.

### Wave P2 — semantic graph convergence

1. Normalize `mro-wkii.17` as the technical engine and `.17.41` as its bounded
   topology/conform/tracker subepic.
2. Preserve `mro-z89e` as the program umbrella and preserve all 32 existing
   certification controls.
3. Preserve `mro-p68a` readiness and `mro-e9j0` release-boundary ownership.
4. Add only verified tracks/blocks/related/callback relationships.
5. Move or supersede candidates only after complete content absorption.
6. Enrich every executable leaf with the autonomous contract and resume capsule.
7. Run tracker hygiene and Dolt push after each semantic batch.

### Wave P3 — technical engine

1. Complete `mro-wkii.17.35` typed topology and capability classification.
2. Implement the restrictive repository-role classifier under `.17.41`.
3. Implement Beads/mise/direnv projection after P1 runtime health.
4. Repair `make setup`, conform, dispatcher, generated Make surfaces, CI, and
   managed documentation at their existing owners.
5. Validate the workspace/member/standalone/external/fork matrix.
6. Perform provider cutover, remove legacy routes, and prove the fixed point.
7. Implement strict generator support for simple roots, lazy exports, short
   aliases, and MRO facades under `mro-whri`, then migrate every consumer with
   AST and dependency-graph evidence.

### Wave P4 — root and foundation certification

Execute and close one control at a time:

1. `mro-z89e.2` — `flext-infra`;
2. `mro-z89e.1` — FLEXT root;
3. `mro-z89e.6` — `flext-core`;
4. `mro-z89e.5` — `flext-cli`;
5. `mro-z89e.31` — `flext-tests`, including its installed pytest-plugin public
   boundary.

### Wave P5 — platform, domain, and connector certification

Continue one project at a time in this dependency-aware order:

1. platform: `.3`, `.4`, `.12`, `.15`, `.16`, `.19`, `.20`, `.32`;
2. domain: `.7`, `.13`, `.14`, `.17`, `.18`;
3. dbt connectors: `.8`–`.11`;
4. taps: `.21`–`.25`;
5. targets: `.26`–`.30`.

For every control: pull `0.12.0-dev` fast-forward, absorb live WIP, apply the
generated contract plus legitimate overlay, fix all Ruff and Pyrefly findings at
root cause, run changed-scope types and tests, commit explicit paths, push the
project, update/push its superproject gitlink when applicable, and record exact
evidence before advancing.

### Wave P6 — documentation convergence

1. Move the source collection into external scratch through Make.
2. Process each file independently.
3. Improve canonical README, ADR, standard, skill, docstring, example, and WAZA
   surfaces where evidence supports the change.
4. Run full `make docs` and project quality gates after every project slice.
5. Retain a complete disposition for all intake files.
6. Reconcile with the parallel documentation feature only after its explicit
   callback or landing; preserve its ownership until then.

### Wave P7 — integrated readiness and external callbacks

1. Link consumer-owned Beads rather than treating external projects as FLEXT
   subprojects.
2. Prove the integrated root + 31 first/second-apply fixed point.
3. Aggregate provider and compatibility evidence in `mro-p68a`.
4. Supply an `0.12.0-dev` provider commit or an already-authorized immutable
   artifact to consumer callbacks; do not publish a new artifact under this
   plan.
5. Validate external workspace use without a hardcoded local path.
6. Record compatibility evidence in both the FLEXT capability Bead and the
   consumer callback.

### Wave P8 — closure and release-boundary handoff

1. Repeat global workspace gates after the final edit.
2. Prove generation and conform idempotence.
3. Run Beads lint, stale, orphan, dependency, and ready-work audits.
4. Verify all required commits are present remotely and the active branch is not
   ahead.
5. Confirm no program-created unowned dirty state remains.
6. Close leaves before their owning technical, certification, documentation, or
   readiness epic.
7. Hand the integrated SHA and readiness record to `mro-e9j0` as a gated input.
   Leave publication, tagging, RC delivery, and promotion unexecuted until a new
   explicit operator authorization.

## 12. Canonical validation matrix

Direct invocations of Ruff, Pyrefly, Pyright, Mypy, Pytest, MkDocs, WAZA, uv,
code generators, or conform internals are not accepted as evidence.

| Purpose | Canonical root command |
| --- | --- |
| Environment and managed tooling | `make setup` |
| Conform and generated root surfaces | `make conform` |
| Python/code generation | `make build WHAT=gen` |
| Complete project documentation and WAZA | `make docs` |
| Global Ruff, format, and Pyrefly | `make check CHECK_GATES=lint,format,pyrefly` |
| Changed-project Pyright and Mypy | `make check PROJECT=<project> CHECK_GATES=pyright,mypy` |
| Changed-project tests | `make test PROJECT=<project>` |
| Integrated workspace behavior | `make val WHAT=workspace` |

If a listed command is absent or does not provide the required generic behavior,
the first executable slice repairs it at FLEXT Infra and validates that repair.
No alternate command is substituted.

Validation is performed after the final edit of each slice. A subsequent edit
invalidates earlier evidence. Required evidence includes command, active
worktree, exit code, decisive output, and exact project scope.

## 13. Git and multi-repository delivery

- Pull `origin/0.12.0-dev` with fast-forward semantics before each repository
  slice and again before integration.
- Integrate all live changes fix-forward. Never report another session's work as
  a reason for failure.
- Commit only explicit paths owned by the Bead.
- Push every commit immediately; a local-only commit is not a completed slice.
- When a first-party subproject and the superproject gitlink both change, the
  subproject is validated, committed, and pushed first. The superproject then
  receives the validated gitlink in its own explicit commit.
- No branch promotion through `main` or `0.20.0-dev` belongs to this program.
- No third-party fork commit or gitlink content is mutated by FLEXT automation.
- Beads Dolt sync and Git source sync are separate protocols; both must be
  current at handoff.

## 14. Required tool-assisted analysis

Structural refactors use complementary evidence:

- AST-based structural search locates Python consumers and verifies removal of
  obsolete import/export forms;
- code-review graph analysis identifies dependency impact and cross-repository
  consumers;
- MCP-backed repository and source inspection supplies bounded canonical context;
- ordinary text search is used for documentation and config inventory;
- every resulting claim is confirmed through a canonical Make verb before it is
  accepted as validation evidence.

Tools accelerate discovery; they do not become alternate mutation, generation,
or validation surfaces.

## 15. Session resume protocol

A new orchestrator session resumes in this order:

1. read the newest operator instruction, universal law, FLEXT law, root
   `AGENTS.md`, this document, and the four participating epic authorities;
2. synchronize Beads with the newest configured schema-compatible `bd`;
3. inspect P0 plus `mro-wkii.17`, `mro-z89e`, `mro-p68a`, `mro-e9j0`, their
   dependencies, ready leaves, assignees, and resume capsules;
4. inspect the active `0.12.0-dev` worktree, subproject state, remote relation,
   and concurrent writers;
5. fast-forward pull without discarding shared work;
6. claim one ready leaf atomically;
7. execute only that leaf to its observable green boundary;
8. validate through Make, perform real public-surface QA, update docs and Bead
   evidence, commit explicit paths, and push;
9. update the resume capsule and hand off or close the leaf only when its full
   acceptance holds;
10. select the next ready leaf from Beads.

Status reporting does not pause execution. A session stops early only for one
precise destructive or authority decision that cannot be resolved from canonical
sources; the exact blocker and question are recorded in the active Bead.

## 16. Definition of done

This program is done only when the live system, not the plan, demonstrates all
of the following:

- universal, FLEXT, and scope governance resolve through one deterministic
  layered contract;
- AI Hub canonically propagates every managed governance surface;
- FLEXT governance skills contain no duplicated global implementation;
- `AGENTS.md` works in workspace, standalone, and external profiles;
- the latest configured official `bd` works with the live schema through the
  managed environment;
- the Beads graph is normalized, dependency-correct, hygienic, and independently
  resumable;
- program umbrella, technical engine, root + 31 certification cohort,
  documentation, readiness, and release-boundary ownership remain
  non-competing and dependency-correct;
- every active lane has an evidenced
  Bead/feature/repository/branch/worktree/WIP/commit/remote/PR mapping;
- `make setup`, conform, code generation, docs, checks, tests, and workspace
  validation work generically;
- strict simple package roots, lazy exports, short aliases, and MRO facades are
  generated and all consumers are migrated;
- every documentation source has an evidenced disposition;
- READMEs, ADRs, standards, skills, docstrings, examples, and WAZA publication
  surfaces agree with runtime reality;
- all first-party projects are green and pushed on `0.12.0-dev`;
- external consumers have validated callback evidence;
- excluded third-party forks remain unmodified;
- generated output is idempotent;
- the workspace has no program-created broken or unowned WIP;
- all final evidence is in Beads;
- the engine, certification, documentation, and readiness authorities close
  only after their own children, while `mro-e9j0` remains at the explicitly
  unauthorized release boundary until the operator separately authorizes
  publication or promotion.
