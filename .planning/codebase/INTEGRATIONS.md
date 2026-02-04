# External Integrations

**Analysis Date:** 2026-01-31

## APIs & External Services

**GraphQL:**
- **gql** >=4.0.0 (flext-api)
  - GraphQL query execution
  - Integration with FastAPI
  - Location: `flext-api/src/flext_api/`

**WebSocket:**
- **websockets** >=15.0.1 (flext-api)
  - Real-time bidirectional communication
  - Client and server support
  - Location: `flext-api/src/flext_api/`

**gRPC Services:**
- **google.golang.org/grpc** v1.74.2 (flexcore - Go)
  - RPC service definitions and implementations
  - Location: `flexcore/`

- **flext-grpc** - FLEXT gRPC foundation
  - gRPC protocol implementations
  - Service interfaces

## Data Storage

**Databases:**

**Oracle Database:**
- **oracledb** >=2.0.0 (flext-db-oracle)
  - Oracle DB client driver
  - Connection management
  - Supports: Oracle 12c+, 21c, 23c
  - Location: `flext-db-oracle/src/flext_db_oracle/clients.py`
  - Connection: `OracleDB_HOST`, `OracleDB_PORT`, `OracleDB_USER`, `OracleDB_PASSWORD`
  - Client: SQLAlchemy 2.0 ORM + oracledb dialect

**PostgreSQL:**
- **psycopg** ^3.2.9 (flexcore - Go via GORM)
- **psycopg2** types (flext-db-oracle - optional dependencies)
  - PostgreSQL client driver
  - Supports: PostgreSQL 12+
  - Location: Used in flexcore via GORM
  - Connection: Standard PostgreSQL connection string
  - Client: GORM ORM in Go

**SQLite:**
- Via SQLAlchemy 2.0 (flext-db-oracle)
  - File-based embedded database
  - No external service
  - Location: Local filesystem

**File Storage:**
- **Local filesystem only** - No cloud storage integration
  - Data files stored locally
  - Docker volumes for container persistence

**Caching:**
- **Redis** (optional, flexcore)
  - **go-redis/redis/v8** v8.11.5 (Go client)
  - Key-value cache
  - Session storage
  - Message queue potential
  - Location: `flexcore/` (Go layer)
  - Connection: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
  - No Python Redis client in current stack

## Authentication & Identity

**Auth Provider:**
- **Custom** - FLEXT auth foundation
  - flext-auth project implements custom authentication
  - Support for LDAP authentication via flext-ldap integration
  - Location: `flext-auth/src/flext_auth/`

**LDAP/Directory Services:**
- **ldap3** >=3.4.4 (flext-ldap)
  - LDAP protocol implementation
  - Server-specific backends: OpenLDAP, Oracle OID/OUD
  - Connection binding and authentication
  - Directory entry search and modification
  - Location: `flext-ldap/src/flext_ldap/adapters/ldap3.py`
  - Connection: `LDAP_HOST`, `LDAP_PORT`, `LDAP_BIND_DN`, `LDAP_BIND_PASSWORD`

**Directory Implementations:**
- **OpenLDAP** 1.x/2.x compatibility
  - Server: OpenLDAP (testable via docker-compose.openldap.yml)
  - Location: `flext-ldap/src/flext_ldap/servers/openldap.py`

- **Oracle OID** (Oracle Internet Directory)
  - Server: Oracle OID
  - Location: `flext-ldap/src/flext_ldap/servers/oracle_oid.py`

- **Oracle OUD** (Oracle Unified Directory)
  - Server: Oracle Unified Directory
  - Location: `flext-ldap/src/flext_ldap/servers/oracle_oud.py`

## Monitoring & Observability

**Error Tracking:**
- **None** - Currently relies on FlextResult and structured logging
- Could integrate Sentry, DataDog, or similar via OpenTelemetry

**Logs:**
- **structlog** >=25.4.0
  - Structured JSON logging
  - Context management
  - Output to stdout/stderr
  - Location: `flext-core/src/flext_core/loggings.py`

**Tracing & Metrics:**
- **OpenTelemetry** (flext-observability)
  - **opentelemetry-api** >=1.39.1 - Trace and metric collection APIs
  - **opentelemetry-sdk** >=1.39.1 - Reference implementation
  - **opentelemetry-exporter-otlp-proto-grpc** >=1.39.1 - OTLP exporter
    - Sends traces to OpenTelemetry Collector
    - Protocol: gRPC with Protocol Buffers
    - Endpoint: Configurable via environment (typically `http://localhost:4317`)
  - Location: `flext-observability/src/flext_observability/`

**Metrics/Prometheus:**
- **prometheus-client** >=0.23.0
  - Prometheus metrics exposure
  - Supports: Counter, Gauge, Histogram, Summary
  - Endpoint: `/metrics` on Prometheus port
  - **opentelemetry-exporter-prometheus** >=0.60b1
    - Converts OpenTelemetry metrics to Prometheus format
    - Scrape endpoint typically `:8000/metrics`

## CI/CD & Deployment

**Hosting:**
- **Docker containers** (Primary)
  - Image base: Python 3.13 official images
  - Orchestration: Docker Compose (for testing)
  - Location: `docker/docker-compose.*.yml` files
  - Deployment platforms: Kubernetes, Docker Swarm, bare Docker

**CI Pipeline:**
- **GitHub Actions** (inferred from `.github/` directory)
  - **Dependabot** for dependency updates
  - Configuration: `.github/dependabot.yml`
  - Likely checks: lint, type-check, tests, security scan

**Container Images:**
- **Testing Infrastructure** (via docker-compose):
  - postgres:16 - PostgreSQL test database
  - oracle-express:21c - Oracle test database
  - osixia/openldap:1.5.0 - OpenLDAP test server
  - redis:latest - Redis test cache
  - milvus - Vector database (for potential embeddings)

## Environment Configuration

**Required env vars (Core):**
- `FLEXT_ENV` - Environment (development, test, production)
- `FLEXT_DEBUG` - Debug mode (true/false)
- `PYTHONPATH` - Python module path (typically `/app/src`)
- `PYTHONDONTWRITEBYTECODE` - Don't write .pyc (true/false)
- `PYTHONUNBUFFERED` - Unbuffered output (true/false)

**Required env vars (Database):**
- `OracleDB_HOST` - Oracle hostname
- `OracleDB_PORT` - Oracle port (default: 1521)
- `OracleDB_USER` - Oracle username
- `OracleDB_PASSWORD` - Oracle password
- `OracleDB_SID` / `OracleDB_SERVICE_NAME` - Database identifier

- `POSTGRES_HOST` - PostgreSQL hostname
- `POSTGRES_PORT` - PostgreSQL port (default: 5432)
- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password
- `POSTGRES_DB` - Database name

**Required env vars (LDAP):**
- `LDAP_HOST` - LDAP server hostname
- `LDAP_PORT` - LDAP port (default: 389 for plain, 636 for SSL)
- `LDAP_BIND_DN` - DN to bind as (e.g., `cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com`)
- `LDAP_BIND_PASSWORD` - Bind password
- `LDAP_BASE_DN` - Base DN for searches (e.g., `dc=example,dc=com`)
- `LDAP_USE_SSL` - Use SSL/TLS (true/false)

**Required env vars (Observability):**
- `OTEL_EXPORTER_OTLP_ENDPOINT` - OpenTelemetry Collector endpoint (e.g., `http://localhost:4317`)
- `OTEL_EXPORTER_OTLP_PROTOCOL` - OTLP protocol (grpc, http/protobuf)
- `PROMETHEUS_PORT` - Metrics exposition port (default: 8000)

**Required env vars (Redis):**
- `REDIS_HOST` - Redis hostname
- `REDIS_PORT` - Redis port (default: 6379)
- `REDIS_PASSWORD` - Redis password (optional)
- `REDIS_DB` - Redis database number (default: 0)

**Secrets location:**
- Environment variables (primary)
- `.env` file in development (via python-dotenv)
- Docker secrets (in Swarm/Kubernetes)
- HashiCorp Vault (potential)
- No hardcoded secrets in source code

## Webhooks & Callbacks

**Incoming:**
- FastAPI endpoints in `flext-api` can handle webhooks
- POST endpoints for data ingestion
- No built-in webhook consumer documented

**Outgoing:**
- Singer tap/target protocol communicates via stdin/stdout
  - Projects: `flext-tap-*`, `flext-target-*`
- dbt communication via Meltano
  - Projects: `flext-dbt-*`
- gRPC service calls (flext-grpc, flexcore)
  - Projects: `flext-grpc/`, `flexcore/`

## Data Integration Framework

**Meltano Integration:**
- **flext-meltano** - Meltano orchestration foundation
- Coordinates Singer taps and targets
- Runs dbt transformations
- Location: `flext-meltano/`

**Singer Protocol (Tap/Target):**
- **Taps** (Data extractors):
  - `flext-tap-ldap` - Extract LDAP entries
  - `flext-tap-ldif` - Extract LDIF entries
  - `flext-tap-oracle` - Extract from Oracle DB
  - `flext-tap-oracle-wms` - Extract from Oracle WMS
  - `flext-tap-oracle-oic` - Extract from Oracle OIC
  - Protocol: stdin/stdout with JSON-serialized messages
  - Types: SCHEMA, RECORD, STATE

- **Targets** (Data loaders):
  - `flext-target-ldap` - Load to LDAP
  - `flext-target-ldif` - Load to LDIF files
  - `flext-target-oracle` - Load to Oracle DB
  - `flext-target-oracle-wms` - Load to Oracle WMS
  - `flext-target-oracle-oic` - Load to Oracle OIC
  - Protocol: stdin/stdout with JSON-serialized messages
  - Types: SCHEMA, RECORD, STATE

**dbt Transformations:**
- **Data Build Tool** for SQL transformations
- Projects:
  - `flext-dbt-ldif` - LDIF data transformations
  - `flext-dbt-ldap` - LDAP data transformations
  - `flext-dbt-oracle` - Oracle data transformations
  - `flext-dbt-oracle-wms` - Oracle WMS transformations
- Output: SQL models, tests, documentation

## Plugin System

**flext-plugin:**
- Go-based plugin system
- HashiCorp go-plugin v1.6.3
- RPC-based plugin communication
- Location: `flext-plugin/`

## Quality & Testing Infrastructure

**flext-quality:**
- Quality assurance utilities
- Code metrics and linting helpers
- Location: `flext-quality/`

**flext-observability:**
- Comprehensive observability foundation
- OpenTelemetry integration
- Prometheus metrics
- Location: `flext-observability/src/flext_observability/`

---

*Integration audit: 2026-01-31*
