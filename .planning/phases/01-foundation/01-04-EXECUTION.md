# Phase 1.4: Standardize ConfigDict Settings - Execution Plan

**Date**: 2026-02-04  
**Status**: IN_PROGRESS  
**Task**: 01-04  
**Duration**: 0.5 days

## Current State Analysis

### ConfigDict Status

- **Models with ConfigDict**: 41
- **Total BaseModel classes**: 50
- **Models without ConfigDict**: 9

### Models Without ConfigDict

1. **ProtocolModel** (protocols.py)
   - Base class for Pydantic models that implement protocols
   - Uses custom metaclass (ProtocolModelMeta)
   - Status: May need special handling

2. **Metadata** (runtime.py)
   - Minimal metadata model
   - Implements p.Log.Metadata protocol
   - Status: Add standard ConfigDict

3. **AutoConfig** (settings.py)
   - Auto-configuration model for dynamic config creation
   - Status: Add standard ConfigDict

4. **MiddlewareConfig** (_models/settings.py)
   - Status: Add standard ConfigDict

5. **RateLimiterState** (_models/settings.py)
   - Status: Add standard ConfigDict

6. **ContextScopeData** (_models/context.py)
   - Status: Add standard ConfigDict

7. **ContextStatistics** (_models/context.py)
   - Status: Add standard ConfigDict

8. **ContextMetadata** (_models/context.py)
   - Status: Add standard ConfigDict

9. **ContextDomainData** (_models/context.py)
   - Status: Add standard ConfigDict

10. **Pagination** (_models/cqrs.py)
    - Status: Add standard ConfigDict

## Standard ConfigDict Settings

### Production Models (Default)

```python
model_config = ConfigDict(
    validate_assignment=True,
    use_enum_values=True,
    extra="forbid",
    str_strip_whitespace=True,
)
```

### Immutable Value Objects

```python
model_config = ConfigDict(
    frozen=True,
    validate_assignment=True,
    extra="forbid",
)
```

### API Response Models

```python
model_config = ConfigDict(
    extra="ignore",
    validate_assignment=True,
    use_enum_values=True,
)
```

## Execution Plan

### Step 1: Add ConfigDict to Models (0.3 days)

For each model without ConfigDict:

1. **Metadata** (runtime.py)
   ```python
   model_config = ConfigDict(
       validate_assignment=True,
       use_enum_values=True,
       extra="forbid",
   )
   ```

2. **AutoConfig** (settings.py)
   ```python
   model_config = ConfigDict(
       validate_assignment=True,
       use_enum_values=True,
       extra="forbid",
   )
   ```

3. **MiddlewareConfig** (_models/settings.py)
   ```python
   model_config = ConfigDict(
       validate_assignment=True,
       use_enum_values=True,
       extra="forbid",
   )
   ```

4. **RateLimiterState** (_models/settings.py)
   ```python
   model_config = ConfigDict(
       validate_assignment=True,
       use_enum_values=True,
       extra="forbid",
   )
   ```

5. **Context Models** (_models/context.py)
   ```python
   model_config = ConfigDict(
       validate_assignment=True,
       use_enum_values=True,
       extra="forbid",
   )
   ```

6. **Pagination** (_models/cqrs.py)
   ```python
   model_config = ConfigDict(
       validate_assignment=True,
       use_enum_values=True,
       extra="forbid",
   )
   ```

### Step 2: Handle ProtocolModel (0.1 days)

**Decision**: ProtocolModel uses custom metaclass, may not need ConfigDict
- Verify if ConfigDict is compatible with ProtocolModelMeta
- If compatible, add standard ConfigDict
- If not, document exception

### Step 3: Verify Consistency (0.1 days)

Check that all models follow one of the standard patterns:
- Production models: standard ConfigDict
- Immutable models: frozen=True
- API response models: extra="ignore"

### Step 4: Validate (0.1 days)

```bash
# Type checking
pyrefly src/flext_core/

# Linting
ruff check src/flext_core/

# Tests
pytest tests/ -v
```

## Commit Strategy

Create atomic commits per file:

```bash
# Commit 1: Add ConfigDict to runtime.py
git commit -m "refactor(flext-core): add ConfigDict to Metadata model

- Add standard ConfigDict to Metadata class
- Enables validation_assignment and extra='forbid'"

# Commit 2: Add ConfigDict to settings.py
git commit -m "refactor(flext-core): add ConfigDict to AutoConfig model

- Add standard ConfigDict to AutoConfig class
- Enables validation_assignment and extra='forbid'"

# Commit 3: Add ConfigDict to _models/settings.py
git commit -m "refactor(flext-core): add ConfigDict to settings models

- Add ConfigDict to MiddlewareConfig
- Add ConfigDict to RateLimiterState
- Standardizes configuration validation"

# Commit 4: Add ConfigDict to _models/context.py
git commit -m "refactor(flext-core): add ConfigDict to context models

- Add ConfigDict to ContextScopeData
- Add ConfigDict to ContextStatistics
- Add ConfigDict to ContextMetadata
- Add ConfigDict to ContextDomainData
- Standardizes context validation"

# Commit 5: Add ConfigDict to _models/cqrs.py
git commit -m "refactor(flext-core): add ConfigDict to Pagination model

- Add standard ConfigDict to Pagination class
- Enables validation_assignment and extra='forbid'"
```

## Success Criteria

- [ ] All 9 models without ConfigDict now have it
- [ ] ConfigDict settings are consistent
- [ ] Type checking passes: `pyrefly src/`
- [ ] Linting passes: `ruff check src/`
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Coverage maintained: 80%+

## Timeline

- Step 1: 0.3 days (add ConfigDict)
- Step 2: 0.1 days (handle ProtocolModel)
- Step 3: 0.1 days (verify consistency)
- Step 4: 0.1 days (validate)
- **Total**: 0.5 days

## Next Steps

1. Add ConfigDict to models
2. Handle ProtocolModel
3. Verify consistency
4. Validate
5. Commit
6. Close Phase 1.4
7. Start Phase 1.5 (Validation & Documentation)
