# ldap MRO Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite ldap from constructor-injection to MRO-based composition like cli — services become mixins, `ldap()` instantiates with zero ceremony.

**Architecture:** FlextLdapConnection and FlextLdapOperations become MRO mixins. ldap inherits from both plus sync logic. Adapter state (`_adapter`) lives on Connection mixin, Operations accesses it via `self._adapter` (shared MRO). All consumers switch to `ldap()` direct usage.

**Tech Stack:** Python 3.13, Pydantic v2, flext-core s, ldap3

---

## Task 1: Fix immediate bugs (norm_string, missing exports)

**Files:**

- Modify: `flext-ldap/src/flext_ldap/services/operations.py:1223`
- Modify: `flext-ldap/src/flext_ldap/api.py:583` (docstring ref)
- Modify: `flext-ldap/src/flext_ldap/constants.py` (add callback param constants)

- [ ] **Step 1: Fix `u.Ldif.norm_string` → `u.Ldif.norm` in operations.py:1223**
- [ ] **Step 2: Fix docstring refs to `norm_string` in operations.py and api.py**
- [ ] **Step 3: Move MULTI_PHASE_CALLBACK_PARAM_COUNT and SINGLE_PHASE_CALLBACK_PARAM_COUNT to c.Ldap constants**
- [ ] **Step 4: Run ruff + pyrefly + pytest on flext-ldap**
- [ ] **Step 5: Commit**

## Task 2: Convert FlextLdapConnection to MRO mixin

**Files:**

- Modify: `flext-ldap/src/flext_ldap/services/connection.py`

- [ ] **Step 1: Change base class from `s[bool]` to `FlextLdapServiceBase`**
- [ ] **Step 2: Replace `__init__` with u.PrivateAttr defaults + lazy init**
- [ ] **Step 3: Absorb detection.py into Connection (inner class or method)**
- [ ] **Step 4: Ensure connect/disconnect/is_connected/execute work as MRO methods**
- [ ] **Step 5: Run ruff + pyrefly**
- [ ] **Step 6: Commit**

## Task 3: Convert FlextLdapOperations to MRO mixin

**Files:**

- Modify: `flext-ldap/src/flext_ldap/services/operations.py`

- [ ] **Step 1: Remove `_connection` field — use `self._adapter` directly (shared MRO)**
- [ ] **Step 2: Change `self._connection.adapter.add()` → `self._adapter.add()` (4 occurrences)**
- [ ] **Step 3: Change `self._connection.is_connected` → `self.is_connected` (2 occurrences)**
- [ ] **Step 4: Change base class to `FlextLdapServiceBase`**
- [ ] **Step 5: Run ruff + pyrefly**
- [ ] **Step 6: Commit**

## Task 4: Rewrite ldap as MRO facade

**Files:**

- Rewrite: `flext-ldap/src/flext_ldap/api.py`

- [ ] **Step 1: ldap MRO: `class ldap(FlextLdapConnection, FlextLdapOperations):`**
- [ ] **Step 2: Remove constructor injection (`__init__` with connection/operations args)**
- [ ] **Step 3: Keep sync methods (sync_phase_entries, sync_multiple_phases) on ldap**
- [ ] **Step 4: Keep FlextLdapSyncCallbacks helper class**
- [ ] **Step 5: Keep context manager (**enter**/**exit**)**
- [ ] **Step 6: Override execute() → r[m.Ldap.SearchResult]**
- [ ] **Step 7: Remove from_settings() (no longer needed)**
- [ ] **Step 8: Run ruff + pyrefly**
- [ ] **Step 9: Commit**

## Task 5: Update **init**.py exports

**Files:**

- Modify: `flext-ldap/src/flext_ldap/__init__.py`

- [ ] **Step 1: Remove FlextLdapConnection, FlextLdapOperations from public exports (internal now)**
- [ ] **Step 2: Keep ldap, c, m, t, p, u, s as public API**
- [ ] **Step 3: Run ruff + pyrefly**
- [ ] **Step 4: Commit**

## Task 6: Fix all flext-ldap tests

**Files:**

- Modify: all files in `flext-ldap/tests/unit/` and `flext-ldap/tests/integration/`

- [ ] **Step 1: Update test_api.py — ldap() direct, fix imports**
- [ ] **Step 2: Update test_operations.py — test via ldap() MRO**
- [ ] **Step 3: Update test_smoke.py — remove ceremony**
- [ ] **Step 4: Update conftest.py if needed**
- [ ] **Step 5: Remove dead/useless tests**
- [ ] **Step 6: Run full pytest suite — 0 failures**
- [ ] **Step 7: Commit**

## Task 7: Update consumers (tap/target/dbt-ldap)

**Files:**

- Modify: `flext-tap-ldap/src/flext_tap_ldap/client.py`
- Modify: `flext-target-ldap/src/flext_target_ldap/client.py`
- Modify: `flext-target-ldap/src/flext_target_ldap/target_client.py`
- Modify: `flext-dbt-ldap/src/flext_dbt_ldap/dbt_client.py`

- [ ] **Step 1: Replace 3-step ceremony with ldap() direct in each consumer**
- [ ] **Step 2: Remove FlextLdapConnection/FlextLdapOperations imports**
- [ ] **Step 3: Run ruff + pyrefly on each consumer project**
- [ ] **Step 4: Commit**

## Task 8: Update algar-oud-mig (production consumer)

**Files:**

- Modify: `algar-oud-mig/src/algar_oud_mig/base.py`
- Modify: `algar-oud-mig/src/algar_oud_mig/services/sync.py`
- Modify: `algar-oud-mig/examples/05_ldap_connection.py`
- Modify: all algar-oud-mig files importing FlextLdapConnection/Operations

- [ ] **Step 1: Replace get_ldap_client() factory with ldap() direct**
- [ ] **Step 2: Remove FlextLdapConnection/FlextLdapOperations imports**
- [ ] **Step 3: Run ruff + pyrefly**
- [ ] **Step 4: Commit**

## Task 9: Archive dead code

**Files:**

- Move: `flext-ldap/src/flext_ldap/services/detection.py` → `.bak`
- Move: `flext-ldap/src/flext_ldap/services/sync.py` → `.bak`

- [ ] **Step 1: mv detection.py detection.py.bak (absorbed into connection)**
- [ ] **Step 2: mv sync.py sync.py.bak (absorbed into api.py)**
- [ ] **Step 3: Update services/**init**.py**
- [ ] **Step 4: Run ruff + pyrefly + pytest**
- [ ] **Step 5: Commit**

## Task 10: Final validation

- [ ] **Step 1: ruff check flext-ldap/src/ — 0 errors**
- [ ] **Step 2: pyrefly check flext-ldap/src/ — 0 errors**
- [ ] **Step 3: pytest flext-ldap/tests/ — 0 failures**
- [ ] **Step 4: ruff check on all consumers — 0 errors**
- [ ] **Step 5: pyrefly check on all consumers — 0 errors**
