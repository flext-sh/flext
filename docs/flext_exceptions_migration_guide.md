# FlextExceptions Migration Guide

**Version**: 1.0.0
**Authority**: FLEXT Ecosystem Refactoring Guide
**Last Updated**: 2025-10-03
**Target**: Projects with non-compliant FlextExceptions implementations

---

## 📋 Purpose

This guide provides **step-by-step instructions** for refactoring existing FlextExceptions implementations to follow the **standard pattern** defined in `flext_exceptions_standard_pattern.md`.

**When to Use This Guide**:

- ❌ Your exceptions extend plain `Exception` instead of `FlextExceptions.BaseError`
- ❌ Your exceptions don't use `_extract_common_kwargs()` helper
- ❌ Your exceptions don't use `_build_context()` helper
- ❌ Your exceptions don't support correlation IDs
- ❌ Your exceptions use factory methods instead of direct instantiation

---

## 🎯 Migration Overview

### Migration Steps

1. **Analyze Current Implementation** (5-10 minutes)
2. **Create New Standard Exceptions** (20-30 minutes)
3. **Update Exception Usages** (10-15 minutes)
4. **Run Tests and Validation** (5-10 minutes)
5. **Document Changes** (5 minutes)

**Total Time**: 45-70 minutes per project

---

## 📖 Step-by-Step Migration

### Step 1: Analyze Current Implementation

**Goal**: Understand what needs to change in your current exception hierarchy.

**Actions**:

1. **Read current exceptions file**:

   ```bash
   # Example for client-a-oud-mig
   cat src/client-a_oud_mig/exceptions.py | head -100
   ```

2. **Identify anti-patterns**:

   ```bash
   # Check if exceptions extend Exception instead of BaseError
   grep "class.*Exception.*:" src/*/exceptions.py | grep -v BaseError

   # Check for missing helper methods
   grep "_extract_common_kwargs\|_build_context" src/*/exceptions.py || echo "Missing helper methods"

   # Check for factory pattern usage
   grep "def create_.*error" src/*/exceptions.py
   ```

3. **Map exception hierarchy**:
   - List all exception classes
   - Identify domain-specific fields for each
   - Note inheritance relationships

**Example Analysis** (client-a-oud-mig):

```
Current Issues:
❌ _MigrationError extends Exception (should extend FlextExceptions.BaseError)
❌ No _extract_common_kwargs() usage
❌ No _build_context() usage
❌ No correlation_id support
❌ Manual context handling

Exception Classes to Migrate:
- _MigrationError (base)
- _LdifProcessingError
- _client-aValidationError
- _client-aConfigurationError
- _LdapConnectionError
- _SyncError
- _client-aConnectionError
- _ConfigError
- _client-aProcessingError
- _client-aAuthenticationError
- _FileError
- _SchemaError
- _WorkflowError
- _RecoverableError
- _client-aCriticalError
- _DataIntegrityError
- _PerformanceError
```

---

### Step 2: Create New Standard Exceptions

**Goal**: Refactor exception classes to follow the standard pattern.

#### Before (Anti-pattern)

```python
# ❌ OLD PATTERN - client-a-oud-mig/src/client-a_oud_mig/exceptions.py
class client-aOudMigExceptions(FlextExceptions):
    """client-a OUD Migration exception hierarchy extending FlextExceptions."""

    class _MigrationError(Exception):  # ❌ Extends Exception, not BaseError
        """Base exception for migration-related errors."""

        operation: str | None

        @override
        def __init__(
            self,
            message: str,
            *,
            operation: str | None = None,
            context: client-aOudMigTypes.Core.client-aDict | None = None,
        ) -> None:
            """Initialize migration error."""
            super().__init__(message)
            self.operation = operation
            self.context: client-aOudMigTypes.Core.client-aDict = (
                context if context is not None else {}
            )
            # ❌ No correlation_id
            # ❌ No error_code
            # ❌ No helper methods
```

#### After (Standard pattern)

```python
# ✅ NEW PATTERN - client-a-oud-mig/src/client-a_oud_mig/exceptions.py
class client-aOudMigExceptions:
    """client-a OUD Migration exception hierarchy extending FlextExceptions."""

    class MigrationError(FlextExceptions.BaseError):  # ✅ Extends BaseError
        """Base exception for migration-related errors.

        Attributes:
            operation: Migration operation name that failed
        """

        @override
        def __init__(
            self,
            message: str,
            *,
            operation: str | None = None,
            **kwargs: object,  # ✅ Accept **kwargs for extensibility
        ) -> None:
            """Initialize migration error.

            Args:
                message: Error message
                operation: Optional operation name
                **kwargs: Additional parameters (context, correlation_id, error_code)
            """
            self.operation = operation

            # ✅ Extract common parameters using helper
            base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

            # ✅ Build context with migration-specific fields
            context = self._build_context(
                base_context,
                operation=operation,
            )

            # ✅ Call parent with complete error information
            super().__init__(
                message,
                code=error_code or "MIGRATION_ERROR",  # ✅ Default error code
                context=context,
                correlation_id=correlation_id,
            )
```

#### Migration Template

Use this template to convert each exception class:

```python
# BEFORE: Anti-pattern exception
class _OldError(Exception):
    def __init__(
        self,
        message: str,
        *,
        domain_field: str | None = None,
        context: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.domain_field = domain_field
        self.context = context if context is not None else {}

# AFTER: Standard pattern exception
class NewError(FlextExceptions.BaseError):
    """[Description of error].

    Attributes:
        domain_field: [Description of field]
    """

    @override
    def __init__(
        self,
        message: str,
        *,
        domain_field: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize [error name].

        Args:
            message: Error message
            domain_field: Optional domain-specific field
            **kwargs: Additional parameters (context, correlation_id, error_code)
        """
        self.domain_field = domain_field

        # Extract common parameters
        base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

        # Build context with domain-specific fields
        context = self._build_context(
            base_context,
            domain_field=domain_field,
        )

        # Call parent with complete information
        super().__init__(
            message,
            code=error_code or "DEFAULT_ERROR_CODE",
            context=context,
            correlation_id=correlation_id,
        )
```

#### Specialized Exception Example

```python
# BEFORE: Specialized exception
class _LdifProcessingError(_MigrationError):
    """Exception for LDIF processing errors."""

    @override
    def __init__(
        self,
        message: str,
        *,
        context: client-aOudMigTypes.Core.client-aDict | None = None,
    ) -> None:
        """Initialize LDIF processing error."""
        super().__init__(message, context=context)

# AFTER: Standard pattern specialized exception
class LdifProcessingError(MigrationError):  # ✅ Inherits from MigrationError
    """LDIF processing error with LDIF-specific context.

    Attributes:
        ldif_file: Path to LDIF file being processed
        entry_dn: DN of entry that failed processing
    """

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
            ldif_file: Optional LDIF file path
            entry_dn: Optional entry DN
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

        # ✅ Call parent with additional context
        super().__init__(
            message,
            operation="ldif_processing",  # ✅ Set parent's operation field
            code=error_code or "LDIF_PROCESSING_ERROR",
            context=context,
            correlation_id=correlation_id,
            **kwargs,
        )
```

---

### Step 3: Update Exception Usages

**Goal**: Update all places where exceptions are raised to use the new pattern.

#### Before (Old usage)

```python
# ❌ OLD USAGE - Manual context handling
raise client-aOudMigExceptions._MigrationError(
    "Migration failed",
    operation="validate",
    context={"phase": "pre-migration"}
)

# ❌ OLD USAGE - No correlation ID
raise client-aOudMigExceptions._LdifProcessingError(
    "Failed to parse LDIF",
    context={"file": "data.ldif"}
)
```

#### After (Standard usage)

```python
# ✅ NEW USAGE - Clean and consistent
raise client-aOudMigExceptions.MigrationError(
    "Migration failed",
    operation="validate",
    context={"phase": "pre-migration"}
)

# ✅ NEW USAGE - With correlation ID
raise client-aOudMigExceptions.LdifProcessingError(
    "Failed to parse LDIF",
    ldif_file="data.ldif",
    correlation_id="mig_run_123",
    context={"entry_count": 150}
)
```

#### Find and Replace Strategy

1. **Find all exception raises**:

   ```bash
   grep -r "raise.*Exceptions\." src/ | grep -v "__pycache__" | grep -v ".pyc"
   ```

2. **Update each occurrence**:
   - Remove leading underscore from exception class name (e.g., `_MigrationError` → `MigrationError`)
   - Add domain-specific fields as named parameters
   - Keep `context` for additional fields
   - Add `correlation_id` where distributed tracing is needed

3. **Example replacements**:

   ```python
   # BEFORE
   raise client-aOudMigExceptions._client-aValidationError(
       "Validation failed",
       field="email",
       value="invalid@",
       context={"rules": "email_format"}
   )

   # AFTER
   raise client-aOudMigExceptions.client-aValidationError(
       "Validation failed",
       field="email",
       value="invalid@",
       context={"rules": "email_format"}
   )
   ```

---

### Step 4: Update Factory Methods (If Present)

**Goal**: Convert factory methods to follow standard pattern or remove them if redundant.

#### Before (Factory pattern)

```python
# ❌ OLD PATTERN - Factory methods
class FlextLdapExceptions(FlextExceptions):
    def connection_error(
        self,
        message: str,
        server_uri: str,
        ldap_code: int | None = None,
    ) -> Exception:
        """Create connection error."""
        return self.LdapConnectionError(
            message, server_uri=server_uri, ldap_code=ldap_code
        )

# ❌ Usage requires instance
exceptions = FlextLdapExceptions()
raise exceptions.connection_error("Failed", "ldap://localhost:389")
```

#### After (Direct instantiation)

```python
# ✅ NEW PATTERN - Direct instantiation (no factory needed)
class FlextLdapExceptions:
    class LdapConnectionError(FlextExceptions.BaseError):
        """LDAP connection error."""
        # ... standard pattern implementation

# ✅ Usage is clean and consistent
raise FlextLdapExceptions.LdapConnectionError(
    "Failed to connect",
    server_uri="ldap://localhost:389",
    ldap_code=91
)
```

**Decision**: If factory methods provide **business value** (e.g., complex error construction logic), keep them as **static methods**. Otherwise, remove and use direct instantiation.

**Keep factories if**:

```python
# ✅ Factory provides business value
@staticmethod
def create_from_ldap_exception(
    ldap_error: Exception,
    server_uri: str,
) -> LdapConnectionError:
    """Create connection error from ldap3 exception."""
    ldap_code = getattr(ldap_error, 'result', {}).get('resultCode')
    message = getattr(ldap_error, 'message', str(ldap_error))

    return FlextLdapExceptions.LdapConnectionError(
        message,
        server_uri=server_uri,
        ldap_code=ldap_code,
        context={"original_error": type(ldap_error).__name__}
    )
```

---

### Step 5: Run Tests and Validation

**Goal**: Ensure migration didn't break anything.

#### Validation Commands

```bash
# 1. Type checking (MyPy strict)
mypy src/ --strict

# 2. Linting (Ruff)
ruff check src/

# 3. Run tests
pytest tests/ -v

# 4. Test coverage
pytest --cov=src --cov-report=term-missing

# 5. Validate exception pattern compliance
python -c "
from src.project_name.exceptions import ProjectExceptions
from flext_core import FlextExceptions

# Verify exceptions extend BaseError
assert issubclass(ProjectExceptions.MainError, FlextExceptions.BaseError), 'Must extend BaseError'

# Verify helper methods exist (inherited from BaseError)
assert hasattr(ProjectExceptions.MainError, '_extract_common_kwargs'), 'Missing helper method'
assert hasattr(ProjectExceptions.MainError, '_build_context'), 'Missing helper method'

print('✅ Exception pattern compliance verified')
"
```

#### Common Migration Errors

**Error 1**: Type annotation issues

```python
# ❌ WRONG
def __init__(self, message: str, *, context: dict | None = None) -> None:
    # dict is too generic

# ✅ CORRECT
def __init__(self, message: str, *, **kwargs: object) -> None:
    # Use **kwargs and extract context via helper
```

**Error 2**: Missing correlation_id support

```python
# ❌ WRONG - Doesn't accept correlation_id
raise MyError("Failed", field="email")

# ✅ CORRECT - Accepts correlation_id via **kwargs
raise MyError("Failed", field="email", correlation_id="req_123")
```

**Error 3**: Hardcoded context instead of using helper

```python
# ❌ WRONG
context = {"field": field, "value": value}
super().__init__(message, context=context)

# ✅ CORRECT
context = self._build_context(base_context, field=field, value=value)
super().__init__(message, context=context, correlation_id=correlation_id)
```

---

### Step 6: Update Public Exports

**Goal**: Ensure exception classes are properly exported.

#### Before

```python
# ❌ OLD - Private class exports
class client-aOudMigExceptions(FlextExceptions):
    # ... exception definitions with _ prefix

    # Public exports at end of class
    MigrationError = _MigrationError
    FileError = _FileError
    # ... more exports
```

#### After

```python
# ✅ NEW - Direct public classes (no _ prefix needed)
class client-aOudMigExceptions:
    """client-a OUD Migration exception hierarchy."""

    class MigrationError(FlextExceptions.BaseError):
        """Base exception for migration-related errors."""
        # ... standard pattern implementation

    class FileError(MigrationError):
        """File operation error."""
        # ... standard pattern implementation

    # No need for public exports - classes are already public
```

#### Update **all** exports

```python
# exceptions.py
__all__ = ["client-aOudMigExceptions"]

# __init__.py (if exposing individual exceptions)
from .exceptions import client-aOudMigExceptions

__all__ = [
    "client-aOudMigExceptions",
    # OR expose individual exceptions for convenience:
    # "MigrationError",
    # "LdifProcessingError",
]
```

---

## 🔍 Validation Checklist

Before considering migration complete:

- [ ] All exception classes extend `FlextExceptions.BaseError`
- [ ] All exception classes use `_extract_common_kwargs()` helper
- [ ] All exception classes use `_build_context()` helper
- [ ] All exception classes accept `**kwargs: object` parameter
- [ ] All exception classes support `correlation_id` via kwargs
- [ ] All exception classes have domain-specific error codes
- [ ] All exception classes have `@override` decorator
- [ ] All exception classes have complete type annotations
- [ ] All exception classes have docstrings
- [ ] All exception usages updated to new class names (no `_` prefix)
- [ ] All tests pass (`pytest tests/`)
- [ ] Type checking passes (`mypy src/ --strict`)
- [ ] Linting passes (`ruff check src/`)
- [ ] Factory methods removed or converted to static helpers
- [ ] Public exports updated in `__all__`
- [ ] Documentation updated with new exception patterns

---

## 📊 Migration Progress Tracking

Use this table to track migration progress across projects:

| Project          | Status         | Issues Found                        | Time Spent | Completed  |
| ---------------- | -------------- | ----------------------------------- | ---------- | ---------- |
| flext-core       | ✅ Complete    | None - reference implementation     | -          | 2025-10-01 |
| flext-api        | ✅ Complete    | None - reference implementation     | -          | 2025-10-01 |
| flext-ldap       | ⏳ In Progress | Factory pattern, missing helpers    | -          | -          |
| flext-tap-oracle | ✅ Complete    | Minor - error code improvements     | -          | 2025-10-01 |
| client-a-oud-mig    | ⏳ Planned     | Critical - doesn't extend BaseError | -          | -          |
| ...              | ...            | ...                                 | ...        | ...        |

---

## 🎯 Quick Reference

### Conversion Quick Guide

1. **Change base class**: `Exception` → `FlextExceptions.BaseError`
2. **Add `**kwargs`**: Accept `\*\*kwargs: object` parameter
3. **Extract common params**: Call `self._extract_common_kwargs(kwargs)`
4. **Build context**: Call `self._build_context(base_context, field1=value1, ...)`
5. **Call super**: Pass `message`, `code`, `context`, `correlation_id` to `super().__init__(...)`
6. **Remove `_` prefix**: Make classes public (e.g., `_MyError` → `MyError`)
7. **Add `@override`**: Decorate `__init__` method
8. **Add docstrings**: Document class, attributes, and parameters

### Common Patterns

**Simple exception**:

```python
class MyError(FlextExceptions.BaseError):
    @override
    def __init__(self, message: str, *, field: str | None = None, **kwargs: object) -> None:
        self.field = field
        base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)
        context = self._build_context(base_context, field=field)
        super().__init__(message, code=error_code or "MY_ERROR", context=context, correlation_id=correlation_id)
```

**Specialized exception**:

```python
class SpecializedError(MyError):
    @override
    def __init__(self, message: str, *, extra_field: str | None = None, **kwargs: object) -> None:
        self.extra_field = extra_field
        base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)
        context = self._build_context(base_context, extra_field=extra_field)
        super().__init__(message, field="auto_set", code=error_code or "SPECIALIZED_ERROR", context=context, correlation_id=correlation_id, **kwargs)
```

---

## 🆘 Troubleshooting

### Issue: MyPy errors after migration

**Symptom**: `error: Signature of "__init__" incompatible with supertype "BaseError"`

**Solution**: Ensure parameter order matches parent:

```python
# ✅ CORRECT parameter order
def __init__(
    self,
    message: str,  # Required positional
    *,             # Keyword-only separator
    field: str | None = None,  # Domain-specific fields
    **kwargs: object,  # Extensibility
) -> None:
```

### Issue: Correlation ID not propagating

**Symptom**: Correlation IDs are lost when re-raising exceptions

**Solution**: Always pass `correlation_id` when re-raising:

```python
try:
    do_something()
except MyError as e:
    raise MyError(
        f"Operation failed: {e.message}",
        field=e.field,
        correlation_id=e.correlation_id,  # ✅ Propagate correlation ID
        context={"original_error": str(e)}
    ) from e
```

### Issue: Tests failing after migration

**Symptom**: Tests expect old exception class names

**Solution**: Update test assertions:

```python
# ❌ OLD
with pytest.raises(client-aOudMigExceptions._MigrationError):

# ✅ NEW
with pytest.raises(client-aOudMigExceptions.MigrationError):
```

---

**Document Authority**: FLEXT Ecosystem Migration Guide
**Version**: 1.0.0 (2025-10-03)
**Next**: Apply to projects identified in quality assessment
