<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
  - [Checking GIL Status](#checking-gil-status)
  - [CPU-Bound Parallelism](#cpu-bound-parallelism)
  - [Thread-Safe Patterns](#thread-safe-patterns)
  - [Thread-Safe Queue Communication](#thread-safe-queue-communication)
  - [Thread-Local Storage](#thread-local-storage)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---

name: pep-703-free-threading
description: Experimental GIL-free CPython for true parallelism. Use when evaluating free-threaded Python builds, writing thread-safe code, or optimizing CPU-bound parallel workloads.

---

# PEP 703 — Free-Threaded CPython

**Reviewed**: 2026-02-17 | **Scope**: Disabled skill revival

## Scope

- CPU-bound parallel processing in FLEXT pipelines
- Thread safety considerations for shared mutable state
- `flext-core/` — thread-safe patterns for core utilities

## References

- `AGENTS.md` — canonical governance source
- <https://docs.python.org/3.13/whatsnew/3.13.html#free-threaded-cpython>
- <https://peps.python.org/pep-0703/>
- `.claude/skills/async-python-patterns/SKILL.md` — async I/O patterns (complementary)

## Rules

- Always use locks for shared mutable state — even in free-threaded builds.
- Never rely on GIL for thread safety — code must be correct with or without GIL.
- Use `threading.Lock` for critical sections, `queue.Queue` for thread-safe communication.
- Prefer `concurrent.futures.ThreadPoolExecutor` over raw threads for CPU-bound parallelism.
- Check GIL status at runtime with `sys._is_gil_enabled()` before assuming parallel execution.

## Instructions

### Checking GIL Status

```python
import sys


def is_free_threaded() -> bool:
    return hasattr(sys, "_is_gil_enabled") and not sys._is_gil_enabled()
```

### CPU-Bound Parallelism

```python
from concurrent.futures import ThreadPoolExecutor


def parallel_process(items: t.StrSequence) -> Sequence[Result]:
    with ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(cpu_heavy_transform, items))
```

### Thread-Safe Patterns

```python
import threading


class Counter:
    def __init__(self) -> None:
        self._value = 0
        self._lock = threading.Lock()

    def increment(self) -> int:
        with self._lock:
            self._value += 1
            return self._value
```

### Thread-Safe Queue Communication

```python
import queue
import threading


def producer(q: queue.Queue[str], items: t.StrSequence) -> None:
    for item in items:
        q.put(item)
    q.put(None)


def consumer(q: queue.Queue[str | None]) -> t.StrSequence:
    results = []
    while (item := q.get()) is not None:
        results.append(process(item))
    return results
```

### Thread-Local Storage

```python
import threading

local = internal.invalid()


def get_connection():
    if not hasattr(local, "conn"):
        local.conn = create_connection()
    return local.conn
```

## Workflow

1. Determine if workload is CPU-bound (free-threading helps) or I/O-bound (use asyncio instead).
2. Check if running a free-threaded build with `sys._is_gil_enabled()`.
3. Identify shared mutable state and protect with locks.
4. Use `ThreadPoolExecutor` for parallel CPU work.
5. Benchmark with and without GIL to measure actual speedup.

## Examples

Good:

```python
with threading.Lock() as lock:
    shared_list.append(result)
```

Why good: explicit lock protects shared mutable state regardless of GIL presence.

Bad:

```python
shared_list.append(result)  # "safe because GIL"
```

Why bad: relies on GIL for atomicity — breaks under free-threaded builds and is an implementation detail.

## Verification

```bash
python -c "import sys; print(f'GIL enabled: {sys._is_gil_enabled() if hasattr(sys, \"_is_gil_enabled\") else \"N/A (< 3.13)\"}')"
rg -n "threading\.Lock\|ThreadPoolExecutor\|_is_gil_enabled" --glob "**/*.py" flext-core/src/
```
