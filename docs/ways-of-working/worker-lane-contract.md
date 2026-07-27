# FLEXT Worker Lane Contract

Every light worker owns exactly one bead in one branch and one dedicated worktree.
Read the canonical authorities first; this file only adds lane discipline.

## Canonical authorities

- Project law and routed skills: [`AGENTS.md`][agents-md]
- Governance router: [`GOVERNANCE.md`][governance-md]
- Local skills: [`flext-law`][flext-law], [`flext-inviolable-rules`][flext-inviolable-rules]
- Universal skills: `~/.agents/skills/make-check/SKILL.md`, `~/.agents/skills/verification-loop/SKILL.md`
- Config/settings SSOT: [ADR-005][adr-005]

[agents-md]: ../../AGENTS.md
[governance-md]: ../GOVERNANCE.md
[flext-law]: ../../.agents/skills/flext-law/SKILL.md
[flext-inviolable-rules]: ../../.agents/skills/flext-inviolable-rules/SKILL.md
[adr-005]: ../architecture/adr/005-config-settings-constants-templates-schemas-ssot.md

## 1. One lane, one bead, one worktree

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
make val WHAT=workspace
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
- Nothing reaches `0.12.0-dev` except through the lead's PR #20 merge after the
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

## 8. Automated adjustments and pre-merge validation

Any automated adjustment — sync, codegen round-trip, auto-fix, or upstream
merge — must be treated as a code change:

- Validate it through the root-Make gates for the affected projects before
  reporting it done.
- Keep it atomic within the lane: one coherent commit or an explicit pathspec-bound
  set of commits. Do not leave open-ended `fixes` commits stacking unrelated
  changes.
- Before the lead merges the lane into `0.12.0-dev`, the lane must pass a
  pre-merge validation: `make check` and `make test` for every affected project.
  A red gate blocks the merge; fix forward inside the lane and re-validate.
- An upstream/external merge into the lane is only absorbed after the same
  lane-context validation passes.
