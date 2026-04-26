---
name: flext-enforcement-catalog
description: Canonical index of cross-layer enforcement rules exposed as c.ENFORCEMENT_CATALOG (typed Pydantic SSOT in flext-core) and driven by the flext-tests pytest dispatcher. Use when adding, retiring, or cross-referencing any workspace enforcement rule, or when wiring a new detector/validator into the shared pytest run.
---

# FLEXT Enforcement Catalog

**Reviewed**: 2026-04-25 | **Scope**: cross-layer rule index + pytest dispatcher

## Scope

- `flext-core/src/flext_core/_constants/enforcement.py` — the `ENFORCEMENT_CATALOG` constant.
- `flext-core/src/flext_core/_models/enforcement.py` — the `EnforcementCatalog` / `EnforcementRuleSpec` / `EnforcementSourceKind` types.
- `flext-tests/src/flext_tests/_fixtures/enforcement.py` — the pytest dispatcher that reads the catalog.
- `flext-tests/pyproject.toml` — the `flext_tests_enforcement` pytest11 entry point.
- Cross-referenced (authoritative for their layer, do NOT rewrite here):
  - `sgconfig.yml` — ast-grep rules loaded from `.agents/skills/*/rules.yml`.
  - `flext-infra/src/flext_infra/refactor/namespace_enforcer.py` — the orchestrator that produces `ProjectEnforcementReport`.
  - `flext-tests/src/flext_tests/validator.py` — `FlextTestsValidator` (`tv.*`).
  - `flext-core/src/flext_core/_constants/enforcement.py::FlextMroViolation` — the runtime warning.
  - `make lint` — ruff enforcement.

## Canonical reference

The catalog is a frozen Pydantic model in Python — there is no YAML, no JSON, no text registry in `.agents/`. Every consumer (pytest dispatcher, skills, test suites) reads the same instance:

```python
from flext_core import c, FlextModelsEnforcement as m_enf

for rule in c.ENFORCEMENT_CATALOG.rules:
    if rule.enabled:
        print(rule.id, rule.severity, rule.source.kind)

# Filter by origin
infra_rules = c.ENFORCEMENT_CATALOG.by_kind(
    m_enf.EnforcementSourceKind.FLEXT_INFRA_DETECTOR
)
```

Each entry is a `m_enf.EnforcementRuleSpec` carrying a discriminated `source` union (one of `EnforcementInfraDetectorSource` / `EnforcementTestsValidatorSource` / `EnforcementRuntimeWarningSource` / `EnforcementRuffSource` / `EnforcementAstGrepSource` / `EnforcementSkillPointerSource` / `EnforcementBeartypeSource`).

## Source kinds

| Kind | Dispatched? | Authority |
| --- | --- | --- |
| `flext_infra_detector` | Yes via `FlextInfraNamespaceEnforcer.enforce()` | field on `m.Infra.ProjectEnforcementReport` |
| `flext_tests_validator` | Yes via `tv.<method>` | classmethod on `FlextTestsValidator` |
| `runtime_warning` | Yes via pytest `filterwarnings` + `pytest_warning_recorded` | warning class in `flext-core` |
| `beartype` | Yes via `FlextUtilitiesEnforcement` (`c.ENFORCEMENT_RULES["<tag>"]` + `check_<tag>` on `FlextUtilitiesBeartypeEngine` + dispatch arm in `FlextUtilitiesEnforcementCollect._namespace_items`) | static method on `FlextUtilitiesBeartypeEngine` |
| `ruff` | No (documentation-only) | `make lint` owns dispatch |
| `ast_grep` | No (documentation-only) | `sgconfig.yml` + `.agents/skills/<skill>/rules.yml` own dispatch |
| `skill_pointer` | No (documentation-only) | narrative SKILL.md only |

## Using the pytest dispatcher

Enabled automatically when pytest's rootdir contains all three workspace markers (`AGENTS.md` + `flext-core/` + `flext-tests/`). Common flags:

```bash
pytest                                      # auto — workspace root
pytest --flext-enforce-strict               # runtime warnings → failures
pytest --flext-enforce-rules=ENFORCE-012    # single rule
pytest --flext-enforce-exclude-rules=ENFORCE-013
pytest --no-flext-enforce                   # force-disable
pytest flext-core/                          # sub-project — no-op
```

Items appear in collection under `flext-enforcement::ENFORCE-NNN[project]`. A terminal summary prints the active rule count grouped by source kind plus the runtime warning tally.

## Adding a rule

1. Identify the origin layer (detector, validator, warning, ast-grep, ruff, narrative).
2. In `flext-core/src/flext_core/_constants/enforcement.py` append a `_me.EnforcementRuleSpec(...)` inside `_hydrate_enforcement_catalog()` with a fresh `ENFORCE-NNN` ID (monotonic, do not reuse retired IDs).
3. For `flext_infra_detector`: the `violation_field` must match an existing attribute on `m.Infra.ProjectEnforcementReport`. No detector code changes.
4. For `flext_tests_validator`: the `method` must be one of `imports`, `types`, `bypass`, `layer`, `tests`, `validate_config`, `markdown`; `rule_ids` filters the validator's internal IDs.
5. For `runtime_warning`: `category` is a dotted class path; pytest will register a `filterwarnings` line automatically.
6. For `ast_grep`: `skill + rule_id` must resolve to an entry in `.agents/skills/<skill>/rules.yml`.
7. For `beartype`: `hook` must name a `check_<tag>` static method on `FlextUtilitiesBeartypeEngine`; the same `<tag>` must be registered in `c.ENFORCEMENT_RULES` and routed by an arm in `FlextUtilitiesEnforcementCollect._namespace_items`. Detection sentinels (regexes / path markers / builtin-name sets) live as `Final` class attributes on `FlextConstantsEnforcement` (never as loose module-level constants on `beartype_engine.py`).
8. Run `pytest flext-core/tests/ -k enforcement_catalog` to validate the catalog.

## Retiring a rule

Set `enabled=False`. Leave the entry in place with a `notes=` marker for at least one release cycle so the ID stays stable for tooling.

## Canonical IDs (summary)

- `ENFORCE-001..014` — flext-infra detectors, one per `ProjectEnforcementReport` field.
- `ENFORCE-015..021` — flext-tests validators, one per `tv.*` method.
- `ENFORCE-022` — `FlextMroViolation` runtime warning.
- `ENFORCE-023..025` — ruff (`ANN401`, `PGH003`, `TID252`).
- `ENFORCE-026..033` — ast-grep cross-references (`flext-patterns`, `flext-strict-typing`).
- `ENFORCE-034..038` — skill pointers (accessor methods, settings inheritance, `model_rebuild`, `os.environ` ban, flat-alias ban).
- `ENFORCE-039..044` + `ENFORCE-054` — beartype runtime hooks + ruff delegation (`cast_outside_core`, `PGH003`, `model_rebuild_call`, `settings_inheritance` (reuses existing hook), `pass_through_wrapper`, `private_attr_probe`, `no_core_tests_namespace`).

For the live set call `len(c.ENFORCEMENT_CATALOG.rules)` — the docs above are a snapshot, not an SSOT.
