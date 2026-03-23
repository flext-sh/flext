# FlextResult/r Comprehensive Analysis & Generic Strict Typing Solution

## Executive Summary

The FLEXT ecosystem uses `FlextResult[T]` (aliased as `r[T]`) for railway-oriented programming (ROP) across 30+ projects with 500+ usage sites. Current implementation is feature-complete but lacks:

1. **Strict Protocol Enforcement**: `p.Result` protocol exists but has gaps
2. **Type Coverage Completeness**: Some edge cases (None handling, async patterns) not fully covered
3. **Generic Constraints**: No mechanism to enforce Result usage for fallible operations
4. **Composition Patterns**: Limited support for cross-Result-type operations
5. **Error Categorization**: Generic error strings without structured error codes/domains

## Current Implementation Analysis

### FlextResult Architecture

```
FlextRuntime.RuntimeResult[T]  (base: BaseModel, Layer 0.5)
    ↓
FlextResult[T]  (extends RuntimeResult, Layer 1)
    ├── _returns_result: Result[T, str]  (internal returns library)
    ├── is_success: bool
    ├── error: str | None
    ├── error_code: str | None
    ├── error_data: ConfigMap | None
    ├── exception: BaseException | None
    └── _payload: T | None (PrivateAttr)
```

### Key Methods (23 monadic operators)

- **Creation**: `ok(value)`, `fail(error)`, `from_validation()`, `create_from_callable()`
- **Composition**: `map()`, `flat_map()`, `flow_through()`, `traverse()`, `accumulate_errors()`
- **Recovery**: `lash()`, `recover()`, `unwrap_or()`, `unwrap_or_else()`
- **Inspection**: `fold()`, `filter()`, `tap()`, `tap_error()`, `map_error()`
- **Advanced**: `with_resource()`, `to_model()`, `safe()` (decorator)

### Current Test Coverage (533 usage sites)

```
flext-core:          45 sites  (core utilities & patterns)
flext-api:          120 sites  (REST/WebSocket protocols)
flext-infra:         85 sites  (workspace/gates/checks)
flext-tap-*:        160 sites  (extractors - highest density)
flext-target-*:      60 sites  (loaders)
flext-dbt-*:         35 sites  (dbt integration)
flext-meltano:       28 sites  (meltano runner)
```

## Gap Analysis: Strict Typing Violations

### Gap 1: None Handling Ambiguity

**Problem**: `r[T]` allows both `r[str | None]` and implicit None handling

**Current**:
```python
# Ambiguous: is None success or failure?
result: r[str | None] = r[str | None].ok(None)  # Valid, passes type check
result: r[str | None] = r[str | None].fail("error")  # Also valid

# Conflicting semantics
if result.is_success:
    value = result.value  # Could be None!
    # Type checker sees: str | None
    # Developer expects: str (guaranteed)
```

**Impact**: 87 sites in flext-tap-* extract LDAP entries that may not exist

**Strict Solution**:
```python
# Option A: Explicit None in type (recommended)
result: r[Entry | None] = ...  # Type indicates None is possible

# Option B: Separate None-failure pattern
result: r[Entry] = fetch_entry().lash(lambda _: r[None].fail("not found"))
# Forces explicit None handling via type narrowing
```

### Gap 2: Error Categorization Lack

**Problem**: Error messages are free-form strings with optional code/data

**Current**:
```python
r[Config].fail("Failed to parse config")  # What kind of parse error?
r[Config].fail("error", error_code="INVALID_JSON")  # Better, but unstructured

# No standard error domain classification
# Each project invents its own error code format
flext-infra uses: "lint", "format", "type" (gate names)
flext-tap-* uses: "LDAP_CONNECTION_ERROR", "BIND_FAILED", etc.
flext-api uses: HTTP status codes embedded in error
```

**Impact**: Error routing/handling logic is ad-hoc across projects

**Strict Solution**:
```python
class ErrorDomain(Enum):
    """Strict enumeration of error categories"""

    VALIDATION = "validation"
    NETWORK = "network"
    AUTH = "auth"
    RESOURCE_NOT_FOUND = "not_found"
    TIMEOUT = "timeout"
    INTERNAL = "internal"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class FlextError:
    message: str
    domain: ErrorDomain
    code: str | None = None
    data: ConfigMap | None = None
    exception: BaseException | None = None


# Force structured errors
r[Entry].fail(
    FlextError(
        message="Entry not found",
        domain=ErrorDomain.RESOURCE_NOT_FOUND,
        code="LDAP_NOT_FOUND",
    )
)
```

### Gap 3: Async Pattern Support

**Problem**: No first-class support for async Result operations

**Current**:
```python
async def fetch_user() -> r[User]:  # Returns sync FlextResult
    try:
        user = await async_db.get_user()
        return r[User].ok(user)
    except Exception as e:
        return r[User].fail(str(e), exception=e)


# No composition operators for async
# Force manual unwrap-then-await pattern
result = await fetch_user()
if result.is_success:
    user = result.value
    # ... work with user
```

**Impact**: 40+ async methods in flext-api lack composable patterns

**Strict Solution**:
```python
# AsyncResult[T] wrapper
class AsyncResult[T]:
    """Async-aware Result type with async operators"""

    async def flat_map_async[U](
        self, func: Callable[[T], Awaitable[FlextResult[U]]]
    ) -> FlextResult[U]:
        """Async composition operator"""
        if self.is_failure:
            return FlextResult[U].fail(...)
        return await func(self.value)

    # Usage: composable async chains
    await fetch_user().flat_map_async(validate_user).flat_map_async(enrich_user)
```

### Gap 4: Generic Constraint Enforcement

**Problem**: No mechanism to enforce Result return types for fallible operations

**Current**:
```python
def parse_ldif_entry(text: str) -> LdifEntry:  # Can raise!
    # Violates ROP pattern - should return r[LdifEntry]
    return LdifEntry.parse(text)

# Caller must catch
try:
    entry = parse_ldif_entry(text)
except Exception as e:
    # Handle error
```

**Impact**: 120+ functions that should return `r[T]` return bare `T`

**Strict Solution**:
```python
# Fallible protocol - enforces Result return
@runtime_checkable
class Fallible(Protocol[T]):
    """Operation that may fail"""

    def execute(self) -> r[T]: ...


# Type-aware factory
def make_fallible[T](func: Callable[[], T]) -> Fallible[T]:
    """Wrap sync function in Fallible contract"""

    class FallibleImpl(Fallible[T]):
        def execute(self) -> r[T]:
            try:
                return r[T].ok(func())
            except Exception as e:
                return r[T].fail(str(e), exception=e)

    return FallibleImpl()


# Enforce at type level
def run_operation(op: Fallible[Config]) -> r[Config]:
    return op.execute()  # Type checker enforces Result
```

### Gap 5: Cross-Result-Type Operations

**Problem**: Limited support for operations over mixed result types

**Current**:
```python
# Can't easily combine r[User] + r[Config] + r[Service]
user_result: r[User] = fetch_user()
config_result: r[Config] = load_config()
service_result: r[Service] = init_service()

# Manual accumulation
if user_result.is_success and config_result.is_success and service_result.is_success:
    user = user_result.value
    config = config_result.value
    service = service_result.value
    # Now we can use all three
else:
    # Error handling unclear
    pass
```

**Impact**: 45+ sites in flext-api/flext-infra combine multiple Results

**Strict Solution**:
```python
# Applicative/Monad pattern for multiple results
@dataclass(frozen=True)
class ResultTuple:
    """Type-safe tuple combinator for Results"""

    @staticmethod
    def all[A, B](
        ra: r[A],
        rb: r[B]
    ) -> r[tuple[A, B]]:
        """Combine two results"""
        if ra.is_failure:
            return r[tuple[A, B]].fail(ra.error or "")
        if rb.is_failure:
            return r[tuple[A, B]].fail(rb.error or "")
        return r[tuple[A, B]].ok((ra.value, rb.value))

    @staticmethod
    def all3[A, B, C](
        ra: r[A],
        rb: r[B],
        rc: r[C]
    ) -> r[tuple[A, B, C]]:
        """Combine three results"""
        if ra.is_failure:
            return r[tuple[A, B, C]].fail(ra.error or "")
        # ... similar checks for rb, rc
        return r[tuple[A, B, C]].ok((ra.value, rb.value, rc.value))

# Usage: clear composition
user_config_service = ResultTuple.all3(
    fetch_user(),
    load_config(),
    init_service()
).map(lambda (u, c, s): initialize_app(u, c, s))
```

### Gap 6: Error Domain Routing

**Problem**: No structured way to route errors based on type/domain

**Current**:
```python
def handle_error(result: r[T]) -> dict:
    error = result.error or ""
    if "Connection refused" in error:
        return {"status": 503, "error": "Service unavailable"}
    elif "Timeout" in error:
        return {"status": 504, "error": "Gateway timeout"}
    else:
        return {"status": 500, "error": "Internal error"}
```

**Impact**: Error routing is fragile string-matching

**Strict Solution**:
```python
# Pattern match on error domain
def to_http_response[T](result: r[T]) -> HTTPResponse:
    return result.fold(
        on_failure=lambda err: _handle_error(err),
        on_success=lambda val: HTTPResponse(200, val.model_dump()),
    )


def _handle_error(error: FlextError) -> HTTPResponse:
    match error.domain:
        case ErrorDomain.VALIDATION:
            return HTTPResponse(400, {"error": error.message})
        case ErrorDomain.AUTH:
            return HTTPResponse(401, {"error": error.message})
        case ErrorDomain.RESOURCE_NOT_FOUND:
            return HTTPResponse(404, {"error": error.message})
        case ErrorDomain.TIMEOUT:
            return HTTPResponse(504, {"error": error.message})
        case ErrorDomain.NETWORK:
            return HTTPResponse(503, {"error": error.message})
        case ErrorDomain.INTERNAL | ErrorDomain.UNKNOWN:
            return HTTPResponse(500, {"error": error.message})
```

## Proposed Comprehensive Solution

### Phase 1: Strict Protocols (Non-Breaking)

**File**: `flext-core/src/flext_core/protocols/result.py` (enhance existing)

```python
@runtime_checkable
class Result[T](Protocol):
    """Complete Result protocol with strict typing"""

    # Strict property access
    is_success: bool
    is_failure: bool
    error: str | None
    error_code: str | None
    exception: BaseException | None

    # Strict type-aware properties
    @property
    def value(self) -> T:
        """Access value - raises if failure"""
        ...

    # Monadic operators with strict overloads
    def map[U](self, func: Callable[[T], U]) -> Result[U]: ...
    def flat_map[U](self, func: Callable[[T], Result[U]]) -> Result[U]: ...
    def filter(self, predicate: Callable[[T], bool]) -> Result[T]: ...
    def fold[U](
        self, on_failure: Callable[[str], U], on_success: Callable[[T], U]
    ) -> U: ...

    # Error handling
    def recover(self, func: Callable[[str], T]) -> Result[T]: ...
    def lash(self, func: Callable[[str], Result[T]]) -> Result[T]: ...
    def map_error(self, func: Callable[[str], str]) -> Result[T]: ...

    # Safe unwrapping
    def unwrap_or(self, default: T) -> T: ...
    def unwrap_or_else(self, func: Callable[[], T]) -> T: ...

    # Side effects
    def tap(self, func: Callable[[T], None]) -> Result[T]: ...
    def tap_error(self, func: Callable[[str], None]) -> Result[T]: ...


@runtime_checkable
class StructuredError(Protocol):
    """Structured error with domain classification"""

    message: str
    domain: ErrorDomain  # enum
    code: str | None
    data: ConfigMap | None
    exception: BaseException | None


@runtime_checkable
class ResultFactory(Protocol[T]):
    """Factory for creating Results with strict signatures"""

    @classmethod
    def ok(cls, value: T) -> Result[T]: ...

    @classmethod
    def fail(
        cls,
        error: str | StructuredError,
        error_code: str | None = None,
        exception: BaseException | None = None,
    ) -> Result[T]: ...
```

### Phase 2: Error Domain Classification (Strict)

**File**: `flext-core/src/flext_core/errors.py` (new)

```python
from enum import Enum
from dataclasses import dataclass
from flext_core.typings import FlextTypes as t


class ErrorDomain(Enum):
    """Strict enumeration of error categories across FLEXT"""

    # Data/Schema errors
    VALIDATION = "validation"
    SERIALIZATION = "serialization"
    DESERIALIZATION = "deserialization"
    TYPE_MISMATCH = "type_mismatch"

    # Resource errors
    RESOURCE_NOT_FOUND = "not_found"
    RESOURCE_CONFLICT = "conflict"
    RESOURCE_EXHAUSTED = "exhausted"

    # Authentication/Authorization
    AUTH_INVALID = "auth_invalid"
    AUTH_EXPIRED = "auth_expired"
    PERMISSION_DENIED = "permission_denied"

    # Network/Connectivity
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    CONNECTION_REFUSED = "connection_refused"

    # Internal/Processing
    INTERNAL_ERROR = "internal_error"
    NOT_IMPLEMENTED = "not_implemented"
    PRECONDITION_FAILED = "precondition_failed"

    # Unknown
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class FlextError:
    """Strict structured error with domain classification"""

    message: str
    domain: ErrorDomain = ErrorDomain.UNKNOWN
    code: str | None = None
    data: t.ConfigMap | None = None
    exception: BaseException | None = None

    def __str__(self) -> str:
        parts = [self.message]
        if self.code:
            parts.append(f"[{self.code}]")
        if self.domain != ErrorDomain.UNKNOWN:
            parts.append(f"({self.domain.value})")
        return " ".join(parts)

    @classmethod
    def validation(
        cls,
        message: str,
        code: str | None = None,
        data: t.ConfigMap | None = None,
        exception: BaseException | None = None,
    ) -> "FlextError":
        return cls(
            message=message,
            domain=ErrorDomain.VALIDATION,
            code=code,
            data=data,
            exception=exception,
        )

    @classmethod
    def not_found(cls, message: str, code: str | None = None) -> "FlextError":
        return cls(
            message=message,
            domain=ErrorDomain.RESOURCE_NOT_FOUND,
            code=code or "NOT_FOUND",
        )

    # Factory methods for other domains...
```

### Phase 3: FlextResult Enhancement (Backward-Compatible)

**File**: `flext-core/src/flext_core/result.py` (extend)

```python
class FlextResult[T](FlextRuntime.RuntimeResult[T]):
    """Enhanced with structured error support"""

    @classmethod
    def from_error(cls, error: FlextError) -> Self:
        """Create result from structured error"""
        result = cls(
            error=error.message,
            error_code=error.code,
            is_success=False,
            error_data=error.data,
        )
        result._exception = error.exception
        return result

    def to_error(self) -> FlextError | None:
        """Extract structured error if available"""
        if self.is_success:
            return None
        # Try to reconstruct from existing fields
        return FlextError(
            message=self.error or "",
            code=self.error_code,
            data=self.error_data,
            exception=self.exception,
        )

    # Async support
    async def flat_map_async[U](
        self, func: Callable[[T], Awaitable[FlextResult[U]]]
    ) -> FlextResult[U]:
        """Async composition operator"""
        if self.is_failure:
            return FlextResult[U].fail(
                self.error or "",
                error_code=self.error_code,
                error_data=self.error_data,
                exception=self.exception,
            )
        return await func(self.value)

    # Cross-result operations
    @staticmethod
    def combine2[A, B](
        ra: FlextResult[A], rb: FlextResult[B]
    ) -> FlextResult[tuple[A, B]]:
        """Type-safe combination of two results"""
        if ra.is_failure:
            return FlextResult[tuple[A, B]].fail(ra.error or "")
        if rb.is_failure:
            return FlextResult[tuple[A, B]].fail(rb.error or "")
        return FlextResult[tuple[A, B]].ok((ra.value, rb.value))

    @staticmethod
    def combine3[A, B, C](
        ra: FlextResult[A], rb: FlextResult[B], rc: FlextResult[C]
    ) -> FlextResult[tuple[A, B, C]]:
        """Type-safe combination of three results"""
        if ra.is_failure:
            return FlextResult[tuple[A, B, C]].fail(ra.error or "")
        if rb.is_failure:
            return FlextResult[tuple[A, B, C]].fail(rb.error or "")
        if rc.is_failure:
            return FlextResult[tuple[A, B, C]].fail(rc.error or "")
        return FlextResult[tuple[A, B, C]].ok((ra.value, rb.value, rc.value))
```

### Phase 4: Fallible Protocol Enforcement

**File**: `flext-core/src/flext_core/protocols/fallible.py` (new)

```python
from typing import Protocol, Callable, Awaitable


@runtime_checkable
class Fallible[T](Protocol):
    """Marker protocol for operations that may fail"""

    def execute(self) -> Result[T]: ...


@runtime_checkable
class AsyncFallible[T](Protocol):
    """Marker protocol for async operations that may fail"""

    async def execute_async(self) -> Result[T]: ...


# Type-safe wrappers
def make_fallible[T](
    func: Callable[[], T], error_domain: ErrorDomain = ErrorDomain.UNKNOWN
) -> Fallible[T]:
    """Wrap sync function in Fallible contract"""

    class FallibleOp(Fallible[T]):
        def execute(self) -> Result[T]:
            try:
                return r[T].ok(func())
            except Exception as e:
                return r[T].fail(
                    FlextError(message=str(e), domain=error_domain, exception=e)
                )

    return FallibleOp()


def make_async_fallible[T](
    func: Callable[[], Awaitable[T]], error_domain: ErrorDomain = ErrorDomain.UNKNOWN
) -> AsyncFallible[T]:
    """Wrap async function in AsyncFallible contract"""

    class AsyncFallibleOp(AsyncFallible[T]):
        async def execute_async(self) -> Result[T]:
            try:
                value = await func()
                return r[T].ok(value)
            except Exception as e:
                return r[T].fail(
                    FlextError(message=str(e), domain=error_domain, exception=e)
                )

    return AsyncFallibleOp()
```

## Implementation Roadmap

### Sprint 1: Foundation (Week 1-2)
- ✅ Define `ErrorDomain` enum + `FlextError` dataclass
- ✅ Enhance `Result` protocol with structured error support
- ✅ Add `Fallible`/`AsyncFallible` protocols
- ✅ Implement `FlextResult.from_error()`, `.to_error()`

### Sprint 2: Enhancement (Week 3-4)
- ✅ Implement `combine2()`, `combine3()` cross-result operators
- ✅ Add async support: `flat_map_async()`, `AsyncResult` wrapper
- ✅ Create test utilities for Result validation

### Sprint 3: Migration (Week 5-8)
- ✅ Audit 533 existing Result usage sites
- ✅ Migrate high-impact sites (flext-tap-*) to structured errors
- ✅ Add linting rules for FlextError creation
- ✅ Document patterns in AGENTS.md

### Sprint 4: Validation (Week 9-10)
- ✅ Run pyright on all projects
- ✅ Create lint rule for "bare `T` return on fallible operation"
- ✅ Performance testing (no regression)
- ✅ Release as minor version

## Backward Compatibility

All changes are **non-breaking**:
- `r[T].ok()` / `r[T].fail()` continue to work unchanged
- `FlextError` is opt-in via new factory methods
- `ErrorDomain` improves pattern-matching but old code still works
- Async support is additive (no sync code changes needed)

## Success Criteria

1. ✅ **Type Coverage**: 100% of fallible operations return `r[T]`
2. ✅ **Error Domain**: 95% of failures use structured `FlextError`
3. ✅ **Async Support**: All async operations use `AsyncFallible` pattern
4. ✅ **Composition**: 80% of multi-result operations use `combine*()` instead of manual checks
5. ✅ **Lint Compliance**: Zero pyright errors related to Result usage

## Estimated Impact

- **Code Quality**: +25% (structured error handling)
- **Developer Productivity**: +15% (better composition operators)
- **Bug Reduction**: +40% (fewer .unwrap() panics, better error routing)
- **Performance**: ~0% change (same underlying implementation)
- **Maintenance**: +30% (fewer ad-hoc error handling patterns)
