---
name: flext-patterns
description: 'Use for architecture-sensitive FLEXT implementation or refactoring that combines facades, MRO composition, ports and adapters, typed results, dependency injection, CLI routing, and package-wide cutovers.'
license: MIT
metadata:
  version: 2.0.0
---
# FLEXT Architecture Patterns

## Architecture decision

1. Locate the responsibility in the ecosystem ownership map.
2. Identify the public contract (`p`, `t`, or `m`) and the current implementation.
3. Confirm allowed dependency direction and all direct consumers.
4. Extend the canonical owner; do not add a local wrapper or parallel abstraction.
5. Cut over exports, callers, tests, examples, and documentation atomically.

## Facades and namespaces

A public facade is a navigation surface, not an implementation container:

```python
from __future__ import annotations

from flext_core import FlextModels


class ModelsDomain:
    class Request(FlextModels.Base):
        value: str


class m(ModelsDomain, FlextModels):
    """Public model facade."""
```

Keep nested domains cohesive, MRO order intentional, and public names collision-free.
Do not duplicate a nested namespace in sibling mixins or import private implementation
modules from another package.

## Ports, adapters, and services

- Protocols describe behavior required by the application layer.
- Services orchestrate typed domain behavior and return `r[T]`.
- Adapters implement protocols for databases, LDAP, Oracle, gRPC, files, or networks.
- Containers bind implementations at the composition root.
- Domain code never imports an adapter or creates a concrete infrastructure client.

Use constructor injection for required collaborators. Do not hide dependency lookup
inside methods or create module-level clients.

## Result flow

```python
result = service.load(request).bind(transform).bind(adapter.write)
return result.alt(lambda error: error.with_context(operation="sync"))
```

Keep success and failure types explicit. Map external exceptions once at the adapter
boundary, attach actionable context, and never use unwrap/exception fallback as normal
control flow.

## Model-driven boundaries

Use Pydantic models for commands, events, queries, settings, and dynamic option
payloads. Validation occurs at entry; internal services receive typed values. Prefer
protocols or definition-time type relationships over late `model_rebuild()` calls.

## CLI pattern

A package CLI declares typed route models, derives parameters through `flext-cli`,
invokes an application service, renders through the shared output abstraction, and
returns a stable integer exit code. It does not own business rules or instantiate
infrastructure directly.

## Refactoring protocol

- Build a definition/caller/export census before moving a symbol.
- Use Rope-backed or equivalent structural refactoring for Python moves and renames.
- Keep batches importable; update required consumers in the same batch.
- Delete the obsolete owner after cutover and prove no live reference remains.
- Regenerate managed projections twice and require an empty second diff.
- Prefer net-negative LOC unless the task adds an accepted capability.

## Validation

Run import smoke, Ruff, Pyrefly, Pyright, Mypy, scoped tests, and direct-consumer
checks. Then use the changed-scope Make gate. Public architecture changes also require
boundary and documentation validation.

## Related skills

- [`flext-ecosystem-patterns`](../flext-ecosystem-patterns/SKILL.md)
- [`flext-architecture-layers`](../flext-architecture-layers/SKILL.md)
- [`flext-mro-namespace-rules`](../flext-mro-namespace-rules/SKILL.md)
- [`flext-refactoring-workflow`](../flext-refactoring-workflow/SKILL.md)
- [`flext-cli-ssot-enforcement`](../flext-cli-ssot-enforcement/SKILL.md)
- [`flext-strict-typing`](../flext-strict-typing/SKILL.md)
