---
name: flext-patterns
description: 'Repository-native implementation patterns for result flow, DI, logging,
  and typed boundaries. Use when selecting or standardizing implementation style. DO
  NOT USE FOR: questions unrelated to flext-patterns creating projects or architecture
  from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Flext Patterns

**UTILITY SKILL**

Repository-native implementation patterns for result flow, DI, logging, and typed boundaries.

## USE FOR

- Selecting or standardizing implementation style.
- Avoiding anti-patterns: bare except, raw dict envelopes, direct external DI imports.

## DO NOT USE FOR

- Questions unrelated to FLEXT patterns.
- Creating projects or architecture from scratch.

## Workflow

1. Find the closest existing pattern for the target behavior.
2. Reuse the pattern with minimal adaptation.
3. Verify no anti-patterns.

## Critical rules

- No bare `except:`.
- No `print()` in `src/`; use `FlextLogger`.
- No `breakpoint()` / `import pdb` / `pdb.set_trace()` in committed code.
- No `TODO/FIXME/HACK/XXX` comments; resolve or track as a bead.
- No hardcoded `__version__` strings; use `importlib.metadata`.
- No `sys.exit()` in library code.
- No raw dict envelopes for errors; use `r[T]`.

## Good examples

### Error handling

```python
try:
    value = int(raw)
except ValueError as exc:
    raise e.ValidationError("invalid integer") from exc
```

### Logging

```python
from flext_core import u

logger = u.get_logger(__name__)
logger.info("user.created", user_id=user_id)
```

### Result flow

```python
from flext_core import r

def load(user_id: int) -> r[m.User]:
    ...
```

## Bad examples

```python
try:
    ...
except:
    pass
```

```python
print("debug")
```

```python
import pdb; pdb.set_trace()
```

```python
def load(user_id: int) -> dict[str, object]:
    return {"ok": False, "error": "not found"}
```

## Validation

```bash
ruff check <file>
pyrefly check <file>
```

## References

- `.agents/skills/coding-standards/SKILL.md` — general coding standards quick-reference
- `.agents/skills/flext-import-rules/SKILL.md` — import boundaries
- `.agents/skills/flext-strict-typing/SKILL.md` — typed boundaries
