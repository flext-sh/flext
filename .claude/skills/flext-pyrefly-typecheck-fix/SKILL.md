<!-- TOC START -->
- [Purpose](#purpose)
- [Error Clusters Covered](#error-clusters-covered)
  - [1. Logger Typing Drift](#1-logger-typing-drift)
  - [2. `FlextResult.ok(None)` — Real Bug](#2-flextresultoknone-real-bug)
  - [3. `FlextResult[object]` Type Erasure](#3-flextresultobject-type-erasure)
  - [4. RootModel Container Coercion](#4-rootmodel-container-coercion)
  - [5. Mapping Mutation](#5-mapping-mutation)
- [Verification](#verification)
- [Hard Rules](#hard-rules)
<!-- TOC END -->

---
name: flext-pyrefly-typecheck-fix
description: Pyrefly type-check error detection and safe auto-fix rules for recurring error patterns across the FLEXT ecosystem
---

# Pyrefly Type-Check Fix Rules

**Reviewed**: 2026-02-18 | **Scope**: Automated detection and fix for recurring pyrefly error clusters

> **Source of truth**: Error patterns extracted from `make check` and `make validate` output across FLEXT projects.
> Cross-referenced with `flext-core/src/flext_core/typings.py`, `protocols.py`, and `result.py`.

## Purpose

Encodes each recurring pyrefly error family into:
- A **detection rule** (ast-grep search) for visibility and counting
- A **safe fix rule** (ast-grep rewrite) when mechanical
- A **manual-only instruction** when semantic

Use `make validate` as the primary execution entrypoint. Internal script orchestration remains an implementation detail.

## Error Clusters Covered

### 1. Logger Typing Drift
- **Symptom**: `BindableLogger` missing `.debug/.info/.warning/.error/.exception`; `BindableLogger` not assignable to `p.Log.StructlogLogger`
- **Fix**: Annotate loggers as `p.Log.StructlogLogger` where logger originates from `FlextRuntime.get_logger` or `FlextLogger.get_logger`

### 2. `FlextResult.ok(None)` — Real Bug
- **Symptom**: `Argument None is not assignable to parameter value with type T`
- **Fix**: Replace `.ok(None)` with `.ok(True)` for `FlextResult[bool]` return types; review other types per call-site intent

### 3. `FlextResult[object]` Type Erasure
- **Symptom**: Invariance prevents safe widening of `FlextResult[object]`
- **Fix**: Rewrite to `FlextResult[t.GeneralValueType]` at boundaries, or make local functions generic

### 4. RootModel Container Coercion
- **Symptom**: `dict.__init__ no-matching-overload` when calling `dict(configmap_instance)`
- **Fix**: Use `.root` instead of `dict(...)` coercion on RootModel instances

### 5. Mapping Mutation
- **Symptom**: `Mapping` has no `setdefault`, cannot be item-assigned
- **Fix**: Keep `Mapping[...]` at read-only boundaries; use `MutableMapping[...]` for mutating contracts, or materialize a local `dict(...)` copy before mutation

## Verification

```bash
# Recommended gates
make validate PROJECT=<name>
make validate PROJECT=<name> FIX=1

# Workspace slice
make validate PROJECTS="proj-a proj-b"
```

When `type: custom` is necessary, keep script implementations inside `.claude/skills/flext-pyrefly-typecheck-fix/` and return `{"violation_count": N}`.

## Hard Rules

- **NO suppressions**: No `# pyrefly: ignore`, no baselines, no suppress commands
- **Non-degrading**: All fixes must reduce or maintain error count; never increase
- **Rollback safety**: skill_fix.py handles hash+backup+rewrite+verify+rollback per file
- **Stub boundary**: `typings/generated/` is for third-party stubs only; never generate stubs for internal modules (`flext_*`, `flext_*`, `flext_*`)
- **Root-cause only**: Internal missing imports must be fixed in source/type architecture, not patched with generated stubs
- **Skill contract**: rules consumed by `skill_validate.py` / `skill_fix.py` must remain flat-key format and executable for `fix_auto: true`
