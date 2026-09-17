# ADR-017 — Parametrized Rule Surfaces and the Single Modernize CLI

<!-- TOC START -->
- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
- [Verification contract](#verification-contract)
<!-- TOC END -->

- **Status:** Accepted (draft evolving per cycle; program plan of 2026-09-15)
- **Date:** 2026-09-15
- **Target line:** FLEXT `0.12.0-dev`, forward baseline `0.13.0`
- **Scope:** flext-infra modernize engine, rule/pattern storage, discovery and
  packaging for the whole fleet plus external consumers (ai-hub pilot)
- **Complements:** ADR-005 (config SSOT), ADR-014 (family shape + codemod rules)
- **Tracking:** Gas City program epic `flext-itpd1` and documentation convergence
  task `flext-itpd1.2`. The versioned resume contract is
  `docs/roadmap/rope-gen-engine-runbook-2026-09-15.md`; workspace-local plans
  are session evidence and do not define the published execution route.

## Context

Modernization policy was scattered: ast-grep rules inside the Python package
(`src/flext_infra/codemod/`), sed-by-list rules in `text_rules.yml`, accessor
renames in a flext-core catalog, and several Python rewrite engines
(re/ast/libcst/tokenize) with embedded policy. Repo-root config trees are
invisible to installed distributions and wheels, so external consumers cannot
inherit fleet rules.

## Decision

1. **Verb taxonomy (operator law).** `mod` is the ONLY adjust/rewrite surface
   (`make mod` / `refactor mod`). `gen` is the template generator (`make gen`,
   conform `mode=CHECK|APPLY`) consuming the SAME rope planners — generation,
   never adjustment. Public verbs `fix/fmt/check/test` are unchanged. No other
   adjust verb survives (`accessor-migrate`, `modernize-dataclass`,
   `fix-enforcement` executor die). A separate standalone `ast` verb is planned
   but not yet a public surface; ast-grep runs only as phase 1 of `mod`.
2. **Rules are data under `flext-infra/config/rules/`** (SSOT, multiple files):
   - `flext-infra/config/rules/mod/` — **current** verb policy: preset-rewire,
     accessor-renames, external-contracts exemptions, sed lists (`sed.yaml`,
     currently empty rules list);
   - `config/rules/ast/` — **planned**, not yet materialized: engine patterns
     `*.yml` + fixtures `tests/` (to be migrated from `src/flext_infra/codemod/`);
   - `config/rules/rope/` — **planned**, not yet materialized: rope phase
     parameters and violation models.
   Enforcement rows stay in `flext-infra/config/infra.yaml`; the beartype
   catalog stays in flext-core. Project-specific renames stay in the project
   (ai-hub owns its own rule files).
3. **Distribution discovery (Option C, planned).** `config/rules/` is planned to
   be force-included in the wheel as distribution data; providers resolve their
   config through `Distribution.locate_file("config/rules/ast")` (editable
   resolves the checkout; a wheel resolves the included data). The `ruleDirs`
   jail is re-anchored to the provider's `config/rules/<engine>/` root — never
   removed. Not yet implemented.
4. **Toggles are data, not flags.** Phase/component selection lives in
   `flext-infra/config/tooling.yaml` (`mod.phases.*`) read through typed enums; dry-run is
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
