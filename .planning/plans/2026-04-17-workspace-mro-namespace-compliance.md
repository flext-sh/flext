# Plan: Workspace-wide MRO + Namespace Compliance (35 projects)

**Objective:** Apply the canonical MRO pattern proven in the `flext-ldif` dirty diff to every `typings.py`, `models.py`, `protocols.py`, `utilities.py`, `constants.py` in all 35 FLEXT projects. Eliminate every enforcement `UserWarning` and every pyrefly/ruff diagnostic triggered by non-canonical inheritance / import shapes. After each edit, re-run `ruff check` and `pyrefly check` — if either fails, the root cause may be in the upstream project we import from; fix that FIRST.

## Canonical pattern — extracted from `git diff flext-ldif`

The user's fix in `flext-ldif` (uncommitted diff) reveals the single authoritative shape.

### Pattern A — single-parent project (1 upstream domain)

Example: `flext-ldif` inherits only from `flext-cli`.

```python
# flext-ldif/src/flext_ldif/typings.py
from flext_cli import t  # ← alias only; never FlextCliTypes
from flext_ldif import FlextLdifTypesBase, FlextLdifTypesDomain


class FlextLdifTypes(t):  # ← single base = alias
    """LDIF domain types extending flext-core FlextTypes."""

    # no redundant `class Cli(FlextCliTypes.Cli):` — MRO already exposes it

    class Ldif(FlextLdifTypesDomain, FlextLdifTypesBase):
        """LDIF-specific type namespace."""


t = FlextLdifTypes
__all__: list[str] = ["FlextLdifTypes", "t"]
```

### Pattern B — multi-parent project (≥2 peer upstream domains)

Example: `flext-quality` needs both `flext-cli` (Cli namespace, adapters) AND `flext-web` (Web namespace).

```python
# flext-quality/src/flext_quality/typings.py
from flext_cli import m, t  # ← alias-first imports
from flext_web import FlextWebTypes  # ← concrete class for second parent


class FlextQualityTypes(t, FlextWebTypes):  # ← alias FIRST, then Web
    """Namespace for flext-quality type definitions."""

    # All t.* / m.* refs resolve via MRO; never touch FlextCliTypes / FlextTypes directly
    CONTAINER_MAPPING_ADAPTER: m.TypeAdapter[t.ContainerMapping] = m.TypeAdapter(
        t.ContainerMapping,
    )


t = FlextQualityTypes
__all__: list[str] = ["FlextQualityTypes", "t"]
```

**Why alias-first in Pattern B?** `t` (from `flext_cli`) is `FlextCliTypes`, and `FlextWebTypes` is a peer (not parent). Placing `t` first makes the MRO resolve `t.ContainerMapping`-style lookups against `FlextCliTypes` before traversing into `FlextWebTypes`. Inverted order can raise C3-linearization errors when both bases reach `FlextCoreTypes` through different chains.

### `utilities.py` — special case (R10)

`u`, `m`, `c`, `t`, `p` are rebound at module bottom (`u = FlextXxxUtilities`). If `utilities.py` has a nested `@staticmethod` whose body reads `u.try_(...)`, the name `u` resolves at call time to the **rebound** value (`FlextXxxUtilities`) — which still works via MRO since `FlextXxxUtilities(u_parent)` inherits `try_`. However, **pyrefly struggles** to statically type an alias that is both a base-class argument and a module-level rebound name.

Canonical solution for `utilities.py`: use **explicit class name** for the second base when methods self-reference:

```python
from flext_cli import FlextCliUtilities  # ← explicit, avoids alias ambiguity
from flext_web import FlextWebUtilities


class FlextQualityUtilities(FlextCliUtilities, FlextWebUtilities):
    class Quality:
        @staticmethod
        def read_stdin() -> p.Result[str]:
            return u.try_(...)  # ← `u` here = rebound alias, resolves via MRO


u = FlextQualityUtilities
```

For the other four files (`typings.py`, `models.py`, `protocols.py`, `constants.py`), the alias-as-base form is preferred:

```python
from flext_cli import m, u  # alias imports


class FlextQualityModels(m, FlextWebModels):  # alias as base
    class Quality:
        class HookConfig(m.BaseModel): ...  # m = FlextCliModels at class-body time


m = FlextQualityModels  # rebind
```

## Rules encoded in the pattern (R1 – R10)

| # | Rule | Violation | Fix |
|---|---|---|---|
| **R1** | Import only ALIASES from immediate parent (`c, m, p, t, u, r, s`). For multi-parent Pattern B, also import the concrete `FlextXxxYYY` class of the second parent | `from flext_core import FlextTypes` in a flext-cli consumer | `from flext_cli import t` (A); `from flext_cli import t` + `from flext_web import FlextWebTypes` (B) |
| **R2** | NEVER import `BaseModel / Field / ConfigDict / TypeAdapter / model_validator / field_validator / computed_field / PrivateAttr` from `pydantic` in consumers | `from pydantic import BaseModel, ConfigDict` | `m.BaseModel`, `u.Field`, `m.ConfigDict`, `m.TypeAdapter`, `u.model_validator`, `u.field_validator`, `u.computed_field`, `u.PrivateAttr` |
| **R3** | NEVER reference `FlextCoreTypes / FlextCliTypes / FlextCliModels / FlextCliProtocols / FlextCliUtilities / FlextCliConstants` directly in class-body type expressions | `FlextTypes.ContainerMapping` | `t.ContainerMapping` |
| **R4** | Single-parent projects: class base = single alias (Pattern A) | `class FlextLdifTypes(FlextCliTypes):` | `class FlextLdifTypes(t):` |
| **R5** | Multi-parent projects: class bases = (alias, ConcreteParentB) — alias FIRST (Pattern B) | `class FlextQualityTypes(FlextWebTypes, FlextCliTypes):` | `class FlextQualityTypes(t, FlextWebTypes):` |
| **R6** | Rebind alias at module bottom | missing last line | `t = FlextXxxTypes` at end |
| **R7** | `typings.py` / `models.py` / `protocols.py` / `constants.py` must NOT import from own package root (breaks lazy init) | `from flext_quality import m` in typings.py | `from flext_cli import m` (from parent) |
| **R8** | Drop redundant inner namespace re-inheritance | `class Cli(FlextCliTypes.Cli):` with empty body | remove — MRO exposes it |
| **R9** | Sibling `_models/*.py` references used only in annotations go under `TYPE_CHECKING`; direct runtime base classes stay at top | `from flext_ldif import FlextLdifModelsDomainMetadata` used only in `Annotated[...]` | `if TYPE_CHECKING: from flext_ldif import FlextLdifModelsDomainMetadata` |
| **R10** | `utilities.py` with self-referencing methods uses **explicit class** base for the first parent, not the alias | `class FlextQualityUtilities(u, FlextWebUtilities):` with `u.try_()` in body | `class FlextQualityUtilities(FlextCliUtilities, FlextWebUtilities):` |

## Enforcement rule additions to `flext-core/_utilities/enforcement.py`

Current checks (lines 62–990): `check_no_any`, `check_no_bare_collections`, `check_no_v1_patterns`, `check_field_descriptions`, `check_extra_policy`, `check_no_object`, `check_no_str_none_with_empty_default`, `check_frozen_value_objects`, `check_no_mutable_field_defaults`, `check_no_inline_union_types`, `check_protocols_inner_classes`, `check_protocols_runtime_checkable`, `check_inner_namespace`, `_scan_cross_layer_recursive`.

### 10 new static checks to add (encoding R1–R10)

| Check name | Encoded rule | Detection strategy |
|---|---|---|
| `check_no_concrete_namespace_import` | R1, R3 | AST-scan: `ImportFrom` where `module.startswith("flext_")` and any alias name matches `^Flext(Core\|Cli\|Web\|Meltano\|...)(Constants\|Models\|Protocols\|Types\|Utilities)$`; exempt canonical-files that legitimately need the concrete class (Pattern-B `utilities.py` via R10 whitelist) |
| `check_no_pydantic_consumer_import` | R2 | AST-scan: `ImportFrom` where `module == "pydantic"` and alias name in `{BaseModel, Field, ConfigDict, TypeAdapter, field_validator, model_validator, computed_field, PrivateAttr, AfterValidator, BeforeValidator}` and current module is NOT in `c.ENFORCEMENT_PYDANTIC_ALLOWED_MODULES` |
| `check_facade_base_is_alias_or_peer` | R4, R5 | Inspect `target.__bases__`: must be `(<alias>,)` for Pattern A, or `(<alias>, FlextPeerXxx)` for Pattern B — reject concrete `FlextCliXxx` in position 0 |
| `check_alias_first_multi_parent` | R5 | `len(bases) > 1` → first base must be a runtime alias (identity match with parent package's alias) |
| `check_alias_rebound_at_module_end` | R6 | Walk module AST: final `Assign` node must bind the expected alias (`t = FlextXxxTypes` etc.) |
| `check_no_redundant_inner_namespace` | R8 | Inner class with same name as parent's namespace + empty body or pure-pass body |
| `check_no_self_root_import_in_core_files` | R7 | In the 5 canonical files, reject `ImportFrom` where `module == own_package` AND alias name in `{c, m, p, t, u, r, s}` |
| `check_sibling_models_type_checking` | R9 | In `_models/*.py`: gather all `Import` usages; cross-reference against `Annotated[...]` positions; annotation-only usages must come from `TYPE_CHECKING` block |
| `check_utilities_explicit_class_when_self_ref` | R10 | `utilities.py`: if body contains `<alias>.<name>(...)` call AND class base list includes the alias → warn |
| `check_no_raw_collections_field_default` | (existing pattern extended) | `u.Field(default_factory=dict)` / `=list` / `=set` without typed callable |

### Improvements to existing checks

- **`check_inner_namespace`** (line 902): emit a fix-it hint with the exact required rename (e.g., `Inner class "AppConfigDict" must be named "Web"; wrap it: class Web: class AppConfigDict: ...`).
- **`check_protocols_inner_classes`** (line 568): add path-aware exemption for `Tests.*` protocol unions used only in test fixtures.
- **`check_field_descriptions`** (line 114): include the full module path + field name in the warning; currently only class qualname.
- **`check_no_v1_patterns`** (line 99): extend to call-site `.dict()` / `.json()` via ast-grep (not only class `Config:` declarations).

### Governance infrastructure

- Add `FlextMroViolation(UserWarning)` subclass in `flext-core/_utilities/enforcement.py`.
- Route all R1–R10 emissions through `FlextMroViolation` so CI can use `python -W error::FlextMroViolation` to fail distinctly from generic pydantic warnings.
- Add constants under `FlextConstantsEnforcement`:
  - `ENFORCEMENT_PYDANTIC_ALLOWED_MODULES` — whitelist (`{"flext_core._models.pydantic", ...}`)
  - `ENFORCEMENT_CANONICAL_FILES` — `{"typings.py", "models.py", "protocols.py", "utilities.py", "constants.py"}`
  - `ENFORCEMENT_MRO_ALIAS_MAP` — parent package → expected alias set
  - `ENFORCEMENT_PATTERN_B_UTILITIES_WHITELIST` — projects that legitimately use R10 explicit-class form in utilities.py

## Project pattern map

| Project | Immediate parent | Pattern | Notes |
|---|---|---|---|
| flext-core | — | — | canonical base — no changes needed |
| flext-cli | flext-core | A | parent for most |
| flext-web | flext-core | A | parent for flext-quality |
| flext-meltano | flext-cli | A | parent for 10 projects |
| flext-api | flext-cli | A | |
| flext-auth | flext-cli | A | |
| flext-grpc | flext-cli | A | |
| flext-infra | flext-cli | A | already uses MRO mixin pattern for CLI groups |
| flext-tests | flext-cli | A | |
| flext-plugin | flext-cli | A | |
| flext-observability | flext-cli | A | |
| flext-ldap | flext-cli | A | **reference (dirty diff)** |
| flext-ldif | flext-cli | A | **reference (dirty diff)** |
| flext-db-oracle | flext-cli | A | |
| flext-oracle-oic | flext-cli | A | |
| flext-oracle-wms | flext-cli | A | |
| flext-quality | flext-cli + flext-web | **B** | typings/models/protocols/constants use alias-first form; utilities uses R10 explicit class |
| flext-tap-ldap | flext-meltano | A | |
| flext-tap-ldif | flext-meltano | A | |
| flext-tap-oracle | flext-meltano | A | |
| flext-tap-oracle-oic | flext-meltano | A | |
| flext-tap-oracle-wms | flext-meltano | A | |
| flext-target-ldap | flext-meltano | A | |
| flext-target-ldif | flext-meltano | A | |
| flext-target-oracle | flext-meltano | A | |
| flext-target-oracle-oic | flext-meltano | A | |
| flext-target-oracle-wms | flext-meltano | A | |
| flext-dbt-ldap | flext-meltano | A | |
| flext-dbt-ldif | flext-meltano | A | |
| flext-dbt-oracle | flext-meltano | A | |
| flext-dbt-oracle-wms | flext-meltano | A | |
| algar-oud-mig | flext-ldap | A | |
| gruponos-meltano-native | flext-meltano | A | |

## Validation contract (after EVERY file edit)

**User's explicit rule:** _"ao alterar codigo, sempre valide o impacto e funcionamento com ruff e pyrefly, se falhar significa que temos problemas e que pode ser até no projeto que estamos importando que precisa ser corrigido primeiro."_

```bash
ruff check <edited-file>              # must be 0 errors
pyrefly check <edited-file>           # must be 0 errors
```

Failure-handling protocol:

1. Read the exact error message.
2. If the error mentions upstream symbols (`FlextCliTypes has no attribute X`, `FlextWebUtilities has no class attribute Cli`), the upstream project is incomplete or diverged from the pattern.
3. Fix the upstream project FIRST using the same canonical pattern — do NOT patch the downstream file to work around the upstream gap.
4. Re-validate the upstream until green.
5. Return to the current file and re-validate.

Never suppress, never downgrade the pattern to silence pyrefly — suppression hides the real architectural gap.

## Execution phases

### Phase 0 — baseline audit

Build an ast-grep rule file that encodes R1–R10 and emit a workspace violation count per project per canonical file:

```bash
cd /home/marlonsc/flext
ast-grep scan --rule .ast-grep/rules/mro-r1-r10.yml --json | \
  jq 'group_by(.file) | map({file: .[0].file, count: length})' > /tmp/mro-baseline.json
```

Sort ascending — fix projects with fewest violations first to build confidence.

### Phase 1 — upstream first: enforcement checks in flext-core

Land the 10 new checks + `FlextMroViolation` class + the 4 new constants in `flext-core/_utilities/enforcement.py` + `FlextConstantsEnforcement`.

After each new check:

```bash
cd flext-core
ruff check src/ tests/
pyrefly check src/ tests/
pytest tests/ --timeout=60
```

No downstream project is touched until flext-core is green with the new enforcement.

### Phase 2 — dependency-ordered rollout

1. **flext-cli, flext-web** (roots for the two domain stacks)
2. **flext-meltano** (parent of 10 projects)
3. **flext-ldap** (parent of algar-oud-mig)
4. **Leaf Pattern-A projects** — batch of 3-5 in parallel:
   - flext-ldif, flext-infra, flext-tests, flext-api, flext-auth, flext-grpc, flext-plugin, flext-observability, flext-db-oracle, flext-oracle-oic, flext-oracle-wms
5. **flext-quality** (Pattern B — only after flext-cli + flext-web done)
6. **Meltano children** (10 projects) — parallel
7. **algar-oud-mig, gruponos-meltano-native**

Per project, sequential within one commit:

```text
typings.py → constants.py → protocols.py → models.py → utilities.py (R10)
→ python -m flext_infra codegen lazy-init --apply
→ ruff + pyrefly + pytest  (must be green)
→ git commit
```

### Phase 3 — cascade consumer updates for inner-namespace renames

When fixing `flext-web` places inner classes under a `Web` namespace (`class FlextWebTypes.Web.HttpMessage` instead of `class FlextWebTypes.HttpMessage`), every downstream consumer that used the flat form must move. Do this in the same commit that renames.

```bash
# find all consumer call-sites of the old flat name
for proj in flext-* algar-* gruponos-*; do
  [ -d "$proj/src" ] || continue
  grep -rn "FlextWebTypes\.\(HttpMessage\|HttpRequest\|HttpResponse\|AppData\|Project\)" "$proj/src" 2>/dev/null
done
```

Bump minor version of the consumer project.

### Phase 4 — workspace verification

```bash
cd /home/marlonsc/flext
ruff check . --exclude='.venv,node_modules,.git'            # 0
for proj in flext-* algar-* gruponos-*; do
  [ -d "$proj/src" ] || continue
  (cd "$proj" && pyrefly check src/ tests/ 2>&1 | grep -i error) && \
    echo "BLOCKED: $proj has pyrefly errors"
done

# Fail on FlextMroViolation
for proj in flext-* algar-* gruponos-*; do
  pkg=$(echo "$proj" | tr - _)
  python -W error::FlextMroViolation -c "import $pkg" 2>&1 | head -3
done
```

## Done criteria

- Every canonical file (`typings.py / models.py / protocols.py / utilities.py / constants.py`) in every project matches Pattern A or Pattern B per the project map.
- `flext-core/_utilities/enforcement.py` has all 10 new checks + `FlextMroViolation(UserWarning)` + whitelist constants.
- `ruff check .` workspace-wide: 0.
- `pyrefly check src/ tests/` per project: 0.
- `python -W error::FlextMroViolation -c "import <pkg>"` per project: silent.
- `pytest` per project: green.
- One atomic commit per project with message `refactor(<project>): normalize to canonical MRO pattern <A|B>`.
