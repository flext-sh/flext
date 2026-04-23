# flext-infra Canonical Namespace Standardization

**Date**: 2026-04-06
**Scope**: flext-infra/src/flext_infra/ (295 .py files)
**Goal**: Zero loose declarations — all code inside c/t/p/m/u namespace hierarchy

## Current State

Facades are well-structured (c, m, t, u, p all exist with proper MRO from FlextCli*).
Violations are in **3 categories** across **14 files**:

## Violations Inventory

### Wave 1 — Constants (23 items)

**A. Cached aliases from c.Infra.* (8 items) — DELETE, use c.Infra.* directly:**

| File                                             | Alias                                          | SSOT                                                         |
| ------------------------------------------------ | ---------------------------------------------- | ------------------------------------------------------------ |
| `detectors/loose_object_detector.py:25`          | `_CONSTANT_RE`                                 | `c.Infra.NAMESPACE_CONSTANT_PATTERN`                         |
| `detectors/loose_object_detector.py:32`          | `_FUNC_DEF_RE`                                 | `c.Infra.FUNC_DEF_RE`                                        |
| `detectors/loose_object_detector.py:33`          | `_ASSIGN_RE`                                   | `c.Infra.ASSIGN_RE`                                          |
| `detectors/loose_object_detector.py:34`          | `_TYPE_ALIAS_RE`                               | `c.Infra.PEP695_RE`                                          |
| `detectors/manual_typing_alias_detector.py:13`   | `_PEP695_RE`                                   | `c.Infra.PEP695_RE`                                          |
| `detectors/manual_typing_alias_detector.py:14`   | `_TYPEALIAS_ANNOT_RE`                          | `c.Infra.TYPEALIAS_ANNOT_RE`                                 |
| `detectors/manual_typing_alias_detector.py:15`   | `_TYPEALIAS_ASSIGN_RE`                         | `c.Infra.TYPING_FACTORY_ASSIGN_RE`                           |
| `detectors/future_annotations_detector.py:13-14` | `_FUTURE_ANNOTATIONS_RE`, `_ONLY_DOCSTRING_RE` | `c.Infra.FUTURE_ANNOTATIONS_RE`, `c.Infra.ONLY_DOCSTRING_RE` |

**B. Constants needing absorption into c.Infra.* (15 items):**

| File                                       | Name                        | Target Class                                                   |
| ------------------------------------------ | --------------------------- | -------------------------------------------------------------- |
| `base.py:35`                               | `APPLY_OPTION_DECLS`        | `c.Infra.Cli.APPLY_OPTION_DECLS`                               |
| `_utilities/codegen_constants.py:43`       | `_LINT_TOOLS`               | `c.Infra.Codegen.LINT_TOOLS`                                   |
| `_utilities/codegen_constants.py:50`       | `_TRIVIAL_VALUES`           | `c.Infra.Codegen.TRIVIAL_VALUES`                               |
| `_utilities/codegen_constants.py:66-72`    | `_FINAL_DECL_RE` + 3 regex  | `c.Infra.Codegen.FINAL_DECL_RE` etc.                           |
| `_utilities/codegen_constants.py:73`       | `_DEFAULT_EXCLUDE`          | `c.Infra.Codegen.DEFAULT_EXCLUDE`                              |
| `_utilities/codegen_execution.py:28`       | `_BARE_IMPORT_FROM_RE`      | `c.Infra.Codegen.BARE_IMPORT_FROM_RE`                          |
| `_utilities/codegen_execution.py:29`       | `_NO_MODIFIED`              | `c.Infra.Codegen.NO_MODIFIED_RESULT`                           |
| `_utilities/codegen_constants.py:104`      | `_MIN_QUOTED_LEN`           | `c.Infra.Codegen.MIN_QUOTED_LEN`                               |
| `transformers/class_reconstructor.py:14`   | `_MIN_METHODS_FOR_REORDER`  | `c.Infra.Refactor.MIN_METHODS_FOR_REORDER`                     |
| `workspace/workspace_makefile.py:36-41`    | `_TEMPLATE_NAME` + 3        | `c.Infra.Workspace.TEMPLATE_NAME` etc.                         |
| `basemk/engine.py:20`                      | `_TEMPLATES_DIR`            | `c.Infra.BaseMk.TEMPLATES_DIR`                                 |
| `codegen/codegen_generation.py:27-29`      | `_TEMPLATE_ROOT`, `_ENV`    | `c.Infra.Codegen.TEMPLATE_ROOT` (env stays as u.PrivateAttr) |
| `detectors/loose_object_detector.py:26-30` | `_ALLOWED_TOP_LEVEL`        | `c.Infra.Scan.ALLOWED_TOP_LEVEL`                               |
| `refactor/migrate_to_class_mro.py:18`      | `_ROPE_MODULE_SYNTAX_ERROR` | `c.Infra.Rope.MODULE_SYNTAX_ERROR`                             |

### Wave 2 — Types (11 inline annotations)

**A. SSOT dedup — already exists in parent chain:**

| flext-infra current                                                              | SSOT replacement                            |                                     |
| -------------------------------------------------------------------------------- | ------------------------------------------- | ----------------------------------- |
| `t.Infra.StrPair`                                                                | Already OK (unique to infra)                |                                     |
| `t.Infra.StrPairSequence`                                                        | Already OK                                  |                                     |
| Inline `list[str]` in `base.py:35`                                               | Use `t.StrSequence`                         |                                     |
| Inline `dict[str, object]` in `__version__.py`                                   | Use `Mapping[str, object]`                  |                                     |
| Inline `dict[str, str]` in `__version__.py`                                      | Use `t.StrMapping`                          |                                     |
| Inline `Callable[[t.StrSequence \                                                | None], int]` in `cli.py:78`                 | Define `t.Infra.CliCommandCallable` |
| Inline `Callable[[t.Cli.CliApp], None]` in `cli.py:90`                           | Define `t.Infra.CliSetupCallable`           |                                     |
| Inline `dict[str, t.Infra.InfraValue]` in codegen_execution.py                   | Define `t.Infra.InfraValueMapping`          |                                     |
| Inline `Mapping[str, MutableSequence[t.Infra.StrPair]]` in codegen_generation.py | Define `t.Infra.StrPairGroupMapping`        |                                     |
| Inline `MutableMapping[str, MutableSequence[t.Infra.StrPair]]`                   | Define `t.Infra.MutableStrPairGroupMapping` |                                     |

### Wave 3 — Functions (26 items)

**A. Dead code — DELETE:**

| File                        | Function              | Evidence        |
| --------------------------- | --------------------- | --------------- |
| `models/refactor.py:23-24` | `_class_moves()`      | Zero references |
| `models/refactor.py:27-28` | `_alias_moves()`      | Zero references |
| `models/docs.py:15-16`     | `_docs_phase_items()` | Zero references |

**B. default_factory → @staticmethod on model class:**

| File                    | Function               | Model          |
| ----------------------- | ---------------------- | -------------- |
| `models/codegen.py:18` | `_census_violations()` | `CensusReport` |
| `models/release.py:14` | `_build_records()`     | `BuildReport`  |
| `models/scan.py:20`    | `_scan_violations()`   | `ScanResult`   |

Pattern: `default_factory=list` (simpler, Pydantic-idiomatic)

**C. Helper functions → @staticmethod or u.Infra.*:**

| File                                     | Function                                    | Target                                                           |
| ---------------------------------------- | ------------------------------------------- | ---------------------------------------------------------------- |
| `__version__.py:21-31`                   | `_is_object_mapping`, `_is_object_sequence` | SSOT: `u.Guards.mapping()`, `u.Guards.is_list()` from flext-core |
| `__version__.py:34-48`                   | `_object_mapping`, `_object_sequence`       | `@staticmethod` on `FlextInfraVersion`                           |
| `__version__.py:51-71`                   | `_pyproject_metadata`                       | `@staticmethod` on `FlextInfraVersion`                           |
| `__version__.py:74-79`                   | `_load_metadata`                            | `@staticmethod` on `FlextInfraVersion`                           |
| `basemk/engine.py:23-32`                 | `_build_environment`                        | `u.PrivateAttr(default_factory=...)` pattern                   |
| `basemk/engine.py:35-38`                 | `_render`                                   | `@staticmethod` on engine class                                  |
| `api.py:34-37`                           | `_load`                                     | `@staticmethod` on `FlextInfra`                                  |
| `_utilities/codegen_constants.py:79-166` | 7 helper functions                          | `@staticmethod` on `FlextInfraUtilitiesCodegenConstantDetection` |
| `_utilities/codegen_execution.py:36-41`  | `_int`, `_totals`                           | `@staticmethod` on `FlextInfraUtilitiesCodegenExecution`         |
| `_utilities/docs_render.py:12`           | `_is_object_list`                           | SSOT: `u.Guards.is_list()` from flext-core                       |

### Wave 4 — Protocol (1 item)

| File                     | Class                   | Target                                       |
| ------------------------ | ----------------------- | -------------------------------------------- |
| `basemk/engine.py:35-39` | `_Renderable(Protocol)` | `p.Infra.Renderable` in `_protocols/base.py` |

### Wave 5 — Call site updates

All references to removed/moved symbols updated via ast-grep or Edit.

### Wave 6 — Validation

- `ruff check src/ tests/` — zero errors
- `pyrefly check src/ tests/` — zero errors

## SSOT Rules Applied

1. If equivalent exists in flext-core → DELETE local, use `u.*`/`c.*`/`t.*` from core
2. If equivalent exists in flext-cli → DELETE local, use from cli chain (inherited via MRO)
3. If equivalent exists elsewhere in flext-infra → DELETE duplicate, use existing
4. If unique to module → absorb into nearest namespace class
5. Dead code → DELETE unconditionally

## Non-Goals

- No changes to flext-core or flext-cli
- No changes to tests/ (unless call sites break)
- No changes to `__init__.py` auto-generated exports
- No functional behavior changes
