# External Integrations

**Analysis Date:** 2026-03-23

## APIs & External Services

**Oracle Integration Cloud (OIC):**
- Service: Oracle Integration Cloud REST API
- What it's used for: Advanced enterprise integrations, middleware operations
- SDK/Client: `requests>=2.31` + `httpx>=0.28.1` for async HTTP
- Auth: `httpx`, `urllib3>=2` (flext-oracle-oic)
- Retry strategy: `tenacity>=9.1.2` for resilient API calls
- Implementation: `flext-oracle-oic/src/flext_oracle_oic/`

**HTTP/REST APIs:**
- Client: FastAPI built-in HTTP client context + `httpx>=0.28.1` for async
- Serialization: `msgpack>=1.1.2`, `cbor2>=5.7`, `orjson>=3.11.3`, `websockets>=15.0.1`
- Implementation: `flext-api/src/flext_api/`, `flext-web/src/flext_web/`

**GraphQL (Potential):**
- Client: `gql>=4` (in flext-api dependencies)
- Purpose: GraphQL query execution capability
- Implementation: Not yet visible in codebase

## Data Storage

**Databases:**

**Oracle Database:**
- Type/Provider: Oracle RDBMS (Enterprise)
- Connection: Native Oracle connection strings
- Client: `oracledb>=2` (thin client, no ODAC required)
- Implementation: `flext-db-oracle/`, `flext-tap-oracle/`, `flext-oracle-wms/`, `flext-dbt-oracle/`, `flext-target-oracle/`
- Docker compose: `docker/docker-compose.db-oracle.yml`, `docker/docker-compose.oracle-db.yml`

**PostgreSQL:**
- Type/Provider: PostgreSQL RDBMS
- Connection: psycopg2 compatible (via `types-psycopg2>=2.9.21.20250718`)
- Purpose: Type stubs available, likely for test/example use
- Docker compose: `docker/docker-compose.postgres.yml`

**DuckDB:**
- Type/Provider: In-process analytical SQL database
- Usage: `duckdb>=1` (flext-meltano)
- Purpose: Embedded analytics and data transformation

**File Storage:**
- Local filesystem only - No S3, GCS, or cloud blob storage detected
- LDIF file format support for LDAP operations: `flext-ldif/`

**Caching:**
- In-memory caching: `cachetools>=5.3` (flext-core)
- Rate limiting: `limits>=3.6` (flext-core)
- Redis: Types available (`types-redis>=4.6`) but no redis-py dependency found
- Status: No external cache services detected

## Authentication & Identity

**Auth Provider:**
- Custom JWT-based authentication: `pyjwt>=2.9`
- Implementation: `flext-auth/src/flext_auth/`

**LDAP / Active Directory:**
- Protocol: LDAP v3
- Client: `ldap3>=2.9` (pure Python LDAP client)
- Encryption: `cryptography>=45.0.5` for SSL/TLS
- Implementation: `flext-ldap/src/flext_ldap/adapters/ldap3.py`
- Docker test instances: `docker/docker-compose.openldap.yml`
- Support modules:
  - `flext-ldif/` - LDIF (LDAP Data Interchange Format) processing
  - `flext-tap-ldap/` - LDAP data source connector
  - `flext-target-ldap/` - LDAP data sink connector
  - `flext-dbt-ldap/` - dbt adapter for LDAP

**OAuth 2.0:**
- Not detected in direct dependencies
- Likely abstracted through integration adapters

**Password Security:**
- Hashing: `bcrypt>=4.3` (flext-auth)
- Key derivation: `cryptography>=45.0.5`

## Monitoring & Observability

**Error Tracking:**
- Service: Not configured (No Sentry, Rollbar, etc.)
- Approach: Application-level exception handling with structured logging

**Logs:**
- Framework: `structlog>=25.4` (structured JSON logging)
- Output: Application logs (stdio/stderr)
- Integration: OpenTelemetry compatible
- Implementation: `flext-observability/src/flext_observability/`

**Metrics:**
- Framework: OpenTelemetry + Prometheus
- Exporters:
  - `opentelemetry-exporter-prometheus>=0.60b1` - Prometheus metrics
  - `opentelemetry-exporter-otlp-proto-grpc>=1.39.1` - OTEL gRPC backend
- Client: `prometheus-client>=0.23` for direct instrumentation
- Scrape endpoint: Exposed via Flask/FastAPI in observability services
- Implementation: `flext-observability/src/flext_observability/`

**Tracing:**
- Framework: OpenTelemetry SDK
- Backend: OTEL Collector via gRPC (`opentelemetry-exporter-otlp-proto-grpc`)
- Instrumentation: Automatic via OTEL decorators and middleware

**Telemetry:**
- SDK: `opentelemetry-sdk>=1.39.1,<2` (full implementation)
- Metrics collection: Integrated across microservices

## CI/CD & Deployment

**Hosting:**
- Docker containers (Compose-based deployment)
- Host agnostic - can run on any Docker-capable infrastructure

**CI Pipeline:**
- Service: Not explicitly detected
- Build: Make-based (`base.mk`, `make build`, `make test`)
- Quality gates: Ruff (linting), pyright/pyrefly (type checking), pytest (tests)
- Validation: `make validate`, `make check` (see base.mk)

**Deployment:**
- Approach: Docker Compose for local/dev deployment
- Orchestration: None detected (no Kubernetes manifests)
- Container images: Built from `docker/images/` directory

## Environment Configuration

**Required env vars:**
- `VIRTUAL_ENV` - Python virtual environment path
- `PYTHONPATH` - Module search paths
- `PYTHONDONTWRITEBYTECODE` - Optimize runtime
- `PYTHONUNBUFFERED` - Streaming output
- Project-specific variables per service (in `pydantic-settings` configs)

**Secrets location:**
- Environment variables only
- `.env` files supported via `python-dotenv>=1`
- `PYTHON_KEYRING_BACKEND="keyring.backends.null.Keyring"` - No system keyring integration

**Configuration:**
- Pydantic Settings models: `pydantic-settings>=2.10.1`
- YAML-based configuration: `pyyaml>=6.0.2`
- Jinja2 templates for config: `jinja2>=3.1.6`

## Webhooks & Callbacks

**Incoming:**
- FastAPI endpoints: `flext-api/src/flext_api/`, `flext-tap-oracle/src/`
- Flask endpoints: `flext-web/src/flext_web/`
- gRPC services: `flext-grpc/src/flext_grpc/`
- Status: Webhook endpoints available, no public registry detected

**Outgoing:**
- Singer targets (`flext-target-*`) - Stream data to external systems
- HTTP client capabilities: `httpx>=0.28.1`, `requests>=2.31`
- Callback chains: Supported via FastAPI background tasks
- Status: No outbound webhook registry

## Data Integration Pipelines

**Singer Protocol (Tap/Target):**
- Framework: `singer-sdk>=0.52`
- Taps (data sources):
  - `flext-tap-oracle/` - Oracle Database
  - `flext-tap-ldap/` - LDAP Directory
  - `flext-tap-ldif/` - LDIF File Format
  - `flext-tap-oracle-oic/` - Oracle Integration Cloud
  - `flext-tap-oracle-wms/` - Oracle Warehouse Management

- Targets (data sinks):
  - `flext-target-oracle/` - Oracle Database
  - `flext-target-ldap/` - LDAP Directory
  - `flext-target-ldif/` - LDIF File Format
  - `flext-target-oracle-oic/` - Oracle Integration Cloud
  - `flext-target-oracle-wms/` - Oracle Warehouse Management

**Meltano (Orchestration):**
- Framework: `meltano @ git+https://github.com/flext-sh/meltano.git@flext/relax-deps`
- Purpose: Pipeline orchestration, scheduling, CLI
- Integration: `flext-meltano/src/flext_meltano/`
- Custom setup: `gruponos-meltano-native/` (custom Meltano implementation)
- Docker compose: `docker/docker-compose.meltano-test.yml`

**dbt (Transformations):**
- Framework: `dbt-core @ git+https://github.com/flext-sh/dbt-core.git@flext/relax-deps#subdirectory=core`
- Adapters:
  - `dbt-adapters @ git+https://github.com/flext-sh/dbt-adapters.git@flext/relax-deps#subdirectory=dbt-adapters`
  - `dbt-common @ git+https://github.com/flext-sh/dbt-common.git@flext/relax-deps`
- Custom implementations:
  - `flext-dbt-oracle/` - Oracle adapter
  - `flext-dbt-ldap/` - LDAP adapter
  - `flext-dbt-ldif/` - LDIF adapter
  - `flext-dbt-oracle-wms/` - Oracle WMS adapter
- Purpose: SQL transformations and analytics engineering

**Workflow:**
1. Taps extract data from sources (Singer protocol)
2. Meltano orchestrates pipeline execution
3. dbt transforms raw data into analytical datasets
4. Targets load data to destinations

## RPC & Microservices

**gRPC:**
- Framework: `grpcio>=1.76,<2`, `grpcio-tools>=1.75.1`
- Serialization: Protocol Buffers (`protobuf>=6.33.5`)
- Implementation: `flext-grpc/src/flext_grpc/`
- Metrics integration: Prometheus instrumentation available
- Status: Production-ready with monitoring

**Service Discovery:**
- Status: Not detected (no Consul, Eureka, etc.)
- Approach: Direct service addressing

## Vendor Lock-in & Custom Forks

**Git Submodules/Forks:**
- All three major tools use custom forked versions:
  - Meltano: `github.com/flext-sh/meltano.git@flext/relax-deps`
  - dbt-core: `github.com/flext-sh/dbt-core.git@flext/relax-deps`
  - dbt-adapters: `github.com/flext-sh/dbt-adapters.git@flext/relax-deps`
  - dbt-common: `github.com/flext-sh/dbt-common.git@flext/relax-deps`
- Purpose: Custom dependency relaxation and FLEXT-specific customizations
- Management: Git references with `flext/relax-deps` branch

---

*Integration audit: 2026-03-23*
