# FLEXT Governance Router

## Purpose

This file maps each change to its canonical owner. It does not restate
engineering law or skill procedures.

## Authority

Apply the newest applicable source in this order:

1. Live operator request.
2. Active Bead in the workspace-root tracker.
3. Accepted ADRs in [`architecture/adr/`](architecture/adr/README.md).
4. Root `AGENTS.md`.
5. The owning skill or standard.
6. Other documentation.

When a higher source changes reality, update the affected lower sources in the
same change. Ask before acting only when the conflict cannot be resolved from
this order.

## Owner Routing

| Concern | Canonical owner | Decisive validation |
| --- | --- | --- |
| Any code or architecture change | `AGENTS.md` (repo root) | Active Bead plus scoped gates |
| Refactor, MRO, facade, namespace, or import work | [Architecture baseline](architecture/baseline-v0.13.0.md) and scoped skill | `ruff`, `pyrefly`, `pyright`, affected `pytest` |
| Public API or interface change | Active Bead design and ADRs | Consumer grep/audit plus project gates |
| Docs or generated docs | [Documentation standard](standards/documentation.md) | `make docs DOCS_PHASE=audit` or narrower markdown gate |
| Docs audit policy or generated-doc exemptions | [Documentation standard](standards/documentation.md) and accepted ADRs | Full docs audit plus affected project audit; evidence must show stale generated symbols are still caught |
| Workspace tooling or Make behavior | [ADR-003](architecture/adr/003-workspace-tooling-hub-distribution.md) and [ADR-004](architecture/adr/004-generic-make-framework-in-flext-tests.md) | `make help`, `make check`, or touched generator tests |
| Operational kernel, CLI platform, or automated conformance | [ADR-007](architecture/adr/007-operational-kernel-cli-conform.md) | Clean-baseline gate, transactional conform proof, consumer gates |
| Pydantic, settings, and strict typing | Pydantic references (`docs/references/pydantic2/`, repo-only) and type-system docs | `pyrefly`, `pyright`, affected tests |
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

<!-- mro-wkii.17.26 (agent: codex) — route every 0.20 stabilization through the ratified clean-baseline sequence. -->

- Beads is the execution ledger. Claim the issue before writes and append
  command evidence after every meaningful step.
- Stabilization is ordered: governance alignment, completion of every existing
  merge, removal of conflicts and markers, a zero-error/zero-warning global
  static and pytest baseline, and only then new architecture work.
- Source changes are batched by ownership. A batch changes at most five files
  before import, lint, typecheck, and scoped test validation.
- `flext-infra codegen conform` is the only owner of broad structural writes.
  Rope validates the complete workspace graph; AST-oriented tools, LSP, Scope,
  and CRG may classify or propose, but cannot independently apply or accept a
  live-tree rewrite.
- No compatibility wrappers, fallback paths, public old-plus-new coexistence,
  suppressions, stubs, or hardcoded carve-outs are acceptable exits.
- If the single source of truth for a rule is missing, fix the source or stop
  and record the blocker. Do not infer a hidden rule from stale artifacts.

## Baseline Commands

Choose the narrowest decisive command from the quality-gates skill, then widen
only after it passes:

```bash
ruff check <path> --no-fix
pyrefly check <path>
pytest <path-or-project>/tests -q
markdownlint-cli2 <path>
make check PROJECT=<project> CHECK_GATES=<gates>
make val VALIDATE_SCOPE=workspace
```

Record every red or green result with its exit code and decisive output in the
active workspace-root Bead.
