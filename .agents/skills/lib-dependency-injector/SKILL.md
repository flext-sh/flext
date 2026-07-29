---
name: lib-dependency-injector
description: 'Dependency-injector bridge patterns for FLEXT runtime and container internals. Use when adding DI wiring, provider registration, or scoped test containers.'
license: MIT
metadata:
  version: 1.0.0
---
# Dependency Injector Bridge

## Workflow

1. Inspect `runtime.py` and `container.py` signatures before editing behavior.
2. Keep direct framework calls in `DependencyIntegration` and `FlextContainer` only.
3. If adding provider types, mirror updates in `p.Container` protocol signatures.

## Contracts

- Direct dependency_injector imports are banned outside flext-core bridge files.
