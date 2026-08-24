---
name: flext-async
description: 'Use this skill to python asyncio patterns for FLEXT integrations — LDAP,
  Oracle, gRPC async operations. Use when building async pipelines, concurrent integrations,
  or I/O-bound FLEXT operations. DO NOT USE FOR: questions unrelated to async-python-patterns
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---

# Async Python Patterns

**UTILITY SKILL**

## Rules

- Always combine async operations with `r` for error handling.
- Use `asyncio.gather()` for concurrent I/O — never sequential awaits for independent operations.
- Use `asyncio.Semaphore` for rate-limiting external API calls.
- Use `async with` context managers for resource cleanup (connections, sessions).
- Never use `asyncio.run()` inside an already-running event loop — use `await` directly.

## Instructions

### Basic Async with r

### Concurrent Execution with gather

### Rate-Limited API Calls

### Async Context Manager

### Producer-Consumer with Queue

### Timeout Handling

## Workflow

1. Identify I/O-bound operations suitable for async (network, disk, DB).
2. Wrap each async operation in a `r`-returning coroutine.
3. Use `asyncio.gather()` for concurrent independent operations.

## Examples

Good:

Why good: concurrent execution of independent I/O operations.

Bad:

Why bad: sequential awaits waste time — each call waits for the previous one to finish.

## Verification

## USE FOR

- Requests about async python patterns.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to async-python-patterns.
- creating projects or architecture from scratch.

## Critical rules

- Prefer canonical sources.
- Require evidence before claiming success.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
- Missing context → state assumptions.
