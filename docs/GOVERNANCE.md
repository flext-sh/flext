# FLEXT Governance Router

## Purpose

This file is the root governance router for the FLEXT workspace. It does not
duplicate the engineering law. It points each change type to the living source
that owns the rule, validation surface, and escalation path.

When this file conflicts with a lower-level guide, this file only decides which
source to read first. The owning source still provides the actual rule.

## Authority Order

1. Current operator request.
1. Root [`AGENTS.md`](../AGENTS.md).
1. Accepted ADRs in [`docs/architecture/adr/`](architecture/adr/README.md).
1. Workspace baseline in
   [`docs/architecture/baseline-v0.13.0.md`](architecture/baseline-v0.13.0.md).
1. Standards in [`docs/standards/`](standards/README.md).
1. The active Bead issue and its child issues as the execution ledger for the
   scoped change.
1. Path-scoped skills in [`.agents/skills/`](../.agents/skills/).

## Change Routing

| Change type | First source | Validation surface |
| --- | --- | --- |
| Any code or architecture change | [`AGENTS.md`](../AGENTS.md) | Active Bead plus scoped gates |
| Refactor, MRO, facade, namespace, or import work | [Architecture baseline](architecture/baseline-v0.13.0.md) and scoped skill | `ruff`, `pyrefly`, `pyright`, affected `pytest` |
| Public API or interface change | Active Bead design and ADRs | Consumer grep/audit plus project gates |
| Docs or generated docs | [Documentation standard](standards/documentation.md) | `make docs DOCS_PHASE=audit` or narrower markdown gate |
| Docs audit policy or generated-doc exemptions | [Documentation standard](standards/documentation.md) and accepted ADRs | Full docs audit plus affected project audit; evidence must show stale generated symbols are still caught |
| Workspace tooling or Make behavior | [ADR-003](architecture/adr/003-workspace-tooling-hub-distribution.md) and [ADR-004](architecture/adr/004-generic-make-framework-in-flext-tests.md) | `make help`, `make check`, or touched generator tests |
| Pydantic, settings, and strict typing | [Pydantic references](references/pydantic2/version-policy.md) and type-system docs | `pyrefly`, `pyright`, affected tests |
| Testing behavior | [Testing standard](standards/testing.md) | `pytest` or `make test PROJECT=<project>` |

## Active ADRs

The canonical ADR registry is
[`docs/architecture/adr/README.md`](architecture/adr/README.md). Do not mirror
the ADR list here; update the registry when an ADR is added, superseded, or
retired.

## Ratified Refactor Gates

These Onda 0 decisions were ratified by the operator on 2026-07-04 for the
total FLEXT refactor plan:

- G1: Current and newly ratified patterns are live through this router and the
  sources it points to; stale backup files are not authority by themselves.
- G2: Additive structural work is allowed only at track scope with a named
  deletion budget that makes the track net-negative or explicitly records the
  remaining debt in Beads.
- G3: `flext-core` is the kernel and is excluded from downstream `base.py`
  service-handler scaffolding; improve existing kernel modules instead.
- G4: Work that conflicts with an active Bead constraint must hand off,
  supersede, or split the Bead before changing the constrained interface.
- G5: External clusters are absorbed through Beads as owned lanes; do not mix
  unrelated ownership inside a batch.
- G6: After scoped green validation, use explicit pathspecs to commit and
  fast-forward push, then record the SHA and evidence in Beads.

## Execution Rules

- Beads is the execution ledger. Claim the issue before writes and append
  command evidence after every meaningful step.
- Source changes are batched by ownership. A batch changes at most five files
  before import, lint, typecheck, and scoped test validation.
- Rope-backed structural changes are required for automated refactors. AST may
  classify and locate code, but structural rewrites must have idempotence and
  dry-run/apply evidence.
- No compatibility wrappers, fallback paths, public old-plus-new coexistence,
  suppressions, stubs, or hardcoded carve-outs are acceptable exits.
- If the single source of truth for a rule is missing, fix the source or stop
  and record the blocker. Do not infer a hidden rule from stale artifacts.

## Baseline Commands

Use the narrowest decisive command for the touched lane:

```bash
ruff check <path> --no-fix
pyrefly check <path>
pyright <path>
pytest <path-or-project>/tests -q
make check CHANGED_ONLY=1
make val VALIDATE_SCOPE=workspace
```

When a command is red, keep the exact command, exit code, and decisive output in
the active Bead before continuing.
