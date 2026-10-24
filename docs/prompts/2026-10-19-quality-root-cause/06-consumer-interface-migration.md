# Migrate tests, scripts and examples to current public contracts

## Authority

Read [the current FLEXT session router](../../../.agents/commands/flext-law.md)
and [this task collection](README.md) before execution. This file supplies only
the task-specific owner, diagnosis and acceptance delta.

## Exclusive ownership

Own stale consumer calls and fixtures only, divided by member/file with the coordinator; source changes require evidence that the source contract itself is wrong.

## Sources to inspect

Begin with flext-core/tests/unit/test_utilities_type_guards_coverage_100.py, test_handler_discovery_module.py, test_logging_stages.py, test_registry.py and their current public owners; expand by actual native diagnostics.

## Required correction

Replace unnecessary raw asserts and literal comparisons introduced in place of valid tm calls. Preserve genuine negative runtime scenarios without statically invalid assignments or invented adapters. For guard results investigate the actual union/public contract before introducing narrowing. Use current typed fixtures and public c/t/p/m/u, direct canonical models and native interface signatures. Do not restore broad private-member-access or test complexity exceptions to preserve outdated tests.

## Acceptance evidence

Prove observable behavior and failure semantics through public boundaries; rerun member Ruff, Pyrefly, Pyright, Mypy and affected tests using native routes. No reduced test collection or renamed expectations solely to accept broken behavior.
