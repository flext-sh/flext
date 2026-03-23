# Target-* Validation Types - Quick Reference

## What Was Changed

All 5 target-* projects converted from bare Pydantic Field constraints to `t.*` validation types:
- **flext-target-ldif:** 17 conversions ✅
- **flext-target-ldap:** 15 conversions ✅
- **flext-target-oracle:** 14 conversions ✅
- **flext-target-oracle-oic:** Already clean ✅
- **flext-target-oracle-wms:** 3 conversions ✅

## Type Mapping Reference

| Old Pattern | New Type | Example |
|---|---|---|
| `Field(ge=0)` on int | `t.NonNegativeInt` | counts, sizes |
| `Field(ge=1)` on int | `t.PositiveInt` | timeouts, ports |
| `Field(gt=0)` on int | `t.PositiveInt` | batch size |
| `Field(ge=0.0)` on float | `t.NonNegativeFloat` | durations |
| `Field(gt=0.0)` on float | `t.PositiveFloat` | timeouts |
| `Field(min_length=1)` on str | `t.NonEmptyStr` | names, paths |
| `Field(ge=1, le=10000)` on int | `t.BatchSize` | batch_size fields |
| `Field(ge=1, le=65535)` on int | `t.PortNumber` | port numbers |

## Import Statement

```python
# Add this import to your file
from flext_core.typings import t

# Or use local import if available
from .typings import t
```

## Usage Examples

### Before
```python
class Config(FlextModels.ArbitraryTypesModel):
    batch_size: Annotated[int, Field(ge=1, le=10000)]
    timeout: Annotated[int, Field(ge=1)]
    name: Annotated[str, Field(min_length=1)]
    duration: Annotated[float, Field(ge=0.0)]
    port: Annotated[int, Field(ge=1, le=65535)]
```

### After
```python
from flext_core.typings import t


class Config(FlextModels.ArbitraryTypesModel):
    batch_size: Annotated[t.BatchSize, Field(...)]
    timeout: Annotated[t.PositiveInt, Field(...)]
    name: Annotated[t.NonEmptyStr, Field(...)]
    duration: Annotated[t.NonNegativeFloat, Field(...)]
    port: Annotated[t.PortNumber, Field(...)]
```

## Files That Changed

```
✅ flext-target-ldif/src/flext_target_ldif/models.py
✅ flext-target-ldap/src/flext_target_ldap/models.py
✅ flext-target-oracle/src/flext_target_oracle/models.py
✅ flext-target-oracle-wms/src/flext_target_oracle_wms/models.py
ℹ️  flext-target-oracle-oic/src/flext_target_oracle_oic/models.py (no changes needed)
```

## Why This Matters

1. **Consistency:** All projects follow the same pattern
2. **Clarity:** Type signature shows intent without reading Field()
3. **Portability:** Works with any framework that understands annotated-types
4. **Type Safety:** Better IDE support and mypy/pyright checking
5. **Maintenance:** Single source of truth in flext-core

## Available t.* Types

```python
# Strings
t.NonEmptyStr  # min_length=1

# Integers
t.PositiveInt  # gt=0
t.NonNegativeInt  # ge=0
t.PortNumber  # 1-65535
t.RetryCount  # 0-10
t.WorkerCount  # 1-100
t.HttpStatusCode  # 100-599
t.BatchSize  # 1-10000
t.MaxLength  # ge=1

# Floats
t.PositiveFloat  # gt=0.0
t.NonNegativeFloat  # ge=0.0
t.PositiveTimeout  # 0.0-300.0
t.BackoffMultiplier  # ge=1.0
t.Percentage  # 0-100%
t.DecimalFraction  # 0-1.0
```

## Testing After Changes

```bash
# Run tests for each project
cd flext-target-ldif && make check && make test
cd flext-target-ldap && make check && make test
cd flext-target-oracle && make check && make test
cd flext-target-oracle-oic && make check && make test
cd flext-target-oracle-wms && make check && make test
```

## Questions?

Refer to:
- `/home/marlonsc/flext/.planning/TARGET_CONVERSION_SUMMARY.md` - Detailed reference
- `/home/marlonsc/flext/.planning/TARGET_VALIDATION_TYPES_REFACTOR.md` - Full documentation
- `/home/marlonsc/flext/flext-core/src/flext_core/_typings/validation.py` - Type definitions

---

**Status:** ✅ Refactor Complete - Ready for Testing
**Backward Compatible:** Yes - No breaking changes
