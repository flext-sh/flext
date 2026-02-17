---
name: rules-flext-core
description: Concrete implementation rules for result flow, typing, DI, and logging in flext-core.
scope: /home/marlonsc/flext/flext-core/
tags: [rules,flext-core,architecture,typing]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/flext-core/`

## Sources

- `/home/marlonsc/flext/flext-core/src/flext_core/result.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/typings.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/runtime.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/container.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/loggings.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/protocols.py`
- `/home/marlonsc/flext/flext-core/docs/architecture/overview.md`
- `/home/marlonsc/flext/flext-core/docs/architecture/patterns.md`
- `/home/marlonsc/flext/flext-core/pyproject.toml`

## Enforced Rules

- Enforced by: result flow uses `FlextResult` and recovery via `.lash` (not ad-hoc exception swallowing).
- Enforced by: map-like public payloads use typed containers from `typings.py` (`ConfigMap`, `ServiceMap`, `ErrorMap`).
- Enforced by: DI wiring goes through `FlextRuntime` bridge + `FlextContainer`, not direct framework leakage into handlers.
- Enforced by: structured logging goes through `FlextRuntime.configure_structlog` and `FlextLogger` context helpers.

## Guidance

- Prefer `r[T].ok(...)` / `r[T].fail(...)` at module boundaries where operations can fail.
- Use `t.*` aliases from `typings.py` instead of redefining local type aliases for shared concepts.
- Use protocol contracts in `protocols.py` when a boundary should be structurally typed.
- Keep external library access behind runtime/container/logging wrappers already present in flext-core.

## Examples

- Result recovery: `result.lash(handler)` pattern in `flext-core/src/flext_core/result.py`.
- DI bridge: `dependency_containers()` / `dependency_providers()` in `flext-core/src/flext_core/runtime.py` and usage in `container.py`.
- Logger context: `bind_global_context` and context operations in `flext-core/src/flext_core/loggings.py`.

## Verification

- `rg -n "\.lash\(" flext-core/src/flext_core/result.py`
- `rg -n "class ConfigMap|class ServiceMap|class ErrorMap" flext-core/src/flext_core/typings.py`
- `rg -n "dependency_containers|dependency_providers|FlextContainer" flext-core/src/flext_core/runtime.py flext-core/src/flext_core/container.py`
- `rg -n "configure_structlog|bind_global_context" flext-core/src/flext_core/runtime.py flext-core/src/flext_core/loggings.py`
