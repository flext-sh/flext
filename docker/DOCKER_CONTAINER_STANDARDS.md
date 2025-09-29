# FLEXT Docker Container Standards

**Version**: 1.0.0 | **Updated**: 2025-09-24

## Container Naming Convention

All FLEXT test containers follow a dual naming pattern:

### Service Name (for compose and directories)

```
{service}
```

### Container Name (when running)

```
flext-{service}-test
```

### Examples

- Service: `openldap` → Container: `flext-openldap-test`
- Service: `postgres` → Container: `flext-postgres-test`
- Service: `redis` → Container: `flext-redis-test`
- Service: `oracle` → Container: `flext-oracle-test`

## Directory Structure Standard

```
docker/
├── docker-compose.{service}.yml    # Compose file (service name)
└── {service}/                      # Container artifacts (service name)
    ├── bootstrap.ldif/            # LDAP bootstrap data (for LDAP)
    │   ├── 00_base_structure.ldif
    │   ├── 01_test_users.ldif
    │   ├── 02_test_groups.ldif
    │   └── 03_service_accounts.ldif
    ├── init/                      # Init scripts (for other services)
    └── config/                    # Configuration files
```

### Key Rules

1. **Artifacts folder**: `docker/{service}/` (simple service name)
2. **Compose file**: `docker/docker-compose.{service}.yml` (simple service name)
3. **Service name in compose**: `{service}` (e.g., `openldap`)
4. **Container name in compose**: `flext-{service}-test` (e.g., `flext-openldap-test`)

## Port Allocation Table

All FLEXT test containers use non-conflicting ports:

| Service   | Container Name       | Ports                                     | Purpose                   |
| --------- | -------------------- | ----------------------------------------- | ------------------------- |
| openldap  | flext-openldap-test  | 3390 (LDAP), 3636 (LDAPS)                 | OpenLDAP directory server |
| postgres  | flext-postgres-test  | 5433                                      | PostgreSQL database       |
| redis     | flext-redis-test     | 6380                                      | Redis cache/queue         |
| oracle-db | flext-oracle-db-test | 1522 (TNS), 2484 (TCPS)                   | Oracle Database XE        |
| client-a-oud | flext-client-a-oud-test | 3389 (LDAP), 3639 (LDAPS), 4449 (Admin)    | Oracle Unified Directory  |
| flext     | flext-test           | 8000                                      | FLEXT Python service      |
| flexcore  | flext-flexcore-test  | 8090 (HTTP), 50051 (gRPC), 9091 (metrics) | FlexCore Go service       |

## OpenLDAP Test Container (Reference Implementation)

### Configuration

- **Service name**: `openldap`
- **Container name**: `flext-openldap-test`
- **Compose file**: `docker/docker-compose.openldap.yml`
- **Artifacts folder**: `docker/openldap/`
- **Image**: `osixia/openldap:1.5.0`
- **Ports**: `3390` (LDAP), `3636` (LDAPS)
- **Domain**: `internal.invalid`
- **Base DN**: `dc=flext,dc=local`
- **Admin credentials**: `cn=REDACTED_LDAP_BIND_PASSWORD,dc=flext,dc=local` / `REDACTED_LDAP_BIND_PASSWORD123`

### Bootstrap Data Structure

```
docker/openldap/bootstrap.ldif/
├── 00_base_structure.ldif      # OUs (people, groups, services, computers)
├── 01_test_users.ldif           # Test user accounts
├── 02_test_groups.ldif          # Test groups
└── 03_service_accounts.ldif     # Service accounts
```

### Volume Configuration (Best Practice)

```yaml
volumes:
  # Named Docker volumes for persistent data (managed by Docker)
  - flext_ldap_data:/var/lib/ldap
  - flext_ldap_config:/etc/ldap/slapd.d

  # Bind mount for files only (read-only)
  - ./openldap/bootstrap.ldif:/container/service/slapd/assets/config/bootstrap/ldif/custom:ro

# Volume definitions
volumes:
  flext_ldap_data:
    driver: local
  flext_ldap_config:
    driver: local
```

**Volume Best Practices:**

- ✅ Use **named Docker volumes** for persistent data (databases, config)
- ✅ Use **bind mounts** only for specific files that need to be accessible from host
- ✅ Always use `:ro` (read-only) for files that should not be modified by container

## FlextTestDocker Integration

### Auto-Start Configuration

FlextTestDocker provides idempotent container management with check-first auto-start:

```python
from flext_tests import FlextTestDocker

docker = FlextTestDocker()

# Idempotent start - checks if running first, only starts if needed
result = docker.start_container("flext-openldap-test")
if result.is_success:
    print("Container ready (already running or started successfully)")
```

### SHARED_CONTAINERS Configuration

```python
SHARED_CONTAINERS: ClassVar[dict[str, dict[str, str | int]]] = {
    "flext-openldap-test": {
        "compose_file": "docker/docker-compose.openldap.yml",
        "service": "openldap",
        "port": 3390,
    },
    # Add more containers following the same pattern...
}
```

**Configuration Keys:**

- **Key name**: Container identifier used in code (`flext-{service}-test`)
- **compose_file**: Path to docker-compose file using service name
- **service**: Service name in docker-compose (simple name like `openldap`)
- **port**: Main port for healthcheck/readiness

````

## Project Integration (flext-ldif, flext-ldap)

### conftest.py Pattern:

```python
import pytest
from flext_tests import FlextTestDocker

@pytest.fixture(scope="session")
def docker_control():
    """Provide Docker control instance for tests."""
    return FlextTestDocker()

@pytest.fixture(scope="session")
def shared_ldap_container(docker_control):
    """Managed LDAP container using FlextTestDocker with auto-start."""
    # Auto-start with check-first behavior
    result = docker_control.start_container("flext-openldap-test")
    if result.is_failure:
        pytest.skip(f"Failed to start LDAP container: {result.error}")

    yield "flext-openldap-test"

    # Keep running for reuse (remove=False)
    docker_control.stop_container("flext-openldap-test", remove=False)
````

## Auto-Start Behavior

### Check-First Logic

1. **Check status**: Query container current state
2. **If RUNNING**: Return success immediately (no action)
3. **If STOPPED**: Start the container
4. **If NOT_FOUND**: Create and start fresh container
5. **Wait for ready**: Poll healthcheck/port availability
6. **Return result**: Success or failure with context

### Benefits

- ✅ **Idempotent**: Safe to call multiple times
- ✅ **Fast**: Skips start if already running
- ✅ **Reliable**: Waits for container readiness
- ✅ **Informative**: Clear error messages and logging

## Container Lifecycle Best Practices

### Development

```bash
# Start container (idempotent)
docker-compose -f docker/docker-compose.flext-openldap-test.yml up -d

# Check status
docker ps | grep flext-openldap-test

# View logs
docker logs flext-openldap-test

# Stop (keep data)
docker-compose -f docker/docker-compose.flext-openldap-test.yml stop

# Reset (remove and recreate)
docker-compose -f docker/docker-compose.flext-openldap-test.yml down
docker-compose -f docker/docker-compose.flext-openldap-test.yml up -d
```

### Testing

```python
# Projects should rely on FlextTestDocker auto-start
# No manual container management needed in tests
```

## Migration Checklist

When adding a new test container:

- [ ] Create folder: `docker/{service}/` (simple service name)
- [ ] Create compose: `docker/docker-compose.{service}.yml` (simple service name)
- [ ] Update service name in compose to `{service}` (e.g., `openldap`)
- [ ] Update container_name in compose to `flext-{service}-test` (e.g., `flext-openldap-test`)
- [ ] Configure named Docker volumes for persistent data
- [ ] Use bind mounts only for specific files (read-only with `:ro`)
- [ ] Add to FlextTestDocker.SHARED_CONTAINERS with correct service name
- [ ] Update project conftest.py to use new container identifier
- [ ] Test auto-start behavior
- [ ] Update documentation

## Standardization Benefits

1. **Consistency**: All containers follow same naming pattern
2. **Discoverability**: Easy to find compose files and artifacts
3. **Automation**: FlextTestDocker can manage all containers uniformly
4. **Maintainability**: Clear structure for new contributors
5. **Reliability**: Idempotent auto-start prevents race conditions
6. **Efficiency**: Containers kept running between test runs

---

**Compliance**: All FLEXT projects MUST follow these standards for test container management.
