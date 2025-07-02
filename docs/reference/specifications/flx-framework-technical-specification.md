# 📋 FLEXT Framework Technical Specification

> **Document Type**: Technical Specification | **Audience**: System architects, senior developers | **Scope**: Complete framework implementation

[![Architecture](https://img.shields.io/badge/architecture-hexagonal-blue.svg)](../../architecture/design/unified-architecture-guide.md)
[![Python](https://img.shields.io/badge/python-3.13+-green.svg)](../../getting-started/setup/installation-guide.md)
[![Oracle](https://img.shields.io/badge/oracle-enterprise-orange.svg)](../../guides/oracle/index.md)

**Formal technical specification for FLEXT Framework implementation based on real source code analysis**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Reference](../index.md) → **📂 Specifications**: [Index](./index.md) → **📂 Current**: FLEXT Framework Technical Specification

---

## 🎯 **Specification Overview**

### **Framework Identity**

- **Name**: FLEXT Framework (Flexible Architecture Framework)
- **Version**: 0.4.0+
- **Architecture**: Hexagonal Architecture with DDD patterns
- **Target Platform**: Python 3.13+ enterprise environments
- **Primary Use Case**: Oracle ecosystem integrations with clean architecture

### **Core Capabilities**

| **Domain**        | **Implementation**           | **Key Components**             |
| ----------------- | ---------------------------- | ------------------------------ |
| **Architecture**  | Hexagonal/Clean Architecture | Ports, Adapters, Domain Layer  |
| **Integration**   | Oracle Enterprise Systems    | WMS, OIC, Database, LDAP       |
| **Configuration** | Hierarchical Configuration   | Dynaconf, Environment-specific |
| **CLI**           | Unified Command Interface    | Cyclopts-based, extensible     |
| **Testing**       | Comprehensive Test Framework | Unit, Integration, E2E         |

---

## 🏗️ **Architecture Specification**

### **1. Domain Layer (Core)**

#### **Base Domain Classes**

```python
# Core domain abstractions
class DomainObject:
    """Base class for all domain objects with validation"""

class Identifiable:
    """Mixin for objects with unique identifiers"""

class Timestamped:
    """Mixin for objects with creation/modification timestamps"""

class Versionable:
    """Mixin for objects supporting optimistic locking"""
```

#### **Entity and Aggregate Root**

```python
class Entity(DomainObject, Identifiable, Timestamped):
    """Domain entity with event collection capabilities"""

    def add_event(self, event: DomainEvent) -> None:
        """Collect domain events for publishing"""

    def clear_events(self) -> list[DomainEvent]:
        """Clear and return collected events"""

class AggregateRoot(Entity, Versionable):
    """Aggregate root with consistency boundary"""

    def touch(self) -> None:
        """Update modification timestamp"""
```

#### **Value Objects**

```python
# Rich value objects with business validation
class Money(ValueObject):
    amount: Decimal
    currency: str

class Email(ValueObject):
    address: str

class DateRange(ValueObject):
    start_date: date
    end_date: date
```

### **2. Application Layer**

#### **Service Base Classes**

```python
class ApplicationService:
    """Base class for application services"""

class CommandService(ApplicationService):
    """Service for handling commands (CQRS)"""

class QueryService(ApplicationService):
    """Service for handling queries (CQRS)"""
```

#### **Bootstrap and Dependency Injection**

```python
class Bootstrap:
    """Application lifecycle and dependency injection"""

    def configure_services(self) -> ServiceRegistry:
        """Configure and return service registry"""

class ServiceRegistry:
    """Dependency management and service location"""
```

### **3. Infrastructure Layer**

#### **Adapter Foundation**

```python
class BaseAdapter(ABC):
    """Abstract base for all adapters with lifecycle management"""

    # Lifecycle methods
    async def _connect(self) -> None: ...
    async def _disconnect(self) -> None: ...
    async def _health_check(self) -> HealthStatus: ...

    # Operational methods
    async def initialize(self) -> None: ...
    async def shutdown(self) -> None: ...
    def get_metrics(self) -> AdapterMetrics: ...
```

#### **Port Protocols**

```python
# Inbound ports
class CliPort(Protocol):
    """Protocol for CLI interactions"""

class ApiPort(Protocol):
    """Protocol for HTTP API interactions"""

# Outbound ports
class DatabasePort(Protocol):
    """Protocol for database operations"""

class HttpPort(Protocol):
    """Protocol for HTTP client operations"""
```

---

## 🔧 **Configuration Management Specification**

### **Hierarchical Configuration System**

#### **Configuration Priority (Highest to Lowest)**

1. **Command-line arguments** - Runtime overrides
2. **Environment variables** - Container/deployment specific
3. **Configuration files** - Environment-specific YAML/JSON
4. **Adapter defaults** - Component-specific defaults
5. **Framework defaults** - System-wide defaults

#### **ConfigManager Implementation**

```python
class ConfigManager:
    """Hierarchical configuration management with Dynaconf backend"""

    def __init__(self, env: str = "development"):
        self.dynaconf = Dynaconf(
            environments=True,
            env_switcher="ENV_FOR_DYNACONF",
            settings_files=[f"config.{env}.yaml", "config.yaml"]
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with hierarchy resolution"""

    def set_runtime(self, key: str, value: Any) -> None:
        """Set runtime configuration value"""
```

#### **Environment-Specific Configuration**

```yaml
# config.development.yaml
database:
  host: localhost
  port: 1521
  service_name: XEPDB1

# config.production.yaml
database:
  host: ${DB_HOST}
  port: ${DB_PORT:1522}
  service_name: ${DB_SERVICE}
  wallet_location: ${ORACLE_WALLET_PATH}
```

---

## 🌐 **Oracle Integration Specifications**

### **1. Oracle Database Integration**

#### **FlextOracleDbAdapter Implementation**

```python
class FlextOracleDbAdapter(BaseAdapter):
    """Oracle Database adapter with enterprise features"""

    # Connection configuration
    host: str
    port: int = 1522
    service_name: str | None = None
    username: str
    password: str
    wallet_location: str | None = None  # For Autonomous Database

    async def _connect(self) -> None:
        """Establish Oracle connection with TCPS support"""
        if self.wallet_location:
            # Autonomous Database with wallet
            dsn = self._build_tcps_dsn()
        else:
            # Standard Oracle connection
            dsn = f"{self.host}:{self.port}/{self.service_name}"

        self._connection = oracledb.connect(
            user=self.username,
            password=self.password,
            dsn=dsn
        )
```

#### **Database Operations**

```python
class DatabaseOperations:
    """High-level database operations"""

    async def upsert(self, table: str, data: dict, key_columns: list[str]) -> None:
        """UPSERT using Oracle MERGE statement"""

    async def bulk_insert(self, table: str, data: list[dict]) -> None:
        """Bulk insert with batch processing"""

    async def execute_query(self, sql: str, params: dict = None) -> list[dict]:
        """Execute query with parameter binding"""
```

### **2. Oracle WMS Integration**

#### **WmsClient Implementation**

```python
class WmsClient(BaseAdapter):
    """Oracle WMS REST API client"""

    # WMS-specific configuration
    base_url: str
    facility_id: str
    client_id: str
    client_secret: str

    # Core WMS operations
    async def inventory_inquiry(self, item_id: str) -> InventoryInfo:
        """Query item inventory status"""

    async def lpn_operations(self, lpn: str, operation: str) -> LpnResult:
        """License Plate Number operations"""

    async def warehouse_tasks(self, task_type: str) -> list[WarehouseTask]:
        """Retrieve warehouse operational tasks"""
```

### **3. Oracle OIC Integration**

#### **OicClient with JWT Authentication**

```python
class OicClient(BaseAdapter):
    """Oracle Integration Cloud client with JWT authentication"""

    # OIC configuration
    oic_host: str
    client_id: str
    client_secret: str
    scope: str = "default"

    async def authenticate(self) -> str:
        """JWT authentication with Oracle Identity Cloud"""

    async def submit_integration(self, integration_id: str, payload: dict) -> str:
        """Submit integration request to OIC"""

    async def monitor_integration(self, instance_id: str) -> IntegrationStatus:
        """Monitor integration execution status"""
```

---

## 🖥️ **CLI Specification**

### **Unified CLI Architecture**

#### **Command Structure**

```bash
flx [global-flags] <command> [subcommand] [args]

# Global flags (available for all commands)
--debug          # Enable debug logging
--verbose        # Verbose output
--json           # JSON output format
--yaml           # YAML output format
--table          # Table output format
--csv            # CSV output format
```

#### **Command Categories**

| **Category** | **Purpose**              | **Example Commands**                                         |
| ------------ | ------------------------ | ------------------------------------------------------------ |
| **app**      | Application lifecycle    | `flx app start`, `flx app stop`, `flx app status`            |
| **config**   | Configuration management | `flx config show`, `flx config set`, `flx config validate`   |
| **system**   | System operations        | `flx system health`, `flx system info`, `flx system metrics` |
| **adapter**  | Adapter management       | `flx adapter list`, `flx adapter status`, `flx adapter test` |
| **help**     | Documentation            | `flx help`, `flx help adapter`                               |
| **version**  | Version information      | `flx version`, `flx version --detailed`                      |

#### **CLI Service Implementation**

```python
class UnifiedCliApplication:
    """Main CLI coordination class"""

    def __init__(self):
        self.cli_service = CliService()
        self.output_service = OutputService()

    async def run(self, args: list[str]) -> int:
        """Execute CLI command with error handling"""

class CliService:
    """Infrastructure service using Cyclopts"""

    def __init__(self, use_test_engine: bool = False):
        if use_test_engine:
            self.engine = CliTestEngine()
        else:
            self.engine = CycloptsEngine()

    async def execute_command(self, name: str, args: list[str], options: dict) -> Any:
        """Dynamic command execution with reflection"""
```

---

## 🧪 **Testing Framework Specification**

### **Test Engine Architecture**

#### **Test Engine Types**

```python
class DeclarativeTestEngine:
    """Behavior-driven testing with declarative syntax"""

    def scenario(self, name: str) -> ScenarioBuilder:
        """Create test scenario with fluent API"""

class CliTestEngine:
    """CLI command testing without external dependencies"""

    def mock_command(self, command: str, response: Any) -> None:
        """Mock CLI command response"""

class OracleTestEngine:
    """Oracle-specific testing with connection mocking"""

    def mock_oracle_connection(self, responses: dict) -> None:
        """Mock Oracle database responses"""
```

#### **Testing Patterns**

```python
# Unit test example
@pytest.mark.unit
async def test_entity_event_collection():
    entity = Entity(id="test-123")
    event = DomainEvent(type="created", data={"id": "test-123"})

    entity.add_event(event)
    events = entity.clear_events()

    assert len(events) == 1
    assert events[0].type == "created"

# Integration test example
@pytest.mark.integration
async def test_oracle_adapter_connection():
    adapter = FlextOracleDbAdapter(
        host="localhost", port=1521, service_name="XEPDB1",
        username="test", password="test"
    )

    await adapter.initialize()
    health = await adapter._health_check()
    await adapter.shutdown()

    assert health.status == HealthStatus.HEALTHY
```

---

## 🔗 **Cross-Section Navigation**

### **⬅️ Prerequisites**

- [Architecture Hub](../../architecture/index.md) - Understanding hexagonal architecture patterns before implementing specifications
- [Getting Started](../../getting-started/index.md) - Framework installation and basic concepts required for specification compliance
- [API Reference](../../api-reference/index.md) - Complete API documentation complementing this technical specification

### **➡️ Next Steps**

- [Development Hub](../../development/index.md) - Development practices implementing these specifications in real projects
- [Guides Hub](../../guides/index.md) - Practical implementation tutorials demonstrating specification compliance
- [Examples Hub](../../examples/index.md) - Working code examples showcasing specification patterns

### **🔗 Related Sections**

- [Oracle Integration Guide](../../guides/oracle/oracle-integration-comprehensive-guide.md) - Oracle-specific implementation patterns following these specifications
- [Testing Documentation](../../development/testing/index.md) - Testing strategies ensuring specification compliance and validation
- [Infrastructure Documentation](../../infrastructure/index.md) - Infrastructure implementations utilizing these framework specifications
- [Engineering Hub](../../engineering/index.md) - Architectural decisions and design proposals based on these specifications

---

## 📊 **Compliance and Validation**

### **Specification Compliance Requirements**

- **Source Code Validation**: All specifications validated against actual implementation in `/flx/src/`
- **API Contract Compliance**: Method signatures and protocols match implementation
- **Testing Coverage**: Comprehensive test coverage for all specified components
- **Documentation Accuracy**: Technical details verified against working code

### **Implementation Standards**

- **Python 3.13+**: Modern Python features and type annotations
- **Pydantic Validation**: Data validation and serialization standards
- **Async/Await**: Non-blocking operations throughout the framework
- **Error Handling**: Comprehensive exception handling and resilience patterns

---

## 📋 **Specification Metadata**

- **Specification Version**: 1.0.0
- **Framework Version**: FLEXT 0.4.0+
- **Validation Date**: June 11, 2025
- **Source Code Base**: `/flx/src/flx/` and Oracle integration projects
- **Compliance Status**: ✅ 100% validated against implementation

---

**📂 Specification**: [Technical Specifications Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
