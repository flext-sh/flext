# Pydantic 2 Migration - Research Phase

**Phase**: 71-pydantic2-migration  
**Status**: RESEARCH  
**Date**: 2026-02-04  
**Goal**: Understand current state and establish migration patterns

## Current State Analysis

### Metrics (from exhaustive codebase analysis)

**cast() Usage**:
- Total: 627 usages
- In src/: ~127 usages
- In tests/: ~500 usages
- Projects affected: 20+

**TypedDict Usage**:
- Total: 305 definitions
- Largest projects:
  - flext-web: 89
  - flext-cli: 84
  - flext-ldif: 93
  - flext-core: 86
  - flext-dbt-oracle-wms: 22
  - Others: 31

**ConfigDict Status**:
- Already using Pydantic v2: 249+ models
- Inconsistent settings: Many models
- Missing ConfigDict: Some models

**Validator Status**:
- Pydantic v1 validators: 0 (already migrated)
- Pydantic v2 validators: Partial
- Modern patterns needed: @field_validator, @model_validator, computed_field

### Projects by Risk Level

**High Risk** (100+ errors or 80+ TypedDicts):
- flext-tap-oracle-wms: 100+ type errors
- flext-web: 89 TypedDicts
- flext-cli: 84 TypedDicts
- flext-ldif: 93 TypedDicts

**Medium Risk** (20-80 TypedDicts or 10+ cast()):
- flext-dbt-oracle-wms: 22 TypedDicts
- flext-target-oracle: 12 cast()
- flext-tap-ldap: 8 cast()
- Others: Various

**Low Risk** (< 10 TypedDicts, < 5 cast()):
- Most infrastructure projects
- Most API projects

## Key Decisions

1. **cast() Strategy**: Convert ALL to TypeGuards (including tests)
2. **TypedDict Strategy**: Convert ALL to structural Pydantic 2 models
3. **Namespace Pattern**: Hierarchical with max reuse
4. **ConfigDict**: Standardize across all models
5. **Validators**: Modernize to Pydantic 2.11+ patterns
6. **Execution**: Parallelized phases (35 days vs 38 days sequential)

## Migration Patterns

### TypeGuard Pattern
```python
from flext_core.utilities.guards import Guards

if Guards.is_config(obj):
    obj.app_name  # Type narrowed
```

### Hierarchical Models
```python
from flext_core.models import m

config: m.Core.Config = ...
entry: m.Ldif.Entry = ...
```

### Standard ConfigDict
```python
model_config = ConfigDict(
    validate_assignment=True,
    use_enum_values=True,
    extra="forbid",
    str_strip_whitespace=True,
)
```

## Success Criteria

- ✅ Zero cast() in ALL code
- ✅ Zero TypedDict (all converted)
- ✅ Standard ConfigDict across 127+ models
- ✅ Modern validators throughout
- ✅ All 29 projects passing `make validate`
- ✅ 80%+ test coverage maintained

## Timeline

- Phase 1: 4 days (foundation)
- Phases 2-6: 20 days (parallelized)
- Phase 7: 4 days (test suite)
- Phase 8: 4 days (problem project)
- Phase 9: 3 days (validation)
- **Total**: 35 days

## Next Steps

1. Create detailed phase plans
2. Create Beads issues
3. Execute Phase 1
4. Parallelize Phases 2-6
5. Complete test suite migration
6. Fix problem project
7. Final validation
