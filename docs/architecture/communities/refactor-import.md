# refactor-import

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 34 nodes

- **Size**: 34 nodes
- **Cohesion**: 0.7716
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
| ------ | ------ | ------ | ------- |
| FlextInfraRefactorTypingUnificationRule | Class | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 13-26 |
| **init** | Function | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 14-15 |
| apply | Function | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 17-26 |
| TestsFlextInfraRefactorInfraRefactorTypingUnifier | Class | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 29-513 |
| test_converts_typealias_to_pep695 | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 32-47 |
| test_converts_multiple_aliases | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 49-69 |
| test_removes_dead_typealias_import | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 71-78 |
| test_removes_all_unused_typing_imports | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 80-87 |
| test_preserves_used_typing_imports | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 89-98 |
| test_replaces_primitives_union | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 100-117 |
| test_replaces_numeric_union | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 119-131 |
| test_replaces_scalar_union | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 133-146 |
| test_replaces_container_union | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 148-160 |
| test_injects_t_import_when_needed | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 162-169 |
| test_replaces_subset_union_with_none | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 171-179 |
| test_skips_definition_files | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 181-191 |
| test_preserves_non_matching_unions | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 193-202 |
| test_noop_clean_module | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 204-214 |
| test_preserves_used_imports_when_import_precedes_usage | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 216-231 |
| test_removes_unused_preserves_used_when_import_precedes_usage | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 233-245 |
| test_removes_all_imports_when_none_used_import_first | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 247-255 |
| test_typealias_conversion_preserves_used_typing_siblings | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 257-274 |
| test_preserves_type_checking_import | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 276-290 |
| test_preserves_protocol_and_runtime_checkable | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 292-307 |
| test_preserves_annotated_in_function_params | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 309-324 |
| test_preserves_override_in_method | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 326-342 |
| test_all_three_capabilities_in_one_pass | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 344-369 |
| test_no_duplicate_t_import_when_t_from_project_package | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 371-388 |
| test_preserves_typealias_import_when_class_level_usage_exists | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 390-406 |
| test_removes_typealias_import_only_when_all_usages_converted | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 408-419 |
| test_rewrites_builtin_containers_to_canonical_t_aliases | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 421-443 |
| test_rewrites_tuple_variadics_and_any_annotations | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 445-456 |
| test_rewrites_fixed_arity_four_tuple_to_quad | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 458-469 |
| test_inserts_t_import_after_parenthesized_import_block | Test | flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py | 471-491 |

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `any` (12 edge(s))
- `Path` (5 edge(s))
- `flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py::TestsFlextInfraRefactorInfraRefactorTypingUnifier.test_skips_duplicate_t_import_in_parenthesized_import_block`
  (3 edge(s))
- `apply_to_source` (1 edge(s))
- `flext-infra/src/flext_infra/transformers/typing_unifier.py::FlextInfraRefactorTypingUnifier` (1 edge(s))
- `flext-quality/src/flext_quality/docs/dashboard.py::FlextQualityDocumentationDashboard.index` (1 edge(s))

### Incoming

- `any` (12 edge(s))
- `Path` (5 edge(s))
- `flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py` (2 edge(s))
- `flext-infra/tests/unit/refactor/test_infra_refactor_typing_unifier.py::TestsFlextInfraRefactorInfraRefactorTypingUnifier.test_skips_duplicate_t_import_in_parenthesized_import_block`
  (2 edge(s))
- `index` (1 edge(s))
