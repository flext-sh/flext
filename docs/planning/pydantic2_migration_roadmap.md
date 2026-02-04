# Pydantic 2 Migration Roadmap

## Executive Summary

**Objective**: Complete transformation of the Flext monorepo (29 projects) from legacy typing patterns to Pydantic 2 BaseModels, eliminating all `cast()` usage and converting all `TypedDict` definitions.

**Current State**:
- **41 `cast()` usages** remaining across 10 projects
- **402 `TypedDict` definitions** remaining across 10 projects
- Multiple projects with lint/type errors requiring correction

**Target State**:
- Zero `cast()` usage
- Zero `TypedDict` for data models (only for external API contracts)
- All projects passing `make check` (lint + types)
- 80%+ test coverage maintained

---

## Migration Metrics

### Cast() Usage by Project
| Project | Count | Priority |
|---------|-------|----------|
| flext-target-oracle | 12 | High |
| flext-core | 8 | Critical |
| flext-tap-ldap | 8 | High |
| flext-ldif | 5 | Medium |
| flext-dbt-oracle | 3 | Medium |
| flext-api | 1 | Critical |
| flext-dbt-ldap | 1 | Low |
| flext-dbt-ldif | 1 | Low |
| flext-dbt-oracle-wms | 1 | Low |
| flext-tap-oracle | 1 | Medium |
| **Total** | **41** | |

### TypedDict Usage by Project
| Project | Count | Priority |
|---------|-------|----------|
| flext-ldif | 93 | High |
| flext-web | 89 | Medium |
| flext-core | 86 | Critical |
| flext-cli | 84 | Medium |
| flext-dbt-oracle-wms | 22 | Medium |
| flext-auth | 19 | Critical (partial done) |
| flext-target-oracle-oic | 5 | Low |
| flext-dbt-ldif | 2 | Low |
| flext-plugin | 1 | Low (done) |
| flext-tap-ldap | 1 | Low |
| **Total** | **402** | |

---

## Phase Structure

### Phase 0: Foundation (COMPLETED)
**Status**: ✅ Done

| Task | Project | Status |
|------|---------|--------|
| Remove cast() in utilities | flext-core | ✅ |
| Remove cast() in models | flext-core | ✅ |
| Convert Plugin to BaseModel | flext-api | ✅ |
| Migrate TypedDicts to Pydantic | flext-auth | ✅ |
| Remove cast() in handlers | flext-plugin | ✅ |

---

### Phase 1: Core Completion
**Goal**: Complete flext-core migration, foundation for all other projects
**Duration**: 2-3 days
**Dependencies**: None

#### Tasks

**1.1 flext-core TypedDict Migration**
- Convert 86 TypedDicts in `typings.py` to Pydantic models in `models.py`
- Organize into nested classes: `FlextModels.Core.*`, `FlextModels.Config.*`
- Update all internal imports

**1.2 flext-core cast() Elimination**
- Remove remaining 8 cast() usages
- Replace with isinstance checks or proper type narrowing
- Update affected functions with TypeGuard where needed

**1.3 flext-core Validation**
- Run `make check` - zero errors
- Run `make test` - 80%+ coverage
- Update AGENTS.md if patterns changed

#### Deliverables
- [ ] `flext-core/src/flext_core/typings.py` - Type aliases only
- [ ] `flext-core/src/flext_core/models.py` - All Pydantic models
- [ ] Zero cast() usage
- [ ] `make validate` passing

---

### Phase 2: API Layer
**Goal**: Complete flext-api and flext-grpc migration
**Duration**: 1-2 days
**Dependencies**: Phase 1

#### Tasks

**2.1 flext-api cast() Elimination**
- Remove remaining 1 cast() usage
- Verify Plugin model integration

**2.2 flext-grpc Lint Fixes**
- Fix RUF052 warnings (dummy variables)
- Rename `_network` → `network_config`, etc.

**2.3 flext-api/grpc Validation**
- Run `make check` for both projects
- Integration tests passing

#### Deliverables
- [ ] Zero cast() in flext-api
- [ ] Zero lint warnings in flext-grpc
- [ ] Both projects passing `make validate`

---

### Phase 3: Infrastructure Layer
**Goal**: Migrate supporting infrastructure projects
**Duration**: 2-3 days
**Dependencies**: Phase 1

#### Tasks

**3.1 flext-observability**
- Fix lint failures
- Migrate any TypedDicts to Pydantic

**3.2 flext-quality**
- Review and migrate types
- Ensure quality checks work with new patterns

**3.3 flext-plugin Completion**
- Fix ARG002 (unused paths argument)
- Add missing docstrings (D106)

#### Deliverables
- [ ] All three projects passing `make validate`
- [ ] No lint errors or warnings

---

### Phase 4: Data Layer
**Goal**: Migrate data access and serialization projects
**Duration**: 3-4 days
**Dependencies**: Phase 1

#### Tasks

**4.1 flext-ldif Migration (LARGE)**
- Convert 93 TypedDicts to Pydantic models
- Remove 5 cast() usages
- Organize into `FlextLdifModels.*` namespace

**4.2 flext-ldap Migration**
- Review existing models
- Ensure LDAP operations use Pydantic validation

**4.3 flext-db-oracle Migration**
- Verify Oracle DB operations use proper types
- No TypedDicts or casts detected

#### Deliverables
- [ ] flext-ldif: Zero TypedDict, zero cast()
- [ ] All data layer projects passing `make validate`

---

### Phase 5: Oracle Integration Layer
**Goal**: Migrate Oracle-specific integration projects
**Duration**: 2-3 days
**Dependencies**: Phase 4

#### Tasks

**5.1 flext-oracle-wms**
- Fix missing imports
- Migrate TypedDicts to models
- Has untracked content requiring review

**5.2 flext-oracle-oic**
- Fix PIE794 (duplicate OIC class field)
- Review and consolidate constants

#### Deliverables
- [ ] Both Oracle projects passing `make validate`
- [ ] Clean lint and type checks

---

### Phase 6: Meltano/Singer Framework
**Goal**: Migrate the Singer framework integration
**Duration**: 2-3 days
**Dependencies**: Phase 1

#### Tasks

**6.1 flext-meltano**
- Fix bad-override error in `FlextMeltanoTapAbstractions.create_instance`
- Review Singer protocol implementations

#### Deliverables
- [ ] flext-meltano passing `make validate`
- [ ] Singer protocol compliance verified

---

### Phase 7: Taps (Source Connectors)
**Goal**: Migrate all tap (source) connectors
**Duration**: 4-5 days
**Dependencies**: Phase 5, Phase 6

#### Tasks

**7.1 flext-tap-ldap**
- Remove 8 cast() usages
- Convert 1 TypedDict
- Fix RUF022 (__all__ sorting)
- Fix F841 (unused loop variable)

**7.2 flext-tap-ldif**
- Review and verify types

**7.3 flext-tap-oracle**
- Remove 1 cast() usage

**7.4 flext-tap-oracle-oic**
- Review and verify types

**7.5 flext-tap-oracle-wms (LARGE)**
- Fix 100+ type errors
- Missing imports: config, exceptions modules
- Fix bad-override errors
- Fix missing attributes on FlextModels/FlextTypes
- This is the most problematic project

#### Deliverables
- [ ] All tap projects passing `make validate`
- [ ] Zero cast() usage across all taps

---

### Phase 8: Targets (Destination Connectors)
**Goal**: Migrate all target (destination) connectors
**Duration**: 4-5 days
**Dependencies**: Phase 5, Phase 6

#### Tasks

**8.1 flext-target-oracle (LARGE)**
- Remove 12 cast() usages
- Major refactoring needed

**8.2 flext-target-ldap**
- Fix missing orchestrator import
- Fix bad-dunder-all error

**8.3 flext-target-ldif**
- Review and verify types

**8.4 flext-target-oracle-oic**
- Convert 5 TypedDicts to Pydantic models

**8.5 flext-target-oracle-wms**
- Review and align with tap-oracle-wms fixes

#### Deliverables
- [ ] All target projects passing `make validate`
- [ ] Zero cast() usage across all targets

---

### Phase 9: DBT Integration
**Goal**: Migrate DBT transformation projects
**Duration**: 2-3 days
**Dependencies**: Phase 4, Phase 5

#### Tasks

**9.1 flext-dbt-oracle**
- Remove 3 cast() usages

**9.2 flext-dbt-ldap**
- Remove 1 cast() usage

**9.3 flext-dbt-ldif**
- Remove 1 cast() usage
- Convert 2 TypedDicts

**9.4 flext-dbt-oracle-wms**
- Remove 1 cast() usage
- Convert 22 TypedDicts to Pydantic models

#### Deliverables
- [ ] All DBT projects passing `make validate`
- [ ] Zero cast() usage across all DBT projects

---

### Phase 10: User-Facing Applications
**Goal**: Migrate CLI and Web applications
**Duration**: 3-4 days
**Dependencies**: All previous phases

#### Tasks

**10.1 flext-cli (LARGE)**
- Convert 84 TypedDicts to Pydantic models
- Organize into `FlextCliModels.*` namespace
- Update command handlers

**10.2 flext-web (LARGE)**
- Convert 89 TypedDicts to Pydantic models
- Organize into `FlextWebModels.*` namespace
- Update API endpoints and handlers

#### Deliverables
- [ ] Both user-facing projects passing `make validate`
- [ ] UI/UX functionality preserved

---

### Phase 11: Final Validation & Documentation
**Goal**: Ensure complete migration and update documentation
**Duration**: 2-3 days
**Dependencies**: All previous phases

#### Tasks

**11.1 Global Validation**
- Run `make validate` on entire monorepo
- Verify zero cast() across all projects
- Verify minimal TypedDict usage (only for external contracts)

**11.2 Test Coverage**
- Ensure 80%+ coverage on all projects
- Fix any broken tests from migration

**11.3 Documentation Update**
- Update AGENTS.md with final patterns
- Update type-system-architecture.md
- Create migration guide for future reference

**11.4 Cleanup**
- Remove deprecated type aliases
- Archive migration plan
- Close all related Beads issues

#### Deliverables
- [ ] `make validate` passing on full monorepo
- [ ] All Beads issues closed
- [ ] Documentation updated

---

## Risk Assessment

### High Risk Projects
1. **flext-tap-oracle-wms**: 100+ type errors, missing modules
2. **flext-ldif**: 93 TypedDicts to convert
3. **flext-web**: 89 TypedDicts, UI implications
4. **flext-core**: 86 TypedDicts, foundation for all projects

### Mitigation Strategies
- Start with flext-core to establish patterns
- Use incremental commits per file/module
- Run tests after each significant change
- Create rollback points before large migrations

---

## Timeline Estimate

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: Core | 3 days | 3 days |
| Phase 2: API | 2 days | 5 days |
| Phase 3: Infrastructure | 3 days | 8 days |
| Phase 4: Data | 4 days | 12 days |
| Phase 5: Oracle | 3 days | 15 days |
| Phase 6: Meltano | 3 days | 18 days |
| Phase 7: Taps | 5 days | 23 days |
| Phase 8: Targets | 5 days | 28 days |
| Phase 9: DBT | 3 days | 31 days |
| Phase 10: User-Facing | 4 days | 35 days |
| Phase 11: Validation | 3 days | 38 days |

**Total Estimated Duration**: ~6-8 weeks (with buffer for issues)

---

## Success Criteria

1. **Zero `cast()` usage** in any production code
2. **Zero `TypedDict` for data models** (only allowed for external API contracts)
3. **All 29 projects** passing `make validate`
4. **80%+ test coverage** maintained or improved
5. **No regression** in functionality
6. **Documentation** updated and complete

---

## Execution Protocol

For each project migration:

1. **Analyze**: Grep for cast() and TypedDict, read affected files
2. **Plan**: Create task breakdown in Beads
3. **Execute**: Convert TypedDicts → Pydantic, remove casts
4. **Verify**: Run `make check` on project
5. **Test**: Run `make test` on project
6. **Commit**: Atomic commits per logical change
7. **Push**: Sync to remote after verification

---

## Related Beads Issues

- `flext-53o`: Remove all cast() usage (IN PROGRESS)
- Additional issues to be created per phase
