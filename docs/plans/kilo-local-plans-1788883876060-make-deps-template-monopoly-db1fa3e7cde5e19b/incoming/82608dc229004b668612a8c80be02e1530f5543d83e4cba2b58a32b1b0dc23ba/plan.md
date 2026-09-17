# Remaining: gen green, FilePlan cutover, one bypass per SHA

Landed on `origin/0.12.0-dev` (not done): flext-infra `4a3003b95`, flext gitlink `bfca036f4`.

## Done (do not redo)

- `FlextInfraMiseLock` / `MiseToolchainLockLease` gone. `run_locked` has no HEAD flock.
- `toolchain.mise_lockfile` / `mise_locked` = false. `.mise.toml` has `[settings] lockfile=false` and `[tool_config] locked=false`.
- Beads/gascity `track: release`, `version: latest`, `prerelease: true`. Selectors for qlty/scc/waza/jscpd live in `codegen.yaml`.
- Beads ledger scalars (`dolt_mode`, `export_auto`, …) in YAML. Template emits `issue_prefix` only.
- `write_publication(*, backup=)`. Recovery `backup=False`. `_codegen_file_staging.py` deleted.
- `make deps` SSOT-only; `make gen` renders pyproject / `.mise.toml`.

## Not done (this plan)

Last `make gen` at `~/flext`: 32/32 conform OK, published `.beads/config.yaml`, then exit 2 `generation journal changed between phases` (`codegen_transaction.py` `append_phase_locked` vs lazy-init). Live `.beads/config.yaml` still has `issue-prefix:` appended by bd. SHA 3–4 writers still call `u.Cli.atomic_write_text_file` / `files_write_text` directly.

## Operator locks (unchanged)

- No hardcoded generator scalars. YAML comments: what / which projection / how to overlay / never edit the projection.
- Mise GitHub forks: `track: release` → always `latest`; `track: branch` → `branch` required, no default `main`, no SHA pin.
- One live writer: `planned_file` → `CodegenFilePlan` → journal v8 (gen only) → `write_publication(*, backup=)` → `u.Cli.atomic_*`.
- No `FileEffect*`, no observer bus, no second journal, no `mise.lock`.
- `.beads/config.yaml` is template SSOT (not skip). Second `make gen` must be a no-op on it.
- Landing: `origin/0.12.0-dev`, `git merge --no-ff` if behind, FF push. No rebase/force.

## SHA order (gen green after each)

### A — Unblock `make gen` (required before 3)

`append_phase_locked` fails because the on-disk journal bytes ≠ `session.journal_state` after conform publish, before lazy-init.

1. Prove the mutation: which path, which process (bd vs lazy-init vs a second gen). Do not guess.
2. Stop that owner from rewriting the journal or `.beads/config.yaml` mid-transaction. Gen must not invoke `bd`.
3. Hyphen `issue-prefix:` stays deleted in the template. If bd appends it after gen returns, that is a post-gen dirtiness defect: keep bd out of the verb; policy `full` overwrite on the next gen must restore template bytes **inside** the same apply, before verify.
4. Proof: `make gen` then `make gen` at `~/flext`. Second run: no beads residual, no journal error. Exit 0.

### B — SHA 3: three codegen writers → FilePlan

Same apply transaction. Delete the direct write in the same change.

| Site                           | Today                        |
| ------------------------------ | ---------------------------- |
| `codegen/scaffolder.py`        | `atomic_write_text_file`     |
| `codegen/version_file.py`      | `atomic_write_text_file`     |
| `codegen/_layout_gitignore.py` | two `atomic_write_text_file` |

Proof: those modules have no `atomic_write_text_file` / `files_write_text`. `make gen` still green.

### C — SHA 4+: one remaining bypass per SHA

Not a dump. Classify first; only rewire if it is a managed projection or live source rewrite.

**Stay off-journal (do not rewire):** `.reports/`, pytest/cProfile, jscpd tmp (`gates/duplication.py` config tmp), `validate/_pytest_runner/*`, `check/_workspace_check_reports.py`.

**Next candidates (one SHA each, gen still green):**

1. `codegen/constants_quality_gate.py` — if those files are managed; else leave as reports.
2. `deps/_floor_profile_writer.py` — SSOT `codegen.yaml`; still `planned_file` + `write_publication`, not a second YAML writer.
3. `workspace/environment.py`
4. `maintenance/python_version.py`
5. Live rewrites (`codemod/semantic_apply.py`, `refactor/modernize_orchestrator.py`, `fixers/transformer_fixer.py`) through a short-lived journaled transaction, fmt still Make after commit.

Stop each SHA at one module. Fail-loud if a bypass of that class remains.

### D — Hardcodes still in the table

Only if still present after A–C (read before editing):

- `"flext_cli"` in `_project_spec_from_existing` → first matching `dependency_profiles.upstream`.
- Nested `MiseToolSpec` for qlty/waza/scc if selectors+versions are still parallel fields.
- Branch-track tools: none until the operator names `branch:` in YAML. Do not default `main`.

## Validation

```text
make gen
make gen
```

cwd `~/flext`. Both exit 0. Second: `.beads/config.yaml` unchanged vs re-plan; no `issue-prefix:`; `.mise.toml` still `latest` / `lockfile=false`; no `mise.lock`; no `FlextInfraMiseLock`.

Do not claim 31-member `make test` or ai-hub gen unless A is green.

## Landing

flext-infra first, then root gitlink. `git merge --no-ff origin/0.12.0-dev` if behind. FF push. Integration branch is `0.12.0-dev` (repo default — no side PR unless a lane exists).

## Exclusions

Observer bus, `FileEffect*` models, pinning SHAs, Helm parallelization, skipping `.beads/config.yaml`, rewriting `u.Cli.atomic_*` signatures.
