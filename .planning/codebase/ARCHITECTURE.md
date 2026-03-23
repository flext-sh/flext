# Architecture

**Analysis Date:** 2026-03-23

## Pattern Overview

**Overall:** Layered DDD (Domain-Driven Design) with dispatcher-driven CQRS and MRO-based namespace composition.

**Key Characteristics:**
- Four-layer inward dependency flow: `L3` (Orchestration) → `L2` (Domain/Infrastructure) → `L1` (Foundation/Bridge) → `L0` (Contracts)
- Dispatcher-first message handling with handler registration and execution reliability
- MRO-based namespace composition via single facade classes per tier (Models, Constants, Protocols, Utilities)
- Strict dependency isolation between platform chains (Core → Cli → Meltano → Integration) and (Core → Web → Api → Auth)
- Result-oriented error handling with `r[T]` type for all fallible operations
- Pydantic v2 BaseModel validation throughout domain layers

## Layers

**L0 - Contracts:**
- Purpose: Type definitions, protocols, and strict typing contracts
- Location: `flext-core/src/flext_core/_typings/`, `flext-core/src/flext_core/_protocols/`
- Contains: Type aliases (`t.*`), Protocols (`p.*`), structured contracts via `annotated-types`
- Depends on: Python standard library only
- Used by: All higher layers

**L1 - Foundation/Bridge:**
- Purpose: Core runtime utilities, context propagation, container management, dependency injection
- Location: `flext-core/src/flext_core/` (runtime.py, context.py, container.py, registry.py, service.py)
- Contains: FlextContext for correlation/timing, FlextLogger for structured logging, FlextDispatcher for message routing, FlextService base for DI integration
- Depends on: L0 (contracts), external libs (dependency_injector, structlog, orjson, pydantic)
- Used by: Domain/Infrastructure layers and orchestration

**L2 - Domain/Infrastructure:**
- Purpose: Domain entities, value objects, CQRS models, constants, utilities for business logic
- Location: `flext-core/src/flext_core/` (models.py, constants.py, utilities.py, exceptions.py, handlers.py)
- Contains: FlextModels (Entity, AggregateRoot, Command, Query, DomainEvent), FlextConstants (validation, settings, platform), FlextUtilities (guards, introspection, transformation)
- Depends on: L1 (Foundation), L0 (Contracts)
- Used by: Orchestration layer and project-specific domain modules

**L3 - Orchestration:**
- Purpose: Platform-specific implementations, integration projects, API servers, CLI tools
- Location: `flext-api/`, `flext-cli/`, `flext-meltano/`, `flext-tap-*/`, `flext-target-*/`, `flext-dbt-*/`
- Contains: FlextApi (HTTP facade), protocol implementations, lifecycle managers, schema validators, client adapters
- Depends on: L2 (Domain), L1 (Foundation), L0 (Contracts), external SDKs
- Used by: Executable applications and external consumers

## Data Flow

**CQRS Message Flow:**

1. Message instantiation as Pydantic model (Command or Query)
2. Dispatcher routes message to registered handler via `dispatch(message)`
3. Handler executes business logic using domain models and utilities
4. Handler returns `r[T]` Result (success or failure)
5. FlextContext propagates correlation IDs and timing through async boundaries
6. FlextLogger captures structured logs keyed by correlation ID
7. Response serialized via FlextApiSerializers (JSON, CBOR, GraphQL)

**Dependency Injection Flow:**

1. Service instance created via `FlextService.__new__()` with optional config
2. Service registers handlers with internal dispatcher via `register_handler()`
3. FlextService wires dependency_injector container for resource injection
4. Handler method receives injected resources via `@handler` decorator
5. Container cleanup via atexit or explicit `FlextService.shutdown()`

**Request Flow (HTTP API):**

1. FastAPI receives HTTP request
2. FlextApiServer routes to handler via OpenAPI/schema validation
3. Request data parsed and validated via FlextApiModels
4. FlextApi delegates to FlextApiClient for protocol execution
5. Client returns `r[T]`, serialized to HTTP response
6. Middleware chains add headers, logging, error transformation

**State Management:**

- **Request State:** Stored in `FlextContext` via contextvars (survives async/thread hops)
- **Service State:** Stored in FlextService instance attributes and DI container
- **Domain State:** Immutable Pydantic models with explicit change tracking via events
- **Correlation:** Automatic via FlextContext (no manual thread-local management needed)

## Key Abstractions

**Service (`s[T]` / FlextService):**
- Purpose: Base class for all executable services (Web, API, CLI, Scheduler)
- Examples: `FlextApi(s[FlextApiSettings])`, `FlextWebApp(s[...])`, `FlextCliApp(s[...])`
- Pattern: Inherits from `FlextService` with generic config type; implements `__init__`, `execute()`, `shutdown()`
- Lifecycle: Created → configured → wired → handlers registered → execute() → shutdown()

**Result (`r[T]` / FlextModelsResult):**
- Purpose: Type-safe error handling for fallible operations
- Examples: `r[str].ok("success")`, `r[User].fail("not found")`, `result.map(transform)`, `result.flat_map(chain)`
- Pattern: Encapsulates success value or failure message with error code; supports monadic composition
- Never use: `T | None`, bare exceptions, or ad-hoc error dicts

**Models (`m.*` / FlextModels):**
- Purpose: Domain-driven entities, aggregates, commands, queries, events
- Examples: `m.Entity`, `m.AggregateRoot`, `m.Command`, `m.Query`, `m.DomainEvent`, `m.ValueObject`
- Pattern: Inherit from Pydantic BaseModel with MRO composition; provide validation, serialization, event tracking
- All models extend base classes from `_models/` and compose via `FlextModels` facade

**Dispatcher (`FlextDispatcher`):**
- Purpose: Message routing and handler registration for CQRS
- Examples: `dispatcher.register_handler(GetUserCommand, get_user_handler)`, `dispatcher.dispatch(command)`
- Pattern: Internal dict maps message type names to handler tuples; supports auto-routing and event subscribers
- Returns: `r[T]` result from handler execution

**Context (`FlextContext`):**
- Purpose: Request-scoped correlation, metadata, timing across async boundaries
- Examples: `FlextContext.current()`, `context.correlation_id`, `context.with_scope(...)`
- Pattern: contextvars-based so survives thread/async hops; FlextLogger hooks for structured logs
- Managed by: FlextDispatcher and FlextApi middleware automatically

**Protocols (`p.*` / FlextProtocols):**
- Purpose: Structural typing contracts (no inheritance required)
- Examples: `p.Logger`, `p.Routable`, `p.ResultLike`, `p.DispatchMessage`
- Pattern: Python Protocols (PEP 544) for duck typing; no MRO inheritance needed
- Used by: Handlers, middleware, external adapters for type narrowing

**Constants (`c.*` / FlextConstants):**
- Purpose: Centralized constant definitions (validation rules, HTTP status codes, settings)
- Examples: `c.COMMAND_PROCESSING_FAILED`, `c.DEFAULT_TIMEOUT`, `c.VALIDATION_ERRORS`
- Pattern: Grouped in `_constants/` subdirectories (base, cqrs, infrastructure, validation, etc.)
- Composed via: `FlextConstants` facade MRO

**Utilities (`u.*` / FlextUtilities):**
- Purpose: Shared helper functions (guards, introspection, transformations)
- Examples: `u.is_pydantic_model()`, `u.get_message_route()`, `u.normalize_value()`
- Pattern: Grouped in `_utilities/` subdirectories; organized by purpose (guards, introspection, transformations)
- Accessed via: Canonical `u.*` namespace only

## Entry Points

**FlextDispatcher (CQRS):**
- Location: `flext-core/src/flext_core/dispatcher.py`
- Triggers: Service initialization, handler registration, message dispatch
- Responsibilities: Route messages to handlers, manage subscriptions, return results

**FlextApi (HTTP REST):**
- Location: `flext-api/src/flext_api/api.py`
- Triggers: HTTP request received by FastAPI
- Responsibilities: Delegate to FlextApiClient, validate via FlextApiModels, serialize via FlextApiSerializers

**FlextApiServer (Protocol Handler):**
- Location: `flext-api/src/flext_api/server.py`
- Triggers: Server startup, incoming protocol messages
- Responsibilities: Route to protocol implementation (HTTP, WebSocket, SSE, AsyncAPI)

**FlextService (Base Lifecycle):**
- Location: `flext-core/src/flext_core/service.py`
- Triggers: Service instantiation, `execute()` call, shutdown signal
- Responsibilities: DI container wiring, handler registration, resource cleanup

**FlextContext (Request Scope):**
- Location: `flext-core/src/flext_core/context.py`
- Triggers: Middleware entry, handler execution, logger initialization
- Responsibilities: Propagate correlation ID, timing metadata, service identity across layers

## Error Handling

**Strategy:** Railway-oriented programming using `r[T]` Result type with monadic composition.

**Patterns:**
- All fallible operations return `r[T]`, never `T | None` or bare exceptions
- Result composition via `map()`, `flat_map()`, `lash()` for pipeline processing
- Dispatcher catches handler exceptions and wraps in `r[T].fail()` with error code
- FlextLogger captures exceptions automatically via contextvars and result inspection
- HTTP responses transformed via middleware: `r[T]` → HTTP status code, error body
- Domain events can capture failures for event sourcing or audit trails

## Cross-Cutting Concerns

**Logging:**
- Framework: `structlog` with JSON output
- FlextLogger provides module-scoped instances with automatic correlation ID injection
- All logs include `correlation_id`, `timestamp`, `level`, and structured context
- Lazy initialization via lazy.py module-level strategy

**Validation:**
- Pydantic v2 `BaseModel` with strict `Field()` constraints
- `annotated-types` for portable validation across frameworks (PositiveInt, NonEmptyStr, BoundedStr, etc.)
- Result-wrapped validation: failed validation returns `r[T].fail()`, not exception
- Constants (`c.*`) provide centralized validation bounds and rules

**Authentication:**
- Platform-specific via `flext-auth/` integration module
- Dispatched through FlextApiServer protocol implementations
- FlextContext can store authenticated user metadata
- Authorization checked in handler decorators or domain service methods

**Dependency Injection:**
- Framework: `dependency_injector` containers and providers
- FlextService manages container lifecycle: create → wire → execute → shutdown
- Handlers can be methods with `@handler` decorator for auto-wiring
- Resources registered as providers: singleton factories, callable providers, resource providers

**Serialization:**
- JSON via `orjson` (fast, strict)
- CBOR via `cbor2` for compact binary transport
- GraphQL via `gql` for query language support
- Schemas: OpenAPI, AsyncAPI, JSONSchema validators
- Models inherit Pydantic `model_dump()` for transport serialization
