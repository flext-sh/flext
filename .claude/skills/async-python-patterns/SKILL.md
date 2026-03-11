<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
  - [Basic Async with r](#basic-async-with-flextresult)
  - [Concurrent Execution with gather](#concurrent-execution-with-gather)
  - [Rate-Limited API Calls](#rate-limited-api-calls)
  - [Async Context Manager](#async-context-manager)
  - [Producer-Consumer with Queue](#producer-consumer-with-queue)
  - [Timeout Handling](#timeout-handling)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

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
from flext_core import r


async def fetch_user(user_id: str) -> r[User]:
    try:
        user = await db.get_user(user_id)
        return r[User].ok(user)
    except Exception as e:
        return r[User].fail(f"fetch failed: {e}")
```

### Concurrent Execution with gather

```python
async def fetch_all_users(ids: list[str]) -> r[list[User]]:
    tasks = [fetch_user(uid) for uid in ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    users = []
    for res in results:
        if isinstance(res, Exception):
            return r[list[User]].fail(str(res))
        if res.is_success:
            users.append(res.value)
    return r[list[User]].ok(users)
```

### Rate-Limited API Calls

```python
semaphore = asyncio.Semaphore(10)


async def rate_limited_call(url: str) -> r[dict]:
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                return r[dict].ok(data)
```

### Async Context Manager

```python
class AsyncDBConnection:
    async def __aenter__(self) -> Self:
        self.conn = await asyncpg.connect(DSN)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.conn.close()
```

### Producer-Consumer with Queue

```python
async def producer(queue: asyncio.Queue[str], items: list[str]) -> None:
    for item in items:
        await queue.put(item)
    await queue.put(None)


async def consumer(queue: asyncio.Queue[str | None]) -> list[str]:
    results = []
    while (item := await queue.get()) is not None:
        results.append(await process(item))
    return results
```

### Timeout Handling

```python
async def with_timeout(coro: Awaitable[T], seconds: float) -> r[T]:
    try:
        result = await asyncio.wait_for(coro, timeout=seconds)
        return r[T].ok(result)
    except asyncio.TimeoutError:
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
async def process_batch(ids: list[str]) -> r[list[Result]]:
    tasks = [process_one(i) for i in ids]
    return await asyncio.gather(*tasks)
```

Why good: concurrent execution of independent I/O operations.

Bad:

```python
async def process_batch(ids: list[str]) -> list[Result]:
    results = []
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
