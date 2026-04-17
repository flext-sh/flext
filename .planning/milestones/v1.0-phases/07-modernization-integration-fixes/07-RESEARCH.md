# Phase 7: Modernization & Integration Fixes - Research

**Researched:** 2026-03-24
**Domain:** Python 3.13 modernization, Pydantic strict mode, circular imports
**Confidence:** HIGH

## Summary

Phase 7 addresses four tightly-scoped technical issues: (1) circular import in `_utilities_loader.py`, (2) StrEnum + strict Pydantic coercion mismatch breaking tests, (3) custom deprecation framework replacement with PEP 702, and (4) UserDict/UserString elimination.

Investigation reveals the circular import may already be resolved (import succeeds in current state — the 2 collection errors in flext-infra are `OutputBackend` attribute errors, not circular imports). The StrEnum coercion issue is confirmed and reproduced — `CreateKwargsParams` extends `FlextModels.Value` (ContractModel with `strict=True`), and both the model default and call sites pass string literals instead of enum instances. The deprecation framework is already dead code with zero callers. UserDict/UserString grep returns zero hits in `*/src/**/*.py`.

**Primary recommendation:** Fix StrEnum coercion with `m.BeforeValidator` on affected fields (fewer touch points than fixing all call sites + defaults). Verify circular import is already resolved. Delete or simplify deprecation.py. Confirm MOD-06 already satisfied.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

- D-01: Break circular import in `_utilities_loader.py` line 18
- D-02: Lazy/deferred imports or restructure; TYPE_CHECKING guard acceptable for type-only imports
- D-03: Fix StrEnum + strict Pydantic coercion mismatch
- D-04: Fix at call sites first; if too many, add `m.BeforeValidator`. Do NOT relax `strict=True`
- D-05: Replace `FlextUtilitiesDeprecation` with `warnings.deprecated` (PEP 702)
- D-06: Use `@warnings.deprecated` directly, remove custom class
- D-07: Replace UserDict/UserString with Pydantic BaseModel; verify and mark complete if already done

### Claude's Discretion

- Exact import restructuring strategy for circular import
- Whether to use m.BeforeValidator or fix call sites for StrEnum coercion
- How to migrate existing @deprecated decorators to PEP 702 form
- Test file adjustments needed for each fix

### Deferred Ideas (OUT OF SCOPE)

None.
</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MOD-02 | `warnings.deprecated` (PEP 702) replaces custom `FlextUtilitiesDeprecation` framework | deprecation.py is dead code with zero callers; already imports `warnings.deprecated` internally. Delete class, update `__init__.py` exports |
| MOD-06 | `UserDict`/`UserString` usages replaced with Pydantic `BaseModel` | Grep confirms zero `UserDict`/`UserString` in `*/src/**/*.py`. Already satisfied — verify and mark complete |
| INFRA-05 | `make pyrefly-repo` policy gate enforces 0 violations | Already marked complete in REQUIREMENTS.md. Circular import fix ensures `make pyre` stays clean |
</phase_requirements>

## Architecture Patterns

### Circular Import Pattern (D-01/D-02)

**Current state:** `_utilities_loader.py` line 18 does `from flext_infra import FlextInfraUtilitiesParsing, c, m, p` at module level. This is the standard pattern used by ALL files in `flext-infra/refactor/` (30+ files do the same). Investigation shows the import currently succeeds without error — the 2 test collection failures in flext-infra are unrelated (`OutputBackend` attribute error).

**Recommendation:** Verify whether the circular import is still an issue. If `make pyre` passes and the 12 test collections referenced in the audit now succeed, this item may already be resolved by prior work. If it still fails under specific conditions, move the module-level import inside functions that use `FlextInfraUtilitiesParsing`.

### StrEnum Coercion Fix (D-03/D-04)

**Root cause confirmed:** `CreateKwargsParams` extends `FlextModels.Value` which inherits from `ContractModel` with `strict=True`. The `fmt` field is typed as `c.Tests.Format` (StrEnum) but has `default="auto"` (string literal). With strict mode, Pydantic requires actual enum instances.

**Affected locations:**

- `flext-tests/src/flext_tests/models.py:426` — field default `"auto"` should be `c.Tests.Format.AUTO`
- `flext-tests/src/flext_tests/files.py:316` — hardcoded `fmt="auto"` should use enum
- Additional call sites in test files (6 occurrences in `test_files.py`)

**Recommendation:** Use `m.BeforeValidator` approach. Rationale:

1. The model's own `default="auto"` proves string-to-enum coercion is the intended API
2. `use_enum_values=True` is already set on the settings (values stored as strings)
3. `m.BeforeValidator(lambda v: c.Tests.Format(v) if isinstance(v, str) else v)` on the `fmt` field resolves all call sites at once
4. Fewer code changes, lower regression risk

```python
from pydantic import m.BeforeValidator

fmt: Annotated[
    c.Tests.Format,
    m.BeforeValidator(lambda v: c.Tests.Format(v) if isinstance(v, str) else v),
    u.Field(default=c.Tests.Format.AUTO, description="File format override."),
]
```

**Also check:** Other StrEnum fields on strict models across the codebase that may have the same pattern. Grep for `StrEnum` fields with string defaults on strict models.

### Deprecation Framework (D-05/D-06)

**Current state:** `deprecation.py` is marked as dead code (line 1 comment added in Phase 4). It already imports `from warnings import deprecated as _stdlib_deprecated` and wraps it. Zero callers in production `src/` code.

**Action:**

1. Remove `FlextUtilitiesDeprecation` class from `deprecation.py`
2. Update auto-generated `__init__.py` exports (run `make codegen`)
3. Remove from `utilities.py` facade MRO
4. Since `_utilities/*` is FROZEN per AGENTS.md 10.2, the file itself should be emptied or reduced to the `__all__` with nothing exported

### UserDict/UserString (D-07)

**Grep result:** Zero hits for `UserDict` or `UserString` in any `*/src/**/*.py` file. Already satisfied. Mark complete with verification evidence.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| StrEnum coercion | Manual str-to-enum conversion at every call site | `m.BeforeValidator` on Pydantic field | Single fix point, validated by Pydantic |
| Deprecation warnings | Custom `FlextUtilitiesDeprecation` wrapper | `warnings.deprecated` (PEP 702) | stdlib, zero maintenance |

## Common Pitfalls

### Pitfall 1: Strict mode + use_enum_values interaction

**What goes wrong:** `use_enum_values=True` stores the string value after validation, but `strict=True` rejects string input before validation reaches the enum coercion step.
**How to avoid:** Use `m.BeforeValidator` to coerce strings to enum instances before strict validation runs. The validator runs in the "before" phase, before Pydantic's strict type check.

### Pitfall 2: FROZEN _utilities policy

**What goes wrong:** Deleting files from `_utilities/` violates AGENTS.md 10.2 freeze policy.
**How to avoid:** Empty the file contents but keep the file. Or get explicit operator approval to delete. The Phase 4 decision already marked it as dead code.

### Pitfall 3: Auto-generated **init**.py

**What goes wrong:** Manually editing `__init__.py` to remove exports breaks on next `make codegen`.
**How to avoid:** Remove the class from the source file, then run `make codegen` to regenerate exports.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.4+ |
| Settings file | `pyproject.toml` [tool.pytest] |
| Quick run command | `.venv/bin/python -m pytest {project}/tests/ -x` |
| Full suite command | `make test` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MOD-02 | No FlextUtilitiesDeprecation in exports | smoke | `sg --pattern 'FlextUtilitiesDeprecation' --lang py flext-core/src/` | N/A (grep-based) |
| MOD-06 | No UserDict/UserString in src | smoke | `sg --pattern 'UserDict' --lang py` | N/A (grep-based) |
| INFRA-05 | make pyre passes | integration | `make pyre` | N/A (make target) |
| — | StrEnum coercion fixed | unit | `.venv/bin/python -m pytest flext-tests/tests/ -x` | test_files.py exists |
| — | Circular import resolved | integration | `.venv/bin/python -m pytest flext-infra/tests/ --collect-only` | existing tests |

### Sampling Rate

- **Per task commit:** `.venv/bin/python -m pytest {affected_project}/tests/ -x`
- **Per wave merge:** `make test`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

None -- existing test infrastructure covers all phase requirements.

## Sources

### Primary (HIGH confidence)

- Direct code inspection of `_utilities_loader.py`, `deprecation.py`, `models.py`, `files.py`, `base.py`
- Live pytest execution confirming StrEnum coercion error
- Live grep confirming zero UserDict/UserString usage

### Secondary (MEDIUM confidence)

- `.planning/v1.0-MILESTONE-AUDIT.md` for issue descriptions (circular import may be stale)

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - no new dependencies needed
- Architecture: HIGH - all fixes are in existing codebase with clear patterns
- Pitfalls: HIGH - reproduced the StrEnum issue, verified deprecation state

**Research date:** 2026-03-24
**Valid until:** 2026-04-24 (stable — internal codebase fixes only)
