---
name: lib-structlog
description: 'FLEXT logger structured logging with context propagation, DI factories, and result adapters. Use when adding logging, binding context, or configuring structlog processors.'
license: MIT
metadata:
  version: 1.0.0
---
# Lib Structlog — FlextLogger and Context-Aware Logging

## Workflow

1. Call `u.configure_structlog()` in your application bootstrap
2. Create loggers via `FlextLogger.create_module_logger(__name__)`
3. Bind request/operation context via `FlextLogger.Context.bind_global_context()`

## Enforced contracts

- Direct structlog.get_logger usage is banned outside FlextLogger/u bridge files.
- Avoid print statements in Python sources; use structured logging.

## Resources

- [`rules/ban-print-in-src.yml`](rules/ban-print-in-src.yml)
- [`rules/direct-get-logger.yml`](rules/direct-get-logger.yml)
