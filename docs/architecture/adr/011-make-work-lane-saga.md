# ADR-0016 — Public make work lane saga

<!-- TOC START -->
- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
<!-- TOC END -->

- **Status:** Accepted
- **Date:** 2026-08-03
- **Scope:** flext-infra `FlextInfraWorkService` + generated Make `work` verb

## Context

Lane lifecycle used to be split across ad-hoc `bd`/`git`/`gh` steps and a
public `worktree` Make surface. That duplicated ownership with `ship`/`pr`
and allowed metadata/registry drift on land.

## Decision

1. Public Make verb is `work` with WHAT=`start|status|land|finish` only.
2. `FlextInfraWorktreeService` remains the internal worktree engine.
3. Land owns the lane PR; finish removes the registered lane after merge.
4. Land/finish bind bead metadata `worktree` to Git `registered_lane`, refuse
   permanent branches, and require `metadata.head_oid` for CAS.
5. On workspace-root, `PROJECT=<member>` maps to `WORKSPACE` when WORKSPACE is
   not overridden on the CLI.

## Consequences

- Operators and agents use one saga; docs live in `docs/guides/make-commands.md`
  and `docs/ways-of-working/worker-lane-contract.md`.
- Residual public `ship`/`worktree` docs are retired from the command guide.
