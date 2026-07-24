---
name: flext-law
description: Apply the mandatory FLEXT engineering law for every implementation, review, migration, refactor, validation, or instruction-surface change.
---

# FLEXT Law

## Authority and scope

1. Read root `AGENTS.md` before touching FLEXT files.
2. Treat the live Bead, validated configuration, public contract, and current
   worktree as authority. Archives, backups, prior plans, and `0.20.0-dev` are
   evidence only unless current project law explicitly adopts them.
3. Claim the owning Bead before mutation. Preserve concurrent work and fix
   forward only: never reset, restore, clean, stash, rebase, or normalize
   shared work.
4. Change one canonical owner, update its consumers in the same cycle, and
   remove superseded paths. Do not add shims, aliases, fallbacks, suppression,
   or old-plus-new coexistence.

## Engineering law

- Follow Python 3.13, Clean Architecture, MRO composition, dependency
  direction, typed public contracts, Pydantic v2, SSOT, YAGNI, DRY, SOLID, and
  dependency injection as defined by root `AGENTS.md`.
- Declarations are data; behavior belongs in focused utilities, services,
  facades, bases, or CLI layers.
- Generated files and deployed projections are outputs, never source owners.
  Change their canonical generator/configuration and regenerate through the
  root Make surface.
- Lint, type, and tooling exception lists (ruff `per-file-ignores`, mypy
  `disabled-error-codes`, and equivalents) are code-generated from the
  flext-infra codegen SSOT (`flext-infra/config/tooling.yaml`), never
  hand-added to a consumer `pyproject.toml`. A required exception that the
  SSOT lacks is a change to that SSOT plus a regenerate, not a local edit.
- Never silence a lint, type error, or gate to make it pass: no `noqa`,
  `type: ignore`, per-file-ignore, or config carve-out added by an agent on
  its own authority. Fix the flagged code at its canonical owner. If a
  finding is a genuine false positive, stop and get explicit operator
  approval before adding any suppression, then encode it in the codegen SSOT.
- Tests validate public behavior. Use existing fixture topology and imports;
  do not create parallel test or configuration paths.
- **P0 — Tests validate config/settings changes by construction.** Tests
  validate config/settings CONTRACTS, never frozen values: any expected value
  that config owns (versions, verbs, paths, URLs, profiles, defaults) is read
  from the same SSOT production reads (codegen.yaml/tooling.yaml/models) or
  proven via generator round-trip. A test that breaks on a legitimate
  config/settings change is a test defect; fix the test, never freeze the
  configuration. Golden files pin STRUCTURE only and are regenerated via the
  canonical make verb. This rule applies to all test tiers, markdown examples,
  and docstring snippets validated by the pytest plugin (operator law
  2026-07-24, cosmos-main-hr9e).

## Automated adjustments and synchronization

- Any automated adjustment — sync, codegen round-trip, auto-fix, or upstream
  merge — is a code change and must pass the same gates as a manual change.
- Before claiming an automated adjustment is done, run the affected root-Make
  gates (`make check` and `make test` for the touched projects) and record the
  exact command, exit code, and decisive output in the owning Bead.
- Automated adjustments must be atomic within the lane: one coherent commit or
  an explicit pathspec-bound set of commits, never open-ended `fixes` commits
  that accumulate unrelated changes.
- Before merging the lane into the original branch (e.g. `0.12.0-dev`), run a
  pre-merge validation of the whole lane against the current target: `make
  check` and `make test` for every affected project. Do not merge if any gate
  is red; fix forward inside the lane and re-validate.
- A merge from upstream/external into the lane must also be validated in the
  lane context before it is considered absorbed.

## Completion discipline

Use `.agents/skills/flext-inviolable-rules/SKILL.md` for every task closure.
No task succeeds while the affected environment is broken, a required gate is
failing, or the work is left as unowned WIP.
