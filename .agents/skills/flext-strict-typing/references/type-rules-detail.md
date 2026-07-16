## Typing Rules Summary

### Core requirements

- Python 3.13+.
- `from __future__ import annotations` in every file.
- Use `collections.abc` (Mapping, Sequence, Callable, Iterable) instead of `typing` generics.
- Keep concrete types (`list`, `dict`, `set`, `tuple`) unless an abstraction is required.

### Mapping-first policy

- Prefer `Mapping[str, T]` for read-only mappings.
- Use `dict[str, T]` only for mutable/owned structures.
- `Sequence[T]` for read-only lists; `tuple[T, ...]` for fixed-size.

### Rule 1: Zero `Any` / bare `object`

Use the `FlextTypes` hierarchy:

- `t.Scalar`, `t.JsonValue`, `t.JsonObject`, `t.JsonArray`
- `t.NestedDict`, `t.PathLike`, `t.AutoStr`
- Container types: `t.ListOf[T]`, `t.DictOf[K,V]`, `t.SetOf[T]`
- `t.Result`, `t.ResultT[T]`

### Rule 2: PEP 695 type aliases

```python
from __future__ import annotations

from collections.abc import Mapping

from flext_core import p, t

type UserIds = list[t.AutoStr]
type ConfigMap = Mapping[str, t.JsonValue]
```

Runtime narrowing uses `u.is_*` helpers (e.g., `u.is_str_list`).

### Rule 3: TypeVars at module level only

```python
from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
```

### Rule 4: Modern Python typing

- `X | Y` instead of `Union[X, Y]`.
- `X | None` instead of `Optional[X]` (inline only; default `""` ⇒ use `str`).
- `tuple[X, Y]` instead of `Tuple[X, Y]`.
- `typing.Self` for fluent return types.

### Rule 5: Pydantic v2 models

- Use `ConfigDict` (not inner `class Config`).
- Use `@u.field_validator` and `@u.model_validator` decorators.
- Declare fields with `u.Field(...)`.
- Avoid plain helper classes — prefer models.

### Rule 6: Annotated validation

```python
from __future__ import annotations

from typing import Annotated

from pydantic import Field

name = Annotated[str, Field(min_length=1)]
```

### Rule 7: protocols.py

- Define structural contracts in `protocols.py`.
- Import protocols via `from flext_core import p`.
- Use `isinstance` / `TypeIs` narrowing, never `type()`.

### Rule 8: Enums

Use `StrEnum` only; no bare `Enum` with string values.

### Rule 9: Constants

Use `Final` and immutable collections (`frozenset`, `tuple`, `MappingProxyType`).

### Rule 10: Explicit return types

Every function/method must declare its return type.

### Rule 11: Callable typing

Use `collections.abc.Callable[[In], Out]`.

### Rule 12: Result flow (`r`)

- `r[T]` is the sole fallibility mechanism.
- Import via `from flext_core import r`.
- Never use bare `try/except` for control flow.

### Rule 13: Fixes

- Move narrowing into `u.is_*` helpers.
- Use protocols to decouple cycles.
- Add typed tests before changing behavior.

### Ruff rules

- `ANN001`, `ANN201`, `ANN202` — explicit annotations
- `UP` — pyupgrade modern syntax
- `FA` — `from __future__ import annotations`
