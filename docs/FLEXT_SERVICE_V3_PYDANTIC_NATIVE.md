# FlextService v3.0 - Pydantic-Native Architecture

**Version:** 3.0  
**Philosophy:** "Just Pydantic with Results"  
**Date:** October 31, 2025

---

## 🎯 Core Insight: Services ARE Pydantic Models

### The Breakthrough

```python
# ❌ OLD WAY: Services trying to be something special
class MyService(ComplexBaseClass):
    def __init__(self, param1, param2, config, logger, container):
        # So much ceremony...
        
# ✅ NEW WAY: Services are just Pydantic models that compute results
class MyService(BaseModel):
    # Input fields
    param1: str
    param2: int
    
    # Computed output (Pydantic v2 computed_field)
    @computed_field
    @property
    def result(self) -> dict[str, Any]:
        """Computed result - executes automatically."""
        return {"status": "success", "value": self.param1 * self.param2}

# Usage - pure Pydantic!
service = MyService(param1="hello", param2=3)
print(service.result)  # Auto-computed!
print(service.model_dump())  # Serializes with result!
```

**Key Insight:** Services don't need special base classes. They're just **data with computed properties**.

---

## 🏗️ Ultra-Lean Architecture

### Layer 0: Pure Pydantic

```python
from pydantic import BaseModel, computed_field, Field
from typing import Annotated

class FlextService(BaseModel):
    """Minimal service base - just Pydantic + Result pattern.
    
    Philosophy:
    - Services are data models with computed results
    - Use Pydantic v2 computed_field for execution
    - No magic, no ceremony, just functions
    """
    
    # Pydantic v2 config
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra="forbid",  # Fail fast on typos
        frozen=False,    # Allow mutation if needed
    )
    
    # Optional: Infrastructure injection via class vars
    _config: ClassVar[FlextConfig | None] = None
    _container: ClassVar[FlextContainer | None] = None
    _logger: ClassVar[FlextLogger | None] = None
    
    @computed_field
    @property
    def result(self) -> FlextResult[Any]:
        """Computed result - override in subclasses."""
        return self.execute()
    
    def execute(self) -> FlextResult[Any]:
        """Override this in subclasses."""
        raise NotImplementedError
    
    # Convenience: Direct value access
    @property
    def value(self) -> Any:
        """Get result value (raises on error)."""
        return self.result.unwrap()
    
    # Pydantic v2 serialization includes computed fields
    def to_dict(self) -> dict[str, Any]:
        """Serialize with result."""
        return self.model_dump(mode='json')
```

**What Changed:**
- ✅ Pure Pydantic BaseModel (no complex inheritance)
- ✅ `computed_field` for lazy result
- ✅ ClassVar for optional infrastructure
- ✅ Pydantic v2 serialization
- ✅ Zero magic

---

## 💡 Pydantic v2 Best Patterns

### Pattern 1: Computed Results (No Manual Execution)

```python
class ParseLdif(BaseModel):
    """Parser as pure Pydantic model."""
    
    # Input fields
    source: Annotated[str | Path, Field(description="LDIF source")]
    encoding: str = "utf-8"
    
    # Computed result - automatic!
    @computed_field
    @property
    def entries(self) -> list[Entry]:
        """Parsed entries - computed automatically."""
        # This runs when accessed, not at construction
        content = self._load_source()
        return self._parse_content(content)
    
    @computed_field
    @property
    def statistics(self) -> dict[str, int]:
        """Statistics - computed from entries."""
        return {
            "total": len(self.entries),
            "users": sum(1 for e in self.entries if "user" in e.dn),
        }
    
    # Private helpers
    def _load_source(self) -> str:
        if isinstance(self.source, Path):
            return self.source.read_text(encoding=self.encoding)
        return self.source
    
    def _parse_content(self, content: str) -> list[Entry]:
        # Parsing logic...
        return parse_ldif_content(content)

# Usage - pure Pydantic!
parser = ParseLdif(source="users.ldif")
print(parser.entries)  # Auto-computed on first access
print(parser.statistics)  # Auto-computed from entries
print(parser.model_dump())  # Serializes everything!
```

**Benefits:**
- ✅ No `.execute()` call needed
- ✅ Results are properties (natural)
- ✅ Automatic serialization
- ✅ Pydantic validation on input
- ✅ Type-safe throughout

### Pattern 2: Discriminated Unions (Multi-Operation)

```python
from typing import Literal
from pydantic import Field, Discriminator

# Base operation
class HttpOperation(BaseModel):
    """Base HTTP operation."""
    url: HttpUrl
    headers: dict[str, str] = Field(default_factory=dict)
    timeout: int = 30

# Specific operations
class HttpGet(HttpOperation):
    """GET operation."""
    operation: Literal["get"] = "get"
    
    @computed_field
    @property
    def response(self) -> dict[str, Any]:
        """Execute GET."""
        return httpx.get(
            str(self.url),
            headers=self.headers,
            timeout=self.timeout
        ).json()

class HttpPost(HttpOperation):
    """POST operation."""
    operation: Literal["post"] = "post"
    body: dict[str, Any] = Field(default_factory=dict)
    
    @computed_field
    @property
    def response(self) -> dict[str, Any]:
        """Execute POST."""
        return httpx.post(
            str(self.url),
            json=self.body,
            headers=self.headers,
            timeout=self.timeout
        ).json()

# Union with discriminator
HttpRequest = Annotated[
    HttpGet | HttpPost,
    Discriminator("operation")
]

def http(request: HttpRequest) -> dict[str, Any]:
    """Execute any HTTP request."""
    return request.response

# Usage - Pydantic discriminates automatically!
get_req = HttpGet(url="https://api.example.com/users")
print(get_req.response)  # GET executed

post_req = HttpPost(
    url="https://api.example.com/users",
    body={"name": "John"}
)
print(post_req.response)  # POST executed
```

**Benefits:**
- ✅ Type-safe discrimination
- ✅ Each operation is independent model
- ✅ Pydantic handles routing
- ✅ Clear, separate classes

### Pattern 3: Field Validators (Not Custom Validation)

```python
class CreateUser(BaseModel):
    """User creation with Pydantic validation."""
    
    # Annotated types for complex validation
    email: Annotated[
        str,
        Field(
            pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$',
            examples=["user@example.com"]
        )
    ]
    
    age: Annotated[
        int,
        Field(gt=0, le=150, description="Age in years")
    ]
    
    username: Annotated[
        str,
        Field(min_length=3, max_length=20, pattern=r'^[a-z0-9_]+$')
    ]
    
    # Field validators
    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        return v.lower().strip()
    
    @field_validator('username')
    @classmethod
    def check_username_available(cls, v: str) -> str:
        """Check username availability."""
        if is_username_taken(v):
            raise ValueError(f"Username '{v}' already taken")
        return v
    
    # Model validators
    @model_validator(mode='after')
    def validate_age_username(self) -> Self:
        """Cross-field validation."""
        if self.age < 13 and not self.username.endswith("_kid"):
            raise ValueError("Usernames for users under 13 must end with '_kid'")
        return self
    
    # Computed result
    @computed_field
    @property
    def user(self) -> User:
        """Create user - computed after validation."""
        return User(
            email=self.email,
            age=self.age,
            username=self.username
        )

# Usage
service = CreateUser(
    email="JOHN@EXAMPLE.COM",  # Will be normalized
    age=25,
    username="john_doe"
)
user = service.user  # Already validated!
```

**Benefits:**
- ✅ Pydantic does validation
- ✅ Clear error messages
- ✅ No custom validation layer
- ✅ Type-safe

### Pattern 4: Model Composition (Not Inheritance)

```python
# Composition over inheritance
class DatabaseConfig(BaseModel):
    """Database configuration."""
    host: str
    port: int = 5432
    database: str
    username: str
    password: SecretStr

class QueryConfig(BaseModel):
    """Query execution configuration."""
    timeout: int = 30
    max_rows: int = 1000
    fetch_size: int = 100

class DatabaseQuery(BaseModel):
    """Database query with composed configs."""
    
    # Composition!
    db_config: DatabaseConfig
    query_config: QueryConfig = Field(default_factory=QueryConfig)
    
    # Query parameters
    sql: str
    params: dict[str, Any] = Field(default_factory=dict)
    
    @computed_field
    @property
    def results(self) -> list[dict[str, Any]]:
        """Execute query - computed."""
        conn = create_connection(self.db_config)
        cursor = conn.cursor()
        cursor.execute(self.sql, self.params)
        return cursor.fetchall()

# Usage - compose at call site
query = DatabaseQuery(
    db_config=DatabaseConfig(
        host="localhost",
        database="users",
        username="REDACTED_LDAP_BIND_PASSWORD",
        password="secret"
    ),
    sql="SELECT * FROM users WHERE age > :age",
    params={"age": 18}
)
results = query.results
```

**Benefits:**
- ✅ Explicit composition
- ✅ Reusable configs
- ✅ Type-safe
- ✅ No inheritance complexity

### Pattern 5: Factory Functions Return Models

```python
# Factory functions for ergonomics
def parse_ldif(source: str | Path, **kwargs) -> ParseLdif:
    """Factory: Create parser model.
    
    Returns the MODEL, not the result.
    User decides what to access.
    """
    return ParseLdif(source=source, **kwargs)

def query_db(sql: str, **kwargs) -> DatabaseQuery:
    """Factory: Create query model."""
    return DatabaseQuery(sql=sql, **kwargs)

# Usage - natural!
parser = parse_ldif("users.ldif")
entries = parser.entries  # Computed
stats = parser.statistics  # Computed
json_data = parser.model_dump()  # Serialize

# Or direct
entries = parse_ldif("users.ldif").entries

# Or serialize
data = parse_ldif("users.ldif").model_dump()
```

**Benefits:**
- ✅ Returns model (more flexible)
- ✅ User controls access
- ✅ Can serialize
- ✅ Natural Python

---

## 🔥 Radical Simplification: Remove FlextService Base

### Current Problem

```python
# Too much inheritance
class MyService(FlextService[T]):
    class FlextService(FlextModels.ArbitraryTypesModel, FlextMixins):
        class FlextMixins(...):
            class FlextModels.ArbitraryTypesModel(BaseModel):
                # 4 levels of inheritance!
```

### New Approach: Pure Pydantic

```python
# Just Pydantic!
from pydantic import BaseModel, computed_field

class MyService(BaseModel):
    """Pure Pydantic model with computed result."""
    
    # Inputs
    param1: str
    param2: int
    
    # Computed result
    @computed_field
    @property
    def result(self) -> dict[str, Any]:
        """Computed result."""
        return {"value": self.param1 * self.param2}

# That's it!
```

### Infrastructure as Functions, Not Mixins

```python
# ❌ OLD: Infrastructure via mixins
class MyService(FlextService):
    def execute(self):
        self.logger.info("Starting")  # From mixin
        config = self.project_config  # From mixin
        
# ✅ NEW: Infrastructure via functions
from flext_core import get_logger, get_config, get_container

class MyService(BaseModel):
    param: str
    
    @computed_field
    @property
    def result(self) -> Any:
        """Computed with infrastructure."""
        logger = get_logger(__name__)  # Function!
        config = get_config()  # Function!
        
        logger.info(f"Processing {self.param}")
        timeout = config.timeout_seconds
        
        return self._process(timeout)

# Even better: Dependency injection via function params
def process_with_logger(
    service: MyService,
    logger: FlextLogger = Depends(get_logger),
    config: FlextConfig = Depends(get_config)
) -> Any:
    """Process with injected dependencies."""
    logger.info(f"Processing {service.param}")
    return service.result
```

---

## 🎨 The New FlextService (Minimal)

```python
# flext-core/src/flext_core/service.py

from pydantic import BaseModel, ConfigDict, computed_field
from typing import Any, ClassVar

class FlextService(BaseModel):
    """Minimal Pydantic-based service.
    
    Services are just data models with computed results.
    Override the `compute()` method to define your logic.
    
    Example:
        class ParseLdif(FlextService):
            source: str
            
            def compute(self) -> list[Entry]:
                return parse(self.source)
        
        # Usage
        parser = ParseLdif(source="file.ldif")
        entries = parser.result  # Computed automatically
    """
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra="forbid",
    )
    
    @computed_field
    @property
    def result(self) -> Any:
        """Computed result (override compute())."""
        return self.compute()
    
    def compute(self) -> Any:
        """Override this to define your computation.
        
        This is called by the `result` property.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.compute() not implemented"
        )
    
    # Convenience
    @property
    def value(self) -> Any:
        """Alias for result (for compatibility)."""
        return self.result

# That's the ENTIRE base class!
```

### Example Services

```python
# Parse LDIF
class ParseLdif(FlextService):
    """Parse LDIF file."""
    source: str | Path
    encoding: str = "utf-8"
    
    def compute(self) -> list[Entry]:
        """Parse and return entries."""
        content = Path(self.source).read_text(encoding=self.encoding)
        return parse_ldif(content)

# HTTP Request
class HttpGet(FlextService):
    """HTTP GET request."""
    url: HttpUrl
    headers: dict[str, str] = Field(default_factory=dict)
    
    def compute(self) -> dict[str, Any]:
        """Execute GET."""
        return httpx.get(str(self.url), headers=self.headers).json()

# Database Query
class QueryDatabase(FlextService):
    """Database query."""
    connection_string: str
    sql: str
    params: dict[str, Any] = Field(default_factory=dict)
    
    def compute(self) -> list[dict[str, Any]]:
        """Execute query."""
        with create_connection(self.connection_string) as conn:
            return conn.execute(self.sql, self.params).fetchall()

# Usage - all the same pattern!
entries = ParseLdif(source="file.ldif").result
data = HttpGet(url="https://api.example.com/users").result
rows = QueryDatabase(
    connection_string="postgresql://...",
    sql="SELECT * FROM users"
).result
```

---

## 🚀 Infrastructure Pattern: Context Managers

```python
# Instead of mixins, use context managers!

from contextlib import contextmanager

@contextmanager
def flext_context(service_name: str):
    """Context manager for infrastructure.
    
    Provides logger, config, container in context.
    """
    logger = get_logger(service_name)
    config = get_config()
    container = get_container()
    
    logger.info(f"Starting {service_name}")
    
    try:
        yield {
            "logger": logger,
            "config": config,
            "container": container,
        }
    finally:
        logger.info(f"Finished {service_name}")

# Usage
class MyService(FlextService):
    param: str
    
    def compute(self) -> Any:
        """Compute with infrastructure context."""
        with flext_context(self.__class__.__name__) as ctx:
            logger = ctx["logger"]
            config = ctx["config"]
            
            logger.info(f"Processing {self.param}")
            return self._process(config.timeout_seconds)
```

---

## 📊 Comparison: Old vs New

| Aspect | Old (FlextService v2) | New (Pydantic-Native) |
|--------|----------------------|----------------------|
| **Base class** | Complex (4-level inheritance) | Simple (BaseModel only) |
| **Execution** | `.execute().unwrap()` | `.result` property |
| **Infrastructure** | Mixins (hidden magic) | Functions/context managers (explicit) |
| **Validation** | Custom + Pydantic | Pure Pydantic v2 |
| **Serialization** | Custom `to_dict()` | Pydantic `model_dump()` |
| **Multi-operation** | `match` statement in execute | Discriminated unions |
| **Error handling** | FlextResult wrapper | Pydantic ValidationError |
| **Lines of code** | ~500 (base class) | ~30 (base class) |
| **Concepts to learn** | 10+ (service, handler, dispatcher, etc.) | 2 (BaseModel, computed_field) |

---

## ✅ Migration Strategy

### Phase 1: Add Pydantic-Native Option

```python
# Keep old FlextService for compatibility
# Add new PydanticService

from flext_core.service import FlextService  # Old
from flext_core.pydantic_service import PydanticService  # New

# Developers can choose
```

### Phase 2: Show Both Patterns in Docs

```python
# Old pattern (still works)
class OldStyle(FlextService[list[Entry]]):
    source: str
    
    def execute(self) -> FlextResult[list[Entry]]:
        return FlextResult.ok(parse(self.source))

# New pattern (recommended)
class NewStyle(PydanticService):
    source: str
    
    def compute(self) -> list[Entry]:
        return parse(self.source)
```

### Phase 3: Gradual Migration

- New services use Pydantic-native
- Old services keep working
- Update docs to show new pattern first

---

## 🎯 Final Architecture

```
┌─────────────────────────────────────────────────────┐
│  USER CODE                                          │
│  ─────────────────────────────────────────────────  │
│  # Pure Pydantic!                                   │
│  parser = ParseLdif(source="file.ldif")            │
│  entries = parser.result  # Computed property      │
│  data = parser.model_dump()  # Serialize           │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  SERVICES (Just Pydantic Models)                    │
│  ─────────────────────────────────────────────────  │
│  class ParseLdif(BaseModel):                        │
│      source: str  # Input fields                    │
│                                                      │
│      @computed_field                                │
│      @property                                      │
│      def result(self) -> list[Entry]:               │
│          return self.compute()                      │
│                                                      │
│      def compute(self) -> list[Entry]:              │
│          # Business logic                           │
│          return parse(self.source)                  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  INFRASTRUCTURE (Functions, not Mixins)             │
│  ─────────────────────────────────────────────────  │
│  def get_logger(name: str) -> FlextLogger           │
│  def get_config() -> FlextConfig                    │
│  def get_container() -> FlextContainer              │
│                                                      │
│  @contextmanager                                    │
│  def flext_context(name: str):                      │
│      yield {"logger": ..., "config": ...}           │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  FOUNDATION                                         │
│  ─────────────────────────────────────────────────  │
│  • Pydantic BaseModel                               │
│  • Python typing                                    │
│  • Standard library                                 │
│  • That's it!                                       │
└─────────────────────────────────────────────────────┘
```

---

## 🎓 Key Principles

1. **Services are data with computed outputs**
   - Not special classes
   - Just Pydantic models
   - Computation via `@computed_field`

2. **Infrastructure is explicit**
   - Functions, not mixins
   - Context managers for scoped access
   - No hidden magic

3. **Leverage Pydantic v2**
   - Field validators
   - Model validators
   - Computed fields
   - Discriminated unions
   - Serialization

4. **Composition over inheritance**
   - Compose models
   - Don't inherit complexity
   - Single-level inheritance max

5. **Make it feel like standard Python**
   - If you know Pydantic, you know this
   - No new concepts
   - Natural patterns

---

**Next Steps:** Implement PydanticService base class and migrate one library (flext-ldif) as proof of concept.

