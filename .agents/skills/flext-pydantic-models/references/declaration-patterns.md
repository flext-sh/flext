## Pydantic v2 Patterns Summary

<!-- mro-wkii.17 (agent: codex) — prefer composition of source objects over local aliases and copies. -->

### Declaration-only model owner

```python
from __future__ import annotations

from typing import Annotated, ClassVar

from flext_core import m as m


class ProjectModels(m):
    class Request(m.FrozenModel):
        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            strict=True,
            frozen=True,
            extra="forbid",
        )

        identifier: Annotated[str, m.Field(min_length=1)]

    class ScopedRequest(m.FrozenModel):
        model_config: ClassVar[t.ConfigDict] = m.ConfigDict(
            strict=True,
            frozen=True,
            extra="forbid",
        )

        source: Request
        project_scope: Annotated[str, m.Field(min_length=1)]


m = ProjectModels
```

`ScopedRequest.source` retains the exact `Request` instance. The additional
field is a documented domain delta; no source fields are flattened or copied.

### Canonical source reuse

Use the upstream model and protocol members directly when semantics are
unchanged. Do not create `type` aliases, forwarding protocols, wrapper models,
or package-local facade names for them. Compose a new model only when the local
domain adds a real field, invariant, capability, or semantic change.

### Protocol interface for the composed model

```python
from __future__ import annotations

from typing import Protocol

from flext_core import p as p


class ProjectProtocols(p):
    class Source(Protocol):
        @property
        def identifier(self) -> str: ...

    class ScopedRequest(Protocol):
        @property
        def source(self) -> ProjectProtocols.Source: ...

        @property
        def project_scope(self) -> str: ...


p = ProjectProtocols
```

Service signatures use `p.ScopedRequest`; the runtime value remains the
canonical model instance.

### Discriminated declarations

Use a field-only discriminated union only when alternatives have distinct
domain semantics. The discriminator is declared with `Field(discriminator=...)`;
consumers retain the selected model instance.

### General principles

- Keep every model field-only and immutable.
- Put behavior and derivation in `u` or a service composed by MRO.
- Prefer declarative constraints; custom validators are not part of the strict model path.
- Validate once at ingress and retain object identity internally.
- Reuse upstream `m.*` and `p.*` members directly.
- Declare a new model only for a documented domain field, invariant, capability, or semantic change.
- Remove parallel loaders, renderers, writers, convenience APIs, and compatibility branches.
