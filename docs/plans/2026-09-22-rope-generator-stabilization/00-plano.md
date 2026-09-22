# Plan — Stabilize worktree, clone for generator validation, evolve generators

Date: 2026-09-22. Approved by the operator in this session. Top priority: short,
functional increments close to `origin/0.12.0-dev`; each increment is integrated only
after green validation plus proof on the integrated SHA. No increment starts while the
previous one is unintegrated or red. Companion findings: `01-achados-worktree.md`,
`02-achados-codegen.md`, `03-achados-make-clone.md`.

## Step 0 — Record the plan markdowns (first action after approval)

This directory. Kilo manifest untouched; dated-plan convention followed; English per
repository law.

## Increment 1 — Stabilize the current worktree (full WIP adoption)

Work in `/home/marlonsc/flext-worktrees/rope-recovery-20260921`, preserving and
adopting all WIP.

1.1 Re-read the live state (never assume the handoff is current); review and stage
    resolutions hunk by hunk for the regenerated-but-unstaged files and the text
    conflict (`docs/ways-of-working/worker-lane-contract.md`). No blanket ours/theirs;
    no `git add -A`.
1.2 Implement the transactional fresh-process verification in the existing owner
    (`codegen/_conform/execute.py::_validate_managed_fixed_point`,
    `codegen_transaction.py::commit_locked`, `validate/fresh_import.py`): typed
    expected publication carried from LazyInitPlan; public contracts resolved in a
    fresh process; real declared entrypoints (`module:attribute`) loaded without
    executing main or re-invoking generation; imported origins proven to belong to
    this worktree; fail-fast with full causal stdout/stderr while rollback is still
    possible; real consumers checked, not only planned names. Run the regression
    `tests/unit/codegen/lazy_init_alias_inheritance_tests.py` through the canonical
    gate; fix the known unused `Annotated` residue in `codegen/lazy_init.py`; prove
    fresh-process bootstrap (the `r` alias from `flext_cli` resolves).
1.3 Conclude the merges of the 17 members holding `MERGE_HEAD` (no-ff, hunk by hunk;
    for the four whose MERGE_HEAD diverges from the superproject "theirs" gitlink —
    flext-auth, flext-oracle-oic, flext-plugin, flext-target-ldap — reconcile against
    the live published tip); flext-tests last, carefully (37 unmerged / 78 dirty).
    Checkpoint per member with explicit-path commits.
1.4 Conclude the superproject merge: resolve the 31 gitlinks to the stabilized member
    tips plus the doc; record a reproducible checkpoint (member SHAs + gitlinks +
    superproject SHA) in this file.
1.5 Gates: full canonical cycle from the root (`make setup gen mod gen gen fix fmt
    check test build`) plus applicable docs/link and public-runtime validation; prove
    repeated `make gen`, `make fix`, `make fmt` are no-op exit-0 on the unchanged
    candidate. Fix every failure at its owner, including pre-existing ones.
1.6 Only then: publish members first (fast-forward pushes), then the superproject
    gitlinks, per the recorded authorizations (known PRs: flext #263, flext-infra
    #798, flext-cli #184, flext-dbt-oracle #107, flext-dbt-oracle-wms #107,
    flext-tests #121, flext-web #99). Green exact-head CI; re-prove the integrated
    SHA.

## Increment 2 — Clone as the generator test bed

2.1 `git clone --no-hardlinks` the stabilized worktree to
    `/home/marlonsc/flext-worktrees/rope-generator-validation-20260922` (if it already
    exists, inspect and preserve before using); per member
    `git submodule update --init --reference /home/marlonsc/flext/.git/modules/<member>`
    so local-only member commits resolve; verify `git submodule status` matches the
    checkpoint.
2.2 `make setup` in the clone with `UV_PROJECT_ENVIRONMENT` and `VIRTUAL_ENV` pinned
    to the clone's `.venv` on every command; own venv and caches; no shared mutable
    state with the worktree or the main checkout.
2.3 Prove isolation: imports, editable dependencies and tools resolve the CLONE's
    files (canonical fresh-import validation; never accidentally the original
    worktree).
2.4 Use the clone for real migrations, regeneration, failure drills and idempotency
    over the full project structure. Transport each candidate as identified commits;
    commit test alterations and evidence before updating the clone; never keep a
    divergent implementation in it.

## Increment 3 — Evolve templates and refactoring (dependency-closed batches)

3a. One real family complete: absorb existing facet bodies into separate internal
    sources; public modules become complete projections without editable duplication.
    Templates control the generation mark, docstrings, future import, imports, public
    composition, aliases, singletons and the trailing `__all__`. Names, bases,
    dependencies and exports derive from the SSOT and dependency contracts (ADR-018:
    derive, never list; ADR-014 §3b: gen is the only writer, pure render,
    transactional publication reused). Incompatible modules are fixed at the source —
    the generator is never loosened, no suppressions, no old paths preserved. Public
    behavior, singleton identity and entrypoints preserved; consumers updated in the
    same increment. Validate in the clone: absorption, behavior preservation, imports,
    exports, MRO, entrypoints, homonyms, collisions, legitimate SSOT changes; drill
    publication failures and concurrent changes proving transactional diagnosis and
    recovery without work loss; canonical cycle from the root in the clone AND
    revalidation of the SAME candidate in the delivery worktree; absorb integration,
    publish members before gitlinks; green CI; proof on the integrated SHA.
3b. Global configuration-vs-settings separation: eliminate incorrect inheritances and
    workaround methods per ADR-016 (singleton lifecycle owned by classmethods; alias
    identity = classmethod identity; pollution-free derived copies); consumers updated
    in the same increment; same validation ritual.
3c. Remaining facets and interfaces (`base.py`, `cli.py`, `api.py`, remaining
    families) in closed batches. `make mod` division: sed (CSV lists) for unambiguous
    textual renames; Rope for movements, symbol identity, references, inheritance,
    collisions and structural corrections.

## Cross-cutting rules

- **Operator law (2026-09-22, mid-execution):** never fight the generator, formatters
  or auto-fixers — their output is canonical code; accept it. If they surface problems,
  fix the ROOT CAUSE instead of arguing with them. Findings produced by flext-infra
  gates (`make check`) are not hand-fix targets: they must remain WARNINGS that do not
  block CI; only automatic fixes apply.
- Commands always through the active workspace root; never bare
  `uv`/`ruff`/`pyrefly`/`mypy`/`pyright`/`pytest`; mypy never uncapped.
- No rebase/force-push/reset/checkout-restore/stash-clean discards; explicit-path
  commits; fix-forward adoption of concurrent WIP.
- Never hand-edit generated files (cure = `make gen`); no `# type: ignore`/`# noqa`
  without documented justification; no compat surface, shims or dual paths.
- Record per increment: commands, directories, exit codes, decisive results (this
  file and the commits).
- Final delivery requires: generators working in BOTH the worktree and the clone,
  full coverage of the planned modules (`_settings.py`, `_config.py`, `constants.py`,
  `typings.py`, `protocols.py`, `models.py`, `utilities.py`, `base.py`, `cli.py`,
  `api.py`), whole integration green, no discarded WIP, no hidden failures.

## Execution log

Appended below as increments land (command, cwd, exit code, decisive output).

### 2026-09-22 — Step 0

- Plan and findings markdowns recorded in this directory (this commit's scoped paths).

### 2026-09-22 — Increment 1 (stabilization, executed with the parallel coordinator lane)

- Fresh-import transactional verification: already wired in the worktree flext-infra at
  plan time — `validate/fresh_import.py` (fresh subprocesses, `EntryPoint.load`, origin
  checks, full stdout/stderr), invoked by
  `codegen/_conform/execute.py::_validate_managed_fixed_point` (stage
  `verify-fresh-imports`, publications from the LazyInitPhase analysis) inside
  `codegen_transaction.py::commit_locked` (validator runs before journal commit, with
  `_recover_failure` rollback available). The unused `Annotated` residue in
  `codegen/lazy_init.py` no longer exists. Fleet-gate run of the regression remains
  part of the canonical cycle (Increment 1.5, coordinator lane).
- Text conflict `docs/ways-of-working/worker-lane-contract.md` resolved as a union
  (theirs reformat + ours canonical-skill paragraph + ours link style); staged.
- Member merges concluded on `recovery/rope-automation-20260921` (16 by this session:
  tap-ldap `745cc8d`, tap-ldif `e36c963`, tap-oracle `535c301`, target-ldap `58d0e69`,
  target-oracle `62e6de2`, target-oracle-oic `61e4f13`, dbt-oracle `af96c7d`,
  dbt-ldap `a774e7e`, dbt-ldif `af22124`, ldap `abfd1e62`, oracle-oic `f4f58b7`,
  dbt-oracle-wms `f7add87`, web `eee34a6`, auth `980ca79b`, plugin `f0197d8`,
  quality `2e5c8e4e`; conflict-marker resolutions in plugin/quality `__init__.py`
  took the ours shape consistent with each file's own `__all__`/`_LAZY_IMPORTS`;
  tests and core converged with the parallel lane: tests `2eb1ffa`/`fcb5977`,
  core `890fdb653` + WIP adoption commit `99fb2032a` — 17 files, +261/−163).
- Superproject absorb concluded by the coordinator lane as `115fe8d8cb` (includes this
  session's staged doc resolution, CSV rename engine, custom.mk, plan docs, gitlinks)
  plus alignment commit `8dfe0ddb0e`. All 31 members hold no `MERGE_HEAD` and carry the
  origin gitlink of `1e59a9d493` as ancestor.
- Reproducible checkpoint: superproject `8dfe0ddb0e`
  (`chore(submodules): update gitlinks after alignment merge 20260922`) with its 31
  recorded gitlinks; member branch tips keep advancing with the coordinator lane's
  cycle (origin tip observed moving to `1511f1e873` during this work — the treadmill
  continues; the checkpoint stays the clone basis and is refreshed by no-ff merges).

### 2026-09-22 — Increment 2.1 (validation clone)

- `git clone --no-hardlinks /home/marlonsc/flext-worktrees/rope-recovery-20260921
  /home/marlonsc/flext-worktrees/rope-generator-validation-20260922` → HEAD
  `8dfe0ddb0e`, clean.
- Per member `git submodule update --init --reference
  /home/marlonsc/flext/.git/modules/<member>` → 31/31 OK, 0 dirty;
  `git submodule status` SHAs == `git ls-tree HEAD` gitlinks (diff empty).
- `make setup` started in the clone with `UV_PROJECT_ENVIRONMENT` and `VIRTUAL_ENV`
  pinned to the clone's `.venv` (evidence appended after completion).
- `make setup` completed exit 0: CPython 3.13.11, `.venv` created in the clone,
  286 packages resolved, every member built editable from
  `file:///home/marlonsc/flext-worktrees/rope-generator-validation-20260922/<member>`
  (log `/tmp/clone-setup.log`, session run 2026-09-22). Scratch/mise state mirrors the
  clone path (`.../rope-generator-validation-20260922/scratch/...`) — no shared mutable
  state with the delivery worktree.

### 2026-09-22 — Increment 2.3 (isolation + fresh-import gate; entrypoint cure)

- First `make gen` in the clone failed at the manifest-origin precondition (clone
  `origin` was the local worktree path). Fixed by `git remote set-url origin
  https://github.com/flext-sh/flext.git` + `git remote add lane <delivery worktree>`
  (members already pointed at GitHub; transport flows through `lane` fetch + no-ff).
- Second `make gen` (exit 1) reached `stage=verify-fresh-imports` and failed loud,
  exactly as designed, at the first broken entrypoint:
  `flext_api: console_scripts/flext-api=flext_api.cli:main` →
  `AttributeError: module 'flext_api.cli' has no attribute 'main'`. Fleet survey
  found 15 members whose declared console scripts did not resolve: missing `cli.py`
  (db-oracle, dbt-ldap, dbt-ldif, ldap, oracle-oic, oracle-wms, target-ldap, cli),
  facade/empty `cli.py` without `main` (api, auth, grpc, observability, plugin,
  ldif), and stale hand-edited pyproject targets (auth `cli_new:cli` module that
  does not exist; tap-oracle `tap:cli` attribute that does not exist).
- Cure at source, delivery worktree, one explicit-path commit per member
  (`fix(cli): restore the declared console-script entrypoint`): minimal canonical
  `main` following the healthy fleet idioms (dbt-oracle no-commands shape;
  tap-oracle bridges both singer names to the real `tap.run_cli`); auth restored
  the single canonical `flext_auth.cli:main` (dropping the broken `cli_new`
  primary and the legacy duplicate).
- Transported to the validation clone: per-member `lane` remote + fetch + no-ff
  merge (`merge: transport stabilized cli entrypoint cures from the delivery
  lane`), 15/15 OK. `make gen` re-run evidence appended below.
- gen-3 (exit 1): entrypoints fixed, all 32 conforms OK; new loud failure at
  `lazy-init public export ownership is ambiguous: 2 collision(s)` — my new
  `cli.py:main` collided with pre-existing `main` owners in flext-oracle-oic
  (`main.py`) and flext-target-ldap (`target.py`). Single-owner cure: removed
  those two `cli.py` files and pointed the pyproject scripts at the existing
  owners (`flext_oracle_oic.main:main`, `flext_target_ldap.target:main`;
  precedent `target-ldif-legacy = flext_target_ldif.tap:main`). Transported,
  gen-4.
- gen-4 (exit 1): fresh-import advanced to `flext_core` and failed with
  `module 'flext_core._lazy_parts' has no attribute 'FlextLazy'`. Root cause:
  `_lazy_parts/flextlazy_part_01.py` declared a stub class named `FlextLazy`
  (also in its `__all__`) while `flextlazy_part_02.py` declares the real
  composed `FlextLazy` importing the stub ALIASED as `FlextLazyPart01` — the
  alias-instead-of-hoist anti-pattern (ADR-014). The strict/total init composer
  saw the sibling `FlextLazy` collision and rendered an EMPTY
  `_lazy_parts/__init__` export surface. Cure at source (flext-core commit
  `4224e3371`): part_01 class renamed to `FlextLazyPart01` (family part name),
  its `__all__` updated, part_02 imports it without the alias. Transported,
  gen-5.

