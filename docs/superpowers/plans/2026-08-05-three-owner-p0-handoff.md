---
artifact_contract: "ce-handoff/v1"
created_at: "2026-08-05T13:49:46Z"
title: "Three-Owner P0 complete — T0 gated for 0.12.0 release"
summary: "P0 tracker+ledger restored; program mro-wshr under mro-wkii; T0 blocked by mro-hsiu.1 until operator request after 0.12.0 release."
keywords: ["three-owner", "P0", "mro-wshr", "mro-hsiu", "enforcement", "flext-tests", "0.20.0-dev"]
cwd: "/home/marlonsc/flext"
resume_focus: "Do not start T0. Keep P0 durable (commit ledger+handoff if operator asks). Resume T0 only after 0.12.0 release + explicit mro-wkii/T0 request: close mro-hsiu.1, set operator_declared_012_final_sha, claim mro-k60y."
repository: "flext"
repo_root_sha: "7be6bf62dc0511f22f63b33d6961bc8780adf0f7"
branch: "0.12.0-dev"
head: "c59d2e61b7022ece3dbf9f1a3de162cec6e83ba7"
---

# Handoff — FLEXT Three-Owner Enforcement (P0)

## Objective and intent

Program: close ownership so `flext-core` = runtime Beartype only, `flext-infra` = static declarative multi-engine + codegen, `flext-tests` = all reusable pytest automation.

Operator scope for the completed session: **execute through P0 only**. T0 (merge `0.12` final → `0.20.0-dev`) starts **only after** the `0.12.0` release is published **and** the operator explicitly requests `mro-wkii` / T0.

Plan reference (not execution SSOT): `~/.cursor/plans/flext_three_owner_enforcement_749c8d6f.plan.md`.

## Authoritative SSOT (use these, not chat history)

| Artifact | Path / ID |
| --- | --- |
| Program epic | `mro-wshr` (parent `mro-wkii`) |
| P0 epic (closed) | `mro-ylo0` |
| T0 epic (open, gated) | `mro-hsiu` |
| Operator gate (open) | `mro-hsiu.1` → blocks `mro-k60y` |
| Typed ledger | `docs/references/three-owner-enforcement-ledger.json` |
| Human ledger | `docs/references/three-owner-enforcement-ledger.md` |
| Related stabilize task | `mro-dxrp` (absorb DoD into T0; do not run competing merge) |
| Deferred Beartype warnings | `mro-31mj` (absorb into EC) |
| Closed folded P3 | `mro-wkii.4` |

Beads design/notes on every program bead carry the full RESUME block (architecture, constraints, DoD, dependency order, T0 gate).

## Implementation analysis (what P0 did / did not do)

### Done (verified live)

- Program child of `mro-wkii`: `mro-wshr` + 13 child epics + implement/validate/cutover/dogfood tasks (label `program:three-owner`, `branch:0.20.0-dev`).
- P0 phase beads closed: `mro-05rh`, `mro-m2h9`, `mro-nr9y`, `mro-gn1z`; epic `mro-ylo0` closed.
- Cross-epic `blocks` edges corrected after inverted `bd create --graph` orientation (lesson recorded in ledger `bd_graph_edge_lesson`).
- Operator gate `mro-hsiu.1` keeps T0.I (`mro-k60y`) blocked after P0.V closed.
- Census rebuilt: **92** catalog rules via `u.build_canonical_catalog()` — core **25** (`beartype` 24 + `runtime_warning` 1), infra **67**; root conftests **31**.

### Gap found during this handoff (fixed)

- Ledger files were **missing from disk** (written in P0 session, never committed, lost before handoff).
- **Restored** on 2026-08-05 from live Beads + catalog; status `P0_COMPLETE_LEDGER_RESTORED`.
- Still **uncommitted** in the workspace at handoff time — durable only after scoped commit of ledger + this handoff.

### Not started (correctly deferred)

- No T0 merge, no ADR amend, no EC/ET/E1/E2 code, no engine cutovers, no fleet waves.
- Workspace remains on `0.12.0-dev` (`c59d2e61…`); forward implementation stays on `0.20.0-dev` after T0.

## Decisions and constraints

- Newest operator instruction wins: P0 only; T0 waits for release + explicit request.
- Beads + ledger are execution SSOT; plan file is reference only.
- One git root per PR; gitlink rollups separate; no shims/old+new; no lane `uv sync` on shared venv.
- `bd create --graph` edge `type=blocks`: use `from_key=BLOCKED` → `to_key=BLOCKER`, or prefer `bd dep <blocker> --blocks <blocked>`.
- Workers annotate evidence; orchestrator mutates graph / merge / close.

## Current state

- Branch: `0.12.0-dev` @ `c59d2e61b7022ece3dbf9f1a3de162cec6e83ba7`
- Program open: `mro-wshr`; next actionable program work is **not** ready — blocked by `mro-hsiu.1`
- Uncommitted (machine-local until commit): ledger JSON/MD + this handoff under `docs/`
- Dirty tree may include unrelated WIP elsewhere — stage **only** three-owner docs paths

## Verification performed

- `bd show` confirms P0 closed, gate open, `mro-k60y` blocked by `mro-hsiu.1`
- Ledger JSON asserts: `prog=mro-wshr`, `t0_operator_gate=mro-hsiu.1`, 92 rules, 67 bead keys mapped
- Catalog rebuild via `PYTHONPATH=flext-core/src` + shared venv interpreter (no `uv sync`)

## Next steps (single path)

1. **Now (optional durability):** scoped commit of:
   - `docs/references/three-owner-enforcement-ledger.json`
   - `docs/references/three-owner-enforcement-ledger.md`
   - `docs/superpowers/plans/2026-08-05-three-owner-p0-handoff.md`
2. **Stop.** Do not claim T0/E0/EC/…
3. **Historical disposition:** this 2026-08-05 instruction used the now-retired
   Make lane lifecycle. It is not operational guidance. Current work uses Gas
   Town and the active Bead.

## Skills for resume

- `.agents/skills/flext-context-routing/SKILL.md` → `flext-law`
- `~/.agents/skills/inviolable-rules`, `make-check`, `verification-loop`
- `docs/ways-of-working/worker-lane-contract.md` (three-boundary)
- Beads worker/orchestrator skills when executing T0+
