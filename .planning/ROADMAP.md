## Phase 70: Foundation Fixes

Install missing dependencies (returns, beartype) in all venvs
- [ ] Fix flext-ldif test timeout issue
- [ ] Fix ldif_max_line_length default (199 vs 100)
- [ ] Verify flext-core passes make validate

**Success:** All 5 projects can run `make test` without crashes or timeouts

---

## Phase 70.1: Urgent Beads Sync (INSERTED)

**Goal:** [Urgent work - to be planned]
**Depends on:** Phase 70
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd-plan-phase 70.1 to break down)

**Details:**
[To be added during planning]

---

## Phase 70.2: Security Baseline (URGENT RECOVERY)

**Goal:** Establish security baseline, audit secrets/dependencies, verify compliance
**Depends on:** Phase 70
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd-plan-phase 70.2 to break down)

**Details:**
- Run detect-secrets
- Run poetry audit
- Verify 02-constraints.md compliance

---

## Phase 70.3: Dead Code Exorcism (URGENT RECOVERY)

**Goal:** Remove legacy code (process_entry, models_v2) and stale artifacts
**Depends on:** Phase 70.2
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd-plan-phase 70.3 to break down)

**Details:**
- Remove models_v2.py, constants_v2.py
- Remove process_entry/convert_entry
- Prune refactor/remove-dead-code branch

---

## Phase 71: flext-core Stabilization

**Goal:** Foundation project must be stable first (all others depend on it)

### Tasks
- [ ] Replace Optional[T] with T | None in flext-core
- [ ] Remove cast() usages in flext-core
- [ ] Remove TYPE_CHECKING blocks in flext-core
- [ ] Fix all MyPy errors in flext-core
- [ ] Achieve 80%+ test coverage in flext-core
- [ ] Verify make validate passes in flext-core

**Success:** `make validate` passes in flext-core with 80%+ coverage

---

## Phase 72: flext-cli Stabilization

**Goal:** CLI foundation depends only on flext-core

### Tasks
- [ ] Replace Optional[T] with T | None in flext-cli
- [ ] Remove cast() usages in flext-cli
- [ ] Remove TYPE_CHECKING blocks in flext-cli
- [ ] Fix all MyPy errors in flext-cli
- [ ] Achieve 80%+ test coverage in flext-cli
- [ ] Verify make validate passes in flext-cli

**Success:** `make validate` passes in flext-cli with 80%+ coverage

---

## Phase 73: flext-ldif Stabilization

**Goal:** LDIF processing library (depends on flext-core)

### Tasks
- [ ] Replace Optional[T] with T | None in flext-ldif
- [ ] Remove cast() usages in flext-ldif
- [ ] Remove TYPE_CHECKING blocks in flext-ldif
- [ ] Fix all MyPy errors in flext-ldif
- [ ] Achieve 80%+ test coverage in flext-ldif
- [ ] Verify make validate passes in flext-ldif

**Success:** `make validate` passes in flext-ldif with 80%+ coverage

---

## Phase 74: flext-ldap Stabilization

**Goal:** LDAP operations (depends on flext-core, flext-ldif)

### Tasks
- [ ] Replace Optional[T] with T | None in flext-ldap
- [ ] Remove cast() usages in flext-ldap
- [ ] Remove TYPE_CHECKING blocks in flext-ldap
- [ ] Fix all MyPy errors in flext-ldap
- [ ] Achieve 80%+ test coverage in flext-ldap
- [ ] Verify make validate passes in flext-ldap

**Success:** `make validate` passes in flext-ldap with 80%+ coverage

---

## Phase 75: client-a-oud-mig Stabilization

**Goal:** Migration tool (depends on all previous projects)

### Tasks
- [ ] Replace Optional[T] with T | None in client-a-oud-mig
- [ ] Remove cast() usages in client-a-oud-mig
- [ ] Remove TYPE_CHECKING blocks in client-a-oud-mig
- [ ] Fix all MyPy errors in client-a-oud-mig
- [ ] Achieve 80%+ test coverage in client-a-oud-mig
- [ ] Verify make validate passes in client-a-oud-mig

**Success:** `make validate` passes in client-a-oud-mig with 80%+ coverage

---

## Phase 76: Final Validation

**Goal:** Cross-project integration and final verification

### Tasks
- [ ] Run make validate on all 5 projects sequentially
- [ ] Verify no cross-project import issues
- [ ] Document final coverage numbers
- [ ] Tag v0.9.0 release

**Success:** All 5 projects pass `make validate`, ready for production

---

*Created: 2026-01-31*
*Milestone: v0.9.0 - Production Stability*