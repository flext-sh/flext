# unit-flext

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 65 nodes

- **Size**: 65 nodes
- **Cohesion**: 0.4016
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| messages | Function | flext-core/tests/unit/_enforcement_support.py | 19-20 |
| synthetic_method | Function | flext-core/tests/unit/_enforcement_support.py | 23-25 |
| make_class | Function | flext-core/tests/unit/_enforcement_support.py | 28-32 |
| TestsFlextCoreEnforcement | Class | flext-core/tests/unit/test_enforcement.py | 22-115 |
| test_check_returns_report_with_violations_collection | Test | flext-core/tests/unit/test_enforcement.py | 25-32 |
| test_compliant_flext_class_produces_no_violations | Test | flext-core/tests/unit/test_enforcement.py | 34-38 |
| test_builtin_class_flagged_missing_project_prefix | Test | flext-core/tests/unit/test_enforcement.py | 41-50 |
| test_private_underscore_class_exempt_from_namespace_layer | Test | flext-core/tests/unit/test_enforcement.py | 52-58 |
| test_accessor_prefix_method_is_flagged | Test | flext-core/tests/unit/test_enforcement.py | 68-75 |
| test_non_accessor_prefix_method_allowed | Test | flext-core/tests/unit/test_enforcement.py | 78-83 |
| test_settings_named_class_requires_inheritance | Test | flext-core/tests/unit/test_enforcement.py | 89-97 |
| test_every_violation_carries_public_metadata | Test | flext-core/tests/unit/test_enforcement.py | 99-108 |
| test_check_is_idempotent_for_same_target | Test | flext-core/tests/unit/test_enforcement.py | 110-115 |
| TestsFlextCoreEnforcementAccessors | Class | flext-core/tests/unit/test_enforcement_accessors.py | 23-179 |
| test_forbidden_accessor_prefix_is_flagged | Test | flext-core/tests/unit/test_enforcement_accessors.py | 27-39 |
| test_domain_verb_method_is_allowed | Test | flext-core/tests/unit/test_enforcement_accessors.py | 42-54 |
| test_accessor_violation_locates_the_owning_class | Test | flext-core/tests/unit/test_enforcement_accessors.py | 56-67 |
| test_bare_collection_field_is_flagged | Test | flext-core/tests/unit/test_enforcement_accessors.py | 69-78 |
| test_missing_field_description_names_the_field | Test | flext-core/tests/unit/test_enforcement_accessors.py | 80-91 |
| test_settings_named_class_must_inherit_flext_settings | Test | flext-core/tests/unit/test_enforcement_accessors.py | 93-104 |
| test_nested_settings_class_is_exempt_from_inheritance_rule | Test | flext-core/tests/unit/test_enforcement_accessors.py | 106-122 |
| test_non_settings_class_is_not_flagged_for_inheritance | Test | flext-core/tests/unit/test_enforcement_accessors.py | 124-134 |
| test_clean_class_yields_an_empty_report | Test | flext-core/tests/unit/test_enforcement_accessors.py | 136-147 |
| test_direct_nested_class_is_a_namespace | Test | flext-core/tests/unit/test_enforcement_accessors.py | 149-159 |
| test_inherited_nested_class_is_a_namespace | Test | flext-core/tests/unit/test_enforcement_accessors.py | 161-171 |
| test_plain_class_is_not_a_namespace | Test | flext-core/tests/unit/test_enforcement_accessors.py | 173-179 |
| TestsFlextEnforcementModels | Class | flext-core/tests/unit/test_enforcement_models.py | 21-162 |
| test_any_field_detected | Test | flext-core/tests/unit/test_enforcement_models.py | 22-26 |
| test_typed_field_passes | Test | flext-core/tests/unit/test_enforcement_models.py | 28-32 |
| test_bare_dict_detected | Test | flext-core/tests/unit/test_enforcement_models.py | 34-38 |
| test_bare_list_detected | Test | flext-core/tests/unit/test_enforcement_models.py | 40-44 |
| test_mapping_passes | Test | flext-core/tests/unit/test_enforcement_models.py | 46-56 |
| test_mutable_sequence_list_factory_passes | Test | flext-core/tests/unit/test_enforcement_models.py | 58-64 |
| test_mutable_mapping_forward_ref_dict_factory_passes | Test | flext-core/tests/unit/test_enforcement_models.py | 66-75 |
| test_mutable_json_mapping_alias_dict_factory_passes | Test | flext-core/tests/unit/test_enforcement_models.py | 77-87 |
| test_sequence_list_factory_detected | Test | flext-core/tests/unit/test_enforcement_models.py | 89-95 |
| test_missing_description_detected | Test | flext-core/tests/unit/test_enforcement_models.py | 97-101 |
| test_description_present_passes | Test | flext-core/tests/unit/test_enforcement_models.py | 103-107 |
| test_v1_config_class_detected | Test | flext-core/tests/unit/test_enforcement_models.py | 109-118 |
| test_flexible_internal_allows_ignore | Test | flext-core/tests/unit/test_enforcement_models.py | 120-124 |
| test_mode_default_is_warn | Test | flext-core/tests/unit/test_enforcement_models.py | 126-127 |
| test_enforcement_rules_loaded | Test | flext-core/tests/unit/test_enforcement_models.py | 129-134 |
| test_canonical_flext_core_class_satisfies_prefix_contract | Test | flext-core/tests/unit/test_enforcement_models.py | 136-138 |
| test_class_prefix_enforced_only_for_knowable_projects | Test | flext-core/tests/unit/test_enforcement_models.py | 144-162 |
| _synthetic | Function | flext-core/tests/unit/test_enforcement_namespace.py | 35-40 |
| TestsFlextCoreEnforcementNamespace | Class | flext-core/tests/unit/test_enforcement_namespace.py | 43-347 |
| test_exempt_or_compliant_targets_report_no_prefix_violation | Test | flext-core/tests/unit/test_enforcement_namespace.py | 80-88 |
| test_flext_core_class_without_prefix_is_flagged_for_flext | Test | flext-core/tests/unit/test_enforcement_namespace.py | 90-104 |
| test_tests_module_class_with_composed_prefix_is_compliant | Test | flext-core/tests/unit/test_enforcement_namespace.py | 106-116 |
| test_run_layer_emits_warnings_for_mutable_constant_under_warn_mode | Test | flext-core/tests/unit/test_enforcement_namespace.py | 202-223 |

*... and 15 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `check` (43 edge(s))
- `any` (11 edge(s))
- `catch_warnings` (6 edge(s))
- `simplefilter` (6 edge(s))
- `all` (4 edge(s))
- `len` (4 edge(s))
- `emit` (4 edge(s))
- `type` (3 edge(s))
- `has_nested_namespace` (3 edge(s))
- `run_layer` (3 edge(s))
- `bool` (2 edge(s))
- `list` (2 edge(s))
- `warns` (2 edge(s))
- `str` (2 edge(s))
- `model_dump` (1 edge(s))

### Incoming

- `check` (42 edge(s))
- `any` (11 edge(s))
- `flext-core/tests/unit/test_enforcement_namespace_part_02.py` (6 edge(s))
- `catch_warnings` (5 edge(s))
- `simplefilter` (5 edge(s))
- `all` (4 edge(s))
- `len` (4 edge(s))
- `emit` (4 edge(s))
- `flext-core/tests/unit/_enforcement_support.py` (3 edge(s))
- `has_nested_namespace` (3 edge(s))
- `bool` (2 edge(s))
- `warns` (2 edge(s))
- `flext-core/tests/unit/test_enforcement_namespace.py` (2 edge(s))
- `run_layer` (2 edge(s))
- `str` (2 edge(s))
