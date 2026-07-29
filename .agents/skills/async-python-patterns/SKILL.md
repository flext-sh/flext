---
name: async-python-patterns
description: 'Use when implementing or reviewing asyncio-based LDAP, Oracle, gRPC, HTTP, or other I/O integrations that require bounded concurrency, cancellation, cleanup, timeout, and typed result flow.'
license: MIT
metadata:
  version: 2.0.0
---
# Async Python Patterns

## Workflow

1. Confirm the operation is I/O-bound and that every dependency offers an async or
   isolated adapter; do not wrap blocking calls without an explicit executor boundary.
2. Define the input, success type, failure mapping, timeout, cancellation behavior,
   and concurrency limit before launching tasks.
3. Acquire connections and sessions with `async with` and release them on success,
   failure, timeout, and cancellation.
4. Run independent operations with bounded concurrency and preserve input/result
   ordering when the consumer contract requires it.
5. Translate expected adapter exceptions once and return `r[T]`; let cancellation
   propagate after cleanup.

## Patterns

```python
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence

from flext_core import r


async def gather_bounded[T](
    values: Sequence[T],
    operation: Callable[[T], Awaitable[r[T]]],
    *,
    limit: int,
) -> list[r[T]]:
    semaphore = asyncio.Semaphore(limit)

    async def run(value: T) -> r[T]:
        async with semaphore:
            return await operation(value)

    return list(await asyncio.gather(*(run(value) for value in values)))
```

Use `TaskGroup` when sibling failure must cancel the group. Use `gather` when each
operation returns its own typed outcome and all outcomes must be collected. Wrap
external calls with `asyncio.timeout(...)` at the boundary that owns the deadline.

## Contracts

- Never call `asyncio.run()` from an async function.
- Never call blocking `time.sleep()` or synchronous HTTP clients from an async function.
- Do not create unbounded tasks from externally sized input.
- Do not swallow `CancelledError`, leak partial resources, or convert cancellation to
  ordinary success/failure.
- Producer/consumer queues have explicit maximum size and shutdown signaling.
- Retries are bounded, classified by error type, and respect the overall deadline.

## Verification

Test success, adapter failure, timeout, cancellation, concurrency limits, stable
ordering, and resource cleanup. Run the focused integration test with a fake or local
real adapter rather than sleeping to coordinate task timing.
