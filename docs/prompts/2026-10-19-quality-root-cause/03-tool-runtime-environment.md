# Repair analyzer environment ownership

## Authority

Read [the current FLEXT session router](../../../.agents/commands/flext-law.md)
and [this task collection](README.md) before execution. This file supplies only
the task-specific owner, diagnosis and acceptance delta.

## Exclusive ownership

Own typed ToolingContextRequest environment input and environment projection; coordinate shared templates with prompts 01/04.

## Sources to inspect

flext-infra/src/flext_infra/_models/deps.py; codegen/_conform/existing_plan.py; scaffold_plan.py; deps/_modernizer/tooling.py; deps/phases/ensure_pyright.py; tests/unit/deps/test_modernizer_pyright.py and test_modernizer_pyrefly.py; docs/guides/execution-context.md.

## Required correction

Adopt the existing unvalidated environment_dir changes. Resolve attached members through the canonical workspace runtime owner; standalone/future scaffold roots use their own declared runtime. Emit paths relative to the project. Analyzer path phases must not independently overwrite the environment binding. No nested fake venv, symlink workaround, borrowed environment, command-line override or fixed absolute path.

## Acceptance evidence

Prove attached, standalone and planned scaffold cases through native tests; regenerate the core projection and rerun native Pyright. Historical report had zero diagnostics but a missing member .venv stderr warning, so its gate was RED. Require no warning and correct runtime provenance.
