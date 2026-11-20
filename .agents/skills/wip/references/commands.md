# ai-hub wip — Command Reference

- `ai-hub wip status [--workspace PATH] [--json]` — hierarchy, git and sync state
- `ai-hub wip doctor [--workspace PATH] [--json]` — validate workspace resolution
- `ai-hub wip claim --bead ID [--path PATH ...] [--reason TEXT]` — claim and declare the
  authorized scope; idempotent; refuses closed, foreign, conflicting or escaping scopes
- `ai-hub wip start --bead ID [--claim] [--path PATH ...] [--branch NAME]` — preflight and
  create the lane; with `--claim` the claim runs before the scope gate
- `ai-hub wip next --bead ID` — next permitted action from observed lane facts
- `ai-hub wip cancel --bead ID --reason TEXT` — close the lane PR, preserving content
- `ai-hub wip sweep [--apply] [--align] [--idle-minutes N] [--json]` — preserve local work
  and retire idle worktrees (mutates only with `--apply`; never removes active or
  `.gc/worktrees`)
- `ai-hub wip evidence --bead ID` — record authenticated native component report
- `ai-hub wip check --bead ID` — run provider lifecycle on dirty repos in the lane
- `ai-hub wip save --bead ID` — commit, push and open the bead's draft PR from the lane
- `ai-hub wip ship --bead ID` — promote eligible draft PRs to ready for review
- `ai-hub wip approve --bead ID` — record an approval bound to the PR head SHA
- `ai-hub wip land --bead ID` — merge the reviewed PR at its approved head
- `ai-hub wip clean --bead ID` — retire the merged lane worktree after publication

Full lifecycle and placement rules: `docs/guides/wip-session-workflow.md` and
`docs/worktrees.md` in ai-hub.
