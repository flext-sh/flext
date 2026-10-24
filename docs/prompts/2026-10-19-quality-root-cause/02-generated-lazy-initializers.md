# Repair generated lazy exports and absolute imports

## Authority

Read [the current FLEXT session router](../../../.agents/commands/flext-law.md)
and [this task collection](README.md) before execution. This file supplies only
the task-specific owner, diagnosis and acceptance delta.

## Exclusive ownership

Own codegen initializer rendering/templates and lazy-bootstrap behavior; coordinate pyproject policy edits with prompt 01.

## Sources to inspect

flext-infra/src/flext_infra/codegen/_codegen_generation_standard.py; _codegen_generation_type_checking.py; _codegen_generation_paths.py; templates/lazy_init_root.py.j2; flext-core/src/flext_core/lazy.py and its implementation.

## Required correction

Require absolute TYPE_CHECKING imports. Keep bootstrap imports from flext_core.lazy, avoiding re-entry through the flext_core facade. Inspect install_lazy_exports: it already installs __getattr__/__dir__ and returns hooks; validate direct invocation versus redundant __getattr__ assignment from real behavior. Some producer corrections are already present; adopt them and complete validation. Runtime lazy-map relative module strings have a distinct contract: do not mechanically rewrite them because static imports are absolute.

## Acceptance evidence

Generate through Make, validate fresh public imports and lazy hook identity, run public lazy behavior tests through the native test route, and prove generator/formatter/autofix idempotence. Previous check had 431 TID252 initializer findings; that count is historical, not a target to suppress.
