# Technology Stack

**Analysis Date:** 2026-01-31

## Languages

**Primary:**
- **Python** 3.13 (exact: `requires-python = ">=3.13,<3.14"`)
  - Used in all 30+ Python projects (flext-core, flext-api, flext-cli, flext-ldap, flext-ldif, flext-auth, flext-db-oracle, flext-grpc, flext-observability, flext-tap-*, flext-target-*, flext-dbt-*, client-a-oud-mig)
  - Location: `src/` directories in each project

**Secondary:**
- **Go** 1.24 (exact: `go 1.24` with toolchain `1.24.5`)
  - Orchestration layer for flexcore (`/home/marlonsc/flext/flexcore/`)
  - API wrapper and plugin system

## Runtime

**Environment:**
- Python 3.13+ only (no backward compatibility with earlier Python versions)
- Go 1.24 runtime for orchestration layer
- Docker containers for testing infrastructure (OpenLDAP, PostgreSQL, Oracle, Redis, etc.)

**Package Manager:**
- **Poetry** (Python) - Primary dependency management
  - Version: poetry-core>=1.9.0
  - Lockfile: `poetry.lock` (present in each project)
- **Go Modules** (Go) - flexcore dependency management
  - go.mod file with standard Go dependencies

## Frameworks

**Core:**
- **flext-core** 0.10.0 - Enterprise foundation framework
  - Railway-oriented error handling via `FlextResult[T]`
  - Dependency injection container (`FlextContainer`)
  - Service base class (`FlextService`)
  - Structured logging (`FlextLogger`)
  - Configuration management (`FlextConfig`)
  - Location: `flext-core/src/flext_core/`

**Web/API:**
- **FastAPI** >=0.116.0 - REST API framework (`flext-api` 0.9.0)
  - HTTP server and request handling
  - GraphQL support via `gql` library
  - Location: `flext-api/src/flext_api/`

- **Gin** v1.10.1 - Go web framework (flexcore)
  - HTTP routing and middleware in Go layer
  - Location: `flexcore/`

**Data Validation & Models:**
- **Pydantic** >=2.12.3 - Data validation and domain models
  - Pydantic v2 with strict mode
  - Used across all projects for model definition
  - Extended via `FlextModels` base classes
  - Location: `src/flext_*/models.py`

- **pydantic-settings** >=2.10.1 - Configuration management
  - Environment variable loading
  - Settings validation
  - Location: `src/flext_*/config.py`

**Database:**
- **SQLAlchemy** >=2.0.0 - ORM and SQL toolkit (`flext-db-oracle`)
  - Oracle dialect
  - Location: `flext-db-oracle/src/flext_db_oracle/`

- **GORM** v1.30.1 - Go ORM (flexcore)
  - PostgreSQL driver via gormdriver
  - Location: `flexcore/`

**LDAP/Directory:**
- **ldap3** >=3.4.4 - LDAP protocol client (`flext-ldap`)
  - Server implementations for OpenLDAP, Oracle OID/OUD
  - Location: `flext-ldap/src/flext_ldap/adapters/ldap3.py`

**RPC/Services:**
- **gRPC** v1.74.2 - Remote procedure calls (`flext-grpc`)
  - Protocol buffers for service definitions
  - Location: `flext-grpc/` and `flexcore/`

- **protobuf** v1.36.6 (Python), v1.36.6 (Go) - Service definition language
  - Message and service definitions
  - Location: `src/*/proto/` (if present)

**Data Integration:**
- **Meltano** - Data integration orchestration
  - Singer tap/target protocol implementation
  - dbt transformation runner
  - Projects: `flext-tap-ldap`, `flext-tap-oracle`, `flext-target-ldif`, `flext-dbt-*`
  - Location: `flext-meltano/`

- **Singer Protocol** - Data pipeline standard
  - Tap connectors (source extractors)
  - Target connectors (data loaders)
  - Projects: `flext-tap-*`, `flext-target-*`

- **dbt** - SQL transformation framework
  - Projects: `flext-dbt-ldif`, `flext-dbt-ldap`, `flext-dbt-oracle`, `flext-dbt-oracle-wms`
  - Transforms structured data

**Testing:**
- **pytest** >=8.4.0 - Test framework
  - Markers for unit/integration/e2e tests
  - Coverage enforcement (minimum 80%)
  - Location: `tests/` in each project

- **pytest plugins**:
  - pytest-cov >=6.2.0 - Coverage reporting
  - pytest-mock >=3.14.0 - Mocking fixtures
  - pytest-xdist >=3.8.0 - Parallel test execution
  - pytest-timeout >=2.4.0 - Timeout protection
  - pytest-randomly >=3.16.0 - Random test ordering
  - pytest-benchmark >=5.1.0 - Performance benchmarking

**Build/Dev:**
- **Ruff** >=0.12.3 - Linting and code formatting
  - Configuration: `ruff-shared.toml`
  - Targets Python 3.13

- **MyPy** >=1.18.2 - Type checking
  - Strict mode enabled
  - Alternative: Pyright

- **Pyrefly** ^0.46.3 - Pyright-based type checking
  - Strict mode enforcement
  - Configuration in `pyproject.toml`

- **pre-commit** >=4.0.1 - Git hooks framework
  - Code quality checks on commit

- **make** - Build automation
  - `base.mk` shared across projects
  - Commands: check, validate, test, lint, format

## Key Dependencies

**Critical (Core Patterns):**
- **FlextResult** (flext-core) - Railway-oriented error handling
  - Every operation returns `FlextResult[T]` (short alias: `r[T]`)
  - Composable error handling without exceptions
  - Location: `flext-core/src/flext_core/result.py`

- **FlextService** (flext-core) - Base service class
  - Dependency injection integration
  - Configuration management
  - Location: `flext-core/src/flext_core/service.py`

- **FlextContainer** (flext-core) - Dependency injection
  - dependency-injector>=4.41.0 wrapper
  - Singleton and factory providers
  - Location: `flext-core/src/flext_core/container.py`

**Infrastructure/Resilience:**
- **beartype** >=0.19.0 - Runtime type validation
  - Validates function parameters and returns
  - Used in critical paths

- **dependency-injector** >=4.41.0 - DI container library
  - Provides provider patterns
  - Supports scoped instances

- **limits** >=3.6.0 - Rate limiting
  - Token bucket implementation
  - Used in API endpoints

- **pybreaker** >=0.8.0 - Circuit breaker pattern
  - Fault tolerance
  - Prevents cascading failures

- **attrs** >=25.4.0 - Class definition helpers
  - Lightweight alternative to dataclasses
  - Used in core utilities

- **wrapt** >=1.17.0 - Function wrapping utilities
  - Decorator implementation
  - Function instrumentation

**Serialization/Encoding:**
- **orjson** >=3.11.3 - Fast JSON encoder/decoder
  - Used across all projects
  - Faster than standard json library

- **msgpack** >=1.1.2 - MessagePack serialization
  - Binary format for data exchange
  - Used in flext-api

- **cbor2** >=5.7.0 - CBOR encoding (flext-api)
  - Concise Binary Object Representation
  - Alternative serialization format

- **PyYAML** >=6.0.2 - YAML parsing
  - Configuration files
  - Location: throughout projects

**Logging & Observability:**
- **structlog** >=25.4.0 - Structured logging
  - JSON-formatted logs
  - Context management
  - Location: `flext-core/src/flext_core/loggings.py`

- **opentelemetry-api** >=1.39.1 - Observability API
  - Trace collection
  - Metrics recording
  - Location: `flext-observability/`

- **opentelemetry-sdk** >=1.39.1 - Reference implementation
  - Trace and metric processing

- **opentelemetry-exporter-otlp-proto-grpc** >=1.39.1 - OTLP exporter
  - Sends traces/metrics to OTLP collectors

- **opentelemetry-exporter-prometheus** >=0.60b1 - Prometheus exporter
  - Metrics for Prometheus scraping

- **prometheus-client** >=0.23.0 - Prometheus metrics
  - Metric types and exposition format

**Configuration:**
- **python-dotenv** >=1.0.0 - .env file loading
  - Environment variable management
  - Development configuration

- **pydantic-core** >=2.41.4 - Pydantic v2 core
  - Validation engine

**Functional Programming:**
- **returns** >=0.26.0 - Functional returns library
  - Monadic patterns
  - Error handling utilities
  - Alternative to custom Result types

**Container Management:**
- **docker** >=7.1.0 - Docker SDK
  - Container control from Python
  - Used in tests and operations

- **python-on-whales** >=0.79.0 - Docker CLI wrapper
  - Docker Compose orchestration
  - Container lifecycle management

**HTTP (Go layer - flexcore):**
- **httpx** >=0.28.1 (Python) - Async HTTP client
  - Used in flext-api

- **google.golang.org/grpc** v1.74.2 (Go) - gRPC client/server
- **go-redis/redis/v8** v8.11.5 (Go) - Redis client
- **lib/pq** v1.10.9 (Go) - PostgreSQL driver
- **go-playground/validator/v10** v10.27.0 (Go) - Struct validation

**WebSocket Support:**
- **websockets** >=15.0.1 - WebSocket protocol (flext-api)
  - Real-time communication
  - Server and client support

**Development/Testing (Optional Dependencies):**
- **hypothesis** >=6.125.0 - Property-based testing
  - Random test case generation
  - Advanced test strategies

- **factory-boy** >=3.3.1 - Test data factories
  - Object creation for tests

- **faker** >=37.4.0 - Fake data generation
  - Realistic test data

- **interrogate** >=1.7.0 - Docstring coverage
  - Minimum 80% documentation requirement

- **bandit** >=1.8.0 - Security linting
  - Vulnerability scanning
  - Configuration file checking

- **pip-audit** >=2.7.3 - Dependency vulnerability audit
  - Identifies vulnerable packages

- **detect-secrets** >=1.5.0 - Secret detection
  - Prevents accidental secret commits

- **autoflake** >=2.3.1 - Unused import removal
- **black** >=25.1.0 - Code formatter (redundant with Ruff)
- **isort** >=6.0.1 - Import sorting (redundant with Ruff)
- **radon** >=6.0.1 - Code metrics (complexity, maintainability)
- **vulture** >=2.13 - Dead code detection

## Configuration

**Environment:**
- Configuration via environment variables and `.env` files
  - `FLEXT_ENV` - Environment name (development, test, production)
  - `FLEXT_DEBUG` - Debug mode flag
  - `PYTHONPATH` - Python path (typically `/app/src` in containers)
- FlextConfig loads from `pydantic-settings` with `python-dotenv`
- Location: `flext-core/src/flext_core/config.py`

**Key configs required:**
- Python version (3.13+)
- Database connection strings (Oracle, PostgreSQL, SQLite)
- LDAP connection parameters (host, port, DN, password)
- OpenTelemetry/Prometheus endpoints (for observability)
- API keys and secrets (injected via environment)

**Build:**
- **pyproject.toml** - Project metadata and dependencies
  - Python version constraint
  - Package configuration
  - Tool settings (pytest, coverage, ruff, mypy, pyrefly)
  - Location: Root of each project

- **ruff-shared.toml** - Shared linting configuration
  - Line length: 88 characters
  - Target version: Python 3.13
  - Ignored rules for enterprise patterns
  - Location: `/home/marlonsc/flext/ruff-shared.toml`

- **Makefile** + **base.mk** - Build automation
  - make check - Quick lint + type check
  - make validate - Full pipeline (lint + type + security + test)
  - make test - Run tests with coverage
  - Location: Each project root + shared base.mk

- **github/dependabot.yml** - Dependency update automation
  - Location: `/home/marlonsc/flext/.github/dependabot.yml`

## Platform Requirements

**Development:**
- **OS**: Linux (primary), macOS, Windows WSL2
- **Python**: 3.13 with venv or Poetry virtual environments
- **Docker**: For testing infrastructure
  - Docker Compose for orchestration
  - Images: postgres:16, oracle-db, openldap, redis
- **Make**: GNU Make for build automation
- **Go**: 1.24 (for flexcore orchestration layer)
- **Git**: For version control and submodule management

**Production:**
- **Deployment target**:
  - Kubernetes (via Docker containers)
  - Docker containers
  - Bare metal with Python 3.13
- **Database backends**:
  - Oracle 12c+ (via oracledb driver)
  - PostgreSQL 12+ (via psycopg)
  - SQLite (for embedded use)
- **Directory services**:
  - OpenLDAP 1.x/2.x
  - Oracle OID
  - Oracle Unified Directory (OUD)
- **Observability stack**:
  - OpenTelemetry Collector (OTLP endpoint)
  - Prometheus (for metrics scraping)
  - Log aggregation system (via structured JSON logs)
- **Message queue** (optional, for flexcore):
  - Redis (caching and potential queue)

---

*Stack analysis: 2026-01-31*
