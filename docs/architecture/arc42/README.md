# FLEXT arc42 Architecture Documentation

<!-- TOC START -->
- [Template Structure](#template-structure)
- [FLEXT Architecture Overview](#flext-architecture-overview)
- [Key Architectural Principles](#key-architectural-principles)
  - [1. Clean Architecture](#1-clean-architecture)
  - [2. Domain-Driven Design](#2-domain-driven-design)
  - [3. Railway-Oriented Programming](#3-railway-oriented-programming)
  - [4. Single Source of Truth](#4-single-source-of-truth)
- [Quality Attributes](#quality-attributes)
  - [Reliability](#reliability)
  - [Security](#security)
  - [Maintainability](#maintainability)
- [Related Documentation](#related-documentation)
- [Additional Resources](#additional-resources)
<!-- TOC END -->

**Reviewed**: 2026-07-12 | **Scope**: arc42 index and architecture overview

This directory documents the FLEXT workspace architecture following the
[arc42 template](https://arc42.org/). Each chapter is one numbered file; this
page is the index and the high-level overview.

## Template Structure

1. [Introduction and Goals](./01-introduction-and-goals.md) — requirements, quality goals, stakeholders
2. [Constraints](./02-constraints.md) — technical and organizational constraints
3. [Context and Scope](./03-context-and-scope.md) — system context and external interfaces
4. [Solution Strategy](./04-solution-strategy.md) — fundamental decisions and solution approaches
5. [Building Block View](./05-building-block-view.md) — package layering, canonical structure, facades
6. [Runtime View](./06-runtime-view.md) — key runtime scenarios
7. [Deployment View](./07-deployment-view.md) — infrastructure and deployment
8. [Cross-cutting Concepts](./08-cross-cutting-concepts.md) — workspace-wide invariants
9. [Architectural Decisions](./09-architectural-decisions.md) — decision log
10. [Quality Requirements](./10-quality-requirements.md) — quality tree and scenarios
11. [Risks and Technical Debt](./11-risks-and-technical-debt.md) — known risks and debt
12. [Glossary](./12-glossary.md) — canonical terms

## FLEXT Architecture Overview

FLEXT is an enterprise data-integration platform built on modern
architectural patterns:

- **Clean Architecture** — domain at the core, frameworks and drivers at the edge
- **Domain-Driven Design** — business logic modeled in typed domain models
- **Railway-Oriented Programming** — `r[T]` result composition for error handling
- **Singer/Meltano ecosystem** — taps and targets for data-integration workflows
- **Typed monorepo** — one foundation (`flext-core → flext-cli → flext-infra`)
  shared by every `flext-*` package

## Key Architectural Principles

### 1. Clean Architecture

- **Dependency Inversion**: high-level modules do not depend on low-level modules
- **Layer Separation**: clear boundaries between presentation, application, domain, and infrastructure
- **Testability**: each layer can be tested independently

### 2. Domain-Driven Design

- **Rich Domain Models**: business logic encapsulated in Pydantic 2-way models
- **Bounded Contexts**: clear boundaries between domain packages
- **Ubiquitous Language**: common vocabulary between business and technical teams

### 3. Railway-Oriented Programming

- **r[T]**: monadic result handling with composition
- **Happy Path**: success flows through the system
- **Sad Path**: typed failures with context instead of exception-driven control flow

### 4. Single Source of Truth

- **One canonical owner per concern**: facades, config, settings, rules
- **Enforcement as data**: static rules are validated YAML records, not code
- **Generated surfaces**: derived docs and manifests are reproduced by the
  engine, never edited by hand

## Quality Attributes

### Reliability

- **Typed contracts**: `r[T]` on every fallible path; Pydantic validation at every boundary
- **Continuous green**: the tree stays importable and collectable at every commit
- **Gate discipline**: lint, typecheck, tests, and docs audit are blocking

### Security

- **Authentication**: pluggable providers (JWT, OAuth2, OIDC, SAML, LDAP, …) via `flext-auth`
- **Data protection**: encryption and secure communication through the provider layer
- **Audit trail**: structured logging across all services

### Maintainability

- **Modularity**: clear separation of concerns per package and facet
- **Testability**: public-interface testing through the `flext-tests` framework
- **Documentation**: code-driven API reference and strict docs gates
- **Extensibility**: plugin architecture for custom functionality

## Related Documentation

- [Architecture Decision Records](../adr/README.md)
- [Code Communities](../communities/index.md) — generated from the code knowledge graph
- C4 Model Diagrams — `docs/architecture/c4-model/` (repo-only reference)
- Deployment Architecture — `docs/architecture/deployment/` (repo-only reference)
- Security Architecture — `docs/architecture/security/` (repo-only reference)
- Data Architecture — `docs/architecture/data/` (repo-only reference)

## Additional Resources

- [arc42 Template](https://arc42.org/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Railway-Oriented Programming](https://fsharpforfunandprofit.com/rop/)
