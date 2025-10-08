# FLEXT Docker Infrastructure - Centralized Management

**Version**: 1.0.0 | **Updated**: 2025-09-30
**Authority**: FLEXT Ecosystem Docker Standardization

---

## 🎯 PURPOSE

This directory contains ALL Docker artifacts for the FLEXT ecosystem in a centralized location. This eliminates duplicate Docker configurations and ensures consistent container management across all projects.

**Core Principle**: All Docker operations go through `FlextTestDocker` from `flext_tests` library.

---

## 📁 DIRECTORY STRUCTURE

```
~/flext/docker/
├── docker-compose.*.yml    # All compose files (17 centralized configs)
├── images/                  # All Dockerfiles (21 consolidated images)
│   ├── Dockerfile.flext-*       # FLEXT service images
│   ├── Dockerfile.client-a-*       # client-a project images
│   └── Dockerfile.*             # Other project images
└── README.md               # This file
```

---

## 🚀 USAGE

### For pytest Tests

All tests MUST use centralized fixtures from `flext_tests.fixtures`:

```python
from flext_tests.fixtures import (
    flext_docker,          # Main Docker management fixture
    client-a_oud_container,   # client-a OUD container (port 3389)
    ldap_container,        # Generic OpenLDAP (port 3390)
    oracle_container,      # Oracle Database (port 1522)
    postgres_container,    # PostgreSQL fixture
    redis_container,       # Redis fixture
)

# Example 1: Using Generic OpenLDAP for LDAP/LDIF projects
def test_with_ldap(ldap_container):
    \"\"\"Test using generic OpenLDAP container (port 3390).\"\"\"
    # Container automatically started and managed
    # Cleanup handled automatically after test
    connection_string = ldap_container  # ldap://localhost:3390
    # Use for flext-ldap, flext-ldif, flext-(dbt|tap|target)-(ldap|ldif)

# Example 2: Using client-a OUD for client-a migration
def test_client-a_migration(client-a_oud_container):
    \"\"\"Test using client-a OUD container (port 3389).\"\"\"
    # client-a-specific OpenLDAP with dc=invaliddc, cn=invalid_user
    connection_string = client-a_oud_container  # ldap://localhost:3389
    # Use for client-a-oud-mig project exclusively

# Example 3: Using Oracle Database for Oracle projects
def test_with_oracle(oracle_container):
    \"\"\"Test using Oracle Database (port 1522).\"\"\"
    # Standard Oracle Database
    connection_string = oracle_container  # oracle://flext:password@localhost:1522/FLEXT
    # Use for flext-db-oracle, flext-(dbt|tap|target)-oracle
```

### Direct FlextTestDocker Usage

For scripts and examples:

```python
from flext_tests import FlextTestDocker
from pathlib import Path

# Initialize with workspace root
docker_mgr = FlextTestDocker(workspace_root=Path.home() / "flext")

# Start container
result = docker_mgr.start_container("flext-postgres-test")
if result.is_success:
    print("Container started successfully")

# Get container status
status = docker_mgr.get_container_status("flext-postgres-test")
if status.is_success:
    container_info = status.unwrap()
    print(f"Ports: {container_info.ports}")

# Stop container (or let it persist for next use)
docker_mgr.stop_container("flext-postgres-test")

# Mark container dirty if test failed
if test_failed:
    docker_mgr.mark_container_dirty("flext-postgres-test")
    # Container will be recreated on next run
```

---

## 🏗️ DOCKER COMPOSE FILES (17 CENTRALIZED)

All compose files follow naming convention: `docker-compose.{project}-{purpose}.yml`

### Container Type Reference (THREE PRIMARY TYPES)

**CRITICAL**: FLEXT ecosystem uses THREE distinct container types for different purposes:

1. **Standard Oracle Database** (`flext-oracle-db-test`)
   - **Port**: 1522
   - **Compose File**: `docker-compose.db-oracle.yml`
   - **Purpose**: Standard Oracle Database for flext-db-oracle, flext-(dbt|tap|target)-oracle
   - **Fixture**: `oracle_container` from `flext_tests.fixtures`

2. **client-a Oracle Unified Directory** (`flext-client-a-oud-test`)
   - **Port**: 3389 (client-a production port)
   - **Compose File**: `docker-compose.client-a-oud.yml`
   - **Purpose**: client-a Telecom OUD migration (OpenLDAP simulating OUD with dc=invaliddc, cn=invalid_user)
   - **Fixture**: `client-a_oud_container` from `flext_tests.fixtures`
   - **Projects**: client-a-oud-mig

3. **Generic OpenLDAP** (`flext-openldap-test`)
   - **Port**: 3390
   - **Compose File**: `docker-compose.openldap.yml`
   - **Purpose**: Generic LDAP/LDIF testing for flext-(ldap|ldif), flext-(dbt|tap|target)-(ldap|ldif)
   - **Fixture**: `ldap_container` from `flext_tests.fixtures`

### Infrastructure Services

- `docker-compose.flext-auth.yml` - Authentication services
- `docker-compose.flext-web.yml` - Web application services
- `docker-compose.db-oracle.yml` - **Oracle Database** (port 1522)
- `docker-compose.client-a-oud.yml` - **client-a OUD** (port 3389)
- `docker-compose.openldap.yml` - **Generic OpenLDAP** (port 3390)
- `docker-compose.ldap-flext.yml` - FLEXT LDAP server
- `docker-compose.ldap-oracle-db.yml` - LDAP + Oracle integration

### Testing Services

- `docker-compose.tap-oracle-test.yml` - Oracle tap testing
- `docker-compose.meltano-test.yml` - Meltano integration tests
- `docker-compose.oracle-wms.yml` - Oracle WMS testing

### Integration Services

- Additional compose files for various integration scenarios

**Usage**:

```bash
# From any project directory, reference central compose files
docker-compose -f ~/flext/docker/docker-compose.db-oracle.yml up -d

# Or let FlextTestDocker manage them automatically
```

---

## 🐳 DOCKERFILES (21 CONSOLIDATED)

All Dockerfiles are consolidated in `images/` directory with descriptive names:

### FLEXT Service Images

- `Dockerfile.flext-auth` (+ simple, test variants)
- `Dockerfile.flext-web` (+ simple variant)
- `Dockerfile.flext-api`
- `Dockerfile.flext-grpc`
- `Dockerfile.flext-observability`
- `Dockerfile.flext-quality` (+ fixed, simple, enterprise, standalone variants)
- `Dockerfile.flext-oracle-wms`
- `Dockerfile.flext-tap-oracle` (+ test variant)
- `Dockerfile.flext-meltano-test`

### Project Images

- `Dockerfile.client-a-oud`, `Dockerfile.client-a-oud-mig`
- `Dockerfile.flext`, `Dockerfile.flexcore`

**Build Example**:

```bash
# Build from centralized location
docker build -f ~/flext/docker/images/Dockerfile.flext-api -t flext-api:latest ~/flext/flext-api/

# Or let FlextTestDocker manage builds automatically
```

---

## 🧹 CONTAINER LIFECYCLE MANAGEMENT

### Automatic Cleanup

FlextTestDocker handles container lifecycle automatically:

1. **Test Isolation**: Each test gets clean container state
2. **Automatic Cleanup**: Changes reverted after test completion
3. **Dirty Marking**: Containers marked dirty on failure
4. **Recreation**: Dirty containers recreated with clean volumes on next run

### Dirty State Management

Containers that can't be cleaned are marked dirty:

```python
# FlextTestDocker automatically manages dirty state
docker_mgr = FlextTestDocker()

# If test fails and container is compromised
docker_mgr.mark_container_dirty("flext-postgres-test")

# On next run, dirty container is automatically:
# 1. Stopped
# 2. Removed with volumes
# 3. Recreated from scratch
```

### Persistent State Location

Dirty state tracked in: `~/.flext/docker_state.json`

---

## 🔧 MIGRATION FROM OLD PATTERNS

### Old Pattern (DEPRECATED)

```python
# ❌ OLD - Direct docker-compose in project directory
import docker
client = docker.from_env()
container = client.containers.run("postgres:13", detach=True)
```

### New Pattern (REQUIRED)

```python
# ✅ NEW - Use FlextTestDocker
from flext_tests import FlextTestDocker

docker_mgr = FlextTestDocker()
result = docker_mgr.start_container("flext-postgres-test")
# Automatic cleanup, dirty state management, etc.
```

### Fixture Migration

```python
# ❌ OLD - Local fixture files
from tests.fixtures.docker_fixtures import postgres_container

# ✅ NEW - Centralized fixtures
from flext_tests.fixtures import postgres_container
```

---

## 🚨 PROHIBITED PATTERNS

### NEVER Create These Files

- ❌ `docker-compose.yml` in project directories (use central location)
- ❌ `Dockerfile` in project directories (use images/ directory)
- ❌ Local `docker_fixtures.py` (use flext_tests.fixtures)
- ❌ Custom Docker scripts (use FlextTestDocker API)

### Always Use

- ✅ `flext_tests.FlextTestDocker` for container management
- ✅ `flext_tests.fixtures` for test fixtures
- ✅ Centralized compose files from `~/flext/docker/`
- ✅ Centralized Dockerfiles from `~/flext/docker/images/`

---

## 📊 VALIDATION

### Verify Docker Standardization

```bash
# Check for prohibited duplicate files
find ~/flext -name "docker-compose.yml" -o -name "docker-compose.*.yml" | grep -v "~/flext/docker/"
# Should return nothing

# Check for prohibited local Dockerfiles
find ~/flext -name "Dockerfile*" -type f | grep -v "~/flext/docker/images/" | grep -v ".bak"
# Should return nothing

# Check for prohibited local fixtures
find ~/flext -name "docker_fixtures.py" | grep -v "flext-core/src/flext_tests/fixtures/" | grep -v ".bak"
# Should return nothing
```

### Verify Centralization

```bash
# Count centralized compose files
ls ~/flext/docker/docker-compose.*.yml | wc -l
# Should be 17

# Count centralized Dockerfiles
ls ~/flext/docker/images/Dockerfile.* | wc -l
# Should be 21
```

---

## 📖 FURTHER READING

- **FlextTestDocker API**: See `flext-core/src/flext_tests/docker.py` (1649 lines)
- **Centralized Fixtures**: See `flext-core/src/flext_tests/fixtures/docker_fixtures.py`
- **FLEXT Standards**: See `~/flext/CLAUDE.md` for ecosystem standards
- **Project Docs**: See individual project README files for specific usage

---

**AUTHORITY**: This is the ONLY location for Docker artifacts in FLEXT ecosystem.
**ENFORCEMENT**: All projects MUST use FlextTestDocker for container management.
**ZERO DUPLICATION**: No Docker files allowed outside this centralized location.

---

**Last Updated**: 2025-09-30
**Maintained By**: FLEXT Core Team
