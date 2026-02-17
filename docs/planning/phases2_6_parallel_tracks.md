# Phases 2-6: Parallel Track Execution Plans

**Timeline**: Days 5-24 (after Phase 1 completes)  
**Strategy**: Parallel execution of Track A and Track B for each phase  
**Dependency**: Phase 1 must complete successfully

---

## Phase 2: API Layer + Infrastructure (Days 5-7)

**Duration**: 3 days  
**Parallel Tracks**: A (API) || B (Infrastructure)

### Track A: API Layer

**Projects**: flext-api, flext-grpc  
**Beads Issues**: To be created

#### Task 2A.1: flext-api cast() Elimination

**Duration**: 0.5 days

**Current State**:

- 1 cast() usage remaining
- Already has Plugin model (converted in Phase 0)

**Steps**:

1. Locate the 1 cast() usage
2. Replace with TypeGuard from flext-core
3. Verify type checking passes
4. Run tests

**Validation**:

- [ ] Zero cast() in flext-api
- [ ] `make validate PROJECT=flext-api` passes

**Commit**:

```
refactor(flext-api): eliminate cast() using TypeGuards
```

#### Task 2A.2: flext-grpc Lint Fixes

**Duration**: 1 day

**Current Issues**:

- RUF052 warnings (dummy variables)
- Rename `_network` → `network_config`, etc.

**Steps**:

1. Find all RUF052 violations
2. Rename dummy variables to meaningful names
3. Update any ConfigDict settings
4. Run linting

**Validation**:

- [ ] Zero RUF052 warnings
- [ ] `make validate PROJECT=flext-grpc` passes

**Commit**:

```
refactor(flext-grpc): fix RUF052 dummy variable warnings
```

---

### Track B: Infrastructure Layer

**Projects**: flext-observability, flext-quality, flext-plugin  
**Beads Issues**: To be created

#### Task 2B.1: flext-observability Migration

**Duration**: 1 day

**Steps**:

1. Fix lint failures
2. Migrate any TypedDicts to Pydantic
3. Standardize ConfigDict
4. Run validation

**Validation**:

- [ ] Zero lint violations
- [ ] `make validate PROJECT=flext-observability` passes

**Commit**:

```
refactor(flext-observability): migrate to Pydantic 2 patterns
```

#### Task 2B.2: flext-quality Migration

**Duration**: 0.5 days

**Steps**:

1. Review and migrate types
2. Ensure quality checks work with new patterns
3. Run validation

**Validation**:

- [ ] `make validate PROJECT=flext-quality` passes

**Commit**:

```
refactor(flext-quality): update for Pydantic 2 patterns
```

#### Task 2B.3: flext-plugin Completion

**Duration**: 0.5 days

**Current Issues**:

- ARG002 (unused paths argument)
- Missing docstrings (D106)

**Steps**:

1. Fix ARG002 violations
2. Add missing docstrings
3. Run validation

**Validation**:

- [ ] Zero ARG002 violations
- [ ] All docstrings present
- [ ] `make validate PROJECT=flext-plugin` passes

**Commit**:

```
refactor(flext-plugin): fix ARG002 and add missing docstrings
```

---

## Phase 3: Data Layer (Days 8-11)

**Duration**: 4 days  
**Parallel Tracks**: None (sequential, large migration)

**Projects**: flext-ldif, flext-ldap, flext-db-oracle

### Task 3.1: flext-ldif Migration (LARGE - 93 TypedDicts)

**Duration**: 2 days

**Current State**:

- 93 TypedDicts (largest in data layer)
- 5 cast() usages
- Critical for downstream projects

**Steps**:

1. **Analyze TypedDict Categories** (0.5 days)
   - Entry models
   - Attribute models
   - Result models
   - Configuration models

2. **Create Hierarchical Models** (1 day)

   ```python
   class FlextLdifModels:
       class Base(BaseModel):
           model_config = ConfigDict(...)

       class Entry(FlextLdifModels.Base):
           dn: str
           attributes: dict[str, list[str]]

       class Attribute(FlextLdifModels.Base):
           name: str
           values: list[str]

       class Result:
           class Success(FlextLdifModels.Base):
               entries: list[FlextLdifModels.Entry]

           class Failure(FlextLdifModels.Base):
               error: str
   ```

3. **Update Imports** (0.5 days)
   - Replace all TypedDict imports
   - Update function signatures
   - Update tests

4. **Eliminate cast()** (0.5 days)
   - Replace 5 cast() with TypeGuards
   - Verify type checking

**Validation**:

- [ ] All 93 TypedDicts converted
- [ ] Zero cast() usage
- [ ] `make validate PROJECT=flext-ldif` passes
- [ ] 80%+ coverage maintained

**Commits** (atomic per category):

```
feat(flext-ldif): add hierarchical Entry models
feat(flext-ldif): add hierarchical Attribute models
feat(flext-ldif): add hierarchical Result models
refactor(flext-ldif): eliminate cast() using TypeGuards
refactor(flext-ldif): update imports to use hierarchical models
```

### Task 3.2: flext-ldap Migration

**Duration**: 1 day

**Steps**:

1. Review existing models
2. Ensure LDAP operations use Pydantic validation
3. Standardize ConfigDict
4. Run validation

**Validation**:

- [ ] `make validate PROJECT=flext-ldap` passes

**Commit**:

```
refactor(flext-ldap): standardize Pydantic 2 patterns
```

### Task 3.3: flext-db-oracle Migration

**Duration**: 0.5 days

**Steps**:

1. Verify Oracle DB operations use proper types
2. Standardize any existing models
3. Run validation

**Validation**:

- [ ] `make validate PROJECT=flext-db-oracle` passes

**Commit**:

```
refactor(flext-db-oracle): standardize Pydantic 2 patterns
```

---

## Phase 4: Oracle Integration + Meltano (Days 12-14)

**Duration**: 3 days  
**Parallel Tracks**: A (Oracle) || B (Meltano)

### Track A: Oracle Integration

**Projects**: flext-oracle-wms, flext-oracle-oic

#### Task 4A.1: flext-oracle-wms Migration

**Duration**: 1.5 days

**Current State**:

- Missing imports
- TypedDicts to convert
- Needs standardization

**Steps**:

1. Fix missing imports
2. Migrate TypedDicts to models
3. Standardize ConfigDict
4. Run validation

**Validation**:

- [ ] `make validate PROJECT=flext-oracle-wms` passes

**Commit**:

```
refactor(flext-oracle-wms): migrate to Pydantic 2 patterns
```

#### Task 4A.2: flext-oracle-oic Migration

**Duration**: 1 day

**Current Issues**:

- PIE794 (duplicate OIC class field)
- Constants consolidation

**Steps**:

1. Fix PIE794 violations
2. Review and consolidate constants
3. Standardize ConfigDict
4. Run validation

**Validation**:

- [ ] Zero PIE794 violations
- [ ] `make validate PROJECT=flext-oracle-oic` passes

**Commit**:

```
refactor(flext-oracle-oic): fix PIE794 and consolidate constants
```

---

### Track B: Meltano/Singer Framework

**Projects**: flext-meltano

#### Task 4B.1: flext-meltano Migration

**Duration**: 1.5 days

**Current Issues**:

- bad-override error in `FlextMeltanoTapAbstractions.create_instance`
- Singer protocol implementations

**Steps**:

1. Fix bad-override error
2. Review Singer protocol implementations
3. Standardize ConfigDict in any models
4. Run validation

**Validation**:

- [ ] Zero bad-override errors
- [ ] Singer protocol compliance verified
- [ ] `make validate PROJECT=flext-meltano` passes

**Commit**:

```
refactor(flext-meltano): fix bad-override and standardize patterns
```

---

## Phase 5: Taps + Targets (Days 15-19)

**Duration**: 5 days  
**Parallel Tracks**: A (Taps) || B (Targets)

### Track A: Taps (Source Connectors)

**Projects**: flext-tap-ldap, flext-tap-ldif, flext-tap-oracle, flext-tap-oracle-oic

#### Task 5A.1: flext-tap-ldap Migration

**Duration**: 1.5 days

**Current State**:

- 8 cast() usages
- 1 TypedDict
- RUF022, F841 violations

**Steps**:

1. Remove 8 cast() usages
2. Convert 1 TypedDict
3. Fix RUF022 (**all** sorting)
4. Fix F841 (unused loop variable)
5. Standardize ConfigDict

**Validation**:

- [ ] Zero cast()
- [ ] Zero TypedDict
- [ ] Zero RUF022, F841
- [ ] `make validate PROJECT=flext-tap-ldap` passes

**Commits**:

```
refactor(flext-tap-ldap): eliminate cast() using TypeGuards
refactor(flext-tap-ldap): convert TypedDict to Pydantic model
refactor(flext-tap-ldap): fix RUF022 and F841 violations
```

#### Task 5A.2: flext-tap-ldif Migration

**Duration**: 0.5 days

**Steps**:

1. Review and verify types
2. Standardize ConfigDict
3. Run validation

**Validation**:

- [ ] `make validate PROJECT=flext-tap-ldif` passes

**Commit**:

```
refactor(flext-tap-ldif): standardize Pydantic 2 patterns
```

#### Task 5A.3: flext-tap-oracle Migration

**Duration**: 0.5 days

**Current State**:

- 1 cast() usage

**Steps**:

1. Remove 1 cast() usage
2. Standardize ConfigDict
3. Run validation

**Validation**:

- [ ] Zero cast()
- [ ] `make validate PROJECT=flext-tap-oracle` passes

**Commit**:

```
refactor(flext-tap-oracle): eliminate cast() using TypeGuards
```

#### Task 5A.4: flext-tap-oracle-oic Migration

**Duration**: 0.5 days

**Steps**:

1. Review and verify types
2. Standardize ConfigDict
3. Run validation

**Validation**:

- [ ] `make validate PROJECT=flext-tap-oracle-oic` passes

**Commit**:

```
refactor(flext-tap-oracle-oic): standardize Pydantic 2 patterns
```

---

### Track B: Targets (Destination Connectors)

**Projects**: flext-target-oracle, flext-target-ldap, flext-target-ldif, flext-target-oracle-oic, flext-target-oracle-wms

#### Task 5B.1: flext-target-oracle Migration (LARGE - 12 cast())

**Duration**: 2 days

**Current State**:

- 12 cast() usages (largest in targets)
- Major refactoring needed

**Steps**:

1. Analyze all 12 cast() usages
2. Replace with TypeGuards
3. Refactor affected functions
4. Standardize ConfigDict
5. Run validation

**Validation**:

- [ ] Zero cast()
- [ ] `make validate PROJECT=flext-target-oracle` passes

**Commits**:

```
refactor(flext-target-oracle): eliminate cast() using TypeGuards (part 1)
refactor(flext-target-oracle): eliminate cast() using TypeGuards (part 2)
refactor(flext-target-oracle): standardize ConfigDict
```

#### Task 5B.2: flext-target-ldap Migration

**Duration**: 0.5 days

**Current Issues**:

- Missing orchestrator import
- bad-dunder-all error

**Steps**:

1. Fix missing orchestrator import
2. Fix bad-dunder-all error
3. Standardize ConfigDict
4. Run validation

**Validation**:

- [ ] `make validate PROJECT=flext-target-ldap` passes

**Commit**:

```
refactor(flext-target-ldap): fix imports and bad-dunder-all error
```

#### Task 5B.3: flext-target-ldif Migration

**Duration**: 0.5 days

**Steps**:

1. Review and verify types
2. Standardize ConfigDict
3. Run validation

**Validation**:

- [ ] `make validate PROJECT=flext-target-ldif` passes

**Commit**:

```
refactor(flext-target-ldif): standardize Pydantic 2 patterns
```

#### Task 5B.4: flext-target-oracle-oic Migration

**Duration**: 1 day

**Current State**:

- 5 TypedDicts to convert

**Steps**:

1. Convert 5 TypedDicts to Pydantic models
2. Standardize ConfigDict
3. Run validation

**Validation**:

- [ ] Zero TypedDict
- [ ] `make validate PROJECT=flext-target-oracle-oic` passes

**Commit**:

```
refactor(flext-target-oracle-oic): convert TypedDicts to Pydantic models
```

#### Task 5B.5: flext-target-oracle-wms Migration

**Duration**: 0.5 days

**Steps**:

1. Review and align with tap-oracle-wms fixes
2. Standardize ConfigDict
3. Run validation

**Validation**:

- [ ] `make validate PROJECT=flext-target-oracle-wms` passes

**Commit**:

```
refactor(flext-target-oracle-wms): align with tap-oracle-wms patterns
```

---

## Phase 6: DBT Integration + User-Facing (Days 20-24)

**Duration**: 5 days  
**Parallel Tracks**: A (DBT) || B (User-Facing)

### Track A: DBT Integration

**Projects**: flext-dbt-oracle, flext-dbt-ldap, flext-dbt-ldif, flext-dbt-oracle-wms

#### Task 6A.1: flext-dbt-oracle Migration

**Duration**: 0.5 days

**Current State**:

- 3 cast() usages

**Steps**:

1. Remove 3 cast() usages
2. Standardize ConfigDict
3. Run validation

**Validation**:

- [ ] Zero cast()
- [ ] `make validate PROJECT=flext-dbt-oracle` passes

**Commit**:

```
refactor(flext-dbt-oracle): eliminate cast() using TypeGuards
```

#### Task 6A.2: flext-dbt-ldap Migration

**Duration**: 0.5 days

**Current State**:

- 1 cast() usage

**Steps**:

1. Remove 1 cast() usage
2. Standardize ConfigDict
3. Run validation

**Validation**:

- [ ] Zero cast()
- [ ] `make validate PROJECT=flext-dbt-ldap` passes

**Commit**:

```
refactor(flext-dbt-ldap): eliminate cast() using TypeGuards
```

#### Task 6A.3: flext-dbt-ldif Migration

**Duration**: 1 day

**Current State**:

- 1 cast() usage
- 2 TypedDicts

**Steps**:

1. Remove 1 cast() usage
2. Convert 2 TypedDicts
3. Standardize ConfigDict
4. Run validation

**Validation**:

- [ ] Zero cast()
- [ ] Zero TypedDict
- [ ] `make validate PROJECT=flext-dbt-ldif` passes

**Commits**:

```
refactor(flext-dbt-ldif): eliminate cast() using TypeGuards
refactor(flext-dbt-ldif): convert TypedDicts to Pydantic models
```

#### Task 6A.4: flext-dbt-oracle-wms Migration

**Duration**: 1.5 days

**Current State**:

- 1 cast() usage
- 22 TypedDicts (large)

**Steps**:

1. Remove 1 cast() usage
2. Convert 22 TypedDicts to hierarchical models
3. Create `FlextDbtOracleWmsModels` namespace
4. Standardize ConfigDict
5. Run validation

**Validation**:

- [ ] Zero cast()
- [ ] Zero TypedDict
- [ ] `make validate PROJECT=flext-dbt-oracle-wms` passes

**Commits**:

```
feat(flext-dbt-oracle-wms): add hierarchical models
refactor(flext-dbt-oracle-wms): eliminate cast() using TypeGuards
refactor(flext-dbt-oracle-wms): update imports to use hierarchical models
```

---

### Track B: User-Facing Applications

**Projects**: flext-cli, flext-web

#### Task 6B.1: flext-cli Migration (LARGE - 84 TypedDicts)

**Duration**: 2.5 days

**Current State**:

- 84 TypedDicts (second largest)
- Command handlers need updates

**Steps**:

1. **Analyze TypedDict Categories** (0.5 days)
   - Command models
   - Option models
   - Result models
   - Configuration models

2. **Create Hierarchical Models** (1.5 days)

   ```python
   class FlextCliModels:
       class Base(BaseModel):
           model_config = ConfigDict(...)

       class Command(FlextCliModels.Base):
           name: str
           description: str

       class Option(FlextCliModels.Base):
           name: str
           value: str | None

       class Result:
           class Success(FlextCliModels.Base):
               output: str

           class Failure(FlextCliModels.Base):
               error: str
   ```

3. **Update Command Handlers** (0.5 days)
   - Replace TypedDict usage
   - Update function signatures
   - Update tests

**Validation**:

- [ ] All 84 TypedDicts converted
- [ ] `make validate PROJECT=flext-cli` passes
- [ ] 80%+ coverage maintained

**Commits**:

```
feat(flext-cli): add hierarchical Command models
feat(flext-cli): add hierarchical Option models
refactor(flext-cli): update command handlers to use models
refactor(flext-cli): update imports to use hierarchical models
```

#### Task 6B.2: flext-web Migration (LARGE - 89 TypedDicts)

**Duration**: 2.5 days

**Current State**:

- 89 TypedDicts (largest)
- API endpoints need updates
- UI/UX functionality must be preserved

**Steps**:

1. **Analyze TypedDict Categories** (0.5 days)
   - Request models
   - Response models
   - Entity models
   - Configuration models

2. **Create Hierarchical Models** (1.5 days)

   ```python
   class FlextWebModels:
       class Base(BaseModel):
           model_config = ConfigDict(...)

       class Request(FlextWebModels.Base):
           endpoint: str
           method: str

       class Response(FlextWebModels.Base):
           status: int
           data: dict

       class Entity:
           class User(FlextWebModels.Base):
               id: str
               email: str
   ```

3. **Update API Endpoints** (0.5 days)
   - Replace TypedDict usage
   - Update function signatures
   - Update tests
   - Verify UI/UX functionality

**Validation**:

- [ ] All 89 TypedDicts converted
- [ ] `make validate PROJECT=flext-web` passes
- [ ] 80%+ coverage maintained
- [ ] UI/UX functionality preserved

**Commits**:

```
feat(flext-web): add hierarchical Request models
feat(flext-web): add hierarchical Response models
feat(flext-web): add hierarchical Entity models
refactor(flext-web): update API endpoints to use models
refactor(flext-web): update imports to use hierarchical models
```

---

## Parallel Execution Strategy

### Day-by-Day Breakdown

**Days 5-7 (Phase 2)**:

- **Track A** (API): 2A.1 + 2A.2 in parallel
- **Track B** (Infrastructure): 2B.1 + 2B.2 + 2B.3 in parallel

**Days 8-11 (Phase 3)**:

- Sequential: 3.1 (2 days) → 3.2 (1 day) → 3.3 (0.5 days)

**Days 12-14 (Phase 4)**:

- **Track A** (Oracle): 4A.1 + 4A.2 in parallel
- **Track B** (Meltano): 4B.1 in parallel

**Days 15-19 (Phase 5)**:

- **Track A** (Taps): 5A.1 + 5A.2 + 5A.3 + 5A.4 in parallel
- **Track B** (Targets): 5B.1 + 5B.2 + 5B.3 + 5B.4 + 5B.5 in parallel

**Days 20-24 (Phase 6)**:

- **Track A** (DBT): 6A.1 + 6A.2 + 6A.3 + 6A.4 in parallel
- **Track B** (User-Facing): 6B.1 + 6B.2 in parallel

### Coordination Points

1. **Daily Sync**: Compare progress between tracks
2. **Merge Conflicts**: Resolve if both tracks modify shared files
3. **Pattern Consistency**: Ensure both tracks follow Phase 1 patterns
4. **Test Coverage**: Verify 80%+ maintained in both tracks

---

## Success Criteria for Phases 2-6

✅ **All Projects Migrated**

- 20+ projects completed
- All following Phase 1 patterns

✅ **Type Safety**

- Zero cast() in all projects
- All replaced with TypeGuards

✅ **Model Organization**

- All TypedDicts converted to Pydantic models
- Hierarchical organization per project

✅ **Standardization**

- All models have standard ConfigDict
- Settings consistent across projects

✅ **Quality**

- `make validate` passes for all projects
- 80%+ coverage maintained
- Zero lint violations
- Zero type errors

✅ **Documentation**

- Patterns documented
- Ready for Phase 7 (test suite)
