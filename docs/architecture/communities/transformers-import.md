# transformers-import


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 169 nodes

- **Size**: 169 nodes
- **Cohesion**: 0.3028
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextInfraUtilitiesRopeImports | Class | flext-infra/src/flext_infra/_utilities/rope_imports.py | 16-900 |
| import_statements | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 20-24 |
| import_statement_module_name | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 27-35 |
| import_statement_names_and_aliases | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 38-48 |
| imported_module_paths | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 51-80 |
| find_occurrences | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 83-109 |
| location_file_path | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 112-121 |
| indexed_search_resources | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 124-170 |
| organize_imports | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 173-214 |
| normalize_imports | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 217-276 |
| _collect_canonical_alias_imports | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 279-332 |
| _referenced_runtime_aliases | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 335-356 |
| _ensure_canonical_alias_imports | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 359-441 |
| get_absolute_from_imports | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 444-462 |
| relocate_from_import_aliases | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 465-510 |
| _strip_aliases_from_source_imports | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 513-553 |
| _merge_aliases_into_target | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 556-592 |
| _uses_parenthesized_from_import | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 595-598 |
| _format_parenthesized_from_import | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 601-621 |
| collapse_submodule_alias_imports | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 624-686 |
| _persisted_import_block | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 689-706 |
| add_import | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 709-728 |
| remove_import_names | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 731-773 |
| rewrite_private_import_bypass_violations | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 776-852 |
| rewrite_foreign_canonical_alias_violations | Function | flext-infra/src/flext_infra/_utilities/rope_imports.py | 855-900 |
| FlextInfraTransformerFixerAdapter | Class | flext-infra/src/flext_infra/fixers/transformer_fixer.py | 39-421 |
| __init__ | Function | flext-infra/src/flext_infra/fixers/transformer_fixer.py | 48-50 |
| can_fix | Function | flext-infra/src/flext_infra/fixers/transformer_fixer.py | 110-115 |
| fix_project | Function | flext-infra/src/flext_infra/fixers/transformer_fixer.py | 118-192 |
| _is_owned_library_exempt | Function | flext-infra/src/flext_infra/fixers/transformer_fixer.py | 195-216 |
| _normalize_imports | Function | flext-infra/src/flext_infra/fixers/transformer_fixer.py | 218-229 |
| _fix_file | Function | flext-infra/src/flext_infra/fixers/transformer_fixer.py | 231-351 |
| _build_transformer | Function | flext-infra/src/flext_infra/fixers/transformer_fixer.py | 354-421 |
| FlextInfraCanonicalAliasGate | Class | flext-infra/src/flext_infra/gates/canonical_alias.py | 28-314 |
| _normalized_project_name | Function | flext-infra/src/flext_infra/gates/canonical_alias.py | 44-46 |
| _alias_files | Function | flext-infra/src/flext_infra/gates/canonical_alias.py | 49-69 |
| check | Function | flext-infra/src/flext_infra/gates/canonical_alias.py | 72-132 |
| fix | Function | flext-infra/src/flext_infra/gates/canonical_alias.py | 135-228 |
| _violation_files | Function | flext-infra/src/flext_infra/gates/canonical_alias.py | 231-255 |
| _plan_edits | Function | flext-infra/src/flext_infra/gates/canonical_alias.py | 258-283 |
| _format_files | Function | flext-infra/src/flext_infra/gates/canonical_alias.py | 286-300 |
| _fix_failure_result | Function | flext-infra/src/flext_infra/gates/canonical_alias.py | 302-314 |
| FlextInfraRefactorProjectAliasMigrator | Class | flext-infra/src/flext_infra/refactor/project_alias_migrator.py | 25-374 |
| _CstImportHelpers | Class | flext-infra/src/flext_infra/refactor/project_alias_migrator.py | 34-124 |
| dotted_name | Function | flext-infra/src/flext_infra/refactor/project_alias_migrator.py | 39-51 |
| import_aliases | Function | flext-infra/src/flext_infra/refactor/project_alias_migrator.py | 54-58 |
| make_import_alias | Function | flext-infra/src/flext_infra/refactor/project_alias_migrator.py | 61-68 |
| module_expression | Function | flext-infra/src/flext_infra/refactor/project_alias_migrator.py | 71-77 |
| insert_local_imports | Function | flext-infra/src/flext_infra/refactor/project_alias_migrator.py | 80-124 |
| _CollectExistingLocal | Class | flext-infra/src/flext_infra/refactor/project_alias_migrator.py | 145-181 |

*... and 119 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (177 edge(s))
- `isinstance` (36 edge(s))
- `append` (31 edge(s))
- `tuple` (26 edge(s))
- `len` (26 edge(s))
- `str` (26 edge(s))
- `frozenset` (23 edge(s))
- `get` (22 edge(s))
- `sorted` (14 edge(s))
- `apply_to_source` (13 edge(s))
- `join` (12 edge(s))
- `is_from_import` (11 edge(s))
- `set` (11 edge(s))
- `from_import` (10 edge(s))
- `read` (9 edge(s))

### Incoming

- `that` (177 edge(s))
- `apply_to_source` (12 edge(s))
- `len` (10 edge(s))
- `write_text` (8 edge(s))
- `flext-infra/src/flext_infra/fixers/transformer_fixer.py` (6 edge(s))
- `mkdir` (5 edge(s))
- `flext-infra/src/flext_infra/refactor/project_alias_migrator.py` (4 edge(s))
- `str` (4 edge(s))
- `flext-infra/tests/unit/transformers/test_infra_transformer_enforcement_fixers.py` (4 edge(s))
- `Path` (3 edge(s))
- `count` (3 edge(s))
- `flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py` (2 edge(s))
- `flext-infra/tests/unit/transformers/test_infra_transformer_cast_remover.py` (2 edge(s))
- `SimpleNamespace` (2 edge(s))
- `FixEnforcementCommand` (2 edge(s))
