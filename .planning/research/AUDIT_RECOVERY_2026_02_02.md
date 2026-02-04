# Audit & Recovery Plan: "Lost Requirements" Recovery
**Date:** 2026-02-02
**Status:** CRITICAL
**Scope:** Dead Code, Security, Ignored Constraints

## 1. Executive Summary

A forensic audit of documentation, git history, and planning files confirms a significant divergence between *documented requirements* and *current implementation*. Critical mandates regarding **dead code elimination** and **security governance** from November 2025 sessions were effectively ignored in subsequent execution phases.

We are currently carrying **untracked technical debt** and **unverified security posture**. This document outlines the findings and a mandatory recovery plan.

## 2. Forensic Findings (The Gap)

| Category | Requirement (Documented) | Source | Current Status | Gap Severity |
|----------|--------------------------|--------|----------------|--------------|
| **Dead Code** | Remove `process_entry`, `convert_entry` | `Execute_Implementation_Complete_2025_11_04.md` | Still present / No removal commits | 🟠 HIGH |
| **Dead Code** | Remove legacy `*_v2.py` files | `Type_Safety_Audit_2025_11_07_Summary.md` | Files exist, unreferenced | 🟠 HIGH |
| **Security** | Secrets Audit & Baseline | `CONCERNS.md` (lines 348-398) | No "security" commits found | 🔴 CRITICAL |
| **Security** | Dependency Audit | `CONCERNS.md` | No audit evidence | 🔴 CRITICAL |
| **Compliance** | MFA/RBAC, Encryption constraints | `arc42/02-constraints.md` | Ignored in implementation | 🔴 CRITICAL |

## 3. Debt Inventory

### 🔴 Critical Security (Priority 0)
1. **Secrets Baseline**: No evidence of `detect-secrets` or similar baseline scan. Potential exposed credentials.
2. **Dependency Audit**: `poetry audit` / `safety` checks missing from workflow.
3. **Compliance Drift**: Implementation has proceeded without checking against `02-constraints.md` (RBAC, Encryption).

### 🟠 Dead Code (Priority 1)
1. **Legacy Refactoring Leftovers**:
   - `process_entry` (deprecated)
   - `convert_entry` (deprecated)
2. **Ghost Files**:
   - `models_v2.py`
   - `constants_v2.py`
   - `_migration/constants_new.py`
3. **Abandoned Branches**: `refactor/remove-dead-code` (stale).

## 4. Recovery Plan

We must immediately halt feature work and inject recovery phases.

### Phase 70.2: Security Baseline (URGENT)
**Goal**: Establish security baseline and verify compliance.
- [ ] Run `detect-secrets` scan and establish baseline.
- [ ] Run `poetry audit` across all 5 projects.
- [ ] Verify `02-constraints.md` compliance for current implementation.
- [ ] **Deliverable**: `SECURITY_BASELINE.md` and remediation tasks.

### Phase 70.3: Dead Code Exorcism
**Goal**: Remove identified dead code and legacy artifacts.
- [ ] Remove `models_v2.py`, `constants_v2.py`.
- [ ] Remove `process_entry`, `convert_entry` functions.
- [ ] Prune stale branches (`refactor/remove-dead-code`).
- [ ] **Deliverable**: Clean codebase matching docs.

## 5. Immediate Actions

1. **Acknowledge**: Accept this plan to update the Roadmap.
2. **Insert**: Inject Phase 70.2 and 70.3 into `ROADMAP.md` immediately.
3. **Execute**: Begin Phase 70.2 (Security) alongside Phase 70.1 (Deps).
