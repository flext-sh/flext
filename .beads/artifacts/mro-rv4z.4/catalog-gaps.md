# Catalog Gap Audit — FLEXT Enforcement Fixers

**Bead:** `mro-rv4z.4`  
**Generated:** 2026-07-03  
**Scope:** Map every canonical enforcement rule that lacks a `fix_action` or whose `fix_action` has no registered adapter in `flext-infra`.

## Method

1. Loaded `FlextUtilitiesEnforcement.build_canonical_catalog()` from `flext_core`.
2. Inspected adapter registries in:
   - `flext-infra/src/flext_infra/fixers/transformer_fixer.py` (`_TRANSFORMERS`)
   - `flext-infra/src/flext_infra/fixers/rope_fixer.py` (`_target_dispatch`)
   - `flext-infra/src/flext_infra/fixers/gate_fixer.py` (gate registry → `FlextInfraSmellsGate`)
   - `flext-infra/src/flext_infra/fixers/manual_fixer.py` (accepts all `kind: manual`)

## Summary

| Metric | Count |
|---|---|
| Total enabled catalog rules | 78 |
| Rules with a declared `fix_action` | 31 |
| Rules whose `fix_action` lacks a registered adapter | **0** |
| Rules without `fix_action` but detectable source | **46** |
| Rules without `fix_action` and undetectable by current orchestrator | 1 (`ENFORCE-022`, `runtime_warning`) |
| Critical gaps (high-frequency / architectural blockers) | 14 |

All declared fix actions (`transformer/*`, `rope/*`, `gate/smells`, `manual/*`) currently resolve to a registered adapter. The real gap is the 46 enabled rules that have no `fix_action` at all, even though their source is already collected by the orchestrator.

## Fix Actions Without Adapter

None. Every catalog `fix_action.kind/target` maps to an adapter:

- `transformer/*` → `FlextInfraTransformerFixerAdapter`
- `rope/*` → `FlextInfraRopeFixerAdapter`
- `gate/smells` → `FlextInfraGateFixerAdapter` → `FlextInfraSmellsGate` (`can_fix=True`)
- `manual/*` → `FlextInfraManualFixerAdapter`

## Rules Without `fix_action` but Detectable Source

| Rule | Source kind | Source field / predicate | Suggested adapter / transformer / rope target | Automation ease | Notes |
|---|---|---|---|---|---|
| ENFORCE-001 | `flext_infra_detector` | `loose_objects` | `manual` or new `rope/relocate_loose_object` | Difícil | Requires domain classification; no canonical owner without human judgment. |
| ENFORCE-002 | `flext_infra_detector` | `import_violations` | `transformer/import_modernizer` (extend params) | Médio | Map non-canonical alias imports to canonical project facade aliases. |
| ENFORCE-003 | `flext_infra_detector` | `namespace_source_violations` | `transformer/import_modernizer` | Médio | Rewrite imports from wrong upstream project to the correct local re-export. |
| ENFORCE-004 | `flext_infra_detector` | `internal_import_violations` | `rope/rewrite_private_import_bypass` (reuse) | Médio/Difícil | Similar to ENFORCE-068; needs package-boundary-aware rewrite. |
| ENFORCE-005 | `flext_infra_detector` | `manual_protocol_violations` | `manual/deep_namespace_refactor` | Difícil | Move Protocol classes to `protocols.py` / `_protocols/` tree; architectural. |
| ENFORCE-006 | `flext_infra_detector` | `cyclic_imports` | `manual/break_import_cycle` | Difícil | Needs import-graph analysis and often domain redesign. |
| ENFORCE-007 | `flext_infra_detector` | `runtime_alias_violations` | `transformer/import_modernizer` | Médio | Rebind or relocate c/p/t/m/u/r/s/x aliases to canonical owner modules. |
| ENFORCE-009 | `flext_infra_detector` | `manual_typing_violations` | `manual/relocation` | Difícil | Move typing aliases to `typings.py` / `_typings/`; facade restructure. |
| ENFORCE-010 | `flext_infra_detector` | `compatibility_alias_violations` | `rope/rewrite_compatibility_alias` (reuse) | Fácil/Médio | Same target already handles `beartype/-/compatibility_alias` for ENFORCE-064/066. |
| ENFORCE-011 | `flext_infra_detector` | `class_placement_violations` | `manual/deep_namespace_refactor` | Difícil | Wrong facade layer; may require moving classes across modules. |
| ENFORCE-012 | `flext_infra_detector` | `mro_completeness_violations` | `manual/mro_completeness` | Difícil | Missing mixin trees; safe rewrite needs semantic MRO knowledge. |
| ENFORCE-013 | `flext_infra_detector` | `parse_failures` | `manual/parse_repair` | Difícil | File does not parse; automatic repair is unsafe. |
| ENFORCE-014 | `flext_infra_detector` | `facade_statuses` | `manual/facade_bootstrap` | Difícil | Missing canonical facade files; project-scaffold change. |
| ENFORCE-095 | `flext_infra_detector` | `direct_oracledb_import_violations` | `transformer/import_modernizer` | Médio | Add oracle/oracledb mapping to import modernizer params. |
| ENFORCE-096 | `flext_infra_detector` | `direct_ldap3_import_violations` | `transformer/import_modernizer` | Médio | Add ldap3 mapping to import modernizer params. |
| ENFORCE-015 | `flext_tests_validator` | — | `manual/test_import_discipline` | Difícil | Lazy imports / TYPE_CHECKING misuse / sys.path manipulation; unsafe to auto-fix. |
| ENFORCE-017 | `flext_tests_validator` | — | `manual/test_bypass` | Difícil | noqa / pragma: no cover / exception swallowing in tests. |
| ENFORCE-018 | `flext_tests_validator` | — | `manual/test_layer_violation` | Difícil | Lower-layer importing upper layer; architectural. |
| ENFORCE-019 | `flext_tests_validator` | — | `manual/test_mock_pattern` | Difícil | monkeypatch / Mock / @patch usage requires test redesign. |
| ENFORCE-020 | `flext_tests_validator` | — | `manual/pyproject_toml` | Difícil | pyproject.toml deviations; config change. |
| ENFORCE-021 | `flext_tests_validator` | — | `manual/markdown_codeblock` | Difícil | Markdown code-block validation. |
| ENFORCE-023 | `ruff` | — | `gate/ruff_lint` | Médio | ANN401 dynamic Any — usually no autofix; needs explicit annotation. |
| ENFORCE-024 | `ruff` | — | `gate/ruff_lint` | Fácil | PGH003 missing specific rule code — Ruff can autofix with rule code. |
| ENFORCE-025 | `ruff` | — | `gate/ruff_lint` | Fácil | TID252 relative imports — Ruff supports autofix to absolute imports. |
| ENFORCE-040 | `ruff` | — | `gate/ruff_lint` | Médio | Linter ignore without justification — needs inline documentation. |
| ENFORCE-039 | `beartype` | `deprecated_syntax` / `cast` | `transformer/pattern` | Médio | Remove or rewrite `cast()` calls outside core result internals. |
| ENFORCE-041 | `beartype` | `deprecated_syntax` / `model_rebuild` | `transformer/pattern` | Médio | Remove `model_rebuild()` calls; may require resolving forward refs first. |
| ENFORCE-042 | `beartype` | `loose_symbol` / settings | `manual/settings_base` | Difícil | Settings class must inherit `FlextSettings`; class signature change. |
| ENFORCE-043 | `beartype` | `wrapper` | `manual/wrapper_elimination` | Difícil | Pass-through wrapper; needs semantic inline. |
| ENFORCE-044 | `beartype` | `deprecated_syntax` / private `*attr` | `transformer/pattern` | Médio | Replace `hasattr/getattr/setattr` probing of private attrs. |
| ENFORCE-046 | `beartype` | `import_blacklist` | `transformer/import_modernizer` | Médio | Canonical facade files importing from own `_models/_protocols` instead of c/m/p/t/u. |
| ENFORCE-047 | `beartype` | `mro_shape` | `manual/mro_rebase` | Difícil | First base must be alias or Pattern-B peer; reordering can break MRO. |
| ENFORCE-049 | `beartype` | `mro_shape` | `manual/mro_rebase` | Difícil | Multi-parent facade must list canonical alias first. |
| ENFORCE-050 | `beartype` | `alias_rebind` | `transformer/alias_rebind_injector` | Fácil | Append `t = FlextXxxTypings` style rebind at end-of-file if missing. |
| ENFORCE-051 | `beartype` | `alias_rebind` | `transformer/import_modernizer` | Médio | Remove self-package imports of c/m/p/t/u and replace with local rebind. |
| ENFORCE-052 | `beartype` | `alias_rebind` | `transformer/import_modernizer` + `TYPE_CHECKING` | Médio | Move sibling `_models/*` imports used only in annotations under `if TYPE_CHECKING`. |
| ENFORCE-053 | `beartype` | `mro_shape` | `manual/mro_rebase` | Difícil | Utilities facade must list explicit parent first. |
| ENFORCE-054 | `beartype` | `deprecated_syntax` | `transformer/pattern` | Médio | Rewrite forbidden `.Core.Tests` namespace paths in tests. |
| ENFORCE-055 | `beartype` | `deprecated_syntax` | `transformer/import_modernizer` | Médio | Redirect wrapper alias imports to wrapper root package. |
| ENFORCE-071 | `beartype` | `method_shape` | `manual/decompose_parameters` | Difícil | Too many parameters; needs domain decomposition. |
| ENFORCE-072 | `code_smell` | — | `gate/smells` (extend `smell_fixer_for`) | Difícil | Too many return statements; control-flow redesign. |
| ENFORCE-073 | `code_smell` | — | `gate/smells` | Difícil | Nesting depth exceeds threshold; needs helper extraction. |
| ENFORCE-075 | `code_smell` | — | `gate/smells` | Difícil | Function cyclomatic complexity; decompose. |
| ENFORCE-076 | `code_smell` | — | `gate/smells` | Difícil | Module cyclomatic complexity; split module. |
| ENFORCE-077 | `code_smell` | — | `gate/smells` | Difícil | Identical code blocks; extract shared helper. |
| ENFORCE-078 | `code_smell` | — | `gate/smells` | Difícil | Similar code blocks; refactor to shared abstraction. |

## Critical Gaps

Rules that are both high-frequency in the workspace and currently block automated remediation:

1. **ENFORCE-002 / ENFORCE-003 / ENFORCE-007** — import/alias violations. Highest ROI; can reuse/extend `transformer/import_modernizer`.
2. **ENFORCE-004 / ENFORCE-068** — private/internal import bypasses. `rope/rewrite_private_import_bypass` already exists for beartype; extending to `flext_infra_detector/internal_import_violations` is the canonical path.
3. **ENFORCE-010** — backwards-compatibility aliases. `rope/rewrite_compatibility_alias` target already implemented for beartype; wire to detector field.
4. **ENFORCE-050 / ENFORCE-051 / ENFORCE-052** — beartype alias rebind rules. ENFORCE-050 is easy (EOF alias injection); 051/052 need import modernizer extensions.
5. **ENFORCE-024 / ENFORCE-025** — ruff autofixable rules. Only need a `gate/ruff_lint` fix action or direct Ruff invocation.
6. **ENFORCE-095 / ENFORCE-096** — direct vendor imports. Extend `transformer/import_modernizer` with vendor-specific mappings.
7. **ENFORCE-054 / ENFORCE-055** — deprecated test/wrapper paths. Pattern transformer handles this well.

## Recommended Next Steps

1. Add `fix_action` to the 14 critical gaps first, starting with import/alias rules that map to existing adapters.
2. Reuse existing rope/transformer targets rather than creating new adapters:
   - `rope/rewrite_compatibility_alias` for ENFORCE-010.
   - `transformer/import_modernizer` for ENFORCE-002/003/007/046/051/052/095/096.
   - `transformer/pattern` for ENFORCE-039/041/044/054/055.
3. For `ruff`-sourced rules, add `fix_action: {kind: gate, target: ruff_lint, params: {smell_tag: ...}}` once `FlextInfraRuffLintGate.can_fix=True` supports the relevant rule codes.
4. Keep architectural refactor rules (`ENFORCE-005`, `ENFORCE-009`, `ENFORCE-011`, `ENFORCE-012`, `ENFORCE-015`–`021`, `ENFORCE-042`–`043`, `ENFORCE-047`/`049`/`053`, `ENFORCE-071`–`078`) as `manual` fix actions; they require human design review.

## Evidence

- Catalog dump command: `cd /home/marlonsc/flext && .venv/bin/python - <<'PY'` importing `FlextUtilitiesEnforcement` and iterating `catalog.enabled_rules()`.
- Adapter registry inspection: direct reads of `transformer_fixer.py:61-79`, `rope_fixer.py:125-134`, `gate_fixer.py:37-50`, `manual_fixer.py:29-37`.
- Gate registry confirms `FlextInfraSmellsGate.gate_id == "smells"` and `can_fix=True`.
