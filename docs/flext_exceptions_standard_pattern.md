# FlextExceptions Standard Pattern

**Version**: 2.0.0
**Authority**: FLEXT Ecosystem Standard
**Last Updated**: 2025-10-03
**Applies To**: ALL FLEXT ecosystem projects (21+ projects)

---

## 📋 Purpose

This document defines the **canonical FlextExceptions pattern** that ALL FLEXT ecosystem projects MUST follow. It ensures:

- ✅ **Consistency**: Same pattern across all domain libraries
- ✅ **Observability**: Correlation ID tracking across system boundaries
- ✅ **Type Safety**: Complete type annotations with MyPy strict compliance
- ✅ **Developer Experience**: Intuitive and consistent API
- ✅ **Railway Pattern Integration**: Seamless FlextResult integration

---

## 🎯 Mandatory Components Checklist

Every domain exception class MUST have:

- [ ] **Extend `FlextExceptions.BaseError`** (NOT plain `Exception`)
- [ ] **Helper method `_extract_common_kwargs()`** for parameter extraction
- [ ] **Helper method `_build_context()`** for domain context building
- [ ] **Correlation ID support** (automatic through BaseError)
- [ ] **Error code support** with domain-specific defaults
- [ ] **Domain-specific context fields** as instance attributes
- [ ] **`@override` decorator** on `__init__` method (Python 3.12+)
- [ ] **`**kwargs: object`\*\* parameter for extensibility
- [ ] **Type annotations** on all parameters and return values

---

## 🏗️ Standard Pattern Template

### Basic Domain Exception

```python
"""[Domain] exception classes extending FlextExceptions."""

from __future__ import annotations

from typing import override

from flext_core import FlextExceptions, FlextConstants


class Flext[Domain]Exceptions:
    """[Domain]-specific exception hierarchy extending FlextExceptions.

    Provides [domain]-specific exception classes that inherit from the FLEXT
    exception system to maintain consistency and proper error handling.
    """

    class [DomainError](FlextExceptions.BaseError):
        """Base error for [domain] operations with [domain]-specific context.

        Attributes:
            domain_field_1: First domain-specific field
            domain_field_2: Second domain-specific field
        """

        @override
        def __init__(
            self,
            message: str,
            *,
            domain_field_1: str | None = None,
            domain_field_2: int | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize [domain] error with [domain]-specific context.

            Args:
                message: Error message
                domain_field_1: Optional first domain field
                domain_field_2: Optional second domain field
                **kwargs: Additional parameters (context, correlation_id, error_code)
            """
            # Store domain-specific fields as instance attributes
            self.domain_field_1 = domain_field_1
            self.domain_field_2 = domain_field_2

            # Extract common parameters using helper method
            base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

            # Build context with domain-specific fields using helper method
            context = self._build_context(
                base_context,
                domain_field_1=domain_field_1,
                domain_field_2=domain_field_2,
            )

            # Call parent with complete error information
            super().__init__(
                message,
                code=error_code or "[DOMAIN]_ERROR",  # Domain-specific default code
                context=context,
                correlation_id=correlation_id,
            )
```

### Specialized Domain Exceptions

```python
    class [DomainValidation]Error([DomainError]):
        """Validation error specific to [domain] operations."""

        @override
        def __init__(
            self,
            message: str,
            *,
            field: str | None = None,
            value: object | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize [domain] validation error.

            Args:
                message: Error message
                field: Field that failed validation
                value: Value that failed validation
                **kwargs: Additional parameters
            """
            self.field = field
            self.value = value

            base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

            context = self._build_context(
                base_context,
                field=field,
                value=value,
            )

            super().__init__(
                message,
                code=error_code or "[DOMAIN]_VALIDATION_ERROR",
                context=context,
                correlation_id=correlation_id,
            )
```

---

## 📚 Real-World Examples

### Example 1: HTTP/API Domain (flext-api)

```python
"""HTTP API exception classes extending FlextExceptions."""

from __future__ import annotations

from typing import override

from flext_core import FlextExceptions, FlextConstants
from flext_core.typings import FlextTypes


HttpStatusCode = int  # Type alias for HTTP status codes


class FlextApiExceptions:
    """HTTP API exception hierarchy extending FlextExceptions."""

    class ApiError(FlextExceptions.BaseError):
        """Base HTTP API error with status code and request context.

        Attributes:
            status_code: HTTP status code
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc.)
        """

        @override
        def __init__(
            self,
            message: str,
            *,
            status_code: HttpStatusCode = FlextConstants["Http.HTTP_INTERNAL_SERVER_ERROR"],
            endpoint: str | None = None,
            method: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize HTTP API error with request context.

            Args:
                message: Error message
                status_code: HTTP status code (default: 500)
                endpoint: API endpoint path
                method: HTTP method
                **kwargs: Additional parameters (context, correlation_id, error_code)
            """
            self.status_code = status_code
            self.endpoint = endpoint
            self.method = method

            # Extract common parameters
            base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

            # Build context with HTTP-specific fields
            context = self._build_context(
                base_context,
                status_code=status_code,
                endpoint=endpoint,
                method=method,
            )

            super().__init__(
                message,
                code=error_code or f"HTTP_{status_code}",
                context=context,
                correlation_id=correlation_id,
            )

    class RequestValidationError(ApiError):
        """HTTP request validation error (400 Bad Request)."""

        @override
        def __init__(
            self,
            message: str,
            *,
            field: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize request validation error.

            Args:
                message: Error message
                field: Field that failed validation
                **kwargs: Additional parameters
            """
            self.field = field

            base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

            context = self._build_context(
                base_context,
                field=field,
            )

            super().__init__(
                message,
                status_code=FlextConstants["Http.HTTP_BAD_REQUEST"],
                code=error_code or "HTTP_400_VALIDATION",
                context=context,
                correlation_id=correlation_id,
                **kwargs,
            )
```

**Usage**:

```python
from flext_api import FlextApiExceptions

# Simple usage
raise FlextApiExceptions.ApiError(
    "Failed to fetch user data",
    status_code=404,
    endpoint="/api/users/123",
    method="GET"
)

# With correlation ID for distributed tracing
raise FlextApiExceptions.ApiError(
    "Service unavailable",
    status_code=503,
    endpoint="/api/orders",
    correlation_id="req_abc123",
    context={"retry_after": 60}
)

# Validation error
raise FlextApiExceptions.RequestValidationError(
    "Email format invalid",
    field="email",
    context={"provided_value": "invalid@"}
)
```

---

### Example 2: LDAP Domain (flext-ldap)

```python
"""LDAP exception classes extending FlextExceptions."""

from __future__ import annotations

from typing import override

from flext_core import FlextExceptions


class FlextLdapExceptions:
    """LDAP-specific exception hierarchy extending FlextExceptions."""

    class LdapError(FlextExceptions.BaseError):
        """Base LDAP error with server and connection context.

        Attributes:
            server_uri: LDAP server URI
            ldap_code: LDAP-specific error code
            bind_dn: DN used for binding
        """

        @override
        def __init__(
            self,
            message: str,
            *,
            server_uri: str | None = None,
            ldap_code: int | None = None,
            bind_dn: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize LDAP error with server context.

            Args:
                message: Error message
                server_uri: LDAP server URI
                ldap_code: LDAP protocol error code
                bind_dn: Distinguished name used for binding
                **kwargs: Additional parameters
            """
            self.server_uri = server_uri
            self.ldap_code = ldap_code
            self.bind_dn = bind_dn

            base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

            context = self._build_context(
                base_context,
                server_uri=server_uri,
                ldap_code=ldap_code,
                bind_dn=bind_dn,
            )

            super().__init__(
                message,
                code=error_code or f"LDAP_{ldap_code}" if ldap_code else "LDAP_ERROR",
                context=context,
                correlation_id=correlation_id,
            )

    class LdapConnectionError(LdapError):
        """LDAP connection error."""

        @override
        def __init__(
            self,
            message: str,
            *,
            server_uri: str | None = None,
            ldap_code: int | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize LDAP connection error."""
            super().__init__(
                message,
                server_uri=server_uri,
                ldap_code=ldap_code,
                **kwargs,
            )
```

**Usage**:

```python
from flext_ldap import FlextLdapExceptions

# Connection error
raise FlextLdapExceptions.LdapConnectionError(
    "Failed to connect to LDAP server",
    server_uri="ldap://localhost:389",
    ldap_code=91,  # LDAP_CONNECT_ERROR
    correlation_id="ldap_conn_123"
)

# Search error with context
raise FlextLdapExceptions.LdapError(
    "Search operation failed",
    server_uri="ldap://localhost:389",
    ldap_code=32,  # NO_SUCH_OBJECT
    context={
        "base_dn": "dc=example,dc=com",
        "filter": "(uid=user123)",
        "scope": "SUBTREE"
    }
)
```

---

### Example 3: Singer Tap Domain (flext-tap-oracle)

```python
"""Singer tap exception classes extending FlextExceptions."""

from __future__ import annotations

from typing import override

from flext_core import FlextExceptions, FlextConstants


class FlextTapOracleExceptions:
    """Oracle tap exception hierarchy extending FlextExceptions."""

    class TapError(FlextExceptions.BaseError):
        """Base error for Oracle tap operations with Singer context.

        Attributes:
            tap_stream_id: Singer stream identifier
            catalog_entry: Catalog entry name
            record_count: Number of records processed
        """

        @override
        def __init__(
            self,
            message: str,
            *,
            tap_stream_id: str | None = None,
            catalog_entry: str | None = None,
            record_count: int | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize Oracle tap error with Singer tap context.

            Args:
                message: Error message
                tap_stream_id: Singer stream identifier
                catalog_entry: Catalog entry being processed
                record_count: Number of records processed before error
                **kwargs: Additional parameters
            """
            self.tap_stream_id = tap_stream_id
            self.catalog_entry = catalog_entry
            self.record_count = record_count

            base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

            context = self._build_context(
                base_context,
                tap_stream_id=tap_stream_id,
                catalog_entry=catalog_entry,
                record_count=record_count,
            )

            super().__init__(
                message,
                code=error_code or "TAP_ERROR",
                context=context,
                correlation_id=correlation_id,
            )

    class TapQueryError(TapError):
        """Singer tap database query error."""

        @override
        def __init__(
            self,
            message: str,
            *,
            query: str | None = None,
            oracle_error_code: int | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize tap query error.

            Args:
                message: Error message
                query: SQL query that failed
                oracle_error_code: Oracle-specific error code
                **kwargs: Additional parameters
            """
            self.query = query
            self.oracle_error_code = oracle_error_code

            base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

            context = self._build_context(
                base_context,
                query=query,
                oracle_error_code=oracle_error_code,
            )

            super().__init__(
                message,
                code=error_code or f"TAP_QUERY_ERROR_{oracle_error_code}" if oracle_error_code else "TAP_QUERY_ERROR",
                context=context,
                correlation_id=correlation_id,
                **kwargs,
            )
```

**Usage**:

```python
from flext_tap_oracle import FlextTapOracleExceptions

# Tap error with stream context
raise FlextTapOracleExceptions.TapError(
    "Stream processing failed",
    tap_stream_id="users_stream",
    catalog_entry="USERS",
    record_count=1250,
    correlation_id="tap_run_abc123"
)

# Query error with Oracle details
raise FlextTapOracleExceptions.TapQueryError(
    "Oracle query timeout",
    query="SELECT * FROM users WHERE created_date > :1",
    oracle_error_code=1013,  # ORA-01013: user requested cancel
    tap_stream_id="users_stream",
    context={"timeout_seconds": 300}
)
```

---

## 🔧 Helper Methods Implementation

### `_extract_common_kwargs()` Helper

This method extracts common parameters from kwargs to avoid repetition.

```python
@staticmethod
def _extract_common_kwargs(
    kwargs: dict[str, object],
) -> tuple[dict[str, object] | None, str | None, str | None]:
    """Extract common kwargs (context, correlation_id, error_code).

    Args:
        kwargs: Keyword arguments dictionary

    Returns:
        Tuple of (context, correlation_id, error_code)
    """
    context_raw = kwargs.get("context")
    context = dict(context_raw) if isinstance(context_raw, dict) else None

    correlation_id_raw = kwargs.get("correlation_id")
    correlation_id = str(correlation_id_raw) if correlation_id_raw is not None else None

    error_code_raw = kwargs.get("error_code")
    error_code = str(error_code_raw) if error_code_raw is not None else None

    return context, correlation_id, error_code
```

### `_build_context()` Helper

This method builds the complete context dictionary with domain-specific fields.

```python
@staticmethod
def _build_context(
    base_context: dict[str, object] | None,
    **domain_fields: object,
) -> dict[str, object]:
    """Build context dictionary with domain-specific fields.

    Args:
        base_context: Base context from kwargs
        **domain_fields: Domain-specific fields to include

    Returns:
        Complete context dictionary
    """
    context = dict(base_context or {})

    # Add non-None domain fields
    for key, value in domain_fields.items():
        if value is not None:
            context[key] = value

    return context
```

**Note**: Both helper methods are inherited from `FlextExceptions.BaseError`, so you don't need to reimplement them in each domain exception class. Just call them using `self._extract_common_kwargs()` and `self._build_context()`.

---

## ❌ Anti-Patterns to Avoid

### ❌ DON'T: Extend Plain Exception

```python
# ❌ WRONG - Breaks FlextExceptions contract
class MyDomainExceptions:
    class MyError(Exception):  # ❌ Should extend FlextExceptions.BaseError
        def __init__(self, message: str) -> None:
            super().__init__(message)
            # ❌ Missing correlation_id, error_code, context
```

### ❌ DON'T: Skip Helper Methods

```python
# ❌ WRONG - Duplicates parameter extraction logic
class MyError(FlextExceptions.BaseError):
    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        context: dict | None = None,
        correlation_id: str | None = None,
        error_code: str | None = None,
    ) -> None:
        self.field = field
        # ❌ Manually handling parameters instead of using helpers
        super().__init__(message, code=error_code, context=context, correlation_id=correlation_id)
```

### ❌ DON'T: Use Factory Methods Only

```python
# ❌ WRONG - Factory method pattern creates inconsistent API
class MyDomainExceptions:
    def create_error(self, message: str) -> Exception:
        """Factory method - inconsistent with direct instantiation."""
        return self.MyError(message)

# ❌ Usage is inconsistent
exceptions = MyDomainExceptions()
raise exceptions.create_error("Failed")  # ❌ Too verbose

# ✅ CORRECT - Direct instantiation
raise MyDomainExceptions.MyError("Failed")  # ✅ Clean and consistent
```

### ❌ DON'T: Ignore Correlation IDs

```python
# ❌ WRONG - Missing correlation ID support
class MyError(FlextExceptions.BaseError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        # ❌ No correlation_id parameter
        # ❌ Breaks distributed tracing
```

---

## ✅ Complete Example: Migration Exception Hierarchy

```python
"""Migration exception classes extending FlextExceptions - COMPLETE EXAMPLE."""

from __future__ import annotations

from typing import override

from flext_core import FlextExceptions


class client-aOudMigExceptions:
    """client-a OUD Migration exception hierarchy extending FlextExceptions."""

    class MigrationError(FlextExceptions.BaseError):
        """Base exception for migration-related errors.

        Attributes:
            operation: Migration operation name
            phase: Migration phase (validation, processing, sync)
        """

        @override
        def __init__(
            self,
            message: str,
            *,
            operation: str | None = None,
            phase: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize migration error.

            Args:
                message: Error message
                operation: Operation name that failed
                phase: Migration phase
                **kwargs: Additional parameters
            """
            self.operation = operation
            self.phase = phase

            base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

            context = self._build_context(
                base_context,
                operation=operation,
                phase=phase,
            )

            super().__init__(
                message,
                code=error_code or "MIGRATION_ERROR",
                context=context,
                correlation_id=correlation_id,
            )

    class LdifProcessingError(MigrationError):
        """LDIF processing error."""

        @override
        def __init__(
            self,
            message: str,
            *,
            ldif_file: str | None = None,
            entry_dn: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize LDIF processing error.

            Args:
                message: Error message
                ldif_file: LDIF file being processed
                entry_dn: DN of entry that failed
                **kwargs: Additional parameters
            """
            self.ldif_file = ldif_file
            self.entry_dn = entry_dn

            base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

            context = self._build_context(
                base_context,
                ldif_file=ldif_file,
                entry_dn=entry_dn,
            )

            super().__init__(
                message,
                operation="ldif_processing",
                phase="processing",
                code=error_code or "LDIF_PROCESSING_ERROR",
                context=context,
                correlation_id=correlation_id,
            )
```

---

## 📖 Usage Guidelines

### 1. Raising Exceptions

```python
# Simple exception
raise FlextApiExceptions.ApiError(
    "Resource not found",
    status_code=404,
    endpoint="/api/users/123"
)

# With correlation ID for distributed tracing
raise FlextApiExceptions.ApiError(
    "Service unavailable",
    status_code=503,
    correlation_id="req_abc123"
)

# With additional context
raise FlextApiExceptions.ApiError(
    "Rate limit exceeded",
    status_code=429,
    endpoint="/api/search",
    context={
        "rate_limit": 1000,
        "current_usage": 1250,
        "reset_time": "2025-10-03T15:00:00Z"
    }
)
```

### 2. Catching and Re-raising

```python
try:
    result = await api.fetch_data()
except FlextApiExceptions.ApiError as e:
    # Log with correlation ID
    logger.error(
        f"API error: {e.message}",
        extra={
            "correlation_id": e.correlation_id,
            "error_code": e.code,
            "context": e.context
        }
    )
    # Re-raise with additional context
    raise FlextApiExceptions.ApiError(
        f"Failed to fetch data: {e.message}",
        status_code=e.status_code,
        correlation_id=e.correlation_id,
        context={"original_error": str(e), **e.context}
    ) from e
```

### 3. FlextResult Integration

```python
def fetch_user(user_id: str) -> FlextResult[User]:
    """Fetch user with FlextResult error handling."""
    try:
        user = api.get_user(user_id)
        return FlextResult[User].ok(user)
    except FlextApiExceptions.ApiError as e:
        return FlextResult[User].fail(
            f"Failed to fetch user: {e.message}",
            context={"correlation_id": e.correlation_id, **e.context}
        )
```

---

## 🔍 Validation Checklist

Before submitting exception changes:

- [ ] All exceptions extend `FlextExceptions.BaseError`
- [ ] Helper methods `_extract_common_kwargs()` and `_build_context()` are used
- [ ] Correlation ID parameter is supported via `**kwargs`
- [ ] Error code has domain-specific default
- [ ] Domain-specific fields are instance attributes
- [ ] `@override` decorator is present
- [ ] Complete type annotations on all parameters
- [ ] Docstrings explain purpose and parameters
- [ ] MyPy strict mode passes with zero errors
- [ ] Usage examples are provided

---

**Document Authority**: FLEXT Ecosystem Standard
**Enforcement**: MANDATORY for all FLEXT projects
**Version**: 2.0.0 (2025-10-03)
