# Findings — Make surface, environment and clone mechanics

<!-- TOC START -->

- [1. Canonical verb surface](#1-canonical-verb-surface)
- [2. Environment isolation (per-lane venv)](#2-environment-isolation-per-lane-venv)
- [3. Clone mechanics for the validation environment](#3-clone-mechanics-for-the-validation-environment)
- [4. Checkpoint reproducibility (a clone cannot carry uncommitted work)](#4-checkpoint-reproducibility-a-clone-cannot-carry-uncommitted-work)

<!-- TOC END -->

Date: 2026-09-22. Sources: live read-only inspection of the worktree root `Makefile`,
`custom.mk`, `.gitmodules`, `config/workspace.yaml`, `config/codegen.yaml` toolchain
section, and the handoff note.

## 1. Canonical verb surface

- All verbs run from the workspace root, never inside members. Root `Makefile` targets
  (`gen`, `mod`, `setup`, `deps`, `build`, `check`, `test`, `fmt`, `fix`,
  `fix-enforcement`, `initialize`, `waza`, `duplication`, ...) dispatch through
  `direnv exec "$(PROJECT_ROOT)"` + `RUN_PUBLIC` into the `flext` workspace CLI (thin
  orchestrator over `flext-cli`), which fans out to members. The Makefile itself is
  fully generated (`overwrite: true` from `base/Makefile.j2`); customization lives ONLY
  in `custom.mk` via pre/post hooks — a project never owns a verb.
- `make check` runs the non-test gates (Ruff/Pyrefly/Pyright/Mypy via the configured
  policy, namespace/codemod gates); `make test` runs the suite through the persistent
  testmon cache; `make build` builds distribution artifacts; `make deps` recalculates
  dependency floors; `make gen` runs conform/codegen to the fixed point; `make mod` runs
  the ast-grep + semantic (Rope) modernize circuit to a guarded fixed point.
- Canonical selection rules: never invoke `uv`/`ruff`/`mypy`/`pyright`/`pytest`
  directly; mypy is memory-capped (`MYPY_MEMORY_LIMIT_MB=6144`, 600s) — never uncapped.

## 2. Environment isolation (per-lane venv)

- The Makefile sanitizes the caller's `VIRTUAL_ENV` bin out of `PATH`
  (`CALLER_VIRTUAL_ENV`, `SANITIZED_CALLER_PATH`) before activating its own environment,
  so an inherited wrong venv is removed — but the handoff law is to set BOTH
  `UV_PROJECT_ENVIRONMENT` and `VIRTUAL_ENV` to the lane's `.venv` explicitly for every
  Make invocation in this lane and in the validation clone.
- Scratch/state is checkout-scoped by construction: `codegen.yaml` toolchain keys
  (`state_directory_name: .flext-runtime`, `scratch_home_relative: tmp` mirroring the
  absolute checkout path, `pycache_namespace`, `mise_namespace`, `uv_link_mode: copy`)
  mean the worktree and the clone keep separate runtime state, mise artifacts and caches
  without shared mutable state.
- Toolchain is fleet-unlocked: moving selectors (`uv_version: latest`, ...) resolved by
  mise at setup; no lock commits; `uv_constraint_dependencies: ["structlog<26"]` is the
  one fleet-wide compatibility cap (meltano upstream).

## 3. Clone mechanics for the validation environment

- `.gitmodules`: one entry per member with ABSOLUTE URLs
  (`https://github.com/flext-sh/<member>.git`, branch `0.12.0-dev`). A plain
  `git submodule update --init` in a clone therefore fetches from GitHub and MISSES
  member local-only commits (members are ahead of origin by up to +45 commits at plan
  time).
- Correct procedure (authorized by the 2026-09-22 request):
  1. `git clone --no-hardlinks /home/marlonsc/flext-worktrees/rope-recovery-20260921 /home/marlonsc/flext-worktrees/rope-generator-validation-20260922`
     (destination verified non-existent at plan time; if it appears, inspect and
     preserve its content before use).
  2. Per member:
     `git submodule update --init --reference /home/marlonsc/flext/.git/modules/<member> <member-path>`
     — alternates supply the objects for every locally-recovered SHA; the GitHub URL
     only serves what alternates lack. The member object stores are shared through
     `/home/marlonsc/flext/.git/modules/<name>` (worktree-linked gitdirs reuse the same
     objects), so all checkout SHAs resolve locally.
  3. Verify `git submodule status` in the clone equals the checkpoint recorded by the
     worktree (member SHA list + superproject SHA).
- The clone is an INDEPENDENT repository (not a worktree), same filesystem, outside
  `/tmp` — satisfying the request. Its `.venv` is rebuilt by `make setup` with
  `UV_PROJECT_ENVIRONMENT`/`VIRTUAL_ENV` pinned to the clone's own `.venv`.
- Transport discipline: candidates travel as identified commits (fetch + `--no-ff` merge
  inside the clone, sourced from the delivery worktree or the published remote); test
  alterations and evidence are committed BEFORE updating the clone; the clone never
  carries a divergent implementation.

## 4. Checkpoint reproducibility (a clone cannot carry uncommitted work)

- Before cloning, the worktree must be at a fully committed checkpoint: every member at
  a committed tip (merges concluded, scoped-path commits), superproject gitlinks
  matching those tips, and one superproject commit recording the state. The checkpoint
  evidence (per-repo SHA + `git submodule status` output) is recorded in `00-plano.md`
  as each increment lands.
