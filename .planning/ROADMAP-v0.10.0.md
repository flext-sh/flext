# Roadmap - v0.10.0 Pydantic 2 Complete Migration

## Overview

**Milestone**: v0.10.0
**Timeline**: ~35 days (parallelized)
**Focus**: Complete Pydantic 2.11+ transformation across 29 projects

---

## Phase Structure

```
Phase 1 ─────────────────────────────────┐
  │ Foundation: flext-core patterns       │
  │ Duration: 4 days                      │
  └───────────────────────────────────────┘
            │
            ├──────────────────────────────┬────────────────────────────────┐
            ▼                              ▼                                ▼
Phase 2A ────────────────         Phase 2B ────────────────         Phase 3 ──────────────
  │ API Layer                       │ Infrastructure                  │ Data Layer
  │ flext-api, flext-grpc           │ flext-observability            │ flext-ldif (93 TD)
  │ Duration: 2 days                │ flext-quality, plugin          │ flext-ldap, db-oracle
  └──────────────────────           │ Duration: 2 days               │ Duration: 4 days
                                    └────────────────────            └──────────────────
            │                              │                                │
            └──────────────────────────────┴────────────────────────────────┘
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                      ▼
Phase 4A ────────────────                      Phase 4B ────────────────
  │ Oracle Integration                           │ Meltano/Singer
  │ flext-oracle-wms, oic                        │ flext-meltano
  │ Duration: 3 days                             │ Duration: 2 days
  └──────────────────────                        └──────────────────────
                        │                                      │
                        └──────────────────┬───────────────────┘
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                      ▼
Phase 5A ────────────────                      Phase 5B ────────────────
  │ Taps (Source Connectors)                     │ Targets (Destinations)
  │ tap-ldap, ldif, oracle, oic                  │ target-ldap, ldif, oracle
  │ Duration: 4 days                             │ Duration: 4 days
  └──────────────────────                        └──────────────────────
                        │                                      │
                        └──────────────────┬───────────────────┘
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                      ▼
Phase 6A ────────────────                      Phase 6B ────────────────
  │ DBT Integration                              │ User-Facing Apps
  │ dbt-ldap, ldif, oracle, wms                  │ flext-cli (84 TD)
  │ Duration: 3 days                             │ flext-web (89 TD)
  │                                              │ Duration: 4 days
  └──────────────────────                        └──────────────────────
                        │                                      │
                        └──────────────────┬───────────────────┘
                                           │
                                           ▼
Phase 7 ─────────────────────────────────────────────────────
  │ Test Suite Migration                                      │
  │ ~500 cast() in tests -> TypeGuards                       │
  │ Duration: 4 days                                         │
  └──────────────────────────────────────────────────────────┘
                                           │
                                           ▼
Phase 8 ─────────────────────────────────────────────────────
  │ Problem Project: flext-tap-oracle-wms                    │
  │ 100+ type errors, isolated risk                          │
  │ Duration: 4 days                                         │
  └──────────────────────────────────────────────────────────┘
                                           │
                                           ▼
Phase 9 ─────────────────────────────────────────────────────
  │ Final Validation + Documentation                         │
  │ Global validation, AGENTS.md update                      │
  │ Duration: 3 days                                         │
  └──────────────────────────────────────────────────────────┘
```

---

## Phase 1: Foundation - flext-core Patterns

**Goal**: Establish all patterns, complete flext-core migration
**Duration**: 4 days
**Dependencies**: None
**Beads Issue**: flext-dhj (parent), flext-fin/pf3/5dr/jt2/nya (tasks)

### Requirements Covered
- TYPE-04: TypeGuard infrastructure
- PYDANTIC-02: Hierarchical namespace organization
- PYDANTIC-03: Modern validator patterns

### Tasks

| ID | Task | Beads | Priority |
|----|------|-------|----------|
| 1.1 | Create TypeGuard infrastructure | flext-fin | P0 |
| 1.2 | Migrate 86 TypedDicts to hierarchical models | flext-pf3 | P0 |
| 1.3 | Eliminate 8 cast() in src/ | flext-5dr | P0 |
| 1.4 | Standardize ConfigDict settings | flext-jt2 | P0 |
| 1.5 | Validation + AGENTS.md update | flext-nya | P0 |

### Success Criteria
- [ ] `flext_core/utilities/guards.py` exists with comprehensive TypeGuards
- [ ] `flext_core/testing/guards.py` exists for test utilities
- [ ] Zero TypedDict in flext-core (all Pydantic models)
- [ ] Zero cast() in flext-core src/
- [ ] `make validate` passes in flext-core
- [ ] Pattern documentation complete

### Deliverables
```
flext-core/src/flext_core/
├── utilities/
│   └── guards.py          # Production TypeGuards
├── testing/
│   └── guards.py          # Test TypeGuards  
├── models.py              # Hierarchical Pydantic models
└── typings.py             # Type aliases only (no TypedDict)
```

---

## Phase 2A: API Layer

**Goal**: Migrate API projects
**Duration**: 2 days
**Dependencies**: Phase 1
**Beads Issue**: flext-x34

### Requirements Covered
- TYPE-01: cast() elimination
- PYDANTIC-01: ConfigDict standardization

### Tasks

| ID | Task | Project | Scope |
|----|------|---------|-------|
| 2A.1 | Remove 1 cast() | flext-api | TypeGuard pattern |
| 2A.2 | Fix lint warnings | flext-grpc | RUF052 (dummy vars) |
| 2A.3 | Standardize ConfigDict | both | All models |

### Success Criteria
- [ ] Zero cast() in flext-api and flext-grpc
- [ ] `make validate` passes in both projects

---

## Phase 2B: Infrastructure Layer

**Goal**: Migrate infrastructure projects
**Duration**: 2 days  
**Dependencies**: Phase 1
**Beads Issue**: flext-tli

### Requirements Covered
- TYPE-01: cast() elimination
- PYDANTIC-01: ConfigDict standardization

### Tasks

| ID | Task | Project | Scope |
|----|------|---------|-------|
| 2B.1 | Fix lint failures | flext-observability | Various |
| 2B.2 | Migrate types | flext-quality | TypedDict -> Pydantic |
| 2B.3 | Fix ARG002, D106 | flext-plugin | Unused args, docstrings |

### Success Criteria
- [ ] All infrastructure projects pass `make validate`

---

## Phase 3: Data Layer

**Goal**: Migrate data access projects (CRITICAL - 93 TypedDicts in ldif)
**Duration**: 4 days
**Dependencies**: Phase 1
**Beads Issues**: flext-t6x (parent), flext-ag7 (ldif), flext-l9g (ldap+oracle)

### Requirements Covered
- TYPE-01: cast() elimination
- TYPE-03: TypedDict conversion
- PYDANTIC-01: ConfigDict standardization
- PYDANTIC-02: Hierarchical organization

### Tasks

| ID | Task | Project | Scope |
|----|------|---------|-------|
| 3.1 | Convert 93 TypedDicts | flext-ldif | Create FlextLdifModels |
| 3.2 | Remove 5 cast() | flext-ldif | TypeGuard pattern |
| 3.3 | Review models | flext-ldap | Standardize ConfigDict |
| 3.4 | Verify types | flext-db-oracle | Standardize models |

### Success Criteria
- [ ] Zero TypedDict in flext-ldif
- [ ] Zero cast() in flext-ldif  
- [ ] FlextLdifModels namespace created
- [ ] All 3 projects pass `make validate`

---

## Phase 4A: Oracle Integration

**Goal**: Migrate Oracle integration projects
**Duration**: 3 days
**Dependencies**: Phase 3
**Beads Issue**: flext-w80

### Tasks

| ID | Task | Project | Scope |
|----|------|---------|-------|
| 4A.1 | Fix missing imports | flext-oracle-wms | Import structure |
| 4A.2 | Migrate TypedDicts | flext-oracle-wms | Pydantic models |
| 4A.3 | Fix PIE794 | flext-oracle-oic | Duplicate class field |

### Success Criteria
- [ ] Both Oracle projects pass `make validate`

---

## Phase 4B: Meltano/Singer

**Goal**: Migrate Meltano framework
**Duration**: 2 days
**Dependencies**: Phase 1
**Beads Issue**: flext-xi7

### Tasks

| ID | Task | Project | Scope |
|----|------|---------|-------|
| 4B.1 | Fix bad-override | flext-meltano | create_instance method |
| 4B.2 | Singer protocol review | flext-meltano | Compliance check |
| 4B.3 | Standardize ConfigDict | flext-meltano | All models |

### Success Criteria
- [ ] flext-meltano passes `make validate`
- [ ] Singer protocol compliant

---

## Phase 5A: Taps (Source Connectors)

**Goal**: Migrate all tap projects
**Duration**: 4 days
**Dependencies**: Phase 4
**Beads Issue**: flext-z5x

### Tasks

| ID | Task | Project | Scope |
|----|------|---------|-------|
| 5A.1 | Remove 8 cast(), 1 TypedDict | flext-tap-ldap | Fix RUF022, F841 |
| 5A.2 | Standardize | flext-tap-ldif | ConfigDict |
| 5A.3 | Remove 1 cast() | flext-tap-oracle | TypeGuard |
| 5A.4 | Standardize | flext-tap-oracle-oic | ConfigDict |

### Success Criteria
- [ ] All tap projects pass `make validate`
- [ ] Zero cast() in tap projects

---

## Phase 5B: Targets (Destination Connectors)

**Goal**: Migrate all target projects
**Duration**: 4 days
**Dependencies**: Phase 4
**Beads Issue**: flext-wzn

### Tasks

| ID | Task | Project | Scope |
|----|------|---------|-------|
| 5B.1 | Remove 12 cast() | flext-target-oracle | Major TypeGuard work |
| 5B.2 | Fix imports | flext-target-ldap | orchestrator import |
| 5B.3 | Standardize | flext-target-ldif | ConfigDict |
| 5B.4 | Convert 5 TypedDicts | flext-target-oracle-oic | Pydantic models |
| 5B.5 | Align with tap | flext-target-oracle-wms | Consistency |

### Success Criteria
- [ ] All target projects pass `make validate`
- [ ] Zero cast() in target projects

---

## Phase 6A: DBT Integration

**Goal**: Migrate DBT projects
**Duration**: 3 days
**Dependencies**: Phase 3, Phase 4
**Beads Issue**: flext-x64

### Tasks

| ID | Task | Project | Scope |
|----|------|---------|-------|
| 6A.1 | Remove 3 cast() | flext-dbt-oracle | TypeGuard |
| 6A.2 | Remove 1 cast() | flext-dbt-ldap | TypeGuard |
| 6A.3 | Remove 1 cast(), 2 TypedDict | flext-dbt-ldif | TypeGuard + models |
| 6A.4 | Remove 1 cast(), 22 TypedDict | flext-dbt-oracle-wms | Major migration |

### Success Criteria
- [ ] All DBT projects pass `make validate`

---

## Phase 6B: User-Facing Applications

**Goal**: Migrate CLI and Web applications (LARGE - 173 TypedDicts total)
**Duration**: 4 days
**Dependencies**: Phase 3, Phase 4
**Beads Issue**: flext-60w

### Tasks

| ID | Task | Project | Scope |
|----|------|---------|-------|
| 6B.1 | Convert 84 TypedDicts | flext-cli | Create FlextCliModels |
| 6B.2 | Update command handlers | flext-cli | Use new models |
| 6B.3 | Convert 89 TypedDicts | flext-web | Create FlextWebModels |
| 6B.4 | Update API endpoints | flext-web | Use new models |

### Success Criteria
- [ ] FlextCliModels namespace created
- [ ] FlextWebModels namespace created
- [ ] Both projects pass `make validate`
- [ ] UI/UX functionality preserved

---

## Phase 7: Test Suite Migration

**Goal**: Eliminate all cast() in tests (~500 usages)
**Duration**: 4 days
**Dependencies**: Phases 1-6
**Beads Issue**: TBD (create)

### Requirements Covered
- TYPE-02: Zero cast() in tests

### Tasks

| ID | Task | Scope |
|----|------|-------|
| 7.1 | Create test TypeGuard library | flext-core/testing/guards.py |
| 7.2 | Migrate flext-core tests | Highest count |
| 7.3 | Migrate flext-ldif tests | Second priority |
| 7.4 | Migrate tap/target tests | Parallel |
| 7.5 | Migrate cli/web tests | Parallel |

### Success Criteria
- [ ] Zero cast() in all test files
- [ ] 80%+ coverage maintained
- [ ] All tests passing

---

## Phase 8: Problem Project (flext-tap-oracle-wms)

**Goal**: Fix the most problematic project (100+ errors)
**Duration**: 4 days
**Dependencies**: All previous phases
**Beads Issue**: TBD (create)

### Tasks

| ID | Task | Scope |
|----|------|-------|
| 8.1 | Fix import structure | config, exceptions modules |
| 8.2 | Fix type errors | 100+ systematically |
| 8.3 | Fix bad-override | Method signatures |
| 8.4 | Apply patterns | TypeGuard, ConfigDict |

### Success Criteria
- [ ] flext-tap-oracle-wms passes `make validate`
- [ ] Zero type errors
- [ ] Consistent with monorepo patterns

---

## Phase 9: Final Validation + Documentation

**Goal**: Complete validation and documentation
**Duration**: 3 days
**Dependencies**: All previous phases
**Beads Issue**: flext-3bc

### Requirements Covered
- VAL-01: All projects pass validate
- VAL-02: 80%+ coverage
- VAL-03: No regressions
- DOCS-01: AGENTS.md update
- DOCS-02: Migration guide

### Tasks

| ID | Task | Scope |
|----|------|-------|
| 9.1 | Global validation | `make validate` on all 29 projects |
| 9.2 | Coverage verification | 80%+ on all projects |
| 9.3 | Update AGENTS.md | Final patterns |
| 9.4 | Create migration guide | Reference document |
| 9.5 | Close all Beads issues | Cleanup |
| 9.6 | Tag v0.10.0 | Release |

### Success Criteria
- [ ] All 29 projects pass `make validate`
- [ ] 80%+ coverage on all projects
- [ ] Zero cast() in entire codebase
- [ ] Zero TypedDict in entire codebase
- [ ] AGENTS.md updated
- [ ] v0.10.0 tagged

---

## Timeline Summary

| Week | Phases | Focus |
|------|--------|-------|
| Week 1 | 1 | Foundation (flext-core) |
| Week 2 | 2A+2B+3 | API + Infrastructure + Data (parallel) |
| Week 3 | 4A+4B+5A+5B | Oracle + Meltano + Connectors (parallel) |
| Week 4 | 6A+6B | DBT + User-Facing (parallel) |
| Week 5 | 7+8 | Test Suite + Problem Project |
| Week 6 | 9 | Validation + Documentation |

**Total**: ~35 days (5-6 weeks)
**Parallelization Savings**: ~10-12 days vs sequential

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Large TypedDict counts | Phase 1 establishes patterns first |
| flext-tap-oracle-wms 100+ errors | Isolated in Phase 8 |
| Test regressions | Continuous testing after each phase |
| Cross-project dependencies | Dependency order maintained |

---

*Created: 2026-02-04*
*Milestone: v0.10.0 - Pydantic 2 Complete Migration*
