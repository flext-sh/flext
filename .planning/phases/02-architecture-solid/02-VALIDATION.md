---
phase: 02
slug: architecture-solid
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4+ |
| **Config file** | `pyproject.toml` [tool.pytest.ini_options] |
| **Quick run command** | `make check PROJECT=<name> CHECK_GATES=pyrefly,pyright` |
| **Full suite command** | `make pyre && make test` |
| **Estimated runtime** | ~120 seconds (per-project check ~10s, full suite ~120s) |

---

## Sampling Rate

- **After every task commit:** Run `make check PROJECT=<name> CHECK_GATES=pyrefly,pyright`
- **After every plan wave:** Run `make pyre && make test`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 0 | ARCH-04/05 | structural | `sg --pattern 'issubclass($A, $B)' --lang python flext-core/src/` | ✅ | ⬜ pending |
| 02-02-01 | 02 | 1 | ARCH-01 | structural | `sg --pattern ': FlextContext' --lang python` | ✅ | ⬜ pending |
| 02-02-02 | 02 | 1 | ARCH-04 | structural | `sg --pattern 'class $A(ABC)' --lang python flext-core/src/` | ✅ | ⬜ pending |
| 02-02-03 | 02 | 1 | ARCH-05 | structural | `grep -r "class.*ABC" flext-core/src/` | ✅ | ⬜ pending |
| 02-03-01 | 03 | 2 | ARCH-03 | structural | `sg --pattern '$X: $T = Field($$$)' --lang python` | ✅ | ⬜ pending |
| 02-03-02 | 03 | 2 | ARCH-06 | structural | `sg --pattern 'TypeAdapter($$$)' --lang python` | ✅ | ⬜ pending |
| 02-03-03 | 03 | 2 | ARCH-07 | structural | `sg --pattern 'Field(default=[$$$])' --lang python` | ✅ | ⬜ pending |
| 02-04-01 | 04 | 3 | ARCH-08 | structural | `grep -r 'TypeAlias' --include='*.py'` | ✅ | ⬜ pending |
| 02-04-02 | 04 | 3 | ARCH-02 | structural | `grep -rn 'from flext_core import.*[cmtup]' tests/` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements. Phase 2 is structural refactoring validated by ast-grep pattern searches and type checkers.

---

## Manual-Only Verifications

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
