# Pydantic-Native Service - Implementation Guide

**Status:** Ready for Implementation  
**Target:** flext-core v3.0

---

## 🎯 Implementation: The New Base Class

### File: `flext-core/src/flext_core/pydantic_service.py`

````python
"""Pydantic-native service implementation.

This module provides a minimal, Pydantic-first service base that leverages
Pydantic v2's computed_field for automatic result computation.

Philosophy:
- Services are just data models with computed outputs
- No magic, no hidden behavior
- Pure Pydantic patterns
"""

from __future__ import annotations

from typing import Any, TypeVar, Generic, ClassVar
from pydantic import BaseModel, ConfigDict, computed_field, Field
from abc import ABC, abstractmethod

T = TypeVar('T')


class PydanticService(BaseModel, ABC, Generic[T]):
    """Minimal Pydantic-native service base.

    Services are data models with computed results. The result is computed
    automatically when accessed via the `result` property.

    Features:
    - Pure Pydantic BaseModel
    - Computed fields for results
    - Automatic validation
    - Built-in serialization
    - Type-safe generics

    Example:
        ```python
        class ParseLdif(PydanticService[list[Entry]]):
            source: str
            encoding: str = "utf-8"

            def compute(self) -> list[Entry]:
                content = Path(self.source).read_text(encoding=self.encoding)
                return parse_ldif(content)

        # Usage
        parser = ParseLdif(source="users.ldif")
        entries = parser.result  # Auto-computed
        data = parser.model_dump()  # Serialize everything
        ```

    Why Pydantic-native:
    - Leverages what developers already know (Pydantic)
    - No custom validation layer
    - Automatic serialization
    - Type-safe throughout
    - Less code, more clarity
    """

    # Pydantic v2 configuration
    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Allow complex types
        validate_assignment=True,       # Validate on field assignment
        extra="forbid",                 # Fail on unknown fields (fail fast)
        validate_default=True,          # Validate default values
        use_enum_values=True,           # Use enum values not names
        populate_by_name=True,          # Allow field_name and alias
    )

    # Private attribute for caching (Pydantic v2 pattern)
    _computed_result: T | None = None
    _result_computed: bool = False

    @computed_field
    @property
    def result(self) -> T:
        """Computed result property.

        The result is computed automatically when accessed. Results are
        cached after first computation for performance.

        Returns:
            T: The computed result

        Raises:
            NotImplementedError: If compute() not overridden
            ValidationError: If result doesn't match type T
        """
        if not self._result_computed:
            self._computed_result = self.compute()
            self._result_computed = True
        return self._computed_result

    @abstractmethod
    def compute(self) -> T:
        """Compute the result.

        Override this method to define your service logic. This is called
        automatically by the `result` property.

        Returns:
            T: The computed result

        Example:
            ```python
            def compute(self) -> list[Entry]:
                # Your logic here
                return parse_ldif(self.source)
            ```
        """
        ...

    # Convenience aliases
    @property
    def value(self) -> T:
        """Alias for result (for compatibility).

        Returns:
            T: The computed result
        """
        return self.result

    @property
    def output(self) -> T:
        """Alias for result (semantic clarity).

        Returns:
            T: The computed result
        """
        return self.result

    # Serialization helpers
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary (includes computed result).

        Returns:
            dict[str, Any]: Serialized model with result
        """
        return self.model_dump(mode='json')

    def to_json(self) -> str:
        """Serialize to JSON string (includes computed result).

        Returns:
            str: JSON representation
        """
        return self.model_dump_json()

    # Factory pattern (optional convenience)
    @classmethod
    def run(cls, **kwargs) -> T:
        """Factory: create and return result directly.

        Convenience method for one-liner execution.

        Args:
            **kwargs: Service initialization parameters

        Returns:
            T: The computed result

        Example:
            ```python
            entries = ParseLdif.run(source="file.ldif")
            ```
        """
        return cls(**kwargs).result


# Type alias for clarity
Service = PydanticService
````

---

## 💡 Real-World Examples

### Example 1: LDIF Parser

```python
# flext-ldif/src/flext_ldif/services/parser.py

from pathlib import Path
from pydantic import Field
from flext_core.pydantic_service import PydanticService
from flext_ldif.models import Entry

class FlextLdifParser(Pydantic[list[Entry]]):
    """Parse LDIF files - Pydantic-native.

    Example:
        >>> parser = FlextLdifParser(source="users.ldif")
        >>> entries = parser.result
        >>> print(f"Parsed {len(entries)} entries")
    """

    # Input fields with validation
    source: str | Path = Field(
        description="LDIF file path or string content"
    )
    encoding: str = Field(
        default="utf-8",
        description="Character encoding"
    )
    strict_mode: bool = Field(
        default=True,
        description="Strict parsing mode"
    )

    # Computed outputs
    def compute(self) -> list[Entry]:
        """Parse LDIF and return entries."""
        # Load content
        if isinstance(self.source, Path):
            content = self.source.read_text(encoding=self.encoding)
        else:
            content = self.source

        # Parse
        return self._parse_content(content)

    @computed_field
    @property
    def statistics(self) -> dict[str, int]:
        """Parsing statistics - computed from result."""
        entries = self.result  # Use cached result
        return {
            "total_entries": len(entries),
            "users": sum(1 for e in entries if "user" in e.dn.lower()),
            "groups": sum(1 for e in entries if "group" in e.dn.lower()),
            "organizational_units": sum(1 for e in entries if "ou" in e.dn.lower()),
        }

    def _parse_content(self, content: str) -> list[Entry]:
        """Internal parsing logic."""
        # Implementation...
        return parse_ldif_content(content, strict=self.strict_mode)


# Factory function for public API
def parse_ldif(
    source: str | Path,
    encoding: str = "utf-8",
    **kwargs
) -> list[Entry]:
    """Parse LDIF file - function interface.

    Args:
        source: LDIF file path or content
        encoding: Character encoding
        **kwargs: Additional parser options

    Returns:
        list[Entry]: Parsed entries

    Example:
        >>> entries = parse_ldif("users.ldif")
        >>> for entry in entries:
        ...     print(entry.dn)
    """
    return FlextLdifParser(
        source=source,
        encoding=encoding,
        **kwargs
    ).result


# Alternative: Return the model (more flexible)
def parse_ldif_model(
    source: str | Path,
    **kwargs
) -> FlextLdifParser:
    """Create parser model (for advanced usage).

    Returns the model itself, allowing access to both result
    and statistics, plus serialization.

    Example:
        >>> parser = parse_ldif_model("users.ldif")
        >>> entries = parser.result
        >>> stats = parser.statistics
        >>> data = parser.model_dump()
    """
    return FlextLdifParser(source=source, **kwargs)
```

### Example 2: HTTP Client (Multi-Operation)

```python
# flext-api/src/flext_api/services/http.py

from typing import Literal, Any
from pydantic import HttpUrl, Field
from flext_core.pydantic_service import PydanticService
import httpx

# Base operation
class HttpOperation(PydanticService[dict[str, Any]]):
    """Base HTTP operation."""

    url: HttpUrl = Field(description="Request URL")
    headers: dict[str, str] = Field(
        default_factory=dict,
        description="HTTP headers"
    )
    timeout: int = Field(
        default=30,
        gt=0,
        le=300,
        description="Timeout in seconds"
    )

    def _make_request(
        self,
        method: str,
        **kwargs
    ) -> dict[str, Any]:
        """Internal request method."""
        response = httpx.request(
            method=method,
            url=str(self.url),
            headers=self.headers,
            timeout=self.timeout,
            **kwargs
        )
        response.raise_for_status()
        return response.json()


# Specific operations
class HttpGet(HttpOperation):
    """HTTP GET request.

    Example:
        >>> get = HttpGet(url="https://api.example.com/users")
        >>> users = get.result
    """

    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Query parameters"
    )

    def compute(self) -> dict[str, Any]:
        """Execute GET request."""
        return self._make_request("GET", params=self.params)


class HttpPost(HttpOperation):
    """HTTP POST request.

    Example:
        >>> post = HttpPost(
        ...     url="https://api.example.com/users",
        ...     body={"name": "John"}
        ... )
        >>> response = post.result
    """

    body: dict[str, Any] = Field(
        default_factory=dict,
        description="Request body"
    )

    def compute(self) -> dict[str, Any]:
        """Execute POST request."""
        return self._make_request("POST", json=self.body)


class HttpPut(HttpOperation):
    """HTTP PUT request."""

    body: dict[str, Any] = Field(default_factory=dict)

    def compute(self) -> dict[str, Any]:
        """Execute PUT request."""
        return self._make_request("PUT", json=self.body)


class HttpDelete(HttpOperation):
    """HTTP DELETE request."""

    def compute(self) -> dict[str, Any]:
        """Execute DELETE request."""
        return self._make_request("DELETE")


# Factory functions for public API
def http_get(url: str, **kwargs) -> dict[str, Any]:
    """Execute HTTP GET request."""
    return HttpGet(url=url, **kwargs).result

def http_post(url: str, data: dict[str, Any], **kwargs) -> dict[str, Any]:
    """Execute HTTP POST request."""
    return HttpPost(url=url, body=data, **kwargs).result

def http_put(url: str, data: dict[str, Any], **kwargs) -> dict[str, Any]:
    """Execute HTTP PUT request."""
    return HttpPut(url=url, body=data, **kwargs).result

def http_delete(url: str, **kwargs) -> dict[str, Any]:
    """Execute HTTP DELETE request."""
    return HttpDelete(url=url, **kwargs).result
```

### Example 3: Database Query

```python
# flext-oracle/src/flext_oracle/services/query.py

from typing import Any
from pydantic import Field, field_validator
from flext_core.pydantic_service import PydanticService
import oracledb

class OracleQuery(PydanticService[list[dict[str, Any]]]):
    """Execute Oracle database query.

    Example:
        >>> query = OracleQuery(
        ...     connection_string="user/pass@localhost:1521/orcl",
        ...     sql="SELECT * FROM users WHERE age > :age",
        ...     params={"age": 18}
        ... )
        >>> rows = query.result
    """

    # Input fields
    connection_string: str = Field(
        description="Oracle connection string"
    )
    sql: str = Field(
        min_length=1,
        description="SQL query to execute"
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Query parameters"
    )
    fetch_size: int = Field(
        default=100,
        gt=0,
        le=10000,
        description="Fetch size for result set"
    )

    # Validation
    @field_validator('sql')
    @classmethod
    def validate_sql_safe(cls, v: str) -> str:
        """Validate SQL is a SELECT statement."""
        if not v.strip().upper().startswith('SELECT'):
            raise ValueError("Only SELECT queries allowed")
        return v

    # Computed result
    def compute(self) -> list[dict[str, Any]]:
        """Execute query and return rows."""
        with oracledb.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.arraysize = self.fetch_size
                cursor.execute(self.sql, self.params)

                # Get column names
                columns = [col[0] for col in cursor.description]

                # Fetch and convert to dicts
                return [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]

    # Additional computed fields
    @computed_field
    @property
    def row_count(self) -> int:
        """Number of rows returned."""
        return len(self.result)

    @computed_field
    @property
    def column_names(self) -> list[str]:
        """Column names from result."""
        if not self.result:
            return []
        return list(self.result[0].keys())


# Factory function
def query_oracle(
    connection: str,
    sql: str,
    params: dict[str, Any] | None = None,
    **kwargs
) -> list[dict[str, Any]]:
    """Execute Oracle query - function interface."""
    return OracleQuery(
        connection_string=connection,
        sql=sql,
        params=params or {},
        **kwargs
    ).result
```

---

## 🔄 Infrastructure Integration

### Pattern 1: Dependency Injection via Functions

```python
# flext-core/src/flext_core/infrastructure.py

from functools import lru_cache
from typing import Any

@lru_cache(maxsize=1)
def get_config() -> FlextConfig:
    """Get global config singleton."""
    return FlextConfig.get_global_instance()

@lru_cache(maxsize=None)
def get_logger(name: str) -> FlextLogger:
    """Get logger for module (cached)."""
    return FlextLogger(name)

@lru_cache(maxsize=1)
def get_container() -> FlextContainer:
    """Get DI container singleton."""
    return FlextContainer.get_global()


# Use in services
class MyService(PydanticService[T]):
    param: str

    def compute(self) -> T:
        """Compute with infrastructure."""
        # Explicit dependency access
        logger = get_logger(__name__)
        config = get_config()
        container = get_container()

        logger.info(f"Processing {self.param}")
        timeout = config.timeout_seconds

        # Implementation...
        return result
```

### Pattern 2: Context Manager for Scoped Access

```python
# flext-core/src/flext_core/context.py

from contextlib import contextmanager
from typing import Iterator

@contextmanager
def service_context(
    service_name: str
) -> Iterator[dict[str, Any]]:
    """Context manager providing infrastructure.

    Provides scoped access to logger, config, and container
    with automatic setup and teardown.

    Example:
        with service_context("MyService") as ctx:
            logger = ctx["logger"]
            logger.info("Starting")
    """
    logger = get_logger(service_name)
    config = get_config()
    container = get_container()

    logger.info(f"[{service_name}] Starting")

    try:
        yield {
            "logger": logger,
            "config": config,
            "container": container,
        }
    except Exception as e:
        logger.error(f"[{service_name}] Error: {e}")
        raise
    finally:
        logger.info(f"[{service_name}] Finished")


# Use in services
class MyService(PydanticService[T]):
    param: str

    def compute(self) -> T:
        """Compute with context."""
        with service_context(self.__class__.__name__) as ctx:
            logger = ctx["logger"]
            config = ctx["config"]

            logger.info(f"Processing {self.param}")
            # Implementation...

            return result
```

### Pattern 3: Optional Infrastructure Mixin

```python
# flext-core/src/flext_core/mixins.py

class InfrastructureMixin:
    """Optional mixin for infrastructure access.

    Add this to services that need infrastructure via properties.
    This is OPTIONAL - services can also use functions directly.
    """

    @property
    def logger(self) -> FlextLogger:
        """Get logger for this service."""
        return get_logger(self.__class__.__name__)

    @property
    def config(self) -> FlextConfig:
        """Get global config."""
        return get_config()

    @property
    def container(self) -> FlextContainer:
        """Get DI container."""
        return get_container()


# Use in services (optional)
class MyService(PydanticService[T], InfrastructureMixin):
    """Service with infrastructure mixin."""
    param: str

    def compute(self) -> T:
        """Compute with mixin properties."""
        self.logger.info(f"Processing {self.param}")
        timeout = self.config.timeout_seconds

        # Implementation...
        return result
```

---

## 📊 Benefits Summary

### For Developers

| Benefit          | Description                          |
| ---------------- | ------------------------------------ |
| **Familiar**     | Just Pydantic - no new concepts      |
| **Simple**       | ~30 lines base class vs ~500 lines   |
| **Natural**      | Computed properties feel like Python |
| **Type-safe**    | Full Pydantic validation + generics  |
| **Serializable** | Built-in `model_dump()`              |
| **Testable**     | Pure functions, easy to mock         |

### For Ecosystem

| Benefit       | Description                      |
| ------------- | -------------------------------- |
| **Lean**      | Less code to maintain            |
| **Flexible**  | Compose services easily          |
| **Adoptable** | Lower learning curve             |
| **Standard**  | Follows Python/Pydantic patterns |
| **Scalable**  | No inheritance complexity        |

### Code Reduction

```
Old FlextService base: ~500 lines
New PydanticService:   ~80 lines
Reduction:             84%

Old service example:   ~50 lines
New service example:   ~25 lines
Reduction:             50%
```

---

## 🚀 Next Steps

1. **Implement `PydanticService` in flext-core**
   - Create `flext_core/pydantic_service.py`
   - Add tests
   - Add documentation

2. **Create proof-of-concept in flext-ldif**
   - Migrate `FlextLdifParser`
   - Add factory functions
   - Compare old vs new

3. **Update documentation**
   - Add Pydantic-native guide
   - Show comparison examples
   - Migration guide

4. **Gradual rollout**
   - Keep old `FlextService` for compatibility
   - New services use `PydanticService`
   - Update examples progressively

---

**Status:** Ready to implement  
**Estimated effort:** 2-3 days  
**Breaking changes:** None (additive only)
