# FLEXT Projects Documentation

## Overview

Individual documentation for all 30 projects in the FLEXT ecosystem.

## Navigation

- [← Back to Main Index](../index.md)
- [Architecture Overview](../architecture/README.md)
- [API Reference](../api-reference/README.md)
- [Standards](../standards/README.md)

## Core Foundation (4 projects)

### [flext-core](./flext-core.md)

**Purpose**: Foundation library with patterns, abstractions, type system  
**Version**: 0.10.0  
**Status**: ✅ Production ready  
**Documentation**: ✅ Complete (38 files)

### [flext-cli](./flext-cli.md)

**Purpose**: CLI framework (Click/Rich abstraction)  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-api](./flext-api.md)

**Purpose**: HTTP framework with FastAPI integration  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flexcore](./flexcore.md)

**Purpose**: Go implementation of FLEXT core patterns  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

## LDAP/Directory Services (3 projects)

### [flext-ldap](./flext-ldap.md)

**Purpose**: LDAP operations and directory services  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-ldif](./flext-ldif.md)

**Purpose**: LDIF processing with RFC compliance  
**Version**: 0.9.0  
**Status**: ✅ Production ready  
**Documentation**: ✅ Complete

### [flext-auth](./flext-auth.md)

**Purpose**: Authentication and authorization services  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

## Infrastructure (4 projects)

### [flext-db-oracle](./flext-db-oracle.md)

**Purpose**: Oracle database connectivity  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-grpc](./flext-grpc.md)

**Purpose**: gRPC communication framework  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-observability](./flext-observability.md)

**Purpose**: Monitoring and observability services  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-web](./flext-web.md)

**Purpose**: Web application framework  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

## Data Integration (3 projects)

### [flext-meltano](./flext-meltano.md)

**Purpose**: Singer/Meltano integration for data orchestration  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-plugin](./flext-plugin.md)

**Purpose**: Plugin system and discovery mechanism  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-quality](./flext-quality.md)

**Purpose**: Code quality tools and static analysis  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

## Singer Ecosystem - Taps (5 projects)

### [flext-tap-ldap](./flext-tap-ldap.md)

**Purpose**: LDAP tap for Singer protocol  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-tap-ldif](./flext-tap-ldif.md)

**Purpose**: LDIF tap for Singer protocol  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-tap-oracle](./flext-tap-oracle.md)

**Purpose**: Oracle tap for Singer protocol  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-tap-oracle-wms](./flext-tap-oracle-wms.md)

**Purpose**: Oracle WMS tap for Singer protocol  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-tap-oracle-oic](./flext-tap-oracle-oic.md)

**Purpose**: Oracle OIC tap for Singer protocol  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

## Singer Ecosystem - Targets (5 projects)

### [flext-target-ldap](./flext-target-ldap.md)

**Purpose**: LDAP target for Singer protocol  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-target-ldif](./flext-target-ldif.md)

**Purpose**: LDIF target for Singer protocol  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-target-oracle](./flext-target-oracle.md)

**Purpose**: Oracle target for Singer protocol  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-target-oracle-wms](./flext-target-oracle-wms.md)

**Purpose**: Oracle WMS target for Singer protocol  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-target-oracle-oic](./flext-target-oracle-oic.md)

**Purpose**: Oracle OIC target for Singer protocol  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

## DBT Adapters (4 projects)

### [flext-dbt-ldap](./flext-dbt-ldap.md)

**Purpose**: LDAP transformations for DBT  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-dbt-ldif](./flext-dbt-ldif.md)

**Purpose**: LDIF transformations for DBT  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-dbt-oracle](./flext-dbt-oracle.md)

**Purpose**: Oracle transformations for DBT  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-dbt-oracle-wms](./flext-dbt-oracle-wms.md)

**Purpose**: Oracle WMS transformations for DBT  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

## Enterprise Integration (2 projects)

### [flext-oracle-wms](./flext-oracle-wms.md)

**Purpose**: Oracle Warehouse Management integration  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

### [flext-oracle-oic](./flext-oracle-oic.md)

**Purpose**: Oracle Integration Cloud integration  
**Version**: -  
**Status**: ✅ Production ready  
**Documentation**: ⏳ In progress

## Integration Guidelines

### Project Dependencies

```
flext-core (foundation)
├── flext-ldif (domain)
├── flext-ldap (domain)
├── flext-oracle (infrastructure)
├── flext-api (infrastructure)
└── flext-auth (infrastructure)
```

### Development Workflow

1. **Core Development**: Changes to flext-core require updates across all projects
2. **Domain Libraries**: Can be developed independently but must maintain API compatibility
3. **Infrastructure Libraries**: Depend on domain libraries for business logic
4. **Testing**: All projects must maintain 100% test coverage

### Release Process

- **Semantic Versioning**: All projects follow semver conventions
- **Changelog Management**: Automated changelog generation from commit messages
- **Dependency Updates**: Coordinated updates across the ecosystem
- **Documentation Updates**: Automatic API documentation generation

## Getting Started with Projects

### Using flext-core

```python
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

# Set up dependency injection
container = FlextContainer()

# Use railway-oriented programming
result = some_operation()
if result.is_success:
    data = result.unwrap()
else:
    error = result.failure()
```

### Using flext-ldif

```python
from flext_ldif import FlextLdif

ldif = FlextLdif()

# Parse LDIF content
result = ldif.parse("dn: cn=test,dc=example,dc=com\ncn: test\n")
if result.is_success:
    entries = result.unwrap()

# Migrate between servers
migration_result = ldif.migrate(
    input_dir=Path("data/input"),
    output_dir=Path("data/output"),
    from_server="oid",
    to_server="oud"
)
```

## Project Standards

- **Single Responsibility**: Each project has a clear, focused purpose
- **API Consistency**: All projects expose similar facade patterns
- **Documentation**: Comprehensive README and API documentation for each project
- **Testing**: Full test coverage with integration and E2E tests
- **CI/CD**: Automated testing and deployment pipelines

## Contributing to Projects

Each project maintains its own:

- Issue tracker for bug reports and feature requests
- Development guidelines and contribution processes
- Release schedule and versioning strategy
- Documentation updates and maintenance

See each project's individual documentation for specific contribution guidelines.
