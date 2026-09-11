# Continuation Prompt — P0 Generic `make setup`, AI Hub/FLEXT Ownership

Continue the active P0 hotfix. Do not restart discovery from zero and do not
silently narrow the operator contract.

## Operator outcome

Make `make setup` sufficient to bootstrap and repair any managed cloned project:

- workspace or standalone;
- internal or external;
- workspace members automatically initialized from typed topology and installed
  into the workspace `.venv` as editable packages;
- third-party forks and `content_only` Gitlinks never initialized, mutated,
  formatted, linted, conformed, or gated;
- complete config-owned development toolchain provisioned through Mise, including
  canonical upstream Beads where policy enables it;
- idempotent repair of missing/stale generated files, managed checkouts, tools,
  virtual environment, and installed packages;
- a healthy second run must be fast, produce zero Git drift, preserve the existing
  `.venv`, and avoid reinstalling unchanged packages.

The newest ownership clarification is **AI Hub**:

- AI Hub is the universal authority for binary installation and distribution.
- FLEXT owns FLEXT-domain generated setup behavior through
  `flext-infra` config/schema/models/conform/templates.
- Do not create two installers, two catalogs, or two `.mise.toml` writers.
- First prove the exact boundary from live sources and existing Beads; then change
  the canonical owner(s) in separate atomic lanes if both repositories need edits.

## Mandatory authority and tools

Before mutation, read completely:

1. `/home/marlonsc/.agents/UNIVERSAL_CORE.md`
2. `/home/marlonsc/.agents/skills/inviolable-rules/SKILL.md`
3. `/home/marlonsc/.agents/skills/flext-law/SKILL.md`
4. `/home/marlonsc/flext/AGENTS.md`
5. `/home/marlonsc/.ai-hub/AGENTS.md` before any AI Hub mutation
6. active Beads and this handoff

Use:

- `ast-grep` for structural discovery and repeated rewrites;
- Code Review Graph **only through the CLI**
  `/home/marlonsc/flext/.venv/bin/code-review-graph`;
- LSP/MCP may be used, but never the Code Review Graph MCP;
- canonical root `make` verbs for setup, generation, tests, formatting, lint,
  static analysis, types, and validation;
- `rtk` prefix for shell commands.

Never reset, restore, checkout away, clean, stash, rebase, force-push, or overwrite
unknown WIP. Never hand-edit generated projections. Never use
`--ignore-schema-skew`.

## Active FLEXT lane

- Repository: `flext-sh/flext-infra`
- Worktree:
  `/home/marlonsc/flext/.worktrees/mro-z89e-2-2-bd-mise`
- Branch: `hotfix/mro-z89e-2-2-bd-mise-1-1-2`
- HEAD/base:
  `a5db193922000e76e036931cae857e073115ffc1`
  (`origin/0.12.0-dev`)
- Active Bead: `mro-z89e.2.2`
- Parent: `mro-z89e.2`
- Related: `mro-d9d5`, `mro-wkii.17.41`

Run first:

```bash
rtk bd show mro-z89e.2.2 --json
rtk git status --short --branch
rtk git diff -- \
  tests/unit/basemk/test_renderer.py \
  tests/unit/codegen/test_codegen_catalog_extensions.py \
  tests/unit/codegen/test_codegen_make_environment.py \
  tests/unit/workspace/test_sync_environment.py
```

Current lane state: only the four test files above are intentionally modified.
No production code has been changed.

## Existing RED evidence

All commands ran from the active FLEXT lane through root Make:

1. `make test FILE=tests/unit/codegen/test_codegen_catalog_extensions.py MATCH=immutable`
   - exit `2`
   - failed because `beads_version` is `latest`, not an immutable release selector
   - report: `.reports/tests/20260729T184810Z-2533649`
2. `make test FILE=tests/unit/codegen/test_codegen_make_environment.py MATCH=generated_setup_is_self_contained`
   - exit `2`
   - generated Make lacks Mise installation
   - report: `.reports/tests/20260729T185406Z-2570963`
3. `make test FILE=tests/unit/workspace/test_sync_environment.py MATCH=conform_is_the_only_mise_writer`
   - exit `2`
   - legacy `sync_mise_toml` is still a duplicate writer
   - report: `.reports/tests/20260729T185456Z-2574664`
4. `make test FILE=tests/unit/basemk/test_renderer.py MATCH=bootstrap_setup_is_self_contained`
   - exit `2`
   - standalone bootstrap lacks Mise installation
   - report: `.reports/tests/20260729T185550Z-2581866`

These are legitimate RED tests. Re-read them before extending them. Config-owned
versions must not be hardcoded in tests; derive expectations from the same typed
SSOT or prove generator/consumer round trips.

## Known canonical sources and defects

FLEXT:

- `config/codegen.yaml`
  - `beads_version: latest`
  - typed toolchain and Make profiles are the canonical FLEXT codegen SSOT.
- `src/flext_infra/templates/project/base/.mise.toml.j2`
  - generated selector already uses
    `github:gastownhall/beads` conditionally.
- `src/flext_infra/templates/project/base/Makefile.j2`
  - current setup runs submodule reconciliation, conform, `uv venv --clear`,
    `uv sync`, and `uv pip check`;
  - it does not run Mise;
  - clearing `.venv` on every run violates repair/idempotence/fast-path.
- `src/flext_infra/templates/makefile_bootstrap.mk.j2`
  - standalone bootstrap also clears `.venv` and lacks Mise.
- `src/flext_infra/environment.py`
  - `sync_environment_files` calls both `.envrc` and legacy `.mise.toml`
    synchronization;
  - `sync_mise_toml`, `render_mise_toml`, `merge_custom_mise_toml`, and
    `mise_tool_selectors` duplicate conform ownership.
- Legacy callers:
  - `src/flext_infra/workspace/_sync_artifacts.py`
  - `src/flext_infra/workspace/_migrator_artifacts.py`
- Legacy template:
  - `src/flext_infra/templates/workspace_mise.toml.j2`

AI Hub:

- `src/ai_hub/services/workspace_base/environment.py`
  delegates environment generation to
  `u.AiHub.sync_environment_files`, implemented by FLEXT.
- `src/ai_hub/services/workspace_base/distribution.py`
  owns universal governed-workspace distribution/orchestration.
- `src/ai_hub/services/install.py`,
  `src/ai_hub/services/install_packages.py`, and
  `src/ai_hub/services/ensure_venv.py`
  own universal AI Hub installation behavior.
- `config/tools.yaml`, `config/products.yaml`, and `config/workspaces.yaml`
  are typed AI Hub policy inputs.
- AI Hub currently has tests that expect its workspace distribution to write
  `.mise.toml` through the FLEXT legacy sync route:
  `tests/unit/test_aihub_distribute_workspace_base.py`.

Do not assume the correct cutover. Prove whether AI Hub should distribute a
config/catalog input consumed by conform, or whether FLEXT project-local selectors
remain wholly FLEXT-owned while AI Hub owns only installation/runtime. The final
design must have one owner per fact and no runtime dependency on an unavailable
local AI Hub clone in a virgin external project.

## AI Hub tracker and dirty state

Relevant read-only Beads found:

- `ai-hub-iwqv.1.1`
  - P0, in progress;
  - standalone `make setup` loses `ai-hub` before `hooks-runtime`.
- `ai-hub-qtka.1`
  - P0 delivery adoption of Beads through Mise;
  - currently blocked by `ai-hub-t2p6`.
- `ai-hub-t2p6`
  - records upstream compatibility:
    stable official `v1.1.2` supports schema through v53, while the live ledger is
    schema v61; official upstream HEAD is currently schema-compatible.

The operator nevertheless explicitly requires official `1.1.2` and recovery of
all Beads databases into shared Dolt mode. Therefore:

- never let `1.1.2` write schema v61 with `--ignore-schema-skew`;
- preserve immutable backups;
- export with the schema-compatible current binary and import into a fresh
  official-1.1.2-compatible database when executing recovery;
- do not restore a v61 physical backup into v53;
- keep database recovery as an explicit, evidenced stage after the setup owner is
  fixed.

Current `/home/marlonsc/.ai-hub` checkout is dirty on `main`:

- modified `AGENTS.md`;
- untracked `.beads/dolt-backup-state.json`;
- untracked `.beads/dolt-backup.json`;
- untracked `session-ses_0521.md`.

These paths are foreign WIP. Do not mutate AI Hub on this checkout. If AI Hub code
must change, update/claim the correct AI Hub Bead, create a dedicated branch and
worktree from the configured development ref, and preserve these paths.

## Required test contract before production code

Complete RED coverage for:

1. Virgin standalone:
   `make setup` exits `0`, provisions selectors/tools, creates a valid `.venv`,
   syncs all groups/extras, and imports the project.
2. Virgin workspace:
   root topology is conformed before submodule selection; only typed managed
   Gitlinks initialize; all managed packages appear as editable installations;
   content-only Gitlinks stay untouched.
3. Repair:
   a missing/stale managed checkout, generated selector, tool, or installed venv
   package is repaired by the next `make setup` without destructive Git actions.
4. Fast healthy rerun:
   two consecutive runs exit `0`; the second has zero Git drift, does not execute
   `venv --clear`, does not reinstall unchanged packages, and has recorded timing.
5. Ownership:
   conform is the sole FLEXT `.mise.toml` writer and official Beads is selected
   only where topology policy enables it.

Prefer extending these existing fixtures/tests:

- `tests/unit/codegen/test_codegen_make_environment.py`
- `tests/unit/codegen/test_codegen_setup_submodules.py`
- `tests/unit/codegen/test_workspace_root_setup_submodules.py`
- `tests/unit/workspace/test_workspace_root_make_contract.py`
- `tests/unit/workspace/test_sync_environment.py`
- `tests/unit/basemk/test_renderer.py`
- existing uv workspace/editable-plan tests

Before implementing, remove positive expectations for `venv --clear`, add
forbidden assertions, add a fake Mise executable to isolated command fixtures,
and add the two-phase ordering contract:

```text
root conform -> managed Gitlinks -> full conform -> mise install -> uv sync -> validation
```

Run every RED through `make test FILE=... MATCH=...`; record exact report
directories in the Bead.

## Likely complete implementation shape

Validate this against live code and background audit evidence before editing:

1. Bootstrap canonical `flext-infra` without requiring the target `.venv`.
2. Conform only the root topology projection first when needed, so a virgin
   workspace obtains typed Gitlink ownership markers.
3. Initialize/reconcile only managed first-party Gitlinks.
4. Conform root and managed members fully.
5. Install the generated project-local Mise selectors idempotently.
6. Run `uv sync` against the workspace root with all packages, groups, and extras,
   or against the standalone project.
7. Run environment/package validation.
8. Never clear a healthy `.venv`; let `uv sync` create or repair it.
9. Use a canonical fingerprint/state comparison only if measured profiling proves
   conform dominates the second run; do not add brittle timestamp stamps.
10. Remove the legacy duplicate `.mise.toml` writer and migrate every consumer in
    the same cycle.

## Fleet and exclusions

Prior read-only inventory found 39 managed repositories:

- FLEXT workspace root plus 31 members;
- `cosmos-main` plus 2 managed members;
- four standalone roots:
  `.ai-hub`, `cosmos-docgen`, `algar-oud-mig`,
  `gruponos-meltano-native`.

Fourteen Gitlinks are immutable exclusions:

- ten `cosmos-main` `content_only` entries;
- four vendored/data submodules under `cosmos-docgen`.

Do not claim fleet completion from samples. After the hotfix is reviewed and
published, run rollout serially, one root/worktree/branch at a time, recording
exact command, cwd, exit, duration, Git drift, editable-package proof, and excluded
Gitlink proof.

## Validation and landing

After final edits, run from the active FLEXT lane:

```bash
rtk make setup
rtk make setup
rtk make check CHECK_GATES=lint,format,pyrefly
rtk make check CHECK_GATES=pyright,mypy
rtk make test
rtk make codegen WHAT=check
```

Use narrower `FILE=`/`MATCH=` checks while iterating, but do not use them to evade
the final gates. Exercise real local Git clone fixtures with real `make setup`,
actual `uv`, editable-install metadata, and measured second-run timing. Prove
generated fixed point after the last edit.

Before each commit:

```bash
rtk git log --oneline -20
rtk git log -5 -- <each-touched-path>
rtk git diff --cached --stat
```

Stage only explicit owned paths. Commit one complete green increment, push the
worker branch fast-forward, update the Bead with SHA/evidence, and open/update the
linked PR. Do not merge or promote `main` without explicit operator confirmation.
Because this is a multi-file P0 refactor, obtain a high-rigor read-only review
against the live diff and scenario evidence before declaring completion.

## Immediate next action

1. Re-read both repositories and relevant Beads.
2. Collect or reproduce the AI Hub/FLEXT ownership audit.
3. Complete the missing RED tests without production edits.
4. Run each RED through root Make and append evidence to `mro-z89e.2.2`.
5. Implement the smallest complete owner cutover.

Stop only when the actual observable setup problem is solved and all declared
gates, real surfaces, rollout evidence, tracker sync, commit/push, and review are
complete.
