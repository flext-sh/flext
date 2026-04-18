# Audit: gruponos-meltano-native — architectural violations (2026-04-17)

**Scope:** Comprehensive audit of `gruponos-meltano-native/src/gruponos_meltano_native/` against the canonical MRO pattern (R1–R10) extracted from the `flext-ldif` dirty diff.

**Static gates baseline:** `ruff check src/` → clean. `pyrefly check src/` → 0 errors. Warnings-as-errors: empty. Architectural violations below are **invisible** to current gates — confirmed need for the new enforcement checks in the plan.

## Finding 1 — **FATAL: duplicated class `GruponosMeltanoNativeModels`**

Two files define the same class name with incompatible shapes:

| File | Parent | Shape | Used by |
|---|---|---|---|
| [src/gruponos_meltano_native/models.py](gruponos-meltano-native/src/gruponos_meltano_native/models.py) | `flext_tap_oracle` + `flext_target_oracle_wms` (Pattern B) | `class GruponosMeltanoNativeModels(m, FlextTargetOracleWmsModels)` with a single nested `GruponosMeltanoNative.AlertSettingsConfig` | — |
| [src/gruponos_meltano_native/models/pipeline.py](gruponos-meltano-native/src/gruponos_meltano_native/models/pipeline.py) | `flext_meltano` (Pattern A) | `class GruponosMeltanoNativeModels(m)` with 12+ nested `PipelineResult`, `PipelineConfig`, `PipelineExecution`, … | `__init__.py` lazy map |

**Which one wins?** The lazy `__init__.py` (line 43) binds `GruponosMeltanoNativeModels` to `models/pipeline.py`. The root `models.py` is dead code — never exported, never imported by anyone.

**Recommended action:**

1. Merge `models.py`'s `AlertSettingsConfig` into `models/pipeline.py`'s nested namespace.
2. Decide canonical parent: the pipeline-side (`flext_meltano`) is correct; the `flext_tap_oracle + flext_target_oracle_wms` combination in `models.py` is incoherent (gruponos is a **native** meltano project, not a tap/target).
3. Delete `models.py` (archive to `.bak`).

## Finding 2 — `_cli_main.py` is dead code, not a CLI

[_cli_main.py](gruponos-meltano-native/src/gruponos_meltano_native/_cli_main.py) (306 lines) claims to be the CLI entry point but:

- Has ad-hoc nested `_HealthHandler`, `_RunHandler`, `_ListHandler`, `_ValidateHandler`, `_ShowConfigHandler`, `_RunWithRetryHandler` classes — none follow the canonical `s[T]` Pydantic-service pattern (cf. `flext-infra/codegen/cli.py`, `algar-oud-mig/cli.py`).
- `cli()` method line 230: returns `0` after calling `create_gruponos_cli()` which just builds a placeholder dict — **no subcommand dispatch happens**.
- `create_gruponos_cli()` line 278: logs and returns `r[t.StrMapping].ok({"framework": "flext-cli", "status": "initialized"})` — does nothing.
- `_initialize_cli_environment()` line 254: accepts `debug` flag but only returns `{"debug": debug, "initialized": True}` — unused.
- Local `GruponosCliOrchestrator(Protocol)` at line 28 — should live in `protocols.py` under the `GruponosMeltanoNative` namespace per canonical rules.
- No integration with `cli.create_app_with_common_params` / `cli.register_result_routes` / `cli.execute_app`.
- `__name__ == "__main__"` at bottom calls `cli()` which does nothing useful.

**Also note:** the root `__init__.py` lazy map (line 149) already exports proper handlers from `gruponos_meltano_native.cli.handlers.{health, list_pipelines, run, run_with_retry, show_config, validate}` — so there's a parallel proper CLI structure in `cli/handlers/` that `_cli_main.py` completely ignores.

**Recommended action:**

1. Delete `_cli_main.py` (archive to `.bak`).
2. Create canonical `cli.py` at project root following `algar-oud-mig/cli.py` pattern: `FlextInfraCli`-style root router with `cli.register_result_routes` using the nested Pydantic services.
3. Move `GruponosCliOrchestrator(Protocol)` into `protocols.py` under `GruponosMeltanoNativeProtocols.GruponosMeltanoNative`.
4. Wire the existing `cli/handlers/` classes as Pydantic input models (or replace with nested `s[T]` services like the flext-quality Cli / Check / Validate pattern).

## Finding 3 — `_models.py` classes at module level (R3 + R-inner-namespace violation)

[_models.py](gruponos-meltano-native/src/gruponos_meltano_native/_models.py) declares 5 classes at MODULE LEVEL (not inside the `GruponosMeltanoNativeModels.GruponosMeltanoNative` namespace):

```python
class AlertConfigDict(m.BaseModel): ...


class JobConfigDict(m.BaseModel): ...


class OracleConnectionConfigDict(m.BaseModel): ...


class TargetOracleConfigDict(m.BaseModel): ...


class WMSSourceConfigDict(m.BaseModel): ...
```

- File name starts with `_` (private) but exports via `__all__` — contradictory.
- Violates **R8/R-inner-namespace**: all project-owned Pydantic models must live under `class <Namespace>:` inside the `FlextXxxModels` facade.
- Imported by `settings.py` line 29 via relative import `from ._models import ...`.
- Fields like `webhook_url: str | None = None`, `host: str | None = None`, `port: int = 1521` — **no `description="..."`** on any field. Violates existing `check_field_descriptions` enforcement but no warning emitted because `FlextUtilitiesEnforcement` only walks `m.BaseModel` subclasses when their module matches `FlextConstantsEnforcement.ENFORCEMENT_MODULE_FRAGMENTS`. The private `_models.py` dodges the check.

**Recommended action:**

1. Move all 5 classes into `models/pipeline.py` (after merging `models.py` per Finding 1) under a new nested namespace `GruponosMeltanoNativeModels.GruponosMeltanoNative.Settings` (or similar).
2. Add `description="..."` to every field.
3. Add `model_config: ClassVar[m.ConfigDict] = m.ConfigDict(extra="forbid", validate_assignment=True)`.
4. Update `settings.py:29-35` to reference via `m.GruponosMeltanoNative.Settings.AlertConfigDict`, etc.
5. Delete `_models.py`.

## Finding 4 — Inconsistent parent package across files (R1)

| File | Imports from |
|---|---|
| `typings.py` | `flext_tap_oracle` + `flext_target_oracle_wms` |
| `constants.py` | `flext_tap_oracle` + `flext_target_oracle_wms` |
| `protocols.py` | `flext_tap_oracle` + `flext_target_oracle_wms` |
| `utilities.py` | `flext_tap_oracle` + `flext_target_oracle_wms` |
| `models.py` (dead) | `flext_tap_oracle` + `flext_target_oracle_wms` |
| `models/pipeline.py` (live) | **`flext_meltano`** |
| `_cli_main.py` | `flext_core` + self |
| `_models.py` | self (`from gruponos_meltano_native import m, t`) |

gruponos-meltano-native is a **native meltano consumer** per the project name. Canonical parent should be `flext_meltano`. The `flext_tap_oracle + flext_target_oracle_wms` dual parent in the canonical files is wrong — that's the Pattern for a tap-target glue project, not native consumer.

**Recommended action:** standardize all canonical files to inherit from `flext_meltano` (Pattern A). If Oracle WMS domain types are needed, add `flext_oracle_wms` as the Pattern-B second parent — **not** the target/tap.

## Finding 5 — Lazy init cascading failures (R7) in upstream dependencies

Runtime `from gruponos_meltano_native import m` fails with:

```
ImportError: cannot import name 'm' from 'flext_target_oracle_wms'
  (… _utilities/helpers.py line 7: from flext_target_oracle_wms import c, m, p, r, t)
```

Chain:

1. gruponos root imports `m` → lazy-loads `models/pipeline.py`
2. pipeline.py imports `FlextTargetOracleWmsModels` → lazy-loads flext-target-oracle-wms root
3. flext-target-oracle-wms root transitively loads `_utilities/helpers.py`
4. helpers.py does `from flext_target_oracle_wms import c, m, p, r, t` — **but the root hasn't finished binding** `m` yet → `ImportError`

Partially fixed this session (at upstream):

- `flext_oracle_wms/typings.py` → moved `m` import from self to `flext_api` ✓
- `flext_target_oracle_wms/typings.py` → moved `m` import from self to `flext_meltano` ✓
- `_utilities/helpers.py` — **still cyclic**. `helpers.py` needs `t.NV_ADAPTER` (project-local) and `m.TargetOracleWms.*` (project-local). Parent package aliases don't expose these.

**Recommended action:**

1. Keep the canonical pattern of `from flext_target_oracle_wms import c, m, p, r, t` in `_utilities/*.py` (this pattern works in `flext-ldif/_utilities/entry.py`).
2. Investigate **why** gruponos's lazy chain triggers helpers.py BEFORE root binding completes. Likely cause: some class body in `models/pipeline.py` or similar calls `m.TargetOracleWms.helpers.xxx` at class-body evaluation time (not method call time), forcing eager helpers.py load.
3. Move any eager helpers.py access into `__init_subclass__` hooks or method bodies.

## Finding 6 — Subdirectory structure inconsistent with canonical pattern

| Directory | Purpose | Status |
|---|---|---|
| `cli/handlers/` | Proper CLI handler classes (lazy-exported) | ✓ Keep |
| `core/` | ExternalCommandResult, MeltanoPipelineExecutor | Keep (domain logic) |
| `models/` | Pipeline models | Keep, merge root `models.py` + `_models.py` contents here |
| `monitoring/` | Alert manager | Keep (domain logic) |
| `oracle/` | Connection manager | Keep (domain logic) |
| `validators/` | Data validator | Keep (domain logic) |

The `_cli_main.py` + `_models.py` are vestigial artifacts duplicating/competing with `cli/handlers/` and `models/pipeline.py`. Remove both.

## Finding 7 — Root `__init__.py` uses flext-core aliases directly (R1)

Lines 189-206:

```python
"d": ("flext_core.decorators", "FlextDecorators"),
"e": ("flext_core.exceptions", "FlextExceptions"),
"h": ("flext_core.handlers", "FlextHandlers"),
"r": ("flext_core.result", "FlextResult"),
"s": ("flext_core.service", "FlextService"),
"x": ("flext_core.mixins", "FlextMixins"),
```

Bypasses the immediate parent (`flext_meltano`, which already re-exports these via its own lazy map). Violates R1 — consumers must go through immediate parent.

**Recommended action:** regenerate `__init__.py` via `python -m flext_infra codegen lazy-init --apply` after fixing Finding 4 (parent standardization). The generator should then point `d/e/h/r/s/x` at `flext_meltano` automatically.

## Finding 8 — `models/__init__.py` identical R1 violation

Lines 16-25 of [models/**init**.py](gruponos-meltano-native/src/gruponos_meltano_native/models/__init__.py):

```python
from flext_core import FlextConstants as c
from flext_core import FlextDecorators as d

...
```

Should come from `flext_meltano` per R1 / R3. Same regeneration required.

## Finding 9 — `settings.py` direct pydantic imports (R2)

[settings.py](gruponos-meltano-native/src/gruponos_meltano_native/settings.py) lines 20-23:

```python
from pydantic import (
    SecretStr,
)
from pydantic_settings import SettingsConfigDict
```

R2 violation. `SecretStr` should come via `t.SecretStr`; `SettingsConfigDict` via `m.SettingsConfigDict`.

## Priority order for fixes

1. **Finding 5** (upstream cascade) — most critical, blocks runtime import. Fix upstream `_utilities/helpers.py` loading order.
2. **Finding 1** (duplicated class) — eliminate dead `models.py`.
3. **Finding 3** (`_models.py` at module level) — move into `models/pipeline.py` namespace, delete private file.
4. **Finding 2** (`_cli_main.py` dead code) — delete, build proper `cli.py` at root.
5. **Finding 4 + 7 + 8** (inconsistent parent) — standardize on `flext_meltano` and regenerate lazy init.
6. **Finding 6** (subdirectory cleanup) — remove vestigial private files after merges.
7. **Finding 9** (pydantic imports in settings) — replace with `m.*`/`t.*` accessors.

## Affected enforcement rules (from the master plan)

This audit validates the need for these new checks specified in [`.planning/plans/2026-04-17-workspace-mro-namespace-compliance.md`](.planning/plans/2026-04-17-workspace-mro-namespace-compliance.md):

| Plan rule | This audit's evidence |
|---|---|
| R1 (import aliases only, immediate parent) | Findings 4, 7, 8 |
| R2 (no raw pydantic imports) | Finding 9 |
| R3 (no concrete namespace class refs) | Finding 1 (`FlextTargetOracleWmsModels` direct) |
| R7 (no own-root import in canonical files) | Finding 5 (upstream) |
| R8 (no redundant inner namespace) | — |
| R9 (TYPE_CHECKING for sibling annotations) | Finding 5 suggests this may help unblock upstream |
| R10 (utilities.py: explicit class if self-ref) | — |
| `check_inner_namespace` (enforce single nested label) | Finding 3 (classes at module level, not under `GruponosMeltanoNative`) |
| `check_facade_base_is_alias_or_peer` | Finding 1, 4 |
| `check_no_duplicate_facade_class` (**NEW**) | Finding 1 |
| `check_no_dead_cli_file` (**NEW**) | Finding 2 |
| `check_no_private_module_level_models` (**NEW**) | Finding 3 |
| `check_canonical_parent_consistency` (**NEW**) | Finding 4 |

## Next-session recommendation

Do NOT attempt to fix gruponos-meltano-native piecemeal. The cascading upstream dependencies (flext-target-oracle-wms, flext-oracle-wms, flext-meltano) need auditing first per the master plan Phase 2 dependency-order rollout. After upstreams are canonical, gruponos becomes a mechanical regeneration + delete-dead-files exercise.
