# ADR-018 — Generator Declarations Law

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
- [Verification contract](#verification-contract)

<!-- TOC END -->

- **Status:** ACCEPTED — operator law 2026-09-20; implementation phased under
  `flext-0in0k`
- **Date:** 2026-09-20
- **Target line:** FLEXT `0.12.0-dev`, forward baseline `0.13.0`
- **Scope:** every FLEXT generator, detector and fix (`make gen`, `make mod`,
  `make fix`, the namespace validator and its gates) and every consumer of them: the
  `flext` workspace and its 31 members, ai-hub, cosmos-main and its apps, cosmos-docgen,
  invest and their FLEXT subprojects.
- **Complements:** ADR-010 (standardization via codegen), ADR-014 (family shape +
  codemod rules), ADR-017 (parametrized rule surfaces). Supersedes every filename→letter
  table, closed folder list and advisory-gate list those ADRs tolerated.
- **Rule owner:** `~/agents/rules/flext/generator-declarations.md` (projected to every
  provider). This ADR records the decision; the rule file is the binding text.
- **Tracking:** epic `flext-0in0k` (20 phased beads, each carrying the full rule text);
  superseded `flext-exbwv`, `flext-crd1y`, `flext-b3xmn`, `flext-szjre`, `flext-fdoah`,
  `flext-s9bxq` (closed, linked); `flext-ssnc7` and `flext-mbowt` linked, kept open for
  their unrelated live children.

## Context

The lazy-init and `pyproject.toml` generators accumulated accommodations that decide
behavior from names and hand lists instead of declarations: a filename→letter table
(`NAMESPACE_LAYER_BY_FILE`, five readers), closed folder sets (`ROOT_WRAPPER_SEGMENTS`,
`NON_PUBLIC_LAZY_ROOTS`, `ALL_SCAN_PATTERNS`, `env-dirs`/`test-like-dirs`, a literal
fallback in `namespace_config`), a hardcoded `TEST_RUNTIME_ALIAS_TARGETS`, `ALIAS_NAMES`
used as the list of who exists, hand-declared `root_packages`/`root_modules`, a
single-part package name treated as a public root, an advisory-gate list by name, a
guard for one `services/models.py`, and an `examples/` bypass in the validator. Every
consumer of the generator inherited them. On 2026-09-20 the fleet `make gen` broke
(`flext-infra a43dcf547`) because export discovery accepted any class of a module with
no `__all__` and rendered `from .01_basic_usage import …`.

The operator negotiated the correct contract point by point and ordered it to become a
FLEXT rule generators cannot violate, followed by the extermination of every hack and of
the permission that tolerated it, one by one, at the source.

## Decision

The fourteen points of `generator-declarations.md` are law. In one line each:

1. A facade letter belongs to the module that declares it in its explicit `__all__`.
2. An `__init__.py` propagates; it never declares.
3. The root inherits from the main module; the root `__all__` overrides.
4. Internal tiers are detected from folders with Python; `src/` is public, the rest
   internal; no list anywhere.
5. Internal tiers inherit by class MRO and declare their own letter; a subdirectory
   declares no short alias.
6. The generator propagates, never compensates; the validator reports.
7. Violations are fixed at the source; recurrence makes a catalog rule with a fixture.
8. Verdict and count derive from one classification; `error` fails, warning does not.
9. Every rule is computed from an existing source and proven fleet-wide before commit.
10. Declaration adjustment is automatic; deriving beats listing; unnecessary lists die.
11. Every module is one nested class; nothing loose, no alias outside `__all__`; the
    existing rules become `error`.
12. An exception is a single motivated entry authorized explicitly by the operator.
13. A hack's permission dies in the same commit as the hack.
14. Every module obeys every rule (FLEXT, SOLID, DRY, YAGNI, CA, SSOT, DI); strict
    compliance is the dedup mechanism expected to free 60–80% of the code.

Order of execution (operator): law → extermination of lists, manual declarations and
their permissions → generator/detector/fix repair → census by the validator → automatic
correction (`make mod`) → consumers → strict compliance → close. One bead per phase;
work in worktrees on the freshly fetched integration tip; never a rollback; never a
manual mass fix.

## Consequences

- `flext-infra` loses every table and list named in Context; the replacement is one
  derivation each (`u.Infra.discover_python_dirs`, the module `__all__`, the class base,
  the folder on disk). Their permissions (exclusions, bypasses, advisory lists) leave in
  the same commits.
- Every consumer regenerates; the diff is the inventory of hacks it carried. Two
  flext-infra forks (`flext-sh@0.12.0-dev`, `datacosmos-br@baseline-20260919`) converge
  to one line.
- The namespace validator reports one-nested-class, no-alias and nothing-loose
  violations as `error`; the fix derives letter ⇄ base and writes the declaration.
- Integration state found on 2026-09-21, adopted forward (never reverted): member tips had
  already received `chore(gen): converge fleet projections` commits ahead of the superproject
  gitlinks (C1 landed before B1); installed standalone those tips fail at import
  (`flext_cli/services/auth.py` imports the `s` letter from the package root while the package
  is importing — a violation of the import law, fixed at its source, never in the lazy loader);
  the superproject tip declared a flext-infra gitlink (`90feb4a76`) that had never been
  published, carried to the integration branch by the rule PR. The consequence for the plan:
  B1 (letter ⇄ base derivation) precedes every further member regeneration.
- Measured populations at decision time: 42 internal facades without the letter in
  `__all__` (10 repos, 0 in `src/`), 5 letters bound to non-extending classes, 4 dead
  example classes, 36 numbered scripts inside packages (12 repos), 8 public + 18 private
  reserved names in nested packages, 61 internal inits with divergent shapes.

## Verification contract

- `make gen` exits 0 in 32/32 and a second run has no diff, after every flext-infra
  commit of the epic — before the commit is pushed.
- `make mod` twice is idempotent; the validator's counts above reach 0.
- `make check` and `make test` green in 32/32 and in every consumer; no new exclusion.
- Logical LOC measured by the canonical verb before the first commit and after the last;
  the delta is recorded on `flext-0in0k`.
- `bd lint --json` clean for every bead of the epic; each closes with SHA, command and
  exit code.
