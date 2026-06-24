## Pydantic v2 Patterns Summary

### Reusable `Annotated` aliases

```python
from typing import Annotated
from pydantic import Field, BeforeValidator

NonEmptyStr = Annotated[
    str, BeforeValidator(lambda v: v.strip() or None), Field(min_length=1)
]
```

### Field validators

```python
@u.field_validator("email", mode="before")
@classmethod
def _normalize_email(cls, v):
    return str(v).strip().lower()
```

### Cross-field model validator

```python
@u.model_validator(mode="after")
def _check_dates(self):
    if self.end < self.start:
        raise ValueError("end must be >= start")
    return self
```

### Computed fields

```python
@u.computed_field
@property
def display_name(self) -> str:
    return f"{self.first} {self.last}"
```

### Discriminated unions

```python
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
@u.field_serializer("created_at", mode="plain")
def _serialize_dt(self, dt: datetime) -> str:
    return dt.isoformat()
```

### Strict + frozen boundaries

```python
class Boundary(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True)
```

### TypeAdapter

```python
adapter = TypeAdapter(list[MyModel])
items = adapter.validate_python(raw)
json_out = adapter.dump_json(items)
```

Cache adapters at module level when reused.

### RootModel

```python
class Tags(RootModel[list[str]]):
    pass
```

### PrivateAttr

```python
class Service(BaseModel):
    _cache: dict[str, Any] = PrivateAttr(default_factory=dict)
```

### General principles

- Prefer validators over manual coercion.
- Use `model_copy(update=...)` for immutable updates.
- Validate `**kwargs` with `Model.model_validate(kwargs)`.
- Keep boundary models strict; internal models permissive.
