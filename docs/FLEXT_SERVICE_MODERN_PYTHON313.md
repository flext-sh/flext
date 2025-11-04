# FlextService - Modern Python 3.13 + Pydantic v2

**Version:** 3.0  
**Python:** 3.13+  
**Pydantic:** 2.0+  
**Philosophy:** "Zero Ceremony, Maximum Power"

---

## 🎯 The Goal: Eliminate ALL Boilerplate

### Current State (Too Much Ceremony)

```python
# ❌ TOO VERBOSE
service = ParseLdif(source="file.ldif")
result = service.execute()
if result.is_success:
    entries = result.unwrap()
```

### Target State (Zero Ceremony)

```python
# ✅ DIRECT ACCESS
entries = ParseLdif(source="file.ldif").value

# ✅ OR EVEN SIMPLER
entries = parse_ldif("file.ldif")
```

**Eliminate:**
- ❌ `.execute()` - automatic via property
- ❌ `.unwrap()` - automatic via property
- ❌ `.run()` - not needed
- ❌ `()` for calling - not needed
- ❌ Explicit error checking - optional

---

## 💡 The Solution: Enhanced FlextService Base

### File: `flext-core/src/flext_core/service.py`

```python
"""Modern FlextService with Python 3.13 + Pydantic v2.

Zero ceremony service pattern with automatic execution.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Self, TypeVar, Generic, override
from pydantic import BaseModel, computed_field, Field, PrivateAttr

from flext_core.models import FlextModels
from flext_core.mixins import FlextMixins
from flext_core.result import FlextResult

# Python 3.13 type parameter syntax
type ServiceResult[T] = FlextResult[T]

class FlextService[TResult](
    FlextModels.ArbitraryTypesModel,
    FlextMixins,
    ABC,
    Generic[TResult]
):
    """Modern service base with zero-ceremony execution.
    
    Features:
    - Automatic execution via computed properties
    - Direct value access (.value)
    - Safe value access (.value_or_none)
    - Full result access (.result)
    - Infrastructure via mixins (logger, config, container)
    - Pydantic v2 validation
    
    Example:
        ```python
        class ParseLdif(FlextService[list[Entry]]):
            source: str
            
            def execute(self) -> FlextResult[list[Entry]]:
                entries = parse(self.source)
                return FlextResult.ok(entries)
        
        # Zero ceremony usage!
        entries = ParseLdif(source="file.ldif").value
        ```
    
    Python 3.13 + Pydantic v2 optimizations:
    - Type parameter syntax for cleaner generics
    - computed_field for automatic execution
    - PrivateAttr for caching
    - Enhanced type hints
    """
    
    # Private cache (Pydantic v2 pattern)
    _cached_result: TResult | None = PrivateAttr(default=None)
    _is_executed: bool = PrivateAttr(default=False)
    
    @abstractmethod
    def execute(self) -> FlextResult[TResult]:
        """Execute service operation.
        
        Override this in subclasses. This is called automatically
        by the .result property on first access.
        
        Returns:
            FlextResult[TResult]: Result monad
        """
        ...
    
    # =========================================================================
    # ZERO CEREMONY PROPERTIES
    # =========================================================================
    
    @computed_field  # type: ignore[misc]
    @property
    def result(self) -> FlextResult[TResult]:
        """Get result (executes automatically, cached).
        
        This property executes the service on first access and caches
        the result for subsequent accesses.
        
        Returns:
            FlextResult[TResult]: Complete result with success/failure info
        
        Example:
            >>> service = ParseLdif(source="file.ldif")
            >>> result = service.result  # Executes here
            >>> if result.is_success:
            ...     print(result.value)
        """
        if not self._is_executed:
            self._cached_result = self.execute()
            self._is_executed = True
        return self._cached_result  # type: ignore[return-value]
    
    @property
    def value(self) -> TResult:
        """Get value directly (auto-execute + unwrap).
        
        Most common usage pattern. Executes the service and returns
        the value directly. Raises exception on failure.
        
        Returns:
            TResult: The actual result value
        
        Raises:
            FlextError: If execution failed
        
        Example:
            >>> entries = ParseLdif(source="file.ldif").value
            >>> print(f"Got {len(entries)} entries")
        """
        return self.result.unwrap()
    
    @property
    def value_or_none(self) -> TResult | None:
        """Get value or None on failure (auto-execute, safe).
        
        Safe access pattern. Never raises exceptions.
        
        Returns:
            TResult | None: Value if successful, None if failed
        
        Example:
            >>> entries = ParseLdif(source="file.ldif").value_or_none
            >>> if entries:
            ...     print(f"Success: {len(entries)}")
            ... else:
            ...     print("Parsing failed")
        """
        r = self.result
        return r.value if r.is_success else None
    
    def value_or(self, default: TResult) -> TResult:
        """Get value or default on failure.
        
        Args:
            default: Value to return on failure
        
        Returns:
            TResult: Value if successful, default if failed
        
        Example:
            >>> entries = ParseLdif(source="bad.ldif").value_or([])
            >>> print(f"Got {len(entries)} entries")  # Always works
        """
        r = self.result
        return r.value if r.is_success else default
    
    # =========================================================================
    # MONADIC OPERATIONS (Delegate to result)
    # =========================================================================
    
    def map[U](self, func: callable[[TResult], U]) -> FlextResult[U]:
        """Transform result value.
        
        Args:
            func: Transformation function
        
        Returns:
            FlextResult[U]: Transformed result
        
        Example:
            >>> result = (
            ...     ParseLdif(source="file.ldif")
            ...     .map(lambda entries: len(entries))
            ... )
            >>> print(result.value)  # Number of entries
        """
        return self.result.map(func)
    
    def and_then[U](
        self,
        func: callable[[TResult], FlextResult[U]]
    ) -> FlextResult[U]:
        """Chain operations (railway pattern).
        
        Args:
            func: Function returning another result
        
        Returns:
            FlextResult[U]: Chained result
        
        Example:
            >>> result = (
            ...     ParseLdif(source="input.ldif")
            ...     .and_then(lambda entries: WriteLdif(entries=entries).result)
            ... )
        """
        return self.result.and_then(func)
    
    def or_else(
        self,
        func: callable[[str], FlextResult[TResult]]
    ) -> FlextResult[TResult]:
        """Provide fallback on failure.
        
        Args:
            func: Function to call on error (receives error message)
        
        Returns:
            FlextResult[TResult]: Original result or fallback
        
        Example:
            >>> entries = (
            ...     ParseLdif(source="file.ldif")
            ...     .or_else(lambda err: FlextResult.ok([]))
            ...     .value
            ... )
        """
        return self.result.or_else(func)


# =========================================================================
# TYPE ALIASES (Python 3.13 style)
# =========================================================================

type Service[T] = FlextService[T]
type ServiceResult[T] = FlextResult[T]
```

---

## 🚀 Real Examples (Python 3.13 + Pydantic v2)

### Example 1: LDIF Parser (Zero Ceremony)

```python
# flext-ldif/src/flext_ldif/services/parser.py

from pathlib import Path
from typing import Annotated
from pydantic import Field, field_validator
from flext_core.service import FlextService, ServiceResult
from flext_ldif.models import Entry

class FlextLdifParserService(FlextService[list[Entry]]):
    """Parse LDIF files.
    
    Python 3.13 + Pydantic v2 optimized implementation.
    """
    
    # Annotated fields (Pydantic v2 pattern)
    source: Annotated[
        str | Path,
        Field(description="LDIF file path or string content")
    ]
    
    encoding: Annotated[
        str,
        Field(default="utf-8", description="Character encoding")
    ] = "utf-8"
    
    strict_mode: Annotated[
        bool,
        Field(default=True, description="Enable strict parsing")
    ] = True
    
    # Field validator (Pydantic v2)
    @field_validator('source')
    @classmethod
    def validate_source_exists(cls, v: str | Path) -> str | Path:
        """Validate source file exists."""
        if isinstance(v, Path) and not v.exists():
            raise ValueError(f"File not found: {v}")
        return v
    
    # Implementation
    def execute(self) -> ServiceResult[list[Entry]]:
        """Parse LDIF and return entries."""
        try:
            # Infrastructure from mixins (automatic!)
            self.logger.info(f"Parsing LDIF from {self.source}")
            
            # Config from auto-resolution (automatic!)
            max_entries = self.project_config.max_ldif_entries
            
            # Load and parse
            content = self._load_content()
            entries = self._parse_ldif(content)
            
            # Validation
            if len(entries) > max_entries:
                return FlextResult.fail(
                    f"Too many entries: {len(entries)} > {max_entries}"
                )
            
            self.logger.info(f"Parsed {len(entries)} entries")
            return FlextResult.ok(entries)
            
        except Exception as e:
            self.logger.error(f"Parse failed: {e}")
            return FlextResult.fail(str(e))
    
    def _load_content(self) -> str:
        """Load content from source."""
        match self.source:
            case Path() as path:
                return path.read_text(encoding=self.encoding)
            case str() as content:
                return content
    
    def _parse_ldif(self, content: str) -> list[Entry]:
        """Parse LDIF content."""
        # Implementation...
        return parse_ldif_content(content, strict=self.strict_mode)


# =========================================================================
# PUBLIC API - Factory Functions (Zero Ceremony)
# =========================================================================

def parse_ldif(
    source: str | Path,
    *,  # Force keyword args
    encoding: str = "utf-8",
    strict_mode: bool = True
) -> list[Entry]:
    """Parse LDIF file - zero ceremony interface.
    
    Args:
        source: LDIF file path or string content
        encoding: Character encoding (default: utf-8)
        strict_mode: Enable strict parsing (default: True)
    
    Returns:
        list[Entry]: Parsed LDIF entries
    
    Raises:
        FlextError: If parsing fails
    
    Example:
        >>> entries = parse_ldif("users.ldif")
        >>> for entry in entries:
        ...     print(entry.dn)
    
    Python 3.13 optimized:
    - Direct value return (no .value needed in function)
    - Keyword-only args for clarity
    - Type hints preserved
    """
    return FlextLdifParserService(
        source=source,
        encoding=encoding,
        strict_mode=strict_mode
    ).value  # Auto-executes + unwraps


def parse_ldif_safe(
    source: str | Path,
    **kwargs
) -> list[Entry] | None:
    """Parse LDIF file - safe interface (never raises).
    
    Returns None on failure instead of raising exception.
    
    Example:
        >>> entries = parse_ldif_safe("might_fail.ldif")
        >>> if entries:
        ...     print(f"Success: {len(entries)} entries")
        ... else:
        ...     print("Parsing failed")
    """
    return FlextLdifParserService(
        source=source,
        **kwargs
    ).value_or_none


# Export
__all__ = [
    # Functions (PRIMARY API)
    "parse_ldif",
    "parse_ldif_safe",
    # Service (for advanced usage)
    "FlextLdifParserService",
]
```

### Usage Examples (Zero Ceremony!)

```python
# ✅ PATTERN 1: Direct function call
entries = parse_ldif("users.ldif")

# ✅ PATTERN 2: Safe call (no exceptions)
entries = parse_ldif_safe("might_fail.ldif")
if entries:
    print(f"Got {len(entries)} entries")

# ✅ PATTERN 3: Direct service usage
entries = FlextLdifParserService(source="users.ldif").value

# ✅ PATTERN 4: With error details
result = FlextLdifParserService(source="users.ldif").result
if result.is_success:
    entries = result.value
else:
    print(f"Error: {result.error}")

# ✅ PATTERN 5: Functional composition
result = (
    FlextLdifParserService(source="input.ldif")
    .map(lambda entries: [e for e in entries if "user" in e.dn])
    .and_then(lambda filtered: 
        FlextLdifWriterService(entries=filtered, output_path="out.ldif").result
    )
)
```

---

### Example 2: HTTP Client (Multi-Operation)

```python
# flext-api/src/flext_api/services/http.py

from typing import Literal, Annotated, Any
from pydantic import HttpUrl, Field
from flext_core.service import FlextService, ServiceResult
import httpx

class FlextHttpClient(FlextService[dict[str, Any]]):
    """HTTP client with multiple operations.
    
    Python 3.13 + Pydantic v2 optimized.
    """
    
    # Multi-operation via Literal
    operation: Annotated[
        Literal["get", "post", "put", "delete", "patch"],
        Field(description="HTTP method")
    ]
    
    url: Annotated[
        HttpUrl,
        Field(description="Request URL")
    ]
    
    headers: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="HTTP headers")
    ] = Field(default_factory=dict)
    
    body: Annotated[
        dict[str, Any] | None,
        Field(default=None, description="Request body (POST/PUT/PATCH)")
    ] = None
    
    params: Annotated[
        dict[str, Any],
        Field(default_factory=dict, description="Query parameters")
    ] = Field(default_factory=dict)
    
    timeout: Annotated[
        int,
        Field(default=30, gt=0, le=300, description="Timeout in seconds")
    ] = 30
    
    def execute(self) -> ServiceResult[dict[str, Any]]:
        """Execute HTTP request."""
        try:
            # Python 3.13 match with better type inference
            match self.operation:
                case "get":
                    response = httpx.get(
                        str(self.url),
                        headers=self.headers,
                        params=self.params,
                        timeout=self.timeout
                    )
                case "post":
                    response = httpx.post(
                        str(self.url),
                        json=self.body,
                        headers=self.headers,
                        timeout=self.timeout
                    )
                case "put":
                    response = httpx.put(
                        str(self.url),
                        json=self.body,
                        headers=self.headers,
                        timeout=self.timeout
                    )
                case "delete":
                    response = httpx.delete(
                        str(self.url),
                        headers=self.headers,
                        timeout=self.timeout
                    )
                case "patch":
                    response = httpx.patch(
                        str(self.url),
                        json=self.body,
                        headers=self.headers,
                        timeout=self.timeout
                    )
            
            response.raise_for_status()
            return FlextResult.ok(response.json())
            
        except httpx.HTTPError as e:
            return FlextResult.fail(f"HTTP error: {e}")


# =========================================================================
# PUBLIC API - Zero Ceremony Functions
# =========================================================================

def http_get(url: str, *, params: dict[str, Any] | None = None, **kwargs) -> dict[str, Any]:
    """HTTP GET request."""
    return FlextHttpClient(
        operation="get",
        url=url,
        params=params or {},
        **kwargs
    ).value

def http_post(url: str, data: dict[str, Any], **kwargs) -> dict[str, Any]:
    """HTTP POST request."""
    return FlextHttpClient(
        operation="post",
        url=url,
        body=data,
        **kwargs
    ).value

def http_put(url: str, data: dict[str, Any], **kwargs) -> dict[str, Any]:
    """HTTP PUT request."""
    return FlextHttpClient(
        operation="put",
        url=url,
        body=data,
        **kwargs
    ).value

def http_delete(url: str, **kwargs) -> dict[str, Any]:
    """HTTP DELETE request."""
    return FlextHttpClient(
        operation="delete",
        url=url,
        **kwargs
    ).value


# Usage - Zero Ceremony!
users = http_get("https://api.example.com/users")
response = http_post("https://api.example.com/users", data={"name": "John"})
```

---

### Example 3: Database Query (Async Support)

```python
# flext-oracle/src/flext_oracle/services/query.py

from typing import Annotated, Any
from pydantic import Field, field_validator
from flext_core.service import FlextService, ServiceResult
import oracledb

class FlextOracleQuery(FlextService[list[dict[str, Any]]]):
    """Execute Oracle query.
    
    Python 3.13 + Pydantic v2 + Async support.
    """
    
    connection_string: Annotated[
        str,
        Field(description="Oracle connection string")
    ]
    
    sql: Annotated[
        str,
        Field(min_length=1, description="SQL query")
    ]
    
    params: Annotated[
        dict[str, Any],
        Field(default_factory=dict, description="Query parameters")
    ] = Field(default_factory=dict)
    
    @field_validator('sql')
    @classmethod
    def validate_select_only(cls, v: str) -> str:
        """Ensure only SELECT queries."""
        if not v.strip().upper().startswith('SELECT'):
            raise ValueError("Only SELECT queries allowed")
        return v
    
    def execute(self) -> ServiceResult[list[dict[str, Any]]]:
        """Execute query synchronously."""
        try:
            with oracledb.connect(self.connection_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(self.sql, self.params)
                    columns = [col[0] for col in cursor.description]
                    rows = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]
                    return FlextResult.ok(rows)
        except Exception as e:
            return FlextResult.fail(str(e))
    
    async def execute_async(self) -> ServiceResult[list[dict[str, Any]]]:
        """Execute query asynchronously."""
        try:
            async with await oracledb.connect_async(self.connection_string) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(self.sql, self.params)
                    columns = [col[0] for col in cursor.description]
                    rows = [
                        dict(zip(columns, row))
                        async for row in cursor
                    ]
                    return FlextResult.ok(rows)
        except Exception as e:
            return FlextResult.fail(str(e))


# Factory functions
def query_oracle(connection: str, sql: str, **kwargs) -> list[dict[str, Any]]:
    """Execute Oracle query."""
    return FlextOracleQuery(
        connection_string=connection,
        sql=sql,
        **kwargs
    ).value

async def query_oracle_async(connection: str, sql: str, **kwargs) -> list[dict[str, Any]]:
    """Execute Oracle query asynchronously."""
    service = FlextOracleQuery(
        connection_string=connection,
        sql=sql,
        **kwargs
    )
    result = await service.execute_async()
    return result.unwrap()


# Usage
rows = query_oracle(
    "user/pass@localhost/orcl",
    "SELECT * FROM users WHERE age > :age",
    params={"age": 18}
)

# Async usage
rows = await query_oracle_async(
    "user/pass@localhost/orcl",
    "SELECT * FROM users"
)
```

---

## 📊 Python 3.13 + Pydantic v2 Features Used

### 1. Type Parameter Syntax (PEP 695)

```python
# Python 3.13 syntax
class FlextService[TResult](...):
    def map[U](self, func: callable[[TResult], U]) -> FlextResult[U]:
        ...

# Instead of old syntax
class FlextService(Generic[TResult]):
    def map(self, func: Callable[[TResult], U]) -> FlextResult[U]:
        ...
```

### 2. Type Aliases (PEP 695)

```python
# Python 3.13
type ServiceResult[T] = FlextResult[T]
type Service[T] = FlextService[T]

# Usage
def my_func() -> ServiceResult[list[Entry]]:
    ...
```

### 3. Pydantic v2 Annotated Fields

```python
# Pydantic v2 pattern
source: Annotated[
    str | Path,
    Field(description="Source file")
]

# With defaults
encoding: Annotated[
    str,
    Field(default="utf-8")
] = "utf-8"
```

### 4. Pydantic v2 computed_field

```python
@computed_field  # type: ignore[misc]
@property
def result(self) -> FlextResult[TResult]:
    """Computed automatically on access."""
    return self.execute()
```

### 5. Pattern Matching (Python 3.10+, improved in 3.13)

```python
match self.operation:
    case "get":
        return self._http_get()
    case "post":
        return self._http_post()
```

### 6. Pydantic v2 PrivateAttr

```python
# Cache that's not serialized
_cached_result: TResult | None = PrivateAttr(default=None)
_is_executed: bool = PrivateAttr(default=False)
```

---

## ✅ Boilerplate Eliminated

### Before (Old Pattern)

```python
# 4 method calls!
service = ParseLdif(source="file.ldif")
result = service.execute()
if result.is_success:
    entries = result.unwrap()

# Or compressed but still verbose
entries = ParseLdif(source="file.ldif").execute().unwrap()
```

### After (Modern Pattern)

```python
# 1 property access!
entries = ParseLdif(source="file.ldif").value

# Or function (0 ceremony!)
entries = parse_ldif("file.ldif")
```

**Reduction:** 75% less code

---

## 🎯 Complete Working Example

```python
# flext-ldif/__init__.py

"""LDIF processing library - zero ceremony API.

Python 3.13 + Pydantic v2 optimized.
"""

from pathlib import Path
from flext_ldif.services.parser import (
    parse_ldif,
    parse_ldif_safe,
    FlextLdifParserService,
)
from flext_ldif.services.writer import (
    write_ldif,
    write_ldif_safe,
    FlextLdifWriterService,
)
from flext_ldif.models import Entry

# =========================================================================
# PRIMARY API - Zero Ceremony Functions
# =========================================================================

__all__ = [
    # Functions (PRIMARY - use these!)
    "parse_ldif",
    "parse_ldif_safe",
    "write_ldif",
    "write_ldif_safe",
    # Services (for advanced usage)
    "FlextLdifParserService",
    "FlextLdifWriterService",
    # Models
    "Entry",
]


# =========================================================================
# USAGE EXAMPLES
# =========================================================================

if __name__ == "__main__":
    # Example 1: Parse LDIF (zero ceremony)
    entries = parse_ldif("users.ldif")
    print(f"Parsed {len(entries)} entries")
    
    # Example 2: Safe parsing (no exceptions)
    entries = parse_ldif_safe("might_fail.ldif")
    if entries:
        print(f"Success: {len(entries)} entries")
    else:
        print("Parsing failed")
    
    # Example 3: Filter and write
    users = [e for e in entries if "user" in e.dn]
    write_ldif(users, output_path=Path("users_only.ldif"))
    
    # Example 4: Functional composition
    result = (
        FlextLdifParserService(source="input.ldif")
        .map(lambda entries: [e for e in entries if "active" in e.dn])
        .and_then(lambda filtered: 
            FlextLdifWriterService(
                entries=filtered,
                output_path=Path("active_users.ldif")
            ).result
        )
    )
    
    if result.is_success:
        print(f"Processed successfully")
```

---

## 🚀 Summary: What We Achieved

### Eliminated Boilerplate

| Pattern | Before | After | Reduction |
|---------|--------|-------|-----------|
| Basic usage | 3 lines | 1 line | 67% |
| Method calls | `.execute().unwrap()` | `.value` | 75% |
| Safe access | try/except block | `.value_or_none` | 80% |
| Factory | Not available | `parse_ldif()` | 90% |

### Python 3.13 Benefits

- ✅ Type parameter syntax (cleaner generics)
- ✅ Better type inference
- ✅ Improved pattern matching
- ✅ Better error messages

### Pydantic v2 Benefits

- ✅ Annotated fields (clearer)
- ✅ computed_field (automatic execution)
- ✅ PrivateAttr (better caching)
- ✅ Better validation

### Architecture Benefits

- ✅ Zero ceremony (.value property)
- ✅ Safe access (.value_or_none)
- ✅ Function wrappers (parse_ldif())
- ✅ Monadic composition (optional)
- ✅ Infrastructure automatic (mixins)
- ✅ Config auto-resolved

---

**Next Step:** Implementar estas 3 propriedades no FlextService atual!

