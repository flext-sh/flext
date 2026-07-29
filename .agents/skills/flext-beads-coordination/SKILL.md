---
name: flext-beads-coordination
description: 'Use when coordinating parallel FLEXT work through Beads or an equivalent active ledger, with disjoint ownership, dependency-aware lanes, evidence, integration review, and scoped landing.'
license: MIT
metadata:
  version: 2.0.0
---
# FLEXT Coordination Ledger

## Workflow

1. Inspect the active Bead when `bd` is available; otherwise maintain the same intent
   and evidence explicitly in the current task and report the tool limitation.
2. Record the target, authority, live/target owner, exclusions, risks, dependencies,
   acceptance gates, and stop condition before assigning writes.
3. Split work by disjoint path ownership and dependency order. Parallelize read-only
   audits before freezing the implementation contract.
4. Give every lane its writable paths, read-only context, required output, exact gates,
   and prohibition on hidden scope expansion.
5. Review returned findings and diffs against live shared state. Reconcile overlaps
   before staging and validate the combined result, not only lane-local results.
6. Record commands, exit status, decisive output, commit SHA, and remaining risk.

## Lane states

`ready → claimed → implementing → validating → integrated → landed`

A lane returns to `implementing` when combined validation exposes a defect. `blocked`
requires an external decision or unavailable owner, not merely a red gate that can be
fixed within the lane.

## Coordination contracts

- One outcome has one coordinator and one frozen target contract.
- One writable path has one active implementation owner at a time.
- Read-only audits may overlap; write lanes may not silently edit shared files.
- Workers do not merge, close coordinator-owned work, or create compatibility paths.
- The coordinator alone reconciles shared files, orders integration, and declares the
  combined acceptance gates complete.
- Long evidence belongs in `.beads/artifacts/<bead-id>/` when Beads is available;
  ledger notes retain the concise result and path.

## Recovery

If a tool or session ends, reload the active ledger, Git state, mutable files, lane
ownership, last green evidence, and next dependency-ready action. Never recover by
resetting, stashing, or discarding shared work.
