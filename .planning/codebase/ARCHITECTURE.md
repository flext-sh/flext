# FLEXT Architecture

**Analysis Date:** 2026-01-31

## Pattern Overview

**Overall:** Layered Monorepo with Railway-Oriented Programming (ROP)

**Key Characteristics:**
- Strict 4-tier layering (Tier 0→3) with import enforcement
- Railway-oriented error handling via `FlextResult[T]` (no exceptions)
- Facade pattern: Single entry point per subproject via `api.py`
- Protocol-based abstractions (SOLID principles, no circular dependencies)
- Python 3.13+ exclusive with zero type-safety exceptions
- 30+ git submodules organized by function/domain

## Layers

**Tier 0 (Foundation):**
- Purpose: Pure definitions with zero internal dependencies
- Location: `constants.py`, `typings.py`, `protocols.py` in each project
- Contains: Enum constants with `Final`, type aliases via `TypeAlias`, Protocol interfaces
- Depends on: Nothing (except `flext_core` protocols for cross-cutting)
- Used by: Tier 1, 2, 3 (all upstream layers)

**Tier 1 (Domain Foundation):**
- Purpose: Business models and utilities
- Location: `models.py`, `utilities.py` and internal `_models/`, `_utilities/` directories
- Contains: Pydantic v2 domain models, validation logic, helper functions
- Depends on: Tier 0 only
- Used by: Tier 2, 3

**Tier 2 (Infrastructure):**
- Purpose: External system integration (databases, APIs, file systems)
- Location: `servers/*.py` for implementation details
- Contains: Connection pools, adapters, transport clients
- Depends on: Tier 0, Tier 1
- Used by: Tier 3

**Tier 3 (Application):**
- Purpose: Business logic, API facades, services
- Location: `services/*.py`, `api.py`
- Contains: Service orchestration, request handling, domain workflows
- Depends on: All lower tiers (0, 1, 2)
- Used by: External consumers only

## Data Flow

**Request Flow (Inbound):**

1. External caller → `api.py` (Facade - Tier 3)
2. `api.py` → Service class in `services/` (Tier 3)
3. Service → Utility/Helper from Tier 1 or Infrastructure from Tier 2
4. Tier 2 (servers) → External system (database, API, file system)

**Response Flow (Outbound):**

1. External system → Tier 2 infrastructure adapter
2. Adapter transforms to Tier 1 domain models
3. Service composes models, applies business logic
4. `api.py` returns `FlextResult[DomainModel]` to caller

**Error Handling:**

- All operations return `FlextResult[T]` (success/failure union)
- No exceptions thrown in framework code
- Errors composed monadically: `.flat_map()`, `.map()`, `.map_error()`
- Railway pattern: Success path flows forward, failure short-circuits

**Example Data Flow:**

```
User Request
    ↓
FlextLdif.parse(path)  [api.py - Tier 3]
    ↓
FlextLdifParser.parse()  [services/ - Tier 3]
    ↓
RfcLdifParser.parse()  [servers/ - Tier 2, RFC baseline]
    ↓
QuirksRegistry.apply()  [services/ - Tier 3, server-specific enhancements]
    ↓
FlextResult[list[LdifEntry]]  [m.Ldif.Entry - Tier 1 models]
    ↓
User Handler (caller receives FlextResult)
```

**State Management:**

- **Stateless by default**: Each call is independent (no session state)
- **Scoped state via DI**: `FlextContainer` manages service instances, configs, loggers
- **Request context via FlextContext**: Operation correlations, audit trails
- **Configuration via FlextConfig**: Environment-driven defaults, feature flags

## Key Abstractions

**FlextResult[T] (Railway-Oriented Programming):**
- Purpose: Type-safe error handling without exceptions
- Examples: `flext-core/src/flext_core/result.py`
- Pattern: Success wraps value `T`, Failure wraps error string
- Usage: All framework operations return `r[T].ok(value)` or `r[T].fail(error)`
- Composable: `.flat_map()`, `.map()`, `.map_error()` for monadic chaining

**Tier 0 Protocols (SOLID - Dependency Inversion):**
- Purpose: Define contracts without concrete implementation
- Examples: `FlextProtocols.Domain.Service[T]`, `FlextProtocols.Application.Handler`
- Benefits: Eliminates circular imports, enables structural typing, testable via duck-typing
- Pattern: Type hints use `p.Domain.Service[T]`, not concrete class names

**Facade Pattern (Single Entry Point per Project):**
- Purpose: Unified API surface hiding internal complexity
- Location: `api.py` in each subproject (exports one main class like `FlextLdif`, `FlextAuth`)
- Pattern: Facade delegates to service classes, composition over inheritance
- Benefits: Clear contract boundaries, easier maintenance, version stability

**Dependency Injection Container:**
- Purpose: Manage service lifecycle (singleton, factory, scoped)
- Location: `flext_core/container.py`, extended per-project
- Pattern: `FlextContainer()` creates scoped container, `container.get(service_name)` returns `r[Service]`
- Auto-registration: Core services (`config`, `logger`, `context`) auto-registered

**Domain-Driven Design (FlextModels):**
- Purpose: Type-safe domain representation with validation
- Examples: Value Objects (`m.Entity.Value`), Entities (`m.Entity.Entity`), Aggregates (`m.Entity.AggregateRoot`)
- Pattern: Pydantic v2 models with computed fields, validators, JSON serialization
- Full namespace: `m.Ldif.Entry`, not `m.Entry` (root alias forbidden)

**Short Aliases for Runtime Access:**
- Purpose: Concise type hints and instantiation
- Pattern: `from flext_core.result import r`, then `r[T].ok(value)`
- Full namespace elsewhere: `p.Domain.Service[T]`, `c.Core.TIMEOUT`, `t.Types.StringDict`
- Standard aliases: `r`, `t`, `c`, `m`, `p`, `u`, `e`, `d`, `x` (FlextResult, Types, Constants, Models, Protocols, Utilities, Exceptions, Decorators, Context)

## Entry Points

**Primary Entry Points per Subproject:**
- Location: `src/flext_<project>/api.py`
- Export: Single main class (e.g., `FlextLdif`, `FlextAuth`, `FlextDbOracleApi`)
- Pattern: Facade that delegates to service layer
- Returns: All methods return `FlextResult[DomainModel]`

**Example Entry Points:**
- `FlextLdif` → `flext-ldif/src/flext_ldif/api.py` | Main LDIF facade
- `FlextAuth` → `flext-auth/src/flext_auth/api.py` | Authentication facade
- `FlextDbOracleApi` → `flext-db-oracle/src/flext_db_oracle/api.py` | Database facade
- `FlextContainer` → `flext-core/src/flext_core/container.py` | DI bootstrap

**Configuration Entry Point:**
- `FlextConfig` → `flext-core/src/flext_core/config.py`
- Purpose: Environment-driven settings, behavior defaults
- Pattern: Singleton, loaded at startup, overrideable via `FlextContainer`

**Logging Entry Point:**
- `FlextLogger` → `flext-core/src/flext_core/loggings.py`
- Purpose: Structured logging with context correlation
- Pattern: Injected via container or accessed via `FlextRuntime.structlog()`

**CLI Entry Point (flext-cli):**
- `FlextCli` → `flext-cli/src/flext_cli/api.py`
- Purpose: Command-line interface with subcommand routing
- Pattern: Loads project via `FlextCli()`, executes command

## Error Handling

**Strategy:** Railway-Oriented Programming (ROP) - no exceptions in framework

**Patterns:**

**Pattern 1: Flat-Map Chaining (Success Path Composition)**
```python
result = (
    validate_input(user_data)
    .flat_map(lambda user: save_user(user))
    .flat_map(lambda user: send_notification(user))
    .map(lambda user: format_response(user))
)
# On first failure, short-circuits remaining operations
```

**Pattern 2: Error Handling with Map-Error**
```python
result = parse_ldif(path).map_error(
    lambda e: f"Failed to parse: {e}"
)
# Transform error message while maintaining success path
```

**Pattern 3: Explicit Success/Failure Branching**
```python
result = FlextLdif().parse(path)
if result.is_success:
    entries = result.value
    for entry in entries:
        process(entry)
elif result.is_failure:
    log_error(result.error)
```

**Pattern 4: User Handler Exceptions (Framework Wraps)**
```python
def execute_user_handler(handler: p.Application.Handler, msg: Message) -> r[Response]:
    try:
        response = handler.handle(msg)
        return r[Response].ok(response)
    except Exception as e:
        return r[Response].fail(f"Handler failed: {e}")
# Framework catches exceptions from user code, wraps in FlextResult
```

## Cross-Cutting Concerns

**Logging:**
- Framework: `FlextLogger` with structured logging via structlog
- Pattern: Injected into services via `self.logger` from `FlextService` base
- Output: Structured JSON logs with operation context, timings, error details
- Correlation: Request ID traced through call stack via `FlextContext`

**Validation:**
- Framework: Pydantic v2 validators in domain models
- Pattern: Model creation validates at Tier 1, errors surface as `FlextResult.fail()`
- Extension: Custom validators via `field_validator`, `computed_field`
- Pre-validation: Input validation in `utilities.py` helpers before model creation

**Authentication:**
- Framework: `FlextAuth` with provider-centric architecture
- Pattern: Registry-based provider loading, all flows through `FlextAuth` facade
- Credentials: Domain models for tokens, credentials in `models.py`
- Protocols: `FlextAuthBaseProvider` for custom auth implementations

**Configuration:**
- Framework: `FlextConfig` (Tier 0.1 - just above constants)
- Pattern: Environment-driven with Pydantic `BaseSettings`
- Overrides: Via `container.configure()`, passed to service constructors
- Defaults: Via `FlextConstants` (Tier 0), applied by `FlextConfig`

## Architectural Decisions

**Decision 1: Why Tier 0.1 (Config) Exists Above Tier 1**
- Config controls all lower-tier behavior (defaults, feature flags)
- Cannot be Tier 1 (circular import with exceptions.py which uses config)
- Position (0.1) eliminates circulars while maintaining control flow

**Decision 2: Why Protocols Instead of Abstract Base Classes**
- Structural typing: Avoids coupling between producer/consumer
- Circular import elimination: Protocols in Tier 0, implementations anywhere
- Duck typing: Type checkers use protocol signature, not class name

**Decision 3: Why Monorepo with Git Submodules**
- Monorepo: Unified CI/CD, shared tooling, easy cross-project changes
- Submodules: Independent versioning, decoupled releases, clear boundaries
- 30+ projects: Tap/target connectors (Singer protocol), dbt projects, infrastructure

**Decision 4: Why Railway Pattern (FlextResult) Not Try-Except**
- Composability: Operations chain naturally via `.flat_map()`
- Predictability: All errors uniform `r[T].fail(msg)`, no exception types
- Testability: No try-catch boilerplate, explicit error paths
- Type safety: Success/failure statically known, no "what exception?"

**Decision 5: Why Facade Pattern for api.py**
- Single contract: One public entry point per project
- Version stability: Internal refactoring doesn't break consumers
- Clear boundaries: Public vs internal separation explicit
- Migration friendly: New API added without breaking old

---

*Architecture analysis: 2026-01-31*
