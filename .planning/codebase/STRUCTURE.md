# Codebase Structure

**Analysis Date:** 2026-03-23

## Directory Layout

```
flext/                                    # Monorepo root
├── AGENTS.md                            # Canonical governance (supreme law)
├── base.mk                              # Shared make targets across workspace
├── flext-core/                          # L1 Foundation + L0 Contracts
│   ├── src/flext_core/
│   │   ├── __init__.py                 # AUTO-GENERATED lazy exports
│   │   ├── _models/                    # Domain entities, aggregates, CQRS
│   │   ├── _constants/                 # Validation, settings, platform constants
│   │   ├── _protocols/                 # Structural typing contracts
│   │   ├── _typings/                   # Type aliases and contracts
│   │   ├── _utilities/                 # Helper functions (guards, introspection)
│   │   ├── models.py                   # FlextModels facade
│   │   ├── constants.py                # FlextConstants facade
│   │   ├── protocols.py                # FlextProtocols facade
│   │   ├── typings.py                  # FlextTypes facade
│   │   ├── utilities.py                # FlextUtilities facade
│   │   ├── runtime.py                  # Runtime bridge for external libs
│   │   ├── context.py                  # FlextContext (correlation, metadata)
│   │   ├── dispatcher.py               # Message dispatcher (CQRS routing)
│   │   ├── container.py                # DI container management
│   │   ├── service.py                  # FlextService base class
│   │   ├── handlers.py                 # Handler decorators and registration
│   │   ├── result.py                   # r[T] Result type
│   │   ├── registry.py                 # Resource registry
│   │   ├── exceptions.py               # Domain exceptions
│   │   ├── decorators.py               # CQRS decorators
│   │   ├── loggings.py                 # FlextLogger
│   │   └── lazy.py                     # Lazy loading utilities
│   ├── tests/                          # Core unit tests
│   │   ├── conftest.py                 # Pytest fixtures (centralized)
│   │   └── test_*.py                   # Test modules
│   ├── pyproject.toml                  # Core dependencies (pydantic, orjson, etc)
│   └── Makefile                        # Project-specific targets
│
├── flext-api/                          # L3 HTTP REST API
│   ├── src/flext_api/
│   │   ├── __init__.py                 # AUTO-GENERATED lazy exports
│   │   ├── api.py                      # FlextApi (HTTP facade)
│   │   ├── app.py                      # FastAPI app factory
│   │   ├── server.py                   # Protocol-agnostic server
│   │   ├── server_factory.py           # Server creation and configuration
│   │   ├── client.py                   # FlextApiClient (HTTP worker)
│   │   ├── models.py                   # FlextApiModels (request/response)
│   │   ├── constants.py                # FlextApiConstants (HTTP-specific)
│   │   ├── protocols.py                # FlextApiProtocols (HTTP contracts)
│   │   ├── typings.py                  # FlextApiTypes
│   │   ├── utilities.py                # FlextApiUtilities
│   │   ├── settings.py                 # FlextApiSettings model
│   │   ├── settings_manager.py         # Settings loading
│   │   ├── middleware.py               # HTTP middleware chain
│   │   ├── lifecycle_manager.py        # Server lifecycle
│   │   ├── adapters.py                 # Protocol adapters
│   │   ├── plugins.py                  # Plugin system
│   │   ├── registry.py                 # API endpoint registry
│   │   ├── storage.py                  # Storage backends
│   │   ├── transports.py               # Transport layers
│   │   ├── serializers.py              # Response serializers
│   │   ├── webhook.py                  # Webhook handlers
│   │   ├── exceptions.py               # HTTP exceptions
│   │   ├── schemas/                    # Schema validators
│   │   │   ├── _shared.py              # Shared validation
│   │   │   ├── openapi.py              # OpenAPI validator
│   │   │   ├── asyncapi.py             # AsyncAPI validator
│   │   │   └── jsonschema.py           # JSONSchema validator
│   │   └── protocol_impls/             # Protocol implementations
│   │       ├── base.py                 # Base protocol class
│   │       ├── http.py                 # HTTP protocol
│   │       ├── http_client.py          # HTTP client implementation
│   │       ├── websocket.py            # WebSocket support
│   │       ├── sse.py                  # Server-Sent Events
│   │       ├── logger.py               # Logger protocol
│   │       ├── rfc.py                  # RFC protocol
│   │       └── storage_backend.py      # Storage backend
│   ├── tests/                          # API integration tests
│   └── pyproject.toml                  # API dependencies (fastapi, httpx, gql)
│
├── flext-infra/                        # L2 Infrastructure tools
│   ├── src/flext_infra/
│   │   ├── __init__.py                 # AUTO-GENERATED
│   │   ├── basemk/                     # Makefile generation
│   │   ├── check/                      # Validation checks
│   │   ├── codegen/                    # Code generation
│   │   ├── deps/                       # Dependency management
│   │   ├── gates/                      # Quality gates
│   │   ├── models.py                   # FlextInfraModels
│   │   ├── protocols.py                # FlextInfraProtocols
│   │   ├── constants.py                # FlextInfraConstants
│   │   ├── typings.py                  # FlextInfraTypes
│   │   └── rules/                      # Refactoring rules
│   └── pyproject.toml
│
├── flext-tests/                        # Centralized test infrastructure
│   ├── src/tests/
│   │   ├── __init__.py                 # AUTO-GENERATED (exports c, m, p, t, u, h)
│   │   ├── conftest.py                 # Shared pytest fixtures
│   │   ├── constants.py                # FlextTestsConstants
│   │   ├── models.py                   # FlextTestsModels
│   │   ├── protocols.py                # FlextTestsProtocols
│   │   ├── typings.py                  # FlextTestsTypes
│   │   ├── utilities.py                # FlextTestsUtilities
│   │   ├── helpers.py                  # FlextTestsHelpers (builders, factories)
│   │   ├── builders/                   # Test builders (fluent object creation)
│   │   └── factories/                  # Test factories (data generation)
│   └── pyproject.toml
│
├── flext-web/                          # L3 Web frontend
│   ├── src/flext_web/
│   │   ├── models.py                   # FlextWebModels
│   │   └── ...                         # Web-specific modules
│   └── pyproject.toml
│
├── flext-cli/                          # L3 CLI orchestration
│   ├── src/flext_cli/
│   │   ├── models.py                   # FlextCliModels
│   │   ├── app.py                      # CLI app factory
│   │   └── ...                         # CLI-specific modules
│   └── pyproject.toml
│
├── flext-meltano/                      # L2/L3 Meltano platform integration
│   ├── src/flext_meltano/
│   │   ├── models.py                   # FlextMeltanoModels
│   │   ├── protocols.py                # FlextMeltanoProtocols
│   │   └── ...
│   └── pyproject.toml
│
├── flext-tap-*/                        # L3 Singer TAP integrations
│   ├── flext-tap-ldap/                 # TAP LDAP (Meltano + LDAP)
│   ├── flext-tap-oracle/               # TAP Oracle (Meltano + Oracle)
│   ├── flext-tap-oracle-wms/           # TAP Oracle WMS
│   ├── flext-tap-oracle-oic/           # TAP Oracle OIC
│   └── flext-tap-ldif/                 # TAP LDIF
│
├── flext-target-*/                     # L3 Singer TARGET integrations
│   ├── flext-target-ldap/              # TARGET LDAP
│   ├── flext-target-oracle/            # TARGET Oracle
│   ├── flext-target-oracle-wms/        # TARGET Oracle WMS
│   ├── flext-target-oracle-oic/        # TARGET Oracle OIC
│   └── flext-target-ldif/              # TARGET LDIF
│
├── flext-dbt-*/                        # L3 dbt integration projects
│   ├── flext-dbt-ldap/                 # dbt LDAP
│   ├── flext-dbt-ldif/                 # dbt LDIF
│   ├── flext-dbt-oracle/               # dbt Oracle
│   └── flext-dbt-oracle-wms/           # dbt Oracle WMS
│
├── flext-auth/                         # L2 Authentication/Authorization
│   ├── src/flext_auth/
│   │   ├── models.py                   # FlextAuthModels
│   │   └── ...
│   └── pyproject.toml
│
├── flext-observability/                # L2 Observability (metrics, tracing)
│   ├── src/flext_observability/
│   │   └── ...
│   └── pyproject.toml
│
├── flext-quality/                      # L2 Quality (linting, validation)
│   ├── src/flext_quality/
│   └── pyproject.toml
│
├── flext-grpc/                         # L3 gRPC protocol support
├── flext-plugin/                       # L3 Plugin system
├── flext-db-oracle/                    # L2 Oracle DB connector
├── flext-ldap/                         # L2 LDAP domain
├── flext-ldif/                         # L2 LDIF domain
├── flext-oracle-wms/                   # L2 Oracle WMS domain
├── flext-oracle-oic/                   # L2 Oracle OIC domain
│
├── .planning/
│   └── codebase/                       # GSD codebase analysis documents
│       ├── ARCHITECTURE.md             # This layer architecture
│       └── STRUCTURE.md                # This directory structure
│
└── docs/                               # Documentation
    ├── maintenance/                    # Maintenance guides
    └── ...
```

## Directory Purposes

**flext-core:**
- Purpose: Foundation layer (L1) and Contracts (L0) - shared by all projects
- Contains: Base models, constants, protocols, types, utilities, dispatcher, context management, DI container
- Key files: `models.py`, `constants.py`, `protocols.py`, `typings.py`, `utilities.py`, `dispatcher.py`, `context.py`, `service.py`

**flext-api:**
- Purpose: HTTP REST API implementation (L3 Orchestration)
- Contains: FastAPI app, HTTP client, schema validators, protocol implementations, middleware, lifecycle management
- Key files: `api.py` (facade), `server.py`, `client.py`, `models.py`, `app.py`, `middleware.py`

**flext-infra:**
- Purpose: Infrastructure automation and code generation (L2)
- Contains: Makefile generation, dependency modernization, code generation (codegen), validation checks, refactoring rules
- Key files: `basemk/`, `codegen/`, `deps/`, `gates/`, `rules/`

**flext-tests:**
- Purpose: Centralized test infrastructure and utilities (test support for all projects)
- Contains: Test builders, factories, fixtures, constants, models, protocols specific to testing
- Key files: `conftest.py`, `helpers.py`, `builders/`, `factories/`

**flext-web:**
- Purpose: Web frontend framework (L3)
- Contains: Frontend-specific models, components, middleware

**flext-cli:**
- Purpose: CLI application and orchestration (L3)
- Contains: CLI commands, input parsing, orchestration logic

**flext-meltano:**
- Purpose: Meltano ELT platform integration (L2/L3)
- Contains: Singer TAP/TARGET support, Meltano plugin system integration

**flext-tap-* and flext-target-*:**
- Purpose: Singer protocol implementations (L3 Orchestration)
- Pattern: Each is a composition of platform (flext-meltano) + domain (flext-ldap, flext-oracle-wms, etc.)
- Example: `flext-tap-ldap` = `class FlextTapLdapProtocols(FlextMeltanoProtocols, FlextLdapProtocols): pass`

**flext-dbt-*:**
- Purpose: dbt model transformations (L3 Orchestration)
- Pattern: Similar composition: platform (dbt runner) + domain

**flext-auth, flext-observability, flext-quality:**
- Purpose: Cross-cutting infrastructure (L2)
- Contains: Shared capabilities for authentication, observability, and quality checking

**flext-db-oracle, flext-ldap, flext-ldif, flext-oracle-wms, flext-oracle-oic:**
- Purpose: Domain-specific modules (L2 Infrastructure)
- Pattern: Strict boundaries (oracle-wms ≠ db-oracle; ldap ≠ ldif)
- Contains: Domain models, protocols, constants specific to that integration point

## Key File Locations

**Entry Points:**

- `flext-core/src/flext_core/dispatcher.py`: CQRS message dispatcher
- `flext-core/src/flext_core/service.py`: Base service lifecycle
- `flext-api/src/flext_api/api.py`: HTTP REST facade
- `flext-api/src/flext_api/server.py`: Protocol-agnostic server
- `flext-cli/src/flext_cli/app.py`: CLI app factory
- `flext-web/src/flext_web/app.py`: Web app factory

**Configuration:**

- `flext-core/src/flext_core/settings.py`: Core runtime settings
- `flext-api/src/flext_api/settings.py`: API server settings
- `flext-api/src/flext_api/settings_manager.py`: Settings loading from env/files
- `flext-*/pyproject.toml`: Project dependencies and metadata

**Core Logic:**

- `flext-core/src/flext_core/_models/`: Domain entities, aggregates, CQRS messages
- `flext-core/src/flext_core/_utilities/`: Shared helper functions
- `flext-core/src/flext_core/_constants/`: Validation bounds, HTTP status codes, settings
- `flext-api/src/flext_api/client.py`: HTTP request/response handling

**Testing:**

- `flext-tests/src/tests/conftest.py`: Shared pytest fixtures
- `flext-tests/src/tests/helpers.py`: Test builders and factories
- `flext-*/tests/test_*.py`: Project-specific unit/integration tests
- `flext-tests/src/tests/builders/`: Fluent test object builders
- `flext-tests/src/tests/factories/`: Data generation factories

## Naming Conventions

**Files:**

- `models.py`: Facade class `Flext*Models` composing all domain models
- `constants.py`: Facade class `Flext*Constants` composing all constants
- `protocols.py`: Facade class `Flext*Protocols` composing all structural typing
- `typings.py`: Facade class `Flext*Types` with type aliases
- `utilities.py`: Facade class `Flext*Utilities` composing all helpers
- `helpers.py`: Test-specific helpers (test builders, factories)
- `_models/`: Directory containing domain-specific model subclasses
- `_constants/`: Directory containing domain-specific constant groups
- `_utilities/`: Directory containing domain-specific utility functions
- `_protocols/`: Directory containing structural typing contracts
- `_typings/`: Directory containing type alias groups

**Directories:**

- `flext-<platform>/`: Platform implementations (api, web, cli, meltano)
- `flext-<domain>/`: Domain-specific modules (ldap, oracle, oracle-wms, ldif, oracle-oic)
- `flext-<platform>-<domain>/`: Integration projects (tap-ldap, target-oracle-wms, dbt-ldap)
- `src/flext_*/`: Package source code
- `tests/`: Project-specific tests

**Classes:**

- `Flext<Project><Tier><Facade>`: E.g., `FlextCoreModels`, `FlextApiModels`, `FlextTestInfraHelpers`
- Pattern: `Flext` prefix, project/domain name, tier (Models, Constants, Protocols, Utilities, Helpers), facade type
- Integration projects omit platform in name: `FlextTapLdapProtocols` (not `FlextTapMeltanoLdapProtocols`)

## Where to Add New Code

**New Feature (Domain Logic):**
- Primary code: `flext-<domain>/src/flext_<domain>/_models/feature.py` (model class)
- Tests: `flext-<domain>/tests/test_feature.py`
- Shared utilities: `flext-core/src/flext_core/_utilities/feature_utils.py`
- Constants: `flext-core/src/flext_core/_constants/feature_constants.py`

**New Component/Module:**
- Implementation: Create new directory under `flext-<domain>/src/flext_<domain>/`
- Facade class: `flext-<domain>/src/flext_<domain>/<module>.py` with `Flext<Domain><Module>` class
- Sub-components: Store in `flext-<domain>/src/flext_<domain>/_<module>/`
- Export: Auto-generated in `__init__.py` via `make codegen`

**Utilities (Shared Helpers):**
- Shared helpers: `flext-core/src/flext_core/_utilities/<purpose>/` (guards, introspection, transformers)
- Access: Always via `u.*` namespace alias (never direct import)
- Test helpers: `flext-tests/src/tests/helpers.py` or `flext-tests/src/tests/builders/`

**Constants:**
- Domain-specific: `flext-<domain>/src/flext_<domain>/_constants.py`
- Shared validation: `flext-core/src/flext_core/_constants/validation.py`
- Access: Always via `c.*` namespace alias

**Tests:**
- Unit tests: `flext-<project>/tests/test_<module>.py`
- Test infrastructure: `flext-tests/src/tests/<purpose>/`
- Fixtures: Centralized in `flext-tests/src/tests/conftest.py`
- Builders: `flext-tests/src/tests/builders/<entity>.py`

## Special Directories

**`.planning/codebase/`:**
- Purpose: GSD (Grand Software Design) codebase analysis documents
- Generated: No (manually maintained by developers)
- Committed: Yes
- Contents: ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, CONCERNS.md

**`.beads/`:**
- Purpose: Distributed issue tracking (alternative to GitHub Issues)
- Generated: Yes (automatically managed)
- Committed: No (.gitignored)
- Contents: Issue metadata, task tracking

**`.reports/`:**
- Purpose: Test reports, coverage, validation results
- Generated: Yes (by `make test`, `make validate`)
- Committed: Partially (tracked in git)
- Contents: Coverage reports, test results, validation logs

**`docs/`:**
- Purpose: Documentation (maintenance guides, architectural decisions)
- Generated: No
- Committed: Yes
- Contents: .md files for project documentation

**`scripts/`:**
- Purpose: Utility scripts for development
- Generated: No
- Committed: Yes
- Contents: Python scripts for code generation, migration, validation

**`examples/`:**
- Purpose: Example code demonstrating usage patterns
- Generated: No
- Committed: Yes
- Contents: Runnable examples using flext modules

**`tests/`:**
- Purpose: Unit and integration tests for the project
- Generated: No
- Committed: Yes
- Contents: Test files following pytest conventions

**`docker/`:**
- Purpose: Docker images and containers
- Generated: No
- Committed: Yes
- Contents: Dockerfiles, docker-compose configurations

---

**GSD Structure Sync:** All workspace projects follow this hierarchy. Use `make validate VALIDATE_SCOPE=workspace` to check structure compliance.
