# Phase 1.2: TypedDict Migration - Discovery Report

**Date**: 2026-02-04  
**Status**: DISCOVERY COMPLETE  
**Task**: 01-02  
**Finding**: Most TypedDicts already converted to Pydantic models!

## Key Discovery

The codebase has **ALREADY MIGRATED** most TypedDicts to Pydantic models. Only 4 TypedDicts remain:

### TypedDicts Remaining (4 total)

1. **DispatcherConfig** (typings.py:398)
   - 11 fields (dispatcher_timeout_seconds, executor_workers, circuit_breaker_threshold, etc.)
   - Status: NOT YET CONVERTED
   - Action: Create Pydantic model in settings.py

2. **ContainerConfigDict** (typings.py:460)
   - 3 fields (compose_file, service, port)
   - Status: ✅ ALREADY CONVERTED (ContainerConfig in container.py:183)
   - Action: Update typings.py to use type alias

3. **BatchResultDictBase** (typings.py:782)
   - 2 fields (results, errors)
   - Status: NOT YET CONVERTED
   - Action: Create Pydantic model in generic.py

4. **RuntimeBootstrapOptions** (protocols.py)
   - Optional fields (config_type: type[BaseModel])
   - Status: NOT YET CONVERTED
   - Action: Create Pydantic model in service.py

## Pydantic Models Already Exist

**File**: `flext-core/src/flext_core/_models/container.py` (line 183)

```python
class ContainerConfig(BaseModel):
    """Model for container configuration.
    
    Replaces: dict[str, t.GeneralValueType] for container configuration storage.
    Provides type-safe configuration for DI container behavior.
    """
    
    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
    )
```

## Revised Phase 1.2 Plan

### Task 1: Create DispatcherConfig Model (0.3 days)

**File**: `flext-core/src/flext_core/_models/settings.py`

**Action**: Add Pydantic model for DispatcherConfig

```python
class DispatcherConfig(BaseModel):
    """Configuration for message dispatcher."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        extra="forbid",
    )
    
    dispatcher_timeout_seconds: float
    executor_workers: int
    circuit_breaker_threshold: int
    rate_limit_max_requests: int
    rate_limit_window_seconds: float
    max_retry_attempts: int
    retry_delay: float
    enable_timeout_executor: bool
    dispatcher_enable_logging: bool
    dispatcher_auto_context: bool
    dispatcher_enable_metrics: bool
```

### Task 2: Create BatchResultDict Model (0.3 days)

**File**: `flext-core/src/flext_core/_models/generic.py`

**Action**: Add Pydantic model for BatchResultDict

```python
class BatchResultDict(BaseModel):
    """Result dictionary for batch operations."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )
    
    results: list[t.GeneralValueType]
    errors: list[tuple[int, str]]
```

### Task 3: Create RuntimeBootstrapOptions Model (0.3 days)

**File**: `flext-core/src/flext_core/_models/service.py`

**Action**: Add Pydantic model for RuntimeBootstrapOptions

```python
class RuntimeBootstrapOptions(BaseModel):
    """Options for runtime bootstrap."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )
    
    config_type: type[BaseModel] | None = None
```

### Task 4: Update typings.py (0.3 days)

**Action**: Replace TypedDict definitions with type aliases

```python
# Remove TypedDict definitions
# Add type aliases
from flext_core._models.settings import DispatcherConfig
from flext_core._models.container import ContainerConfig as ContainerConfigDict
from flext_core._models.generic import BatchResultDict
from flext_core._models.service import RuntimeBootstrapOptions
```

### Task 5: Update imports across codebase (0.3 days)

**Action**: Find and update all usages

```bash
grep -r "DispatcherConfig" flext-core/src/ --include="*.py"
grep -r "ContainerConfigDict" flext-core/src/ --include="*.py"
grep -r "BatchResultDictBase" flext-core/src/ --include="*.py"
grep -r "RuntimeBootstrapOptions" flext-core/src/ --include="*.py"
```

## Revised Timeline

- Task 1: 0.3 days (DispatcherConfig)
- Task 2: 0.3 days (BatchResultDict)
- Task 3: 0.3 days (RuntimeBootstrapOptions)
- Task 4: 0.3 days (Update typings.py)
- Task 5: 0.3 days (Update imports)
- **Total**: 1.5 days

## Success Criteria

- [ ] DispatcherConfig Pydantic model created
- [ ] BatchResultDict Pydantic model created
- [ ] RuntimeBootstrapOptions Pydantic model created
- [ ] TypedDict definitions removed from typings.py
- [ ] TypedDict definitions removed from protocols.py
- [ ] All imports updated
- [ ] Type checking passes: `pyrefly src/`
- [ ] Linting passes: `ruff check src/`
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Coverage maintained: 80%+

## Next Steps

1. Create DispatcherConfig model in settings.py
2. Create BatchResultDict model in generic.py
3. Create RuntimeBootstrapOptions model in service.py
4. Update typings.py with type aliases
5. Update imports across codebase
6. Validate
7. Commit
8. Close Phase 1.2
