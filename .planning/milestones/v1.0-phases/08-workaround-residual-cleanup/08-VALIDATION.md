---
phase: 8
slug: workaround-residual-cleanup
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Settings file** | `pyproject.toml` (root workspace) |
| **Quick run command** | `grep -rn "except Exception:" --include="*.py" src/ tests/ examples/` |
| **Full suite command** | `make lint && grep -c "except Exception:\|sys\.exit(\|print(" --include="*.py" -r src/` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick grep to verify violation count decreases
- **After every plan wave:** Run full suite (lint + grep census)
- **Before `/gsd:verify-work`:** Full suite must show zero violations in scope
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | WA-03 | grep | `grep -rn "except Exception:" --include="*.py" src/ tests/ examples/` | ✅ | ⬜ pending |
| 08-01-02 | 01 | 1 | WA-04 | grep | `grep -rn "sys\.exit(" --include="*.py" src/ \| grep -v __main__` | ✅ | ⬜ pending |
| 08-01-03 | 01 | 1 | WA-05 | grep | `grep -rn "print(" --include="*.py" src/` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No new test files needed — validation is via grep census.

---

## Manual-Only Verifications

All phase behaviors have automated verification (grep-based census).

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
