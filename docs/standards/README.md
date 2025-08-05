# FLEXT Standards

**Version**: 1.0.0 | **Status**: Active

## Overview

Coding standards, best practices, and quality guidelines for the FLEXT ecosystem.

## Standards Documents

### [Documentation Standards](./documentation.md)

Guidelines for writing and maintaining documentation.

### [Python Standards](./python.md)

Python coding conventions and module organization.

### [PEP Semantic Matrix](./pep-semantic.md)

PEP compliance and semantic patterns mapping.

## Key Guidelines

### Code Quality

- **Type Coverage**: 95%+ with strict MyPy
- **Docstring Coverage**: 100% for public APIs
- **Test Coverage**: 80%+ with unit and integration tests
- **Linting**: Zero errors with ruff/flake8

### Naming Conventions

- **Python**: PEP 8 compliant with semantic patterns
- **Go**: Go standard with package-level organization
- **Documentation**: Clear, concise, professional English

### Version Control

- **Commits**: Conventional commits (feat:, fix:, docs:)
- **Branches**: GitFlow with feature/fix/docs prefixes
- **PRs**: Template-based with quality checks

---

See [Patterns](../patterns/README.md) for implementation patterns.
