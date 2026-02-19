<!-- TOC START -->
- [Scope](#scope)
- [References](#references)
  - [Subproject Usage Map](#subproject-usage-map)
- [Rules](#rules)
- [Instructions](#instructions)
  - [FlextLogger Class Hierarchy](#flextlogger-class-hierarchy)
  - [Configuration (at application startup)](#configuration-at-application-startup)
  - [Logger Creation Patterns](#logger-creation-patterns)
  - [Context Binding](#context-binding)
  - [ClassVar State](#classvar-state)
  - [FlextRuntime Structlog Integration](#flextruntime-structlog-integration)
- [Workflow](#workflow)
- [Examples](#examples)
  - [Good: Module logger with scoped context](#good-module-logger-with-scoped-context)
  - [Good: Container-scoped logger for DI](#good-container-scoped-logger-for-di)
  - [Bad: Direct structlog usage](#bad-direct-structlog-usage)
  - [Bad: Configuring structlog at logger creation](#bad-configuring-structlog-at-logger-creation)
  - [Bad: Forgetting to clean up scoped context](#bad-forgetting-to-clean-up-scoped-context)
- [Verification](#verification)
<!-- TOC END -->

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

- <https://www.structlog.org/en/stable/> — structlog official docs
- `flext-core/pyproject.toml` — pins `structlog>=25.4.0`
- `flext-core/tests/unit/test_runtime.py` — runtime/logger tests

### Subproject Usage Map

- `flext-core`: owns `FlextLogger` and runtime structlog configuration bridge.
- `flext-auth`: consumes structured logging patterns in auth flows and middleware.
- `flext-grpc`: relies on structured logger context for request/transport events.
- `flext-cli`: uses logger output controls for command execution traces.

## Rules

- **Never** configure structlog directly — always use `FlextRuntime.configure_structlog()` at application bootstrap.
- **Never** create loggers with `structlog.get_logger()` directly — use `FlextLogger.create_module_logger(name)` or `FlextLogger.for_container(container)`.
- Bind context via `FlextLogger.Context` methods — never modify `structlog.contextvars` directly.
- Clean up scoped contexts to prevent leakage across requests/operations.

## Instructions

### FlextLogger Class Hierarchy

`FlextLogger` inherits from `FlextRuntime` and implements `p.Log.StructlogLogger` protocol.

**Nested Operation Groups** (composition pattern):

- `FlextLogger.Context` — bind/unbind/scoped context management
- `FlextLogger.Factory` — `create_service_logger`, `create_module_logger`
- `FlextLogger.Performance` — timing and performance helpers
- `FlextLogger.ResultAdapter` — inner class wrapping log methods to return `r[bool]`

### Configuration (at application startup)

```python
from flext_core import FlextRuntime

# One-time setup — MUST be called before any logging
FlextRuntime.configure_structlog(
    level="INFO",
    json_output=True,
    processors=[...],  # optional custom processors
)
```

Internal lazy fallback: `FlextRuntime.ensure_structlog_configured()` is called by `create_module_logger` if not yet configured, but explicit bootstrap is strongly preferred.

### Logger Creation Patterns

```python
from flext_core import FlextLogger

# Module-level logger (most common)
logger = FlextLogger.create_module_logger(__name__)

# Container-scoped logger (DI integration)
logger = FlextLogger.for_container(container, level="DEBUG", correlation_id="abc-123")

# Static bridge to FlextRuntime.get_logger
logger = FlextLogger.get_logger("my_service")
```

### Context Binding

```python
# Global context (persists across all log entries)
FlextLogger.Context.bind_global_context(request_id="req-123", tenant="acme")
FlextLogger.Context.clear_global_context()
FlextLogger.Context.unbind_global_context("request_id")

# Level-based context (only for specific log levels)
FlextLogger.Context.bind_context_for_level("DEBUG", trace_id="xyz")
FlextLogger.Context.unbind_context_for_level("DEBUG", "trace_id")

# Scoped context (context manager — auto-cleanup)
with FlextLogger.Context.scoped_context(operation="user_sync"):
    logger.info("processing")  # includes operation="user_sync"
# operation key is automatically removed here
```

### ClassVar State

```python
_scoped_contexts: ClassVar[dict[str, dict[str, t.GeneralValueType]]]  # {scope: {key: value}}
_level_contexts: ClassVar[dict[str, dict[str, t.GeneralValueType]]]   # {level: {key: value}}
```

### FlextRuntime Structlog Integration

In `runtime.py`, the `FlextRuntime` class provides:

- `FlextRuntime.structlog()` — returns the structlog module
- `FlextRuntime.get_logger(name)` — creates a bound logger
- `FlextRuntime.configure_structlog(...)` — sets up processor chain (TimeStamper, level filter, context merge, JSONRenderer)
- `FlextRuntime.ensure_structlog_configured()` — lazy one-time init
- `FlextRuntime.is_structlog_configured()` — check config state
- `FlextRuntime.reset_structlog_state_for_testing()` — reset for test isolation

Telemetry integration methods:

- `FlextRuntime.Integration.track_service_resolution(...)` — emit directly to structlog
- `FlextRuntime.Integration.track_domain_event(...)` — emit directly to structlog

## Workflow

1. Call `FlextRuntime.configure_structlog()` in your application bootstrap
2. Create loggers via `FlextLogger.create_module_logger(__name__)`
3. Bind request/operation context via `FlextLogger.Context.bind_global_context()`
4. Use `scoped_context()` for operation-scoped context that auto-cleans
5. Use `FlextLogger.ResultAdapter` when you need log operations to return `r[bool]`

## Examples

### Good: Module logger with scoped context

```python
from flext_core import FlextLogger

logger = FlextLogger.create_module_logger(__name__)

async def handle_request(request_id: str):
    with FlextLogger.Context.scoped_context(request_id=request_id):
        logger.info("request_started")
        result = process(request_id)
        logger.info("request_completed", success=result.is_success)
    # request_id context is auto-cleaned here
```

### Good: Container-scoped logger for DI

```python
logger = FlextLogger.for_container(
    container,
    level="DEBUG",
    service_name="auth",
)
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
# ✗ WRONG — configuration belongs in bootstrap only
def get_logger():
    structlog.configure(processors=[...])  # DON'T do this
    return structlog.get_logger()
```

**Why bad**: Causes race conditions and inconsistent processor chains. Call `FlextRuntime.configure_structlog()` once at startup.

### Bad: Forgetting to clean up scoped context

```python
# ✗ WRONG — context leaks to subsequent requests
FlextLogger.Context.bind_global_context(user_id="123")
process_request()
# forgot to unbind → user_id appears in all subsequent logs
```

**Why bad**: Context leakage causes misleading log entries. Use `scoped_context()` or explicitly `unbind_global_context()`.

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
