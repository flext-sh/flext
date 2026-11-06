# FLEXT Fleet-Wide Docstring Curation Program Tracker

> **Tracker ID:** `flext-ez35p` (Docstring PEP campaign: D413 mechanical + curated quality, fleet-wide)  
> **Authority:** Operator Order 2026-11-03 (Cyclic interactive fleet-wide docstring professionalization)  
> **Docstring Convention:** Google Style / PEP 257 (`[tool.ruff.lint.pydocstyle] convention = "google"`)  
> **Language:** English  
> **Philosophy:** Focus on **WHAT** the module, class, method, or function does (behavioral contracts, invariants, outcomes), **NOT HOW** it is internally implemented.  
> **Cross-References:** Mandatory correlation to Architecture Decision Records (`docs/architecture/adr/ADR-*.md`), architectural guides (`docs/guides/*.md`), and related sibling/member modules.

---

## 1. Governance & Execution Rules

1. **Behavioral Focus**: Describe responsibilities, guarantees, preconditions, and return semantics. Exclude internal implementation plumbing, variable assignments, loops, and private mechanics.
2. **PEP 257 & Google Format**:
   - Single-line summary ending in a period.
   - Blank line after summary.
   - Extended description with behavioral invariants and domain roles.
   - Standard sections: `Args:`, `Returns:`, `Raises:`, `Yields:`, `Attributes:`.
   - `See Also:` section referencing canonical ADRs (e.g., `ADR-001`, `ADR-016`, `ADR-027`, `ADR-028`) and documentation guides.
3. **Continuous Validation (Rule 7)**:
   - `uv run ruff check <paths> --select D`
   - `uv run ruff check <paths>`
   - `uv run ruff format --check <paths>`
   - Applicable unit test gates.
4. **Idempotence & Generator Law (Rule 6, ADR-018)**:
   - For auto-generated facades (`c.py`, `m.py`, `p.py`, `t.py`, `u.py`, `__init__.py`), ensure hand-curated documentation aligns with generated projections and generator templates.

---

## 2. Cohort Roadmap & Fleet Inventory

| Cohort | Subproject / Target | Location | Modules (`src`) | Status | Validated Green |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0** | **Root Workspace** (`flext`) | `src/flext/` | 28 | **DONE** | **GREEN (Ruff check + format)** |
| **1** | **Foundational Core** (`flext-core`) | `flext-core/src/flext_core/` | 235 | **IN PROGRESS** | Pending |
| **2** | **CLI & Infrastructure** (`flext-cli`, `flext-infra`) | `flext-cli/`, `flext-infra/` | ~306 + ~150 | QUEUED | Pending |
| **3** | **Auth, API & Web** (`flext-auth`, `flext-api`, `flext-web`) | `flext-auth/`, `flext-api/`, `flext-web/` | ~180 | QUEUED | Pending |
| **4** | **Protocols & Quality** (`flext-grpc`, `flext-observability`, `flext-quality`, `flext-plugin`) | `flext-grpc/`, etc. | ~250 | QUEUED | Pending |
| **5** | **Data Connectors: LDAP / LDIF** (`flext-ldap`, `flext-ldif`, taps/targets/dbt) | `flext-ldap/`, `flext-ldif/`, etc. | ~400 | QUEUED | Pending |
| **6** | **Data Connectors: Oracle & Meltano** (`flext-db-oracle`, `flext-oracle-oic`, `flext-oracle-wms`, `flext-meltano`, taps/targets/dbt) | `flext-oracle-*/`, `flext-db-oracle/`, etc. | ~1000 | QUEUED | Pending |
| **7** | **Shared Test Kit** (`flext-tests`) | `flext-tests/src/flext_tests/` | ~300 | QUEUED | Pending |

---

## 3. Cohort 0: Root Workspace (`src/flext/`) Modules

| Module | Purpose / Domain Role | ADR Cross-References | Status |
| :--- | :--- | :--- | :--- |
| `src/flext/__init__.py` | Root namespace lazy export hub | ADR-018, ADR-027, ADR-028 | DONE |
| `src/flext/cli.py` | Workspace root CLI orchestrator | ADR-028, ADR-017 | DONE |
| `src/flext/config.py` | Process-wide singleton configuration facade | ADR-005, ADR-016, ADR-024 | DONE |
| `src/flext/settings.py` | Process-wide environment settings facade | ADR-005, ADR-016, ADR-024 | DONE |
| `src/flext/constants.py` | Unified constants facade (`c.Root.*`) | ADR-005, ADR-027, ADR-028 | DONE |
| `src/flext/models.py` | Unified models facade (`m.Root.*`) | ADR-018, ADR-027, ADR-028 | DONE |
| `src/flext/protocols.py` | Unified protocols facade (`p.Root.*`) | ADR-018, ADR-019, ADR-027 | DONE |
| `src/flext/typings.py` | Unified typings facade (`t.Root.*`) | ADR-027, ADR-028 | DONE |
| `src/flext/utilities.py` | Unified utilities facade (`u.Root.*`) | ADR-001, ADR-027, ADR-028 | DONE |
| `src/flext/_config/base.py` | Base configuration declarations for workspace root | ADR-005, ADR-016 | DONE |
| `src/flext/_config/config.py` | Concrete configuration properties for workspace root | ADR-005, ADR-016 | DONE |
| `src/flext/_config/__init__.py` | Config subpackage lazy exports | ADR-018, ADR-027 | DONE |
| `src/flext/_constants/base.py` | Base constants declarations for workspace root | ADR-005, ADR-027 | DONE |
| `src/flext/_constants/config.py` | Configuration constants declarations for workspace root | ADR-005, ADR-027 | DONE |
| `src/flext/_constants/__init__.py` | Constants subpackage lazy exports | ADR-018, ADR-027 | DONE |
| `src/flext/_models/base.py` | Base models declarations for workspace root | ADR-018, ADR-028 | DONE |
| `src/flext/_models/config.py` | Pipeline and stage data payload models | ADR-001, ADR-018, ADR-028 | DONE |
| `src/flext/_models/__init__.py` | Models subpackage lazy exports | ADR-018, ADR-027 | DONE |
| `src/flext/_protocols/base.py` | Base protocols declarations for workspace root | ADR-019, ADR-027 | DONE |
| `src/flext/_protocols/config.py` | Configuration runtime protocols for workspace root | ADR-016, ADR-019 | DONE |
| `src/flext/_protocols/generated_models_value.py` | Value model protocol declarations | ADR-018, ADR-019 | DONE |
| `src/flext/_protocols/__init__.py` | Protocols subpackage lazy exports | ADR-018, ADR-027 | DONE |
| `src/flext/_typings/base.py` | Base type aliases declarations for workspace root | ADR-027, ADR-028 | DONE |
| `src/flext/_typings/config.py` | Configuration type definitions for workspace root | ADR-005, ADR-027 | DONE |
| `src/flext/_typings/__init__.py` | Typings subpackage lazy exports | ADR-018, ADR-027 | DONE |
| `src/flext/_utilities/base.py` | Base utility functions for workspace root | ADR-001, ADR-027 | DONE |
| `src/flext/_utilities/config.py` | Configuration utility functions for workspace root | ADR-005, ADR-016 | DONE |
| `src/flext/_utilities/__init__.py` | Utilities subpackage lazy exports | ADR-018, ADR-027 | DONE |

---

## 4. Session Handoff & Continuity Log

- **2026-11-03 (Session 1)**: Program initiated per Operator order. Durable tracker created. Cohort 0 (`flext` root package, 28 modules) undergoing comprehensive PEP 257 / Google style docstring upgrade focusing on "what it does" and ADR cross-referencing.
