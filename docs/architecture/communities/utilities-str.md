# utilities-str


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 69 nodes

- **Size**: 69 nodes
- **Cohesion**: 0.0194
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| test_version_info_is_consistent_with_version_string | Test | flext-cli/tests/unit/test_version.py | 57-64 |
| FlextUtilitiesConversion | Class | flext-core/src/flext_core/_utilities/conversion.py | 17-136 |
| join | Function | flext-core/src/flext_core/_utilities/conversion.py | 21-32 |
| normalize | Function | flext-core/src/flext_core/_utilities/conversion.py | 35-42 |
| to_str | Function | flext-core/src/flext_core/_utilities/conversion.py | 45-58 |
| to_str_list | Function | flext-core/src/flext_core/_utilities/conversion.py | 61-74 |
| to_int | Function | flext-core/src/flext_core/_utilities/conversion.py | 77-92 |
| to_float | Function | flext-core/src/flext_core/_utilities/conversion.py | 95-106 |
| to_bool | Function | flext-core/src/flext_core/_utilities/conversion.py | 109-113 |
| to_positive_int | Function | flext-core/src/flext_core/_utilities/conversion.py | 116-129 |
| to_optional_str | Function | flext-core/src/flext_core/_utilities/conversion.py | 132-136 |
| test_real_filterwarnings_keep_mro_violations_visible | Test | flext-core/tests/unit/test_enforcement_warning_visibility.py | 72-129 |
| test_to_bool_follows_truthiness | Test | flext-core/tests/unit/test_utilities.py | 65-68 |
| test_to_int_parses_or_defaults_to_zero | Test | flext-core/tests/unit/test_utilities.py | 73-76 |
| test_to_positive_int_clamps_negatives_to_zero | Test | flext-core/tests/unit/test_utilities.py | 87-90 |
| test_to_str_stringifies_with_empty_default | Test | flext-core/tests/unit/test_utilities.py | 93-96 |
| test_to_optional_str_preserves_none | Test | flext-core/tests/unit/test_utilities.py | 99-102 |
| test_to_str_list_wraps_scalars_and_preserves_lists | Test | flext-core/tests/unit/test_utilities.py | 108-111 |
| test_to_int_returns_int_or_default | Test | flext-core/tests/unit/test_utilities_coverage.py | 39-43 |
| test_to_bool_returns_truthiness_or_default | Test | flext-core/tests/unit/test_utilities_coverage.py | 72-76 |
| test_to_positive_int_accepts_only_positive_values | Test | flext-core/tests/unit/test_utilities_coverage.py | 92-96 |
| test_to_str_formats_value | Test | flext-core/tests/unit/test_utilities_coverage.py | 102-106 |
| test_to_str_uses_default_for_none | Test | flext-core/tests/unit/test_utilities_coverage.py | 108-110 |
| test_to_optional_str_only_returns_non_empty_strings | Test | flext-core/tests/unit/test_utilities_coverage.py | 116-120 |
| test_to_str_list_produces_list_of_strings | Test | flext-core/tests/unit/test_utilities_coverage.py | 125-129 |
| test_to_str_list_uses_default_for_none | Test | flext-core/tests/unit/test_utilities_coverage.py | 131-133 |
| test_join_concatenates_with_separator_and_case | Test | flext-core/tests/unit/test_utilities_coverage.py | 144-148 |
| test_normalize_stringifies_with_case | Test | flext-core/tests/unit/test_utilities_coverage.py | 159-163 |
| test_join_produces_expected_string | Test | flext-core/tests/unit/test_utilities_domain.py | 32-35 |
| test_join_empty_sequence_is_empty_string | Test | flext-core/tests/unit/test_utilities_domain.py | 37-38 |
| test_normalize_returns_expected_string | Test | flext-core/tests/unit/test_utilities_domain.py | 53-56 |
| test_to_str_converts_value | Test | flext-core/tests/unit/test_utilities_domain.py | 63-66 |
| test_to_str_none_uses_default | Test | flext-core/tests/unit/test_utilities_domain.py | 68-69 |
| test_to_str_present_value_ignores_default | Test | flext-core/tests/unit/test_utilities_domain.py | 71-72 |
| test_to_str_list_converts_value | Test | flext-core/tests/unit/test_utilities_domain.py | 84-87 |
| test_to_str_list_none_uses_default | Test | flext-core/tests/unit/test_utilities_domain.py | 89-90 |
| test_to_int_converts_value | Test | flext-core/tests/unit/test_utilities_domain.py | 106-109 |
| test_to_int_invalid_uses_default | Test | flext-core/tests/unit/test_utilities_domain.py | 111-112 |
| test_to_bool_converts_value | Test | flext-core/tests/unit/test_utilities_domain.py | 140-143 |
| test_to_bool_none_uses_default | Test | flext-core/tests/unit/test_utilities_domain.py | 145-146 |
| test_to_positive_int_rejects_non_positive | Test | flext-core/tests/unit/test_utilities_domain.py | 164-167 |
| test_to_positive_int_non_positive_uses_default | Test | flext-core/tests/unit/test_utilities_domain.py | 169-170 |
| test_to_optional_str_returns_non_empty_string_only | Test | flext-core/tests/unit/test_utilities_domain.py | 177-180 |
| test_version_string_and_info_describe_the_same_version | Test | flext-core/tests/unit/test_version.py | 36-39 |
| test_subclass_version_info_is_the_release_triple | Test | flext-core/tests/unit/test_version.py | 53-74 |
| test_subclass_rejects_non_semantic_release_metadata | Test | flext-core/tests/unit/test_version.py | 77-99 |
| test_noise_patterns_are_skipped | Test | flext-infra/tests/unit/_utilities/test_log_parser.py | 64-73 |
| test_max_lines_truncates_results | Test | flext-infra/tests/unit/_utilities/test_log_parser.py | 75-83 |
| test_default_max_lines_is_five | Test | flext-infra/tests/unit/_utilities/test_log_parser.py | 85-93 |
| test_mixed_errors_and_noise | Test | flext-infra/tests/unit/_utilities/test_log_parser.py | 103-110 |

*... and 19 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (42 edge(s))
- `join` (24 edge(s))
- `ok` (16 edge(s))
- `isinstance` (13 edge(s))
- `to_str` (11 edge(s))
- `str` (10 edge(s))
- `parse_ldif` (10 edge(s))
- `write_text` (8 edge(s))
- `lower` (7 edge(s))
- `to_str_list` (7 edge(s))
- `range` (6 edge(s))
- `len` (6 edge(s))
- `startswith` (5 edge(s))
- `int` (5 edge(s))
- `get` (5 edge(s))

### Incoming

- `that` (42 edge(s))
- `join` (24 edge(s))
- `ok` (16 edge(s))
- `flext-core/tests/unit/test_utilities_domain.py::TestsFlextCoreUtilitiesDomain` (15 edge(s))
- `to_str` (11 edge(s))
- `flext-core/tests/unit/test_utilities_coverage.py::TestsFlextCoreUtilitiesCoverage` (10 edge(s))
- `parse_ldif` (10 edge(s))
- `write_text` (8 edge(s))
- `to_str_list` (7 edge(s))
- `flext-core/tests/unit/test_utilities.py::TestsFlextCoreUtilities` (6 edge(s))
- `range` (6 edge(s))
- `len` (6 edge(s))
- `str` (5 edge(s))
- `startswith` (5 edge(s))
- `get` (5 edge(s))
