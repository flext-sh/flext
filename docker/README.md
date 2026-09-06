# FLEXT Docker Infrastructure - Centralized Management

<!-- TOC START -->

- [Key Features](#key-features)
- [Installation](#installation)
- [Usage](#usage)
  - [For pytest Tests](#for-pytest-tests)
  - Direct tk Usage
- [Architecture](#architecture)
  - [DOCKER COMPOSE FILES (17 CENTRALIZED)](#docker-compose-files-17-centralized)
  - [Container Type Reference (THREE PRIMARY TYPES)](#container-type-reference-three-primary-types)
  - [Infrastructure Services](#infrastructure-services)
  - [Testing Services](#testing-services)
  - [Integration Services](#integration-services)
  - [DOCKERFILES (21 CONSOLIDATED)](#dockerfiles-21-consolidated)
  - [FLEXT Service Images](#flext-service-images)
  - [Project Images](#project-images)
  - [CONTAINER LIFECYCLE MANAGEMENT](#container-lifecycle-management)
  - [Automatic Cleanup](#automatic-cleanup)
  - [Dirty State Management](#dirty-state-management)
  - [Persistent State Location](#persistent-state-location)
  - [MIGRATION FROM OLD PATTERNS](#migration-from-old-patterns)
  - [Old Pattern (DEPRECATED)](#old-pattern-deprecated)
  - [New Pattern (REQUIRED)](#new-pattern-required)
  - [Fixture Migration](#fixture-migration)
  - [PROHIBITED PATTERNS](#prohibited-patterns)
  - [NEVER Create These Files](#never-create-these-files)
  - [Always Use](#always-use)
  - [VALIDATION](#validation)
  - [Verify Docker Standardization](#verify-docker-standardization)
  - [Verify Centralization](#verify-centralization)
  - [FURTHER READING](#further-reading)
- [Contributing](#contributing)
- [License](#license)
<!-- TOC END -->

**Reviewed**: 2026-02-17 | **Version**: 0.10.0-dev

Part of the [FLEXT](https://github.com/flext-sh/flext) ecosystem.

---

## Key Features

```text
~/flext/docker/
├── docker-compose.*.yml    # All compose files (17 centralized configs)
├── images/                  # All Dockerfiles (21 consolidated images)
│   ├── Dockerfile.flext-*       # FLEXT service images
│   ├── Dockerfile.flext-*       # FLEXT project images
│   └── Dockerfile.*             # Other project images
└── README.md               # This file
```

---

## Installation

Ensure you have Docker and Docker Compose installed.

## Usage

### For pytest Tests

All tests MUST use centralized fixtures from `flext_tests.fixtures`:

```python
from flext_tests import (
    flext_docker,  # Main Docker management fixture
    flext_oud_container,  # FLEXT OUD container (port 3389)
    ldap_container,  # Generic OpenLDAP (port 3390)
    oracle_container,  # Oracle Database (port 1522)
    postgres_container,  # PostgreSQL fixture
    redis_container,  # Redis fixture
)


# Example 1: Using Generic OpenLDAP for LDAP/LDIF projects
def test_with_ldap(ldap_container):
    """Test using generic OpenLDAP container (port 3390)."""
    # Container automatically started and managed
    # Cleanup handled automatically after test
    connection_string = ldap_container  # ldap://localhost:3390
    # Use for flext-ldap, flext-ldif, flext-(dbt|tap|target)-(ldap|ldif)


# Example 2: Using FLEXT OUD for FLEXT migration
def test_flext_migration(flext_oud_container):
    """Test using FLEXT OUD container (port 3389)."""
    # FLEXT-specific OpenLDAP with dc=invaliddc, cn=invalid_user
    connection_string = flext_oud_container  # ldap://localhost:3389
    # Use for OUD migration workloads exclusively


# Example 3: Using Oracle Database for Oracle projects
def test_with_oracle(oracle_container):
    """Test using Oracle Database (port 1522)."""
    # Standard Oracle Database
    connection_string = oracle_container  # oracle://flext:password@localhost:1522/FLEXT
    # Use for flext-db-oracle, flext-(dbt|tap|target)-oracle
```

### Direct tk Usage

For scripts and examples:

```python
from flext_tests import tk
from pathlib import Path

# Initialize with workspace root
docker_mgr = tk(workspace_root=Path.home() / "flext")

# Start container
result = docker_mgr.start_container("flext-postgres-test")
if result.is_success:
    u.Cli.print("Container started successfully")

# Get container status
status = docker_mgr.get_container_status("flext-postgres-test")
if status.is_success:
    container_info = status.unwrap()
    u.Cli.print(f"Ports: {container_info.ports}")

# Stop container (or let it persist for next use)
docker_mgr.stop_container("flext-postgres-test")

# Mark container dirty if test failed
if test_failed:
    docker_mgr.mark_container_dirty("flext-postgres-test")
    # Container will be recreated on next run
```

---

## Architecture

### DOCKER COMPOSE FILES (17 CENTRALIZED)

All compose files follow naming convention: `docker-compose.{project}-{purpose}.yml`

### Container Type Reference (THREE PRIMARY TYPES)

**CRITICAL**: FLEXT ecosystem uses THREE distinct container types for different purposes:

1. **Standard Oracle Database** (`flext-oracle-db-test`)
   - **Port**: 1522
   - **Compose File**: `docker-compose.db-oracle.yml`
   - **Purpose**: Standard Oracle Database for flext-db-oracle, flext-(dbt|tap|target)-oracle
   - **Fixture**: `oracle_container` from `flext_tests.fixtures`

2. **FLEXT Oracle Unified Directory** (`flext-flext-oud-test`)
   - **Port**: 3389 (FLEXT production port)
   - **Compose File**: `docker-compose.flext-oud.yml`
   - **Purpose**: FLEXT Telecom OUD migration (OpenLDAP simulating OUD with dc=invaliddc, cn=invalid_user)
   - **Fixture**: `flext_oud_container` from `flext_tests.fixtures`
   - **Projects**: OUD migration workloads

3. **Generic OpenLDAP** (`flext-openldap-test`)
   - **Port**: 3390
   - **Compose File**: `docker-compose.openldap.yml`
   - **Purpose**: Generic LDAP/LDIF testing for flext-(ldap|ldif), flext-(dbt|tap|target)-(ldap|ldif)
   - **Fixture**: `ldap_container` from `flext_tests.fixtures`

### Infrastructure Services

- `docker-compose.flext-auth.yml` - Authentication services
- `docker-compose.flext-web.yml` - Web application services
- `docker-compose.db-oracle.yml` - **Oracle Database** (port 1522)
- `docker-compose.flext-oud.yml` - **FLEXT OUD** (port 3389)
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

# Or let tk manage them automatically
```

---

### DOCKERFILES (21 CONSOLIDATED)

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

- `Dockerfile.flext-oud`, `Dockerfile.flext-oud-mig`
- `Dockerfile.flext`

**Build Example**:

```bash
# Build from centralized location
docker build -f ~/flext/docker/images/Dockerfile.flext-api -t flext-api:latest ~/flext/flext-api/

# Or let tk manage builds automatically
```

---

### CONTAINER LIFECYCLE MANAGEMENT

### Automatic Cleanup

tk handles container lifecycle automatically:

1. **Test Isolation**: Each test gets clean container state
2. **Automatic Cleanup**: Changes reverted after test completion
3. **Dirty Marking**: Containers marked dirty on failure
4. **Recreation**: Dirty containers recreated with clean volumes on next run

### Dirty State Management

Containers that can't be cleaned are marked dirty:

```python
# tk automatically manages dirty state
docker_mgr = tk()

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

### MIGRATION FROM OLD PATTERNS

### Old Pattern (DEPRECATED)

```python
# ❌ OLD - Direct docker-compose in project directory
import docker

client = docker.from_env()
container = client.containers.run("postgres:13", detach=True)
```

### New Pattern (REQUIRED)

```python
# ✅ NEW - Use tk
from flext_tests import tk

docker_mgr = tk()
result = docker_mgr.start_container("flext-postgres-test")
# Automatic cleanup, dirty state management, etc.
```

### Fixture Migration

```python
# ❌ OLD - Local fixture files
from tests import postgres_container

# ✅ NEW - Centralized fixtures
from flext_tests import postgres_container
```

---

### PROHIBITED PATTERNS

### NEVER Create These Files

- ❌ `docker-compose.yml` in project directories (use central location)
- ❌ `Dockerfile` in project directories (use images/ directory)
- ❌ Local `docker_fixtures.py` (use flext_tests.fixtures)
- ❌ Custom Docker scripts (use tk API)

### Always Use

- ✅ `flext_tests.tk` for container management
- ✅ `flext_tests.fixtures` for test fixtures
- ✅ Centralized compose files from `~/flext/docker/`
- ✅ Centralized Dockerfiles from `~/flext/docker/images/`

---

### VALIDATION

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

### FURTHER READING

- **tk API**: See `flext-core/src/flext_tests/docker.py` (1649 lines)
- **Centralized Fixtures**: See `flext-core/src/flext_tests/fixtures/docker_fixtures.py`
- **FLEXT Standards**: See `~/flext/AGENTS.md` for ecosystem standards
- **Project Docs**: See individual project README files for specific usage

---

**AUTHORITY**: This is the ONLY location for Docker artifacts in FLEXT ecosystem.
**ENFORCEMENT**: All projects MUST use tk for container management.
**ZERO DUPLICATION**: No Docker files allowed outside this centralized location.

---

**Last Updated**: 2025-09-30
**Maintained By**: FLEXT Core Team

## Contributing

Please see our Contributing Guide for details.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
