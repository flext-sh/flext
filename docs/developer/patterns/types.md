# Type System Patterns

**Version**: 0.9.0 | **Status**: Active | **Python**: 3.13+

## Overview

Hierarchical, namespace-based type system that ensures consistency and type safety across the FLEXT ecosystem. Eliminates type duplication and provides clear semantic meaning.

## Core Principles

### Namespace Organization

All types organized under `FlextTypes` with semantic domain grouping:

```python
FlextTypes.*     # Foundation types
FlextTypes.Data.*     # Data integration types
FlextTypes.Obs.*      # Observability types
FlextTypes.Singer.*   # Singer protocol types
FlextTypes.Bridge.*   # Go-Python bridge types
```

### Single Source of Truth

Each type defined exactly once in its semantic domain.

### Protocol-Based Extensibility

Use protocols for structural typing instead of deep inheritance.

## Core Foundation Types

```python
from typing import Union, Dict, Callable, Protocol

from datetime import datetime
from decimal import Decimal
from flext_core import T, U, V

class FlextTypes:
    """Unified type system for FLEXT ecosystem."""

    class Core:
        """Foundation types used across all domains."""

        # JSON Types
        JsonValue = Union[str, int, float, bool, None, FlextTypes.Dict, list]
        JsonDict = Dict[str, JsonValue]
        JsonList = list[JsonValue]

        # Result Types
        Result = 'FlextResult[T]'
        ResultList = 'FlextResult[list[T]]'
        ResultDict = 'FlextResult[Dict[K, V]]'

        # Functional Types
        Predicate = Callable[[T], bool]
        Transformer = Callable[[T], T]
        Validator = Callable[[T], Result]
        Factory = Callable[..., Result]

        # Time Types
        Timestamp = datetime
        Duration = float  # seconds

        # Numeric Types
        Money = Decimal
        Percentage = float  # 0.0 to 1.0
        Count = int       # Non-negative integer

        # Identifier Types
        Id = str          # UUID string
        Slug = str        # URL-safe identifier
        Version = str     # Semantic version
```

## Data Integration Types

```python
class FlextTypes:
    class Data:
        """Data integration and processing types."""

        # Connection Types
        ConnectionString = str
        ConnectionConfig = FlextTypes.Dict
        Connection = Union[ConnectionString, ConnectionConfig]

        # Schema Types
        FieldName = str
        FieldType = str  # 'string', 'integer', 'number', 'boolean', 'object', 'array'
        FieldDefinition = FlextTypes.Dict
        Schema = Dict[FieldName, FieldDefinition]

        # Record Types
        Record = FlextTypes.Dict
        RecordBatch = list[Record]
        RecordStream = Iterator[Record]

        # Transformation Types
        FieldMapping = Dict[FieldName, FieldName]
        ValueTransformer = Callable[[object], object]
        RecordTransformer = Callable[[Record], Record]

        # Query Types
        Query = str
        QueryParams = FlextTypes.Dict
        QueryResult = Union[Record, RecordBatch]

        # Metadata Types
        TableName = str
        DatabaseName = str
        SchemaName = str
        ColumnMetadata = FlextTypes.Dict
        TableMetadata = FlextTypes.Dict
```

## Authentication Types

```python
class FlextTypes:
    class Auth:
        """Authentication and authorization types."""

        # Token Types
        Token = str
        TokenType = Literal['Bearer', 'Basic', 'API']
        TokenPayload = FlextTypes.Dict

        # Credential Types
        Username = str
        Password = str
        ApiKey = str
        ClientId = str
        ClientSecret = str

        # Authentication Types
        Credentials = Union[
            Tuple[Username, Password],
            ApiKey,
            Tuple[ClientId, ClientSecret]
        ]

        # Session Types
        SessionId = str
        SessionData = FlextTypes.Dict
        SessionStore = Dict[SessionId, SessionData]

        # Permission Types
        Permission = str
        Role = str
        Scope = str
        PermissionSet = Set[Permission]
        RoleSet = Set[Role]

        # Context Types
        UserId = str
        TenantId = str
        AuthContext = FlextTypes.Dict
```

## Observability Types

```python
class FlextTypes:
    class Obs:
        """Observability and monitoring types."""

        # Logging Types
        LogLevel = Literal['TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']
        LogContext = FlextTypes.Dict
        LogEntry = FlextTypes.Dict

        # Metrics Types
        MetricName = str
        MetricValue = Union[int, float]
        MetricTags = Dict[str, str]
        MetricType = Literal['counter', 'gauge', 'histogram', 'summary']

        # Tracing Types
        TraceId = str
        SpanId = str
        SpanContext = FlextTypes.Dict
        SpanKind = Literal['CLIENT', 'SERVER', 'PRODUCER', 'CONSUMER', 'INTERNAL']

        # Alert Types
        AlertLevel = Literal['INFO', 'WARNING', 'ERROR', 'CRITICAL']
        AlertName = str
        AlertMessage = str
        AlertContext = FlextTypes.Dict

        # Health Check Types
        HealthStatus = Literal['HEALTHY', 'DEGRADED', 'UNHEALTHY']
        HealthCheck = FlextTypes.Dict
        HealthReport = Dict[str, HealthCheck]
```

## Singer Protocol Types

```python
class FlextTypes:
    class Singer:
        """Singer protocol specific types."""

        # Message Types
        MessageType = Literal['RECORD', 'STATE', 'SCHEMA', 'ACTIVATE_VERSION']
        Record = FlextTypes.Dict
        State = FlextTypes.Dict
        Schema = FlextTypes.Dict

        # Stream Types
        StreamName = str
        TapStreamId = str
        StreamMetadata = FlextTypes.Dict

        # Catalog Types
        CatalogEntry = FlextTypes.Dict
        Catalog = Dict[str, CatalogEntry]
        SelectedStreams = Set[StreamName]

        # Configuration Types
        TapConfig = FlextTypes.Dict
        TargetConfig = FlextTypes.Dict
        StateValue = object

        # Replication Types
        ReplicationMethod = Literal['FULL_TABLE', 'INCREMENTAL', 'LOG_BASED']
        ReplicationKey = str
        BookmarkValue = object
```

## Bridge Types (Go-Python)

```python
class FlextTypes:
    class Bridge:
        """Go-Python bridge communication types."""

        # Message Types
        MessageId = str
        MessageType = str
        MessagePayload = FlextTypes.Dict

        # Protocol Types
        RequestId = str
        ResponseId = str
        ErrorCode = str

        # Serialization Types
        SerializedData = bytes
        EncodingType = Literal['json', 'msgpack', 'protobuf']

        # Contract Types
        ServiceName = str
        MethodName = str
        ServiceContract = Dict[MethodName, FlextTypes.Dict]

        # Bridge Message Structure
        BridgeMessage = TypedDict('BridgeMessage', {
            'id': MessageId,
            'type': MessageType,
            'service': ServiceName,
            'method': MethodName,
            'payload': MessagePayload,
            'timestamp': datetime,
            'correlation_id': Optional[str]
        })
```

## Usage Examples

### Basic Type Usage

```python
from flext_core.types import FlextTypes
from flext_core.result import FlextResult

# Using core types
def validate_data(data: FlextTypes.JsonDict) -> FlextTypes.Result:
    if not isinstance(data, dict):
        return FlextResult[None].fail("Data must be a dictionary")
    return FlextResult[None].ok(data)

# Using data types
def create_connection(
    config: FlextTypes.Data.ConnectionConfig
) -> FlextResult[FlextTypes.Data.Connection]:
    required_keys = {'host', 'port', 'database'}
    if not all(key in config for key in required_keys):
        return FlextResult[None].fail("Missing required connection parameters")

    connection_string = f"{config['host']}:{config['port']}/{config['database']}"
    return FlextResult[None].ok(connection_string)

# Using auth types
def validate_token(
    token: FlextTypes.Auth.Token,
    token_type: FlextTypes.Auth.TokenType = 'Bearer'
) -> FlextResult[FlextTypes.Auth.TokenPayload]:
    if not token.startswith(f"{token_type} "):
        return FlextResult[None].fail(f"Invalid token type, expected {token_type}")

    payload: FlextTypes.Auth.TokenPayload = {
        'user_id': '12345',
        'scopes': ['read', 'write'],
        'exp': 1234567890
    }
    return FlextResult[None].ok(payload)
```

### Type-Safe Data Transformation

```python
def transform_records(
    records: FlextTypes.Data.RecordBatch,
    transformer: FlextTypes.Data.RecordTransformer,
    validator: FlextTypes.Validator[FlextTypes.Data.Record]
) -> FlextResult[FlextTypes.Data.RecordBatch]:
    """Transform and validate a batch of records."""
    transformed: FlextTypes.Data.RecordBatch = []

    for record in records:
        new_record = transformer(record)
        validation_result = validator(new_record)

        if not validation_result.success:
            return FlextResult[None].fail(
                f"Record validation failed: {validation_result.error}",
                record=new_record
            )

        transformed.append(new_record)

    return FlextResult[None].ok(transformed)
```

### Protocol-Based Connection Handling

```python
@runtime_checkable
class DataSource(Protocol):
    """Protocol for data sources."""

    def connect(self, config: FlextTypes.Data.ConnectionConfig) -> FlextTypes.Result: ...

    def query(
        self,
        query: FlextTypes.Data.Query,
        params: FlextTypes.Data.QueryParams
    ) -> FlextResult[FlextTypes.Data.QueryResult]: ...

    def disconnect(self) -> FlextTypes.Result: ...

# Implementation
class PostgresSource:
    def connect(self, config: FlextTypes.Data.ConnectionConfig) -> FlextTypes.Result:
        return FlextResult[None].ok(None)

    def query(
        self,
        query: FlextTypes.Data.Query,
        params: FlextTypes.Data.QueryParams
    ) -> FlextResult[FlextTypes.Data.QueryResult]:
        result: FlextTypes.Data.RecordBatch = []
        return FlextResult[None].ok(result)

    def disconnect(self) -> FlextTypes.Result:
        return FlextResult[None].ok(None)

# Type checking
source: DataSource = PostgresSource()
assert isinstance(source, DataSource)  # True due to Protocol
```

## Quality Standards

- **Semantic Naming**: Types must clearly indicate their purpose
- **Single Definition**: Each type defined exactly once
- **Namespace Organization**: Types grouped by semantic domain
- **Protocol Usage**: Prefer protocols over concrete inheritance
- **Type Aliases**: Use meaningful aliases for complex types

## Related Patterns

- [Foundation](./foundation.md) - Uses type system
- [Error & Observability](./error-observability.md) - Defines Obs types
- [Configuration](./config-cli.md) - Uses type definitions

---

**Type System Patterns** - A unified, hierarchical type system that eliminates duplication and provides semantic clarity across the entire FLEXT ecosystem.
