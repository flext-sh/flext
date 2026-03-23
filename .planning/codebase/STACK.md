# Technology Stack

**Analysis Date:** 2026-03-23

## Languages

**Primary:**
- Python 3.13 - All application code, data integration, API services, and infrastructure tooling
- Go - Limited usage in `flexcore/` for CLI/command utilities

**Secondary:**
- YAML - Configuration files, dbt/meltano definitions, docker-compose files
- TOML - pyproject.toml project manifests
- SQL - Database operations and schema management via dbt
- Protocol Buffers - gRPC service definitions

## Runtime

**Environment:**
- Python 3.13 (strict requirement: `requires-python = ">=3.13,<3.14"`)

**Package Manager:**
- Poetry 2.0+ (via poetry-core)
- uv - Virtual environment and dependency management
- Lockfile: `poetry.lock` (present in workspace)

## Frameworks

**Core:**
- Pydantic 2.12+ - Data validation, settings management, type safety
- FastAPI 0.116+ - REST API framework (flext-api, flext-tap-oracle, flext-meltano)
- Flask 3+ - Web framework (flext-web, flext-observability)
- SQLAlchemy 2.0+ - Database ORM and query builder

**Data Integration:**
- Meltano (git fork: `flext/relax-deps`) - Data pipeline orchestration platform
- dbt-core (git fork: `flext/relax-deps`) - Analytics engineering, transformations
- Singer SDK 0.52+ - Tap/target framework for ETL

**RPC & Microservices:**
- gRPC 1.76+ - High-performance RPC framework
- Protobuf 6.33+ - Message serialization

**Testing:**
- pytest 8.4+ - Test runner
- pytest-xdist 3.8+ - Parallel test execution
- pytest-benchmark 5.1+ - Performance testing
- factory-boy 3.3+ - Test fixtures and factories
- hypothesis 6.125+ - Property-based testing

**Build/Dev:**
- ruff 0.12+ - Linter and formatter (Python)
- pyrefly - Type checking (experimental/custom)
- pyright - Static type checker (strict mode)
- mypy 1.18+ - Type checker with Pydantic plugin
- black 25.1+ - Code formatter
- deptry 0.23+ - Dependency analysis

**Documentation:**
- mkdocs 1.6+ - Static documentation generator
- mkdocstrings 0.24+ - Docstring-driven documentation
- Material theme - Professional documentation theme

## Key Dependencies

**Critical:**
- `pydantic-core>=2.41.4` - Pydantic validation engine (required across all projects)
- `pydantic-settings>=2.10.1` - Environment-based configuration
- `pydantic-extra-types[semver]>=2.10` - Extra type validators
- `dependency-injector>=4.41` - Dependency injection container (flext-core)
- `structlog>=25.4` - Structured logging (flext-core, flext-ldap, flext-observability)
- `orjson>=3.11.3` - Fast JSON serialization

**Infrastructure:**
- `docker>=7.1,<8` - Docker Python SDK for container operations
- `python-on-whales>=0.79` - Docker CLI wrapper
- `psutil>=5.9` - System and process utilities (flext-grpc)

**Database:**
- `oracledb>=2` - Oracle Database adapter (flext-db-oracle, flext-tap-oracle)
- `ldap3>=2.9` - LDAP/Active Directory operations (flext-ldap)

**Authentication & Security:**
- `cryptography>=45.0.5` - Cryptographic operations (flext-ldap, flext-auth)
- `bcrypt>=4.3` - Password hashing (flext-auth)
- `pyjwt>=2.9` - JWT token operations (flext-auth)

**Monitoring & Observability:**
- `opentelemetry-sdk>=1.39.1,<2` - OTEL tracing/metrics backend
- `opentelemetry-exporter-otlp-proto-grpc>=1.39.1` - OTEL gRPC exporter
- `opentelemetry-exporter-prometheus>=0.60b1` - OTEL Prometheus exporter
- `prometheus-client>=0.23` - Prometheus metrics client

**Data Processing:**
- `duckdb>=1` - In-process analytical SQL database (flext-meltano)
- `pandas>=2` - Data manipulation and analysis (flext-meltano)
- `sqlalchemy>=2` - SQL toolkit and ORM (flext-grpc, flext-meltano)

**Serialization:**
- `msgpack>=1.1.2` - Binary serialization (flext-api)
- `cbor2>=5.7` - CBOR binary serialization (flext-api)
- `websockets>=15.0.1` - WebSocket protocol support (flext-api)

**Code Analysis & Refactoring:**
- `libcst>=1.5.1` - Concrete syntax tree parser (flext-infra)
- `rope>=1.14.0,<2.0.0` - Python refactoring library (flext-infra, flext-core)

**Miscellaneous:**
- `jinja2>=3.1.6` - Template engine (flext-core, flext-meltano)
- `cachetools>=5.3` - Caching decorators (flext-core)
- `limits>=3.6` - Rate limiting (flext-core)
- `pybreaker>=0.8` - Circuit breaker pattern (flext-core)
- `wrapt>=1.17` - Function wrapper utilities
- `returns>=0.26` - Functional return types (flext-core)
- `tomlkit>=0.13` - TOML library with formatting preservation
- `pyyaml>=6.0.2` - YAML parsing and serialization
- `importlib-resources>=6.5.2` - Resource loading
- `typing-extensions>=4.15` - Extended typing utilities
- `tenacity>=9.1.2` - Retry decorator (flext-oracle-oic)
- `typer>=0.12-0.15` - CLI framework (flext-observability, flext-oracle-oic)
- `rich>=14.2,<15` - Rich terminal output (flext-observability)
- `starlette>=0.52.1` - ASGI framework (flext-observability)

## Configuration

**Environment:**
- `.envrc` - direnv configuration for automatic venv activation and environment setup
- `VIRTUAL_ENV` - Points to `${PWD}/.venv`
- `PYTHONPATH` - Includes workspace `src/` directory
- `PYTHON_KEYRING_BACKEND="keyring.backends.null.Keyring"` - Disable system keyring
- `PYTHONDONTWRITEBYTECODE=1` - Skip .pyc generation
- `PYTHONUNBUFFERED=1` - Unbuffered stdout/stderr

**Build:**
- `base.mk` - Shared Makefile patterns for all projects
- `pyproject.toml` - Root workspace configuration with centralized tool configs:
  - `[tool.ruff]` - Linter and formatter rules (line-length: 88, target: py313)
  - `[tool.pyright]` - Type checker configuration (strict mode)
  - `[tool.pyrefly]` - Type checking configuration
  - `[tool.mypy]` - Type checking with Pydantic plugin
  - `[tool.pytest.ini_options]` - Test configuration with markers
  - `[tool.coverage.report]` - Coverage thresholds (45% minimum)

**Project Structure:**
- 50+ independent Python projects with standardized `pyproject.toml` structure
- All managed projects follow [MANAGED] sections controlled by `flext_infra.deps.modernizer`
- Custom extension points marked [CUSTOM] for project-specific configuration
- Consolidated development dependencies across workspace

## Platform Requirements

**Development:**
- Python 3.13 with venv/uv support
- direnv for environment management
- Poetry for dependency resolution
- Docker (for containerized services during development)
- Go 1.x (for flexcore command utilities)

**Production:**
- Python 3.13 runtime
- Docker container runtime (implied by composition files)
- Network connectivity to:
  - Oracle Database instances
  - LDAP/Active Directory servers
  - OpenTelemetry OTLP endpoints (optional)
  - Prometheus scrape endpoints (optional)

---

*Stack analysis: 2026-03-23*
