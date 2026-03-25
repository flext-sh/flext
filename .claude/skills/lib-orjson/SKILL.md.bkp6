<!-- TOC START -->

- [Scope](#scope)
  - [Subproject Usage Map](#subproject-usage-map)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---

name: lib-orjson
description: Deterministic high-performance JSON serialization with orjson in flext_core utilities. Trigger when editing sort keys, cache normalization, or JSON boundary conversion logic.

---

## Scope

- Direct runtime usage: `flext-core/src/flext_core/_utilities/validation.py`
- Dependency declaration: `flext-core/pyproject.toml`
- Workspace-level package dependency context: `pyproject.toml`

### Subproject Usage Map

- `flext-core`: only direct Python call-site (`import orjson`, `orjson.dumps(...)`).
- `flext-api` and root packaging: declare `orjson` dependency, but do not directly import it in source from current evidence.
- Other `flext-*` packages: rely on higher-level serialization helpers, not direct `orjson` calls.

## References

- `flext-core/src/flext_core/_utilities/validation.py`: `FlextUtilitiesValidation.sort_key`
- `flext-core/pyproject.toml`: `orjson (>=3.11.3)`
- `pyproject.toml`: workspace dependency metadata where applicable
- `https://github.com/ijl/orjson`

## Rules

- Treat `orjson.dumps(...)` return type as `bytes` and decode explicitly before returning/ordering.
- Always keep deterministic ordering: pass `option=orjson.OPT_SORT_KEYS`.
- Preserve fallback path to stdlib JSON for unsupported types or serialization failures.
- Catch and handle serialization boundary errors where utility currently protects callers.
- Keep encoded string format consistent with `c.Utilities.DEFAULT_ENCODING`.
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, `cast()`, and `inline imports`. Wait for definition time or use Protocol decoupling.
## Instructions

- Anchor changes to the real declaration:

```python
# flext-core/src/flext_core/_utilities/validation.py

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

@staticmethod
def sort_key(value: t.GeneralValueType) -> tuple[str, str]:
    ...
    try:
        json_bytes = orjson.dumps(value, option=orjson.OPT_SORT_KEYS)
        serialized = json_bytes.decode(c.Utilities.DEFAULT_ENCODING)
    except (AttributeError, TypeError, ValueError, RuntimeError, KeyError):
        serialized = json.dumps(value, sort_keys=True, default=str)
    return (type_cat, serialized)
```

- Import pattern to preserve:
  - `import json`
  - `import orjson`
- If adding call-sites, enforce bytes->str decoding at the same boundary where `dumps` is called.
- If behavior changes, document deterministic ordering impact for cache keys and stable comparisons.

## Workflow

1. Locate existing `orjson` imports and calls in the target module.
2. Confirm deterministic options (`OPT_SORT_KEYS`) remain present.
3. Confirm decoded text output remains `str` for tuple sorting and key comparison.
4. Keep failure fallback to `json.dumps(..., sort_keys=True, default=str)`.
5. Verify no raw `bytes` leak into callers expecting text.

## Examples

Good:

```python
json_bytes = orjson.dumps(value, option=orjson.OPT_SORT_KEYS)
serialized = json_bytes.decode(c.Utilities.DEFAULT_ENCODING)
return (type_cat, serialized)
```

Why good: keeps deterministic key ordering and converts bytes to text at boundary.

Bad:

```python
serialized = orjson.dumps(value)
return (type_cat, serialized)
```

Why bad: returns bytes in a tuple expected to contain `str`, and drops explicit sorted-key determinism.

Good:

```python
try:
    json_bytes = orjson.dumps(value, option=orjson.OPT_SORT_KEYS)
    serialized = json_bytes.decode(c.Utilities.DEFAULT_ENCODING)
except (AttributeError, TypeError, ValueError, RuntimeError, KeyError):
    serialized = json.dumps(value, sort_keys=True, default=str)
```

Why good: preserves robustness for non-serializable values and deterministic ordering under fallback.

Bad:

```python
serialized = orjson.dumps(value).decode("utf-16")
```

Why bad: hardcoded wrong encoding breaks compatibility with project default encoding and can corrupt output.

## Verification

Make gates:

- `make check PROJECT=flext-core` — lint + type gates
- `make test PROJECT=flext-core` — verify serialization behavior

Pattern checks:

- `rg -n "import orjson|orjson\.dumps|OPT_SORT_KEYS|decode\(c\.Utilities\.DEFAULT_ENCODING\)|json\.dumps\(value, sort_keys=True, default=str\)" flext-core/src/flext_core/_utilities/validation.py`
- `rg -n "orjson \(>=3\.11\.3\)|orjson" flext-core/pyproject.toml pyproject.toml`
- `rg -n "import orjson" --glob "**/*.py"`
