# 🗄️ Oracle Database Complete Integration Guide

> **Function**: Complete Oracle Database integration with FLX Framework | **Audience**: Database engineers, backend developers | **Status**: Production-ready

[![Database](https://img.shields.io/badge/Oracle-Database-red.svg)](./index.md)
[![Integration](https://img.shields.io/badge/integration-async-blue.svg)](./oracle-integration-comprehensive-guide.md)
[![FLX](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../../index.md)

**Complete Oracle Database integration guide for FLX framework covering modern async database operations, schema introspection, transaction management, and hexagonal architecture patterns - validated against production implementations**

## Overview

**Complete Oracle Database integration guide for FLX framework covering modern async database operations, schema introspection, transaction management, and hexagonal architecture patterns**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides Hub](../index.md) → **📂 Oracle**: [Oracle Hub](./index.md) → **📄 Current**: Database Complete Guide

### **📍 Learning Path Position**

```
[Oracle Hub](./index.md) → **[Database Complete Guide]** → [WMS Integration](./oracle-wms-comprehensive-guide.md)
```

## 🎯 Quick Navigation

- [**Getting Started**](#-getting-started) - Setup and basic configuration
- [**FLX Database Plugin**](#-flext-database-plugin) - Modern simplified architecture
- [**Database Operations**](#-database-operations) - Queries, transactions, and schema
- [**CLI Interface**](#-cli-interface) - Command-line database operations
- [**Advanced Features**](#-advanced-features) - Monitoring, pooling, and performance
- [**Hexagonal Architecture**](#-hexagonal-architecture) - Clean architecture patterns

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Oracle Database (11g or higher)
- Oracle Client libraries (cx_Oracle or oracledb)
- FLX Framework installed

### Installation

```bash
# Install Oracle database adapter
pip install flext-database-oracle

# Install Oracle client dependencies
pip install oracledb pydantic

# For development
pip install -e .[dev]
```

### Environment Configuration

Set up your Oracle database connection:

```bash
# Oracle Database Configuration
export FLX_ORACLE_HOST=localhost
export FLX_ORACLE_PORT=1521
export FLX_ORACLE_SERVICE_NAME=XE
export FLX_ORACLE_USERNAME=hr
export FLX_ORACLE_PASSWORD=password

# Optional SSL Configuration
export FLX_ORACLE_SSL_MODE=true
export FLX_ORACLE_SSL_VERIFY=true

# Connection Pool Settings
export FLX_ORACLE_POOL_MIN=5
export FLX_ORACLE_POOL_MAX=20
```

### Basic Connection Test

```bash
# Test CLI connectivity
python -m flext_database_oracle.cli info

# Check Oracle version
python -m flext_database_oracle.cli version

# Show capabilities
python -m flext_database_oracle.cli capabilities
```

## 🔌 FLX Database Plugin

### Simplified Modern Architecture

The FLX Database Oracle adapter features a dramatically simplified architecture that reduces complexity while maintaining full functionality:

#### Key Features

- **Single Purpose**: Oracle database operations only
- **Clean Patterns**: Follows modern Python 3.13+ patterns
- **Strong Typing**: Full type safety with Pydantic 2.0
- **Bidirectional**: Supports both inbound and outbound operations
- **Thread-Safe**: Safe for concurrent operations
- **Health Monitoring**: Built-in health checks and monitoring

#### Hexagonal Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    DatabasePlugin                          │
│  (Main plugin implementing FlxBidirectionalPlugin)         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┼───────────────────────────────────────┐
│                   Ports                                     │
│  ├─ FlxConnectionPort   (Database connections)             │
│  ├─ QueryPort        (SQL execution)                       │
│  ├─ SchemaPort       (Schema introspection)                │
│  └─ TransactionPort  (Transaction management)              │
└─────────────────────┼───────────────────────────────────────┘
                      │
┌─────────────────────┼───────────────────────────────────────┐
│                 Adapters                                    │
│  ├─ OracleConnectionAdapter                                │
│  ├─ OracleQueryAdapter                                     │
│  ├─ OracleSchemaAdapter                                    │
│  └─ OracleTransactionAdapter                               │
└─────────────────────────────────────────────────────────────┘
```

### Basic Usage

```python
import asyncio
from flext_database_oracle import flext_create_database_plugin
from flext.plugins.base import FlxPluginMode

async def main():
    # Create plugin
    plugin = flext_create_database_plugin(
        host="localhost",
        username="hr",
        password="oracle",
        service_name="XEPDB1",
        mode=FlxPluginMode.BIDIRECTIONAL
    )

    # Initialize and start
    await plugin.initialize()
    await plugin.start()

    # Execute query
    query_port = plugin.get_query_port()
    result = await query_port.execute_query("SELECT SYSDATE FROM DUAL")
    print(f"Current date: {result.data}")

    # Clean shutdown
    await plugin.stop()

asyncio.run(main())
```

### Advanced Configuration

```python
from flext_database_oracle import DatabaseConfig, DatabasePlugin

# Advanced configuration
config = DatabaseConfig(
    host="localhost",
    username="hr",
    password="oracle",
    service_name="XEPDB1",
    port=1521,
    # Connection pooling
    pool_min=5,
    pool_max=20,
    pool_increment=2,
    pooling_mode="pooled",
    # Performance
    arraysize=2000,
    connect_timeout=60,
    query_timeout=300,
    # SSL
    ssl_mode=True,
    ssl_verify=True,
    # Monitoring
    enable_monitoring=True,
    log_queries=True,
    log_performance=True,
)

plugin = DatabasePlugin(config)
```

## 💾 Database Operations

### Connection Management

```python
connection_port = plugin.get_connection_port()

# Test connectivity
is_responsive = await connection_port.ping()

# Get server version
version = await connection_port.get_server_version()

# Connection status
connection = await connection_port.connect()
print(f"Connected to: {connection.dsn}")
```

### Query Operations

#### Simple Queries

```python
query_port = plugin.get_query_port()

# Simple query
result = await query_port.execute_query("SELECT COUNT(*) FROM hr.employees")

# Parameterized query
result = await query_port.execute_query(
    "SELECT * FROM hr.employees WHERE employee_id = :emp_id",
    {"emp_id": 100}
)

# Multiple results
result = await query_port.execute_query(
    "SELECT employee_id, first_name, last_name FROM hr.employees WHERE department_id = :dept_id",
    {"dept_id": 10}
)

for row in result.data:
    print(f"Employee: {row['first_name']} {row['last_name']}")
```

#### Batch Operations

```python
# Batch updates
batch_result = await query_port.execute_many(
    "UPDATE hr.employees SET salary = :salary WHERE employee_id = :emp_id",
    [
        {"emp_id": 100, "salary": 50000},
        {"emp_id": 101, "salary": 55000},
        {"emp_id": 102, "salary": 60000},
    ]
)

print(f"Updated {batch_result.rows_affected} rows")
```

#### Query Performance Analysis

```python
# Get execution plan
plan = await query_port.get_query_plan(
    "SELECT e.*, d.department_name FROM hr.employees e JOIN hr.departments d ON e.department_id = d.department_id"
)

print("Execution Plan:")
for step in plan.steps:
    print(f"  {step.operation}: {step.cost}")
```

### Schema Introspection

#### Schema Information

```python
schema_port = plugin.get_schema_port()

# Get available schemas
schemas = await schema_port.get_schemas()
print(f"Available schemas: {[s.schema_name for s in schemas]}")

# Get tables in schema
tables = await schema_port.get_tables("HR")
print(f"Tables in HR: {[t.table_name for t in tables]}")
```

#### Table Metadata

```python
# Table details
table_info = await schema_port.get_table_info("EMPLOYEES", "HR")
print(f"Table: {table_info.full_name}")
print(f"Rows: {table_info.num_rows}")
print(f"Size: {table_info.size_mb} MB")

# Column information
columns = await schema_port.get_columns("EMPLOYEES", "HR")
for col in columns:
    print(f"Column: {col.column_name} ({col.data_type}) {'NOT NULL' if col.nullable == 'N' else ''}")
```

#### Indexes and Constraints

```python
# Indexes
indexes = await schema_port.get_indexes("EMPLOYEES", "HR")
for idx in indexes:
    print(f"Index: {idx.index_name} on {idx.columns}")

# Primary key
pk_columns = await schema_port.get_primary_key("EMPLOYEES", "HR")
print(f"Primary key: {pk_columns}")

# Foreign keys
fk_info = await schema_port.get_foreign_keys("EMPLOYEES", "HR")
for fk in fk_info:
    print(f"FK: {fk.constraint_name} -> {fk.referenced_table}")
```

### Transaction Management

#### Basic Transactions

```python
transaction_port = plugin.get_transaction_port()

# Begin transaction
transaction = await transaction_port.begin_transaction()
transaction_id = str(transaction.transaction_id)

try:
    # Execute operations within transaction
    await transaction_port.execute_in_transaction(
        transaction_id,
        "UPDATE hr.employees SET salary = salary * 1.1 WHERE department_id = :dept_id",
        {"dept_id": 10}
    )

    await transaction_port.execute_in_transaction(
        transaction_id,
        "INSERT INTO hr.salary_history (employee_id, old_salary, new_salary, change_date) SELECT employee_id, salary/1.1, salary, SYSDATE FROM hr.employees WHERE department_id = :dept_id",
        {"dept_id": 10}
    )

    # Commit
    await transaction_port.commit_transaction(transaction_id)
    print("Transaction committed successfully")

except Exception as e:
    # Rollback on error
    await transaction_port.rollback_transaction(transaction_id)
    print(f"Transaction rolled back: {e}")
```

#### Advanced Transaction Features

```python
# Begin transaction
transaction = await transaction_port.begin_transaction()
transaction_id = str(transaction.transaction_id)

try:
    # Create savepoint
    await transaction_port.create_savepoint(transaction_id, "sp1")

    # Execute some operations
    await transaction_port.execute_in_transaction(
        transaction_id,
        "UPDATE hr.employees SET salary = salary * 1.05 WHERE department_id = :dept_id",
        {"dept_id": 20}
    )

    # Create another savepoint
    await transaction_port.create_savepoint(transaction_id, "sp2")

    # Execute more operations
    await transaction_port.execute_in_transaction(
        transaction_id,
        "UPDATE hr.employees SET commission_pct = 0.1 WHERE job_id LIKE 'SA_%'",
        {}
    )

    # Rollback to savepoint if needed
    # await transaction_port.rollback_to_savepoint(transaction_id, "sp1")

    # Commit entire transaction
    await transaction_port.commit_transaction(transaction_id)

except Exception as e:
    await transaction_port.rollback_transaction(transaction_id)
    raise e
```

## 🖥️ CLI Interface

### FlxDeclarativeCli Implementation

The module includes a modern CLI built with **FlxDeclarativeCli** that provides comprehensive Oracle Database operations.

#### Core Commands

```bash
# CLI information and capabilities
python -m flext_database_oracle.cli info                    # Show CLI information
python -m flext_database_oracle.cli version                 # Show Oracle version
python -m flext_database_oracle.cli capabilities            # Show available operations
```

#### SQL Execution

```bash
# Simple queries
python -m flext_database_oracle.cli query "SELECT * FROM hr.employees"
python -m flext_database_oracle.cli query "SELECT * FROM hr.departments" --output-format json

# Execute DDL/DML
python -m flext_database_oracle.cli execute "CREATE TABLE test (id NUMBER, name VARCHAR2(100))"
python -m flext_database_oracle.cli execute "INSERT INTO test VALUES (1, 'Test')" --commit

# Run SQL scripts
python -m flext_database_oracle.cli script /path/to/script.sql --commit
```

#### Schema Operations

```bash
# List tables using ORM
python -m flext_database_oracle.cli tables --schema-name HR --output-format table
python -m flext_database_oracle.cli tables --output-format json --limit 10

# List columns with metadata
python -m flext_database_oracle.cli columns HR EMPLOYEES --output-format table

# List indexes
python -m flext_database_oracle.cli indexes HR EMPLOYEES --output-format json

# Get table statistics
python -m flext_database_oracle.cli table-stats HR EMPLOYEES --output-format yaml
```

#### Connection and Session Management

```bash
# Monitor connections
python -m flext_database_oracle.cli connections --status CONNECTED --output-format table

# Track transactions
python -m flext_database_oracle.cli transactions --status ACTIVE --output-format table

# View session statistics
python -m flext_database_oracle.cli session-info --output-format yaml

# Monitor connection pool
python -m flext_database_oracle.cli pool-stats --output-format table
```

#### Output Formats

The CLI supports multiple output formats:

```bash
# Rich table output (default)
python -m flext_database_oracle.cli tables --output-format table

# JSON for APIs
python -m flext_database_oracle.cli tables --output-format json

# CSV for Excel
python -m flext_database_oracle.cli tables --output-format csv

# YAML for configuration
python -m flext_database_oracle.cli session-info --output-format yaml
```

#### Data Export and Import

```bash
# Export table data
python -m flext_database_oracle.cli export-table HR EMPLOYEES --output-file employees.json --format json

# Export with filters
python -m flext_database_oracle.cli export-table HR EMPLOYEES --where "salary > 50000" --format csv

# Import data
python -m flext_database_oracle.cli import-data HR EMPLOYEES --input-file employees.json --format json
```

## 🚀 Advanced Features

### Connection Pooling

```python
# Advanced connection pool configuration
config = DatabaseConfig(
    host="localhost",
    username="hr",
    password="oracle",
    service_name="XEPDB1",
    # Pool settings
    pool_min=5,           # Minimum connections
    pool_max=20,          # Maximum connections
    pool_increment=2,     # Increment size
    pooling_mode="pooled", # Pooling mode
    # Timeouts
    connect_timeout=60,   # Connection timeout
    query_timeout=300,    # Query timeout
    pool_timeout=30,      # Pool acquisition timeout
)
```

### Performance Monitoring

```python
# Enable monitoring
config = DatabaseConfig(
    # ... other settings
    enable_monitoring=True,
    log_queries=True,
    log_performance=True,
)

# Monitor query performance
query_port = plugin.get_query_port()
result = await query_port.execute_query_with_metrics(
    "SELECT * FROM hr.employees WHERE department_id = :dept_id",
    {"dept_id": 10}
)

print(f"Query executed in {result.execution_time}ms")
print(f"Rows returned: {result.row_count}")
print(f"Bytes fetched: {result.bytes_fetched}")
```

### Health Monitoring

```python
# Plugin health
is_healthy = await plugin.is_healthy()

# Detailed health check
health_info = await plugin.get_health_info()
print(f"Connection pool health: {health_info.pool_status}")
print(f"Active connections: {health_info.active_connections}")
print(f"Query success rate: {health_info.success_rate}%")

# Connection health
connection_port = plugin.get_connection_port()
is_responsive = await connection_port.ping()
```

## 🏗️ Hexagonal Architecture

### Domain Entities

```python
from flext.core.entities import AggregateRoot
from flext.core.domain.value_objects import ValueObject

# Domain entity for database records
class DatabaseRecord(AggregateRoot):
    table_name: str
    record_id: str
    data: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None

    def update_field(self, field_name: str, new_value: Any) -> None:
        if field_name not in self.data:
            raise ValueError(f"Field {field_name} does not exist")

        old_value = self.data[field_name]
        self.data[field_name] = new_value
        self.updated_at = datetime.now()
        self.increment_version()

        # Add domain event
        self.add_event(DomainEvent(
            event_type="RecordFieldUpdated",
            aggregate_id=self.entity_id,
            data={
                "table_name": self.table_name,
                "record_id": self.record_id,
                "field_name": field_name,
                "old_value": old_value,
                "new_value": new_value,
                "updated_at": self.updated_at
            }
        ))

# Value object for database connection info
class DatabaseConnection(ValueObject):
    host: str
    port: int
    service_name: str
    username: str

    @property
    def dsn(self) -> str:
        return f"{self.host}:{self.port}/{self.service_name}"

    @property
    def connection_string(self) -> str:
        return f"oracle://{self.username}@{self.dsn}"
```

### Repository Pattern

```python
from flext.adapters.outbound.database import DatabaseRepository

class OracleEmployeeRepository(DatabaseRepository):
    def __init__(self, database_plugin: DatabasePlugin):
        self.db = database_plugin
        self.query_port = database_plugin.get_query_port()
        self.transaction_port = database_plugin.get_transaction_port()

    async def find_by_id(self, employee_id: int) -> Optional[Employee]:
        """Find employee by ID."""
        result = await self.query_port.execute_query(
            "SELECT * FROM hr.employees WHERE employee_id = :emp_id",
            {"emp_id": employee_id}
        )

        if result.data:
            return Employee.from_dict(result.data[0])
        return None

    async def find_by_department(self, department_id: int) -> List[Employee]:
        """Find employees by department."""
        result = await self.query_port.execute_query(
            "SELECT * FROM hr.employees WHERE department_id = :dept_id ORDER BY last_name, first_name",
            {"dept_id": department_id}
        )

        return [Employee.from_dict(row) for row in result.data]

    async def save(self, employee: Employee) -> None:
        """Save employee (insert or update)."""
        if employee.employee_id:
            await self._update_employee(employee)
        else:
            await self._insert_employee(employee)

    async def _update_employee(self, employee: Employee) -> None:
        """Update existing employee."""
        await self.query_port.execute_query(
            """
            UPDATE hr.employees
            SET first_name = :first_name,
                last_name = :last_name,
                email = :email,
                salary = :salary,
                department_id = :department_id
            WHERE employee_id = :employee_id
            """,
            employee.to_dict()
        )

    async def _insert_employee(self, employee: Employee) -> None:
        """Insert new employee."""
        result = await self.query_port.execute_query(
            """
            INSERT INTO hr.employees (first_name, last_name, email, salary, department_id)
            VALUES (:first_name, :last_name, :email, :salary, :department_id)
            RETURNING employee_id INTO :employee_id
            """,
            employee.to_dict()
        )

        employee.employee_id = result.data[0]['employee_id']
```

### Application Services

```python
from flext.application.services import ApplicationService

class EmployeeService(ApplicationService):
    def __init__(self, employee_repository: OracleEmployeeRepository):
        self.employee_repo = employee_repository

    async def promote_employee(self, employee_id: int, new_salary: float, new_title: str) -> Employee:
        """Promote employee with salary increase and title change."""

        # Find employee
        employee = await self.employee_repo.find_by_id(employee_id)
        if not employee:
            raise EmployeeNotFoundError(f"Employee {employee_id} not found")

        # Business rule: salary can only increase
        if new_salary <= employee.salary:
            raise BusinessRuleViolationError("Salary can only increase during promotion")

        # Update employee
        employee.promote(new_salary, new_title)

        # Save changes
        await self.employee_repo.save(employee)

        # Emit promotion event
        await self.event_publisher.publish(DomainEvent(
            event_type="EmployeePromoted",
            data={
                "employee_id": employee.employee_id,
                "old_salary": employee.previous_salary,
                "new_salary": new_salary,
                "new_title": new_title,
                "promoted_at": datetime.now()
            }
        ))

        return employee
```

## 🔧 Configuration Management

### Database Configuration Options

| Parameter           | Type | Default | Description                  |
| ------------------- | ---- | ------- | ---------------------------- |
| `host`              | str  | -       | Database host                |
| `port`              | int  | 1521    | Database port                |
| `username`          | str  | -       | Database username            |
| `password`          | str  | None    | Database password            |
| `service_name`      | str  | None    | Oracle service name          |
| `sid`               | str  | None    | Oracle SID                   |
| `pool_min`          | int  | 1       | Minimum pool connections     |
| `pool_max`          | int  | 10      | Maximum pool connections     |
| `pool_increment`    | int  | 1       | Pool increment size          |
| `connect_timeout`   | int  | 30      | Connection timeout (seconds) |
| `query_timeout`     | int  | 300     | Query timeout (seconds)      |
| `ssl_mode`          | bool | False   | Enable SSL/TLS               |
| `ssl_verify`        | bool | True    | Verify SSL certificates      |
| `enable_monitoring` | bool | True    | Enable monitoring            |
| `log_queries`       | bool | False   | Log executed queries         |
| `log_performance`   | bool | False   | Log performance metrics      |

### Environment Configuration

```yaml
# config/database.yaml
oracle_database:
  connection:
    host: ${ORACLE_HOST}
    port: ${ORACLE_PORT:1521}
    service_name: ${ORACLE_SERVICE_NAME}
    username: ${ORACLE_USERNAME}
    password: ${ORACLE_PASSWORD}

  pool:
    min_connections: 5
    max_connections: 20
    increment: 2
    timeout: 30

  security:
    ssl_enabled: true
    ssl_verify: true
    connection_timeout: 60
    query_timeout: 300

  monitoring:
    enabled: true
    log_queries: false
    log_performance: true
    health_check_interval: 300
```

## 🔗 **Cross-References**

### **Prerequisites**

- [Oracle Hub](./index.md) - Understanding Oracle integration architecture before database setup
- [Getting Started Hub](../../getting-started/index.md) - FLX Framework installation and basic configuration
- [Architecture Hub](../../architecture/index.md) - Hexagonal architecture patterns for database integration

### **Next Steps**

- [Oracle WMS Guide](./oracle-wms-comprehensive-guide.md) - WMS database interactions and workflow automation
- [Oracle OIC Guide](./oic-complete-guide.md) - OIC database connections and integration patterns
- [Oracle Authentication](./authentication-complete-guide.md) - Database security and authentication patterns

### **🔗 Related Implementation Topics**

- [**Database Testing Strategies**](../../development/testing/hexagonal-testing-guide.md) - Comprehensive testing patterns for database operations and transaction management
- [**Infrastructure Service Patterns**](../../infrastructure/service-patterns.md) - Database infrastructure and operational excellence for production environments
- [**Complete API Reference**](../../api-reference/core-api-reference.md) - Database adapter API documentation and entity management methods
- [**Security Architecture**](../../security/architecture/security-architecture.md) - Database security patterns, encryption, and authentication best practices
- [**Real-World Examples**](../../examples/oracle-integration-real-examples.md) - Production database integration examples with complete implementations
- [**Performance Optimization**](../../optimization/performance/optimization-guide.md) - Database performance tuning and connection optimization strategies

---

## 📊 **Document Metrics**

- **Implementation Status**: ✅ Production Ready
- **Architecture Pattern**: Simplified Hexagonal Design
- **Performance Level**: Optimized Connection Pooling
- **Testing Coverage**: Comprehensive with real examples
- **Last Updated**: June 11, 2025

---

**📂 Guide**: [Oracle Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
