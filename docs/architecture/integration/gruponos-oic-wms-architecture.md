# GN WMS-OIC Database Operations - Standardized Architecture

## Overview

This document describes the standardized architecture implemented for the `gn_oic_wms_db` flx_project, which eliminates code duplication and maximizes reuse of existing `dc-oracle-db`, `dc-oracle-wms`, and `dc-oracle-oic` flx_project functionality.

## Architecture Principles

### 1. Layered Architecture

- **Core Layer**: Foundation services (config, logging, exceptions)
- **Operations Layer**: Business logic using existing flx_project components  
- **CLI Layer**: User interface and command orchestration
- **Scripts Layer**: Specific automation tasks

### 2. Dependency Integration

- Projects integrated via Poetry local dependencies
- No `sys.path` manipulation needed
- Clean imports from `db`, `wms`, and `oic` modules
- Shared configuration and patterns

### 3. Responsibility Separation

- Clear boundaries between layers
- Single responsibility per module
- Consistent error handling
- Centralized configuration

## Directory Structure

```
src/gn_oic_wms_db/
├── core/                    # Foundation layer
│   ├── __init__.py
│   ├── config.py           # Centralized configuration management
│   ├── exceptions.py       # Standardized exception hierarchy
│   └── logging_setup.py    # Structured logging configuration
├── operations/              # Business logic layer
│   ├── __init__.py
│   ├── database.py         # Database operations using DbClient
│   ├── schema.py           # Schema operations using db.schema
│   ├── wms_integration.py  # WMS integration using WmsClient
│   └── pipeline.py         # Pipeline orchestration
├── cli.py                  # Command line interface
├── scripts/                # Legacy scripts (being refactored)
│   ├── check_wms_tables.py
│   ├── clear_wms_data.py
│   ├── create_control_tables.py
│   ├── create_wms_tables.py
│   └── wms_pipeline.py
└── ARCHITECTURE.md         # This document
```

## Core Layer

### Configuration Management (`core/config.py`)

**Purpose**: Centralized, validated configuration for all database operations.

**Key Features**:

- Pydantic-based validation for type safety
- Environment variable loading with defaults
- Integration with existing flx_project patterns
- Credential masking for security
- Configuration validation and display

**Integration Points**:

- Uses patterns from `dc-oracle-db` for database configuration
- Extends patterns for WMS and OIC integration
- Provides unified configuration interface

**Example Usage**:

```python
from .core.config import get_config

config = get_config()
db_config = config.database
wms_config = config.wms
```

### Exception Handling (`core/exceptions.py`)

**Purpose**: Standardized exception hierarchy with context preservation.

**Key Features**:

- Base `GnWmsDbError` with context information
- Specialized exceptions for different operation types
- Integration with existing flx_project exception patterns
- Structured error information for debugging

**Exception Hierarchy**:

- `GnWmsDbError` (base)
  - `ConfigurationError`
  - `DatabaseOperationError`
  - `SchemaError`
  - `WmsIntegrationError`
  - `PipelineError`

### Logging (`core/logging_setup.py`)

**Purpose**: Structured logging with contextual information.

**Key Features**:

- Structured logging using `structlog`
- Environment-based configuration
- Context preservation across operations
- Integration with existing flx_project logging patterns
- Support for different output formats

## Operations Layer

### Database Operations (`operations/database.py`)

**Purpose**: Standardized database operations using `dc-oracle-db` functionality.

**Key Features**:

- Uses `db.client.DbClient` for all database operations
- Connection management and pooling
- Transaction handling with proper cleanup
- Watermark management for incremental sync
- Performance monitoring and metrics

**Integration with dc-oracle-db**:

```python
from db.client import DbClient
from db.exceptions import DbError

class GnDatabaseManager:
    def __init__(self):
        self._client = DbClient(config.database.connection_string)
```

### Schema Operations (`operations/schema.py`)

**Purpose**: Schema discovery and management using `db.schema` functionality.

**Key Features**:

- Uses `db.schema.SchemaExtractor` for schema discovery
- Table creation and management
- Column validation and mapping
- Index and constraint management

**Integration with dc-oracle-db**:

```python
from db.schema import SchemaExtractor, TableSchema

class GnSchemaManager:
    def get_table_schema(self, table_name: str) -> dict:
        extractor = SchemaExtractor(self.db_client)
        return extractor.extract_table_schema(table_name)
```

### WMS Integration (`operations/wms_integration.py`)

**Purpose**: WMS data extraction using `dc-oracle-wms` functionality.

**Key Features**:

- Uses `WmsClient` for data extraction when available
- Graceful fallback to sample data generation
- Data transformation and validation
- Resource management and pagination
- Error handling and retry logic

**Integration with dc-oracle-wms**:

```python
from wms import WmsClient
from wms.exceptions import WmsError

class GnWmsIntegration:
    def extract_data(self, resource: str) -> list[dict]:
        result = self.client.search(entity_name=resource)
        return self._process_wms_records(result.data)
```

### Pipeline Operations (`operations/pipeline.py`)

**Purpose**: ETL pipeline orchestration integrating all components.

**Key Features**:

- Full and incremental synchronization
- Batch processing with progress tracking
- Error handling and recovery
- Integration with OIC for notifications
- Watermark management

**Integration with dc-oracle-oic**:

```python
from oic import OicClient
from oic.exceptions import OicError

class GnPipelineOrchestrator:
    def _send_sync_notification(self, results: dict) -> None:
        if self.oic_client:
            self.oic_client.send_notification(results)
```

## CLI Layer

### Command Line Interface (`cli.py`)

**Purpose**: User-friendly interface for all database operations.

**Key Features**:

- Uses `typer` for modern CLI experience
- Rich formatting for better user experience
- Comprehensive error handling
- Progress tracking for long operations
- Consistent output formatting

**Available Commands**:

- `config`: Validate and display configuration
- `tables`: List and analyze database tables
- `sync`: Synchronize WMS data to database
- `validate`: Data integrity validation
- `backup`: Export table data
- `test-connections`: Test all connections

## Integration with Existing Projects

### Poetry Dependencies

The flx_project is configured to use the existing projects as local dependencies:

```toml
[tool.poetry.dependencies]
# Local flx_project dependencies
dc-oracle-db = { path = "../dc-oracle-db", develop = true }
dc-oracle-wms = { path = "../dc-oracle-wms", develop = true }
dc-oracle-oic = { path = "../dc-oracle-oic", develop = true }
```

### Import Patterns

Direct imports from the dependency projects:

```python
# Database operations
from db.client import DbClient
from db.schema import SchemaExtractor
from db.exceptions import DbError

# WMS integration
from wms import WmsClient
from wms.exceptions import WmsError

# OIC integration
from oic import OicClient
from oic.exceptions import OicError
```

### Configuration Integration

Reuses existing flx_project configuration patterns while extending them:

```python
# Database configuration follows dc-oracle-db patterns
class DatabaseConfig(BaseModel):
    host: str = Field(default="localhost")
    port: int = Field(default=1521)
    service_name: str = Field(...)
    username: str = Field(...)
    password: str = Field(...)
    
    @computed_field
    @property
    def connection_string(self) -> str:
        # Uses same format as dc-oracle-db
        return f"oracle://{self.username}:{self.password}@{self.host}:{self.port}/{self.service_name}"
```

## Benefits of Standardized Architecture

### 1. Code Reuse

- Eliminates duplication across modules
- Leverages existing, tested functionality
- Maintains consistency with other projects

### 2. Maintainability

- Clear separation of concerns
- Standardized error handling
- Centralized configuration management
- Consistent logging and monitoring

### 3. Extensibility

- Easy to add new operations
- Modular design allows selective usage
- Clear interfaces between layers

### 4. Reliability

- Uses proven components from existing projects
- Comprehensive error handling
- Proper resource management
- Transaction safety

## Migration from Legacy Scripts

### Before (Legacy Pattern)

```python
# Duplicated configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "1521"))
# ... more duplicated config

# Custom database connection
def get_connection():
    # Custom connection logic
    pass

# Inconsistent error handling
try:
    # operations
except Exception as e:
    print(f"Error: {e}")
```

### After (Standardized Pattern)

```python
# Centralized configuration
from .core.config import get_config
from .core.logging_setup import get_logger
from .operations.database import GnDatabaseManager

# Standardized operations
config = get_config()
logger = get_logger(__name__)
db_manager = GnDatabaseManager()

# Consistent error handling
try:
    with db_manager.get_connection() as conn:
        # operations using standardized components
        pass
except DatabaseOperationError as e:
    logger.error("Database operation failed", error=str(e), context=e.context)
```

## Usage Examples

### Basic Operations

```python
# Test connections
from .operations.database import GnDatabaseManager
from .operations.wms_integration import GnWmsIntegration

db_manager = GnDatabaseManager()
wms_integration = GnWmsIntegration()

if db_manager.test_connection() and wms_integration.test_connection():
    print("All connections successful")
```

### Data Synchronization

```python
# Run pipeline
from .operations.pipeline import GnPipelineOrchestrator

pipeline = GnPipelineOrchestrator()
results = pipeline.run_incremental_sync(
    table_name="WMS_ORDER_HDR",
    wms_resource="order_hdr",
    batch_size=1000
)
```

### CLI Usage

```bash
# Validate configuration
gn-wms-cli config

# List tables
gn-wms-cli tables --pattern "WMS_%"

# Synchronize data
gn-wms-cli sync WMS_ORDER_HDR order_hdr --type incremental

# Validate data
gn-wms-cli validate WMS_ORDER_HDR

# Backup data
gn-wms-cli backup WMS_ORDER_HDR --format csv
```

## Performance Considerations

### Connection Management

- Uses connection pooling from `dc-oracle-db`
- Proper connection lifecycle management
- Transaction boundaries respected

### Batch Processing

- Configurable batch sizes for memory efficiency
- Progress tracking for long operations
- Graceful handling of large datasets

### Resource Usage

- Lazy initialization of expensive resources
- Proper cleanup in error scenarios
- Memory-efficient data processing

## Error Handling Strategy

### Graceful Degradation

- WMS unavailable → Use sample data
- OIC unavailable → Log warning, continue
- Partial failures → Report and continue

### Context Preservation

- All errors include operation context
- Structured error information
- Consistent error reporting

### Recovery Mechanisms

- Retry logic for transient failures
- Checkpoint/watermark for long operations
- Rollback capabilities for transactions

## Testing Strategy

### Unit Tests

- Mock external dependencies
- Test core functionality in isolation
- Validate error handling

### Integration Tests

- Test with real database connections
- Validate WMS integration patterns
- End-to-end pipeline testing

### Configuration Tests

- Validate all configuration combinations
- Test environment variable handling
- Verify credential masking

## Future Enhancements

### Planned Features

1. **Real-time Sync**: WebSocket-based real-time synchronization
2. **Data Quality**: Advanced data quality checks and reporting
3. **Monitoring**: Integration with monitoring systems
4. **API**: REST API for programmatic access

### Extension Points

- Plugin system for custom transformations
- Additional export formats
- Custom validation rules
- External notification systems

---

This standardized architecture provides a solid foundation for WMS-OIC database operations while maximizing reuse of existing Datacosmos flx_project functionality and maintaining clear separation of concerns.
