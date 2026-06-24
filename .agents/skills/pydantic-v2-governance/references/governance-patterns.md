:## Pydantic v2 Governance Summary

### Use `Annotated` for reusable field constraints

```python
from typing import Annotated
from pydantic import Field

NonEmptyStr = Annotated[str, Field(min_length=1)]
```

### Mutable defaults via `default_factory`

```python
class Config(BaseModel):
    tags: list[str] = Field(default_factory=list)
```

### Cache TypeAdapters

```python
from functools import lru_cache
from pydantic import TypeAdapter


@lru_cache
def _ids_adapter() -> TypeAdapter[list[int]]:
    return TypeAdapter(list[int])
```

### Protocol vs ABC

- Use `Protocol` for structural typing in `protocols.py`.
- Use `ABC` only for shared implementation base classes.

### `issubclass()` safety

Always guard with `isinstance(x, type) and issubclass(x, BaseModel)`.

### ConfigDict defaults

```python
class MyModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        frozen=False,
        extra="forbid",
        validate_assignment=True,
    )
```

### Validation boundaries

- Public entrypoints: `Model.model_validate(data)` or `Model.model_validate_json(json_bytes)`.
- Internal payloads: cached `TypeAdapter[T].validate_python(data)`.
- Never call `Model(**data)` directly.

### Anti-patterns

- `cast()` — forbidden.
- `Any` / bare `object` — forbidden.
- `t.JsonValue` as model field — forbidden; use typed models.
- `type()` for narrowing — forbidden; use `isinstance` / `TypeIs`.
- Double `Field()` assignment — forbidden.
- `Model(data)` with dict — forbidden; use `model_validate`.

### Facade-only imports

Consumers import Pydantic abstractions through `flext_core` (`u.BaseModel`, `u.Field`, `u.ConfigDict`). No direct `from pydantic import ...` in consumer projects.
