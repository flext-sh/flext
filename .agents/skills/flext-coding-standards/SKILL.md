---
name: flext-coding-standards
description: >-
  Route daily FLEXT Python implementation decisions to the canonical facade,
  typing, result, configuration, testing, and validation owners. Use for code
  changes and reviews; load a focused child skill for detailed procedure.
license: MIT
metadata:
  version: 2.0.0
---

# FLEXT Coding Standards

This is a compact decision index, not a second architecture specification.

## Canonical Owners

| Concern | Read first |
| --- | --- |
| Layering and facade ownership | `flext-architecture-layers` |
| Imports and public aliases | `flext-import-rules` |
| Strict types and protocols | `flext-strict-typing` |
| Result composition | `lib-returns` |
| Pydantic boundary models | `lib-pydantic-v2` |
| Settings | `lib-pydantic-settings` |
| Testing | `using-flext-tests` |
| Gates | `flext-quality-gates` |

## Daily Invariants

- Use Python 3.13 syntax and absolute imports from the package's public facade.
- Public responsibilities compose through canonical `c/t/p/m/u` facades and
  operational aliases owned by the package; do not create flat compatibility
  aliases or deep-import private parts from consumers.
- Declaration facets contain declarations. Behavior belongs in utilities,
  services, API, CLI, base, or approved adapters.
- Validate an owned payload once at its external boundary into the canonical
  Pydantic model and pass that same object through protocol contracts. Do not
  substitute a raw mapping, `TypedDict`, dataclass, or dump/revalidate copy for
  an owned domain model. Mapping types remain valid for genuinely open or
  foreign data when the owning protocol declares them.
- Read configuration and settings only through their direct validated
  namespaced singletons. Do not re-read environment/files in consumers.
- Fallible paths return the canonical Result. Load `lib-returns` for the current
  operation surface; do not add aliases from another Result library.
- Structured logging owns runtime output; library code does not print or hide
  exceptions.
- Tests exercise public behavior with canonical fixtures. They validate the
  contract but never define it.

## Change Workflow

1. Identify the owning declaration/config and affected consumers.
2. Load only the focused skills needed for the touched responsibility.
3. Make the smallest root-cause change and remove the replaced path.
4. Update or verify affected docs, skills, agents, and provider entries.
5. Run the narrowest gates from `flext-quality-gates`, then the native project
   gate.
6. Record exact evidence in the active root-workspace Bead.

## Evidence

```bash
ruff check <path> --no-fix
ruff format --check <path>
pyrefly check <path>
make test PROJECT=<project> MATCH=<expression>
```

Do not add a helper, abstraction, suppression, or alternate path merely to make
a validator pass. Fix the canonical owner.

## References

- [`docs/GOVERNANCE.md`](../../../docs/GOVERNANCE.md)
- [`flext-quality-gates`](../flext-quality-gates/SKILL.md)
- [`flext-context-routing`](../flext-context-routing/SKILL.md)
