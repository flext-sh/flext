---
name: flext-dependency-injection
description: 'Use this skill to dependency_injector bridge patterns for FLEXT runtime
  and container internals. Use when adding DI wiring, provider registration, or scoped
  test containers. DO NOT USE FOR: questions unrelated to lib-dependency-injector
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Skill

**UTILITY SKILL**

## USE FOR

- Requests about lib dependency injector.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to lib-dependency-injector.
- creating projects or architecture from scratch.

## Workflow

1. Inspect `runtime.py` and `container.py` signatures before editing behavior.
2. Keep direct framework calls in `DependencyIntegration` and `FlextContainer` only.
3. If adding provider types, mirror updates in `p.Container` protocol signatures.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
