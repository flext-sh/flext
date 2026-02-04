# Codebase Structure

**Analysis Date:** 2026-01-31

## Directory Layout

```
flext/ (monorepo root - git superproject)
├── flext-core/                 # Foundation library (all projects depend on this)
├── flext-cli/                  # CLI framework and command routing
├── flext-api/                  # REST API framework (FastAPI/Pydantic integration)
├── flext-auth/                 # Authentication/authorization services
├── flext-ldif/                 # RFC 2849/4512 LDIF processing
├── flext-ldap/                 # LDAP operations and directory services
├── flext-db-oracle/            # Oracle database integration (SQLAlchemy 2.0)
├── flext-grpc/                 # gRPC services and protobuf integration
├── flext-plugin/               # Plugin management system
├── flext-quality/              # Code quality analysis and validation
├── flext-observability/        # Observability (metrics, traces, events)
├── flext-meltano/              # Meltano ELT orchestration
│
├── flext-tap-ldap/             # LDAP data tap (Singer protocol, Meltano source)
├── flext-tap-ldif/             # LDIF data tap
├── flext-tap-oracle/           # Oracle data tap
├── flext-tap-oracle-oic/       # Oracle OIC data tap
├── flext-tap-oracle-wms/       # Oracle WMS data tap
│
├── flext-target-ldap/          # LDAP data target (Singer protocol, Meltano sink)
├── flext-target-ldif/          # LDIF data target
├── flext-target-oracle/        # Oracle data target
├── flext-target-oracle-oic/    # Oracle OIC data target
├── flext-target-oracle-wms/    # Oracle WMS data target
│
├── flext-dbt-ldap/             # dbt transformation models for LDAP
├── flext-dbt-ldif/             # dbt transformation models for LDIF
├── flext-dbt-oracle/           # dbt transformation models for Oracle
├── flext-dbt-oracle-wms/       # dbt transformation models for Oracle WMS
│
├── flext-oracle-wms/           # Oracle Warehouse Management System integration
├── flext-oracle-oic/           # Oracle Identity Cloud Service integration
├── client-a-oud-mig/              # Oracle Unified Directory migration tool
│
├── flext-web/                  # Web UI/frontend (TypeScript)
├── web/                        # Alternative web implementation
├── .claude/                    # Claude Code configuration and skills
├── .github/                    # GitHub workflows and templates
├── docs/                       # User-facing documentation
├── docker/                     # Docker compose and container configs
├── scripts/                    # Development and utility scripts
├── base.mk                     # Shared Makefile for all projects
└── CLAUDE.md                   # Workspace standards and patterns
```

## Directory Purposes

**flext-core/ (Foundation Library):**
- Purpose: Core abstractions, types, protocols - dependency for all 30+ projects
- Contains: Railway-oriented result handling, DI container, service base, logging, configuration
- Key files: `src/flext_core/result.py`, `src/flext_core/container.py`, `src/flext_core/config.py`
- Versioning: Breaking changes affect entire ecosystem (strict backward compatibility)

**flext-cli/ (Command-Line Framework):**
- Purpose: Unified CLI command routing and output formatting
- Contains: Subcommand parser, output service, help text generation
- Key file: `src/flext_cli/api.py` (FlextCli facade)
- Usage: Base for project-specific CLIs (flext-ldif CLI, flext-ldap CLI, etc.)

**flext-api/ (REST API Framework):**
- Purpose: FastAPI integration, OpenAPI schemas, REST patterns
- Contains: Route decorators, request/response handling, CORS configuration
- Key file: `src/flext_api/api.py` (FlextApi facade)
- Usage: Base for REST services (if any projects need REST endpoints)

**flext-auth/ (Authentication):**
- Purpose: Unified authentication with pluggable providers (JWT, OAuth2, Basic)
- Contains: Provider registry, token handling, credential validation
- Key file: `src/flext_auth/api.py` (FlextAuth facade)
- Pattern: Provider-centric (all auth flows through registry)

**flext-ldif/ (LDIF Processing):**
- Purpose: RFC 2849/4512 LDIF parsing/writing with server-specific quirks
- Contains: RFC baseline parsers, quirks registry, server detection
- Key file: `src/flext_ldif/api.py` (FlextLdif facade)
- Features: 7+ server-specific quirks (OID, OUD, OpenLDAP, AD, etc.)

**flext-ldap/ (LDAP Operations):**
- Purpose: LDAP protocol operations (bind, search, modify, etc.)
- Contains: Connection pooling, search filters, entry operations
- Key file: `src/flext_ldap/api.py` (FlextLdap facade)
- Integration: Works with flext-ldif for LDIF ↔ LDAP transformations

**flext-db-oracle/ (Database Foundation):**
- Purpose: SQLAlchemy 2.0 + oracledb integration
- Contains: Connection pooling, ORM models, query builders
- Key file: `src/flext_db_oracle/api.py` (FlextDbOracleApi facade)
- Abstraction: Hides SQLAlchemy complexity, exposes simple API

**flext-tap-*/ and flext-target-*/ (Singer Protocol - Data Integration):**
- Purpose: Data extraction (taps) and loading (targets) using Singer protocol
- Contains: Stream schemas, record transformations, state management
- Pattern: Meltano plugins (executable as standalone, callable from Meltano)
- Dependency: All use flext-meltano for pipeline orchestration

**flext-dbt-*/ (dbt Transformation):**
- Purpose: dbt transformation models and macros
- Contains: SQL models, tests, documentation
- Pattern: Standalone dbt projects, integrated into flext-meltano pipelines

**flext-web/ and web/ (Frontend):**
- Purpose: Web UI for FLEXT services
- Language: TypeScript/React
- Pattern: Communicates with backend services via REST/gRPC

**.claude/ (Claude Code Configuration):**
- Purpose: AI assistant configuration, skills, agents, rules
- Contains: Project-specific skills, development patterns, MCP servers
- Key file: `.claude/CLAUDE.md` (project instructions)

**docs/ (Documentation):**
- Purpose: User guides, API reference, architecture docs
- Pattern: Markdown files, linked from README.md

**scripts/ (Development Utilities):**
- Purpose: One-time setup, batch fixes, data migration
- Pattern: Python/shell scripts, not production code
- Examples: `setup_env.sh`, `fix_*.sh` (batch corrections)

## Key File Locations

**Entry Points:**
- `flext-core/src/flext_core/__init__.py` - Root exports (FlextResult, FlextContainer, etc.)
- `flext-ldif/src/flext_ldif/api.py` - LDIF main facade
- `flext-auth/src/flext_auth/api.py` - Authentication facade
- `flext-cli/src/flext_cli/api.py` - CLI framework facade
- `flext-api/src/flext_api/api.py` - REST API facade

**Configuration:**
- `flext-core/src/flext_core/config.py` - Global configuration (FlextConfig)
- `flext-core/pyproject.toml` - Workspace Python dependencies
- `base.mk` - Shared Makefile (included by all projects)
- `ruff-shared.toml` - Shared linting rules (imported by all projects)

**Core Logic:**
- `flext-core/src/flext_core/result.py` - Railway-oriented FlextResult[T] implementation
- `flext-core/src/flext_core/container.py` - Dependency injection container
- `flext-core/src/flext_core/protocols.py` - SOLID protocols (interfaces)
- `flext-core/src/flext_core/typings.py` - Centralized type system (t.Types.*)
- `flext-core/src/flext_core/constants.py` - Centralized constants (c.Namespace.*)

**Testing:**
- `flext-core/tests/unit/` - Unit tests (no external dependencies)
- `flext-core/tests/integration/` - Integration tests (real dependencies)
- `flext-core/src/flext_tests/` - Shared test utilities (extends flext_core)

**Quality/Validation:**
- `flext-quality/src/flext_quality/api.py` - Code quality analysis facade
- `.github/workflows/` - CI/CD pipelines (GitHub Actions)
- `.qlty/` - QLT configuration for quality enforcement

## Naming Conventions

**Files:**
- `api.py` - Tier 3 facade (single main public class per project)
- `constants.py` - Tier 0 constants (Enum with Final values, no functions)
- `typings.py` - Tier 0 type definitions (TypeAlias, Protocol, TypeVar)
- `protocols.py` - Tier 0 interfaces (Protocol classes only)
- `models.py` - Tier 1 domain models facade (imports from `_models/`)
- `utilities.py` - Tier 1 helpers facade (imports from `_utilities/`)
- `settings.py` - Configuration models (if different from config.py)
- `services/` - Tier 3 business logic (one service per file, no helpers)
- `servers/` - Tier 2 infrastructure (connection pools, adapters)
- `_models/` - Internal Tier 1 submodules (aggregated by models.py)
- `_utilities/` - Internal Tier 1 submodules (aggregated by utilities.py)

**Directories:**
- `src/flext_<project>/` - Source code (always contains __init__.py)
- `tests/unit/` - Unit tests (no external dependencies)
- `tests/integration/` - Integration tests (real dependencies like databases)
- `docs/` - Project documentation

**Classes:**
- Main facade: `Flext<ProjectName>` (e.g., `FlextLdif`, `FlextAuth`)
- Service: `Flext<ProjectName><Service>` (e.g., `FlextLdifParser`, `FlextAuthRegistry`)
- Model: No `Flext` prefix if Pydantic (e.g., `LdifEntry`, `User`)
- Constant class: `Flext<ProjectName>Constants` (e.g., `FlextLdifConstants`)
- Type class: `Flext<ProjectName>Types` (e.g., `FlextLdifTypes`)
- Protocol: `Flext<ProjectName><Protocol>` (e.g., `FlextLdifServerProvider`)

**Functions/Methods:**
- Snake_case for all functions and methods
- Prefix with action verb: `parse_`, `validate_`, `fetch_`, `save_`
- Return type always annotated: `def parse(data: str) -> r[ParsedData]:`

## Where to Add New Code

**New Feature (Example: "Add LDAP Schema Validation"):**
- Primary code: `flext-ldap/src/flext_ldap/services/` (business logic)
  - Create file: `schema_validator.py` with class `FlextLdapSchemaValidator`
  - Implement: Service extends `FlextService`, returns `r[ValidationResult]`
- Models: `flext-ldap/src/flext_ldap/models.py` (domain models)
  - Add: Pydantic model `SchemaValidationError` in `m.Ldap.*` namespace
- Facade: `flext-ldap/src/flext_ldap/api.py` (expose via FlextLdap)
  - Add: Method `validate_schema(schema_data) -> r[ValidationResult]`
  - Delegate: To `FlextLdapSchemaValidator.validate()`
- Tests: `flext-ldap/tests/unit/test_schema_validator.py`
  - Pattern: Test `FlextLdapSchemaValidator` directly, real objects (no mocks)
  - Coverage: All success paths, all error conditions

**New Component/Module (Example: "Add Oracle Unified Directory Adapter"):**
- Infrastructure: `flext-ldap/src/flext_ldap/servers/oud.py` (Tier 2)
  - Implement: `FlextLdapOudServer` extending base server class
  - Returns: Domain models from Tier 1 (m.Ldap.*)
- Service: `flext-ldap/src/flext_ldap/services/oud_operations.py` (Tier 3)
  - Implement: `FlextLdapOudOperations` for OUD-specific workflows
  - Composes: `FlextLdapOudServer` + Tier 1 models
- Facade: `flext-ldap/src/flext_ldap/api.py`
  - Add: Method routing to OUD-specific service
  - Example: `connect_oud(config) -> r[OudConnection]`
- Tests: `flext-ldap/tests/unit/servers/test_oud.py`
  - Test Tier 2 infrastructure with real connections (integration tests)

**Shared Utilities:**
- Location: `flext-core/src/flext_core/utilities.py` (Tier 1)
- Pattern: Static method groups in nested classes
  - Example: `u.Validation.validate_email(email) -> r[bool]`
- Access: Via `from flext_core import FlextUtilities as u`
- For LDIF-specific: `flext-ldif/src/flext_ldif/utilities.py`

**Configuration/Constants:**
- Location: `flext-core/src/flext_core/constants.py` (shared)
- Pattern: Namespace enum (e.g., `c.Core.TIMEOUT = Final[int] = 30`)
- Project-specific: `flext-ldif/src/flext_ldif/constants.py`
  - Pattern: `c.Ldif.RFC_VERSION`, `c.Ldif.ServerTypes`

**New Entry Point (CLI Command):**
- Location: `flext-cli/src/flext_cli/commands/` (if CLI gets new command)
- Pattern: Subcommand handler class, routed from main CLI
- Returns: `r[CliOutput]` (success/failure with formatted message)

## Special Directories

**node_modules/ (JavaScript Dependencies):**
- Generated: Yes (via npm install)
- Committed: No (.gitignore)
- Regenerated when: package-lock.json changes

**.venv/ (Python Virtual Environment):**
- Generated: Yes (via poetry install or make setup)
- Committed: No (.gitignore)
- Single shared venv: Workspace-level `.venv/` shared by all projects

**build/, dist/ (Build Artifacts):**
- Generated: Yes (via poetry build or make build)
- Committed: No (.gitignore)
- Regenerated when: Source changes or version bumps

**__pycache__/ (Python Bytecode):**
- Generated: Yes (automatic on import)
- Committed: No (.gitignore)
- Automatic cleanup: Via `make clean`

**.pytest_cache/ (Test Cache):**
- Generated: Yes (via pytest)
- Committed: No (.gitignore)
- Cleared: Via `make clean`

**.coverage (Coverage Data):**
- Generated: Yes (via pytest --cov)
- Committed: No (locally, kept in CI)
- Usage: Generate coverage reports before commit

**docs/guides/ (AI Developer Guides):**
- Purpose: Patterns and checklists for Claude Code
- Examples: `dependency_injector_prompt.md`, architecture guides
- Committed: Yes (referenced by .claude/CLAUDE.md)

---

*Structure analysis: 2026-01-31*
