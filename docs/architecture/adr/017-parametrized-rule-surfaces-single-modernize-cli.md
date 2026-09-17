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
  `make mod` is wired in the current Make owner. The infra-owned
  `config/rules/mod/` exists; the workspace-root `config/rules/` and
  infra `config/rules/ast/` trees are absent in this source snapshot.
- **Complements:** ADR-005 (config SSOT), ADR-014 (family shape + codemod rules)
- **Tracking:** `flext-itpd1.3` coordinates recovery under `flext-itpd1`;
  `flext-itpd1.2` owns documentation and `flext-itpd1.4` owns Make machinery.
  The historical AST/migration reference `flext-oquk7` is retained for owner
  reconciliation, not a claim of its current status. Beads records execution
  state; it does not establish runtime behavior. The versioned resume contract
  is the [Rope-Gen runbook](../../roadmap/rope-gen-engine-runbook-2026-09-15.md).
  Private plans are local context, not automatic authority or publication sources.

Source inspection on 2026-09-17 distinguishes Make verbs from CLI routes:
`make mod` dispatches to `refactor mod --apply`; the current CLI source also
registers `refactor ast`, but the Make verb catalog contains no `ast` verb.
Neither CLI execution nor wheel discovery was validated by this reconciliation.

## Context

Modernization policy was scattered: ast-grep rules inside the Python package
(`src/flext_infra/codemod/`), sed-by-list rules in `text_rules.yml`, accessor
renames in a flext-core catalog, and several Python rewrite engines
(re/ast/libcst/tokenize) with embedded policy. Repo-root config trees are
invisible to installed distributions and wheels, so external consumers cannot
inherit fleet rules.

## Decision

1. **Unified structural modernization.** `make mod` is the current public Make
   surface for structural rewrites; its template invokes `refactor mod --apply`.
   `make gen` invokes conform generation. Public `fix/fmt/check/test` remain;
   `fix-enforcement` is also still declared in the Make catalog. Historical
   removal proposals are targets, not proof that declared commands disappeared.
   `refactor ast` is registered in `services/cli_routes_refactor.py`; this does
   not establish a separate `make ast` verb or completion of AST rule migration.
2. **Rules are data at their canonical owner.** The inspected infra tree contains
   `flext-infra/config/rules/mod/sed.yaml` with `rules: []` and
   `flext-infra/config/rules/rope/README.md`. A README records intent, not an
   implemented parameter catalog. Do not claim preset/accessor/exemption files
   are present in that directory when only `sed.yaml` is present. The accepted
   AST pattern/fixture migration into `config/rules/ast/` remains unproved;
   preserve the existing source owner until a complete validated cutover.
   Enforcement and project-specific policies retain their typed owners; this
   ADR does not authorize copying another project's rule catalog.
3. **Distribution discovery (Option C, accepted target).** Distribution-owned
   rule data must resolve from editable and wheel installations, with the
   `ruleDirs` boundary preserved. The proposed
   `Distribution.locate_file("config/rules/ast")` locator describes the target,
   not a usable path demonstrated by this source inventory. Foreign-root and
   built-wheel receipts are required before claiming this migration delivered.
4. **Phase policy is data.** `flext-infra/config/tooling.yaml` currently declares
   `mod.phases.import-alignment`. That declaration alone does not prove typed
   consumption of every proposed phase. Public `make mod` applies its fixed
   operation; do not document a Make dry-run toggle absent from its owner.
5. **Enforcement convergence — ACCEPTED TARGET.** ENFORCE-XXX rows with
   `fix_action` kind `codemod` must converge on the same rules/phases of `mod`,
   without a second execution loop. This convergence is not established as
   implemented or runtime-proven; the declared `fix-enforcement` route remains.

## Consequences

- The accepted target removes competing rewrite engines through a complete
  owner/consumer cutover; this ADR does not certify that removal has happened.
- Discovery must be proven from a foreign project root (tmp project with local
  sgconfig) and from a built wheel before each landing cycle closes.
- Any new detector/transformer with embedded policy is a review defect.

## Verification contract

- Public `make mod` must converge with zero actionable or detection-only
  findings after migration; its Make route is apply, not a claimed dry-run.
- Rule fixtures validate through the mod gate engine.
- Foreign-root and wheel discovery tests stay green in every cycle.

These are acceptance requirements, not recorded results. Fleet stability remains
unproved until the canonical root lifecycle, runtime and applicable docs/link
checks pass on the published integrated candidate, including repeated gen/fix/fmt
no-op receipts. The coordinator owns that validation and closure.
