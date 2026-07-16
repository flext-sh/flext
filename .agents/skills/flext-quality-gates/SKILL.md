---
name: flext-quality-gates
description: >-
  Select and run the narrowest decisive FLEXT validation before widening to
  project or workspace gates. Use for lint, formatting, typing, tests, docs,
  provider catalogs, and interpreting gate failures.
license: MIT
metadata:
  version: 2.0.0
---
# FLEXT Quality Gates

Gate commands validate the owning source. They do not define behavior,
configuration, catalog membership, or project type.

## Selection

| Changed surface | First gate | Native widening gate |
| --- | --- | --- |
| Python source | `ruff check <path> --no-fix` then `pyrefly check <path>` | affected behavior test or project check |
| Python formatting | `ruff format --check <path>` | project format gate |
| Markdown or skill | `markdownlint-cli2 <path>` | `make docs DOCS_PHASE=audit` |
| Provider TOML | typed parse plus exact declared-path inventory | provider projection probe |
| Make or tooling | `make help` plus targeted verb | `make check` or `make val` |
| Structural codemod | provider preview and exact expected cardinality | apply, rescan, and idempotence |

## Workflow

1. Identify the declaration or config that owns the expected behavior.
2. Run the first gate for only the touched path.
3. If red, record exact evidence and fix the owner before widening.
4. Run the affected behavior or integration gate.
5. Run the project/workspace gate required by impact.
6. Record command, exit code, and decisive output in the active root-workspace
   Bead.

## Make Surface

```bash
make help
make check PROJECT=<project> CHECK_GATES=<gates>
make test PROJECT=<project> MATCH=<expression>
make docs DOCS_PHASE=<generate|fix|audit|build|validate>
make val VALIDATE_SCOPE=workspace
```

The root `Makefile`, shared make framework, and `pyproject.toml` own available
verbs and thresholds. Do not mirror their changing values in this skill.

## Non-Negotiables

- Use direct tools for narrow feedback and Make for canonical orchestration.
- Do not auto-fix before a read-only failure establishes the blast radius.
- Do not suppress, bypass, mock, or restore legacy content to obtain green.
- Do not claim success without command, exit code, and decisive output.

## References

- [`flext-development-workflow`](../flext-development-workflow/SKILL.md)
- [`docs/GOVERNANCE.md`](../../../docs/GOVERNANCE.md)
- [`ADR-004`](../../../docs/architecture/adr/004-generic-make-framework-in-flext-tests.md)
