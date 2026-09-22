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
