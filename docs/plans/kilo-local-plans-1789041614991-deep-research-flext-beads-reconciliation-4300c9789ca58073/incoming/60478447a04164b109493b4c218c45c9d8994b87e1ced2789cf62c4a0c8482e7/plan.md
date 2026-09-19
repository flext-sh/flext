# Deep Research — Beads Reconciliation Retry

## Objective

- Make the next Beads reconciliation cycle reproducible, bounded, and evidence-first.
- Reuse FLEXT skills and standards so this is a normal governed workflow, not ad-hoc
  cleanup.
- Use subagents for the majority of analytical work; the coordinator applies only
  reviewed mutation batches.

## Current Reality

- Tracker runtime is degraded. Dolt server probe failed:
  - `2026/09/10 10:30:18 ERROR native_store_unavailable gate=identity_match`
    `reason="database project_id could not be confirmed" scope=~/gc`
  - `bd ping` / `bd graph check` failed with
    `dolt circuit breaker is open: server appears down` at 127.0.0.1:14499.
  - `gc status --json` reports the city as `running:true`, `suspended:true`,
    `degraded:true`, and `no_agents_running`.
- The last complete inventory snapshot still exists:
  - `.beads/artifacts/inventory-20260910/{open,in_progress,blocked,deferred,ready,stale,orphans,duplicates,related-open}.json`
  - `stats.json` at `11:30Z`: 2,867 closed, 265 open, 24 in progress, 5 deferred, 60
    blocked.
- Four inventory batches were exported read-only and remain usable:
  - `.beads/artifacts/recon-20260910/queue-b0.csv`
  - `queue-20.csv` (190 records)
  - `queue-40.csv`
  - `queue-60.csv`
- Subagent adjudication results already return useful partials:
  - deferred-state audit: all five deferred beads are currently valid; none should be
    undeferred now.
  - active-claim audit: many stale claims between July and Sept; no evidence of live
    work in most.
  - labels/parents/hierarchy and duplicate candidates need one reviewed pass before any
    write.
- Operator constraint: work stays on `0.12.0-dev`; `0.20.0-dev` is read-only comparison
  evidence.

## Important Details

- Repository law:
  - Beads mutations only after fresh read of exactly the target bead.
  - Max 20 reviewed mutations per coordinator batch and stop on the first stale read,
    failed precondition, graph defect, or inconsistent state.
  - Tasks under one parent; bugs at root with `bugfix`; `hotfix` only on P0/P1 bugs.
  - Valid closure reasons: `SUPERSEDED:`, `OBSOLETE:`, `DONE:` — each names proof.
  - No old+new, no shims, no fake green, no bypass of generated Make surfaces.
  - FLEXT standards: ADR-005 config/settings SSOT, fp-over-role, bounded scope and
    reciprocal evidence, unified `conftest.py`, Make-control graph, and fleet-open
    boundaries.
- Session evidence:
  - Active coordination bead is `flext-0kl7`. In-progress under `flext-wshr`.
  - Prior work plus rules live in `.beads/artifacts/recon-20260910/` and prior plan refs
    (see `.kilo/plans/1788987519000-checkpoint-refactor-plan.md`).
  - The reconciliation script is read-only-safe:
    `~/agents/skills/tool/beads-organization/scripts/reconcile-inventory.sh --limit 20`
    `--integration origin/0.12.0-dev --dry-run`.
  - Coordinator does not close or merge code; subagents analyze and report.

## Next Move

### 1) Recover runtime (coordinator, single first action)

- Re-run Dolt health as one batch, So before reading Beads again:
  - Preferred gate: `gc status --json`.
- Then, only after runtime is stable:
  - `make gen`
  - `make gen`
  - `make gen`
- Stop at the first failure and triage from exact output.
- Only after those three steps pass:
  - `make gen`
  - `make test`

### 2) Re-baseline fresh Beads state (coordinator)

- Run the standup and inventory script again for exact fresh snapshots:
  - `bd ping --json`
  - `bd context --json`
  - `bd status --json`
  - `bd graph check --json`
  - `bd find-duplicates --limit 0 --json`
  - `bd orphans --json`
  - `bd stale --json`
- Save new artifacts under `.beads/artifacts/recon-20260910/` only when the read is
  clean.

### 3) Spawn bounded subagent waves (read-only)

- Use four parallel workers, each with a precise row scope:
  1. Review `queue-20p1.csv` (records 21–40) and return a compact ≤120-row plan.
  2. Review `queue-20p2.csv` (records 41–60) and return a compact ≤120-row plan.
  3. Reconcile exact `inde-progress` claims (no labels or `bugfix`) and classify
     keep/unclaim/defer.
  4. Re-run `queue-40p2.csv` and `queue-60p2.csv` with strict output format and explicit
     proof citations.
- Every worker must return:
  - id, action, target, labels_add, labels_remove, status, evidence (≤15 words), exact
    command/SHA.
  - explicit `undecided` list when evidence is insufficient.
- Do NOT mutate Beads from workers; only the coordinator applies batches.

### 4) Coordinator mutation batches (max 20 operations)

- Apply only after fresh `bd graph check` and `bd count --by-status --json`.
- Use canonical command grammar:
  - Label moves:
    `bd update <id> --add-label bugfix --remove-label invalid_hotfix --set-labels "..."`
    (verify exact grammar with `bd update --help` before use).
  - Parent moves: `bd update <id> --parent <target>` only when the target parent is open
    and in a valid feature epic.
  - Claims: `bd update <id> --unclaim` only when the current evidence proves the claim
    is just stale and no live executor exists.
- After each batch, re-run:
  - `bd graph check --json`
  - `bd count --by-status --json`
  - `bd find-duplicates --limit 20 --json`
  - `bd orphans --json`
- Stop immediately on any mismatch and either revise the batch or ask the operator.

### 5) Closure / hierarchy / dependency policy

- Bugs stay at root and carry `bugfix`; `hotfix` only when P0/P1.
- Any task may have at most one parent.
- End-state rule per bead:
  - `DONE:` only with agreed user proof.
  - `SUPERSEDED:` with exact file path or reason.
  - `OBSOLETE:` with a concrete residue check.
- Use `bd close` sparingly; always close a bead only after the code/test/docs alignment
  is proven.
- Start with the most valuable first slice:
  1. Set exact labels for P0/P1 from the `bugfix`/`hotfix` labels.
  2. Fix parent assignments before any close.
  3. Finish with the graph-level gate.

### 6) Validation protocol

- Gates per batch:
  - Before: `bd graph check --json`.
  - During: inspect at most 20 beads per batch.
  - After: `bd count --by-status --json`.
- End-of-cycle:
  - `make gen`
  - `make test`
- Failure protocol:
  - Every gating failure or stale claim is RED.
  - Coordinator asks the operator only after `make check`/`make test` are tried once.

## Relevant Files

- `.beads/artifacts/recon-20260910/queue-b0.csv`
- `.beads/artifacts/recon-20260910/queue-20.csv`
- `.beads/artifacts/recon-20260910/queue-40.csv`
- `.beads/artifacts/recon-20260910/queue-60.csv`
- `.beads/artifacts/inventory-20260910/`
- `.kilo/plans/1788987519000-checkpoint-refactor-plan.md`
- `.agents/skills/source-local-fallback/tests/plugins/conftest_cls_hook.py`
