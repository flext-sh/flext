# FLEXT Core API Reference

**Complete reference for FLEXT Core foundation patterns**

This document provides accurate API documentation for FLEXT Core v0.9.0, based on the actual implementation in `src/flext_core/__init__.py`.

## 🎯 Essential Imports

### Core Patterns (Most Common)

```python
from flext_core import (
    # Railway-oriented programming
    FlextResult,

    # Dependency injection
    FlextContainer,       # Dependency injection container

    # Domain modeling
    FlextModels,          # Domain models namespace

    # Configuration
    FlextConfig,          # Environment-aware config

    # Constants and utilities
    FlextConstants,       # System constants
    FlextUtilities,       # Utility functions

    # Logging
    FlextLogger,          # Structured logging
)
```

### Additional Patterns

```python
from flext_core import (
    # Commands and handlers (CQRS)
    FlextBus,
    FlextHandlers,
    FlextProcessors,

    # Utilities
    FlextUtilities,

    # Logging
    FlextLogger,
)

# Domain-specific imports (use instead of direct third-party imports)
from flext_cli import FlextCli, FlextCliCommands  # For Rich/Click/Typer functionality
from flext_web import FlextWebServer             # For FastAPI/Flask/Django
from flext_api import FlextApiClient             # For requests/httpx
from flext_quality import FlextQualityAnalyzer   # For MyPy/pytest/coverage
from flext_grpc import FlextGrpcServer           # For gRPC/grpcio
from flext_plugin import FlextPluginManager      # For plugin management
from flext_tools import FlextToolsManager        # For development tooling
from flext_observability import FlextMetrics     # For Prometheus/Redis monitoring
from flext_auth import FlextAuthService          # For authentication
```

## 🚂 FlextResult[T] - Railway-Oriented Programming

Type-safe error handling without exceptions.

### Basic Usage

```python
from flext_core import FlextResult

def divide(a: int, b: int) -> FlextResult[float]:
    if b == 0:
        return FlextResult[None].fail("Division by zero")
    return FlextResult[None].ok(a / b)

# Chain operations safely
result = (
    divide(10, 2)
    .map(lambda x: x * 2)        # Transform success value
    .flat_map(lambda x: divide(x, 3))  # Chain another operation
)

if result.is_success:
    print(f"Result: {result.value}")
else:
    print(f"Error: {result.error}")
```

### Key Methods

- `FlextResult[None].ok(value)` - Create success result
- `FlextResult[None].fail(error)` - Create failure result
- `.map(func)` - Transform success value
- `.flat_map(func)` - Chain operations returning FlextResult
- `.is_success` - Boolean indicating success
- `.is_failure` - Boolean indicating failure
- `.value` - Success value (when is_success=True)
- `.unwrap()` - Get value or raise exception
- `.error` - Error message (when is_failure=True)

## 📦 FlextContainer - Dependency Injection

Dependency injection with type safety.

### Basic Usage

```python
from flext_core import FlextContainer

# Use global container
container = FlextContainer.get_global()

# Register services
result = container.register("user_service", UserService())
assert result.is_success

# Retrieve services
service_result = container.get("user_service")
if service_result.is_success:
    user_service = service_result.value
```

### Key Methods

- `container.register(name, instance)` - Register service instance
- `container.register_factory(name, factory)` - Register service factory
- `container.get(name)` - Retrieve service (returns FlextResult)
- `container.get_typed(name, expected_type)` - Get service with type checking
- `container.has(name)` - Check if service exists
- `container.list_services()` - List all services with their types
- `container.get_service_count()` - Get total service count
- `container.clear()` - Clear all services
- `FlextContainer.get_global()` - Get global container instance
- `FlextContainer.configure_global(container)` - Configure global container

## 🏛️ Domain Modeling

### FlextModels.Entity - Rich Domain Entities

```python
from flext_core import FlextModels

class User(FlextModels.Entity):
    name: str
    email: str
    is_active: bool = False

    def activate(self) -> FlextResult[None]:
        if self.is_active:
            return FlextResult[None].fail("User already active")

        self.is_active = True
        # Domain events can be added here
        self.add_domain_event(
            FlextModels.Event(
                event_type="user_activated",
                aggregate_id=self.id,
                payload={"user_id": self.id}
            )
        )
        return FlextResult[None].ok(None)
```

### FlextModels.Value - Immutable Values

```python
from flext_core import FlextModels

class Email(FlextModels.Value):
    address: str

    @field_validator('address')
    @classmethod
    def validate_address(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v
```

### FlextModels.AggregateRoot - DDD Aggregates

```python
from flext_core import FlextModels

class Order(FlextModels.AggregateRoot):
    customer_id: str
    items: list = Field(default_factory=list)
    total: float = Field(default=0.0)

    def add_item(self, item) -> FlextResult[None]:
        self.items.append(item)
        self.total += item.price

        # Add domain event using apply_domain_event
        event = FlextModels.Event(
            event_type="item_added_to_order",
            aggregate_id=self.id,
            payload={"item_id": item.id, "new_total": self.total}
        )
        self.apply_domain_event(event)

        return FlextResult[None].ok(None)
```

## ⚙️ Configuration Management

### FlextConfig - Environment-Aware Config

```python
from flext_core import FlextConfig
from pydantic import Field

class AppSettings(FlextConfig):
    database_url: str = Field(default="postgresql://localhost/app")
    log_level: str = Field(default="INFO")
    debug: bool = Field(default=False)

    model_config = ConfigDict(env_prefix="APP_")

# Usage
settings = AppSettings()  # Reads from environment variables
print(settings.database_url)  # Uses APP_DATABASE_URL if set

# Create from constants
config_result = FlextConfig.create(constants={"log_level": "DEBUG"})
if config_result.is_success:
    config = config_result.value
```

## 📝 Structured Logging

### FlextLogger Usage

```python
from flext_core import FlextLogger

logger = FlextLogger(__name__)

# Structured logging with context
logger.info("Processing request",
    user_id="123",
    operation="user_update",
    duration_ms=45)

# Error logging with FlextResult
result = some_operation()
if result.is_failure:
    logger.error("Operation failed",
        error=result.error,
        operation="some_operation")

# Use with context
with logger.context(operation="user_processing"):
    logger.info("Starting user processing")
    # All logs in this block will include operation context

# Note: FlextLogger handles structured logging internally
# For external logging integrations, use flext-observability domain
```

## 🧪 Testing Patterns

### Using FlextResult in Tests

```python
import pytest
from flext_core import FlextResult

def test_user_activation():
    user = User(name="John", email="john@test.com")

    result = user.activate()

    assert result.is_success
    assert user.is_active

def test_user_double_activation():
    user = User(name="John", email="john@test.com", is_active=True)

    result = user.activate()

    assert result.is_failure
    assert "already active" in result.error
```

### Container Testing

```python
def test_service_registration():
    container = FlextContainer()
    service = UserService()

    result = container.register("user_service", service)

    assert result.is_success

    retrieved = container.get("user_service")
    assert retrieved.is_success
    assert retrieved.value is service
```

## 🏷️ Value Objects and Validation

### Built-in Value Objects

```python
from flext_core import FlextModels

# Email addresses with validation
email_result = FlextModels.EmailAddress.create("user@example.com")
if email_result.is_success:
    email = email_result.value
    print(email.domain())  # "example.com"

# URLs with validation
url_result = FlextModels.Url.create("https://api.example.com")
if url_result.is_success:
    url = url_result.value
    print(url.get_hostname())  # "api.example.com"

# Entity IDs
entity_id_result = FlextModels.EntityId.create("user-123")
if entity_id_result.is_success:
    entity_id = entity_id_result.value

# Timestamps
timestamp_result = FlextModels.Timestamp.create(datetime.now())
if timestamp_result.is_success:
    timestamp = timestamp_result.value
```

### Validation Methods

```python
from flext_core import FlextModels

# Validate email addresses
email_result = FlextModels.create_validated_email("test@domain.com")
if email_result.is_success:
    validated_email = email_result.value

# Validate URLs
url_result = FlextModels.create_validated_url("https://api.service.com")
if url_result.is_success:
    validated_url = url_result.value

# Validate HTTP URLs with advanced checks
http_url_result = FlextModels.create_validated_http_url(
    "https://api.example.com:8080",
    max_length=2048,
    max_port=65535
)
if http_url_result.is_success:
    validated_http_url = http_url_result.value

# Validate file paths
path_result = FlextModels.create_validated_file_path("/home/user/file.txt")
if path_result.is_success:
    validated_path = path_result.value

# Validate existing file paths
existing_path_result = FlextModels.create_validated_existing_file_path("/etc/hosts")
if existing_path_result.is_success:
    existing_path = existing_path_result.value

# Validate ISO date strings
date_result = FlextModels.create_validated_iso_date("2025-01-08")
if date_result.is_success:
    validated_date = date_result.value

# Validate date ranges
date_range_result = FlextModels.create_validated_date_range(
    "2025-01-01", "2025-01-31"
)
if date_range_result.is_success:
    start_date, end_date = date_range_result.value
```

## 🔧 Advanced Container Features

### Factory Registration and Auto-wiring

```python
from flext_core import FlextContainer

container = FlextContainer.get_global()

# Register a factory function
def create_database_service():
    return DatabaseService()

result = container.register_factory("database", create_database_service)
assert result.is_success

# Auto-wire service dependencies
class UserService:
    def __init__(self, database: DatabaseService):
        self.database = database

# Register database first
container.register("database", DatabaseService())

# Auto-wire UserService (will automatically inject database dependency)
user_service_result = container.auto_wire(UserService, "user_service")
if user_service_result.is_success:
    user_service = user_service_result.value
```

### Batch Operations and Service Management

```python
# Batch register multiple services
services = {
    "cache": RedisCache(),
    "logger": FlextLogger(__name__),
    "config": AppConfig(),
    "email_factory": EmailService,  # Factory (callable)
}

batch_result = container.batch_register(services)
if batch_result.is_success:
    registered_names = batch_result.value
    print(f"Registered: {registered_names}")

# Get service information
info_result = container.get_info("cache")
if info_result.is_success:
    service_info = info_result.value
    print(f"Service type: {service_info['type']}")

# List all services
services_list = container.list_services()
for name, service_type in services_list.items():
    print(f"{name}: {service_type}")

# Get or create pattern
service_result = container.get_or_create(
    "new_service",
    lambda: NewService()
)
if service_result.is_success:
    service = service_result.value
```

## 📝 CQRS Commands and Queries

### Commands and Events

```python
from flext_core import FlextModels

# Create commands
command = FlextModels.Command(
    command_type="create_user",
    payload={"name": "John", "email": "john@example.com"}
)

# Validate command
validation_result = command.validate_command()
assert validation_result.is_success

# Create events
event = FlextModels.Event(
    event_type="user_created",
    aggregate_id="user-123",
    payload={"user_id": "user-123", "name": "John"}
)

# Create queries
query = FlextModels.Query(
    query_type="get_users",
    filters={"status": "active"},
    pagination={"page": 1, "size": 20}
)

# Validate query
query_validation = query.validate_query()
assert query_validation.is_success
```

### Enhanced CQRS Models

```python
# Use enhanced CQRS command with auto-naming
class CreateUserCommand(FlextModels.CqrsCommand):
    user_name: str
    user_email: str

# Command type is automatically derived: "create_user"
cmd = CreateUserCommand(user_name="John", user_email="john@example.com")
print(cmd.command_type)  # "create_user"
print(cmd.get_command_type())  # "create_user"

# Enhanced query with auto-naming
class GetActiveUsersQuery(FlextModels.CqrsQuery):
    status_filter: str = "active"

query = GetActiveUsersQuery()
print(query.query_type)  # "get_active_users"
```

## 🏢 Domain Library Usage

### FLEXT Domain Separation Principle

FLEXT follows strict domain separation where third-party libraries are accessed only through their designated FLEXT domain libraries:

```python
# ❌ FORBIDDEN - Direct third-party imports

# CLI/UI Libraries
import rich            # Use flext-cli instead
import click           # Use flext-cli instead
import typer           # Use flext-cli instead

# Web Framework Libraries
import fastapi         # Use flext-web instead
import flask           # Use flext-web instead
import django          # Use flext-web instead
import httpx           # Use flext-web instead

# HTTP Client Libraries
import requests        # Use flext-api instead
import httpx           # Use flext-api instead

# Data Pipeline Libraries
import meltano         # Use flext-meltano instead
import singer          # Use flext-meltano instead
import dbt             # Use flext-meltano instead

# Database Libraries
import sqlalchemy      # Use flext-db-oracle instead
import oracledb        # Use flext-db-oracle instead
import ldap3           # Use flext-ldap instead

# Quality/Testing Libraries
import mypy            # Use flext-quality instead
import pytest          # Use flext-quality instead
import coverage        # Use flext-quality instead
import ruff            # Use flext-quality instead
import black           # Use flext-quality instead

# gRPC Libraries
import grpc            # Use flext-grpc instead
import grpcio          # Use flext-grpc instead

# Monitoring Libraries
import redis           # Use flext-observability instead
import prometheus_client  # Use flext-observability instead

# ✅ CORRECT - Through FLEXT domains
from flext_cli import FlextCli          # Rich/Click/Typer functionality
from flext_web import FlextWebServer       # FastAPI/Flask/Django
from flext_api import FlextApiClient       # HTTP/REST requests
from flext_core import FlextLogger         # Structured logging
from flext_meltano import FlextMeltanoRunner  # Meltano/Singer/DBT
from flext_db_oracle import FlextOracleClient # SQLAlchemy 2 + oracledb
from flext_ldap import FlextLdapClient      # LDAP3 functionality
from flext_ldif import FlextLdifProcessor   # LDIF processing
from flext_quality import FlextQualityAnalyzer # Code quality analysis
from flext_grpc import FlextGrpcServer      # gRPC services
from flext_plugin import FlextPluginManager # Plugin management
from flext_tools import FlextToolsManager   # Development tooling
from flext_observability import FlextMetrics  # Monitoring/metrics
```

### Data Pipeline Domain Examples

```python
# ❌ FORBIDDEN - Direct Singer/DBT usage
# import singer
# import meltano
# from dbt.cli.main import dbtRunner
# from singer import write_record

# ✅ CORRECT - Through flext-meltano domain
from flext_meltano import FlextMeltanoRunner, FlextSingerTap, FlextDbtRunner
from flext_ldap import FlextLdapClient
from flext_db_oracle import FlextOracleClient

class DataPipelineService:
    def __init__(self):
        self._meltano = FlextMeltanoRunner()
        self._ldap = FlextLdapClient()
        self._oracle = FlextOracleClient()

    def run_ldap_to_oracle_pipeline(self) -> FlextResult[None]:
        """Run LDAP extraction to Oracle loading through FLEXT domains."""
        # Extract from LDAP using flext-ldap domain
        extract_result = self._ldap.extract_users()
        if extract_result.is_failure:
            return FlextResult[None].fail(f"LDAP extraction failed: {extract_result.error}")

        # Transform using flext-meltano domain
        transform_result = self._meltano.run_singer_pipeline(
            tap="flext-tap-ldap",
            target="flext-target-oracle",
            config=extract_result.value
        )
        if transform_result.is_failure:
            return FlextResult[None].fail(f"Pipeline failed: {transform_result.error}")

        return FlextResult[None].ok(None)

    def run_dbt_transformation(self, project: str) -> FlextResult[None]:
        """Run DBT transformations through flext-meltano domain."""
        return self._meltano.run_dbt_project(
            project_name=project,
            models=["staging", "marts"]
        )
```

### CLI Output Example

```python
# ❌ FORBIDDEN - Direct Rich usage
# from rich.console import Console
# from rich.table import Table
# console = Console()
# table = Table()

# ✅ CORRECT - Rich through flext-cli
from flext_cli import FlextCli

class UserService:
    def __init__(self):
        self._cli = FlextCli()

    def display_users(self, users: list[FlextTypes.Dict]) -> FlextResult[None]:
        """Display users using Rich tables through flext-cli domain."""
        return self._cli.display_table(
            data=users,
            title="Active Users",
            columns=["id", "name", "email", "status"]
        )

    def show_progress(self, total: int) -> FlextResult[None]:
        """Show progress using Rich progress bars through flext-cli domain."""
        return self._cli.create_progress_bar(
            total=total,
            description="Processing users..."
        )
```

### Database Integration Example

```python
# ❌ FORBIDDEN - Direct SQLAlchemy/LDAP usage
# from sqlalchemy import create_engine
# import oracledb
# import ldap3

# ✅ CORRECT - Through database domains
from flext_db_oracle import FlextOracleClient
from flext_ldap import FlextLdapClient
from flext_ldif import FlextLdifProcessor

class MigrationService:
    def __init__(self):
        self._oracle = FlextOracleClient()
        self._ldap = FlextLdapClient()
        self._ldif = FlextLdifProcessor()

    def migrate_ldap_to_oracle(self) -> FlextResult[None]:
        """Migrate LDAP data to Oracle through domain libraries."""
        # Extract from LDAP using flext-ldap domain
        users_result = self._ldap.search_users(filter="(objectClass=person)")
        if users_result.is_failure:
            return FlextResult[None].fail(f"LDAP search failed: {users_result.error}")

        # Process through LDIF domain
        ldif_result = self._ldif.convert_to_ldif(users_result.value)
        if ldif_result.is_failure:
            return FlextResult[None].fail(f"LDIF conversion failed: {ldif_result.error}")

        # Load to Oracle using flext-db-oracle domain
        load_result = self._oracle.bulk_insert(
            table="users",
            data=ldif_result.value
        )
        if load_result.is_failure:
            return FlextResult[None].fail(f"Oracle insert failed: {load_result.error}")

        return FlextResult[None].ok(None)
```

### Benefits of Domain Separation

1. **Consistency**: All CLI output follows FLEXT patterns
2. **Maintainability**: Third-party library updates handled in one place
3. **Testing**: Mock FLEXT domains instead of external libraries
4. **Standards**: Enforced coding patterns across the ecosystem
5. **Upgrades**: Centralized dependency management

---

This API reference is based on actual implementation analysis and provides working examples for all documented patterns.
