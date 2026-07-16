---
name: flext-beads-coordination
description: >-
  Coordinate parallel FLEXT work in the single Beads tracker owned by the
  workspace root. Use for ownership matrices, child lanes, evidence, handoffs,
  and landing. Do not use to initialize a tracker inside a workspace member.
license: MIT
metadata:
  version: 2.0.0
---
# FLEXT Beads Coordination

## Use For

- Claiming a root or child Bead before writes.
- Splitting parallel work into disjoint path ownership.
- Recording state changes, validation, blockers, commits, and pushes.

## Workspace Ownership

The workspace root owns the Beads database. Every member and submodule uses
that same tracker, even when work targets only that member. Run `bd` from the
root or pass it explicitly:

```bash
bd -C <workspace-root> show <id>
bd -C <workspace-root> update <id> --append-notes '<evidence>'
```

Never run `bd init` in a member project. A separate tracker is correct only
when the project is independent rather than a member of a larger workspace.

## Workflow

1. Resolve the workspace root and inspect the named Bead.
2. Claim the issue and record target, impact, risk, and exact path ownership.
3. Create child Beads in the same root tracker for independent parallel lanes.
4. Keep writers inside owned paths; read-only audits may inspect broadly.
5. After every state-changing step, append the command or edit summary, exit
   code, decisive output, and next state.
6. Run the narrowest affected gates, then the native project/workspace gate.
7. Land with explicit pathspecs, one scoped commit, fast-forward push, and final
   evidence in the same tracker.

## Non-Negotiables

- Never edit `.beads/*.jsonl` directly.
- Never create a nested database to work around missing context.
- Never overwrite, reset, clean, stash, revert, or absorb another lane's work.
- Resolve overlapping ownership in the root Bead before either writer proceeds.
- A red gate remains an active incident with its exact evidence.

## Troubleshooting

- `database not initialized` inside a member: rerun with
  `bd -C <workspace-root>`; do not initialize locally.
- Unknown claim flag during create: create the Bead, then claim it with the
  supported `bd update` action.
- Push rejection: stop, record the exact error and local/remote SHAs, and do not
  rebase or force-push autonomously.
