# Phase 1.2: TypedDict Migration - Execution Plan

**Date**: 2026-02-04  
**Status**: IN_PROGRESS  
**Task**: 01-02  
**Duration**: 1.5 days

## Current State Analysis

### TypedDicts Found

**In flext-core**: 4 TypedDicts total
1. `DispatcherConfig` (typings.py:398)
2. `ContainerConfigDict` (typings.py:460)
3. `BatchResultDictBase` (typings.py:782)
4. `RuntimeBootstrapOptions` (protocols.py)

**Status**: Much smaller than initially estimated (4 vs 86)

### FlextModels Structure

**File**: `flext-core/src/flext_core/models.py` (312 lines)

**Existing Nested Classes**:
- Entity
- ValueObject
- AggregateRoot
- DomainEvent
- OperationContext
- Service
- Configuration
- Health
- Operation
- Conversion
- Value
- Identity
- IdentityRequest
- ServiceRuntime
- Container
- ExecuteDispatchAttemptOptions
- Handler

**Status**: FlextModels already has hierarchical structure!

## Execution Plan

### Step 1: Analyze Each TypedDict (0.3 days)

#### TypedDict 1: DispatcherConfig

**Location**: typings.py:398

**Current Definition**:
```python
class DispatcherConfig(TypedDict, total=True):
    """Configuration for message dispatcher."""
    # Fields to be extracted
```

**Action**: Convert to Pydantic model in FlextModels.Configuration

#### TypedDict 2: ContainerConfigDict

**Location**: typings.py:460

**Action**: Convert to Pydantic model in FlextModels.Container

#### TypedDict 3: BatchResultDictBase

**Location**: typings.py:782

**Action**: Convert to Pydantic model in FlextModels.Operation

#### TypedDict 4: RuntimeBootstrapOptions

**Location**: protocols.py

**Action**: Convert to Pydantic model in FlextModels.ServiceRuntime

### Step 2: Create Pydantic Models (0.5 days)

For each TypedDict:

1. Read the TypedDict definition
2. Extract fields and types
3. Create Pydantic model with same structure
4. Add to appropriate FlextModels namespace
5. Add validation if needed

### Step 3: Update Imports (0.4 days)

1. Find all usages of each TypedDict
2. Update imports to use Pydantic models
3. Update type hints
4. Verify type checking

### Step 4: Remove TypedDict Definitions (0.2 days)

1. Remove TypedDict classes from typings.py
2. Remove TypedDict classes from protocols.py
3. Update typings.py to use type aliases pointing to models

### Step 5: Validate (0.1 days)

1. Run type checking: `pyrefly src/`
2. Run linting: `ruff check src/`
3. Run tests: `pytest tests/ -v`
4. Verify coverage: 80%+

## Detailed Execution

### Phase 1.2.1: Read TypedDict Definitions

**Command**:
```bash
cd flext-core
grep -A 10 "class DispatcherConfig" src/flext_core/typings.py
grep -A 10 "class ContainerConfigDict" src/flext_core/typings.py
grep -A 10 "class BatchResultDictBase" src/flext_core/typings.py
grep -A 10 "class RuntimeBootstrapOptions" src/flext_core/protocols.py
```

### Phase 1.2.2: Create Pydantic Models

**File**: `flext-core/src/flext_core/models.py`

**Add to FlextModels.Configuration**:
```python
class DispatcherConfig(FlextModels.Configuration):
    """Configuration for message dispatcher."""
    # Fields from TypedDict
```

**Add to FlextModels.Container**:
```python
class ContainerConfig(FlextModels.Container):
    """Configuration for container."""
    # Fields from TypedDict
```

**Add to FlextModels.Operation**:
```python
class BatchResultDict(FlextModels.Operation):
    """Result dictionary for batch operations."""
    # Fields from TypedDict
```

**Add to FlextModels.ServiceRuntime**:
```python
class RuntimeBootstrapOptions(FlextModels.ServiceRuntime):
    """Options for runtime bootstrap."""
    # Fields from TypedDict
```

### Phase 1.2.3: Update Imports

**Find usages**:
```bash
grep -r "DispatcherConfig" flext-core/src/ --include="*.py"
grep -r "ContainerConfigDict" flext-core/src/ --include="*.py"
grep -r "BatchResultDictBase" flext-core/src/ --include="*.py"
grep -r "RuntimeBootstrapOptions" flext-core/src/ --include="*.py"
```

**Update each file**:
```python
# BEFORE
from flext_core.typings import DispatcherConfig

# AFTER
from flext_core.models import m

config: m.Configuration.DispatcherConfig = ...
```

### Phase 1.2.4: Remove TypedDict Definitions

**Remove from typings.py**:
- Delete DispatcherConfig class
- Delete ContainerConfigDict class
- Delete BatchResultDictBase class

**Remove from protocols.py**:
- Delete RuntimeBootstrapOptions class

**Add type aliases in typings.py**:
```python
# Type aliases for convenience
DispatcherConfig = m.Configuration.DispatcherConfig
ContainerConfigDict = m.Container.ContainerConfig
BatchResultDictBase = m.Operation.BatchResultDict
RuntimeBootstrapOptions = m.ServiceRuntime.RuntimeBootstrapOptions
```

### Phase 1.2.5: Validation

```bash
# Type checking
pyrefly src/flext_core/

# Linting
ruff check src/flext_core/

# Tests
pytest tests/ -v

# Coverage
pytest tests/ --cov=flext_core --cov-report=term-missing
```

## Commit Strategy

Create atomic commits:

```bash
# Commit 1: Add Pydantic models
git commit -m "feat(flext-core): add Pydantic models for TypedDicts

- Add DispatcherConfig to FlextModels.Configuration
- Add ContainerConfig to FlextModels.Container
- Add BatchResultDict to FlextModels.Operation
- Add RuntimeBootstrapOptions to FlextModels.ServiceRuntime"

# Commit 2: Update imports
git commit -m "refactor(flext-core): update imports to use Pydantic models

- Replace TypedDict imports with model imports
- Update type hints across codebase
- Maintain backward compatibility with type aliases"

# Commit 3: Remove TypedDict definitions
git commit -m "refactor(flext-core): remove TypedDict definitions

- Remove TypedDict classes from typings.py
- Remove TypedDict classes from protocols.py
- Add type aliases for backward compatibility"
```

## Success Criteria

- [ ] All 4 TypedDicts converted to Pydantic models
- [ ] All imports updated
- [ ] Type checking passes: `pyrefly src/`
- [ ] Linting passes: `ruff check src/`
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Coverage maintained: 80%+
- [ ] No TypedDict definitions remaining

## Timeline

- Step 1: 0.3 days (analyze)
- Step 2: 0.5 days (create models)
- Step 3: 0.4 days (update imports)
- Step 4: 0.2 days (remove definitions)
- Step 5: 0.1 days (validate)
- **Total**: 1.5 days

## Next Steps

1. Read TypedDict definitions
2. Create Pydantic models
3. Update imports
4. Remove TypedDict definitions
5. Validate
6. Commit
7. Close Phase 1.2
8. Start Phase 1.3
