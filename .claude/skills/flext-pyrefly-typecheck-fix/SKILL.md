<!-- TOC START -->

- [Purpose](#purpose)
- [Error Clusters Covered](#error-clusters-covered)
  - [1. Logger Typing Drift](#1-logger-typing-drift)
  - [2. `r.ok(None)` — Real Bug](#2-flextresultoknone-real-bug)
  - [3. `r[object]` Type Erasure](#3-flextresultobject-type-erasure)
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

- `AGENTS.md` — canonical governance source

## Scope

- Recurring pyrefly error families across FLEXT projects.
- Detection and fix workflows for type-check remediation using standardized automation.

## References

- `AGENTS.md`
- `flext-core/src/flext_core/typings.py`
- `flext-core/src/flext_core/protocols.py`
- `flext-core/src/flext_core/result.py`

## Rules

- Express recurring failures as explicit rule families with deterministic detection.
- Keep fix logic safe and reversible for mechanical rewrites.
- Never use suppression comments as default resolution path.
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, `cast()`, and `inline imports`.

## Instructions

- Run standardized quality gates before and after each fix batch.
- Prefer ast-grep rules for structural changes; keep custom scripts minimal and auditable.
- Keep rule metadata in flat-key format for `skill_validate.py`/`skill_fix.py` consumption.

## Workflow

1. Detect failing cluster type from gate output.
2. Apply mechanical rewrite when safe.
3. Apply manual semantic fix when required.
4. Re-run validation gates and confirm non-regression.

## Examples

```bash
# Focus one project first
make validate PROJECT=flext-core

# Apply approved auto-fix path and re-validate
make validate PROJECT=flext-core FIX=1
```

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

### 2. `r[T].ok(None)` — Real Bug

- **Symptom**: `Argument None is not assignable to parameter value with type T`
- **Fix**: Replace `.ok(None)` with `.ok(True)` for `r[bool]` return types; review other types per call-site intent

### 3. `r[object]` Type Erasure

- **Symptom**: Invariance prevents safe widening of `r[object]`
- **Fix**: Rewrite to `r[object]` at boundaries, or make local functions generic

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
- **AXIOMATIC — ALL 4 linters mandatory**: Every change MUST pass ruff, mypy, pyright, AND pyrefly with ZERO errors. ALL impacted references across ALL 33 projects MUST be updated via ast-grep (`sg`) search-and-replace immediately. No partial fixes.
- **AXIOMATIC — No suppressions without triple justification**: `# type: ignore`, `# noqa`, `# pyright: ignore`, `# pyrefly: ignore`, `# mypy: ignore` require: (1) real internet citations proving unavoidability, (2) business necessity documented in the same comment, (3) per-line only — never global. Global suppression rules are TOTALLY FORBIDDEN. Fix the code, never silence the linter.
- **Skill contract**: rules consumed by `skill_validate.py` / `skill_fix.py` must remain flat-key format and executable for `fix_auto: true`
