# Findings — Worktree state (rope-recovery-20260921)

Date: 2026-09-22. Sources: live read-only inventory (git status/log per repository),
`HANDOFF-ROPE-GENERATOR-2026-09-22.md` (worktree root, ignored file). Nothing was
modified while collecting these findings.

## 1. Lane identity

- Worktree: `/home/marlonsc/flext-worktrees/rope-recovery-20260921` (linked worktree of
  `/home/marlonsc/flext`; gitdir `/home/marlonsc/flext/.git/worktrees/rope-recovery-20260921`).
- Branch: `recovery/rope-automation-20260921` (root and members), HEAD
  `a17f35a1edae05b3a92dd7471941f243e2456cc9` ("[WIP] preserve workspace generation and
  incremental integration contract").
- 13 commits ahead / 21 behind `origin/0.12.0-dev` (origin tip `1e59a9d493`).
- Handoff constraints (operator 2026-09-22): absorb `origin/0.12.0-dev` with
  `git merge --no-ff`; no rebase/force-push/reset/checkout-restore/stash-clean discard;
  no blanket ours/theirs; no unscoped staging; exclusions `main`, `0.20.0-dev`, Dolt
  refs; do not create another checkout/worktree (the validation CLONE requested on
  2026-09-22 is explicitly authorized and is a clone, not a worktree).

## 2. Superproject merge in progress

- `MERGE_HEAD` = `1e59a9d493` (exactly current `origin/0.12.0-dev`), `MERGE_MODE` no-ff,
  `MERGE_MSG` "[WIP] absorb current workspace integration for fleet validation".
- 32 unmerged paths: all 31 `flext-*` gitlinks + `docs/ways-of-working/worker-lane-contract.md`.
- 19 staged entries include the CSV rename engine already byte-identical to origin's
  `9a8f437e31` (`codemod/rules/refactor/apply_renames.py`, `cacophony.csv`,
  `cli-prefixes.csv`, `infra-dedup.csv`, `custom.mk`) plus 10 `src/flext/*.py` WIP files.
- 0 untracked files at root (checked with `-uall`). Ignored artifacts: `.venv`, `uv.lock`,
  `.state`, `.reports`, `.flext-runtime`, `.code-review-graph`, `.benchmarks`,
  `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `mkdocs.yml`,
  `HANDOFF-ROPE-GENERATOR-2026-09-22.md`.

## 3. Member repositories (31)

- 17 members have their own half-finished merges (`MERGE_HEAD` present): flext-auth,
  flext-dbt-ldap, flext-dbt-ldif, flext-dbt-oracle, flext-dbt-oracle-wms, flext-ldap,
  flext-oracle-oic, flext-plugin, flext-quality, flext-tap-ldap, flext-tap-ldif,
  flext-tap-oracle, flext-target-ldap, flext-target-oracle, flext-target-oracle-oic,
  flext-tests, flext-web.
- 4 of those MERGE_HEADs do NOT match the superproject's "theirs" gitlink (needs live
  reconciliation, hunk by hunk): flext-auth, flext-oracle-oic, flext-plugin,
  flext-target-ldap.
- Every member working tree sits at a SHA matching none of base/ours/theirs — these are
  the recovered member-history tips.
- Dirty (entries): flext-tests 78 (37 unmerged), flext-plugin 17, flext-core 16,
  flext-quality 12, flext-auth 5, flext-dbt-oracle-wms 5, flext-web 3, and 2–3 in most
  singer-family members. Clean (0): flext-api, flext-cli, flext-db-oracle, flext-grpc,
  flext-infra, flext-ldif, flext-meltano, flext-observability, flext-oracle-wms,
  flext-tap-oracle-oic, flext-tap-oracle-wms, flext-target-ldif, flext-target-oracle-wms.
- Ahead of origin per member (local-only commits a clone must carry): flext-api +45,
  flext-dbt-oracle +33, flext-dbt-oracle-wms +31, flext-dbt-ldap +31, flext-ldap +18,
  flext-grpc +17, flext-tap-ldap +29, flext-tap-ldif +28, flext-tap-oracle +28,
  flext-target-ldif +29, flext-target-oracle +28, flext-target-oracle-oic +27,
  flext-web +31; smaller ahead counts elsewhere (full table in the inventory session).

## 4. Preserved WIP not in commits

- Stashes: superproject `stash@{0}` (autostash, 9 files, worker-lane-contract +
  tests/infra/{constants,protocols,typings}.py); flext-infra ×4; flext-core ×1;
  flext-quality ×1.
- External patch: `/home/marlonsc/flext-worktrees/rope-modernize-flext-infra-uncommitted.patch`
  (57,836 bytes, 2026-09-16; first hunk: `_conform_gitignore.py` ruff per-file-ignores).
  Evidence only; inspect before adopting.
- Local WIP checkpoints recorded by the handoff: flext-cli `62862b7e`,
  flext-infra `9475df044` (preserve, not green candidates; unpushed at handoff time).
- Unrecoverable objects (operator already authorized reimplementation; do NOT re-search):
  flext-core `46754761...`, flext-dbt-oracle `bcdbb7a5...`.

## 5. Generator state at handoff (2026-09-22 12:37 UTC)

- Last `make gen` in this worktree: exit 0, 32/32 repositories, 150 Dockerfile
  artifacts, 81 initializer effects, fixed-point verify complete (session 57228).
- NOT proven: fresh-process import validity of the newly generated artifacts. A prior
  green generation was followed by `ImportError: cannot import name 'r' from 'flext_cli'`
  (declaration inventory missed owner-module aliases such as `flext_core/result.py`).
- Fixes already implemented in flext-infra source but NOT yet gated:
  `_lazy_init_planner_cache.py` (indexed packages reuse declared aliases),
  relative-import resolution, Rope resource identity for imported-module discovery,
  publication/repair policy separation, TYPE_CHECKING planning alignment; regression
  file `tests/unit/codegen/lazy_init_alias_inheritance_tests.py` exists but has not run
  through the canonical gate. Known lint residue: unused `Annotated` import in
  `codegen/lazy_init.py`.
- Required next implementation (handoff "transactional fresh-process verification"):
  extend owners `codegen/_conform/execute.py::_validate_managed_fixed_point`,
  `codegen_transaction.py` (`commit_locked`), `validate/fresh_import.py` — carry typed
  expected publication from LazyInitPlan, resolve public contracts in a fresh process,
  load real declared entrypoints (`module:attribute`), confirm imported origins belong
  to this worktree, fail fast with full causal stdout/stderr while rollback is possible,
  and check real consumers (not only planned names).

## 6. Adjacent state

- Validation clone `/home/marlonsc/flext-worktrees/rope-generator-validation-20260922`
  did NOT exist when this plan was written (verified).
- Other worktrees: `/home/marlonsc/flext-integration-20260922` (branch
  `integration/beads-20260922`) and `/home/marlonsc/.worktrees/flext-infra-fix-20260921`
  (prunable).
- Main checkout `/home/marlonsc/flext`: branch `0.12.0-dev`, HEAD `daa51e8822`, only
  2 dirty gitlinks (flext-core, flext-tests), no merge in progress.
- Known open PRs (remote state not freshly queried): flext #263, flext-infra #798,
  flext-cli #184, flext-dbt-oracle #107, flext-dbt-oracle-wms #107, flext-tests #121,
  flext-web #99.
