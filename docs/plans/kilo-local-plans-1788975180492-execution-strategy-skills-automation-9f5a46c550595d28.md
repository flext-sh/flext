# 0.12.0 Checkpoint — Strategy v2: Skills & Automation-Accelerated Landing

Created: 2026-09-09 18:50 UTC. Supersedes the execution detail in
`1788961161018-flext-012-checkpoint-release.md` (operator directives there
remain law). Live state:
`1788961161018-flext-012-checkpoint-status.md`.

## Goal

Land the 0.12.0 checkpoint (all PRs, integration with `origin/0.12.0-dev`,
gates green via testmon, version/publish/verify, acceptance Beads closed)
faster by routing recurring work through the canonical automations instead of
hand-edits: `make mod` for mechanical rewrites, manual `code-review-graph`
pre-pass on the release diff, `pr-sheriff` evidence for PR landing, and
per-member subagent triage so the parent context stays lean.

## Learnings → Strategy Shifts (evidence from this session)

| # | Learning (evidence) | Shift |
|---|---|---|
| L1 | `make gen` renders whatever the template says — fixed-point green did NOT catch the self-gate block being inside the standalone branch (`_builtin-self-*` defect, fixed in `9c503e16a`) | After any template change, verify a rendered projection semantically (grep the target set), not only exit 0 |
| L2 | Force-push dropped fix `3a447b553`; recovered only by no-ff merge | Hard law: never rebase/force shared lanes; prove `merge-base --is-ancestor` before every push |
| L3 | fmt residue polluted the checkpoint WIP; clean closure required a second commit | Run `make gen` BEFORE closing a WIP slice; commit once, green |
| L4 | OOM killed `make gen` (exit 137) leaving stale `transaction-*` trees that fail closed | Checkpoint cadence: after every green gate slice, commit+push scoped paths so recovery is a fast-forward, not forensics |
| L5 | PR CI red ≠ PR defect (#83/#84 red at `make setup` = fleet blocker `flext-cpkk`) | Triage PR failures against fleet blockers before judging the PR |
| L6 | Parent context burned on long gate logs; user had to abort | Bounded per-member discovery in subagents; parent only integrates |
| L7 | RUF059/ISC004 violations recurred across members; hand-fixed one file at a time | Recurring violation classes (≥3 sites) become codemod rules; propagate via `make mod` |
| L8 | `make mod` is cwd-scoped and selector-free (`refactor mod --apply`, root Makefile:1061) — safe blast radius per member | Use member-cwd `make mod` as the bulk-fix engine; never raw ast-grep/rope/LSP |

## Automation Map

| Automation | Role in this checkpoint | Guard |
|---|---|---|
| `make gen` | Project every managed surface; fixed-point is the commit precondition | Verify rendered semantics (L1), not just exit 0 |
| `make mod` (member cwd) | Bulk mechanical classes: `pytest.raises` narrowing (RUF059), ISC004 concat, import ordering — ONLY after the private-import cutover guard (bead `flext-sc3ud`, fix `05d48a886` on an unmerged lane) is verified present in the release lane | First run: one member, diff review; if the cutover guard is absent, land that lane first |
| `code-review-graph` (manual, host tool `~/.local/share/ai-hub/host-tools/current/bin/`) | Pre-check structural pass over the release diff (superproject + flext-infra + flext-ldif) before the expensive `make check`: dead code, ownership drift, duplication hotspots | Scope to the checkpoint diff; findings feed `make fix`/`make mod`, never bypass gates |
| `make fix/fmt/check/test` | The only evidence gates; testmon mandatory on every test run | Full output captured (no tail pipes); no invented selectors |
| `code-review` skill (read-only diff review) | Human-grade review of each checkpoint commit before publish | Evidence-backed findings; no approve-by-default |
| `pr-sheriff` + `gh` | PR landing loop: view mergeable/checks → local no-ff merge → gates → push → `gh pr merge --merge` → rerun gates on merged SHA | "mergeable"/open PR is never landed |
| `bd` evidence loop | Append verb/cwd/exit/decisive output to `flext-yirgp` after every merged SHA and gate rerun | No closure claims without it |
| Subagents (explore) | Bounded per-member gate triage; ancestry audits | Parent keeps merge/integration decisions |

## Execution Sequence (gate slices, checkpoint after each green slice)

1. **Sync & bead updates.** Update `flext-yirgp` with the v2 strategy adoption;
   refresh the status file gate table. Verify `flext-sc3ud` cutover guard
   presence in the release lane (`git log --all --oneline --grep=cutover`,
   inspect `private_import_cst.py` guard) — precondition for step 4.
2. **fmt full fleet.** `make gen` to completion (root already green;
   infra fixed in `0d29f44ee`). Fix any member at root cause. Commit+push.
3. **Manual code-review-graph pass.** Build/refresh graph on the release
   worktree; review the checkpoint diff (`origin/0.12.0-dev...HEAD`).
   Triage findings → `make fix` targets or beads. No gate bypass.
4. **fix + mod slice.** `make gen`; for recurring classes surfaced by
   step 3, add/extend the codemod rule at flext-infra, propagate with member-cwd
   `make mod`, regen, re-fmt. Commit+push.
5. **check full fleet.** `make gen` (ruff/pyrefly/pyright/mypy/
   duplication/WAZA). Expected long pole (~1700 known findings, bead
   `flext-hkz4p`): triage per member via subagents; parent fixes root causes;
   structlog/Meltano constraint conflicts go to `config/codegen.yaml` only.
6. **test full fleet.** `make test` through testmon, all 32.
   No historical results count.
7. **PR landing.** `gh pr merge 665 --merge` and `666 --merge` on flext-infra;
   decide #83/#84 (merge only after fleet `setup` green). Rerun affected gates
   on each merged SHA; bead evidence per merge.
8. **Integration.** `git merge --no-ff origin/0.12.0-dev` into the release
   lane; gates on the unified tree; commit+push.
9. **Version/publish/verify.** `make release-*` →
   `make publication INDEX=Y` → clean-install verify from PyPI →
   close acceptance Beads (`flext-y3qpq.5`, `.6`, `flext-1wjg1.11`, `.12`)
   with merged SHA + digests + runtime evidence.
10. **Teardown.** Delete release worktree/branches only after remote proof.

## Doc & Tracking Updates (this plan authorizes; execute in implementation)

- `.kilo/plans/1788961161018-flext-012-checkpoint-status.md`: replace the
  Immediate TODO with sequence steps 2–10; add L1/L2 lessons to the
  environment-warnings block.
- Bead `flext-yirgp`: append the v2 strategy note + L2 recovery law as the
  standing evidence template (verb, cwd, exit, decisive output, SHA).
- No ADR: this is execution-level, not architecture. No AGENTS.md change
  (no law delta).

## Risks & Guards

| Risk | Guard |
|---|---|
| `make mod` cutover bug (flext-sc3ud) corrupts code at fleet scale | Precondition check (step 1); first run scoped to one member with diff review |
| code-review-graph findings become a shortcut around gates | Findings only feed fix targets; `make check/test` remain the sole acceptance gates |
| OOM on gen/check like the observed exit 137 | Slice cadence + stable-tip commits after each green slice |
| Fleet blockers mask PR health | pr-sheriff triage against `flext-cpkk`/`flext-5k9r7` before judging PRs |
| Context blowup in parent | Subagents for per-member triage; parent integrates only |

## Validation

- Every slice ends with: canonical verb exit 0, full log path recorded,
  scoped commit pushed (fast-forward, ancestry-proven), bead evidence appended.
- Acceptance only after steps 5–6 green on the integrated SHA and publication
  verified from PyPI in a clean environment.

## Decisions

- Adopted: member-cwd `make mod` as the bulk-fix engine (L7/L8) with the
  cutover-guard precondition; manual `code-review-graph` as a pre-check
  (not a gate); pr-sheriff for PR landing.
- Out of scope: new ADRs, AGENTS.md law changes, ai-hub/cosmos beads
  (separate epics `flext-mbowt.*`), deleting #83/#84 without a decision.
