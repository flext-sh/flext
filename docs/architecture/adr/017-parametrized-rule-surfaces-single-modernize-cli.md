# ADR-017 — Parametrized Rule Surfaces and the Single Modernize CLI

<!-- TOC START -->
- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
- [Verification contract](#verification-contract)
<!-- TOC END -->

- **Status:** ACCEPTED TARGET — implementation in progress
- **Date:** 2026-09-15
- **Target line:** FLEXT `0.12.0-dev`, forward baseline `0.13.0`
- **Scope:** flext-infra modernize engine, rule/pattern storage, discovery and
  packaging for the whole fleet plus external consumers (ai-hub pilot).
  `make mod` is CURRENT IMPLEMENTATION; `config/rules/ast/` and repo-root
  `config/rules/` are ACCEPTED TARGET (not yet present in tree).
- **Complements:** ADR-005 (config SSOT), ADR-014 (family shape + codemod rules)
- **Tracking:** program epic beads (P0..Cn+1), plan
  `.kilo/plans/1789564109553-rope-modernize-execution-plan.md`

As of 2026-09-17, `make mod` is the implemented unified modernization surface.
The standalone `ast` verb and source-owned `config/rules/ast/` tree remain
planned under Bead `flext-oquk7`; this ADR records the accepted target contract,
not evidence that those surfaces are already available.

## Context

Modernization policy was scattered: ast-grep rules inside the Python package
(`src/flext_infra/codemod/`), sed-by-list rules in `text_rules.yml`, accessor
renames in a flext-core catalog, and several Python rewrite engines
(re/ast/libcst/tokenize) with embedded policy. Repo-root config trees are
invisible to installed distributions and wheels, so external consumers cannot
inherit fleet rules.

## Decision

1. **Verb taxonomy (operator law).** `mod` is the ONLY adjust/rewrite surface
   (CURRENT IMPLEMENTATION: `make mod` / `refactor mod`). `ast` is the
   ast-grep engine (ACCEPTED TARGET): it runs as phase 1 of `mod`
   (`flext-infra/src/flext_infra/codemod/ast_scan.py` exists) but its
   config/rules/ast/ pattern tree is not yet present in tree; standalone
   `refactor ast` is planned under Bead `flext-oquk7`. `gen` is the
   template generator (`make gen`, conform `mode=CHECK|APPLY`) consuming the
   SAME rope planners — generation, never adjustment. Public verbs
   `fix/fmt/check/test` are unchanged. No other adjust verb survives
   (`accessor-migrate`, `modernize-dataclass`, `fix-enforcement` executor die).
2. **Rules are data under `config/rules/`** (ACCEPTED TARGET — repo-root
   tree not yet present in CURRENT IMPLEMENTATION):
    - `flext-infra/config/rules/mod/sed.yaml` exists (sed-by-list rules,
      currently empty — `rules: []`);
    - `flext-infra/config/rules/rope/README.md` exists (rope phase
      parameters, ADR-017);
    - `config/rules/ast/` engine patterns `*.yml` + fixtures `tests/`
      (migrated from `src/flext_infra/codemod/{rules,utils,tests}`;
      the old directory is deleted in the same change) — ACCEPTED TARGET,
      not yet present in tree.
   Enforcement rows stay in `flext-infra/config/infra.yaml` (CURRENT
   IMPLEMENTATION); the beartype catalog stays in flext-core. Project-specific
   renames stay in the project (ai-hub owns its own rule files).

   **Migration note:** ADR-017 §2 describes the target contract at repo-root
   `config/rules/`. The CURRENT IMPLEMENTATION stores rules under
   `flext-infra/config/rules/` (`mod/sed.yaml`, `rope/README.md`) with enforcement
   rules in `flext-infra/config/infra.yaml`. Repo-root `config/rules/` and
   `config/rules/ast/` are ACCEPTED TARGET artifacts tracked under program epic
   beads (P0..Cn+1).
3. **Distribution discovery (Option C).** `config/rules/` is ACCEPTED TARGET
   (repo-root tree not present in CURRENT IMPLEMENTATION) and is planned
   as force-included distribution data in the wheel; providers resolve
   their config through `Distribution.locate_file("config/rules/ast")`
   (editable resolves the checkout; a wheel resolves the included
   data). The `ruleDirs` jail is re-anchored to the provider's
   `config/rules/<engine>/` root — never removed.
4. **Toggles are data, not flags.** Phase/component selection lives in
   `config/tooling.yaml` (`mod.phases.*`) read through typed enums; dry-run is
   scan mode without `--apply`.
5. **Enforcement convergence.** ENFORCE-XXX rows with `fix_action` kind
   `codemod` execute the SAME rules/phases of `mod`; no second execution loop.

## Consequences

- Python rewrite engines (re/ast/libcst/tokenize) are exterminated in
  flext-infra, never encapsulated; consumers rewire to the three instruments
  (rope, make mod, config rows).
- Discovery must be proven from a foreign project root (tmp project with local
  sgconfig) and from a built wheel before each landing cycle closes.
- Any new detector/transformer with embedded policy is a review defect.

## Verification contract

- `make mod` dry-run reports zero pending findings after migration.
- Rule fixtures validate through the mod gate engine.
- Foreign-root and wheel discovery tests stay green in every cycle.
