---
name: coding-standards
description: 'Use this skill for FLEXT coding standards quick-reference: aliases, imports,
  typing, MRO, results, logging, testing, and local validation. Use when writing or
  reviewing Python code in the FLEXT monorepo. DO NOT USE FOR: questions unrelated to
  FLEXT coding standards or creating projects/architecture from scratch.'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Coding Standards

**UTILITY SKILL**

Quick-reference for daily coding in the FLEXT monorepo. When in doubt, prefer canonical sources: `AGENTS.md`, `pyproject.toml`, and the child skills listed below.

## USE FOR

- Writing or reviewing Python code in FLEXT projects.
- Choosing imports, aliases, types, result flow, logging, or test style.
- Running the narrowest local validation gate.

## DO NOT USE FOR

- Questions unrelated to FLEXT coding standards.
- Creating projects or architecture from scratch.

## Workflow

1. Check the relevant section below for the pattern.
2. Copy the **Good** example, avoid the **Bad** example.
3. Run the validation command for the touched file before claiming done.

## Critical rules

- Prefer canonical sources (`AGENTS.md`, child skills, `pyproject.toml`).
- Require evidence: `ruff check <file>` and `pyrefly check <file>` must pass.
- Do not add bypasses, shims, fallbacks, or suppression comments.

---

## 1. Required file header

Every Python file starts with these two imports.

```python
from __future__ import annotations
from collections.abc import Mapping, Sequence
```

**Why:** enables PEP 563 postponed annotations and makes collection types available for strict contracts without importing from `typing`.

**Validate:** `ruff check <file>` (`I002` enforces this).

---

## 2. Canonical aliases

Use the project facade aliases. Do not rename or shadow them.

| Alias | Meaning | Example |
|-------|---------|---------|
| `c` | constants / constants namespace | `c.SomeConstant` |
| `m` | models | `m.SomeModel` |
| `p` | protocols | `p.SomeProtocol` |
| `t` | typings / types | `t.JsonValue` |
| `u` | utilities | `u.some_utility` |
| `r` | result / returns | `r[SomeModel]` |
| `e` | errors / exceptions | `e.SomeError` |
| `s` | service / runtime | `s.fetch_global()` |
| `x` | mixins / execution | `x.SomeMixin` |
| `d` | decorators | `d.some_decorator` |
| `h` | handlers | `h.some_handler` |

Settings classes (`FlextSettings`, `FlextCliSettings`, etc.) have no short alias; import the class by name.

**Good:**

```python
from __future__ import annotations

from flext_core import c, r, t, u


def fetch() -> r[t.JsonValue]:
    return u.Result.ok({"user_id": 1})
```

**Bad:**

```python notest
# Illustrative anti-pattern: shadowing the canonical `m` alias with the long module name.
from flext_core import models


def fetch() -> models.User:  # shadowing, extra keystrokes
    ...
```

---

## 3. Imports

### Order

1. `from __future__ import annotations`
2. `from collections.abc import Mapping, Sequence`
3. stdlib
4. third-party
5. first-party (`flext_core.*`, `flext_*`)
6. local package

Use absolute imports only. No wildcards. No relative imports in `src/`.

**Good:**

```python
from __future__ import annotations
from collections.abc import Mapping, Sequence
from pathlib import Path

from pydantic import BaseModel

from flext_core import c, m, t, u
from flext_ldap import constants as ldap_constants
```

**Bad:**

```python notest
# Illustrative anti-patterns — these imports violate FLEXT import discipline.
from .utils import helper  # relative import
from flext_core import *  # wildcard
from typing import Dict, List  # legacy typing
```

**Validate:** `ruff check <file>` (`I001`, `I002`, `TID252`).

---

## 4. Typing

### Prefer mapping-family types for contracts

| Intent | Use | Avoid |
|--------|-----|-------|
| read-only contract | `Mapping[str, t.JsonValue]` | `dict[...]`, `typing.Dict` |
| mutating contract | `MutableMapping[str, t.JsonValue]` | `dict[...]` |
| schema payload | Pydantic `BaseModel` or `TypedDict` | bare `dict` |
| unknown JSON | `t.JsonValue` | `Any` |

**Good:**

```python
from __future__ import annotations

from collections.abc import Mapping
from flext_core import t


def normalize(data: Mapping[str, t.JsonValue]) -> t.JsonValue: ...
```

**Bad:**

```python notest
# Illustrative anti-pattern: legacy typing and bare Any.
from typing import Any, Dict


def normalize(data: Dict[str, Any]) -> Any: ...
```

### Narrowing

Use `isinstance` with `TypeGuard` or protocol checks. Avoid `type()`.

**Good:**

```python notest
# Illustrative narrowing pattern — value comes from caller context.
from collections.abc import Mapping

if isinstance(value, Mapping):
    ...
```

**Bad:**

```python notest
# Illustrative anti-pattern: use isinstance(value, Mapping) instead.
if type(value) is dict:
    ...
```

**Validate:** `pyrefly check <file>`, `ruff check <file>`.

---

## 5. Result flow

Fallible application paths return `r[T]`. Do not use raw exceptions or ad-hoc error dicts for control flow.

**Good:**

```python
from __future__ import annotations

from flext_core import r


def load_user(user_id: int) -> r[str]: ...


result = load_user(1)
# compose with .map / .bind / .alt from returns
```

**Bad:**

```python notest
# Illustrative anti-pattern: ad-hoc error dict instead of r[T].
def load_user(user_id: int) -> dict[str, object]:
    return {"ok": False, "error": "not found"}
```

---

## 6. Logging

Use `FlextLogger`. No `print()` in `src/`.

**Good:**

```python
from __future__ import annotations

from flext_core import u

user_id = 42
logger = u.fetch_logger(__name__)
logger.info("user.created", user_id=user_id)
```

**Bad:**

```python notest
# Illustrative anti-pattern: print() in library code.
print(f"created user {user_id}")
```

---

## 7. Error handling

Catch specific exceptions. No bare `except:`. No empty `except/pass`.

**Good:**

```python
from __future__ import annotations

raw = "not-an-int"
try:
    value = int(raw)
except ValueError as exc:
    raise ValueError("invalid integer") from exc
```

**Bad:**

```python notest
# Illustrative anti-pattern: bare except/pass swallows all errors.
try:
    value = int(raw)
except:
    pass
```

---

## 8. Models and settings

Use Pydantic v2 `BaseModel`. Validate dynamic payloads with `OptionsModel.model_validate(kwargs)`.

**Good:**

```python
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: int
    name: str
```

**Bad:**

```python notest
# Illustrative anti-pattern: use Pydantic BaseModel for schema payloads.
from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
```

---

## 9. Common anti-patterns

| Anti-pattern | Why it hurts | Fix |
|--------------|--------------|-----|
| `from typing import Any` | breaks strict typing | use `t.JsonValue` or a real type |
| `isinstance(x, dict)` | narrows too tightly | `isinstance(x, Mapping)` |
| `default_factory=dict` | hides schema intent | explicit factory or model |
| `sys.exit()` in library code | kills the caller | raise an exception |
| `breakpoint()` / `import pdb` | leaks debug code | remove before commit |
| `TODO/FIXME/HACK/XXX` | silent debt | resolve or track as bead |
| `# type: ignore` / `# noqa` | hides real problems | fix root cause |
| relative imports in `src/` | breaks package boundaries | absolute imports |
| wildcard imports | pollutes namespace | explicit imports |

---

## 10. Local validation workflow

After editing a file, run the gates in this order:

```bash
# 1. lint + format
ruff check <file>
ruff format <file>

# 2. type check
pyrefly check <file>

# 3. behavior gate (when applicable)
make test PROJECT=<proj> MATCH=<expr>
```

For multiple changed files, use the project baseline:

```bash
make check CHANGED_ONLY=1
```

---

## Cross-references

- `flext-import-rules` — import order, aliases, absolute imports, MRO matrix.
- `flext-strict-typing` — mapping-first typing, banning `Any`/`dict`/`typing.Dict`.
- `flext-patterns` — bare except, print, breakpoints, TODO, version strings.
- `flext-quality-gates` — exact commands and thresholds for `ruff`, `pyrefly`, `pytest`.
- `flext-development-workflow` — bootstrap, make targets, CI/CD lifecycle.
- `AGENTS.md` — root engineering law (R0–R15).

## Troubleshooting

- Unclear which alias to use → check the nearest facade `__init__.py` or ask.
- `ruff`/`pyrefly` disagree → prefer `pyrefly`; if blocked, escalate instead of suppressing.
- Need a new pattern → prove the canonical owner is missing before adding a helper.
