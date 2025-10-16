# Logging Context Cleanup Pattern - FLEXT Ecosystem

**Date**: 2025-10-15
**Version**: 1.0.0
**Status**: ✅ Production Pattern
**Scope**: All 33 FLEXT Projects

---

## Executive Summary

**Problem**: structlog's global context accumulates across operations, causing logging variables to repeat and grow with each service call.

**Solution**: Three-layer defense with automatic cleanup at foundation, service, and application boundaries.

**Impact**: Zero context accumulation, predictable logging, clean separation of operation contexts.

---

## Table of Contents

1. [Problem Description](#problem-description)
2. [Root Cause Analysis](#root-cause-analysis)
3. [Solution Architecture](#solution-architecture)
4. [Implementation Layers](#implementation-layers)
5. [Usage Guidelines](#usage-guidelines)
6. [Testing Strategy](#testing-strategy)
7. [Migration Guide](#migration-guide)
8. [Best Practices](#best-practices)

---

## Problem Description

### Symptoms

When running CLI commands or executing multiple service operations:

```bash
# First run - clean
[INFO] operation=migrate module=migration_service Processing entries...

# Second run - accumulation begins
[INFO] operation=migrate operation=validate module=migration_service module=validation_service Processing entries...

# Third run - context explosion
[INFO] operation=migrate operation=validate operation=sync operation=migrate operation=validate module=migration_service module=validation_service module=sync_service ...
```

### Impact

1. **Log Pollution**: Repeated context variables make logs unreadable
2. **Performance**: Growing context increases logging overhead
3. **Debugging**: Hard to identify which operation generated logs
4. **Memory**: Context variables persist in memory across operations

### Affected Variables

- `operation`: Operation name from `@log_operation` decorator
- `correlation_id`: Request correlation from `@with_correlation` decorator
- `module`, `function`, `service_name`: Service context bindings
- Custom context: Any `FlextLogger.bind_global_context()` calls

---

## Root Cause Analysis

### FlextDecorators

The decorators in `flext-core/src/flext_core/decorators.py` bind global context:

```python
# @log_operation decorator (line 170)
FlextLogger.bind_global_context(operation=op_name)

# @track_performance decorator (line 267)
FlextLogger.bind_global_context(operation=op_name)
```

While they attempt cleanup in `finally` blocks, context can accumulate because:

1. **Global Persistence**: structlog's contextvars persist across function calls
2. **Nested Operations**: Decorators stack when services call other services
3. **Partial Unbind**: `unbind_global_context("operation")` only removes one key
4. **Cross-Service State**: Context survives service boundaries

### Structlog Context Management

```python
# structlog uses contextvars for global context
import structlog

# This persists across ALL subsequent logging calls
structlog.contextvars.bind_contextvars(operation="first")

# This ADDS to existing context (doesn't replace)
structlog.contextvars.bind_contextvars(operation="second")

# Result: Both operations in context!
```

---

## Solution Architecture

### Three-Layer Defense Strategy

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: APPLICATION BOUNDARY (client-a-oud-mig, etc.)        │
│ - Clear at command START: FlextLogger.clear_global_context()│
│ - Clear at CLI exit: finally block cleanup                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: SERVICE LIFECYCLE (flext-core)                    │
│ - execute_with_context_cleanup(): Automatic wrapper         │
│ - Guarantees cleanup after service execution                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: DECORATOR CLEANUP (flext-core)                    │
│ - Enhanced finally blocks with suppress()                   │
│ - Defensive cleanup that never fails                        │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Defense in Depth**: Multiple cleanup layers ensure no accumulation
2. **Fail-Safe**: Cleanup failures don't break application flow
3. **Explicit Boundaries**: Clear at operation/command boundaries
4. **Zero Tolerance**: No context should leak between operations

---

## Implementation Layers

### Layer 1: Foundation (flext-core)

#### A. Service Lifecycle Cleanup

**File**: `flext-core/src/flext_core/service.py`

```python
def execute_with_context_cleanup(self) -> FlextResult[TDomainResult]:
    """Execute with automatic context cleanup.

    Prevents context accumulation by clearing global logging context
    after service execution completes.

    Usage:
        >>> service = MyService()
        >>> result = service.execute_with_context_cleanup()  # Auto-cleaned
    """
    try:
        return self.execute()
    finally:
        # CRITICAL: Clean up global logging context
        self._clear_operation_context()
```

**When to Use**:

- CLI/API boundaries calling services
- Long-running service orchestrators
- Batch processing workflows

#### B. Decorator Defensive Cleanup

**File**: `flext-core/src/flext_core/decorators.py`

```python
from contextlib import suppress

@staticmethod
def log_operation(operation_name: str | None = None):
    """Decorator with defensive cleanup."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            FlextLogger.bind_global_context(operation=op_name)
            try:
                return func(*args, **kwargs)
            finally:
                # CRITICAL: Defensive cleanup (never fails)
                with suppress(Exception):
                    FlextLogger.unbind_global_context("operation")
        return wrapper
    return decorator
```

**Pattern**: Use `contextlib.suppress` for guaranteed cleanup without exceptions.

### Layer 2: Application Entry Points

#### Pattern: CLI Command Cleanup with Correlation

**File**: `src/your_app/cli.py`

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

class YourAppCli:
    def _execute_command(self, args: list[str]) -> FlextResult[None]:
        # CRITICAL: Clear and initialize context for this CLI invocation
        FlextLogger.clear_global_context()

        # Generate unique correlation_id for this CLI run
        # All logs for this invocation will share this correlation_id
        correlation_id = FlextContext.Correlation.generate_correlation_id()
        self.logger.debug(
            "cli_command_started",
            command="your_command",
            correlation_id=correlation_id,
        )

        # Execute command logic
        service = YourService()
        result = service.execute_with_context_cleanup()

        return result

    def execute_cli(self, args: list[str] | None = None) -> FlextResult[None]:
        try:
            # Route and execute commands
            return self._execute_command(args)
        finally:
            # CRITICAL: Clear context at CLI exit
            FlextLogger.clear_global_context()
```

#### Pattern: Application Entry Point

**File**: `src/your_app/__main__.py`

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities
from your_app.cli import YourAppCli

if __name__ == "__main__":
    try:
        cli = YourAppCli()
        result = cli.execute_cli()
        if result.is_failure:
            sys.exit(1)
    finally:
        # CRITICAL: Defensive cleanup on application exit
        FlextLogger.clear_global_context()
```

---

## Usage Guidelines

### When to Clear Context

| Location             | When                               | Method                               |
| -------------------- | ---------------------------------- | ------------------------------------ |
| **Command Start**    | At beginning of each CLI command   | `FlextLogger.clear_global_context()` |
| **CLI Exit**         | In finally block of execute_cli()  | `FlextLogger.clear_global_context()` |
| **Service Calls**    | When calling services from CLI/API | Use `execute_with_context_cleanup()` |
| **Application Exit** | In **main**.py finally block       | `FlextLogger.clear_global_context()` |

### What Gets Cleared

```python
FlextLogger.clear_global_context()
```

Clears ALL global context variables:

- `operation` (from `@log_operation`)
- `correlation_id` (from `@with_correlation`)
- `module`, `function`, `service_name` (from service bindings)
- Any custom context from `bind_global_context()`

### What Doesn't Get Cleared

- **Logger-specific context**: From `logger.bind()` (creates new logger instance)
- **Thread-local context**: If using threading
- **Process-level config**: Application configuration

---

## Testing Strategy

### Test Scenarios

#### 1. Context Cleared After Execution

```python
def test_context_cleared_after_execution():
    """Verify context is cleared after CLI execution."""
    FlextLogger.clear_global_context()

    # Execute command
    cli = YourAppCli()
    result = cli.execute_cli(["command"])

    # Verify cleanup
    context = FlextLogger.get_global_context()
    assert len(context) == 0, "Context should be cleared"
```

#### 2. No Accumulation Across Multiple Runs

```python
def test_no_accumulation_across_runs():
    """Simulate repeated CLI invocations."""
    FlextLogger.clear_global_context()

    for i in range(5):
        cli = YourAppCli()

        # Bind test context
        FlextLogger.bind_global_context(iteration=i)

        # Execute
        result = cli.execute_cli(["command"])

        # Verify no accumulation
        context = FlextLogger.get_global_context()
        assert len(context) == 0, f"Context should be cleared after iteration {i}"
```

#### 3. Cleanup on Errors

```python
def test_cleanup_on_error():
    """Ensure cleanup happens even on errors."""
    FlextLogger.clear_global_context()
    FlextLogger.bind_global_context(test_error="error_scenario")

    # Execute with invalid command (will fail)
    cli = YourAppCli()
    result = cli.execute_cli(["invalid-command"])

    # Verify cleanup despite error
    context = FlextLogger.get_global_context()
    assert len(context) == 0, "Context should be cleared even on error"
```

### Test Coverage Requirements

- ✅ Context cleared after successful execution
- ✅ Context cleared after failed execution
- ✅ No accumulation across multiple operations
- ✅ Entry point cleanup (\_\_main\_\_.py)

---

## Migration Guide

### Step 1: Update flext-core (Already Done ✅)

The foundation patterns are already implemented in flext-core v0.9.9+:

- `Service.execute_with_context_cleanup()`
- Enhanced decorators with `suppress()`

### Step 2: Update Your Application

For each CLI application in the FLEXT ecosystem:

#### 2.1: Add Command-Level Cleanup

```python
# src/your_app/cli.py
def _execute_your_command(self, args: list[str]) -> FlextResult[None]:
    # ADD THIS LINE at start of EACH command handler
    FlextLogger.clear_global_context()

    # ... rest of command logic
```

#### 2.2: Add CLI Exit Cleanup

```python
# src/your_app/cli.py
def execute_cli(self, args: list[str] | None = None) -> FlextResult[None]:
    try:
        # ... command routing and execution
        return result
    finally:
        # ADD THIS cleanup in finally block
        FlextLogger.clear_global_context()
```

#### 2.3: Add Application Exit Cleanup

```python
# src/your_app/__main__.py
if __name__ == "__main__":
    try:
        cli = YourAppCli()
        result = cli.execute_cli()
        if result.is_failure:
            sys.exit(1)
    finally:
        # ADD THIS defensive cleanup
        FlextLogger.clear_global_context()
```

### Step 3: Add Tests

Create `tests/unit/test_cli_logging_context.py` with test scenarios from Testing Strategy section.

### Step 4: Verify

Run your application multiple times and check logs for repeated context variables. Should be zero accumulation!

---

## Best Practices

### ✅ DO

1. **Clear at Boundaries**: Always clear context at command/operation boundaries
2. **Use finally Blocks**: Ensure cleanup happens even on errors
3. **Test Cleanup**: Add tests for context cleanup behavior
4. **Use Wrapper Method**: Prefer `execute_with_context_cleanup()` for service calls
5. **Document Lifecycle**: Add comments explaining context lifecycle

### ❌ DON'T

1. **Assume Auto-Cleanup**: Decorators alone don't clean up all context
2. **Skip Application Cleanup**: CLI applications must implement cleanup
3. **Mix Context Types**: Don't confuse global context with logger-specific context
4. **Skip Testing**: Always test that context cleanup works
5. **Bind Without Understanding**: Know what you're binding to global context

---

## Example Implementation

### Complete Example: client-a-oud-mig

See `client-a-oud-mig/docs/logging-context-pattern.md` for a complete working example.

**Key Files**:

- `src/client-a_oud_mig/cli.py`: Command-level and exit cleanup
- `src/client-a_oud_mig/__main__.py`: Application exit cleanup
- `tests/unit/test_cli_logging_context.py`: Comprehensive tests (4/4 passing)

---

## Architecture Decision Record

### Decision

Implement three-layer context cleanup strategy across FLEXT ecosystem.

### Rationale

1. **Defense in Depth**: Multiple cleanup layers prevent accumulation
2. **Fail-Safe**: Cleanup failures don't break application flow
3. **Explicit**: Clear at obvious boundaries (command start/end)
4. **Testable**: Easy to verify cleanup behavior

### Consequences

**Positive**:

- Zero context accumulation
- Predictable logging behavior
- Clear separation of operation contexts
- Easy to debug and maintain

**Negative**:

- Requires pattern implementation in each application
- Developers must understand context lifecycle
- Slight overhead from cleanup operations

### Alternatives Considered

1. **Auto-Cleanup in Decorators**: Insufficient - doesn't handle nested calls
2. **Context Manager Pattern**: Complex - requires wrapping all operations
3. **Thread-Local Context**: Incompatible - FLEXT uses contextvars
4. **Manual Unbind**: Error-prone - easy to forget keys

---

## Future Enhancements

### Potential flext-core Improvements

#### 1. Scoped Context Decorator

```python
@FlextDecorators.scoped_context()
def operation(self):
    # Context automatically cleared after method returns
    pass
```

#### 2. Context Manager Pattern

```python
with FlextLogger.scoped_context(operation="task"):
    # Context auto-cleared on exit
    do_work()
```

#### 3. Context Lifecycle Hooks

```python
FlextLogger.on_context_change(callback)
FlextLogger.on_context_clear(callback)
```

---

## Related Documentation

- **client-a-oud-mig Pattern**: `client-a-oud-mig/docs/logging-context-pattern.md`
- **flext-core Service**: `flext-core/src/flext_core/service.py`
- **flext-core Decorators**: `flext-core/src/flext_core/decorators.py`
- **FlextLogging**: `flext-core/src/flext_core/loggings.py`

---

## Changelog

### v1.0.0 (2025-10-15)

- ✅ Initial pattern documentation
- ✅ flext-core foundation implementation complete
- ✅ client-a-oud-mig reference implementation complete
- ✅ Three-layer defense strategy validated
- ✅ Test patterns established (4/4 passing)
- ✅ Zero tolerance policy for context accumulation

---

## Support

**Questions**: FLEXT Team
**Issues**: Report to workspace maintainers
**Updates**: This document is maintained in `/home/marlonsc/flext/docs/`

---

**Last Updated**: 2025-10-15
**Status**: ✅ Production Pattern
**Compliance**: ZERO TOLERANCE for context accumulation
