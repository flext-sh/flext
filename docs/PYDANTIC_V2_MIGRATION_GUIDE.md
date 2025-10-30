# Pydantic v1 → v2 Migration Guide - FLEXT Ecosystem

**Purpose**: Step-by-step guide for migrating FLEXT projects from Pydantic v1 to v2
**Target Audience**: FLEXT development team
**Status**: Complete - All 29 projects migrated and verified
**Last Updated**: 2025-10-22

---

## Table of Contents

1. [Pre-Migration Checklist](#pre-migration-checklist)
2. [Phase 1: Project Assessment](#phase-1-project-assessment)
3. [Phase 2: Configuration Update](#phase-2-configuration-update)
4. [Phase 3: Validator Modernization](#phase-3-validator-modernization)
5. [Phase 4: BeforeValidator Removal](#phase-4-beforevalidator-removal)
6. [Phase 5: Method Name Updates](#phase-5-method-name-updates)
7. [Phase 6: Domain Type Application](#phase-6-domain-type-application)
8. [Phase 7: Testing & Validation](#phase-7-testing--validation)
9. [Phase 8: Documentation & Sign-off](#phase-8-documentation--sign-off)
10. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## Pre-Migration Checklist

Before starting migration on any project:

- [ ] Create feature branch: `git checkout -b pydantic-v2-migration`
- [ ] Ensure all tests passing: `make test` (baseline)
- [ ] Commit current state: `git add . && git commit -m "Before: Pydantic v1 baseline"`
- [ ] Review project structure: Identify all config files
- [ ] Check for custom validators: `grep -r "@validator" src/`
- [ ] Check for BeforeValidator usage: `grep -r "BeforeValidator" src/`
- [ ] Identify environment variable coercion: `grep -r "_coerce" src/`

---

## Phase 1: Project Assessment

### Step 1.1: Identify Model Files

**Command**:

```bash
# Find all files with BaseModel
find src -name "*.py" -exec grep -l "class.*BaseModel" {} \;

# Count total models
find src -name "*.py" -exec grep -c "class.*BaseModel" {} \; | paste -sd+ | bc
```

**Expected Output**:

```
src/config.py - contains 5 models
src/models.py - contains 8 models
src/handlers.py - contains 2 models
Total: 15 models to migrate
```

### Step 1.2: Identify All Validator Types

**Commands**:

```bash
# Find @validator decorators (v1 pattern)
grep -rn "@validator" src/ | wc -l

# Find custom validator functions
grep -rn "def _validate" src/ | wc -l
grep -rn "def validate_" src/ | wc -l

# Find BeforeValidator usage
grep -rn "BeforeValidator" src/ | wc -l

# Find custom coercion functions
grep -rn "def _coerce" src/ | wc -l
```

**Assessment Template**:

```
Project: flext-ldif
Models: 12
@validator decorators: 3
Custom validators: 2
BeforeValidator uses: 5
Coercion functions: 2
Complexity: Medium
Estimated time: 2-3 hours
```

### Step 1.3: Check Dependencies

**Verify** `pyproject.toml`:

```toml
[tool.poetry.dependencies]
pydantic = "^2.0"  # ✅ Should be v2
flext-core = "^0.9.0"  # ✅ Required for domain types
```

---

## Phase 2: Configuration Update

### Step 2.1: Update Model Configuration

**Find all instances**:

```bash
grep -rn "class Config:" src/ --include="*.py"
```

**For each file, replace**:

```python
# ❌ OLD (Pydantic v1)
class MyModel(BaseModel):
    field1: str
    field2: int

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        orm_mode = True

# ✅ NEW (Pydantic v2)
from pydantic import ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,  # Renamed from allow_population_by_field_name
        from_attributes=True,   # Renamed from orm_mode
    )

    field1: str
    field2: int
```

**Configuration Mapping Table**:

| v1 Setting                       | v2 Setting                | Notes                 |
| -------------------------------- | ------------------------- | --------------------- |
| `validate_assignment`            | `validate_assignment`     | Same name             |
| `arbitrary_types_allowed`        | `arbitrary_types_allowed` | Same name             |
| `allow_population_by_field_name` | `populate_by_name`        | Renamed               |
| `orm_mode`                       | `from_attributes`         | Renamed               |
| `json_schema_extra`              | `json_schema_extra`       | Same name             |
| `validate_default`               | `validate_default`        | Same name (new in v2) |
| `str_strip_whitespace`           | `str_strip_whitespace`    | Same name (new in v2) |

### Step 2.2: Verify Configuration Update

**Test**:

```bash
# Ensure models can be imported
PYTHONPATH=src python -c "from mymodule import MyModel; print('✅ Config OK')"

# Verify configuration is applied
python -c "from mymodule import MyModel; print(MyModel.model_config)"
```

---

## Phase 3: Validator Modernization

### Step 3.1: Update @validator to @field_validator

**Find**:

```bash
grep -rn "@validator" src/ --include="*.py"
```

**Replace Pattern**:

```python
# ❌ OLD (v1)
from pydantic import validator

class Config(BaseModel):
    email: str

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v

# ✅ NEW (v2)
from pydantic import field_validator

class Config(BaseModel):
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
```

**Key Changes**:

1. Import `field_validator` instead of `validator`
2. Add `@classmethod` decorator
3. Add type annotations: parameter and return type
4. No other logic changes

### Step 3.2: Update @root_validator to @model_validator

**Find**:

```bash
grep -rn "@root_validator" src/ --include="*.py"
```

**Replace Pattern**:

```python
# ❌ OLD (v1)
from pydantic import root_validator

class Config(BaseModel):
    password: str
    password_confirm: str

    @root_validator
    def verify_passwords_match(cls, values):
        pwd1 = values.get('password')
        pwd2 = values.get('password_confirm')
        if pwd1 != pwd2:
            raise ValueError('Passwords do not match')
        return values

# ✅ NEW (v2)
from pydantic import model_validator

class Config(BaseModel):
    password: str
    password_confirm: str

    @model_validator(mode='after')
    def verify_passwords_match(self) -> 'Config':
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self
```

**Key Changes**:

1. `@root_validator` → `@model_validator(mode='after')`
2. Remove `@classmethod`, use `self` instead
3. Return `self` instead of `values`
4. Access fields via `self.field_name` instead of `values['field_name']`

---

## Phase 4: BeforeValidator Removal

### Step 4.1: Find All BeforeValidator Usage

```bash
grep -rn "BeforeValidator" src/ --include="*.py"
grep -rn "Annotated\[" src/ --include="*.py"
```

### Step 4.2: Understand What BeforeValidator Does

**Pattern in v1**:

```python
from typing import Annotated
from pydantic import BeforeValidator

def _coerce_bool(value: object) -> bool:
    """Convert string 'true' to boolean True"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {'true', '1', 'yes', 'on'}
    return bool(value)

class Config(BaseModel):
    debug: Annotated[bool, BeforeValidator(_coerce_bool)] = False
```

**Why Remove**:

- ❌ Pydantic v2 handles type coercion natively
- ❌ Custom coercion functions duplicate v2 functionality
- ❌ Code becomes simpler without custom functions
- ❌ Performance improved with native coercion

### Step 4.3: Remove BeforeValidator Pattern

```python
# ❌ BEFORE
from typing import Annotated
from pydantic import BeforeValidator, Field

def _coerce_port(value: object) -> int:
    if isinstance(value, str):
        return int(value)
    return value

class Config(BaseModel):
    port: Annotated[int, BeforeValidator(_coerce_port)] = Field(
        ge=1, le=65535
    )

# ✅ AFTER (Simple!)
from pydantic import Field

class Config(BaseModel):
    # Pydantic v2 handles string→int coercion natively
    port: int = Field(ge=1, le=65535)
```

**Process**:

1. Locate `_coerce_*` function definition
2. Verify it's NOT used elsewhere: `grep -n "_coerce_function_name" src/**/*.py`
3. Remove function definition (usually 5-15 lines)
4. Remove `BeforeValidator` from field type
5. Remove `Annotated` wrapper if no other annotations
6. Remove `Annotated` import if unused
7. Verify: `make type-check && make test`

### Step 4.4: Verify Coercion Functions Removed

```bash
# Verify no dead _coerce functions remain
grep -rn "def _coerce" src/ --include="*.py"
# Should return: (empty)

# Verify no BeforeValidator remains
grep -rn "BeforeValidator" src/ --include="*.py"
# Should return: (empty)

# Verify imports cleaned up
grep -rn "from typing import.*Annotated" src/ --include="*.py"
# Should not have orphaned Annotated imports
```

---

## Phase 5: Method Name Updates

### Step 5.1: Replace .dict() with .model_dump()

```bash
# Find all .dict() calls
grep -rn "\.dict(" src/ tests/ --include="*.py"
```

**Replace**:

```python
# ❌ OLD
config_dict = model.dict()
config_dict_exclude = model.dict(exclude={'password'})

# ✅ NEW
config_dict = model.model_dump()
config_dict_exclude = model.model_dump(exclude={'password'})
```

### Step 5.2: Replace .JSON() with .model_dump_JSON()

```bash
# Find all .json() calls
grep -rn "\.json(" src/ tests/ --include="*.py"
```

**Replace**:

```python
# ❌ OLD
json_str = model.json()
json_str_pretty = model.json(indent=2)

# ✅ NEW
json_str = model.model_dump_json()
json_str_pretty = model.model_dump_json(indent=2)
```

### Step 5.3: Replace .parse_obj() with .model_validate()

```bash
# Find all .parse_obj() calls
grep -rn "\.parse_obj(" src/ tests/ --include="*.py"
```

**Replace**:

```python
# ❌ OLD
data = {"name": "John", "age": 30}
model = MyModel.parse_obj(data)

# ✅ NEW
data = {"name": "John", "age": 30}
model = MyModel.model_validate(data)
```

### Step 5.4: Replace .parse_raw() with .model_validate_JSON()

```bash
# Find all .parse_raw() calls
grep -rn "\.parse_raw(" src/ tests/ --include="*.py"
```

**Replace**:

```python
# ❌ OLD
json_str = '{"name": "John", "age": 30}'
model = MyModel.parse_raw(json_str)

# ✅ NEW
json_str = '{"name": "John", "age": 30}'
model = MyModel.model_validate_json(json_str)
```

### Step 5.5: Verify All Methods Updated

```bash
# No old methods should remain
grep -rn "\.dict(\|\.json(\|\.parse_obj(\|\.parse_raw(" src/ --include="*.py"
# Should return: (empty)

# Verify new methods used instead
grep -rn "\.model_dump\|\.model_validate" src/ --include="*.py"
# Should show all replacements
```

---

## Phase 6: Domain Type Application

### Step 6.1: Identify Applicable Fields

**Find fields that are candidates for domain types**:

```bash
# Network ports
grep -rn "ge=1.*le=65535\|ge=1.*le=.*MAX_PORT" src/ --include="*.py"

# Timeouts
grep -rn "gt=0.*le=300\|Field.*gt=0" src/ --include="*.py"

# Retry counts
grep -rn "ge=0.*le=10\|Field.*retry" src/ --include="*.py" -i

# Log levels
grep -rn "Literal\[.*DEBUG.*INFO\|LogLevel" src/ --include="*.py"
```

### Step 6.2: Import Domain Types

**Add import to file**:

```python
from flext_core import (
    PortNumber,
    TimeoutSeconds,
    RetryCount,
    LogLevel,
)
```

### Step 6.3: Apply Domain Types

**Before**:

```python
class Config(BaseModel):
    port: int = Field(
        default=389,
        ge=1,
        le=65535,
        description="LDAP port"
    )
    timeout: float = Field(
        default=30.0,
        gt=0,
        le=300,
        description="Operation timeout"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Max retry attempts"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
```

**After**:

```python
from flext_core import PortNumber, TimeoutSeconds, RetryCount, LogLevel

class Config(BaseModel):
    port: PortNumber = Field(
        default=389,
        description="LDAP port"  # Constraints now in domain type
    )
    timeout: TimeoutSeconds = Field(
        default=30.0,
        description="Operation timeout"
    )
    max_retries: RetryCount = Field(
        default=3,
        description="Max retry attempts"
    )
    log_level: LogLevel = Field(
        default="INFO",
        description="Logging level"
    )
```

### Step 6.4: Verify Domain Types

```bash
# Import domain types in Python
PYTHONPATH=src python -c "
from flext_core import PortNumber, TimeoutSeconds, RetryCount, LogLevel
from mymodule import Config

# Validate constraints still work
try:
    Config(port=99999)  # Should fail
except Exception as e:
    print(f'✅ Port validation works: {e}')

try:
    Config(timeout=-1)  # Should fail
except Exception as e:
    print(f'✅ Timeout validation works: {e}')

print('✅ All domain types working correctly')
"
```

---

## Phase 7: Testing & Validation

### Step 7.1: Run Unit Tests

```bash
# Run all tests
make test

# Or with pytest directly
PYTHONPATH=src poetry run pytest tests/unit/ -v

# Check coverage
PYTHONPATH=src poetry run pytest tests/ --cov=src --cov-report=term-missing
```

### Step 7.2: Type Checking

```bash
# Run Pyrefly (recommended for FLEXT)
make type-check

# Or manually
PYTHONPATH=src poetry run pyrefly check src/ --show-error-codes

# Check for type errors
PYTHONPATH=src python -m mypy src/ --strict
```

### Step 7.3: Linting

```bash
# Ruff linting
make lint

# Or manually
ruff check src/
```

### Step 7.4: Security Scanning

```bash
# Bandit security
make security

# Or manually
poetry run bandit -r src/
```

### Step 7.5: Comprehensive Validation

```bash
# All quality gates
make validate

# Should output:
# ✅ Lint: PASS
# ✅ Type-check: PASS
# ✅ Tests: PASS
# ✅ Security: PASS
```

### Step 7.6: Pydantic v2 Audit

```bash
# Run Pydantic v2 compliance audit
python ../scripts/audit_pydantic_v2.py --project .

# Expected output:
# Status: PASS
# Total violations: 0
# Total Python files: XX
# Compliance: 100%
```

---

## Phase 8: Documentation & Sign-off

### Step 8.1: Update CLAUDE.md

Add Pydantic v2 compliance section to project's `CLAUDE.md`:

```markdown
## Pydantic v2 Compliance Standards

**Status**: ✅ Fully Pydantic v2 Compliant
**Verified**: [DATE]

### Standards Applied

This project adheres to FLEXT ecosystem Pydantic v2 standards:

1. **Model Configuration**: All models use `model_config = ConfigDict()`
2. **Validators**: All use `@field_validator` and `@model_validator` decorators
3. **Serialization**: All use `.model_dump()` and `.model_dump_json()` methods
4. **Deserialization**: All use `.model_validate()` and `.model_validate_json()` methods
5. **Domain Types**: Use FLEXT domain types (PortNumber, TimeoutSeconds, RetryCount, LogLevel)
6. **No Duplication**: Zero Pydantic v1 patterns or custom coercion functions

### Reference Guide

For detailed standards and patterns, see: `/flext-core/docs/PYDANTIC_V2_PATTERNS.md`
```

### Step 8.2: Run Final Audit

```bash
# Comprehensive ecosystem audit
make audit-pydantic-v2

# All projects should show PASS
```

### Step 8.3: Create Commit

```bash
# Stage all changes
git add -A

# Create commit with proper message
git commit -m "refactor: Modernize to Pydantic v2 standards

- Replace class Config with model_config = ConfigDict()
- Update @validator to @field_validator
- Remove BeforeValidator patterns (native coercion in v2)
- Replace .dict() with .model_dump()
- Replace .parse_obj() with .model_validate()
- Apply domain types (PortNumber, TimeoutSeconds, RetryCount, LogLevel)
- Verify all quality gates pass
- 100% Pydantic v2 compliant
"
```

### Step 8.4: Create PR

```bash
# Push to remote
git push origin pydantic-v2-migration

# Create PR on GitHub with description:
# - Reference this migration guide
# - Link to audit results
# - Note: All tests passing, all quality gates pass
```

---

## Troubleshooting Common Issues

### Issue 1: Import Error - "No module named pydantic.v1"

**Problem**:

```
ImportError: cannot import name 'validator' from 'pydantic'
```

**Solution**:

```python
# ❌ WRONG - v1 imports
from pydantic import validator

# ✅ CORRECT - v2 imports
from pydantic import field_validator
```

### Issue 2: Field Validation Not Working

**Problem**:

```python
@field_validator('email')
def validate_email(cls, v):  # Missing @classmethod
    return v.lower()
```

**Solution**:

```python
@field_validator('email')
@classmethod  # ✅ Add this
def validate_email(cls, v: str) -> str:  # ✅ Add type hints
    return v.lower()
```

### Issue 3: Model Configuration Not Applied

**Problem**:

```python
class MyModel(BaseModel):
    class Config:  # ❌ v1 pattern
        validate_assignment = True
```

**Solution**:

```python
class MyModel(BaseModel):
    model_config = ConfigDict(  # ✅ v2 pattern
        validate_assignment=True
    )
```

### Issue 4: Type Coercion Not Working

**Problem**:

```python
# String "true" not being converted to boolean
debug: bool = Field(...)
# Input: "true" → Expected: True, Got: ValueError
```

**Solution**:

```python
# Verify Pydantic v2 is installed
pip show pydantic  # Should be 2.x

# Verify model uses BaseModel (not custom base)
from pydantic import BaseModel  # ✅ Standard base

# Test coercion
from pydantic import BaseModel, Field

class Test(BaseModel):
    debug: bool = Field(default=False)

t = Test(debug="true")  # ✅ Works in v2
assert t.debug is True
```

### Issue 5: Serialization Method Missing

**Problem**:

```python
# AttributeError: 'MyModel' object has no attribute 'dict'
data = model.dict()  # ❌ v1 method
```

**Solution**:

```python
# Use v2 method
data = model.model_dump()  # ✅ v2 method
```

### Issue 6: Domain Type Validation Failing

**Problem**:

```python
# Value error when using domain type
from flext_core import PortNumber
port: PortNumber = Field(default=99999)  # ❌ Too high
```

**Solution**:

```python
# Use valid port range (1-65535)
from flext_core import PortNumber
port: PortNumber = Field(default=8080)  # ✅ Valid port

# Verify constraints
from flext_core import PortNumber
from pydantic import BaseModel, ValidationError

class Config(BaseModel):
    port: PortNumber

try:
    Config(port=99999)  # Should raise ValidationError
except ValidationError as e:
    print(f"✅ Constraint working: {e}")
```

---

## Migration Checklist

Complete this checklist for each project:

- [ ] **Phase 1: Assessment**
  - [ ] Identified all model files
  - [ ] Counted validators and BeforeValidators
  - [ ] Created feature branch
  - [ ] Baseline tests passing

- [ ] **Phase 2: Configuration**
  - [ ] Updated all `class Config` → `model_config = ConfigDict()`
  - [ ] Verified imports updated
  - [ ] Tested configuration

- [ ] **Phase 3: Validators**
  - [ ] Updated @validator → @field_validator
  - [ ] Updated @root_validator → @model_validator
  - [ ] Added @classmethod decorators
  - [ ] Added type annotations

- [ ] **Phase 4: BeforeValidator**
  - [ ] Removed \_coerce functions
  - [ ] Removed BeforeValidator annotations
  - [ ] Removed Annotated wrappers
  - [ ] Verified no duplication

- [ ] **Phase 5: Methods**
  - [ ] Updated .dict() → .model_dump()
  - [ ] Updated .JSON() → .model_dump_JSON()
  - [ ] Updated .parse_obj() → .model_validate()
  - [ ] Updated .parse_raw() → .model_validate_JSON()

- [ ] **Phase 6: Domain Types**
  - [ ] Imported domain types from flext_core
  - [ ] Applied PortNumber to network ports
  - [ ] Applied TimeoutSeconds to timeouts
  - [ ] Applied RetryCount to retry fields
  - [ ] Applied LogLevel to log level fields

- [ ] **Phase 7: Testing**
  - [ ] Unit tests passing: make test
  - [ ] Type checking passing: make type-check
  - [ ] Linting passing: make lint
  - [ ] Security passing: make security
  - [ ] Full validation passing: make validate
  - [ ] Pydantic audit passing: audit_pydantic_v2.py

- [ ] **Phase 8: Sign-off**
  - [ ] Updated CLAUDE.md with compliance note
  - [ ] Created commit with descriptive message
  - [ ] Pushed to remote
  - [ ] Created PR for review

---

## Success Criteria

A successful migration has:

✅ **All Tests Passing**: No test failures after migration
✅ **Type Safety**: Zero Pyrefly/MyPy errors
✅ **Zero Violations**: Ruff linting returns no issues
✅ **Security Passed**: Bandit finds no issues
✅ **100% Compliance**: Pydantic v2 audit shows PASS
✅ **Code Quality**: Same or improved code quality metrics
✅ **Performance**: Same or improved performance
✅ **Documentation**: CLAUDE.md updated with Pydantic v2 standards

---

## Timeline

| Phase              | Duration      | Effort     |
| ------------------ | ------------- | ---------- |
| 1. Assessment      | 15-30 min     | Low        |
| 2. Configuration   | 30-60 min     | Low        |
| 3. Validators      | 60-90 min     | Medium     |
| 4. BeforeValidator | 30-60 min     | Low        |
| 5. Methods         | 30-60 min     | Low        |
| 6. Domain Types    | 30-60 min     | Low        |
| 7. Testing         | 60-120 min    | High       |
| 8. Documentation   | 15-30 min     | Low        |
| **Total**          | **4-7 hours** | **Medium** |

---

## Questions & Support

- **Technical Questions**: See `/docs/PYDANTIC_V2_PATTERNS.md`
- **Code Examples**: See real implementations in `flext-ldif`, `flext-ldap`, `flext-cli`
- **Validation Issues**: Run audit script: `python scripts/audit_pydantic_v2.py`
- **Pre-commit Hook**: Prevents v1 patterns: `scripts/check_pydantic_v2_precommit.py`

---

**Version**: 1.0
**Status**: Production-Ready
**Completed**: All 29 FLEXT projects (2025-10-22)
