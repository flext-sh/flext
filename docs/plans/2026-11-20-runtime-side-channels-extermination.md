# Runtime Side-Channels Extermination Plan

<!-- TOC START -->

- [Mandate](#mandate)
- [Root causes](#root-causes)
- [Phases](#phases)
  - [Fase 0 — Census (done 2026-11-20)](#fase-0-census-done-2026-11-20)
  - [Fase 1 — Canonicalize (in progress)](#fase-1-canonicalize-in-progress)
  - [Fase 2 — Proof (GATE)](#fase-2-proof-gate)
  - [Fase 3 — Exterminate (gated on Fase 2 pass)](#fase-3-exterminate-gated-on-fase-2-pass)
  - [Fase 4 — Pytest runtimes + scattered .venv](#fase-4-pytest-runtimes-scattered-venv)
  - [Fase 5 — Validation (the only proof)](#fase-5-validation-the-only-proof)
- [Blockers](#blockers)
- [ADR compliance](#adr-compliance)

<!-- TOC END -->

**Bead:** flext-9qlie  
**Status:** Approved, in execution (Fase 0/1)  
**Integration branch:** 0.12.0-dev

## Mandate

Exterminate `.flext/executor` and ALL non-homologated runtime paths. The ONLY canonical
runtime is `<workspace>/.venv` provisioned by `make setup`. ADR-030, ADR-029, ADR-018,
ADR-028 D18 are inviolable.

## Root causes

1. `.flext/executor` — separate venv holding stale `flext_core` (missing
   `_constants.infrastructure`). Created/maintained outside `make setup`. OpenMoat
   blocks its python binary (non-pinned path).
2. `core.hooksPath=/dev/null` — silent skip in `INSTALL_GIT_HOOKS_RECIPE`. Must
   fail-loud.
3. Scattered `.venv` / mise data / runtimes across projects.
4. Manual `pip install` / `uv pip install` outside `make setup`.

## Phases

### Fase 0 — Census (done 2026-11-20)

- `.flext/executor` exists (Python 3.13.18, mise-pinned home) but binary path not in
  OpenMoat allowlist.
- 12 `.flext` dirs across root + 7 members + 2 worktrees + 2 nested.
- 15 `.venv` dirs; pytest runtimes in `/tmp`, `~/tmp` (orphaned).
- `core.hooksPath` unset in root (exit 1); hook pre-commit installed.

### Fase 1 — Canonicalize (in progress)

- Executor already uses pinned Python (`--python $$desired_python` in template).
- Add hooksPath fail-loud pre-flight in `_setup_activated`.
- OpenMoat homologation: either add executor path to allowlist or reroute to mise
  binary.
- Owner: `flext-infra/src/flext_infra/templates/project/base/Makefile.j2`.

### Fase 2 — Proof (GATE)

- Destructive test in isolated worktree: break flext-infra source, run `make upg`,
  verify self-repair.
- Success → proceed to Fase 3. Failure → keep executor canonical (Fase 1 is final).

### Fase 3 — Exterminate (gated on Fase 2 pass)

- Remove executor vars/recipe/model/config from template + model + artifact + codegen.
- Reroute `_upg_lifecycle` to `PROJECT_INFRA_RUN` with `-I` + sanitized env.
- `rm -rf .flext/executor` everywhere.
- Full gate sequence.

### Fase 4 — Pytest runtimes + scattered .venv

- Remove orphaned runtimes in `/tmp`, `~/tmp`.
- Consolidate `.venv`: workspace uses `<workspace>/.venv`; standalone/worktree own
  `make setup`.
- Single isolated pytest environment per full cycle, created/destroyed by pytest.

### Fase 5 — Validation (the only proof)

1. Fresh checkout → `make setup` → `make upg` → `make gen` (×2, 2nd=0) → `make fix` →
   `make fmt` (2nd=no-op) → `make check` (primary) → `make tests` = ALL GREEN.
2. `ls .flext/executor` → "No such file or directory".
3. `grep -rn executor Makefile *.mk` → ZERO hits.
4. `$(VENV_DIR)/bin/python -c "import flext_core._constants.infrastructure"` → editable
   path.
5. `git config core.hooksPath` → empty or valid dir (never `/dev/null`).
6. `find . -name .venv -type d` → only `<workspace>/.venv`.
7. OpenMoat: no non-pinned binary.

## Blockers

- Fase 3 blocked until Fase 2 proves repair alternative.
- All Makefile/template changes via `make gen`, never hand-edit.
- Lint-rule freeze: no rule change without explicit authorization.

## ADR compliance

ADR-030 (locks), ADR-029 (verb order), ADR-018 (single pipeline), ADR-028 D18 (one rule
per law).
