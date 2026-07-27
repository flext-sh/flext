# FLEXT Type System Architecture Guide

**Version**: 1.0.0
**Last Updated**: 2025-12-10
**Scope**: Complete FLEXT ecosystem type system
**Status**: Specification and reference

---

## Table of Contents

1. [Overview](#overview)
2. [Type System Hierarchy](#type-system-hierarchy)
3. [Canonical Type Patterns](#canonical-type-patterns)
4. [Namespace Architecture](#namespace-architecture)
5. [Covariance and Variance Rules](#covariance-and-variance-rules)
6. [Design](#protocol-design)
7. [TypeVar Organization](#typevar-organization)
8. [Migration Guide](#migration-guide)
9. [Best Practices](#best-practices)
10. [Project Status](#project-status)

---

## Overview

The FLEXT type system provides a unified, composable type architecture across the core FLEXT projects:

1. **flext-core** - Foundation library with TypeVars, Protocols, and base types
2. **flext-cli** - Command-line interface with CLI-specific types
3. **flext-ldif** - LDIF processing domain library
4. **flext-ldap** - LDAP operations library

**Key Principles**:

- **2-level namespace maximum**: `t.Domain.Concept` (never `t.Domain.Concern.SubConcern.Type`)
- **Covariance first**: Use `Mapping`/`Iterable` instead of `dict`/`Sequence` in protocols
- **Single source of truth**: No duplicate type definitions across namespace levels
- **Protocol-based design**: Complex unions → Protocols for extensibility
- **TypeVar centralization**: Use flext-core TypeVars, add domain-specific only when necessary
- **Complete namespace always**: Never use root-level aliases or convenience methods

---

## Type System Hierarchy

### Project Dependency Order

```text
flext-core (Foundation - No dependencies)
    ↓
flext-cli (depends on flext-core)
flext-ldif (depends on flext-core)
    ↓
flext-ldap (depends on flext-core, flext-ldif)
```

### Architecture Layering within Projects

**Tier 0 - Foundation (ZERO internal dependencies)**:

- `constants.py` - StrEnum, Final, Literal definitions only
- `typings.py` - Type aliases, TypeVars
- `protocols.py` - Interface definitions (Protocol classes)

**Tier 1 - Domain Foundation**:

- `models.py` - Pydantic models (depends on: constants, typings, protocols)
- `utilities.py` - Helper functions (depends on: constants, typings, protocols, models)

**Tier 2 - Infrastructure**:

- `services/*.py` - Business logic (depends on: Tier 0, Tier 1)

**Tier 3 - Application**:

- `api.py` - Facade/API (depends on: all lower tiers)
- CLI/commands modules (depends on: all lower tiers)

---

## Canonical Type Patterns

### Pattern 1: Simple Type Contract (No Namespace Needed)

**When**: Single-purpose type, used rarely, clearly scoped

```python
# Use canonical contracts from runtime facades (never bare generic types)
type ScalarLike = t.Scalar

# Usage: keep values in strict canonical contracts
result: m.Domain.ValueModel = json_value
```

### Pattern 2: Domain Collection Type (Nested Namespace)

**When**: Related collection types for same domain

```python
class FlextCliTypes:
    class Cli:
        class Data:
            # Collection types grouped by domain
            type RowData = t.MappingKV[str, m.Cli.RowModel]
            type CellContent = t.Primitives | None
```

### Pattern 3: TypeVar Bounded to Protocol (Avoiding Circular Imports)

**When**: Need generic type but importing Protocol causes circular dependency

```python
# In typings.py (Tier 0)
FlextFlextDemoMigrationEntryT = TypeVar(
    "FlextFlextDemoMigrationEntryT", bound="fldif.Ldif.Entry"
)


# In protocols.py (Tier 0) - declare actual protocol
@runtime_checkable
class EntryService[T: "fldif.Ldif.Entry"](Protocol):
    """Service for entry operations with generic type parameter."""

    def get(
        self, dn: str
    ) -> "FlextDemoMigrationProtocols.FlextDemoMigration.Result[T]": ...
```

### Pattern 4: Union → Protocol (Complexity Reduction)

**When**: Multiple Callable variants (3+ combinations)

```python
# ❌ BEFORE: 5 union variants (complex, less extensible)
type ProgressCallback = (
    Callable[[int], None]
    | Callable[[int, int], None]
    | Callable[[int, int, str], None]
    | Callable[[m.Cli.ProgressEventModel], None]
    | Callable[[Exception], None]
)


# ✅ AFTER: Protocol-based (extensible, maintainable)
@runtime_checkable
class ProgressCallback(Protocol):
    """Flexible callback protocol for progress tracking."""

    def **call**(self, event: m.Cli.ProgressEventModel) -> None:
        """Accept any arguments for maximum flexibility."""
        ...
```

### Pattern 5: Covariance in Protocols

**Rule**: Read-only protocols use `Mapping`/`Iterable`, not `dict`/`Sequence`

```python
# ❌ WRONG: Invariant dict (rejects Mapping-compatible inputs)
class DataProvider(Protocol):
    def get_data(self) -> t.MappingKV[str, m.Tests.ValueModel]: ...


# ✅ CORRECT: Covariant Mapping (accepts multiple mapping implementations)
class DataProvider(Protocol):
    def get_data(self) -> t.MappingKV[str, m.Tests.ValueModel]: ...


# Usage: Works with any dict subtype
def process_data(provider: DataProvider) -> None:
    # Provider can return t.IntMapping, t.StrMapping, etc.
    data = provider.get_data()
    ...
```

### Pattern 6: TypeVar Reuse (Centralized)

**Rule**: Use flext-core TypeVars, add domain-specific only when absolutely necessary

```python
# ✅ CORRECT: Use centralized TypeVars from flext-core
from flext_core import t

T = T  # Generic type variable
M = t.M  # Generic mapping type
S = t.S  # Generic sequence type
R = t.R  # Generic result type
E = t.E  # Generic exception type

# ❌ WRONG: Creating redundant domain-specific TypeVars
FlextCliCommandT = TypeVar("FlextCliCommandT", bound="CliCommand")  # NO - use generic T
FlextCliOutputT = TypeVar("FlextCliOutputT")  # NO - use generic R
```

---

## Namespace Architecture

### Standard Namespace Structure

```python
# CORRECT: 2-level maximum nesting
class FlextTypes:
    class Core:
        type Result[T] = "r[T]"

    class Utilities:
        type SettingsData = t.MappingKV[str, m.Tests.SettingsEntryModel]


# Usage
result: t.Tests.Result[bool] = ok_result
data: t.Utilities.SettingsData = {"key": m.Tests.SettingsEntryModel(value="value")}


# ❌ WRONG: Over-nesting (3+ levels)
class FlextTypes:
    class Domain:
        class Subdomain:
            class Details:
                type SomeType = str  # TOO DEEP!
```

### Namespace Organization by Project

**flext-core**:

```text
t.Tests                      # Foundation (Result, Settings, Handler)
t.Utilities                 # Reusable (Json, Collection, Validation)
t.Exceptions                # Error types
t.Constants                 # Enum definitions
t.Decorators                # Type decorators
```

**flext-cli**:

```text
t.Cli                       # CLI-specific
  .Data                     # Data structures (Tables, Progress)
  .Output                   # Output formats (Table, JSON, YAML)
  .Auth                     # Authentication
```

**flext-ldif**:

```text
t.Ldif                      # LDIF domain
  .Entry                    # Entry types
  .Attribute                # Attribute types
  .Schema                   # Schema types
  .ModelMetadata            # Model metadata
```

**flext-ldap**:

```text
t.Ldap                      # LDAP operations
  .Client                   # Client types
  .Connection               # Connection types
  .Operation                # Operation types
t.Ldap.Protocol             # Infrastructure (ldap3 wrappers)
```

### Models Namespace Architecture (m.\*)

**CRITICAL RULE**: Models follow **2-level maximum** namespace: `m.Domain.Class` (not `m.Domain.Concern.SubClass`)

**Pattern**: Domain-level classes directly in namespace, no nested sub-namespaces

```python
# ✅ CORRECT: 2-level namespace (flext-cli examples)
m.Cli.SystemInfo  # CLI-specific system info model
m.Cli.SessionStatistics  # CLI session statistics
m.Cli.CommandStatistics  # CLI command statistics
m.Cli.CliCommand  # CLI command model
m.Cli.CliSession  # CLI session model

# ✅ CORRECT: Module-level aliases for common classes
from flext_cli import (
    SystemInfo,  # alias for m.Cli.SystemInfo
    SessionStatistics,  # alias for m.Cli.SessionStatistics
    CommandStatistics,  # alias for m.Cli.CommandStatistics
)

# ❌ WRONG: Over-nesting (3+ levels - PROHIBITED)
m.Cli.Value.SystemInfo  # TOO DEEP - violates 2-level rule
m.Cli.Data.Command.Execution  # TOO DEEP - nested sub-concerns

# ❌ WRONG: Root-level aliases without domain
m.SystemInfo  # Missing domain context (m.Cli.*)
m.Statistics  # Ambiguous - which domain?
```

**Models Organization by Project**:

**flext-core**:

```text
m.Settings                    # Configuration models
m.ProcessingSettings          # Processing-specific settings
m.RuntimeScopeOptions       # Runtime options
m.Options                   # Generic options
```

**flext-cli**:

```text
m.Cli                       # CLI domain
  .CliCommand               # Command model
  .CliSession               # Session model
  .CliSettings                # CLI configuration
  .SystemInfo               # System information (module alias available)
  .EnvironmentInfo          # Environment info (module alias available)
  .PathInfo                 # Path information (module alias available)
  .CommandStatistics        # Command stats (module alias available)
  .SessionStatistics        # Session stats (module alias available)
  .ServiceExecutionResult   # Service result (module alias available)
```

**flext-ldif**:

```text
m.Ldif                      # LDIF domain
  .Entry                    # LDIF entry
  .Attribute                # LDIF attribute
  .Schema                   # LDIF schema
```

**flext-ldap**:

```text
m.Ldap                      # LDAP domain
  .Connection               # Connection model
  .Operation                # Operation model
  .Result                   # Operation result
```

---

## Covariance and Variance Rules

### Covariance (Subtype Compatibility)

```python
# Example: t.BoolMapping should be compatible with t.MappingKV[str, m.Tests.ValueModel]

# ❌ INVARIANT - WRONG
def process_dict(data: t.MappingKV[str, m.Tests.ValueModel]) -> None: ...


result: t.BoolMapping = {"ok": True}
process_dict(result)  # Type error: dict is invariant

# ✅ COVARIANT - CORRECT
from collections.abc import Mapping


def process_mapping(data: t.MappingKV[str, m.Tests.ValueModel]) -> None: ...


result: t.BoolMapping = {"ok": True}
process_mapping(result)  # OK: Mapping is covariant
```

### Protocol Return Types (Always Covariant)

```python
# ✅ CORRECT: Return type uses covariant Mapping
@runtime_checkable
class DataProvider(Protocol):
    def get_attributes(self) -> t.MappingKV[str, t.StrSequence]:
        """Returns read-only attributes - covariant."""
        ...


# Implementation can return more specific dict type
class MyProvider:
    def get_attributes(self) -> t.MappingKV[str, t.StrSequence]:
        return {"cn": ["test"], "mail": ["user@example.com"]}


provider: DataProvider = MyProvider()  # OK: dict is assignable to Mapping
```

### Type Parameter Bounds (Always Covariant)

```python
# ✅ CORRECT: Use Iterable (covariant) not Sequence (invariant)
@runtime_checkable
class ItemProcessor(Protocol):
    def process_items(self, items: Iterable[str]) -> None:
        """Accepts any iterable source."""
        ...


# ❌ WRONG: Sequence is invariant
@runtime_checkable
class ItemProcessor(Protocol):
    def process_items(self, items: t.StrSequence) -> None:
        """Too restrictive - can't accept list subclasses."""
        ...
```

---

## Protocol Design

### Protocol Organization Rules

**Rule 1**: Protocols NEVER import Models, Settings, or concrete classes

```python
# ✅ CORRECT: Protocols only import other Protocols
from typing import Protocol


@runtime_checkable
class Entry(Protocol):
    dn: str
    attributes: t.MappingKV[str, t.StrSequence]


# ❌ WRONG: Don't import concrete classes
from flext_ldif import Entry  # NO


@runtime_checkable
class Entry(Protocol):
    entry: Entry  # NO - creates circular dependency
```

**Rule 2**: Protocol Composition (Extends)

```python
# ✅ CORRECT: Protocols extend other protocols
@runtime_checkable
class ReadableEntry(Protocol):
    """Read-only entry access."""

    @property
    def dn(self) -> str: ...


@runtime_checkable
class MutableEntry(ReadableEntry, Protocol):
    """Mutable entry with write operations."""

    def set_attribute(self, name: str, values: t.StrSequence) -> Self: ...
```

**Rule 3**: @runtime_checkable for isinstance() Checks

```python
# ✅ CORRECT: Use @runtime_checkable for runtime validation
from typing import Protocol, runtime_checkable


@runtime_checkable
class Entry(Protocol):
    dn: str
    attributes: t.MappingKV[str, t.StrSequence]


# Can now use isinstance() at runtime
if isinstance(obj, Entry):
    u.Cli.print(f"DN: {obj.dn}")
```

**Rule 4**: Self Type for Method Chaining

```python
# ✅ CORRECT: Use Self for fluent interface
from typing import Self


@runtime_checkable
class MutableEntry(Protocol):
    def set_attribute(self, name: str, values: t.StrSequence) -> Self:
        """Returns self for method chaining."""
        ...


# Usage: Fluent interface
entry.set_attribute("mail", ["new@example.com"]).add_attribute("cn", ["User"])
```

---

## TypeVar Organization

### Centralized TypeVars (flext-core)

```python
# flext-core/src/flext_core/typings.py

# Generic type variables (reuse in all projects)
T = TypeVar("T")  # Generic type
M = TypeVar("M")  # Generic mapping/model
S = TypeVar("S")  # Generic sequence
R = TypeVar("R")  # Generic result
E = TypeVar("E", bound=BaseException)  # Generic exception
P = TypeVar("P")  # Generic protocol
U = TypeVar("U")  # Generic utility

# Bound TypeVars
FlextModelT = TypeVar("FlextModelT", bound="FlextModels.Model")
FlextServiceT = TypeVar("FlextServiceT", bound="s")
```

### Domain-Specific TypeVars (When Necessary)

```python
# ✅ ONLY add domain TypeVars if truly specialized
# Example: a workspace-specific migration package has specialized entry types

FlextFlextDemoMigrationEntryT = TypeVar(
    "FlextFlextDemoMigrationEntryT",
    bound="fldif.Ldif.Entry",  # Protocol-bound to avoid circular imports
)

# ❌ DON'T create redundant TypeVars
FlextCliCommandT = TypeVar("FlextCliCommandT")  # NO - use T
FlextCliOutputT = TypeVar("FlextCliOutputT")  # NO - use R
```

---

## Migration Guide

### Migrating from Old Patterns to New

#### Migration 1: Union → Protocol

**Before**:

```python
type ProgressCallback = (
    Callable[[int], None] | Callable[[int, int], None] | Callable[[int, int, str], None]
)


def track_progress(callback: ProgressCallback) -> None:
    callback(50)
    callback(50, 100)
    callback(50, 100, "processing")
```

**After**:

```python
@runtime_checkable
class ProgressCallback(Protocol):
    def **call**(self, event: m.Cli.ProgressEventModel) -> None: ...


def track_progress(callback: ProgressCallback) -> None:
    callback(50)
    callback(50, 100)
    callback(50, 100, "processing")
```

**Benefits**: Extensible, clearer intent, supports any argument combination

---

#### Migration 2: dict → Mapping in Protocols

**Before**:

```python
@runtime_checkable
class AttributeProvider(Protocol):
    def get_attributes(self) -> t.MappingKV[str, t.StrSequence]: ...


# Can only accept exact t.MappingKV[str, t.StrSequence]
result: t.BoolMapping = {"ok": True}
provider.get_attributes()  # May fail type check
```

**After**:

```python
@runtime_checkable
class AttributeProvider(Protocol):
    def get_attributes(self) -> t.MappingKV[str, t.StrSequence]: ...


# Can accept any dict subtype or Mapping implementation
result: t.BoolMapping = {"ok": True}
provider.get_attributes()  # Works with covariance
```

**Benefits**: Better type compatibility, standard library alignment

---

#### Migration 3: Duplicate Aliases → Single Source of Truth

**Before**:

```python
# typings.py (Tier 0)
class FlextLdapTypes:
    class Ldap:
        type ModifyChanges = t.MappingKV[str, t.SequenceOf[tuple[str, t.StrSequence]]]

    class Ldap:
        class Operation:
            type ModifyChanges = t.MappingKV[
                str, t.SequenceOf[tuple[str, t.StrSequence]]
            ]  # DUPLICATE


# Confusion: Which one to use?
```

**After**:

```python
# typings.py (Tier 0) - Single definition
class FlextLdapTypes:
    class Ldap:
        type ModifyChanges = t.MappingKV[str, t.SequenceOf[tuple[str, t.StrSequence]]]

        # Backward compatibility (remove after 2-3 releases)
        class Operation:
            ModifyChanges = Ldap.ModifyChanges


# Clear: One source of truth
```

**Benefits**: No redundancy, easier maintenance, clearer dependencies

---

## Best Practices

### 1. Use Complete Namespace Always

```python
# ✅ CORRECT
from flext_ldif import m

entry = m.Ldif.Entry(dn="cn=test")
attributes = m.Ldif.AttributeDict()

# ❌ WRONG - Convenience aliases
entry = m.Entry(dn="cn=test")  # NO
attributes = m.AttributeDict()  # NO
```

### 2. No cast(), tipagem frouxa, ou TYPE_CHECKING

```python
# ✅ CORRECT: Use Models and Protocols
def process_model(
    data: t.MappingKV[str, m.Domain.InputModel],
) -> p.Result[m.Domain.OutputModel]:
    return r.ok(SomeModel(data))


# ❌ WRONG: cast() hides type issues
def process_model(
    data: t.MappingKV[str, m.Domain.InputModel],
) -> p.Result[m.Domain.OutputModel]:
    return r.ok(cast(SomeModel, data))


# ❌ WRONG: TYPE_CHECKING (fix circular import instead)
if TYPE_CHECKING:
    from flext_ldif import ParserService
```

### 3. Covariant Protocols for Read-Only

```python
# ✅ CORRECT: Mapping for read-only
def read_attributes(attrs: t.MappingKV[str, t.StrSequence]) -> None:
    for key, values in attrs.items():
        u.Cli.print(f"{key}: {values}")


# ❌ WRONG: dict for read-only (invariant)
def read_attributes(attrs: t.MappingKV[str, t.StrSequence]) -> None:
    for key, values in attrs.items():
        u.Cli.print(f"{key}: {values}")
```

### 4. TypeVar with Proper Bounds

```python
# ✅ CORRECT: Clear bounds
T = TypeVar("T")  # Generic any type
M = TypeVar("M", bound="FlextModels.Model")  # Specific bound
E = TypeVar("E", bound=BaseException)  # Exception bound

# ❌ WRONG: Unclear or missing bounds
T = TypeVar("T", int, str, bool)  # Limited union (use overloads)
M = TypeVar("M")  # Missing bound
```

### 5. Namespace Depth Management

```python
# ✅ CORRECT: Max 2 levels
t.Cli.Output  # OK: 2 levels
t.Ldif.Entry.Attribute  # ❌ 3 levels - flatten to t.Ldif.Attribute

# ❌ WRONG: Over-nesting
t.Cli.UI.Components.Display.Table  # NO: 5 levels!
t.Ldif.Entry.Transformation  # NO: 4 levels!
```

---

## Project Status

### ✅ Completed Projects

| Project        | Tier 0 | Tier 1 | Tier 2 | Status                  |
| -------------- | ------ | ------ | ------ | ----------------------- |
| **flext-core** | ✅     | ✅     | ✅     | Reference template      |
| **flext-cli**  | ✅     | ✅     | ✅     | Consolidated namespaces |
| **flext-ldif** | ✅     | ✅     | ✅     | Validated               |
| **flext-ldap** | ✅     | ✅     | ✅     | Variance fixed          |

### Type System Metrics

- **Total TypeVars**: 26 (centralized in flext-core)
- **Total Protocols**: 155+ across all projects
- **Type Aliases**: 180+ with PEP 695 syntax
- **Duplicate Aliases**: 0 (eliminated in CYCLE 4)
- **Architecture Violations**: 0 (Tier 0 modules validated)
- **Covariance Issues**: 0 (fixed in CYCLE 5)
- **Namespace Depth**: Max 2 levels across all projects

### Validation Results

```text
flext-core:      Pyright: 0 errors | Ruff: ✅ | Tests: ✅
flext-cli:       Pyright: 0 errors | Ruff: ✅ | Tests: ✅
flext-ldif:      Pyright: 0 errors | Ruff: ✅ | Tests: ✅
flext-ldap:      Pyright: 0 errors | Ruff: ✅ | Tests: ✅
```

---

## Summary

The FLEXT type system provides a **unified, composable, and extensible** architecture across the core projects with:

1. **Consistent namespace patterns** - 2-level maximum depth
2. **Proper covariance** - Protocols use `Mapping`/`Iterable`
3. **Single source of truth** - No duplicate aliases
4. **Extensible design** - Protocols instead of complex unions
5. **Zero architectural violations** - Tier 0 modules have no internal imports
6. **Complete type safety** - No `cast()`, tipagem frouxa, ou blocos `TYPE_CHECKING`
7. **Comprehensive validation** - All projects pass type checking and linting

This architecture enables maintainable, type-safe code across the entire FLEXT ecosystem while supporting future
extensions and domain-specific requirements.

---

**Document Status**: Complete and ready for reference
**Last Validation**: 2025-12-10
**Next Review**: When new type patterns emerge or architecture decisions change
