# utilities-filter

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 71 nodes

- **Size**: 71 nodes
- **Cohesion**: 0.0776
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| Filter | Class | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 19-374 |
| **init** | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 24-46 |
| create_filter | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 49-53 |
| filter_by_field | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 56-74 |
| filter_by_id_range | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 77-97 |
| _check_max | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 100-105 |
| _check_min | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 108-113 |
| _compare | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 116-129 |
| _compare_float | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 132-142 |
| _compare_string | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 145-155 |
| _condition_size | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 158-169 |
| filter_records | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 171-190 |
| sort_records | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 192-213 |
| key_func | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 202-206 |
| _apply_operator | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 215-275 |
| _get_nested_value | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 277-312 |
| _matches_all_filters | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 314-324 |
| _matches_condition | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 326-343 |
| _normalize | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 345-354 |
| _validate_filter_conditions_total | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 356-364 |
| _validate_filters | Function | flext-oracle-wms/src/flext_oracle_wms/_utilities/filtering.py | 366-374 |
| ValidationError | Class | flext-oracle-wms/src/flext_oracle_wms/errors.py | 22-23 |
| test_construction_exposes_configuration | Test | flext-oracle-wms/tests/unit/test_filtering.py | 62-65 |
| test_construction_defaults_are_case_insensitive | Test | flext-oracle-wms/tests/unit/test_filtering.py | 67-70 |
| test_construction_rejects_invalid_max_conditions | Test | flext-oracle-wms/tests/unit/test_filtering.py | 75-79 |
| test_create_filter_rejects_invalid_max_conditions | Test | flext-oracle-wms/tests/unit/test_filtering.py | 84-88 |
| test_create_filter_matches_constructor_contract | Test | flext-oracle-wms/tests/unit/test_filtering.py | 90-93 |
| test_construction_accepts_valid_initial_filters | Test | flext-oracle-wms/tests/unit/test_filtering.py | 95-99 |
| test_construction_rejects_initial_filters_over_limit | Test | flext-oracle-wms/tests/unit/test_filtering.py | 101-109 |
| test_empty_filters_returns_all_records_unchanged | Test | flext-oracle-wms/tests/unit/test_filtering.py | 114-118 |
| test_scalar_equality_selects_matching_records | Test | flext-oracle-wms/tests/unit/test_filtering.py | 120-124 |
| test_numeric_equality_selects_single_record | Test | flext-oracle-wms/tests/unit/test_filtering.py | 126-130 |
| test_list_value_matches_membership | Test | flext-oracle-wms/tests/unit/test_filtering.py | 132-138 |
| test_no_matching_records_yields_empty_success | Test | flext-oracle-wms/tests/unit/test_filtering.py | 140-144 |
| test_limit_truncates_result_set | Test | flext-oracle-wms/tests/unit/test_filtering.py | 146-153 |
| test_limit_applied_over_large_record_set | Test | flext-oracle-wms/tests/unit/test_filtering.py | 155-164 |
| test_default_equality_is_case_insensitive | Test | flext-oracle-wms/tests/unit/test_filtering.py | 169-173 |
| test_case_sensitive_equality_respects_case | Test | flext-oracle-wms/tests/unit/test_filtering.py | 175-179 |
| test_case_insensitive_equality_folds_unicode | Test | flext-oracle-wms/tests/unit/test_filtering.py | 181-186 |
| test_numeric_comparison_operators_select_range | Test | flext-oracle-wms/tests/unit/test_filtering.py | 200-208 |
| test_eq_operator_dict_matches_value | Test | flext-oracle-wms/tests/unit/test_filtering.py | 210-216 |
| test_ne_operator_dict_excludes_value | Test | flext-oracle-wms/tests/unit/test_filtering.py | 218-224 |
| test_in_operator_dict_matches_membership | Test | flext-oracle-wms/tests/unit/test_filtering.py | 226-233 |
| test_contains_operator_dict_matches_substring | Test | flext-oracle-wms/tests/unit/test_filtering.py | 235-242 |
| test_unknown_operator_matches_nothing | Test | flext-oracle-wms/tests/unit/test_filtering.py | 244-251 |
| test_comparison_requires_matching_types | Test | flext-oracle-wms/tests/unit/test_filtering.py | 253-261 |
| test_none_field_does_not_match_valued_condition | Test | flext-oracle-wms/tests/unit/test_filtering.py | 263-270 |
| test_none_field_does_not_match_list_condition | Test | flext-oracle-wms/tests/unit/test_filtering.py | 272-277 |
| test_dotted_path_resolves_nested_mapping | Test | flext-oracle-wms/tests/unit/test_filtering.py | 282-290 |
| test_dotted_path_falls_back_to_flattened_key | Test | flext-oracle-wms/tests/unit/test_filtering.py | 292-300 |

*... and 21 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `ok` (43 edge(s))
- `that` (43 edge(s))
- `Filter` (35 edge(s))
- `filter_records` (29 edge(s))
- `flext-oracle-wms/tests/unit/test_filtering.py::TestsFlextOracleWmsFiltering._ids` (15 edge(s))
- `create_filter` (9 edge(s))
- `Operator` (8 edge(s))
- `unwrap` (8 edge(s))
- `len` (6 edge(s))
- `fail` (6 edge(s))
- `sort_records` (6 edge(s))
- `str` (5 edge(s))
- `raises` (5 edge(s))
- `type` (4 edge(s))
- `isinstance` (3 edge(s))

### Incoming

- `that` (43 edge(s))
- `flext-oracle-wms/tests/unit/test_filtering.py::TestsFlextOracleWmsFiltering` (37 edge(s))
- `ok` (37 edge(s))
- `Filter` (35 edge(s))
- `filter_records` (29 edge(s))
- `flext-oracle-wms/tests/unit/test_filtering.py::TestsFlextOracleWmsFiltering._ids` (15 edge(s))
- `flext-oracle-wms/tests/unit/test_helpers.py::TestsFlextOracleWmsHelpers` (12 edge(s))
- `create_filter` (9 edge(s))
- `Operator` (8 edge(s))
- `unwrap` (8 edge(s))
- `sort_records` (6 edge(s))
- `raises` (5 edge(s))
- `filter_by_id_range` (3 edge(s))
- `len` (3 edge(s))
- `fail` (3 edge(s))
