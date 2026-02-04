# Roadmap - v0.10.0 Pydantic 2 Complete Migration

**Version**: 0.10.0  
**Created**: 2026-02-04  
**Timeline**: 35 days (parallelized)

---

## Phase 1: Foundation (Days 1-4) - CURRENT

**Goal**: Establish patterns and infrastructure for all subsequent phases

**Directory**: `.planning/phases/01-foundation/`

**Requirements Mapped**: TYPE-01, TYPE-04, PYDANTIC-01, PYDANTIC-04

### Plans

| Plan | Description | Status | Days |
|------|-------------|--------|------|
| 01-01 | TypeGuard Infrastructure | Validated | 1 |
| 01-02 | TypedDict Migration | Executing | 1.5 |
| 01-03 | cast() Elimination | Discovered | 1 |
| 01-04 | ConfigDict Standardization | Executing | 0.5 |
| 01-05 | Validation & Documentation | Planned | 0.5 |

### Success Criteria

- [ ] TypeGuard utilities created and tested
- [ ] All 86 TypedDicts in flext-core converted to Pydantic models
- [ ] Zero cast() in flext-core src/
- [ ] Standard ConfigDict across all models
- [ ] AGENTS.md updated with final patterns
- [ ] `make validate PROJECT=flext-core` passes

---

## Phase 2: API Layer + Infrastructure (Days 5-7)

**Goal**: Migrate API and infrastructure projects in parallel

**Directory**: `.planning/phases/02-api-infra/`

**Requirements Mapped**: TYPE-01, TYPE-03, PYDANTIC-01, PYDANTIC-03

### Parallel Tracks

**Track A** (API Layer):
- flext-api (0.5 days)
- flext-grpc (1 day)

**Track B** (Infrastructure):
- flext-observability (1 day)
- flext-quality (0.5 days)
- flext-plugin (0.5 days)

### Success Criteria

- [ ] Zero cast() in all 5 projects
- [ ] Zero TypedDict in all 5 projects
- [ ] Standard ConfigDict applied
- [ ] All projects passing `make validate`

---

## Phase 3: Data Layer (Days 8-11)

**Goal**: Migrate data access and serialization projects

**Directory**: `.planning/phases/03-data-layer/`

**Requirements Mapped**: TYPE-01, TYPE-03, PYDANTIC-01, PYDANTIC-02

### Projects

- **flext-ldif** (93 TypedDicts - HIGH RISK)
- **flext-ldap**
- **flext-db-oracle**

### Success Criteria

- [ ] All 93 TypedDicts in flext-ldif converted
- [ ] Zero cast() in all 3 projects
- [ ] Hierarchical model pattern established
- [ ] All projects passing `make validate`

---

## Phase 4: Oracle + Meltano (Days 12-14)

**Goal**: Migrate Oracle and Meltano projects in parallel

**Directory**: `.planning/phases/04-oracle-meltano/`

**Requirements Mapped**: TYPE-01, TYPE-03, PYDANTIC-01

### Parallel Tracks

**Track A** (Oracle):
- flext-oracle-wms (1.5 days)
- flext-oracle-oic (1 day)

**Track B** (Meltano):
- flext-meltano (1.5 days)

### Success Criteria

- [ ] Zero cast() in all 3 projects
- [ ] Zero TypedDict in all 3 projects
- [ ] All projects passing `make validate`

---

## Phase 5: Taps + Targets (Days 15-19)

**Goal**: Migrate source and destination connectors in parallel

**Directory**: `.planning/phases/05-taps-targets/`

**Requirements Mapped**: TYPE-01, TYPE-03, PYDANTIC-01

### Parallel Tracks

**Track A** (Taps):
- flext-tap-ldap (1.5 days)
- flext-tap-ldif (0.5 days)
- flext-tap-oracle (0.5 days)
- flext-tap-oracle-oic (0.5 days)

**Track B** (Targets):
- flext-target-oracle (2 days)
- flext-target-ldap (0.5 days)
- flext-target-ldif (0.5 days)
- flext-target-oracle-oic (1 day)
- flext-target-oracle-wms (0.5 days)

### Success Criteria

- [ ] Zero cast() in all 9 projects
- [ ] Zero TypedDict in all 9 projects
- [ ] All projects passing `make validate`

---

## Phase 6: DBT + User-Facing (Days 20-24)

**Goal**: Migrate DBT and user-facing applications in parallel

**Directory**: `.planning/phases/06-dbt-user-facing/`

**Requirements Mapped**: TYPE-01, TYPE-03, PYDANTIC-01

### Parallel Tracks

**Track A** (DBT):
- flext-dbt-oracle (0.5 days)
- flext-dbt-ldap (0.5 days)
- flext-dbt-ldif (1 day)
- flext-dbt-oracle-wms (1.5 days)

**Track B** (User-Facing):
- flext-cli (84 TypedDicts - 2.5 days)
- flext-web (89 TypedDicts - 2.5 days)

### Success Criteria

- [ ] All TypedDicts in flext-cli converted
- [ ] All TypedDicts in flext-web converted
- [ ] Zero cast() in all 6 projects
- [ ] All projects passing `make validate`

---

## Phase 7: Test Suite (Days 25-28)

**Goal**: Eliminate all ~500 cast() in test files

**Directory**: `.planning/phases/07-test-suite/`

**Requirements Mapped**: TYPE-02, VAL-02

### Tasks

- 07-01: Create test TypeGuard library
- 07-02: Migrate tests by project
- 07-03: Verify coverage maintained

### Success Criteria

- [ ] Zero cast() in all test files
- [ ] 80%+ coverage maintained
- [ ] All tests passing

---

## Phase 8: Problem Project (Days 29-32)

**Goal**: Fix flext-tap-oracle-wms (100+ type errors)

**Directory**: `.planning/phases/08-problem-project/`

**Requirements Mapped**: VAL-01

### Tasks

- 08-01: Import structure fixes
- 08-02: Type error resolution
- 08-03: Model migration

### Success Criteria

- [ ] flext-tap-oracle-wms passing validation
- [ ] Zero type errors
- [ ] Patterns consistent with other projects

---

## Phase 9: Final Validation (Days 33-35)

**Goal**: Ensure complete migration and update documentation

**Directory**: `.planning/phases/09-final-validation/`

**Requirements Mapped**: VAL-01, VAL-02, VAL-03, DOCS-01, DOCS-02

### Tasks

- 09-01: Global validation (`make validate` on all 29 projects)
- 09-02: Test coverage verification (80%+ across all)
- 09-03: Documentation update (AGENTS.md, migration guide)
- 09-04: Cleanup and issue closure

### Success Criteria

- [ ] `make validate` passes on full monorepo
- [ ] All 29 projects passing
- [ ] 80%+ coverage maintained
- [ ] Documentation complete
- [ ] All Beads issues closed

---

## Summary

| Phase | Name | Duration | Days | Status |
|-------|------|----------|------|--------|
| 1 | Foundation | 4 days | 1-4 | EXECUTING |
| 2 | API + Infrastructure | 3 days | 5-7 | PLANNED |
| 3 | Data Layer | 4 days | 8-11 | PLANNED |
| 4 | Oracle + Meltano | 3 days | 12-14 | PLANNED |
| 5 | Taps + Targets | 5 days | 15-19 | PLANNED |
| 6 | DBT + User-Facing | 5 days | 20-24 | PLANNED |
| 7 | Test Suite | 4 days | 25-28 | PLANNED |
| 8 | Problem Project | 4 days | 29-32 | PLANNED |
| 9 | Final Validation | 3 days | 33-35 | PLANNED |
| **Total** | | **35 days** | | |

**Savings**: ~10-12 days from parallelization vs sequential execution

---

*Last updated: 2026-02-04*
*Milestone: v0.10.0 - Pydantic 2 Complete Migration*
