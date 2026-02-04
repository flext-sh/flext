# Phase 71: Pydantic 2 Migration - Execution Coordination

**Phase**: 71-pydantic2-migration  
**Status**: READY FOR EXECUTION  
**Created**: 2026-02-04  
**Timeline**: 35 days (parallelized)

## Phase Structure

### Phase 1: Foundation (Days 1-4)

**Goal**: Establish patterns and infrastructure for all subsequent phases

**Tasks**:
- 01-01: TypeGuard Infrastructure (1 day)
- 01-02: TypedDict Migration (1.5 days)
- 01-03: cast() Elimination (1 day)
- 01-04: ConfigDict Standardization (0.5 days)
- 01-05: Validation & Documentation (0.5 days)

**Beads Issues**:
- flext-fin: Task 01-01
- flext-pf3: Task 01-02
- flext-5dr: Task 01-03
- flext-jt2: Task 01-04
- flext-nya: Task 01-05

**Success Criteria**:
- ✅ TypeGuard utilities created
- ✅ All 86 TypedDicts converted
- ✅ Zero cast() in src/
- ✅ Standard ConfigDict
- ✅ AGENTS.md updated
- ✅ `make validate PROJECT=flext-core` passes

### Phase 2: API Layer + Infrastructure (Days 5-7)

**Goal**: Migrate API and infrastructure projects in parallel

**Parallel Tracks**:
- Track A: flext-api, flext-grpc
- Track B: flext-observability, flext-quality, flext-plugin

**Beads Issues** (to be created):
- 02-01-A: flext-api cast() elimination
- 02-02-A: flext-grpc lint fixes
- 02-01-B: flext-observability migration
- 02-02-B: flext-quality migration
- 02-03-B: flext-plugin completion

### Phase 3: Data Layer (Days 8-11)

**Goal**: Migrate data access and serialization projects

**Projects**:
- flext-ldif (93 TypedDicts - LARGE)
- flext-ldap
- flext-db-oracle

**Beads Issues** (to be created):
- 03-01: flext-ldif migration
- 03-02: flext-ldap migration
- 03-03: flext-db-oracle migration

### Phase 4: Oracle Integration + Meltano (Days 12-14)

**Goal**: Migrate Oracle and Meltano projects in parallel

**Parallel Tracks**:
- Track A: flext-oracle-wms, flext-oracle-oic
- Track B: flext-meltano

**Beads Issues** (to be created):
- 04-01-A: flext-oracle-wms migration
- 04-02-A: flext-oracle-oic migration
- 04-01-B: flext-meltano migration

### Phase 5: Taps + Targets (Days 15-19)

**Goal**: Migrate source and destination connectors in parallel

**Parallel Tracks**:
- Track A: 4 tap projects
- Track B: 5 target projects

**Beads Issues** (to be created):
- 05-01-A: flext-tap-ldap migration
- 05-02-A: flext-tap-ldif migration
- 05-03-A: flext-tap-oracle migration
- 05-04-A: flext-tap-oracle-oic migration
- 05-01-B: flext-target-oracle migration
- 05-02-B: flext-target-ldap migration
- 05-03-B: flext-target-ldif migration
- 05-04-B: flext-target-oracle-oic migration
- 05-05-B: flext-target-oracle-wms migration

### Phase 6: DBT Integration + User-Facing (Days 20-24)

**Goal**: Migrate DBT and user-facing applications in parallel

**Parallel Tracks**:
- Track A: 4 DBT projects
- Track B: flext-cli, flext-web

**Beads Issues** (to be created):
- 06-01-A: flext-dbt-oracle migration
- 06-02-A: flext-dbt-ldap migration
- 06-03-A: flext-dbt-ldif migration
- 06-04-A: flext-dbt-oracle-wms migration
- 06-01-B: flext-cli migration
- 06-02-B: flext-web migration

### Phase 7: Test Suite Migration (Days 25-28)

**Goal**: Eliminate all ~500 cast() in test files

**Tasks**:
- 07-01: Create test TypeGuard library
- 07-02: Migrate tests by project
- 07-03: Verify coverage

**Beads Issues** (to be created):
- 07-01: Test TypeGuard library
- 07-02: Test suite migration
- 07-03: Coverage verification

### Phase 8: Problem Project (Days 29-32)

**Goal**: Fix flext-tap-oracle-wms (100+ type errors)

**Tasks**:
- 08-01: Import structure fixes
- 08-02: Type error resolution
- 08-03: Model migration

**Beads Issues** (to be created):
- 08-01: Import fixes
- 08-02: Type error resolution
- 08-03: Model migration

### Phase 9: Final Validation (Days 33-35)

**Goal**: Ensure complete migration and update documentation

**Tasks**:
- 09-01: Global validation
- 09-02: Test coverage verification
- 09-03: Documentation update
- 09-04: Cleanup and issue closure

**Beads Issues** (to be created):
- 09-01: Global validation
- 09-02: Coverage verification
- 09-03: Documentation update
- 09-04: Cleanup

## Execution Protocol

### Daily Workflow

1. **Morning**: Check Beads for ready tasks
   ```bash
   bd ready
   ```

2. **Start Task**: Update status to in_progress
   ```bash
   bd update <id> --status in_progress
   ```

3. **Execute**: Follow task plan
   - Read PLAN.md
   - Execute steps
   - Validate
   - Commit

4. **Complete**: Close issue
   ```bash
   bd close <id>
   ```

5. **Sync**: Push to remote
   ```bash
   bd sync
   git push
   ```

### Quality Gates

Before committing:

```bash
# Type checking
pyrefly src/

# Linting
ruff check src/

# Tests
pytest tests/ -v

# Coverage
pytest tests/ --cov=<project> --cov-report=term-missing
```

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

Closes: <beads-id>
```

**Types**: feat, fix, refactor, test, docs, chore  
**Scope**: Project name (flext-core, flext-ldif, etc.)  
**Subject**: Brief description  
**Body**: Detailed explanation  
**Closes**: Beads issue ID

### Rollback Strategy

If critical issues arise:

1. **Identify Issue**: Document in Beads
2. **Create Tag**: `git tag phase-{N}-rollback`
3. **Rollback**: `git reset --hard phase-{N}-start`
4. **Analyze**: Determine root cause
5. **Retry**: Address issue and restart task

## Parallel Execution Coordination

### Phase 2 (Days 5-7)

**Track A** (API Layer):
- 02-01-A: flext-api (0.5 days)
- 02-02-A: flext-grpc (1 day)

**Track B** (Infrastructure):
- 02-01-B: flext-observability (1 day)
- 02-02-B: flext-quality (0.5 days)
- 02-03-B: flext-plugin (0.5 days)

**Coordination**:
- Both tracks start on Day 5
- Daily sync on progress
- Merge conflicts resolved immediately
- Pattern consistency checked

### Phase 4 (Days 12-14)

**Track A** (Oracle):
- 04-01-A: flext-oracle-wms (1.5 days)
- 04-02-A: flext-oracle-oic (1 day)

**Track B** (Meltano):
- 04-01-B: flext-meltano (1.5 days)

**Coordination**:
- Both tracks start on Day 12
- Daily sync on progress
- Pattern consistency checked

### Phase 5 (Days 15-19)

**Track A** (Taps):
- 05-01-A: flext-tap-ldap (1.5 days)
- 05-02-A: flext-tap-ldif (0.5 days)
- 05-03-A: flext-tap-oracle (0.5 days)
- 05-04-A: flext-tap-oracle-oic (0.5 days)

**Track B** (Targets):
- 05-01-B: flext-target-oracle (2 days)
- 05-02-B: flext-target-ldap (0.5 days)
- 05-03-B: flext-target-ldif (0.5 days)
- 05-04-B: flext-target-oracle-oic (1 day)
- 05-05-B: flext-target-oracle-wms (0.5 days)

**Coordination**:
- Both tracks start on Day 15
- Daily sync on progress
- Pattern consistency checked

### Phase 6 (Days 20-24)

**Track A** (DBT):
- 06-01-A: flext-dbt-oracle (0.5 days)
- 06-02-A: flext-dbt-ldap (0.5 days)
- 06-03-A: flext-dbt-ldif (1 day)
- 06-04-A: flext-dbt-oracle-wms (1.5 days)

**Track B** (User-Facing):
- 06-01-B: flext-cli (2.5 days)
- 06-02-B: flext-web (2.5 days)

**Coordination**:
- Both tracks start on Day 20
- Daily sync on progress
- Pattern consistency checked

## Success Metrics

### Phase 1 (Foundation)
- ✅ TypeGuard utilities created
- ✅ All 86 TypedDicts converted
- ✅ Zero cast() in src/
- ✅ Standard ConfigDict
- ✅ AGENTS.md updated

### Phases 2-6 (Main Migration)
- ✅ 20+ projects migrated
- ✅ All following Phase 1 patterns
- ✅ Zero cast() in all projects
- ✅ Zero TypedDict in all projects
- ✅ Standard ConfigDict across all projects

### Phase 7 (Test Suite)
- ✅ Zero cast() in all tests
- ✅ 80%+ coverage maintained
- ✅ All tests passing

### Phase 8 (Problem Project)
- ✅ flext-tap-oracle-wms passing validation
- ✅ Zero type errors
- ✅ Patterns consistent

### Phase 9 (Validation)
- ✅ `make validate` passes on full monorepo
- ✅ All 29 projects passing
- ✅ 80%+ coverage maintained
- ✅ Documentation complete

## Risk Mitigation

### High Risk Projects

1. **flext-tap-oracle-wms** (100+ errors)
   - Isolated in Phase 8
   - Doesn't block other work

2. **flext-ldif** (93 TypedDicts)
   - Dedicated time in Phase 3
   - Patterns established in Phase 1

3. **flext-web** (89 TypedDicts)
   - Parallel with flext-cli
   - UI/UX testing required

### Mitigation Strategies

- Phase 1 establishes all patterns
- Incremental commits per file/module
- Continuous testing after changes
- Git tags for rollback points
- Problem project isolated

## Next Steps

1. ✅ Create GSD phase plans (DONE)
2. ⏳ Create Beads issues for all phases
3. ⏳ Start Phase 1 execution
4. ⏳ Execute Tasks 01-01 through 01-05
5. ⏳ Parallelize Phases 2-6
6. ⏳ Complete Phase 7 (test suite)
7. ⏳ Fix Phase 8 (problem project)
8. ⏳ Final validation (Phase 9)

## Timeline Summary

| Phase | Duration | Days | Status |
|-------|----------|------|--------|
| Phase 1: Foundation | 4 days | 1-4 | READY |
| Phase 2: API + Infra | 3 days | 5-7 | PLANNED |
| Phase 3: Data | 4 days | 8-11 | PLANNED |
| Phase 4: Oracle + Meltano | 3 days | 12-14 | PLANNED |
| Phase 5: Taps + Targets | 5 days | 15-19 | PLANNED |
| Phase 6: DBT + User-Facing | 5 days | 20-24 | PLANNED |
| Phase 7: Test Suite | 4 days | 25-28 | PLANNED |
| Phase 8: Problem Project | 4 days | 29-32 | PLANNED |
| Phase 9: Validation | 3 days | 33-35 | PLANNED |
| **Total** | **35 days** | | |

**Savings**: ~10-12 days from parallelization
