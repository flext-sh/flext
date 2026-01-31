# FLEXT Production Stability

## What This Is

A systematic stabilization initiative for 5 production-critical FLEXT projects (flext-core, flext-cli, flext-ldif, flext-ldap, client-a-oud-mig). The goal is to achieve full test coverage, type safety, and clean CI pipelines across all projects using Python 3.13+ modern syntax and ast-grep for bulk transformations.

## Core Value

**Every project must pass `make validate` with zero errors, 80%+ coverage, and strict type checking.** If a project can't be deployed confidently, nothing else matters.

## Requirements

### Validated

(Existing capabilities - inferred from codebase mapping)

- ✓ FlextResult[T] railway-oriented error handling — existing in flext-core
- ✓ 4-tier architecture (constants → models → servers → services) — existing
- ✓ Pydantic v2 models with validation — existing
- ✓ Protocol-based dependency injection — existing
- ✓ RFC 2849/4512 LDIF processing — existing in flext-ldif
- ✓ LDAP operations with quirks handling — existing in flext-ldap
- ✓ Oracle UD migration capabilities — existing in client-a-oud-mig

### Active

- [ ] All tests pass without timeouts in all 5 projects
- [ ] Zero MyPy/Pyrefly errors (strict mode) in all 5 projects
- [ ] 80%+ test coverage in all 5 projects
- [ ] `make validate` passes cleanly in all 5 projects
- [ ] Python 3.13+ modern syntax (T | None, list[T], dict[K, V]) throughout
- [ ] No cast() usage - replaced with Models/Protocols/TypeGuards
- [ ] No TYPE_CHECKING blocks - circular dependencies properly resolved
- [ ] Missing test dependencies resolved (returns, beartype)

### Out of Scope

- New feature development — stability first
- Projects outside the 5 critical ones — focused scope
- Performance optimization — not blocking production
- Documentation updates — unless blocking tests

## Context

**Current State (from codebase mapping):**
- 14,908 instances of deprecated `Optional[T]` pattern
- 717 MyPy errors pending resolution
- 26,627 suppressed warnings (`# noqa`, `# type: ignore`)
- flext-ldif test suite timing out (~4% completion)
- Missing dependencies: `returns`, `beartype` modules
- Test failure: `ldif_max_line_length` expects 199, gets 100

**Previous Session Work:**
- FlextSettings initialization fix (field validators not executing)
- Changed inheritance to `p.ProtocolSettings`
- Partial test infrastructure repairs
- Singleton reset mechanism for test isolation

**Environment:**
- Each project has its own `.venv`
- Python 3.13+ required
- Poetry for dependency management
- Pyrefly/MyPy for type checking
- Ruff for linting

## Constraints

- **Tech Stack**: Python 3.13+ with strict typing, no backwards compatibility
- **Tool**: ast-grep for bulk syntax transformations
- **Coverage**: 80% minimum enforced per project
- **Quality**: Zero tolerance for Any, cast(), TYPE_CHECKING, type: ignore
- **Isolation**: Each project's .venv must be self-contained

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use ast-grep for bulk transforms | 14,908 changes too many for manual editing | — Pending |
| Python 3.13 modern syntax only | Project requirement, no backwards compat | — Pending |
| Fix in dependency order | flext-core first (all depend on it) | — Pending |
| Per-project venvs | Isolation prevents cross-contamination | — Pending |

---
*Last updated: 2026-01-31 after initialization*
