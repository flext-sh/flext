# CLAUDE.md — AI Agent Configuration Index

<!-- TOC START -->

- [Agent Configuration Map](#agent-configuration-map)
- [Maintenance Rules](#maintenance-rules)
- [Practical Usage](#practical-usage)
<!-- TOC END -->

**Reviewed**: 2026-02-17 | **Scope**: Pointer policy and mapping consistency

This repository uses multiple AI coding agents. All share a **single source of truth**
for project rules, architecture, and conventions: [`AGENTS.md`](AGENTS.md).

## Agent Configuration Map

| Agent                  | Config File                                                               | Role                                         |
| ---------------------- | ------------------------------------------------------------------------- | -------------------------------------------- |
| **Claude Code**        | [`AGENTS.md`](AGENTS.md)                                                  | Canonical — all rules defined here           |
| **Gemini Code Assist** | [`.gemini/styleguide.md`](.gemini/styleguide.md)                          | PR review priorities, delegates to AGENTS.md |
| **GitHub Copilot**     | [`.github/copilot-instructions.md`](.github/copilot-instructions.md)      | Pointer to AGENTS.md                         |
| **Cursor AI**          | [`.cursor/rules/flext.mdc`](.cursor/rules/flext.mdc)                      | Pointer to AGENTS.md                         |
| **OpenAI Codex**       | [`codex.md`](codex.md)                                                    | Pointer to AGENTS.md                         |
| **Cline**              | [`.clinerules`](.clinerules)                                              | Pointer to AGENTS.md                         |
| **Windsurf**           | [`.windsurfrules`](.windsurfrules)                                        | Pointer to AGENTS.md                         |
| **Continue.dev**       | [`.continue/rules/flext.md`](.continue/rules/flext.md)                    | Pointer to AGENTS.md                         |
| **Aider**              | [`CONVENTIONS.md`](CONVENTIONS.md) + [`.aider.conf.yml`](.aider.conf.yml) | Auto-loads CONVENTIONS.md + AGENTS.md        |

## Maintenance Rules

1. **All rule changes go to `AGENTS.md` first** — agent-specific files only add tool-specific behavior.
2. **Never duplicate rules** across agent configs — reference `AGENTS.md` sections instead.
3. **Agent-specific files must stay under 50 lines** — they are pointers, not copies.
4. When updating architecture, conventions, or quality gates, update `AGENTS.md` only.

## Practical Usage

1. Start with root `AGENTS.md`, then load scoped skills from `.claude/skills/` by touched path.
2. For `flext-core` changes, include `rules-flext-core` and matching `lib-*` skills for dependencies in scope.
3. For docs/governance changes, include `skill-format-universal` and `flext-docs-pointer-policy`.
4. Run `make validate VALIDATE_SCOPE=workspace` and `make check` before finalizing workspace-wide governance edits.
5. In final reports, reference changed paths and provide validation evidence with concrete commands.

## Alignment and anti-drift

- Every project must stay aligned with `AGENTS.md`, root `base.mk`, and the path-to-skill mapping (see AGENTS.md § Skill Enforcement).
- Before claiming completion for policy or automation changes, run `make validate VALIDATE_SCOPE=workspace` and fix any failures.
- Before adding a new submodule or changing base.mk/scripts: run `make validate VALIDATE_SCOPE=workspace` and fix any failure.
- Changes to `base.mk`, shared `scripts/`, or `scripts/dependencies/modernize_pyproject.py` must be validated with `make validate VALIDATE_SCOPE=workspace` and with `make check` / `make validate` on affected projects.
- Baseline and per-project check status: see [.reports/validate/refactoring-baseline.md](.reports/validate/refactoring-baseline.md).

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

<!-- GSD:project-start source:PROJECT.md -->
## Project

**FLEXT Monorepo Hardening & Modernization**

A 33-project Python monorepo built on MRO-based namespace composition, DDD/CQRS with a dispatcher-first message bus, and strict Pydantic v2 models. The monorepo is architecturally sound but carries accumulated technical debt: 4,385 pyrefly type errors, widespread `Any`/`object`/`type:ignore` usage, inconsistent runtime patterns, and legacy tooling (Poetry) that limits speed and scalability. This project sequences 25 existing `.sisyphus` plans into executable GSD phases to drive the codebase to production-grade quality.

**Core Value:** Zero type errors, zero typing shortcuts, zero workarounds — a clean, strict, fully typed Python 3.13 monorepo that enforces AGENTS.md governance at every layer.

### Constraints

- **Tooling**: All changes via `make` targets, `ast-grep`, native tools — never direct `git`/`grep`/`find`
- **Typing**: No `Any`, no `object` annotations, no `cast()`, no `# type: ignore` — zero exceptions
- **Freeze policy**: `flext-core/_utilities/*` FROZEN per AGENTS.md §10.2 (except where explicitly unfrozen by operator)
- **Autogenerated files**: `__init__.py` exports are autogenerated — fix generators, never hand-edit
- **Commit protocol**: Stage → commit → `bd sync` → push before ending each session
- **Dependency order**: flext-core → flext-infra → flext-tests → consumers (respect this for all refactors)
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.13 - All application code, data integration, API services, and infrastructure tooling
- Go - Limited usage in `flexcore/` for CLI/command utilities
- YAML - Configuration files, dbt/meltano definitions, docker-compose files
- TOML - pyproject.toml project manifests
- SQL - Database operations and schema management via dbt
- Protocol Buffers - gRPC service definitions
## Runtime
- Python 3.13 (strict requirement: `requires-python = ">=3.13,<3.14"`)
- Poetry 2.0+ (via poetry-core)
- uv - Virtual environment and dependency management
- Lockfile: `poetry.lock` (present in workspace)
## Frameworks
- Pydantic 2.12+ - Data validation, settings management, type safety
- FastAPI 0.116+ - REST API framework (flext-api, flext-tap-oracle, flext-meltano)
- Flask 3+ - Web framework (flext-web, flext-observability)
- SQLAlchemy 2.0+ - Database ORM and query builder
- Meltano (git fork: `flext/relax-deps`) - Data pipeline orchestration platform
- dbt-core (git fork: `flext/relax-deps`) - Analytics engineering, transformations
- Singer SDK 0.52+ - Tap/target framework for ETL
- gRPC 1.76+ - High-performance RPC framework
- Protobuf 6.33+ - Message serialization
- pytest 8.4+ - Test runner
- pytest-xdist 3.8+ - Parallel test execution
- pytest-benchmark 5.1+ - Performance testing
- factory-boy 3.3+ - Test fixtures and factories
- hypothesis 6.125+ - Property-based testing
- ruff 0.12+ - Linter and formatter (Python)
- pyrefly - Type checking (experimental/custom)
- pyright - Static type checker (strict mode)
- mypy 1.18+ - Type checker with Pydantic plugin
- black 25.1+ - Code formatter
- deptry 0.23+ - Dependency analysis
- mkdocs 1.6+ - Static documentation generator
- mkdocstrings 0.24+ - Docstring-driven documentation
- Material theme - Professional documentation theme
## Key Dependencies
- `pydantic-core>=2.41.4` - Pydantic validation engine (required across all projects)
- `pydantic-settings>=2.10.1` - Environment-based configuration
- `pydantic-extra-types[semver]>=2.10` - Extra type validators
- `dependency-injector>=4.41` - Dependency injection container (flext-core)
- `structlog>=25.4` - Structured logging (flext-core, flext-ldap, flext-observability)
- `orjson>=3.11.3` - Fast JSON serialization
- `docker>=7.1,<8` - Docker Python SDK for container operations
- `python-on-whales>=0.79` - Docker CLI wrapper
- `psutil>=5.9` - System and process utilities (flext-grpc)
- `oracledb>=2` - Oracle Database adapter (flext-db-oracle, flext-tap-oracle)
- `ldap3>=2.9` - LDAP/Active Directory operations (flext-ldap)
- `cryptography>=45.0.5` - Cryptographic operations (flext-ldap, flext-auth)
- `bcrypt>=4.3` - Password hashing (flext-auth)
- `pyjwt>=2.9` - JWT token operations (flext-auth)
- `opentelemetry-sdk>=1.39.1,<2` - OTEL tracing/metrics backend
- `opentelemetry-exporter-otlp-proto-grpc>=1.39.1` - OTEL gRPC exporter
- `opentelemetry-exporter-prometheus>=0.60b1` - OTEL Prometheus exporter
- `prometheus-client>=0.23` - Prometheus metrics client
- `duckdb>=1` - In-process analytical SQL database (flext-meltano)
- `pandas>=2` - Data manipulation and analysis (flext-meltano)
- `sqlalchemy>=2` - SQL toolkit and ORM (flext-grpc, flext-meltano)
- `msgpack>=1.1.2` - Binary serialization (flext-api)
- `cbor2>=5.7` - CBOR binary serialization (flext-api)
- `websockets>=15.0.1` - WebSocket protocol support (flext-api)
- `libcst>=1.5.1` - Concrete syntax tree parser (flext-infra)
- `rope>=1.14.0,<2.0.0` - Python refactoring library (flext-infra, flext-core)
- `jinja2>=3.1.6` - Template engine (flext-core, flext-meltano)
- `cachetools>=5.3` - Caching decorators (flext-core)
- `limits>=3.6` - Rate limiting (flext-core)
- `pybreaker>=0.8` - Circuit breaker pattern (flext-core)
- `wrapt>=1.17` - Function wrapper utilities
- `returns>=0.26` - Functional return types (flext-core)
- `tomlkit>=0.13` - TOML library with formatting preservation
- `pyyaml>=6.0.2` - YAML parsing and serialization
- `importlib-resources>=6.5.2` - Resource loading
- `typing-extensions>=4.15` - Extended typing utilities
- `tenacity>=9.1.2` - Retry decorator (flext-oracle-oic)
- `typer>=0.12-0.15` - CLI framework (flext-observability, flext-oracle-oic)
- `rich>=14.2,<15` - Rich terminal output (flext-observability)
- `starlette>=0.52.1` - ASGI framework (flext-observability)
## Configuration
- `.envrc` - direnv configuration for automatic venv activation and environment setup
- `VIRTUAL_ENV` - Points to `${PWD}/.venv`
- `PYTHONPATH` - Includes workspace `src/` directory
- `PYTHON_KEYRING_BACKEND="keyring.backends.null.Keyring"` - Disable system keyring
- `PYTHONDONTWRITEBYTECODE=1` - Skip .pyc generation
- `PYTHONUNBUFFERED=1` - Unbuffered stdout/stderr
- `base.mk` - Shared Makefile patterns for all projects
- `pyproject.toml` - Root workspace configuration with centralized tool configs:
- 50+ independent Python projects with standardized `pyproject.toml` structure
- All managed projects follow [MANAGED] sections controlled by `flext_infra.deps.modernizer`
- Custom extension points marked [CUSTOM] for project-specific configuration
- Consolidated development dependencies across workspace
## Platform Requirements
- Python 3.13 with venv/uv support
- direnv for environment management
- Poetry for dependency resolution
- Docker (for containerized services during development)
- Go 1.x (for flexcore command utilities)
- Python 3.13 runtime
- Docker container runtime (implied by composition files)
- Network connectivity to:
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Public facades: `{name}.py` (e.g., `models.py`, `utilities.py`, `constants.py`)
- Private/internal modules: `_{name}.py` or `_{category}/{name}.py` (e.g., `_utilities/guards.py`, `_models/result.py`)
- Test files: `test_*.py`, `*_test.py`, `*_tests.py` (matched by pytest configuration)
- Subpackage organization: Logical domain grouping in subdirectories like `_models/`, `_utilities/`, `_constants/`, `_protocols/`
- camelCase is FORBIDDEN. Use snake_case exclusively: `def parse_input()`, `def validate_range()`, `def from_kwargs()`
- Async functions: same snake_case pattern: `async def process_data()`
- Factory functions: `create_*()`, `make_*()`, `from_*()` patterns
- Validation/guard functions: `is_*()`, `ensure_*()`, `check_*()`, `validate_*()`
- snake_case for all local and module-level variables
- UPPER_CASE for module-level constants and classvars that are truly constant
- Private attributes: prefix with underscore (`self._state`), use Pydantic `PrivateAttr()` for BaseModel fields
- No single-letter variables except loop indices (`i`, `j`) or accepted aliases: `r` (result), `m` (models), `c` (constants), `t` (types), `u` (utilities), `p` (protocols), `h` (helpers), `s` (services), `e` (errors), `d` (dependency), `x` (execution)
- Type aliases: Use PEP 695 `type X = ...` syntax (Python 3.13+) in `typings.py` only
- Never use bare `Any`, `object`, or generic `Mapping[str, Any]`. Use specific `t.*` contracts from typings
- Class names: PascalCase with semantic prefixes: `Flext{Module}{Domain}{Facade}` (e.g., `FlextCoreModels`, `FlextUtilitiesGuards`, `FlextTestInfraHelpers`)
- No backward-compat aliases: never create `LegacyX = NewX` style assignments
- `m` = Models (`FlextModels`, `FlextXyzModels`)
- `c` = Constants (`FlextConstants`, `FlextXyzConstants`)
- `t` = Types (`FlextTypes`, `FlextXyzTypes`)
- `u` = Utilities (`FlextUtilities`, `FlextXyzUtilities`)
- `p` = Protocols (`FlextProtocols`, `FlextXyzProtocols`)
- `h` = Helpers (`FlextHelpers` - test/infra helpers only)
- `s` = Services (`FlextServices`, `FlextXyzServices`)
- `r` = Result (railway-oriented programming from `returns` library)
- `e` = Errors/Exceptions
- `d` = Dependency (DI container)
- `x` = Execution/Runtime primitives
## Code Style
- Line length: 88 characters (configured in ruff)
- Indentation: 4 spaces
- Quote style: Double quotes `"string"` (enforced by Ruff/Black)
- Trailing commas: Yes on multi-line (split-on-trailing-comma = true)
- Line endings: LF only
- Tool: Ruff (with Black formatter)
- Configuration: `pyproject.toml` `[tool.ruff]` section
- Key settings:
- Type checking: Pyright (strict mode) + Mypy + Pyrefly (Python 3.13 diagnostics)
- Any module, class, method, or function exceeding 200 logical lines (blank/comments excluded) is a violation
- Must be refactored via OO composition, MRO inheritance, or facade extraction to `_modules/` subdirectories
- FORBIDDEN approaches: removing blank lines, compressing docstrings, arbitrary code splits without domain decomposition
- VALID reduction: deleting dead code, removing unnecessary wrappers, replacing inline type unions with canonical `t.*` contracts
## Import Organization
- Root imports by class name: `from flext_core import FlextProtocols` (never `from flext_core.protocols import Protocols`)
- Submodule imports only for direct access: `from flext_core._utilities.guards import FlextUtilitiesGuardsEnsure`
- In test code: Use `from tests import c, m, t, u` for local test infrastructure
- Forbidde: Importing private `_` internals outside the module; importing aliases from sibling projects in tests
## Error Handling
- Fallible operations MUST return `r[T]` (Result type from `returns` library)
- Never use `T | None` for error states; use `r[T]` instead
- Bare `try/except` in business logic is FORBIDDEN when `r` composition (`map`/`flat_map`/`lash`) can handle the flow
- Catch explicit exceptions, never bare `except:` or `except Exception:`
- Domain exceptions inherit from flext exception hierarchy: `FlextError` base with specific subclasses
## Logging
- Use `FlextLogger` abstraction (never `print()` or `logging` directly in production)
- Logger access: `from flext_core import FlextServices` then use `s.get_logger()`
- Log levels: debug < info < warning < error < critical
- Structured context: Use keyword arguments for context fields
- No raw tracebacks in logs; use result/error objects for structured output
## Comments
- Explain the WHY, not the WHAT (code should be self-documenting)
- Highlight non-obvious design decisions or trade-offs
- Mark TODO/FIXME with responsibility and timeline: `# TODO(owner): description (target_date)`
- Warn about subtle invariants or performance implications
- Never document trivial logic or iterate over obvious loop structure
- Use module docstrings (triple-quoted at module top) to explain purpose and scope
- Use class docstrings to explain responsibility and key methods
- Use function/method docstrings with:
## Function Design
- Target: 15-30 lines of logical code
- Absolute cap: 200 lines (strict enforcement)
- Single responsibility: one domain concept per function
- Parameters: Maximum 5-7 (use dataclass/Pydantic model if more needed)
- Use dataclass or Pydantic models for multiple related parameters
- Keyword-only after 2-3 positional args: `def func(arg1, arg2, *, kwarg1, kwarg2)`
- Type hints MANDATORY for all parameters: `def func(value: str) -> r[Result]:`
- Never use `*args` or `**kwargs` in production code (only test fixtures)
- Always include explicit return type: `-> r[T]`, `-> T | None` (if semantically required), `-> None`
- Consistent return across all code paths (no implicit `None` returns)
- Use `r[T]` for operations that can fail, never bare exceptions
- Multi-value returns: Use Pydantic model or named tuple, never bare tuples
## Module Design
- Public API defined in module docstring and `__all__` list
- Top-level `__init__.py` files are AUTO-GENERATED and EXPORT-ONLY
- Use native `__getattr__` module-level lazy loading pattern (generated via `make codegen`)
- Never manually edit auto-generated `__init__.py` files
- Organize subpackage exports through `__init__.py` in `_modules/`
- Central facade classes compose all domain subclasses via MRO inheritance
- Example: `FlextModels` inherits from `FlextModelFoundation`, `FlextModelsCqrs`, `FlextModelsEntity`, etc.
- Every class MUST extend `BaseModel` or FLEXT base models via MRO
- Use `Field()` with constraints, descriptions, and defaults
- Use `model_config = ConfigDict(...)` for serialization/validation settings
- Use `PrivateAttr()` for internal mutable state
- Use `field_validator` or `model_validator` for custom logic
- Forbidde: Standalone `*Config` classes, unnecessary `@property`, manual `self._x` assignments
- Single namespace class per tier: exactly ONE `FlextXyzModels`, `FlextXyzUtilities`, `FlextXyzConstants` per project
- All domain logic resides in this single class via inheritance from `_models/`, `_utilities/`, `_constants/` subclasses
- Loose functions/classes outside MRO hierarchy are FORBIDDEN – absorb into namespace classes
- Subprojects inherit parent facades to cascade namespaces: `class FlextTapOracleProtocols(FlextMeltanoProtocols, FlextOracleProtocols): pass`
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Four-layer inward dependency flow: `L3` (Orchestration) → `L2` (Domain/Infrastructure) → `L1` (Foundation/Bridge) → `L0` (Contracts)
- Dispatcher-first message handling with handler registration and execution reliability
- MRO-based namespace composition via single facade classes per tier (Models, Constants, Protocols, Utilities)
- Strict dependency isolation between platform chains (Core → Cli → Meltano → Integration) and (Core → Web → Api → Auth)
- Result-oriented error handling with `r[T]` type for all fallible operations
- Pydantic v2 BaseModel validation throughout domain layers
## Layers
- Purpose: Type definitions, protocols, and strict typing contracts
- Location: `flext-core/src/flext_core/_typings/`, `flext-core/src/flext_core/_protocols/`
- Contains: Type aliases (`t.*`), Protocols (`p.*`), structured contracts via `annotated-types`
- Depends on: Python standard library only
- Used by: All higher layers
- Purpose: Core runtime utilities, context propagation, container management, dependency injection
- Location: `flext-core/src/flext_core/` (runtime.py, context.py, container.py, registry.py, service.py)
- Contains: FlextContext for correlation/timing, FlextLogger for structured logging, FlextDispatcher for message routing, FlextService base for DI integration
- Depends on: L0 (contracts), external libs (dependency_injector, structlog, orjson, pydantic)
- Used by: Domain/Infrastructure layers and orchestration
- Purpose: Domain entities, value objects, CQRS models, constants, utilities for business logic
- Location: `flext-core/src/flext_core/` (models.py, constants.py, utilities.py, exceptions.py, handlers.py)
- Contains: FlextModels (Entity, AggregateRoot, Command, Query, DomainEvent), FlextConstants (validation, settings, platform), FlextUtilities (guards, introspection, transformation)
- Depends on: L1 (Foundation), L0 (Contracts)
- Used by: Orchestration layer and project-specific domain modules
- Purpose: Platform-specific implementations, integration projects, API servers, CLI tools
- Location: `flext-api/`, `flext-cli/`, `flext-meltano/`, `flext-tap-*/`, `flext-target-*/`, `flext-dbt-*/`
- Contains: FlextApi (HTTP facade), protocol implementations, lifecycle managers, schema validators, client adapters
- Depends on: L2 (Domain), L1 (Foundation), L0 (Contracts), external SDKs
- Used by: Executable applications and external consumers
## Data Flow
- **Request State:** Stored in `FlextContext` via contextvars (survives async/thread hops)
- **Service State:** Stored in FlextService instance attributes and DI container
- **Domain State:** Immutable Pydantic models with explicit change tracking via events
- **Correlation:** Automatic via FlextContext (no manual thread-local management needed)
## Key Abstractions
- Purpose: Base class for all executable services (Web, API, CLI, Scheduler)
- Examples: `FlextApi(s[FlextApiSettings])`, `FlextWebApp(s[...])`, `FlextCliApp(s[...])`
- Pattern: Inherits from `FlextService` with generic config type; implements `__init__`, `execute()`, `shutdown()`
- Lifecycle: Created → configured → wired → handlers registered → execute() → shutdown()
- Purpose: Type-safe error handling for fallible operations
- Examples: `r[str].ok("success")`, `r[User].fail("not found")`, `result.map(transform)`, `result.flat_map(chain)`
- Pattern: Encapsulates success value or failure message with error code; supports monadic composition
- Never use: `T | None`, bare exceptions, or ad-hoc error dicts
- Purpose: Domain-driven entities, aggregates, commands, queries, events
- Examples: `m.Entity`, `m.AggregateRoot`, `m.Command`, `m.Query`, `m.DomainEvent`, `m.ValueObject`
- Pattern: Inherit from Pydantic BaseModel with MRO composition; provide validation, serialization, event tracking
- All models extend base classes from `_models/` and compose via `FlextModels` facade
- Purpose: Message routing and handler registration for CQRS
- Examples: `dispatcher.register_handler(GetUserCommand, get_user_handler)`, `dispatcher.dispatch(command)`
- Pattern: Internal dict maps message type names to handler tuples; supports auto-routing and event subscribers
- Returns: `r[T]` result from handler execution
- Purpose: Request-scoped correlation, metadata, timing across async boundaries
- Examples: `FlextContext.current()`, `context.correlation_id`, `context.with_scope(...)`
- Pattern: contextvars-based so survives thread/async hops; FlextLogger hooks for structured logs
- Managed by: FlextDispatcher and FlextApi middleware automatically
- Purpose: Structural typing contracts (no inheritance required)
- Examples: `p.Logger`, `p.Routable`, `p.ResultLike`, `p.DispatchMessage`
- Pattern: Python Protocols (PEP 544) for duck typing; no MRO inheritance needed
- Used by: Handlers, middleware, external adapters for type narrowing
- Purpose: Centralized constant definitions (validation rules, HTTP status codes, settings)
- Examples: `c.COMMAND_PROCESSING_FAILED`, `c.DEFAULT_TIMEOUT`, `c.VALIDATION_ERRORS`
- Pattern: Grouped in `_constants/` subdirectories (base, cqrs, infrastructure, validation, etc.)
- Composed via: `FlextConstants` facade MRO
- Purpose: Shared helper functions (guards, introspection, transformations)
- Examples: `u.is_pydantic_model()`, `u.get_message_route()`, `u.normalize_value()`
- Pattern: Grouped in `_utilities/` subdirectories; organized by purpose (guards, introspection, transformations)
- Accessed via: Canonical `u.*` namespace only
## Entry Points
- Location: `flext-core/src/flext_core/dispatcher.py`
- Triggers: Service initialization, handler registration, message dispatch
- Responsibilities: Route messages to handlers, manage subscriptions, return results
- Location: `flext-api/src/flext_api/api.py`
- Triggers: HTTP request received by FastAPI
- Responsibilities: Delegate to FlextApiClient, validate via FlextApiModels, serialize via FlextApiSerializers
- Location: `flext-api/src/flext_api/server.py`
- Triggers: Server startup, incoming protocol messages
- Responsibilities: Route to protocol implementation (HTTP, WebSocket, SSE, AsyncAPI)
- Location: `flext-core/src/flext_core/service.py`
- Triggers: Service instantiation, `execute()` call, shutdown signal
- Responsibilities: DI container wiring, handler registration, resource cleanup
- Location: `flext-core/src/flext_core/context.py`
- Triggers: Middleware entry, handler execution, logger initialization
- Responsibilities: Propagate correlation ID, timing metadata, service identity across layers
## Error Handling
- All fallible operations return `r[T]`, never `T | None` or bare exceptions
- Result composition via `map()`, `flat_map()`, `lash()` for pipeline processing
- Dispatcher catches handler exceptions and wraps in `r[T].fail()` with error code
- FlextLogger captures exceptions automatically via contextvars and result inspection
- HTTP responses transformed via middleware: `r[T]` → HTTP status code, error body
- Domain events can capture failures for event sourcing or audit trails
## Cross-Cutting Concerns
- Framework: `structlog` with JSON output
- FlextLogger provides module-scoped instances with automatic correlation ID injection
- All logs include `correlation_id`, `timestamp`, `level`, and structured context
- Lazy initialization via lazy.py module-level strategy
- Pydantic v2 `BaseModel` with strict `Field()` constraints
- `annotated-types` for portable validation across frameworks (PositiveInt, NonEmptyStr, BoundedStr, etc.)
- Result-wrapped validation: failed validation returns `r[T].fail()`, not exception
- Constants (`c.*`) provide centralized validation bounds and rules
- Platform-specific via `flext-auth/` integration module
- Dispatched through FlextApiServer protocol implementations
- FlextContext can store authenticated user metadata
- Authorization checked in handler decorators or domain service methods
- Framework: `dependency_injector` containers and providers
- FlextService manages container lifecycle: create → wire → execute → shutdown
- Handlers can be methods with `@handler` decorator for auto-wiring
- Resources registered as providers: singleton factories, callable providers, resource providers
- JSON via `orjson` (fast, strict)
- CBOR via `cbor2` for compact binary transport
- GraphQL via `gql` for query language support
- Schemas: OpenAPI, AsyncAPI, JSONSchema validators
- Models inherit Pydantic `model_dump()` for transport serialization
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
