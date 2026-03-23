# Tap Validation Type Refactoring - Code Examples

## flext-tap-ldap Conversion Examples

### Example 1: Simple String Constraints

**Before:**
```python
class LdapConnectionParams(FlextLdapModels.Value):
    host: Annotated[str, Field(min_length=1)]
    base_dn: Annotated[str, Field(min_length=1)]
```

**After:**
```python
class LdapConnectionParams(FlextLdapModels.Value):
    host: t.NonEmptyStr
    base_dn: t.NonEmptyStr
```

### Example 2: Integer Constraints with Defaults

**Before:**
```python
class LdapConnectionParams(FlextLdapModels.Value):
    port: Annotated[int, Field(default=c.TapLdap.DEFAULT_PORT, ge=1)]
    timeout_seconds: Annotated[
        int, Field(default=c.TapLdap.DEFAULT_SEARCH_TIMEOUT, ge=1)
    ]
    page_size: Annotated[int, Field(default=c.TapLdap.DEFAULT_PAGE_SIZE, ge=1)]
```

**After:**
```python
class LdapConnectionParams(FlextLdapModels.Value):
    port: Annotated[t.PortNumber, Field(default=c.TapLdap.DEFAULT_PORT)]
    timeout_seconds: Annotated[
        t.PositiveInt, Field(default=c.TapLdap.DEFAULT_SEARCH_TIMEOUT)
    ]
    page_size: Annotated[t.PositiveInt, Field(default=c.TapLdap.DEFAULT_PAGE_SIZE)]
```

### Example 3: Multiple Constraints

**Before:**
```python
class LdapConnectionParams(FlextLdapModels.Value):
    max_retries: Annotated[int, Field(default=3, ge=0)]
```

**After:**
```python
class LdapConnectionParams(FlextLdapModels.Value):
    max_retries: Annotated[t.RetryCount, Field(default=3)]
```

### Example 4: Entity Fields

**Before:**
```python
class LdapConnection(FlextLdapModels.Entity):
    host: Annotated[str, Field(min_length=1)]
    port: Annotated[int, Field(ge=1)]
    timeout: Annotated[int, Field(ge=1)]
```

**After:**
```python
class LdapConnection(FlextLdapModels.Entity):
    host: t.NonEmptyStr
    port: t.PortNumber
    timeout: t.PositiveInt
```

### Example 5: Value Objects

**Before:**
```python
class StreamCreationParams(FlextLdapModels.Value):
    stream_type: Annotated[str, Field(min_length=1)]
    connection_id: Annotated[str, Field(min_length=1)]
    search_filter: Annotated[str, Field(min_length=1)]
```

**After:**
```python
class StreamCreationParams(FlextLdapModels.Value):
    stream_type: t.NonEmptyStr
    connection_id: t.NonEmptyStr
    search_filter: t.NonEmptyStr
```

## Type Reference Table

| Use Case | Old Pattern | New Type | Constraint |
|----------|------------|----------|-----------|
| Non-empty string | `Annotated[str, Field(min_length=1)]` | `t.NonEmptyStr` | Length ≥ 1 |
| Positive integer | `Annotated[int, Field(ge=1)]` | `t.PositiveInt` | Value > 0 |
| Non-negative integer | `Annotated[int, Field(ge=0)]` | `t.NonNegativeInt` | Value ≥ 0 |
| Port number | `Annotated[int, Field(ge=1, le=65535)]` | `t.PortNumber` | 1 ≤ Value ≤ 65535 |
| Retry count | `Annotated[int, Field(ge=0, le=10)]` | `t.RetryCount` | 0 ≤ Value ≤ 10 |
| Non-negative float | `Annotated[float, Field(ge=0.0)]` | `t.NonNegativeFloat` | Value ≥ 0.0 |
| Positive float | `Annotated[float, Field(gt=0.0)]` | `t.PositiveFloat` | Value > 0.0 |

## Import Statement

All converted files need this import:

```python
from flext_core.typings import t
```

## Validation Semantics

The converted types maintain the exact same validation semantics through `annotated-types` constraints:

- `t.NonEmptyStr` uses `Len(1)` - minimum length of 1
- `t.PositiveInt` uses `Gt(0)` - greater than 0
- `t.PortNumber` uses `Ge(1), Le(65535)` - between 1 and 65535
- `t.RetryCount` uses `Ge(0), Le(10)` - between 0 and 10

These are framework-independent and work with Pydantic v2 natively.
