# Pydantic 2 Migration Roadmap

<!-- TOC START -->

- [Executive Summary](#executive-summary)
- [Key Decisions](#key-decisions)
- [Migration Patterns](#migration-patterns)
  - [TypeGuard Pattern (Replaces cast())](#typeguard-pattern-replaces-cast)
  - [TypedDict to Pydantic Model (Hierarchical Inheritance)](#typeddict-to-pydantic-model-hierarchical-inheritance)
  - [Standard ConfigDict Settings](#standard-configdict-settings)
  - [Modern Validator Patterns (Pydantic 2.11+)](#modern-validator-patterns-pydantic-211)
  - [Namespace Hierarchy Standard](#namespace-hierarchy-standard)
- [Migration Metrics](#migration-metrics)
  - [Cast() Usage by Location (627 total)](#cast-usage-by-location-627-total)
  - [TypedDict Usage by Project (305 total)](#typeddict-usage-by-project-305-total)
  - [ConfigDict Standardization Scope](#configdict-standardization-scope)
- [Phase Structure (Parallelized)](#phase-structure-parallelized)
  - [Phase 0: Foundation (COMPLETED)](#phase-0-foundation-completed)
  - [Phase 1: Core Completion + Pattern Establishment](#phase-1-core-completion-pattern-establishment)
  - [Phase 2: API Layer + Infrastructure (PARALLEL)](#phase-2-api-layer-infrastructure-parallel)
  - [Phase 3: Data Layer](#phase-3-data-layer)
  - [Phase 4: Oracle Integration + Meltano (PARALLEL)](#phase-4-oracle-integration-meltano-parallel)
  - [Phase 5: Taps + Targets (PARALLEL)](#phase-5-taps-targets-parallel)
  - [Phase 6: DBT Integration + User-Facing (PARALLEL)](#phase-6-dbt-integration-user-facing-parallel)
  - [Phase 7: Test Suite Migration](#phase-7-test-suite-migration)
  - [Phase 8: Problem Project (flext-tap-oracle-wms)](#phase-8-problem-project-flext-tap-oracle-wms)
  - [Phase 9: Final Validation & Documentation](#phase-9-final-validation-documentation)
- [Timeline Estimate (Parallelized)](#timeline-estimate-parallelized)
- [Risk Assessment](#risk-assessment)
  - [High Risk Projects](#high-risk-projects)
  - [Mitigation Strategies](#mitigation-strategies)
- [Success Criteria](#success-criteria)
- [Execution Protocol](#execution-protocol)
- [Related Beads Issues](#related-beads-issues)
- [Appendix: Reference Files](#appendix-reference-files)
<!-- TOC END -->

## Executive Summary

**Objective**: Complete transformation of the Flext monorepo (29 projects) to modern Pydantic 2.11+ patterns with hierarchical BaseModel inheritance, eliminating all `cast()` usage, converting all `TypedDict` definitions to structural Pydantic models, standardizing `ConfigDict` settings, and modernizing validators.

**Current State** (from exhaustive codebase analysis):

- **627 `cast()` usages** across the codebase (~500 in tests, ~127 in src/)
- **305 `TypedDict` definitions** across 74 files
- **249+ `model_config = ConfigDict()`** patterns - **codebase ALREADY uses Pydantic v2**
- **127 BaseModel subclasses** across the monorepo
- **ZERO `@validator` or `@root_validator`** (Pydantic v1) - already migrated to v2
- Multiple projects with lint/type errors requiring correction

**Target State**:

- Zero `cast()` usage in ALL code (src/ AND tests/)
- Zero `TypedDict` - ALL converted to structural Pydantic 2 models with hierarchical inheritance
- Standardized `ConfigDict` settings across all 127+ models
- Modern validator patterns (`@field_validator`, `@model_validator`, `computed_field`)
- All projects passing `make validate`
- 80%+ test coverage maintained

---

## Key Decisions

| Decision                       | Choice                                      | Rationale                                            |
| ------------------------------ | ------------------------------------------- | ---------------------------------------------------- |
| **cast() in tests**            | Convert ALL to TypeGuards                   | Consistent type safety, no exceptions                |
| **TypedDict treatment**        | Convert ALL to structural Pydantic 2 models | Hierarchical inheritance enables reuse               |
| **Namespace pattern**          | Hybrid with max reuse                       | `m.Entity`, `m.Ldif.Entry`, `m.Cli.Command`          |
| **ConfigDict standardization** | YES                                         | Consistent validation, serialization across projects |
| **Validator modernization**    | YES                                         | Leverage Pydantic 2.11 features                      |
| **Phase parallelization**      | YES                                         | Reduce timeline from 38 to ~25-28 days               |
| **flext-tap-oracle-wms**       | Final phase                                 | 100+ errors, isolate risk                            |

---

## Migration Patterns

### TypeGuard Pattern (Replaces cast())

```python
# BEFORE: Using cast() - FORBIDDEN
from typing import cast
config = cast(ConfigDict, data)

# AFTER: Using TypeGuard
from flext_core.utilities import u

if u.Guards.is_config(data):
    config = data  # Type narrowed automatically
    config.app_name  # Safe access

# For tests, create test-specific TypeGuards in conftest.py
def is_user_response(obj: object) -> TypeGuard[UserResponse]:
    return isinstance(obj, dict) and "user_id" in obj and "email" in obj
```

### TypedDict to Pydantic Model (Hierarchical Inheritance)

```python
# BEFORE: TypedDict - FORBIDDEN
class DispatcherConfig(TypedDict):
    timeout: int
    retries: int
    batch_size: int

class BatchResultDict(TypedDict):
    success_count: int
    failure_count: int

# AFTER: Structural Pydantic models with inheritance
class FlextModels:
    """Hierarchical model namespace with max reuse."""

    class Base(BaseModel):
        """Base for all Flext models."""
        model_config = ConfigDict(
            validate_assignment=True,
            use_enum_values=True,
            extra="forbid",
            str_strip_whitespace=True,
        )

    class Config:
        """Configuration models namespace."""

        class Dispatcher(FlextModels.Base):
            timeout: int = Field(ge=0, description="Timeout in seconds")
            retries: int = Field(ge=0, le=10, description="Max retry attempts")
            batch_size: int = Field(ge=1, le=10000, description="Batch size")

    class Result:
        """Result models namespace."""

        class Batch(FlextModels.Base):
            success_count: int = Field(ge=0)
            failure_count: int = Field(ge=0)

            @computed_field
            @property
            def total(self) -> int:
                return self.success_count + self.failure_count
```

### Standard ConfigDict Settings

```python
# Standard production model
model_config = ConfigDict(
    validate_assignment=True,      # Validate on attribute assignment
    use_enum_values=True,          # Serialize enums to values
    extra="forbid",                # Reject unknown fields
    str_strip_whitespace=True,     # Clean string inputs
    frozen=False,                  # Mutable by default
)

# Immutable value object
model_config = ConfigDict(
    frozen=True,                   # Immutable
    validate_assignment=True,
    extra="forbid",
)

# API response model (allows extra for forward compatibility)
model_config = ConfigDict(
    extra="ignore",                # Ignore unknown fields from API
    validate_assignment=True,
)
```

### Modern Validator Patterns (Pydantic 2.11+)

```python
from pydantic import BaseModel, field_validator, model_validator, computed_field

class User(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if len(self.password) < 8:
            raise ValueError("Password too short")
        return self

    @computed_field
    @property
    def domain(self) -> str:
        return self.email.split("@")[1]
```

### Namespace Hierarchy Standard

```python
# Project-level namespace pattern
# flext-core/src/flext_core/models.py
class FlextModels:
    class Core:
        class Config(BaseModel): ...
        class Context(BaseModel): ...
    class Result:
        class Success(BaseModel): ...
        class Failure(BaseModel): ...

# flext-ldif/src/flext_ldif/models.py
class FlextLdifModels:
    class Entry(BaseModel): ...      # m.Ldif.Entry
    class Attribute(BaseModel): ...  # m.Ldif.Attribute

# Usage with short aliases
from flext_ldif.models import m as ldif_m

config: m.Core.Config = ...
entry: ldif_m.Entry = ...
```

---

## Migration Metrics

### Cast() Usage by Location (627 total)

| Location            | Count   | Strategy                   |
| ------------------- | ------- | -------------------------- |
| **tests/**          | ~500    | TypeGuards in conftest.py  |
| **src/ production** | ~127    | TypeGuards in utilities.py |
| **Total**           | **627** |                            |

### TypedDict Usage by Project (305 total)

| Project                 | Count   | Priority             |
| ----------------------- | ------- | -------------------- |
| flext-ldif              | 93      | High                 |
| flext-web               | 89      | Medium               |
| flext-core              | 86      | Critical             |
| flext-cli               | 84      | Medium               |
| flext-dbt-oracle-wms    | 22      | Medium               |
| flext-auth              | 19      | Low (partially done) |
| flext-target-oracle-oic | 5       | Low                  |
| flext-dbt-ldif          | 2       | Low                  |
| flext-tap-ldap          | 1       | Low                  |
| Other projects          | 4       | Low                  |
| **Total**               | **305** |                      |

### ConfigDict Standardization Scope

| Pattern                          | Current Count | Action               |
| -------------------------------- | ------------- | -------------------- |
| `model_config = ConfigDict(...)` | 249+          | Standardize settings |
| Missing `extra="forbid"`         | TBD           | Add to all models    |
| Missing `validate_assignment`    | TBD           | Add to all models    |

---

## Phase Structure (Parallelized)

### Phase 0: Foundation (COMPLETED)

**Status**: Done

| Task                           | Project      | Status |
| ------------------------------ | ------------ | ------ |
| Remove cast() in utilities     | flext-core   | Done   |
| Remove cast() in models        | flext-core   | Done   |
| Convert Plugin to BaseModel    | flext-api    | Done   |
| Migrate TypedDicts to Pydantic | flext-auth   | Done   |
| Remove cast() in handlers      | flext-plugin | Done   |

---

### Phase 1: Core Completion + Pattern Establishment

**Goal**: Complete flext-core migration, establish patterns for all other projects
**Duration**: 3-4 days
**Dependencies**: None
**Parallel Tracks**: None (foundation phase)

#### Tasks

**1.1 TypeGuard Infrastructure**

- Create `flext_core/utilities/guards.py` with comprehensive TypeGuards
- Add test utilities in `flext_core/testing/guards.py`
- Document pattern in AGENTS.md

**1.2 flext-core TypedDict Migration**

- Convert 86 TypedDicts to hierarchical Pydantic models
- Organize into `FlextModels.Core.*`, `FlextModels.Config.*`, `FlextModels.Result.*`
- Ensure all models inherit from common base with standard ConfigDict

**1.3 flext-core cast() Elimination**

- Remove all 8 cast() usages in src/
- Replace with TypeGuards from 1.1
- Update affected functions

**1.4 ConfigDict Standardization Template**

- Create base model classes with standard ConfigDict
- Document which settings apply to which model types
- Create migration checklist for other projects

**1.5 Validation**

- Run `make validate` - zero errors
- 80%+ coverage maintained
- Update AGENTS.md with final patterns

#### Deliverables

- [ ] `flext_core/utilities/guards.py` - TypeGuard implementations
- [ ] `flext_core/testing/guards.py` - Test TypeGuards
- [ ] `flext_core/models.py` - All Pydantic models with hierarchy
- [ ] `flext_core/typings.py` - Type aliases only (no TypedDict)
- [ ] Zero cast() usage
- [ ] Standard ConfigDict documented
- [ ] `make validate` passing

---

### Phase 2: API Layer + Infrastructure (PARALLEL)

**Goal**: Migrate API and infrastructure projects in parallel
**Duration**: 2-3 days
**Dependencies**: Phase 1

#### Track A: API Layer

**2A.1 flext-api cast() Elimination**

- Remove remaining 1 cast() usage
- Apply TypeGuard pattern

**2A.2 flext-grpc Lint Fixes**

- Fix RUF052 warnings (dummy variables)
- Standardize ConfigDict in any models

#### Track B: Infrastructure Layer

**2B.1 flext-observability**

- Fix lint failures
- Migrate any TypedDicts to Pydantic
- Standardize ConfigDict

**2B.2 flext-quality**

- Review and migrate types
- Ensure quality checks work with new patterns

**2B.3 flext-plugin Completion**

- Fix ARG002 (unused paths argument)
- Add missing docstrings (D106)

#### Deliverables

- [ ] Track A + Track B all passing `make validate`
- [ ] Zero cast(), zero TypedDict in these projects

---

### Phase 3: Data Layer

**Goal**: Migrate data access and serialization projects
**Duration**: 3-4 days
**Dependencies**: Phase 1

#### Tasks

**3.1 flext-ldif Migration (LARGE - 93 TypedDicts)**

- Convert all TypedDicts to hierarchical models
- Create `FlextLdifModels` namespace
- Remove 5 cast() usages
- Standardize all ConfigDict settings

**3.2 flext-ldap Migration**

- Review existing models
- Ensure LDAP operations use Pydantic validation
- Standardize ConfigDict

**3.3 flext-db-oracle Migration**

- Verify Oracle DB operations use proper types
- Standardize any existing models

#### Deliverables

- [ ] flext-ldif: Zero TypedDict, zero cast(), standard ConfigDict
- [ ] All data layer projects passing `make validate`

---

### Phase 4: Oracle Integration + Meltano (PARALLEL)

**Goal**: Migrate Oracle and Meltano projects in parallel
**Duration**: 3 days
**Dependencies**: Phase 3 (for Oracle), Phase 1 (for Meltano)

#### Track A: Oracle Integration

**4A.1 flext-oracle-wms**

- Fix missing imports
- Migrate TypedDicts to models
- Standardize ConfigDict

**4A.2 flext-oracle-oic**

- Fix PIE794 (duplicate OIC class field)
- Review and consolidate constants
- Standardize ConfigDict

#### Track B: Meltano/Singer Framework

**4B.1 flext-meltano**

- Fix bad-override error in `FlextMeltanoTapAbstractions.create_instance`
- Review Singer protocol implementations
- Standardize ConfigDict in any models

#### Deliverables

- [ ] Both tracks passing `make validate`
- [ ] Singer protocol compliance verified

---

### Phase 5: Taps + Targets (PARALLEL)

**Goal**: Migrate source and destination connectors in parallel
**Duration**: 4-5 days
**Dependencies**: Phase 4

#### Track A: Taps (Source Connectors)

**5A.1 flext-tap-ldap**

- Remove 8 cast() usages
- Convert 1 TypedDict
- Fix RUF022, F841

**5A.2 flext-tap-ldif**

- Review and verify types
- Standardize ConfigDict

**5A.3 flext-tap-oracle**

- Remove 1 cast() usage
- Standardize ConfigDict

**5A.4 flext-tap-oracle-oic**

- Review and verify types
- Standardize ConfigDict

#### Track B: Targets (Destination Connectors)

**5B.1 flext-target-oracle (LARGE - 12 cast())**

- Remove 12 cast() usages
- Major TypeGuard refactoring
- Standardize ConfigDict

**5B.2 flext-target-ldap**

- Fix missing orchestrator import
- Fix bad-dunder-all error

**5B.3 flext-target-ldif**

- Review and verify types
- Standardize ConfigDict

**5B.4 flext-target-oracle-oic**

- Convert 5 TypedDicts to Pydantic models
- Standardize ConfigDict

**5B.5 flext-target-oracle-wms**

- Review and align with tap-oracle-wms fixes

#### Deliverables

- [ ] All tap and target projects passing `make validate`
- [ ] Zero cast() across all connectors

---

### Phase 6: DBT Integration + User-Facing (PARALLEL)

**Goal**: Migrate DBT and user-facing applications in parallel
**Duration**: 4-5 days
**Dependencies**: Phase 3, Phase 4

#### Track A: DBT Integration

**6A.1 flext-dbt-oracle**

- Remove 3 cast() usages
- Standardize ConfigDict

**6A.2 flext-dbt-ldap**

- Remove 1 cast() usage
- Standardize ConfigDict

**6A.3 flext-dbt-ldif**

- Remove 1 cast() usage
- Convert 2 TypedDicts
- Standardize ConfigDict

**6A.4 flext-dbt-oracle-wms**

- Remove 1 cast() usage
- Convert 22 TypedDicts to Pydantic models
- Standardize ConfigDict

#### Track B: User-Facing Applications

**6B.1 flext-cli (LARGE - 84 TypedDicts)**

- Convert all TypedDicts to hierarchical models
- Create `FlextCliModels` namespace
- Update command handlers
- Standardize ConfigDict

**6B.2 flext-web (LARGE - 89 TypedDicts)**

- Convert all TypedDicts to hierarchical models
- Create `FlextWebModels` namespace
- Update API endpoints and handlers
- Standardize ConfigDict

#### Deliverables

- [ ] All DBT projects passing `make validate`
- [ ] Both user-facing projects passing `make validate`
- [ ] UI/UX functionality preserved

---

### Phase 7: Test Suite Migration

**Goal**: Eliminate all cast() in tests (~500 usages)
**Duration**: 3-4 days
**Dependencies**: Phases 1-6 (TypeGuard infrastructure must exist)

#### Tasks

**7.1 Create Test TypeGuard Library**

- Add comprehensive TypeGuards in each project's `conftest.py`
- Create shared test utilities in `flext-core/testing/`

**7.2 Migrate Tests by Project**

- flext-core tests (highest count)
- flext-ldif tests
- flext-tap-\* tests
- flext-target-\* tests
- flext-dbt-\* tests
- flext-cli tests
- flext-web tests

**7.3 Verify Test Coverage**

- Ensure 80%+ coverage maintained
- No test regressions

#### Deliverables

- [ ] Zero cast() in all test files
- [ ] 80%+ coverage maintained across all projects

---

### Phase 8: Problem Project (flext-tap-oracle-wms)

**Goal**: Fix the most problematic project separately
**Duration**: 3-4 days
**Dependencies**: All previous phases

#### Tasks

**8.1 Import Structure Fixes**

- Fix missing config module imports
- Fix missing exceptions module imports
- Resolve circular dependencies

**8.2 Type Error Resolution**

- Fix 100+ type errors systematically
- Fix bad-override errors
- Fix missing attributes on FlextModels/FlextTypes

**8.3 Model Migration**

- Apply all patterns established in earlier phases
- Convert any remaining TypedDicts
- Remove any remaining cast()
- Standardize ConfigDict

#### Deliverables

- [ ] flext-tap-oracle-wms passing `make validate`
- [ ] Zero type errors
- [ ] Patterns consistent with rest of monorepo

---

### Phase 9: Final Validation & Documentation

**Goal**: Ensure complete migration and update documentation
**Duration**: 2-3 days
**Dependencies**: All previous phases

#### Tasks

**9.1 Global Validation**

- Run `make validate` on entire monorepo
- Verify zero cast() across ALL projects (src/ AND tests/)
- Verify zero TypedDict (all converted to Pydantic models)
- Verify ConfigDict standardized across all 127+ models

**9.2 Test Coverage**

- Ensure 80%+ coverage on all projects
- Fix any broken tests from migration

**9.3 Documentation Update**

- Update AGENTS.md with final patterns
- Update type-system-architecture.md
- Create migration guide for future reference
- Document TypeGuard patterns
- Document hierarchical model inheritance patterns
- Document ConfigDict standards

**9.4 Cleanup**

- Remove deprecated type aliases
- Archive migration plan
- Close all related Beads issues

#### Deliverables

- [ ] `make validate` passing on full monorepo
- [ ] All Beads issues closed
- [ ] Documentation complete
- [ ] Zero technical debt from migration

---

## Timeline Estimate (Parallelized)

| Phase                      | Duration | Parallel With | Cumulative |
| -------------------------- | -------- | ------------- | ---------- |
| Phase 1: Core              | 4 days   | -             | 4 days     |
| Phase 2: API + Infra       | 3 days   | (A \|\| B)    | 7 days     |
| Phase 3: Data              | 4 days   | -             | 11 days    |
| Phase 4: Oracle + Meltano  | 3 days   | (A \|\| B)    | 14 days    |
| Phase 5: Taps + Targets    | 5 days   | (A \|\| B)    | 19 days    |
| Phase 6: DBT + User-Facing | 5 days   | (A \|\| B)    | 24 days    |
| Phase 7: Test Suite        | 4 days   | -             | 28 days    |
| Phase 8: Problem Project   | 4 days   | -             | 32 days    |
| Phase 9: Validation        | 3 days   | -             | 35 days    |

**Total Estimated Duration**: ~5-6 weeks (reduced from 6-8 weeks via parallelization)

**Savings from Parallelization**: ~10-12 days

---

## Risk Assessment

### High Risk Projects

| Project                  | Risk                      | Mitigation                       |
| ------------------------ | ------------------------- | -------------------------------- |
| **flext-tap-oracle-wms** | 100+ type errors          | Isolated in Phase 8              |
| **flext-ldif**           | 93 TypedDicts             | Dedicated time in Phase 3        |
| **flext-web**            | 89 TypedDicts, UI impact  | Parallel track, thorough testing |
| **flext-cli**            | 84 TypedDicts             | Parallel track with web          |
| **flext-core**           | 86 TypedDicts, foundation | Phase 1 priority, sets patterns  |

### Mitigation Strategies

1. **Pattern First**: Phase 1 establishes all patterns before parallel work
2. **Incremental Commits**: Atomic commits per file/module
3. **Continuous Testing**: Run tests after each significant change
4. **Rollback Points**: Create git tags before large migrations
5. **Problem Isolation**: flext-tap-oracle-wms separated to Phase 8

---

## Success Criteria

1. **Zero `cast()` usage** in ALL code (src/ AND tests/)
2. **Zero `TypedDict`** - all converted to structural Pydantic 2 models
3. **Hierarchical inheritance** - models organized in namespaced hierarchies
4. **Standard ConfigDict** - consistent settings across all 127+ models
5. **Modern validators** - `@field_validator`, `@model_validator`, `computed_field`
6. **All 29 projects** passing `make validate`
7. **80%+ test coverage** maintained or improved
8. **No regression** in functionality
9. **Documentation** complete with patterns and examples

---

## Execution Protocol

For each project migration:

1. **Analyze**: Grep for cast(), TypedDict, ConfigDict patterns
2. **Plan**: Create task breakdown in Beads
3. **Infrastructure**: Add TypeGuards to project's utilities
4. **Convert**: TypedDicts -> hierarchical Pydantic models
5. **Eliminate**: cast() -> TypeGuards
6. **Standardize**: ConfigDict settings per model type
7. **Verify**: Run `make check` on project
8. **Test**: Run `make test` on project
9. **Commit**: Atomic commits per logical change
10. **Push**: Sync to remote after verification

---

## Related Beads Issues

- `flext-53o`: Remove all cast() usage (IN PROGRESS)
- Additional issues to be created per phase

---

## Appendix: Reference Files

Key files demonstrating target patterns:

| File                                          | Content                        |
| --------------------------------------------- | ------------------------------ |
| `flext-core/src/flext_core/typings.py`        | Type system (888 lines)        |
| `flext-core/src/flext_core/models.py`         | Model patterns (313 lines)     |
| `flext-core/src/flext_core/result.py`         | Railway patterns with Pydantic |
| `flext-tap-ldif/src/flext_tap_ldif/models.py` | Pydantic 2.11 patterns         |
