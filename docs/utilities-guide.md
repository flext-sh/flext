# FLEXT Utilities Usage Guide

**Last Updated**: 2025-12-28
**Version**: 1.0.0

---

## Overview

This guide documents the centralized utilities system in the FLEXT ecosystem. All generic utility functionality is
centralized in `flext-core`, with domain-specific utilities added in each project library.

## Utilities Architecture

### Inheritance Hierarchy

```text
FlextUtilities (flext-core) - Foundation utilities
   ↓
FlextLdifUtilities (flext-ldif) - Extends with LDIF-specific utilities
   ↓
FlextLdapUtilities (flext-ldap) - Extends with LDAP-specific utilities
   ↓
FlextCliUtilities (flext-cli) - Extends with CLI-specific utilities
```

### Import Pattern (MANDATORY)

```python
# ✅ CORRECT - Use short alias
from flext_core import u

# Access centralized utilities
result = u.to_str("value")
result = u.get(data, "key")
matches = u.find_callable(predicates, value)

# ❌ FORBIDDEN - Direct internal imports
from flext_core import FlextUtilitiesConversion
```

---

## Centralized Utilities in flext-core

### Core Classes (20+ utility classes)

| Class                           | Namespace       | Purpose                             | Count   |
| ------------------------------- | --------------- | ----------------------------------- | ------- |
| **FlextUtilitiesConversion**    | `u`             | Value type conversion (3 methods)   | NEW     |
| **FlextUtilitiesMapper**        | `u`             | Data structure mapping (91 methods) | UPDATED |
| **FlextUtilitiesCollection**    | `u`             | List/dict/set operations            | 40+     |
| **FlextUtilitiesValidator**     | `u.Validator`   | Value validation                    | 30+     |
| **FlextUtilitiesParser**        | `u`             | String/data parsing                 | 25+     |
| **FlextUtilitiesPattern**       | `u.Pattern`     | Regex pattern matching              | 20+     |
| **FlextUtilitiesGuards**        | `u`             | Type guards and narrowing           | 20+     |
| **FlextUtilitiesCast**          | `u.Cast`        | Type casting utilities              | 15+     |
| **FlextUtilitiesText**          | `u`             | String manipulation                 | 20+     |
| **FlextUtilitiesEnum**          | `u`             | Enum utilities                      | 10+     |
| **FlextUtilitiesContext**       | `u.Context`     | Context/state management            | 8+      |
| **FlextUtilitiesCache**         | `u`             | Caching utilities                   | 5+      |
| **FlextUtilitiesConfiguration** | `u`             | Settings handling                   | 8+      |
| **FlextUtilitiesDomain**        | `u`             | Domain model utilities              | 10+     |
| **FlextUtilitiesDeprecation**   | `u.Deprecation` | Deprecation handling                | 4       |
| **FlextUtilitiesGenerators**    | `u`             | Data generators                     | 10+     |
| **FlextUtilitiesModel**         | `u`             | Pydantic model utilities            | 12+     |
| **FlextUtilitiesPagination**    | `u`             | Pagination utilities                | 5+      |
| **FlextUtilitiesReliability**   | `u`             | Retry/circuit breaker               | 8+      |
| **FlextUtilitiesValidation**    | `u.Validation`  | Data validation                     | 15+     |
| **FlextUtilitiesChecker**       | `u`             | Type/value checking                 | 12+     |
| **FlextUtilitiesArgs**          | `u`             | CLI argument handling               | 8+      |

**Total**: 548+ centralized utility methods in flext-core

### New Methods (Added December 28, 2025)

#### 1. `FlextUtilitiesConversion.to_str_list_safe()`

**Purpose**: Safe conversion to list of strings, filtering nested list structures

**Signature**:

```python
@staticmethod
def to_str_list_safe(
    value: m.Tests.ListInputModel, *, filter_list_like: bool = True
) -> t.StrSequence:
    """Convert value to t.StrSequence with safe nested list handling."""
```

**Usage**:

```python
from flext_core import u

# Simple values
result = u.to_str_list_safe("hello")
# → ["hello"]

# Lists with nested structures
result = u.to_str_list_safe(["a", "b", ["nested"]], filter_list_like=True)
# → ["a", "b"]  # Nested list filtered out

# Disable filtering
result = u.to_str_list_safe(["a", ["b"]], filter_list_like=False)
# → ["a", "[b]"]  # Nested list converted to string
```

**Use Cases**:

- Flatten mixed data structures to flat strings
- Prevent deeply nested lists in results
- Safe user input processing

#### 2. `FlextUtilitiesConversion.to_str_list_truthy()`

**Purpose**: Safe conversion to list of strings, filtering falsy values

**Signature**:

```python
@staticmethod
def to_str_list_truthy(value: m.Tests.ListInputModel) -> t.StrSequence:
    """Convert value to t.StrSequence filtering out falsy values."""
```

**Usage**:

```python
from flext_core import u

# Filter falsy values
result = u.to_str_list_truthy(["a", "", "b", None])
# → ["a", "b"]  # Empty strings and None removed

# Single value
result = u.to_str_list_truthy("test")
# → ["test"]

# Empty/falsy input
result = u.to_str_list_truthy(None)
# → []
```

**Use Cases**:

- Clean up lists with empty/None values
- Filter empty strings from results
- Prepare data for downstream processing

#### 3. `FlextUtilitiesMapper.find_callable()`

**Purpose**: Find first matching predicate from dictionary of predicates

**Signature**:

```python
@staticmethod
def find_callable[T](
    callables: t.MappingKV[str, _Predicate[T]], value: T
) -> str | None:
    """Find first matching callable key from dict of predicates."""
```

**Usage**:

```python
from flext_core import u

# Define predicates
predicates = {
    "is_empty": lambda v: len(v) == 0,
    "is_single": lambda v: len(v) == 1,
    "is_multiple": lambda v: len(v) > 1,
}

# Find matching predicate
result = u.find_callable(predicates, [1, 2])
# → "is_multiple"

result = u.find_callable(predicates, [])
# → "is_empty"

result = u.find_callable(predicates, "no_match")
# → None  # No predicate matched
```

**Use Cases**:

- Pattern matching on values
- Dynamic dispatch based on predicates
- Classification of input types
- Safe predicate evaluation (failures ignored)

---

## Project-Specific Utilities

### flext-ldif Utilities (extending flext-core)

**Namespace**: `u.Ldif.*`

**Domain-specific utilities** (NOT in flext-core):

- LDIF entry parsing and validation
- DN (Distinguished Name) manipulation
- LDIF schema handling
- Change record processing
- Custom LDIF operations

**Example**:

```python
from flext_ldif import u

# Use inherited methods from flext-core
result = u.to_str_list(values)  # Inherited

# Use LDIF-specific methods
entry = u.Ldif.parse_entry(ldif_data)  # Domain-specific
```

### flext-ldap Utilities (extending flext-ldif)

**Namespace**: `u.Ldap.*`

**Domain-specific utilities** (NOT in flext-core):

- LDAP directory operations
- Active Directory integration
- User/group management
- Authentication/authorization
- LDAP filter building

### flext-cli Utilities (extending flext-core)

**Namespace**: `u.Cli.*`

**Domain-specific utilities** (NOT in flext-core):

- Command-line argument parsing
- Interactive prompts
- Output formatting
- Progress indicators
- Configuration file loading

### Migration Utilities (extending all)

**Namespace**: `u.Migration.*`

**Domain-specific utilities** (NOT in flext-core):

- OUD migration-specific operations
- Data transformation for migration
- Validation rules for migration
- Progress tracking

---

## Best Practices

### DO's ✅

1. **Use short aliases**: `from flext_core import u`
2. **Access via namespace**: `u.method()`, `u.method()`
3. **Chain operations**: `u.filter(...).map(...)`
4. **Inherit for domain extensions**: Extend `FlextUtilities` for project-specific utilities
5. **Reuse existing methods**: Check if method already exists before adding
6. **Use full namespaces in type hints**: `u.to_str()`

### DON'Ts ❌

1. **Don't import internal modules**: ❌ `from flext_core import ...`
2. **Don't re-implement**: ❌ Create your own string conversion if `u.*` exists
3. **Don't mix namespaces**: ❌ `from flext_core import FlextUtilities`
4. **Don't use module imports**: ❌ `from flext_core import utilities as util`
5. **Don't create new utility classes at same level**: ❌ Extend in your project, not flext-core root

---

## Adding New Utilities

### When to Add to flext-core

Add utility method to flext-core when:

1. **Generic pattern** - Used by 2+ projects
2. **No existing method** - Method doesn't already exist
3. **Type-safe** - Proper type annotations without `Any` or `cast()`
4. **Well-tested** - Real tests, no mocks
5. **Documented** - Clear docstring with examples

### How to Add

1. **Choose appropriate class**: Add to existing `FlextUtilities*` class
2. **Follow patterns**: Use `@staticmethod`, proper typing, error handling
3. **Add to `**all**`**: Export from the module
4. **Test**: Create tests in `tests/unit/`
5. **Update this guide**: Document in "New Methods" section

### Example: Add new utility method

```python
# In src/flext_core/_utilities/conversion.py

class FlextUtilitiesConversion:
    @staticmethod
    def new_method(value: m.Tests.UtilityInputModel) -> p.Result[str]:
        """New utility method."""
        try:
            result = ...process value...
            return r[str].ok(result)
        except Exception as e:
            return r[str].fail(f"Error: {e}")

    # **all**: list[str] = ["FlextUtilitiesConversion"]  # Already exported
```

---

## Quality Standards

All utilities must meet:

- ✅ **Type Safety**: Full type annotations, no `Any` or `cast()`
- ✅ **Testing**: 100% test coverage with real implementations
- ✅ **Documentation**: Clear docstrings with examples
- ✅ **Error Handling**: r pattern for fallible operations
- ✅ **Performance**: No unnecessary complexity or allocations
- ✅ **Code Quality**: MyPy strict, Ruff lint, zero violations

---

## See Also

- `AGENTS.md` - Overall architecture patterns and workspace implementation details
- `README.md` - General project information

---

**Questions?** File an issue at <https://github.com/anthropics/flext/issues>
