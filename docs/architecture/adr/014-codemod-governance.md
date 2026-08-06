# ADR-014 — Codemod governance: ast-grep + make mod + CRG as universal refactoring law

<!-- TOC START -->
- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
<!-- TOC END -->

- **Status:** Accepted
- **Date:** 2026-08-06

## Context

FLEXT refactoring across 38 projects lacked a single enforcement mechanism. Ad-hoc sed/grep edits, manual rewrites, and inconsistent patterns accumulated debt. Pre-commit hooks existed but did not enforce refactoring rules as error gates. Codemod rules were projected to disk (copied per-project) instead of discovered from installed packages.

## Decision

1. **ast-grep + `make mod` + CRG (Code Review Graph) is the sole official refactoring method.** No ad-hoc refactoring outside this pipeline.
2. **Codemod rules are package data**, not disk projections. Rules live in `flext_infra.codemod.rules` (and domain equivalents), discovered via `importlib.resources` in cascade order: `flext_core` → `flext_cli` → `flext_infra` → project-local.
3. **`make gen` does not project `ast-grep-rules/` to submodules.** `sgconfig.yml` is rendered only when a project has its own rules.
4. **Codemod bans are error gates in `make check`.** Violations block the build; they are not warnings.
5. **Pre-commit and pre-push hooks are installed and enforced.** They run fmt, fix, and codemod checks before any commit or push.
6. **Zero compatibility shims.** Refactoring removes the old pattern completely; no adapters, wrappers, or fallback paths.

## Consequences

- Every refactoring is atomic, reviewable, and reversible via `make mod` safety circuit (checkpoint → apply → measure → rollback).
- Rules propagate to all 38 projects automatically via package updates — no per-project file copying.
- CI enforces codemod bans as blocking gates; local development gets immediate feedback via pre-commit.
- Dead code is exterminated by codemod rules, not by manual deletion.
