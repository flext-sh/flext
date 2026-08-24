---
name: flext-logging
description: >-
  Use the current FLEXT logging facade for bootstrap configuration, module
  loggers, and validated context propagation. Use when application code logs or
  binds context; do not use to define enforcement or structural codemods.
license: MIT
metadata:
  version: 2.0.0
---

# FLEXT Structured Logging

## Contract

Application and library consumers import the project facade `u`. `flext-core`
owns the implementation and logging protocols; direct `structlog` and concrete
`FlextLogger` access is reserved for the owning bridge implementation.

| Intent | Public operation |
| --- | --- |
| configure the runtime once at bootstrap | `u.configure_structlog(...)` |
| obtain a module logger | `u.fetch_logger(__name__)` |
| bind validated shared context | `u.bind_global_context(**context)` |
| remove shared context | `u.unbind_global_context(*keys)` |

Context operations return the canonical Result and must be composed or handled
as such.

## Workflow

1. Configure logging once in the application bootstrap, not in leaf modules.
2. Fetch a module logger through the local public `u` facade.
3. Bind only normalized domain context at ingress and unbind it at the matching
   lifecycle boundary.
4. Emit structured event names and typed key/value fields.
5. Preserve exceptions and correlation context when translating a failure.

## Non-Negotiables

- No `print`, direct `structlog.get_logger`, or direct `structlog.configure` in
  consumers.
- No logging setup in import-time leaf code.
- No formatted prose where structured event fields carry the data.
- No duplicate rule inventory in this skill. Static enforcement declarations
  and the codemod provider remain separate canonical owners.
- Tests and log snapshots validate declared behavior; they do not define the
  logging contract.

## Verification

Use a fresh public-facade import, the narrow lint/type gates, and a behavior
probe that observes the configured logger/context boundary. Record exact
evidence in the active root-workspace Bead.

## References

- [`coding-standards`](../coding-standards/SKILL.md)
- [`flext-enforcement-catalog`](../flext-enforcement-catalog/SKILL.md)
- [`flext-quality-gates`](../flext-quality-gates/SKILL.md)
