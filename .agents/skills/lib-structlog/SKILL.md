---
name: lib-structlog
description: 'Use this skill to flextLogger structured logging with context propagation,
  DI factories, and result adapters. Use when adding logging, binding context, or
  configuring structlog processors. DO NOT USE FOR: questions unrelated to lib-structlog
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Lib Structlog — FlextLogger and Context-Aware Logging

**UTILITY SKILL**

## USE FOR

- Requests about lib structlog.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to lib-structlog.
- creating projects or architecture from scratch.

## Workflow

1. Call `u.configure_structlog()` in your application bootstrap
2. Create loggers via `FlextLogger.create_module_logger(__name__)`
3. Bind request/operation context via `FlextLogger.Context.bind_global_context()`

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
