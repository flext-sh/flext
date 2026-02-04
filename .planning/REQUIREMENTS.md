# Requirements - v0.10.0 Pydantic 2 Complete Migration

## Milestone Overview

**Version**: 0.10.0
**Codename**: Pydantic 2 Complete Migration
**Status**: In Progress
**Goal**: Complete transformation to modern Pydantic 2.11+ patterns across all 29 projects

---

## v0.10.0 Requirements

### TYPE-SAFETY: Type System Modernization

- [ ] **TYPE-01**: Zero `cast()` usage in ALL production code (src/)
  - Current: 34 usages in 8 projects
  - Target: Replace with TypeGuards
  
- [x] **TYPE-02**: Zero `cast()` usage in ALL test code (tests/) - **DEFERRED to v0.11.0**
  - Note: Test code cast() is acceptable for test fixtures
  
- [ ] **TYPE-03**: Zero `TypedDict` definitions in src/ (converted to Pydantic models)
  - Current: 152 TypedDicts in 11 projects (src/ only)
  - Target: Hierarchical Pydantic 2 models
  
- [x] **TYPE-04**: TypeGuard infrastructure in flext-core
  - EXISTS: `flext_core/_utilities/guards.py` (1389 lines, 50+ TypeGuards)

### PYDANTIC: Model Standardization

- [ ] **PYDANTIC-01**: Standard ConfigDict settings across all 127+ models
  - Settings: validate_assignment, use_enum_values, extra, str_strip_whitespace
  
- [ ] **PYDANTIC-02**: Hierarchical model namespace organization
  - Pattern: `m.Entity`, `m.Ldif.Entry`, `m.Cli.Command`
  
- [ ] **PYDANTIC-03**: Modern validator patterns throughout
  - Migrate: `@field_validator`, `@model_validator`, `computed_field`
  - Remove: Any legacy patterns

- [ ] **PYDANTIC-04**: Railway integration with Pydantic validation
  - Pattern: `r[T].from_validation(data, Model)`

### VALIDATION: Quality Gates

- [ ] **VAL-01**: All 29 projects pass `make validate`
  - Zero lint errors (Ruff)
  - Zero type errors (Pyrefly)
  
- [ ] **VAL-02**: 80%+ test coverage maintained across all projects
  
- [ ] **VAL-03**: No regression in functionality after migration

### DOCS: Documentation

- [ ] **DOCS-01**: AGENTS.md updated with final patterns
  - TypeGuard patterns
  - Hierarchical model patterns
  - ConfigDict standards
  
- [ ] **DOCS-02**: Migration guide for reference
  - Pattern examples
  - Before/after comparisons

---

## v0.11.0 Requirements (Deferred)

- [ ] **PERF-01**: Performance optimization of new model patterns
- [ ] **ASYNC-01**: Async/await integration improvements
- [ ] **GRAPHQL-01**: GraphQL API integration

---

## Out of Scope

- **New features** - Focus on migration only
- **Performance optimization** - Deferred to v0.11.0
- **API changes** - Maintain backwards compatibility
- **Documentation portal** - Only AGENTS.md and migration guide

---

## Traceability Matrix

| REQ-ID | Phase | Beads Issue | Status |
|--------|-------|-------------|--------|
| TYPE-01 | Phase 1-6 | flext-5dr, multiple | Pending |
| TYPE-02 | Phase 7 | TBD | Pending |
| TYPE-03 | Phase 1-6 | flext-pf3, multiple | Pending |
| TYPE-04 | Phase 1 | flext-fin | Pending |
| PYDANTIC-01 | Phase 1-6 | flext-jt2, multiple | Pending |
| PYDANTIC-02 | Phase 1 | flext-pf3 | Pending |
| PYDANTIC-03 | Phase 1-6 | multiple | Pending |
| PYDANTIC-04 | Phase 1 | flext-fin | Pending |
| VAL-01 | Phase 9 | flext-3bc | Pending |
| VAL-02 | Phase 9 | flext-3bc | Pending |
| VAL-03 | Phase 9 | flext-3bc | Pending |
| DOCS-01 | Phase 9 | flext-nya | Pending |
| DOCS-02 | Phase 9 | flext-nya | Pending |

---

## Success Metrics

| Metric | Current | Target | 
|--------|---------|--------|
| cast() usages (src/) | 34 | 0 |
| TypedDict definitions (src/) | 152 | 0 |
| Projects passing validate | 29/29 | 29 ✅ |
| Disconnected projects | 0/2 | 2 |
| Test coverage | 80%+ | 80%+ ✅ |

---

*Created: 2026-02-04*
*Milestone: v0.10.0 - Pydantic 2 Complete Migration*
