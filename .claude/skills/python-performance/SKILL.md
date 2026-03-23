<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
  - [CPU Profiling with cProfile](#cpu-profiling-with-cprofile)
  - [Line-by-Line Profiling](#line-by-line-profiling)
  - [Memory Profiling](#memory-profiling)
  - [Production Profiling with py-spy](#production-profiling-with-py-spy)
  - [Optimization Patterns](#optimization-patterns)
  - [String Performance](#string-performance)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---

name: python-performance
description: Profile and optimize Python code using cProfile, memory profilers, and performance best practices. Use when debugging slow pipelines, optimizing bottlenecks, or improving application throughput.

---

# Python Performance Optimization

**Reviewed**: 2026-02-17 | **Scope**: Disabled skill revival

## Scope

- Performance-critical paths in FLEXT Python subprojects
- Pipeline processing in `flext-ldif/`, `flext-tap-*/`, `flext-target-*/`
- Data transformation and serialization hot paths

## References

- `AGENTS.md` — canonical governance source
- <https://docs.python.org/3.13/library/profile.html>
- <https://github.com/benfred/py-spy>
- `.claude/skills/flext-patterns/SKILL.md`

## Rules

- Profile before optimizing — never guess at bottlenecks.
- Prefer algorithmic improvements over micro-optimizations.
- Use list comprehensions and generator expressions over explicit loops for data transforms.
- Avoid premature optimization — optimize only measured hot paths.
- Use `__slots__` on high-frequency data classes to reduce memory overhead.
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, `cast()`, and `inline imports`. Wait for definition time or use Protocol decoupling.

## Instructions

### CPU Profiling with cProfile

```python
import cProfile
import pstats


def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("cumulative")
    stats.print_stats(20)
    return result
```

```bash
python -m cProfile -s cumulative script.py
```

### Line-by-Line Profiling

```bash
# line_profiler — add to project dev-dependencies if not already present
kernprof -l -v script.py
```

### Memory Profiling

```python
from memory_profiler import profile


@profile
def memory_intensive():
    data = [i**2 for i in range(1_000_000)]
    return sum(data)
```

### Production Profiling with py-spy

```bash
py-spy record -o profile.svg -- python script.py
py-spy top --pid <PID>
```

### Optimization Patterns

```python
# Prefer comprehensions
squares = [x**2 for x in range(1000)]  # faster than loop

# Use generators for large datasets
total = sum(x**2 for x in range(1_000_000))  # no intermediate list

# Cache expensive computations
from functools import lru_cache


@lru_cache(maxsize=256)
def expensive_lookup(key: str) -> dict:
    return db.query(key)


# Use __slots__ for memory-intensive classes
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


# Batch I/O operations
def process_batch(items: Sequence[str]) -> Sequence[Result]:
    return db.bulk_query(items)  # 1 query, not N queries
```

### String Performance

```python
# Use join for string concatenation
result = "".join(parts)  # O(n), not O(n^2) with +=

# Use f-strings over format()
name = f"user_{user_id}"  # faster than "user_{}".format(user_id)
```

## Workflow

1. Identify the slow operation (user report, metrics, observation).
2. Profile with cProfile to find the hot function.
3. Use line_profiler on the hot function for line-level detail.
4. If memory is the concern, use memory_profiler instead.
5. Apply targeted optimization to the measured bottleneck.
6. Re-profile to confirm improvement and check for regressions.

## Examples

Good:

```python
from functools import lru_cache


@lru_cache(maxsize=128)
def parse_entry(raw: str) -> dict:
    return json.loads(raw)
```

Why good: caches repeated parsing of identical input — measured hot path.

Bad:

```python
result = ""
for item in large_list:
    result += str(item) + ","
```

Why bad: O(n^2) string concatenation — use `",".join(str(i) for i in large_list)`.

## Verification

```bash
python -c "import cProfile; print('cProfile available')"
rg -n "lru_cache|__slots__|\.join\(" --glob "**/*.py" flext-core/src/
```
