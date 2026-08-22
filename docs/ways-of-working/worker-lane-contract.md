# FLEXT Worker Lane Contract

<!-- TOC START -->
- [Canonical authorities](#canonical-authorities)
- [1. One lane, one bead, one worktree](#1-one-lane-one-bead-one-worktree)
- [2. Gates only through root Make verbs](#2-gates-only-through-root-make-verbs)
- [3. Cooperative git](#3-cooperative-git)
- [4. Beads evidence only](#4-beads-evidence-only)
- [5. Definition of done](#5-definition-of-done)
- [6. Gas Town CLI surface](#6-gas-town-cli-surface)
- [7. Coordination protocol](#7-coordination-protocol)
- [8. Anti-patterns that burned us](#8-anti-patterns-that-burned-us)
- [9. Three-boundary validation contract](#9-three-boundary-validation-contract)
  - [9.1 Final worker lane](#91-final-worker-lane)
  - [9.2 Updated worker lane before merge](#92-updated-worker-lane-before-merge)
  - [9.3 Original target after integration](#93-original-target-after-integration)
- [Integration line](#integration-line)
<!-- TOC END -->

Every light worker owns exactly one bead in one branch and one dedicated worktree.
Read the canonical authorities first; this file only adds lane discipline.

## Canonical authorities

- Project law and routed skills: [`AGENTS.md`][agents-md]
- Governance router: [`GOVERNANCE.md`][governance-md]
- Local skills: [`flext-law`][flext-law]
- Universal skills: `~/.agents/skills/inviolable-rules/SKILL.md`,
  `~/.agents/skills/make-check/SKILL.md`, `~/.agents/skills/verification-loop/SKILL.md`
- Gas Town rig: `gt prime` / `gt rig status flext` / `gt sling` / `gt convoy`
- Config/settings SSOT: [ADR-005][adr-005]

[agents-md]: ../../AGENTS.md
[governance-md]: ../GOVERNANCE.md
[flext-law]: ../../.agents/skills/flext-law/SKILL.md
[adr-005]: ../architecture/adr/005-config-settings-constants-templates-schemas-ssot.md

## 1. One lane, one bead, one worktree

Open and complete the lane through Gas Town:

```bash
gt sling <id> flext
gt hook status
gt convoy status <convoy-id>
# Choose one completion path:
gt done
gt handoff <id>
```

Claim exactly one bead and stay inside the worktree created for it. Do not edit
paths outside your declared scope; do not borrow files from another lane. If
another lane's output blocks you, message the lead instead of patching around it.

## 2. Gates only through root Make verbs

Never invoke bare `ruff`, `pyrefly`, `pyright`, `mypy`, `pytest`, or `uv`. Use
the dispatcher:

```bash
make check CHECK_GATES=lint,format,pyrefly
make check PROJECT=<affected> CHECK_GATES=pyright,mypy
make test PROJECT=<affected>
make test CI=Y PROJECT=<affected>
make gen WHAT=check PROJECT=<affected>
```

The complete applicable validation boundary, including coverage when required,
must be green before `gt done`. `gt done` submits a validated lane; it does not
authorize integration.

Run the narrowest changed-scope gate first; widen only after it passes.

## 3. Cooperative git

Treat every git command as `GIT_MASTER=1` safe. Commit by explicit pathspec after
inspecting `git diff --cached --stat`. Never `git add -A`, stash, reset,
checkout-away, clean, amend, or force-push. If foreign WIP appears in `git
status`, leave it untouched and ask the lead. Fix forward only.

## 4. Beads evidence only

Append truthful notes with `bd update <id> --append-notes '...'`. Never change
bead status, assignee, dependency, priority, or close/merge beads. The lead owns
bead state.

## 5. Definition of done

Done means all of the following:

- local `make test` (coverage enabled) is green for the affected project when tests changed

- RED→GREEN proof exists for the change.
- Exact Make-gate evidence is recorded: command, cwd, exit code, decisive line.
- No new lint, type, or test failures are injected.
- Changed files are clean and scoped.
- Nothing reaches `0.12.0-dev` except through the lead's `origin/0.12.0-dev` merge after the
  whole fleet is green.

## 6. Gas Town CLI surface

Make owns build and validation. Gas Town owns lane dispatch, tracking, and completion:

| Intent | Command | Notes |
|--------|---------|-------|
| Start work on a bead | `gt sling <bead> <rig>` | Hooks + spawns; auto-creates convoy |
| Attach without spawning | `gt hook <bead>` or `gt work <bead>` | Just attaches to hook |
| Check hook status | `gt hook` or `gt work` | Shows current assignment |
| Submit and exit | `gt done` | Pushes branch, submits MR, exits session |
| Check convoy progress | `gt convoy status <id>` | Batch tracking across rigs |
| Check ready work | `gt ready` | Unblocked work across town |
| Hand off to fresh session | `gt handoff <bead>` | Hooks + restarts with fresh context |
| Restore context | `gt prime` | Loads role context after compaction |
| Message another worker | `gt nudge <target> "msg"` | Ephemeral, no Dolt cost |
| Durable message | `gt mail send <rig>/<role> -s "subj" -m "msg"` | Persistent bead record |

`gt work` is an alias for `gt hook`; there is no separate `gt work` command group.

## 7. Coordination protocol

Talk only through `gt nudge` (ephemeral) or `gt mail send` (durable). Report to the lead, then go idle;
idle-after-report is correct. When blocked, nudge the lead the exact blocker and stop. Do not wander to other beads.

## 8. Anti-patterns that burned us

Do not repeat these:

- Heavy opus workers timing out on large tasks.
- Workers wandering to unrelated beads.
- Running bare-tool gate commands outside the Make dispatcher.
- `git add -A` commits sweeping foreign WIP.
- Treating idle-after-report as failure.

## 9. Three-boundary validation contract

Any edit or automated adjustment — sync, codegen round-trip, auto-fix, or
upstream merge — is a code change. Keep automated corrections atomic within the
lane: one coherent commit or an explicit pathspec-bound set of commits.

The following fresh evidence is mandatory at every boundary:

- `make check CHECK_GATES=lint,format,pyrefly` for the global workspace;
- `make check PROJECT=<affected> CHECK_GATES=pyright,mypy` for every affected
  project and consumer;
- `make test PROJECT=<affected>` for every affected project and integration
  surface;
- real public-surface QA for the changed behavior; and
- generator/consumer idempotence when generated outputs are involved.

### 9.1 Final worker lane

After the final lane edit or automated adjustment, the worker runs the complete
boundary above and records exact commands, cwd, exit codes, and decisive output.

### 9.2 Updated worker lane before merge

Before reporting `READY_FOR_REVIEW`, the worker must non-destructively merge the
latest `origin/0.12.0-dev` into the lane, resolve any resulting issues without
discarding WIP, and rerun the complete boundary above. An upstream merge is
absorbed only after this lane-context validation passes.

### 9.3 Original target after integration

After the lead/orchestrator integrates the lane into the original target, the
orchestrator reruns the complete boundary on that target and performs the real
public-surface QA. This is post-integration evidence, not worker evidence, and
must not be claimed before integration.

Any red, inconclusive, timed-out without a verdict, zero-project, partial-scope,
or stale-HEAD result blocks review or integration. Only complete, fresh green
evidence at the applicable boundary permits `READY_FOR_REVIEW`.

## Integration line

Submit worker lanes to Refinery with `gt done` only after the readiness boundary
is green. Refinery integrates into `origin/0.12.0-dev` only after fleet-wide
validation and lead authorization, then closes the lane after merge. Promotion
to `main` is a separate operator-authorized release action.
