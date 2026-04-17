---
name: lib-structlog
description: FlextLogger structured logging with context propagation, DI factories, and result adapters. Use when adding logging, binding context, or configuring structlog processors.

---

# Lib Structlog — FlextLogger and Context-Aware Logging

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

## Scope

- `flext-core/src/flext_core/loggings.py` — FlextLogger class (context-aware, DI-ready logger)
- `flext-core/src/flext_core/runtime.py` — structlog configuration and processor chain setup

## References

- `AGENTS.md` — canonical governance source
- <https://www.structlog.org/en/stable/> — structlog official docs
- `flext-core/pyproject.toml` — pins `structlog>=25.4.0`
- `flext-core/tests/unit/test_runtime.py` — runtime/logger tests

### Subproject Usage Map

- `flext-core`: owns `FlextLogger` and runtime structlog configuration bridge.
- `flext-auth`: consumes structured logging patterns in auth flows and middleware.
- `flext-grpc`: relies on structured logger context for request/transport events.
- `flext-cli`: uses logger output controls for command execution traces.

## Rules

- **Never** configure structlog directly — always use `u.configure_structlog()` at application bootstrap.
- **Never** create loggers with `structlog.get_logger()` directly — use `FlextLogger.create_module_logger(name)` or `FlextLogger.for_container(container)`.
- Bind context via `FlextLogger.Context` methods — never modify `structlog.contextvars` directly.
- Clean up scoped contexts to prevent leakage across requests/operations.

## Instructions

### FlextLogger Class Hierarchy

`FlextLogger` inherits from `u` and implements `p.Logger` protocol.

**Nested Operation Groups** (composition pattern):

- `FlextLogger.Context` — bind/unbind/scoped context management
- `FlextLogger.Factory` — `create_service_logger`, `create_module_logger`
- `FlextLogger.Performance` — timing and performance helpers
- `FlextLogger.ResultAdapter` — inner class wrapping log methods to return `r[bool]`

### Configuration (at application startup)

```python
from flext_core import u

# One-time setup — MUST be called before any logging
u.configure_structlog(log_level=20, console_renderer=True)
```

Internal lazy fallback: `u.ensure_structlog_configured()` is called by `create_module_logger` if not yet configured, but explicit bootstrap is strongly preferred.

### Logger Creation Patterns

```python
from flext_core import u

# Module-level logger (most common)
logger = u.create_module_logger(__name__)

# Named logger (alternative)
logger2 = u.create_module_logger("my_service")
```

### Context Binding

```python
from flext_core import u

# Global context (persists across all log entries)
u.bind_global_context(request_id="req-123", tenant="acme")
u.clear_global_context()
u.unbind_global_context("request_id")

# Level-based context (only for specific log levels)
u.bind_context_for_level("DEBUG", trace_id="xyz")

# Scoped context (bind to named scope, clear when done)
u.bind_context("request", operation="user_sync")
u.clear_scope("request")
```

### ClassVar State

Internal to `FlextLogger` (accessed via `u` MRO):

- `_scoped_contexts: ClassVar[t.ScopedContainerRegistry]` — `{scope: {key: value}}`
- `_level_contexts: ClassVar[t.ScopedContainerRegistry]` — `{level: {key: value}}`

### u Structlog Integration

In `runtime.py`, the `u` class provides:

- `u.structlog()` — returns the structlog module
- `u.create_module_logger(name)` — creates a bound logger
- `u.configure_structlog(...)` — sets up processor chain (TimeStamper, level filter, context merge, JSONRenderer)
- `u.ensure_structlog_configured()` — lazy one-time init
- `u.is_structlog_configured()` — check settings state
- `u.reset_structlog_state_for_testing()` — reset for test isolation

Telemetry integration methods:

- `u.Integration.track_service_resolution(...)` — emit directly to structlog
- `u.Integration.track_domain_event(...)` — emit directly to structlog

## Workflow

1. Call `u.configure_structlog()` in your application bootstrap
2. Create loggers via `FlextLogger.create_module_logger(__name__)`
3. Bind request/operation context via `FlextLogger.Context.bind_global_context()`
4. Use `scoped_context()` for operation-scoped context that auto-cleans
5. Use `FlextLogger.ResultAdapter` when you need log operations to return `r[bool]`

## Examples

### Good: Module logger with scoped context

```python
from __future__ import annotations

import asyncio

from flext_core import p, r, u

logger = u.create_module_logger(__name__)


async def handle_request(request_id: str) -> p.Result[str]:
    """Handle request with scoped context."""
    u.bind_context("request", request_id=request_id)
    logger.info("request_started")
    await asyncio.sleep(0)
    logger.info("request_completed")
    u.clear_scope("request")
    return r[str].ok(request_id)
```

### Good: Container-scoped logger for DI

```python
from flext_core import FlextContainer, u

container = FlextContainer()
logger = u.for_container(container, service_name="auth")
logger.info("service_initialized")
```

### Bad: Direct structlog usage

```python
# ✗ WRONG — bypasses FlextLogger context management
import structlog

logger = structlog.get_logger("my_module")
```

**Why bad**: Misses global/scoped context bindings, DI integration, and result adapters. Use `FlextLogger.create_module_logger()`.

### Bad: Configuring structlog at logger creation

```python
from __future__ import annotations

import structlog


# WRONG — configuration belongs in bootstrap only
def get_logger_bad() -> structlog.stdlib.BoundLogger:
    """Anti-pattern: configuring structlog at logger creation."""
    structlog.configure(processors=[])
    return structlog.get_logger()
```

**Why bad**: Causes race conditions and inconsistent processor chains. Call `u.configure_structlog()` once at startup.

### Bad: Forgetting to clean up scoped context

```python
from flext_core import u

# WRONG — context leaks to subsequent requests
u.bind_global_context(user_id="123")
# forgot to unbind → user_id appears in all subsequent logs
```

**Why bad**: Context leakage causes misleading log entries. Use `u.bind_context(scope, ...)` + `u.clear_scope(scope)` or explicitly `u.unbind_global_context()`.

## Verification

Make gates:

```bash
make check PROJECT=flext-core                  # lint + type gates for logging module
make check PROJECT=flext-core CHECK_GATES=lint # lint catches direct structlog imports
make test PROJECT=flext-core                   # logging integration tests
```

Pattern checks:

```bash
# Confirm FlextLogger declarations
rg -n "class FlextLogger|class Context:|class Factory:|class Performance:|class ResultAdapter" flext-core/src/flext_core/loggings.py

# Confirm structlog configuration in runtime
rg -n "configure_structlog|ensure_structlog_configured|get_logger" flext-core/src/flext_core/runtime.py

# Verify no direct structlog.get_logger in subprojects
rg -n "structlog\.get_logger" --glob "**/*.py" flext-auth/src/ flext-grpc/src/ flext-cli/src/

# Confirm structlog pinned
rg "structlog>=" flext-core/pyproject.toml
```
