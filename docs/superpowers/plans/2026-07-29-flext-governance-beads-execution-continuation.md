> **HISTORICAL / SUPERSEDED** — retained for provenance only; live Beads is authoritative.

# FLEXT 0.12.0-dev Governance and Beads Execution Continuation

| Field | Current value |
| --- | --- |
| Status | Paused only for an operator-requested session transfer |
| Date | 2026-07-29 |
| Program | `flext-012-conform-beads-docs` |
| Program epic | `mro-z89e` |
| Active P0 epic | `mro-1o6t.1` |
| Active FLEXT leaf | `mro-1o6t.1.1` |
| Lane registry | `mro-e9j0.6` |
| Integration branch | `0.12.0-dev` |
| Active FLEXT worktree | `/home/marlonsc/flext/.worktrees/flext-0.12.0-dev` |
| AI Hub callback | `ai-hub-t449.10`, blocked by active `ai-hub-t449.2.4` |
| Durable program plan | `docs/superpowers/plans/2026-07-29-flext-beads-governance-reorganization-handoff.md` |
| This handoff | `docs/superpowers/plans/2026-07-29-flext-governance-beads-execution-continuation.md` |

This file is the authoritative session-transfer checkpoint for the execution
state described below. It does not replace Beads or the durable program plan.
The next session must verify mutable state before acting, update the active Bead
after every state-changing slice, and continue from the first unfinished action
rather than restarting the audit.

## 1. Exact operator outcome

The approved program must:

1. establish a deterministic governance composition:
   operator instruction -> global generic law -> branch-matched FLEXT law ->
   scope-only delta -> active Bead;
2. keep FLEXT as the sole semantic owner of FLEXT domain behavior and have AI
   Hub distribute, configure, and validate it without competing with it;
3. repair generic FLEXT Infra setup, conform, codegen, Make, CI, Beads, WAZA,
   documentation, strict lazy exports, and MRO/facade generation at their
   canonical owners;
4. propagate the same generated contract to the FLEXT workspace, all 31
   first-party members, standalone clones, and declared external consumers;
5. inventory and durably associate every relevant Bead, feature, repository,
   branch, worktree, WIP, commit, remote branch, PR, and CI state;
6. preserve and absorb all useful dirty, staged, committed, detached, remote,
   and concurrent work fix-forward;
7. use only `0.12.0-dev` as the FLEXT integration line and make it the ancestry
   base of every retained FLEXT branch, excluding GitHub technical refs and
   Dolt refs;
8. process future Markdown evidence from external scratch one file at a time,
   improve canonical README/ADR/skills/docs/docstrings, and validate complete
   documentation through `make docs`;
9. deliver small green explicit-path commits and fast-forward push each commit;
10. leave third-party forks, content-only repositories, and the parallel
    feature-documentation content lane unmodified.

The immediate P0 slice is governance, not the documentation-content rewrite.
The user explicitly approved execution and later requested this durable
handoff before continuing in another session.

## 2. Non-negotiable authority and tool rules

Read these exact authorities before mutation:

1. newest operator instruction;
2. `/home/marlonsc/.codex/RTK.md`;
3. `~/.agents/UNIVERSAL_CORE.md`;
4. `~/.agents/skills/inviolable-rules/SKILL.md`;
5. `~/.agents/skills/make-check/SKILL.md`;
6. active worktree `AGENTS.md`;
7. active worktree `.agents/skills/flext-context-routing/SKILL.md`;
8. active worktree `.agents/skills/flext-law/SKILL.md`;
9. `~/.agents/skills/verification-loop/SKILL.md`;
10. `mro-z89e`, `mro-1o6t.1`, `mro-1o6t.1.1`, `mro-e9j0.6`, the durable
    program plan, and this handoff.

Binding execution rules:

- prefix every shell command with `rtk`;
- use Code Review Graph only through the CLI:
  `/home/marlonsc/.ai-hub/.venv/bin/code-review-graph`;
- never use the Code Review Graph MCP tools;
- use `ast-grep` structurally for repeated syntax and cutover proof;
- use other MCP sources when useful, but never treat them as validation;
- run setup, conform, generation, docs, build, lint, format, typing, tests, and
  validation only through the active root Make dispatcher;
- never invoke Ruff, Pyrefly, Pyright, Mypy, Pytest, WAZA, uv, MkDocs, or
  generators directly;
- if a required Make verb is missing or broken, fix it generically in
  `flext-infra`; do not route around it;
- use the schema-compatible upstream Beads binary at:

  ```text
  /home/marlonsc/.local/share/mise/installs/go-github-com-steveyegge-beads-cmd-bd/423afdcb2813/bin/bd
  ```

- never use stable `bd` 1.1.2 for this schema, downgrade the schema, or use
  `--ignore-schema-skew`;
- use `BEADS_FSCK_TIMEOUT=240s` for Dolt push because the default 30-second
  integrity check is too short for this store;
- never reset, restore, clean, stash, rebase published work, force-push, amend,
  or discard unknown work;
- never hand-edit generated projections;
- never replace a GitHub PR body while adding the canonical association block;
  add a top-level comment that preserves the original body and discussion;
- use explicit-path staging and inspect `git diff --cached --stat` before every
  commit.

## 3. Canonical governance decision

The final P0 ownership decision is:

| Layer | Sole owner | Content |
| --- | --- | --- |
| Global | `~/.agents` | Universal Core plus `inviolable-rules`, `make-check`, and `verification-loop` |
| FLEXT | FLEXT branch-matched root | root `AGENTS.md`, `flext-context-routing`, and the local `flext-law` domain delta |
| Scope | nearest member or standalone project | only domain-specific facts, public surfaces, exclusions, and extra acceptance |
| Execution | active Bead | current intent, owner, dependencies, branch/worktree/PR/WIP, evidence, next action, and stop condition |

There is no global semantic owner for `flext-law`. FLEXT owns exactly:

```text
.agents/skills/flext-law/SKILL.md
```

AI Hub may project that skill after provider discovery, but it may not author a
second global copy. The duplicated local
`.agents/skills/flext-inviolable-rules/SKILL.md` is removed. The router uses
exact global generic paths plus the exact local branch-matched FLEXT law path.
No `flext-workspace-law` rename or compatibility adapter is created.

## 4. Active FLEXT tree and preserved WIP

At the last audit:

```text
worktree: /home/marlonsc/flext/.worktrees/flext-0.12.0-dev
branch:   0.12.0-dev
remote:   origin/0.12.0-dev
relation: 0 ahead / 0 behind before any new source commit
base SHA: f00b2eadf08169f13bf65c4d58d9ca0bd4d2a63b
```

### 4.1 P0-owned source changes

The P0 worker changed only these six governance paths:

| Path | State | Intended result |
| --- | --- | --- |
| `AGENTS.md` | modified | compact global -> FLEXT -> scope -> Bead composition |
| `.agents/commands/flext-law.md` | modified | exact-path authority loading |
| `.agents/provider.toml` | modified | remove local `flext-inviolable-rules` surface |
| `.agents/skills/flext-context-routing/SKILL.md` | modified | exact global generic plus local law routing |
| `.agents/skills/flext-law/SKILL.md` | modified | concise FLEXT-only architecture/import/Make/fleet delta |
| `.agents/skills/flext-inviolable-rules/SKILL.md` | deleted | remove duplicated global execution law |

Current source diff for these six paths:

```text
6 files changed, 102 insertions, 352 deletions
```

The following plan is also new and modified in the active worktree:

```text
docs/superpowers/plans/2026-07-29-flext-beads-governance-reorganization-handoff.md
```

It contained 1,031 lines at the first consolidated review; re-read the live
file because subsequent authority corrections added content. It merges:

- the earlier governance/Beads/documentation plan;
- `/home/marlonsc/flext/FLEXT_0_12_BEADS_LANE_REORGANIZATION_PLAN.md`;
- the approved P0 governance model;
- the root + 31 controls;
- the autonomous Bead contract;
- Bead/feature/branch/worktree/PR/commit/WIP association;
- external callbacks;
- documentation scratch intake;
- Make-only validation;
- the parallel documentation-feature exclusion.

The plan was corrected after generation to state that:

- `mro-z89e` is the reused program umbrella and rollout authority;
- `mro-z89e.1` through `.32` are the certification cohort;
- FLEXT owns the local `flext-law`;
- no global duplicate `flext-law` is retained;
- `mro-e9j0.6` is the canonical live lane registry.

### 4.2 Unrelated root WIP that must remain untouched

These paths were dirty before or independently of the P0 worker:

```text
.gitignore
.gitmodules
Makefile
pyproject.toml
ci/
all 31 FLEXT member gitlinks
```

Do not include them in the P0 governance commit unless a live Bead and exact
owner prove they belong to the same completed slice.

### 4.3 Direct consumers still requiring classification

The last text inventory found active references to the removed local skill in:

```text
.agents/prompts/continuation-monopoly.md
.github/prompts/flext-aggressive-scale-refactor.prompt.md
.github/prompts/flext-strict-jsonvalue-session-continuation.prompt.md
docs/GOVERNANCE.md
docs/standards/development.md
docs/standards/testing.md
docs/ways-of-working/worker-lane-contract.md
```

Likely disposition:

- the `.agents/prompts` and `.github/prompts` references are direct instruction
  consumers and should be cut over in `mro-1o6t.1.1` after re-reading live
  ownership;
- the four `docs/**` references overlap the reserved parallel documentation
  lane and must not be edited in this session without its explicit callback;
- record the reserved documentation consumers in the Bead rather than leaving
  their ambiguity undocumented;
- the durable program plan reference was already corrected.

## 5. Parallel documentation-feature exclusion

Do not mutate or semantically reorganize documentation content in:

```text
/home/marlonsc/flext                       feature/mro-ydhf-docs-local
/home/marlonsc/flext/.worktrees/pr40-docs
/home/marlonsc/flext/.worktrees/mro-p68a-12-2-docs
mro-ydhf.1
mro-ydhf.1.1
flext-infra PR 64
docs/** WIP owned by those lanes
```

The durable plan, this handoff, P0 governance, FLEXT skills, the canonical
`AGENTS.md` model, AI Hub propagation, and the generic `make docs` engine remain
in scope. Only feature-documentation content is reserved.

## 6. Beads state and completed semantic mutations

### 6.1 Canonical hierarchy

```text
mro-z89e  FLEXT 0.12.0-dev program umbrella
├── mro-z89e.2  FLEXT Infra engine/conform/Beads/CI
├── mro-z89e.1-.32  root + 31 certification controls
└── mro-1o6t  living documentation, intake, WAZA, publication
    └── mro-1o6t.1  P0 governance and distribution
        ├── mro-1o6t.1.1  FLEXT root AGENTS/provider/router/local law
        ├── mro-1o6t.1.2  generated member/standalone AGENTS profiles
        └── mro-1o6t.1.3  strict declared-artifact/WAZA validation

mro-wkii.17  typed technical engine tracked by the program
mro-p68a     stabilization and readiness
mro-e9j0     release boundary
└── mro-e9j0.6  canonical branch/worktree/PR/WIP registry
```

The P0 sequence is:

```text
mro-1o6t.1.1 -> ai-hub-t449.10 -> mro-1o6t.1.2 -> mro-1o6t.1.3
```

### 6.2 Consolidations already applied

These semantic consolidations were completed:

```text
mro-vx2y      superseded by mro-1o6t.1
mro-4o9a.5    superseded by mro-1o6t.1.3
mro-ww3x      superseded by mro-1o6t.1.3
mro-l078      superseded by mro-e9j0.6 after unique content absorption
mro-p68a.37   superseded by mro-e9j0.6 after unique content absorption
```

`mro-wrbd` was not superseded because it has unique Cosmos/AI Hub cross-project
scope. It now tracks `mro-e9j0.6` for its FLEXT portion. `mro-z89e` also tracks
`mro-e9j0.6`.

### 6.3 P0 Beads already rewritten

The following were rewritten into autonomous contracts:

- `mro-z89e`;
- `mro-1o6t`;
- `mro-1o6t.1`;
- `mro-1o6t.1.1`;
- `mro-1o6t.1.2`;
- `mro-1o6t.1.3`.

`mro-1o6t.1.1` now explicitly retains the local `flext-law` in place and
removes only the local duplicate `flext-inviolable-rules`. Its metadata links
the active integration worktree, the historical PR 39 worktree, PRs
28/29/35/39/47/49, exact owned paths, preserved root WIP, and CLI-only CRG.

### 6.4 Lane registry batch already pushed to Dolt

`mro-e9j0.6` was retitled:

> Register and converge every live FLEXT branch, worktree, PR, and WIP onto
> 0.12.0-dev

Its current notes include:

- 24 root worktrees;
- 27 local branches;
- 11 useful remote refs;
- 49 superproject PRs;
- 18 open FLEXT-organization PRs;
- canonical mappings for P0, engine, baseline/gitlinks, setup, provider,
  package/plugin, external provenance, release history, and detached snapshots;
- explicit documentation exclusion;
- exact open-PR mappings;
- the supersession reasoning for `mro-l078` and `mro-p68a.37`.

That semantic batch was pushed successfully using:

```text
cwd: /home/marlonsc/flext/.worktrees/flext-0.12.0-dev
command: rtk env BEADS_FSCK_TIMEOUT=240s PATH=<schema-compatible-bd-path>:... bd dolt push --json
exit: 0
decisive output: Push complete.
```

The default 30-second push attempt exited 1 before publication because its
pre-push `fsck` timed out. The retry did not ignore integrity; it gave the same
integrity check enough time.

### 6.5 Root feature association batch already pushed to Dolt

These Beads received real branch/worktree/SHA/PR/WIP mappings and were then
pushed to Dolt:

```text
mro-1o6t.1.1
mro-z89e.2
mro-pd8f
mro-pd8f.3
mro-shxw
mro-9fdx
mro-gvjs
mro-jk1p
mro-sw2l.1
mro-0tvv.1
mro-p68a
```

Important mappings include:

- `mro-z89e.2` ->
  `/home/marlonsc/.worktrees/flext-infra-mro-z89e-conform-beads`,
  `feature/mro-z89e-conform-beads`, `e0adbfc4`;
- `mro-pd8f` -> published-baseline lane plus detached snapshots `3705362f`
  and `b42a24a9`;
- `mro-shxw` -> current-base `fix/mro-shxw-superproject` survivor plus old
  nested-WIP source lane;
- `mro-pd8f.3` -> projection-only remainder after governance semantics move to
  `mro-1o6t.1.1`;
- `mro-jk1p` -> package lane, integration evidence lane, and clean provider
  evidence;
- `mro-0tvv.1` -> obsolete wrong-base root PR 48;
- `mro-p68a` -> historical PRs 36/37/38/46 and residual conform-owned WIP.

### 6.6 Final interrupted batch: applied, not yet Dolt-pushed

The operator interrupted the long command to request this handoff. A live
post-interruption audit proved that all 13 intended Bead updates completed
before interruption:

| Bead | Repository / PR | Current mapping |
| --- | --- | --- |
| `mro-wkii.17.37.2` | `flext-infra#67` | lazy CLI lane `d02ae363`, CRG CLI-only |
| `mro-e9j0.6.4` | `flext-infra#47` | remote-only 0.12 -> 0.20 convergence |
| `mro-e9j0.6.3` | `flext-tests#9` | typings-import worktree `894a7773` |
| `mro-e9j0.7` | `flext-infra#69` | v2 dependency-DAG survivor `2fce1800` |
| `mro-wkii.17.41` | `flext-infra#68` | conform topology worktree `b6e05562`, CRG CLI-only |
| `mro-e9j0.6.1` | `flext-core#339` | UCLI worktree plus main/0.20/async WIP worktrees |
| `mro-e9j0.5.1` | `flext-cli#48` | file-iteration worktree `8962a559` |
| `mro-e9j0.4.1` | `flext-tests#6` | pytest shard v2 worktree `be6f5641` |
| `mro-wkii.17.39` | `flext-infra#65` | gitlink identity worktree `86bf73ed`; status corrected to `in_progress` |
| `mro-e9j0.6.5` | API/Auth/gRPC PRs | remote-only heads and full URLs |
| `mro-e9j0.6.7` | `flext-db-oracle#38` | remote-only head `3a76d3fe` |
| `mro-wfc8` | `flext-web#32` | feature owner, remote-only head `36c5ba2b` |
| `mro-e9j0.6.11` | `flext-web#32` | convergence control linked back to `mro-wfc8` |

This final 13-Bead batch has **not** received a subsequent `bd dolt push`.
The next session must push it before performing more Beads mutations.

### 6.7 Bead content still requiring correction

`mro-e9j0.6` was created before the newest operator rule and its description or
acceptance still contains the phrase `CRG/MCP`. Update future execution wording
to:

```text
ast-grep + Code Review Graph CLI + other bounded MCP source inspection
```

Do not delete historical notes that truthfully record old MCP timeouts; append
an explicit superseding route correction.

## 7. GitHub PR association state

No GitHub write occurred in this session. No reciprocal comment was posted and
no PR was closed. The three root PRs remain open.

### 7.1 Root PRs requiring immediate reciprocal comments

| PR | Head | Canonical association | Required action |
| --- | --- | --- | --- |
| `flext#47` | `a74ea78a`, base `main` | evidence for `mro-1o6t.1.1`, exact duplicate of #49 | add canonical comment, then close as duplicate |
| `flext#49` | same branch/SHA, base `0.12.0-dev` | evidence for `mro-1o6t.1.1`; superseded by the short current-base P0 implementation | add canonical comment, then close as superseded/evidence-only |
| `flext#48` | `5bfd2238`, branch built on 0.20 | historical closed `mro-0tvv.1`; 466-file wrong-base PR | add canonical comment, then close without merge |

PRs 47 and 49 have the same remote head and SHA. PR 47 retains 19 unresolved
CodeRabbit threads over 16 paths; closing it must preserve the discussion as
evidence. Neither tree is valid merge input.

Use the GitHub connector to:

1. add a top-level comment with Program, Bead, Epic, base, branch, SHA,
   worktree state, WIP classification, disposition, and next action;
2. close the PR through the connector;
3. never replace the original PR body;
4. record the final PR state in the matching Bead and Dolt-push it.

### 7.2 Other open FLEXT PR mappings

| PR | Bead |
| --- | --- |
| `flext-infra#67` | `mro-wkii.17.37.2` |
| `flext-infra#47` | `mro-e9j0.6.4` |
| `flext-tests#9` | `mro-e9j0.6.3` |
| `flext-infra#69` | `mro-e9j0.7` |
| `flext-infra#68` | `mro-wkii.17.41` |
| `flext-core#339` | `mro-e9j0.6.1` |
| `flext-cli#48` | `mro-e9j0.5.1` |
| `flext-infra#64` | reserved docs `mro-ydhf.1.1`; do not reorganize |
| `flext-grpc#37` | `mro-e9j0.6.5` |
| `flext-db-oracle#38` | `mro-e9j0.6.7` |
| `flext-api#38` | `mro-e9j0.6.5` |
| `flext-auth#36` | `mro-e9j0.6.5` |
| `flext-tests#6` | `mro-e9j0.4.1` |
| `flext-infra#65` | `mro-wkii.17.39` |
| `flext-web#32` | feature `mro-wfc8`; convergence `mro-e9j0.6.11` |

Add reciprocal comments to PRs that currently lack the Bead. Preserve existing
correct associations and bodies. A historical or merged PR is evidence, never
an active lane.

## 8. Root worktree and branch inventory

The root inventory found 24 worktrees:

| Worktree or branch | Owner / disposition |
| --- | --- |
| `.worktrees/flext-0.12.0-dev` | active P0 integration; split GOV from unrelated technical WIP |
| `/home/marlonsc/flext` | reserved docs content; non-doc WIP still needs technical owners |
| `cycle/mro-458l-provider-manifest` | clean historical candidate after P0 absorption proof |
| detached `ac899064` Cosmos snapshot | external consumer callback; never invent FLEXT ownership |
| detached `3705362f` | current-base fleet snapshot -> `mro-pd8f`/`mro-e9j0.6` |
| detached `a0447e18` | conform/CI/provider snapshot -> `mro-z89e.2`/`mro-bqt3` |
| detached `b42a24a9` | competing current-base fleet snapshot -> `mro-pd8f` |
| `fix/mro-shxw-superproject` | current-base `mro-shxw` survivor |
| `bugfix/mro-0tvv-1-backup-disabled` | closed Bead / obsolete PR 48 evidence |
| `bugfix/mro-9fdx-pr-booleans` | `mro-9fdx` |
| `bugfix/mro-gvjs-make-routing-output` | `mro-gvjs`, multi-consumer WIP |
| `bugfix/mro-jk1p-package-plugin` | `mro-jk1p` package lane |
| `integration/mro-jk1p-pr66` | `mro-jk1p` integration evidence |
| `bugfix/mro-jk1p-provider-repair` | clean `mro-jk1p` evidence |
| `agent/mro-p68a-12-1-inventory` | clean lane with nonexistent inferred child; reassign administratively |
| `agent/mro-p68a-12-2-docs` | reserved documentation content |
| `bugfix/mro-pd8f-3-provider-sgconfig` | projection-only remainder after P0 owner cutover |
| `bugfix/mro-pd8f-published-baseline` | `mro-pd8f`, divergent dirty baseline |
| `bugfix/mro-shxw-setup-submodules` | old `mro-shxw` WIP source |
| `feature/mro-sw2l-1-external-provenance` | `mro-sw2l.1` |
| `pr38-release` | merged release evidence; residual GEN -> conform |
| `pr39-governance` | merged governance evidence; residual GEN -> conform |
| `pr40-docs` | reserved docs history; residual GEN -> conform |
| `provider-sgconfig-owner` | overlapping intake; not a second provider owner |

Local branches without their own worktree include:

```text
0.10.0-dev
0.11.0-dev
0.20.0-dev
c16
feature/mro-ydhf-docs
main
snapshot/cosmos-main-wvsc-pr-route--20260727-ac89906
snapshot/flext-0.12.0-dev--20260727-9271369
```

Do not delete any branch or worktree from this list during the first
continuation slice. Cleanup requires remote reachability proof, path-level WIP
classification, `mro-re80`, and the safe-delete workflow.

## 9. AI Hub callback state

AI Hub remains the required universal distributor, but no new writer should
overlap its active lane.

### 9.1 Active lane

```text
Bead: ai-hub-t449.2.4
status: in_progress
assignee: Codex
branch: feature/governance-skills-docs-convergence
worktree: /home/marlonsc/.ai-hub/.worktrees/governance-skills-docs-convergence
HEAD: 561a4449
remote relation: ahead 4
dirty paths: 12
last canonical state: static Make gates green; make test red with 21/1222 failures
```

This lane overlaps `ai-hub-t449.10` only in:

```text
src/ai_hub/services/validate_agent_law_surface.py
tests/unit/test_aihub_validate_agent_law_surface.py
```

Its 12 dirty paths at the audit were:

```text
src/ai_hub/services/_model_catalog.py
src/ai_hub/services/agent_work.py
src/ai_hub/services/model_availability.py
src/ai_hub/services/validate_agent_law_surface.py
src/ai_hub/services/worktree_create.py
tests/unit/test_aihub_gateway_static_catalog.py
tests/unit/test_aihub_generate_codex_assets.py
tests/unit/test_aihub_go7o_6_1_incident_fallback.py
tests/unit/test_aihub_go7o_6_1_variant_probe.py
tests/unit/test_aihub_model_availability_state.py
tests/unit/test_aihub_validate_agent_law_surface.py
tests/unit/test_opencode_permission_policy.py
```

It does not yet fix global AGENTS distribution, the global duplicate
`flext-law`, provider topology, or WAZA discovery.

### 9.2 Reserved P0 distribution lane

```text
Bead: ai-hub-t449.10
status: open, blocked by ai-hub-t449.2.4
branch: bugfix/ai-hub-t449-10-universal-landing-law
worktree: /home/marlonsc/.ai-hub/.worktrees/bugfix/ai-hub-t449-10-universal-landing-law
HEAD/remote: 22a76449
dirty paths: 14
relation to origin/dev at audit: 14 ahead / 7 behind
```

Its 14 dirty paths at the audit were:

```text
config/governance.yaml
docs/agent-law-full.md
src/ai_hub/_constants/workspace.py
src/ai_hub/_models/_config/governance.py
src/ai_hub/_models/cli.py
src/ai_hub/_protocols/cli.py
src/ai_hub/services/_ssot_relink_parts/__init__.py
src/ai_hub/services/_ssot_relink_parts/driver.py
src/ai_hub/services/generate_workspace_config.py
src/ai_hub/services/ssot_relink.py
src/ai_hub/services/validate_agent_law_surface.py
templates/workspace/CLAUDE.md
tests/unit/test_aihub_generate_workspace_config.py
tests/unit/test_aihub_validate_agent_law_surface.py
```

Its metadata is contradictory and must be corrected after re-reading:

```text
integration_branch=dev
integration_target=main          # stale/incorrect for the implementation PR
merge_state=reconciled           # false while dirty and behind dev
```

Retain `development_ref=dev` and the configured production boundary `main`, but
do not claim reconciliation. Add `flext_integration_target=0.12.0-dev` for the
provider callback instead of using a generic conflicting integration target.

### 9.3 Unresolved universal/distribution defects

At the audit:

- `~/.agents/AGENTS.md` was a symlink to dirty AI Hub main `AGENTS.md`, making
  uncommitted project WIP globally live;
- `~/.agents/skills` was a symlink to AI Hub `skills/`;
- AI Hub `skills/flext-law/SKILL.md` remained globally active and duplicated
  FLEXT ownership;
- provider topology used static `${HOME}/flext`, `recurse_submodules: false`,
  and only root plus nine FLEXT entries instead of deriving all 31 from the
  FLEXT topology SSOT;
- provider link validation rejected any Git-tracked `.agents` destination;
- WAZA required `<root>/skills` even when provider surfaces live under
  `.agents/skills`;
- `ssot_relink` copied `.waza.yaml` fleet-wide instead of consuming declared
  provider surfaces.

Canonical AI Hub sequencing:

1. finish `ai-hub-t449.2.4` green and land it to `dev`;
2. preserve and reconcile the dirty main `AGENTS.md` as input, never discard it;
3. claim and refresh `ai-hub-t449.10`;
4. absorb the two overlapping files;
5. finish source -> projection, remove the global `flext-law`, make provider
   discovery dynamic, allow exact declared Git-tracked links, and make WAZA
   consume provider surfaces;
6. use `ai-hub-t449.3` only if unique source/projection scope remains;
7. use `ai-hub-t449.6` as the final distribution/idempotence proof.

No AI Hub source mutation was performed by this session. Before the read-only
audit, `ai-hub-t449.10` metadata was linked to `mro-z89e`,
`mro-1o6t.1`, and `mro-1o6t.1.1`; that is the same metadata record whose
contradictory integration fields are listed above. No subsequent AI Hub Beads
batch was Dolt-pushed by this session.

## 10. Analysis and validation evidence

### 10.1 Structural and graph analysis

Text inventory:

```text
command: rtk rg -n --hidden ... 'flext-inviolable-rules|...'
cwd: /home/marlonsc/flext/.worktrees/flext-0.12.0-dev
exit: 0
result: eight stale direct documentation/prompt references identified
```

Ast-grep:

```text
command: rtk ast-grep scan --config flext-infra/src/flext_infra/codemod/sgconfig.yml --rule flext-infra/src/flext_infra/codemod/rules/hardcoded-ssot-literal.yml .agents .github AGENTS.md
cwd: /home/marlonsc/flext/.worktrees/flext-0.12.0-dev
exit: 0
result: no structural hardcoded-SSOT finding in the changed instruction surfaces
```

Code Review Graph CLI:

```text
binary: /home/marlonsc/.ai-hub/.venv/bin/code-review-graph
status: 84,437 nodes, 227,685 edges, 5,767 files
built branch: 0.12.0-dev
built commit: 98e4a36d69c2
detect-changes base: origin/0.12.0-dev
result: 41 changed files, zero changed code symbols, zero flows, risk 0.00
```

The zero graph risk reflects documentation/config/gitlink changes, not a
completion claim. CRG is analysis only.

### 10.2 Make validation

No final Make validation has run after the P0 file edits. Therefore:

- no `make setup` health claim exists;
- no `make docs` or WAZA claim exists;
- no Ruff, format, or Pyrefly claim exists;
- no affected Pyright/Mypy/Pytest claim exists;
- no provider-loading or standalone-routing QA claim exists;
- no generated fixed-point claim exists.

Do not call this slice green before fresh final Make evidence.

### 10.3 Git source publication

No P0 source commit was created and no Git source push occurred. The active
branch is still aligned with `origin/0.12.0-dev` at the old base, with all P0
changes uncommitted. The durable plan and this continuation handoff are
untracked until an explicit validated commit includes them.

### 10.4 GitHub publication

No GitHub comment, PR close, PR body update, merge, review, or new PR occurred.

### 10.5 Dolt publication frontier

- the lane-registry/supersession batch was pushed;
- the root-feature association batch was pushed;
- the final 13-Bead open-PR mapping batch was applied but not pushed;
- AI Hub Beads were not pushed by this session after the read-only audit.

## 11. Exact continuation order

The next session should execute these bounded slices in order.

### Slice A — recover and publish the pending tracker batch

1. Re-read this handoff and the live Beads.
2. Verify the 13 metadata mappings in section 6.6 still exist.
3. Run the FLEXT Dolt push with `BEADS_FSCK_TIMEOUT=240s`.
4. Re-read `mro-e9j0.6`; append the CLI-only CRG correction.
5. Update `mro-e9j0.6` with push evidence and the next action.

### Slice B — finish reciprocal root PR association

1. Re-read root PRs 47, 48, and 49 through the GitHub connector.
2. Add canonical association comments without replacing bodies.
3. Close 47 as duplicate, 49 as superseded evidence, and 48 as wrong-base
   redundant evidence.
4. Re-read final PR states.
5. Update `mro-1o6t.1.1`, `mro-0tvv.1`, and `mro-e9j0.6`.
6. Dolt-push the semantic batch.

### Slice C — complete the FLEXT P0 source cutover

1. Fast-forward refresh `0.12.0-dev` without discarding WIP.
2. Re-read the six P0 paths and the three direct prompt consumers.
3. Update in-scope prompt references to exact global generic skills and local
   FLEXT law.
4. Leave reserved `docs/**` content untouched and record the callback.
5. Audit every reference through `rg`, ast-grep, and CRG CLI.
6. Review the complete P0 diff and the durable plan for contradictions.

### Slice D — canonical Make proof and source publication

1. Run `make help` from the active root to confirm exact verbs.
2. Run the supported `make setup`. If it is absent or broken, repair the
   generic FLEXT Infra owner; do not substitute another setup path.
3. Run complete `make docs`; it must include WAZA and executable documentation.
4. Run global lint/format/Pyrefly and affected Pyright/Mypy/Pytest through Make.
5. Exercise real provider loading and branch-matched workspace/standalone
   routing through a canonical Make or documented public CLI surface.
6. Prove generation or conform fixed point if the owner declares these files
   generated.
7. Re-run every gate after the final edit.
8. Stage only the explicit P0 and plan/handoff paths.
9. Inspect the cached diff and commit.
10. Fast-forward push `0.12.0-dev` immediately.
11. Record SHA, push, commands, cwd, exit codes, decisive outputs, preserved
    WIP, and next action in `mro-1o6t.1.1`; Dolt-push.

### Slice E — AI Hub propagation

1. Do not overlap `ai-hub-t449.2.4`.
2. Verify whether its 21 test failures are green and whether it landed to
   `dev`.
3. Correct `ai-hub-t449.10` metadata only after re-reading live state.
4. Claim and reconcile its preserved lane.
5. Complete the global source/projection, provider-discovery, global duplicate
   removal, declared-link, and WAZA cutover.
6. Validate only through AI Hub Make commands, commit/push, open the correct PR
   to `dev`, and record reciprocal FLEXT callback evidence.
7. Continue with `mro-1o6t.1.2` and `.1.3` only after the AI Hub owner lands.

## 12. Copy-paste continuation prompt

Copy the following prompt into the next session:

```text
Continue the approved FLEXT 0.12.0-dev governance, Beads, PR, worktree, and AI
Hub propagation program. Do not restart planning and do not infer state from
chat memory.

First read completely, in order:
1. /home/marlonsc/.codex/RTK.md
2. ~/.agents/UNIVERSAL_CORE.md
3. ~/.agents/skills/inviolable-rules/SKILL.md
4. ~/.agents/skills/make-check/SKILL.md
5. /home/marlonsc/flext/.worktrees/flext-0.12.0-dev/AGENTS.md
6. the local flext-context-routing and flext-law skills in that worktree
7. ~/.agents/skills/verification-loop/SKILL.md
8. /home/marlonsc/flext/.worktrees/flext-0.12.0-dev/docs/superpowers/plans/2026-07-29-flext-beads-governance-reorganization-handoff.md
9. /home/marlonsc/flext/.worktrees/flext-0.12.0-dev/docs/superpowers/plans/2026-07-29-flext-governance-beads-execution-continuation.md
10. live Beads mro-z89e, mro-1o6t.1, mro-1o6t.1.1, and mro-e9j0.6.

Execution root:
/home/marlonsc/flext/.worktrees/flext-0.12.0-dev
Integration branch:
0.12.0-dev
Program:
flext-012-conform-beads-docs
Active leaf:
mro-1o6t.1.1
Lane registry:
mro-e9j0.6

Use the schema-compatible bd binary built from upstream SHA
423afdcb2813e36b2bc4c96b07e0fc3516a34495. Never use bd 1.1.2, downgrade the
schema, or use --ignore-schema-skew. Prefix every shell command with rtk.
Code Review Graph is CLI-only via
/home/marlonsc/.ai-hub/.venv/bin/code-review-graph; never use CRG MCP. Use
ast-grep structurally. Use Make only for setup, conform, generation, docs,
checks, types, tests, WAZA, and validation.

Preserve all dirty/staged/untracked/concurrent WIP. Never reset, restore, clean,
stash, amend, rebase published work, force-push, hand-edit generated files, or
blame another lane. Do not touch the parallel documentation-feature content in
feature/mro-ydhf-docs-local, pr40-docs, mro-p68a-12-2-docs, mro-ydhf.1/.1.1,
flext-infra PR64, or their docs/** paths.

The P0 governance source cutover is already implemented but unvalidated and
uncommitted: root AGENTS, provider, command, router, local flext-law, and
deletion of local flext-inviolable-rules. FLEXT owns the local flext-law;
global authority owns only inviolable-rules, make-check, and
verification-loop. Do not create flext-workspace-law or retain a global
flext-law duplicate.

The final interrupted Beads batch did apply all 13 open-PR metadata mappings but
has not been Dolt-pushed. Start by verifying and pushing it with
BEADS_FSCK_TIMEOUT=240s. Then append the CRG CLI-only correction to
mro-e9j0.6.

No GitHub writes have occurred. Add reciprocal top-level association comments
without replacing PR bodies, then close flext#47 as a duplicate, flext#49 as
superseded evidence, and flext#48 as a wrong-base redundant PR. Record final
states in Beads and Dolt-push.

Next finish the three in-scope direct prompt consumers of the removed local
skill, preserve the reserved docs consumers, audit with rg/ast-grep/CRG CLI,
run the complete canonical Make validation after the final edit, commit only
explicit owned paths, fast-forward push 0.12.0-dev immediately, and record exact
evidence in mro-1o6t.1.1.

AI Hub callback ai-hub-t449.10 is preserved and blocked by active
ai-hub-t449.2.4. Do not start an overlapping AI Hub writer. Re-audit it after
.2.4 is green and landed, then complete global source/projection, remove the
global duplicate flext-law, derive all FLEXT providers dynamically, permit only
exact declared Git-tracked links, and make WAZA consume provider surfaces.

Continue until the current bounded P0 slice is validated, committed, pushed,
reciprocally linked, and evidenced. If a genuine destructive or authority
decision appears, record it in the Bead and ask one precise question; otherwise
fix forward.
```

## 13. Session-transfer stop state

The previous session intentionally stops at this checkpoint because the
operator requested a new-session continuation artifact. This is not a green,
committed, pushed, or completed P0 claim.

The next observable action is:

```text
verify the 13 final Bead mappings, then push the pending FLEXT Dolt batch with
BEADS_FSCK_TIMEOUT=240s
```
