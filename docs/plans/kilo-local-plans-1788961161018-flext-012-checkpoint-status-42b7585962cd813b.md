# Flext 0.12.0 Checkpoint — Status Against Beads

> Parent execution status artifact. Beads own semantic state. This is a
> read/progress view, not a second tracker.
> Updated: 2026-09-09 18:55 UTC (checkpoint turn — operator asked for a
> stable WIP close, published tips, and a progress stop).
>
> **Execution plan of record (v2):**
> `1788975180492-execution-strategy-skills-automation.md` — skills &
> automation-accelerated landing (`make mod` bulk fixes, manual
> `code-review-graph` pre-pass, pr-sheriff PR loop, subagent triage,
> checkpoint-after-each-green-slice cadence).

## Published Tips (remote-proof this turn)

| Project | Branch | Tip | Proof |
|---|---|---|---|
| flext-infra | release/checkpoint-0.12.0 | `0d29f44ee` | `git ls-remote` → 0d29f44ee (fast-forward, no force) |
| flext-ldif | release/checkpoint-0.12.0 | `8c558dfe` | pushed earlier this session; PR #96 merged `c6231b6f` on 0.12.0-dev |
| root (superproject) | release/checkpoint-0.12.0 | `4147d43428` | push `5f93143da0..4147d43428` exit 0 |

Root gitlinks: flext-infra `0d29f44ee`, flext-ldif `8c558dfe`.
`make gen` exit 0, fixed-point verified, root Makefile carries the
9 `_builtin-self-*` targets.

## Recovery Recorded (incident + fix)

The prior turn force-pushed `54b2fc6ab` over `3a447b553`, dropping the
template fix (self-gate recipes hoisted out of the standalone `{% else %}`
branch). This turn recovered it by `git merge --no-ff 3a447b553` →
`9c503e16a`, then committed fmt residue + regenerated projection →
`0d29f44ee`, and fast-forward-pushed. Lesson recorded in the bead: never
rebase/force a shared lane; recover exclusives by no-ff merge.

## Gate State

| Gate | State | Evidence |
|---|---|---|
| `make setup` | GREEN | exit 0, full log /tmp/setup.log |
| `make gen` | GREEN | exit 0, fixed-point verified (/tmp/gen8.log) |
| `make gen` | RED → fixed at owner, re-run pending | flext-infra RUF059 + import order + ISC004 fixed in `0d29f44ee`; full fleet fmt not yet green in one run |
| `make gen` | NOT RUN this session | — |
| `make gen` | NOT RUN | — |
| `make test` | NOT RUN | no historical results count (operator directive) |

## PRs

- flext-infra #665, #666: pre-landed locally in `f2f4b526d`/`44ffee13b`
  (no-ff merges). Remote PR objects still OPEN — close/merge via gh in the
  PR-landing pass, do not assume equivalence.
- flext-ldif #96: MERGED via gh (`c6231b6f`).
- flext-api #83, #84: OPEN, MERGEABLE, CI red at `make setup` bootstrap
  (fleet-wide blocker `flext-cpkk`/`flext-5k9r7`, not caused by the PRs).
  Pending decision: merge after fleet setup is green.
- Root repo: 0 open PRs.

## Immediate TODO (next turn)

1. `make gen` full fleet — expect green on root+infra; fix any
   remaining member at root cause (no suppression).
2. `make gen`, then `make gen` (ruff/pyrefly/pyright/
   mypy/duplication/WAZA) — fix at root cause; structlog/Meltano constraint
   conflicts go to `config/codegen.yaml`, never --no-deps/override.
3. `make test` through canonical testmon on all 32.
4. Land infra PRs #665/#666 via `gh pr merge --merge`; decide #83/#84.
5. Merge `origin/0.12.0-dev` into release lane (no-ff) if base moved.
6. Version (`make release-*`), publish (`make publication INDEX=Y`),
   clean-install verify, close acceptance Beads, delete release worktree
   after remote proof.

## Environment Warnings (do not repeat)

- `make gen` was OOM-killed once (exit 137) mid lazy-init, leaving stale
  `.state/mise-artifacts/transaction-*` trees that fail closed on rerun.
- `git submodule update` resets every gitlink to its committed SHA — never
  use it after a checkpoint gitlink change; checkout the single submodule.
- Detached-HEAD commits: always confirm the branch ref before push
  (this session fast-forwarded `release/checkpoint-0.12.0` to the intended
  tip instead of rebase/force).
- Piping to `tail` discards the Make exit code — capture full output.
- `uv run --project` without `--no-sync` resynchronizes the shared venv.
