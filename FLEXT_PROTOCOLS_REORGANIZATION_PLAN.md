# FLEXT PROTOCOLS REORGANIZATION PLAN

**Version**: 1.0.0 | **Created**: 2025-10-03 | **Status**: PLANNING
**Objective**: Organize FlextProtocols to eliminate excess unused protocols and ensure proper domain extension patterns across all FLEXT ecosystem projects

---

## 📊 CURRENT STATE ANALYSIS

### Protocol Files Inventory

| Project | File | Lines | Structure Pattern |
|---------|------|-------|------------------|
| **flext-core** | protocols.py | 1431 | FlextProtocols class with nested namespaces |
| **flext-ldap** | protocols.py | 318 | FlextLdapProtocols class |
| **flext-api** | protocols.py | 417 | FlextApiProtocols class |
| **flext-cli** | protocols.py | 139 | FlextCliProtocols class (minimal) |
| **flext-web** | protocols.py | 479 | FlextWebProtocols class |
| **flext-db-oracle** | protocols.py | 434 | FlextDbOracleProtocols class |

**Total**: 3,218 lines of protocol definitions across 6 projects

### flext-core FlextProtocols Structure

**Current Nested Namespaces** (1431 lines):

1. **Foundation** (108 lines)
   - OperationCallable
   - Validator[T]
   - HasModelDump
   - HasModelFields
   - HasValue
   - HasResultValue
   - HasTimestamps
   - HasHandlerType
   - HasValidateCommand

2. **Domain** (256 lines)
   - Service (core domain service protocol)
   - Repository[T]
   - AggregateRoot[TState]
   - DomainEvent
   - Command
   - Query
   - Saga[TState]

3. **Application** (257 lines)
   - Handler[TInput, TResult]
   - CommandHandler[TCommand, TResult]
   - QueryHandler[TQuery, TResult]
   - EventHandler[TEvent]
   - SagaManager[TState]
   - EventStore
   - EventPublisher

4. **Infrastructure** (208 lines)
   - Connection
   - Configurable
   - LoggerProtocol
   - LogRenderer
   - LogContextManager
   - ConfigValidator
   - ConfigPersistence
   - ConfigFactory

5. **Extensions** (90 lines)
   - Plugin
   - PluginContext
   - Middleware
   - Observability

6. **Commands** (124 lines)
   - CommandHandler[CommandT, ResultT]
   - QueryHandler[QueryT, ResultT]
   - CommandBus
   - Middleware

**Runtime Implementation** (183 lines):
- Protocol registry methods
- Validation functionality
- Middleware management

---

## 🎯 IDENTIFIED PROBLEMS

### 1. Protocol Overload in flext-core

**Issue**: FlextProtocols contains 50+ protocol definitions, many unused or domain-specific

**Evidence**:
- Complex domain patterns (Saga, AggregateRoot, EventStore) rarely used in FLEXT projects
- Duplicate command/query protocols (in both Domain and Commands namespaces)
- Infrastructure protocols too specific (LogRenderer, ConfigPersistence, ConfigFactory)

**Impact**:
- Confusion about which protocols to use
- Heavy imports for simple use cases
- Maintenance burden for unused patterns

### 2. Inconsistent Domain Protocol Extension

**Issue**: Domain libraries create separate protocol classes but don't properly extend FlextProtocols

**Evidence**:
- flext-ldap: FlextLdapProtocols (318 lines) - separate class
- flext-api: FlextApiProtocols (417 lines) - separate class
- flext-web: FlextWebProtocols (479 lines) - separate class
- NO inheritance or extension relationship with FlextProtocols

**Impact**:
- Protocol duplication across projects
- No unified protocol hierarchy
- Difficult to understand protocol relationships

### 3. Unused Advanced Patterns

**Issue**: Many advanced DDD/CQRS protocols are defined but not used

**Unused Protocols** (from code analysis):
- Domain.Saga[TState] - NO usage in ecosystem
- Domain.AggregateRoot[TState] - LIMITED usage
- Application.EventStore - NO usage
- Application.SagaManager[TState] - NO usage
- Extensions.Observability - Minimal usage

**Impact**:
- Code bloat (500+ lines unused)
- False impression of required complexity
- Maintenance burden

### 4. Missing Domain-Specific Protocols

**Issue**: Domain libraries need protocols NOT in flext-core

**Examples**:
- flext-ldap: LDAP-specific connection, entry, search protocols
- flext-api: HTTP request/response, endpoint protocols
- flext-web: Flask/FastAPI application, route protocols
- flext-db-oracle: Oracle connection, query result protocols

**Impact**:
- Domain libraries forced to create from scratch
- No guidance on extending FlextProtocols
- Protocol pattern inconsistency

---

## 🏗️ REORGANIZATION STRATEGY

### Phase 1: Core Protocol Consolidation (flext-core)

**Objective**: Reduce FlextProtocols to ESSENTIAL foundation protocols only

#### Keep (Essential Foundation - ~500 lines)

**Foundation Namespace** (Keep All - 108 lines):
- ✅ OperationCallable - Used throughout
- ✅ Validator[T] - Core validation pattern
- ✅ HasModelDump - Pydantic integration
- ✅ HasModelFields - Pydantic integration
- ✅ HasValue - Enum-like protocol
- ✅ HasResultValue - FlextResult integration
- ✅ HasTimestamps - Common model pattern
- ✅ HasHandlerType - Handler identification
- ✅ HasValidateCommand - Command validation

**Domain Namespace** (Simplify to ~100 lines):
- ✅ Service - Core domain service (KEEP - widely used)
- ✅ Repository[T] - Data access (KEEP - essential pattern)
- ❌ AggregateRoot[TState] - REMOVE (complex, rarely used)
- ❌ DomainEvent - REMOVE (move to Extensions if needed)
- ❌ Command - REMOVE (duplicate with Commands namespace)
- ❌ Query - REMOVE (duplicate with Commands namespace)
- ❌ Saga[TState] - REMOVE (advanced pattern, unused)

**Application Namespace** (Simplify to ~120 lines):
- ✅ Handler[TInput, TResult] - Core handler (KEEP - essential)
- ❌ CommandHandler[TCommand, TResult] - REMOVE (use Handler)
- ❌ QueryHandler[TQuery, TResult] - REMOVE (use Handler)
- ❌ EventHandler[TEvent] - REMOVE (move to Extensions)
- ❌ SagaManager[TState] - REMOVE (unused advanced pattern)
- ❌ EventStore - REMOVE (unused infrastructure)
- ❌ EventPublisher - REMOVE (move to Extensions)

**Infrastructure Namespace** (Simplify to ~100 lines):
- ✅ Connection - Basic connection protocol (KEEP)
- ✅ Configurable - Basic configuration (KEEP)
- ✅ LoggerProtocol - Essential logging (KEEP)
- ❌ LogRenderer - REMOVE (too specific, move to flext-observability)
- ❌ LogContextManager - REMOVE (too specific, move to flext-observability)
- ❌ ConfigValidator - REMOVE (too specific, use Validator[T])
- ❌ ConfigPersistence - REMOVE (too specific, domain concern)
- ❌ ConfigFactory - REMOVE (factory pattern, not protocol concern)

**Commands Namespace** (Keep Consolidated - ~100 lines):
- ✅ CommandHandler[CommandT, ResultT] - CQRS pattern (KEEP)
- ✅ QueryHandler[QueryT, ResultT] - CQRS pattern (KEEP)
- ✅ CommandBus - Bus pattern (KEEP)
- ✅ Middleware - Middleware pattern (KEEP)

**Extensions Namespace** (Keep Simple - ~70 lines):
- ✅ Plugin - Plugin system (KEEP)
- ✅ PluginContext - Plugin context (KEEP)
- ✅ Middleware - Cross-cutting (KEEP)
- ✅ Observability - Monitoring (KEEP - consolidate moved protocols here)

#### Remove (~900 lines)

**Protocols to Remove**:
- All Saga-related protocols (~200 lines)
- All EventStore-related protocols (~150 lines)
- Duplicate command/query protocols (~100 lines)
- Over-specific infrastructure protocols (~250 lines)
- All AggregateRoot complex patterns (~200 lines)

**Result**: flext-core FlextProtocols reduces from 1431 to ~500 lines (65% reduction)

### Phase 2: Domain Protocol Extension Pattern

**Objective**: Establish clear extension pattern for domain libraries

#### Extension Pattern (Standard for ALL domain libraries)

```python
# File: flext-[domain]/src/flext_[domain]/protocols.py

from __future__ import annotations
from typing import Protocol, runtime_checkable
from flext_core import FlextProtocols, FlextResult

class Flext[Domain]Protocols:
    """Domain-specific protocols extending FlextProtocols foundation.

    Extends FlextProtocols with [domain]-specific protocol definitions.
    ALL domain libraries MUST follow this pattern.
    """

    # MANDATORY: Re-export FlextProtocols for convenience
    Foundation = FlextProtocols.Foundation
    Domain = FlextProtocols.Domain
    Application = FlextProtocols.Application
    Infrastructure = FlextProtocols.Infrastructure
    Extensions = FlextProtocols.Extensions
    Commands = FlextProtocols.Commands

    # Domain-specific namespace (ONLY domain-specific protocols)
    class [Domain]:
        """[Domain]-specific protocols NOT in foundation."""

        @runtime_checkable
        class [DomainSpecificProtocol](Protocol):
            """Domain-specific protocol definition."""
            ...

__all__ = ["Flext[Domain]Protocols"]
```

#### Example: flext-ldap Extension

```python
# File: flext-ldap/src/flext_ldap/protocols.py

from __future__ import annotations
from typing import Protocol, runtime_checkable
from flext_core import FlextProtocols, FlextResult

class FlextLdapProtocols:
    """LDAP-specific protocols extending FlextProtocols foundation."""

    # Re-export foundation protocols
    Foundation = FlextProtocols.Foundation
    Domain = FlextProtocols.Domain
    Application = FlextProtocols.Application
    Infrastructure = FlextProtocols.Infrastructure
    Extensions = FlextProtocols.Extensions
    Commands = FlextProtocols.Commands

    # LDAP-specific protocols only
    class Ldap:
        """LDAP domain-specific protocols."""

        @runtime_checkable
        class LdapConnection(Protocol):
            """LDAP connection protocol."""
            def bind(self, dn: str, password: str) -> FlextResult[None]: ...
            def search(self, base_dn: str, search_filter: str) -> FlextResult[list]: ...
            def unbind(self) -> FlextResult[None]: ...

        @runtime_checkable
        class LdapEntry(Protocol):
            """LDAP entry protocol."""
            def get_dn(self) -> str: ...
            def get_attributes(self) -> dict: ...

        @runtime_checkable
        class LdapSearchResult(Protocol):
            """LDAP search result protocol."""
            def get_entries(self) -> list: ...
            def get_count(self) -> int: ...

__all__ = ["FlextLdapProtocols"]
```

### Phase 3: Project-by-Project Execution

**Execution Order**: (One project at a time, validate after each)

1. ✅ **flext-core** (WEEK 1)
   - Remove unused protocols
   - Consolidate to ~500 lines
   - Validate against ecosystem usage

2. ✅ **flext-ldap** (WEEK 2)
   - Implement extension pattern
   - Remove duplicated foundation protocols
   - Add LDAP-specific protocols only
   - Reduce from 318 to ~150 lines

3. ✅ **flext-api** (WEEK 2-3)
   - Implement extension pattern
   - Remove duplicated foundation protocols
   - Add HTTP/API-specific protocols only
   - Reduce from 417 to ~200 lines

4. ✅ **flext-cli** (WEEK 3)
   - Implement extension pattern (already minimal at 139 lines)
   - Verify CLI-specific protocols necessity
   - Target: ~100 lines

5. ✅ **flext-web** (WEEK 3-4)
   - Implement extension pattern
   - Remove duplicated foundation protocols
   - Add Flask/web-specific protocols only
   - Reduce from 479 to ~250 lines

6. ✅ **flext-db-oracle** (WEEK 4)
   - Implement extension pattern
   - Remove duplicated foundation protocols
   - Add Oracle-specific protocols only
   - Reduce from 434 to ~200 lines

**Total Reduction**: 3,218 lines → ~1,400 lines (56% reduction)

---

## 📋 EXECUTION CHECKLIST (PER PROJECT)

### Pre-Execution (MANDATORY)

- [ ] Activate serena project: `mcp__serena-flext__activate_project`
- [ ] Read project CLAUDE.md for domain-specific patterns
- [ ] List current protocols: `mcp__serena-flext__get_symbols_overview`
- [ ] Check protocol usage: `mcp__serena-flext__find_referencing_symbols`
- [ ] Identify domain-specific vs. duplicated foundation protocols

### During Execution (INCREMENTAL VALIDATION)

- [ ] Remove ONE protocol category at a time
- [ ] Validate after EACH change: `ruff check src/flext_[project]/protocols.py`
- [ ] Test imports: `pytest tests/unit/test_protocols.py -v`
- [ ] Check ecosystem impact: `grep -r "FlextProtocols\.[removed]" ../flext-*`
- [ ] Update __all__ exports

### Post-Execution (QUALITY GATES)

- [ ] Full quality validation: `make validate`
- [ ] Type checking: `make type-check` (ZERO errors)
- [ ] Linting: `make lint` (ZERO violations)
- [ ] Test suite: `make test` (100% pass rate)
- [ ] Ecosystem integration test: Test dependent projects

---

## 🎯 SUCCESS CRITERIA

### Quantitative Goals

- ✅ **Core Protocols**: flext-core reduces from 1431 to ~500 lines (65% reduction)
- ✅ **Domain Libraries**: Average reduction of 50% per project
- ✅ **Total Ecosystem**: Reduce from 3,218 to ~1,400 lines (56% reduction)
- ✅ **Protocol Usage**: 90%+ of protocols actively used in ecosystem
- ✅ **Extension Compliance**: 100% of domain libraries follow extension pattern

### Qualitative Goals

- ✅ **Clear Hierarchy**: FlextProtocols → Domain Extensions pattern obvious
- ✅ **Reduced Complexity**: No unused advanced patterns in core
- ✅ **Better Documentation**: Each protocol has clear purpose and usage examples
- ✅ **Consistent Patterns**: All domain libraries follow identical extension pattern
- ✅ **Maintainability**: Easy to add new domain-specific protocols

### Validation Criteria

```bash
# Protocol usage validation
echo "=== PROTOCOL USAGE VALIDATION ==="

# 1. Check all protocols are used
for protocol in $(grep "@runtime_checkable" src/flext_core/protocols.py | grep "class" | awk '{print $2}'); do
    usage_count=$(grep -r "$protocol" ../flext-* --include="*.py" | wc -l)
    if [ "$usage_count" -lt 2 ]; then
        echo "⚠️ Protocol $protocol has low usage: $usage_count"
    fi
done

# 2. Verify extension pattern compliance
for project in flext-{ldap,api,cli,web,db-oracle}; do
    if ! grep -q "Foundation = FlextProtocols.Foundation" $project/src/*/protocols.py; then
        echo "❌ $project NOT following extension pattern"
    else
        echo "✅ $project follows extension pattern"
    fi
done

# 3. Measure reduction
echo "Protocol line reduction:"
echo "Before: 3,218 lines"
current_lines=$(wc -l flext-*/src/*/protocols.py | tail -1 | awk '{print $1}')
echo "After: $current_lines lines"
reduction=$(echo "scale=2; 100 * (3218 - $current_lines) / 3218" | bc)
echo "Reduction: ${reduction}%"
```

---

## 📝 IMPLEMENTATION NOTES

### Protocol Removal Strategy

1. **Identify Unused**: Use `find_referencing_symbols` to check usage
2. **Deprecate First**: Add deprecation warning before removal (if ANY usage found)
3. **Remove After Validation**: Only remove after confirming ZERO ecosystem usage
4. **Update Tests**: Remove or update tests for removed protocols

### Extension Pattern Benefits

1. **Consistency**: All domain libraries follow identical pattern
2. **Discoverability**: Easy to find foundation vs. domain-specific protocols
3. **Reusability**: Foundation protocols available through domain namespace
4. **Maintainability**: Clear separation of concerns

### Migration Path for Projects

**For projects using removed protocols**:

1. Identify replacement protocol (usually simpler alternative exists)
2. Update imports: `FlextProtocols.Domain.Service` instead of complex patterns
3. Simplify implementation: Use Foundation.Handler instead of specific handlers
4. Test thoroughly: Ensure behavior unchanged

---

## 🚀 EXECUTION TIMELINE

**Total Duration**: 4 weeks (one project per 2-5 days)

| Week | Projects | Focus | Lines Reduced |
|------|----------|-------|---------------|
| **Week 1** | flext-core | Foundation consolidation | ~900 lines |
| **Week 2** | flext-ldap, flext-api | Extension pattern implementation | ~400 lines |
| **Week 3** | flext-cli, flext-web | Extension pattern + domain cleanup | ~270 lines |
| **Week 4** | flext-db-oracle, Validation | Final implementation + ecosystem validation | ~234 lines |

**Milestones**:
- Week 1 End: Core protocols consolidated, documented, validated
- Week 2 End: 2 major domain libraries migrated to extension pattern
- Week 3 End: All domain libraries following extension pattern
- Week 4 End: Complete ecosystem validation, documentation updated

---

## ✅ COMPLETION CRITERIA

**Project COMPLETE when**:

- [ ] FlextProtocols reduced to ~500 essential lines
- [ ] All domain libraries follow extension pattern
- [ ] Total ecosystem protocols reduced by 50%+
- [ ] 90%+ protocol usage rate (no dead code)
- [ ] Zero quality gate violations (ruff, mypy, pytest)
- [ ] All dependent projects tested and validated
- [ ] Documentation updated with clear protocol hierarchy
- [ ] Extension pattern examples in all domain library CLAUDE.md files

---

**PLAN STATUS**: READY FOR EXECUTION
**NEXT STEP**: Execute Phase 1 - flext-core protocol consolidation
**VALIDATION**: Execute one project at a time, validate after each change
