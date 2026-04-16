---
name: async-python-patterns
description: Python asyncio patterns for FLEXT integrations — LDAP, Oracle, gRPC async operations. Use when building async pipelines, concurrent integrations, or I/O-bound FLEXT operations.

---

# Async Python Patterns

**Reviewed**: 2026-02-17 | **Scope**: Disabled skill revival

## Scope

- Async service implementations across FLEXT subprojects
- `flext-core/src/flext_core/` — async-compatible result and service patterns
- `flext-auth/`, `flext-grpc/` — async API and gRPC handlers

## References

- `AGENTS.md` — canonical governance source
- <https://docs.python.org/3.13/library/asyncio.html>
- `.claude/skills/lib-returns/SKILL.md` — r composition (async-compatible)
- `.claude/skills/flext-patterns/SKILL.md` — core patterns

## Rules

- Always combine async operations with `r` for error handling.
- Use `asyncio.gather()` for concurrent I/O — never sequential awaits for independent operations.
- Use `asyncio.Semaphore` for rate-limiting external API calls.
- Use `async with` context managers for resource cleanup (connections, sessions).
- Never use `asyncio.run()` inside an already-running event loop — use `await` directly.

## Instructions

### Basic Async with r

```python
from __future__ import annotations

import asyncio

from flext_core import m, p, r, t


class User(m.Value):
    user_id: t.NonEmptyStr = m.Field(description="User identifier")
    name: t.NonEmptyStr = m.Field(description="User display name")


async def _db_get_user(user_id: str) -> User:
    await asyncio.sleep(0)  # simulated async DB call
    return User(user_id=user_id, name="Alice")


async def fetch_user(user_id: str) -> p.Result[User]:
    try:
        user = await _db_get_user(user_id)
        return r[User].ok(user)
    except Exception as e:
        return r[User].fail(f"fetch failed: {e}")
```

### Concurrent Execution with gather

```python
from __future__ import annotations

import asyncio
from collections.abc import Sequence

from flext_core import m, p, r, t


class User(m.Value):
    user_id: t.NonEmptyStr = m.Field(description="User identifier")
    name: t.NonEmptyStr = m.Field(description="User display name")


async def fetch_user(user_id: str) -> p.Result[User]:
    await asyncio.sleep(0)
    return r[User].ok(User(user_id=user_id, name="Alice"))


async def fetch_all_users(ids: t.StrSequence) -> p.Result[Sequence[User]]:
    tasks = [fetch_user(uid) for uid in ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    users: list[User] = []
    for res in results:
        if isinstance(res, BaseException):
            return r[Sequence[User]].fail(str(res))
        if res.success:
            users.append(res.value)
    return r[Sequence[User]].ok(users)
```

### Rate-Limited API Calls

```python
from __future__ import annotations

import asyncio
import json
import urllib.request

from flext_core import p, r

_semaphore = asyncio.Semaphore(10)


async def rate_limited_call(url: str) -> p.Result[dict]:
    async with _semaphore:
        try:
            loop = asyncio.get_running_loop()
            data_bytes = await loop.run_in_executor(
                None,
                lambda: urllib.request.urlopen(url).read(),
            )
            data: dict = json.loads(data_bytes)
            return r[dict].ok(data)
        except Exception as e:
            return r[dict].fail(str(e))
```

### Async Context Manager

```python
from __future__ import annotations

import asyncio
from types import TracebackType
from typing import Self


class AsyncDBConnection:
    """Async context manager for DB connections (stdlib-only example)."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._open = False

    async def __aenter__(self) -> Self:
        await asyncio.sleep(0)  # simulate async connect
        self._open = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await asyncio.sleep(0)  # simulate async close
        self._open = False
```

### Producer-Consumer with Queue

```python
from __future__ import annotations

import asyncio

from flext_core import t


async def _process(item: str) -> str:
    await asyncio.sleep(0)
    return item.upper()


async def producer(queue: asyncio.Queue[str | None], items: t.StrSequence) -> None:
    for item in items:
        await queue.put(item)
    await queue.put(None)


async def consumer(queue: asyncio.Queue[str | None]) -> list[str]:
    results: list[str] = []
    while (item := await queue.get()) is not None:
        results.append(await _process(item))
    return results
```

### Timeout Handling

```python
from __future__ import annotations

import asyncio
from collections.abc import Awaitable

from flext_core import p, r


async def with_timeout[T](coro: Awaitable[T], seconds: float) -> p.Result[T]:
    try:
        result = await asyncio.wait_for(coro, timeout=seconds)
        return r[T].ok(result)
    except TimeoutError:
        return r[T].fail(f"operation timed out after {seconds}s")
```

## Workflow

1. Identify I/O-bound operations suitable for async (network, disk, DB).
2. Wrap each async operation in a `r`-returning coroutine.
3. Use `asyncio.gather()` for concurrent independent operations.
4. Apply rate limiting via `Semaphore` for external APIs.
5. Use `async with` for resource lifecycle management.
6. Add timeouts with `asyncio.wait_for()` for external calls.

## Examples

Good:

```python
from __future__ import annotations

import asyncio

from flext_core import p, r, t


async def process_one(item: str) -> p.Result[str]:
    await asyncio.sleep(0)
    return r[str].ok(item.upper())


async def process_batch(ids: t.StrSequence) -> list[p.Result[str]]:
    tasks = [process_one(i) for i in ids]
    results: list[p.Result[str]] = await asyncio.gather(*tasks)
    return results
```

Why good: concurrent execution of independent I/O operations.

Bad:

```python
from __future__ import annotations

import asyncio

from flext_core import p, r, t


async def process_one(item: str) -> p.Result[str]:
    await asyncio.sleep(0)
    return r[str].ok(item.upper())


# BAD: sequential awaits waste time
async def process_batch_bad(ids: t.StrSequence) -> list[p.Result[str]]:
    results: list[p.Result[str]] = []
    for i in ids:
        results.append(await process_one(i))
    return results
```

Why bad: sequential awaits waste time — each call waits for the previous one to finish.

## Verification

```bash
rg -n "async def|await |asyncio\." --glob "**/*.py" flext-core/src/ flext-auth/src/ flext-grpc/src/
rg -n "asyncio\.gather\|asyncio\.Semaphore\|asyncio\.wait_for" --glob "**/*.py"
```
