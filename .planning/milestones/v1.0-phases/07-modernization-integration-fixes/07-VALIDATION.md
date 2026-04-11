---
phase: 7
slug: modernization-integration-fixes
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4+ |
| **Settings file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `.venv/bin/pytest -x --no-header -q` |
| **Full suite command** | `.venv/bin/pytest --no-header -q` |
| **Estimated runtime** | ~30 seconds (affected test collections) |

---

## Sampling Rate

- **After every task commit:** Run `.venv/bin/pytest -x --no-header -q {affected_test_file}`
- **After every plan wave:** Run `.venv/bin/pytest --no-header -q` on affected projects
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | INFRA-05 | integration | `.venv/bin/pytest flext-infra/tests/ -x -q` | ✅ | ⬜ pending |
| 07-02-01 | 02 | 1 | MOD-02 | unit | `.venv/bin/pytest flext-tests/tests/ -x -q` | ✅ | ⬜ pending |
| 07-03-01 | 03 | 2 | MOD-02 | unit | `.venv/bin/pytest flext-core/tests/ -x -q` | ✅ | ⬜ pending |
| 07-04-01 | 04 | 2 | MOD-06 | grep | `grep -r 'UserDict\|UserString' flext-*/src/` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.*

---

## Manual-Only Verifications

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
