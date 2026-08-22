## Pydantic v2 Governance Summary

<!-- mro-wkii.17 (agent: codex) — document boundary-once models without duplicate transports. -->

### Canonical flow

```text
external input
→ flext-cli validates once into the owning m.* model
→ the same instance crosses p.* contracts and MRO services
→ r[p.Result]
→ flext-cli serializes once at the true external egress
```

Pydantic two-way is the pair of external boundaries. It is never an internal
dump-to-validate roundtrip.

### Model owner

- Declare each model only in the owning `_models` facet.
- Keep models field-only, frozen, strict, and `extra="forbid"` where applicable.
- Use immutable defaults and declarative field constraints.
- Do not add methods, validators, serializers, computed fields, private state,
  factories, getters, or setters.

### Protocol interface

- Expose each model shape through the owning `p.*` protocol.
- Annotate service/utility/api interfaces (params, returns) and collaborator/DI fields with `p.*` (or `t.*` scalars), imported at runtime — not concrete models, not under `TYPE_CHECKING` (ADR-011).
- Data/payload fields, including nested and composed (`list`/`dict` of models), are concrete `m.*` — a bare protocol cannot validate or serialize a data field.
- Use `m.*` to construct the canonical object at the boundary and pass the same instance through `p.*`.
- Pass the original instance through every internal call.

### Direct upstream reuse

When an upstream `m.*` model and `p.*` protocol already express the required
semantics, import and use those facade members directly. A local alias,
pass-through wrapper, name-only subclass, or shadow schema is a duplicate API.

### Config and settings SSOT

```text
from package import config, settings

project = config.Package.project
runtime = settings.Package.runtime
```

The namespaced singletons are already validated. Consumers never call a getter,
proxy, loader, slice validator, or settings accessor.

### Anti-patterns

- `cast()`, `Any`, or bare `object`.
- `dict`, `TypedDict`, dataclass, `NamedTuple`, `SimpleNamespace`, or JSON-shaped contracts.
- Internal `model_dump` to `model_validate` reconstruction.
- `model_copy` or TypeAdapter reconstruction used as transport.
- Duplicate DTO/model/protocol or local alias for an unchanged upstream contract.
- Custom model methods, validators, serializers, properties, or factories.
- A second loader, writer, renderer, facade, or compatibility execution branch.

### Facade-only imports

Consumer code imports project and upstream `c/t/p/m/u` members from package
roots. Pydantic models are declared only inside the owning model facet.
