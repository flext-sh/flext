# 🔧 FLX Adapter Example - Source Implementation

> **Module**: Source code implementation for FLX Adapter Example demonstrating enterprise adapter patterns | **Audience**: Developers, Framework Engineers | **Status**: Reference Implementation

## 📋 **Overview**

Complete source implementation of a FLX framework adapter example, demonstrating enterprise patterns for creating custom adapters with comprehensive error handling, configuration management, and CLI interfaces.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../../README.md) → **📂 Component**: [FLX Adapter Example](../README.md) → **📂 Current**: Source Implementation

---

## 🎯 **Module Purpose**

This source module provides a production-ready template for creating FLX framework adapters, showcasing best practices in hexagonal architecture, domain modeling, and enterprise integration patterns.

### **Key Components**

- **cli.py** - Command-line interface using Python Fire
- **client.py** - HTTP client implementation with resilience patterns
- **config.py** - Pydantic-based configuration management
- **entity.py** - Domain entity definitions
- **exceptions.py** - Custom exception hierarchy
- **models.py** - Data models and schemas
- **pagination.py** - Pagination utilities for large datasets
- **schema.py** - JSON schema definitions and validation

---

## 📁 **Module Structure**

```
src/flx_adapter_example/
├── __init__.py              # Public API exports
├── __version__.py           # Version information
├── cli.py                   # CLI interface implementation
├── client.py                # HTTP client with resilience
├── config.py                # Configuration management
├── entity.py                # Domain entities
├── exceptions.py            # Exception hierarchy
├── models.py                # Data models
├── pagination.py            # Pagination utilities
├── schema.py                # Schema validation
└── utils/                   # Utility modules
    ├── __init__.py
    ├── formatting.py         # Data formatting utilities
    ├── logging.py            # Structured logging setup
    └── validation.py         # Validation helpers
```

---

## 🔧 **Core Components**

### **1. CLI Interface (cli.py)**

Python Fire-based command-line interface:

```python
class AdapterCLI:
    """Command-line interface for FLX Adapter Example."""

    def __init__(self, config: AdapterConfig):
        self.config = config
        self.client = AdapterClient(config)

    def health(self) -> Dict[str, Any]:
        """Check adapter health status."""

    def list_entities(self, page: int = 1, limit: int = 100) -> List[Dict]:
        """List entities with pagination."""

    def get_entity(self, entity_id: str) -> Dict[str, Any]:
        """Get specific entity by ID."""
```

### **2. HTTP Client (client.py)**

Resilient HTTP client implementation:

```python
class AdapterClient:
    """HTTP client with circuit breaker and retry logic."""

    async def get(self, endpoint: str, params: Dict = None) -> Dict:
        """GET request with error handling."""

    async def post(self, endpoint: str, data: Dict) -> Dict:
        """POST request with validation."""

    async def health_check(self) -> HealthStatus:
        """Check service health."""
```

### **3. Configuration (config.py)**

Pydantic-based configuration with validation:

```python
class AdapterConfig(BaseSettings):
    """Adapter configuration with validation."""

    # Connection settings
    base_url: HttpUrl
    api_key: SecretStr
    timeout: int = Field(default=30, ge=1, le=300)

    # Resilience settings
    max_retries: int = Field(default=3, ge=0, le=10)
    circuit_breaker_threshold: int = Field(default=5, ge=1)

    class Config:
        env_prefix = "ADAPTER_"
        env_file = ".env"
```

### **4. Domain Entities (entity.py)**

Domain entity definitions with business logic:

```python
@dataclass
class AdapterEntity:
    """Domain entity with business rules."""

    id: str
    name: str
    status: EntityStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    def is_active(self) -> bool:
        """Check if entity is active."""
        return self.status == EntityStatus.ACTIVE

    def activate(self) -> None:
        """Activate entity with business rules."""
        if self.status == EntityStatus.DELETED:
            raise EntityError("Cannot activate deleted entity")
        self.status = EntityStatus.ACTIVE
        self.updated_at = datetime.utcnow()
```

### **5. Exception Hierarchy (exceptions.py)**

Comprehensive exception management:

```python
class AdapterError(Exception):
    """Base adapter exception."""
    pass

class ConfigurationError(AdapterError):
    """Configuration validation error."""
    pass

class ConnectionError(AdapterError):
    """Connection-related error."""
    pass

class EntityError(AdapterError):
    """Entity operation error."""
    pass

class ValidationError(AdapterError):
    """Data validation error."""
    pass
```

### **6. Data Models (models.py)**

Pydantic models for data serialization:

```python
class EntityModel(BaseModel):
    """Entity data model with validation."""

    id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    status: EntityStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### **7. Pagination Utilities (pagination.py)**

Enterprise pagination patterns:

```python
class PaginationParams(BaseModel):
    """Pagination parameters with validation."""

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=100, ge=1, le=1000)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: List[T]
    total: int
    page: int
    limit: int
    has_next: bool
    has_previous: bool
```

### **8. Schema Validation (schema.py)**

JSON schema definitions:

```python
ENTITY_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
        "status": {"enum": ["active", "inactive", "deleted"]},
        "created_at": {"type": "string", "format": "date-time"}
    },
    "required": ["id", "name", "status", "created_at"]
}

def validate_entity_data(data: Dict) -> None:
    """Validate entity data against schema."""
    jsonschema.validate(data, ENTITY_SCHEMA)
```

---

## 🛠️ **Utility Modules**

### **Formatting Utilities (utils/formatting.py)**

```python
def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

def format_currency(amount: Decimal, currency: str = "USD") -> str:
    """Format currency amount."""
    return f"{currency} {amount:,.2f}"

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis."""
    return text[:max_length] + "..." if len(text) > max_length else text
```

### **Logging Setup (utils/logging.py)**

```python
def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("adapter.log")
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """Get configured logger instance."""
    return logging.getLogger(name)
```

### **Validation Helpers (utils/validation.py)**

```python
def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_input(text: str) -> str:
    """Sanitize user input."""
    return html.escape(text.strip())
```

---

## 🔗 **Integration Patterns**

### **FLX Framework Integration**

```python
# Register as FLX plugin
from flx.core import Plugin

class AdapterExamplePlugin(Plugin):
    """FLX plugin implementation."""

    def __init__(self, config: AdapterConfig):
        self.config = config
        self.client = AdapterClient(config)

    async def initialize(self) -> None:
        """Initialize plugin resources."""
        await self.client.health_check()

    async def cleanup(self) -> None:
        """Cleanup plugin resources."""
        await self.client.close()
```

### **Dependency Injection**

```python
# Service container setup
container = Container()
container.wire(modules=[__name__])

@container.provider
def adapter_config() -> AdapterConfig:
    return AdapterConfig()

@container.provider
def adapter_client(config: AdapterConfig = Provide[adapter_config]) -> AdapterClient:
    return AdapterClient(config)
```

---

## 🧪 **Testing Patterns**

### **Unit Test Example**

```python
@pytest.mark.asyncio
async def test_entity_activation():
    """Test entity activation business logic."""
    # Arrange
    entity = AdapterEntity(
        id="test-1",
        name="Test Entity",
        status=EntityStatus.INACTIVE,
        created_at=datetime.utcnow()
    )

    # Act
    entity.activate()

    # Assert
    assert entity.status == EntityStatus.ACTIVE
    assert entity.updated_at is not None
```

### **Integration Test Example**

```python
@pytest.mark.asyncio
async def test_client_health_check(mock_server):
    """Test client health check integration."""
    # Arrange
    config = AdapterConfig(base_url=mock_server.url)
    client = AdapterClient(config)

    # Act
    health = await client.health_check()

    # Assert
    assert health.status == HealthStatus.HEALTHY
```

---

## 🔗 **Cross-References**

### **Component Documentation**

- [Component Overview](../README.md) - Complete component documentation
- [Configuration Guide](../docs/configuration.md) - Setup and configuration
- [API Reference](../docs/api/README.md) - Complete API documentation

### **Framework Integration**

- [FLX Core](../../flx/README.md) - Framework foundation
- [FLX Plugin System](../../flx/docs/plugins.md) - Plugin development
- [Hexagonal Architecture](../../docs/architecture/hexagonal.md) - Architecture patterns

---

**📂 Module**: Source Implementation | **🏠 Component**: [FLX Adapter Example](../README.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-19
