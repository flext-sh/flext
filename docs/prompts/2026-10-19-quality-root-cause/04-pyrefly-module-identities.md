# Repair Pyrefly source-root identity

## Authority

Read [the current FLEXT session router](../../../.agents/commands/flext-law.md)
and [this task collection](README.md) before execution. This file supplies only
the task-specific owner, diagnosis and acceptance delta.

## Exclusive ownership

Own Pyrefly search-path derivation and relevant tests; preserve analysis coverage.

## Sources to inspect

flext-infra/src/flext_infra/deps/extra_paths.py; config/tooling.yaml path rules; modernizer Pyrefly tests and projection owner.

## Required correction

Investigate pyrefly_search_paths adding _included_pyrefly_env_dirs even though project-shared-search-paths is empty and policy explains that scripts.* has one package identity. Analysis inclusion and import search roots are different concepts. Repair their conflation using typed existing owners. Never exclude tests/examples/scripts to remove duplicate identities or missing imports.

## Acceptance evidence

Exercise real public package imports and native Pyrefly after regeneration. Verify all intended trees remain analyzed and package identities remain qualified. Historical full check reported 18 generated-initializer missing imports; recalculate current findings.
