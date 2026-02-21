<!-- TOC START -->
- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Examples](#examples)
- [Workflow](#workflow)
- [Verification](#verification)
<!-- TOC END -->

---
name: flext-architecture-layers
description: Layer map and dependency-direction contract for flext-core. Use when adding modules, moving responsibilities, or reviewing imports.
---

# Flext Architecture Layers

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment


## Scope

- `flext-core/src/flext_core/` (intra-module layers)
- `flext-core/docs/architecture/`
- Cross-project inheritance chains (workspace-wide)

## References

- `flext-core/docs/architecture/overview.md` defines L3/L2/L1/L0 and inward arrows.
- `flext-core/src/flext_core/runtime.py` is the bridge for `structlog` and `dependency_injector`.
- `flext-core/src/flext_core/container.py` encapsulates provider registration and resolution.
- `flext-core/src/flext_core/__init__.py` exposes the stable public API aliases.
- `CLAUDE.md` section "Workspace Project Dependency Map" is the canonical cross-project reference.

## Rules

- Allowed direction only: `L3 -> L2 -> L1 -> L0`.
- Never reverse dependency direction (no `L0/L1` imports from `L2/L3`).
- Keep external dependency touchpoints in bridge modules (`runtime.py`, `container.py`).
- Route consumer imports through `flext-core/src/flext_core/__init__.py` where possible.
- Layer map (source-aligned):
  - `L3 Application/Orchestration`: `dispatcher.py`, `handlers.py`, `decorators.py`.
  - `L2 Domain & Infrastructure`: `models.py`, `mixins.py`, `service.py`, `utilities.py`, `loggings.py`, `container.py`.
  - `L1 Foundation & Bridge`: `result.py`, `exceptions.py`, `registry.py`, `runtime.py`.
  - `L0 Pure Contracts`: `constants.py`, `typings.py`, `protocols.py`.

## Instructions

- `runtime.py` owns integration helpers like `FlextRuntime.DependencyIntegration.create_layered_bridge`.
- `runtime.py` owns `configure_structlog` and low-level type/serialization guards.
- `container.py` centralizes DI with `FlextContainer.register`, `register_factory`, `register_resource`, `get`, `get_typed`.
- Higher layers should call bridge APIs, not import third-party infrastructure directly.

- Keep stable aliases exported in `__init__.py`: `r`, `t`, `c`, `m`, `p`, `u`, `d`, `e`, `h`, `s`, `x`.
- If a symbol is for public use, add it to `__init__.py`; if not exported, treat it as internal.
- Verify exports stay aligned with architecture boundaries and ownership.

## Examples

```python
# Good: orchestration consumes bridge + public alias
from flext_core import r
from flext_core.runtime import FlextRuntime

bridge, services, resources = FlextRuntime.DependencyIntegration.create_layered_bridge()
result = r[bool].ok(True)
```

```python
# Bad: direct third-party dependency import in application code
from dependency_injector import providers

container = providers.DynamicContainer()
```

Why bad: bypasses `runtime.py` and `container.py`, increases coupling, and breaks inward-only layering.

```python
# Bad: low-level contracts importing service layer
from flext_core.service import FlextService
```

Why bad: inverts `L1 -> L2` direction and violates the documented architecture topology.

## Cross-Project Dependency Architecture (CRITICAL)

The workspace has **distinct domain projects** that MUST NOT be confused. Each project owns a specific system domain and provides its own `m.<Domain>.*` namespace.

### Domain Projects (provide namespaces via inheritance)

```
flext-core (FlextModels)
├── flext-meltano (FlextMeltanoModels) → m.Meltano.*     [Singer/Meltano pipeline protocol]
├── flext-db-oracle (FlextDbOracleModels) → m.DbOracle.* [Oracle DATABASE connectivity]
├── flext-oracle-wms (FlextOracleWmsModels) → m.OracleWms.* [Oracle WMS - Warehouse Management]
├── flext-ldap (FlextLdapModels) → m.Ldap.*              [LDAP directory]
└── flext-ldif (FlextLdifModels) → m.Ldif.*              [LDIF file format]
```

**flext-db-oracle ≠ flext-oracle-wms**: Oracle Database and Oracle WMS are completely separate systems.

### Integration Projects (inherit from domain layers they USE)

```
flext-target-oracle-wms → (FlextMeltanoModels, FlextOracleWmsModels)  # WMS, NOT db-oracle
flext-tap-oracle-wms    → (FlextMeltanoModels, FlextOracleWmsModels)  # WMS, NOT db-oracle
flext-dbt-oracle-wms    → (FlextMeltanoModels, FlextOracleWmsModels)  # WMS, NOT db-oracle
flext-target-oracle     → (FlextMeltanoModels, FlextDbOracleModels)   # Database, NOT oracle-wms
flext-tap-oracle        → (FlextMeltanoModels, FlextDbOracleModels)   # Database, NOT oracle-wms
flext-dbt-oracle        → (FlextMeltanoModels, FlextDbOracleModels)   # Database, NOT oracle-wms
flext-target-ldap       → (FlextMeltanoModels, FlextLdapModels)
flext-tap-ldap          → (FlextMeltanoModels, FlextLdapModels)
flext-dbt-ldap          → (FlextMeltanoModels, FlextLdapModels)
flext-target-ldif       → (FlextMeltanoModels, FlextLdifModels)
flext-tap-ldif          → (FlextMeltanoModels, FlextLdifModels)
flext-dbt-ldif          → (FlextMeltanoModels, FlextLdifModels)
```

### Selection Rule

| Project name contains | Inherits from (domain) | NEVER inherits from |
|-----------------------|-----------------------|---------------------|
| `oracle-wms` | `FlextOracleWmsModels` | `FlextDbOracleModels` |
| `oracle` (no `-wms`) | `FlextDbOracleModels` | `FlextOracleWmsModels` |
| `ldap` | `FlextLdapModels` | `FlextLdifModels` |
| `ldif` | `FlextLdifModels` | `FlextLdapModels` |

ALL integration projects (targets, taps, dbt) ALSO inherit `FlextMeltanoModels` for Singer protocol types (`m.Meltano.*`).

## Workflow

1. Assign each touched module to L0/L1/L2/L3 before editing.
2. **For cross-project changes**: Identify the correct domain project using the Selection Rule above. NEVER guess.
3. Inspect imports for outward dependencies.
4. Move infrastructure calls behind bridge APIs when needed.
5. Recheck exported/public symbols in `__init__.py`.
6. Run diagnostics and tests before finalization.

## Verification

Make gates:

- `make check PROJECT=flext-core` — lint + type gates enforce import boundaries
- `make check PROJECT=flext-core CHECK_GATES=lint,type` — focused boundary checks
- `make test PROJECT=flext-core` — layer integrity verified by tests

Pattern checks:

- `rg -n "Layered Topology|L3|L2|L1|L0" flext-core/docs/architecture/overview.md`
- `rg -n "class FlextRuntime|class DependencyIntegration|configure_structlog" flext-core/src/flext_core/runtime.py`
- `rg -n "class FlextContainer|def register\(|def register_factory\(|def register_resource\(" flext-core/src/flext_core/container.py`
- `rg -n "FlextResult|FlextTypes|FlextConstants|FlextModels|FlextProtocols|FlextUtilities|FlextDecorators|FlextExceptions|FlextHandlers|FlextService|FlextMixins" flext-core/src/flext_core/__init__.py`
