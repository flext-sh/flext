# FLEXT Worker Lane Contract

<!-- TOC START -->

- [Canonical authorities](#canonical-authorities)
- [1. One lane, one bead, one worktree](#1-one-lane-one-bead-one-worktree)
- [2. Gates only through root Make verbs](#2-gates-only-through-root-make-verbs)
- [3. Cooperative git](#3-cooperative-git)
- [4. Beads evidence only](#4-beads-evidence-only)
- [5. Definition of done](#5-definition-of-done)
- [6. Coordination protocol](#6-coordination-protocol)
- [7. Anti-patterns that burned us](#7-anti-patterns-that-burned-us)
- [8. Three-boundary validation contract](#8-three-boundary-validation-contract)
  - [8.1 Final worker lane](#81-final-worker-lane)
  - [8.2 Updated worker lane before merge](#82-updated-worker-lane-before-merge)
  - [8.3 Original target after integration](#83-original-target-after-integration)

<!-- TOC END -->

Every light worker owns exactly one bead in one branch and one dedicated worktree. Read
the canonical authorities first; this file only adds lane discipline.

## Canonical authorities

- Project law and routed skills: [`AGENTS.md`][agents-md]
- Governance router: [`GOVERNANCE.md`][governance-md]
- Local skills:
  [`flext-law`](https://github.com/flext-sh/flext/blob/0.12.0-dev/.agents/skills/flext-law/SKILL.md)
- Universal skills: `~/.agents/skills/project-wide/shell/make-check/SKILL.md`,
  `~/.agents/skills/agent-wide/verification/verification-loop/SKILL.md`
- Config/settings SSOT: [ADR-005][adr-005]
- Command and test policy: `~/agents/rules/workflow/canonical-commands.md`
- Inter-session mail: `~/agents/rules/coordination/inter-session-mail.md`

[agents-md]: https://github.com/flext-sh/flext/blob/0.12.0-dev/AGENTS.md
[governance-md]: ../GOVERNANCE.md
[adr-005]: ../architecture/adr/005-config-settings-constants-templates-schemas-ssot.md

## 1. One lane, one bead, one worktree

Claim exactly one bead and stay inside the worktree created for it. Do not edit paths
outside your declared scope. Operator-authorized adoption of reviewed, committed work
uses `git cherry-pick -x` or `git merge --no-ff`, with source SHA, provenance, scope,
and authorization recorded in the Bead and PR. Never copy raw WIP, environments, caches,
or generated projections from another lane. Notify the lead through canonical mail
before adoption; preserve unrelated work and route blockers to their owners, never
bypass them.

## 2. Gates only through root Make verbs

Never invoke bare `ruff`, `pyrefly`, `pyright`, `mypy`, `pytest`, or `uv`. Use the
dispatcher:

```bash
make gen
make check
make test
```

Follow `canonical-commands.md` for test verbs, selection, and cache policy.

## 3. Cooperative git

Treat every git command as `GIT_MASTER=1` safe. Commit by explicit pathspec after
inspecting `git diff --cached --stat`. Never `git add -A`, stash, reset, checkout-away,
clean, amend, or force-push. If foreign WIP appears in `git status`, leave it untouched
and ask the lead. Fix forward only.

## 4. Beads evidence only

Append truthful notes with `bd comment <id> '...'`. Never change bead status, assignee,
dependency, priority, or close/merge beads. The lead owns bead state.

## 5. Definition of done

Done means all of the following:

- RED→GREEN proof exists for the change.
- Exact Make-gate evidence is recorded: command, cwd, exit code, decisive line.
- Applicable native lint, type, test, docs/build, and public-runtime gates pass on the
  exact candidate; report executed, reported, deselected, and inventory counts and their
  agreement. No new failures are injected, and zero execution is not a passing receipt
  except where the canonical owner explicitly permits a typed cache hit.
- Changed files are clean and scoped.
- Nothing reaches `0.12.0-dev` except through the lane's own reviewed PR: one bead ->
  one branch -> PR against `0.12.0-dev` -> green native gates -> PR Sheriff gate
  (`pr_triage.py gate <owner/repo> <pr> --base 0.12.0-dev --head <oid>` in
  `~/.agents/skills/tool/pr-sheriff/scripts/`) -> independent review or
  operator-authorized administrative merge -> actual GitHub PR `MERGED` with merge SHA
  -> applicable integrated CI GREEN and post-merge runtime proof -> bead evidence ->
  authorized branch cleanup. An approval waiver does not waive native gates, count
  evidence, CI, or post-merge proof. The coordinator owns admin integration and closure;
  workers do not merge or close.

## 6. Coordination protocol

Use `gc mail` notification and message readback under `inter-session-mail.md`; the
Bead is execution SSOT and the PR records review, source, and CI evidence. Persist
scoped checkpoints and continue authorized, unblocked work rather than stopping merely
after a report. For a real blocker, record the first cause, command, cwd, and exit
(unknown if execution never reached the command), notify the lead, and route its owner.
Do not wander to other beads or bypass blocked gates.

## 7. Anti-patterns that burned us

Do not repeat these:

- Heavy opus workers timing out on large tasks.
- Workers wandering to unrelated beads.
- Running bare-tool gate commands outside the Make dispatcher.
- `git add -A` commits sweeping foreign WIP.
- Treating a report or source checkpoint as delivery, or stopping merely after
  reporting.

## 8. Three-boundary validation contract

Any edit or automated adjustment — sync, codegen round-trip, auto-fix, or upstream merge
— is a code change. Keep automated corrections atomic within the lane: one coherent
commit or an explicit pathspec-bound set of commits.

A WIP checkpoint preserves a scoped commit on its remote branch; it does not establish
review readiness. Resolve the integration branch from the repository's current
declaration before fetching it. Substitute that branch for `<integration>` below.
Freshly fetch and absorb `origin/<integration>` with `git merge --no-ff`, never rebase.
Publish explicit-path scoped commits by fast-forward push and open the lane's PR
against that verified integration branch; a DRAFT preservation PR is not delivery.
`git merge-base --is-ancestor origin/<integration> HEAD` proves base absorption; the
reverse order proves that the lane commit is contained in integration. Neither proof
replaces reviewed PR merge-commit evidence or runtime validation. Propagation requires
fresh native validation in the original target checkout against the integrated
candidate. Record these boundaries separately in the active Bead.

The following fresh evidence is mandatory at every boundary:

- `make check` for the workspace;
- applicable test evidence for affected projects and integration surfaces through the
  verbs and cache policy owned by `canonical-commands.md`;
- real public-surface QA for the changed behavior; and
- generator/consumer idempotence when generated outputs are involved.

### 8.1 Final worker lane

After the final lane edit or automated adjustment, the worker runs the complete boundary
above and records exact commands, cwd, exit codes, and decisive output.

### 8.2 Updated worker lane before merge

Before reporting `READY_FOR_REVIEW`, the worker must non-destructively merge the latest
freshly fetched, declared integration branch with `git merge --no-ff`, resolve issues
without discarding WIP, and rerun the complete boundary above. An upstream merge is
absorbed only after this lane-context validation passes.

### 8.3 Original target after integration

After the lead/orchestrator integrates the lane into the original target, the
orchestrator reruns the complete boundary on that target and performs the real
public-surface QA. This is post-integration evidence, not worker evidence, and must not
be claimed before integration.

Any red, inconclusive, timed-out without a verdict, zero-project, partial-scope, or
stale-HEAD result blocks review or integration. Only complete, fresh green evidence at
the applicable boundary permits `READY_FOR_REVIEW`.
