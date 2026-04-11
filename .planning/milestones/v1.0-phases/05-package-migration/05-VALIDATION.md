---
phase: 5
slug: package-migration
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4+ |
| **Settings file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `make test-unit` |
| **Full suite command** | `make test` |
| **Estimated runtime** | ~120 seconds |

---

## Sampling Rate

- **After every task commit:** Run `make test-unit`
- **After every plan wave:** Run `make test`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | MIG-01 | integration | `test -d flext-infra/.git` | ✅ | ⬜ pending |
| 05-01-02 | 01 | 1 | MIG-02 | integration | `test -d flext-tests/.git` | ✅ | ⬜ pending |
| 05-01-03 | 01 | 1 | MIG-03 | integration | `! test -d flext-core/src/flext_infra` | ✅ | ⬜ pending |
| 05-02-01 | 02 | 1 | MIG-04 | unit | `grep -L poetry flext-core/pyproject.toml` | ✅ | ⬜ pending |
| 05-02-02 | 02 | 1 | MIG-04 | unit | `grep hatchling flext-core/pyproject.toml` | ✅ | ⬜ pending |
| 05-03-01 | 03 | 2 | MIG-05 | integration | `uv lock --dry-run` | ❌ W0 | ⬜ pending |
| 05-03-02 | 03 | 2 | MIG-05 | unit | `test -f uv.lock && ! test -f flext-core/poetry.lock` | ✅ | ⬜ pending |
| 05-04-01 | 04 | 3 | MIG-06 | integration | `grep -r "uv run" base.mk` | ✅ | ⬜ pending |
| 05-04-02 | 04 | 3 | MIG-06 | integration | `grep "setup-uv" .github/workflows/ci.yml` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Verify `uv lock --dry-run` resolves cleanly with workspace members
- [ ] Verify submodule checkout in fresh clone

*Existing infrastructure covers most phase requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| CI passes without Poetry | MIG-06 | Requires GitHub Actions run | Push branch, verify CI green |
| Submodule clone works | MIG-01/02 | Requires fresh clone | `git clone --recurse-submodules` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
