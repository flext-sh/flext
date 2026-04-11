---
phase: 9
slug: rope-native-refactor-engine-rewrite
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-25
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4+ |
| **Settings file** | `flext-infra/pyproject.toml` |
| **Quick run command** | `/home/marlonsc/flext/.venv/bin/pytest flext-infra/tests/ -x -q` |
| **Full suite command** | `/home/marlonsc/flext/.venv/bin/pytest flext-infra/tests/ -v` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `/home/marlonsc/flext/.venv/bin/pytest flext-infra/tests/ -x -q`
- **After every plan wave:** Run `/home/marlonsc/flext/.venv/bin/pytest flext-infra/tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 9-01-00 | 01 | 0 | setup | scaffold | `/home/marlonsc/flext/.venv/bin/pytest flext-infra/tests/refactor/test_rope_stubs.py -x -q` | ❌ W0 | ⬜ pending |
| 9-01-01 | 01 | 1 | ROPE-01, ROPE-05, ROPE-06 | unit | `/home/marlonsc/flext/.venv/bin/pytest flext-infra/tests/test_infra_refactor_rope_project.py -x -q` | ❌ W0 | ⬜ pending |
| 9-02-01 | 02 | 2 | ROPE-02 | integration | `/home/marlonsc/flext/.venv/bin/pytest flext-infra/tests/test_infra_refactor_rope_migrations.py -x -q -k symbol` | ❌ | ⬜ pending |
| 9-02-02 | 02 | 2 | ROPE-03, ROPE-04 | integration | `/home/marlonsc/flext/.venv/bin/pytest flext-infra/tests/test_infra_refactor_rope_migrations.py -x -q` | ❌ | ⬜ pending |
| 9-03-01 | 03 | 3 | ROPE-05, ROPE-07 | integration | `/home/marlonsc/flext/.venv/bin/pytest flext-infra/tests/ -x -q` | ✅ | ⬜ pending |
| 9-03-02 | 03 | 3 | ROPE-07 | checkpoint | `wc -l flext-infra/src/flext_infra/transformers/*.py` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Wave 0 is handled by Plan 01, Task 0 which creates stub test files at the canonical path `flext-infra/tests/refactor/`:

- [ ] `flext-infra/tests/refactor/__init__.py` — package init
- [ ] `flext-infra/tests/refactor/test_rope_stubs.py` — stub tests asserting rope import works

All plan `<verify>` commands use paths under `flext-infra/tests/` (existing test dir convention).

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Cross-project rename correctness | D-04 | Requires full 33-project monorepo run | Run `make refactor --rules rope_rename_symbol` on a known symbol used across 3+ projects; verify all sites updated |
| LOC reduction in transformers/ | D-22, ROPE-07 | Requires before/after count comparison | `wc -l flext-infra/src/flext_infra/transformers/*.py` before and after; must be ≤ 4120 baseline |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
