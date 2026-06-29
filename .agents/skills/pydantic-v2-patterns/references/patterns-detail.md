## Pydantic v2 Patterns Summary

### Reusable `Annotated` aliases

```python
from __future__ import annotations

from typing import Annotated
from pydantic import BeforeValidator, Field

NonEmptyStr = Annotated[
    str, BeforeValidator(lambda v: v.strip() or None), Field(min_length=1)
]
```

### Field validators

```python
from __future__ import annotations

from flext_core import t, u


@u.field_validator("email", mode="before")
@classmethod
def _normalize_email(cls, v: t.JsonValue) -> str:
    return str(v).strip().lower()
```

### Cross-field model validator

```python
from __future__ import annotations

from flext_core import u


@u.model_validator(mode="after")
def _check_dates(self):
    if self.end < self.start:
        raise ValueError("end must be >= start")
    return self
```

### Computed fields

```python
from __future__ import annotations

from flext_core import u


@u.computed_field
@property
def display_name(self) -> str:
    return f"{self.first} {self.last}"
```

### Discriminated unions

```python
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Cat(BaseModel):
    kind: Literal["cat"]
    meows: int


class Dog(BaseModel):
    kind: Literal["dog"]
    barks: int


Pet = Cat | Dog
```

Use `Discriminator("kind")` for open unions.

### Serializers

```python
from __future__ import annotations

from datetime import datetime

from flext_core import u


@u.field_serializer("created_at", mode="plain")
def _serialize_dt(self, dt: datetime) -> str:
    return dt.isoformat()
```

### Strict + frozen boundaries

```python
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Boundary(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)
```

### TypeAdapter

```python
from __future__ import annotations

from pydantic import BaseModel, TypeAdapter


class MyModel(BaseModel):
    id: int


raw = [{"id": 1}]
adapter = TypeAdapter(list[MyModel])
items = adapter.validate_python(raw)
json_out = adapter.dump_json(items)
```

Cache adapters at module level when reused.

### RootModel

```python
from __future__ import annotations

from pydantic import RootModel


class Tags(RootModel[list[str]]):
    pass
```

### PrivateAttr

```python notest
# Illustrative pattern — private cache attribute on a Pydantic model.
class Service(BaseModel):
    _cache: dict[str, Any] = PrivateAttr(default_factory=dict)
```

### General principles

- Prefer validators over manual coercion.
- Use `model_copy(update=...)` for immutable updates.
- Validate `**kwargs` with `Model.model_validate(kwargs)`.
- Keep boundary models strict; internal models permissive.
