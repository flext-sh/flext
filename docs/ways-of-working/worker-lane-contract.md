# FLEXT Worker Lane Contract

Every light worker owns exactly one bead in one branch and one dedicated worktree.
Read the canonical authorities first; this file only adds lane discipline.

## Canonical authorities

- Project law and routed skills: [`AGENTS.md`][agents-md]
- Governance router: [`GOVERNANCE.md`][governance-md]
- Local skills: [`flext-law`][flext-law]
- Universal skills: `~/.agents/skills/inviolable-rules/SKILL.md`,
  `~/.agents/skills/make-check/SKILL.md`, `~/.agents/skills/verification-loop/SKILL.md`
- Config/settings SSOT: [ADR-005][adr-005]

[agents-md]: ../../AGENTS.md
[governance-md]: ../GOVERNANCE.md
[flext-law]: ../../.agents/skills/flext-law/SKILL.md
[adr-005]: ../architecture/adr/005-config-settings-constants-templates-schemas-ssot.md

## 1. One lane, one bead, one worktree

Open the lane with the public saga (not ad-hoc worktree commands):

```bash
make work WHAT=status PROJECT=<member> BEAD=<id>
make work WHAT=start PROJECT=<member> BEAD=<id> KIND=feature NAME=<slug> APPLY=Y
make work WHAT=land PROJECT=<member> BEAD=<id> APPLY=Y
make work WHAT=finish PROJECT=<member> BEAD=<id> APPLY=Y
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
make codegen WHAT=check PROJECT=<affected>
```

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

- RED→GREEN proof exists for the change.
- Exact Make-gate evidence is recorded: command, cwd, exit code, decisive line.
- No new lint, type, or test failures are injected.
- Changed files are clean and scoped.
- Nothing reaches `0.12.0-dev` except through the lead's `origin/0.12.0-dev` merge after the
  whole fleet is green.

## 6. Coordination protocol

Talk only through `team_send_message`. Report to the lead, then go idle;
idle-after-report is correct. When blocked, message the lead the exact blocker
and stop. Do not wander to other beads.

## 7. Anti-patterns that burned us

Do not repeat these:

- Heavy opus workers timing out on large tasks.
- Workers wandering to unrelated beads.
- Running bare-tool gate commands outside the Make dispatcher.
- `git add -A` commits sweeping foreign WIP.
- Treating idle-after-report as failure.

## 8. Three-boundary validation contract

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

### 8.1 Final worker lane

After the final lane edit or automated adjustment, the worker runs the complete
boundary above and records exact commands, cwd, exit codes, and decisive output.

### 8.2 Updated worker lane before merge

Before reporting `READY_FOR_REVIEW`, the worker must non-destructively merge the
latest `origin/0.12.0-dev` into the lane, resolve any resulting issues without
discarding WIP, and rerun the complete boundary above. An upstream merge is
absorbed only after this lane-context validation passes.

### 8.3 Original target after integration

After the lead/orchestrator integrates the lane into the original target, the
orchestrator reruns the complete boundary on that target and performs the real
public-surface QA. This is post-integration evidence, not worker evidence, and
must not be claimed before integration.

Any red, inconclusive, timed-out without a verdict, zero-project, partial-scope,
or stale-HEAD result blocks review or integration. Only complete, fresh green
evidence at the applicable boundary permits `READY_FOR_REVIEW`.

## Integration line

Land worker lanes onto `origin/0.12.0-dev` via `make work WHAT=land` / fast-forward
merge. Do not run `workspace-merge-main` or otherwise promote to `main` unless the
operator explicitly requests a release promote.

