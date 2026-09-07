# matchers-validate


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 155 nodes

- **Size**: 155 nodes
- **Cohesion**: 0.1655
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| test_canonical_settings_satisfies_cli_protocol | Test | flext-cli/tests/unit/test_base.py | 43-46 |
| test_legacy_timeout_contract_remains_a_failure | Test | flext-cli/tests/unit/test_runtime_streamed_process.py | 200-209 |
| test_broken_live_sink_fails_after_complete_durable_log | Test | flext-cli/tests/unit/test_runtime_streamed_process.py | 248-275 |
| test_run_checked_fails_with_error_naming_failure | Test | flext-cli/tests/unit/test_runtime_utilities_extra.py | 57-65 |
| test_run_to_file_fails_with_timeout_error_on_slow_command | Test | flext-cli/tests/unit/test_runtime_utilities_extra.py | 111-124 |
| test_run_to_file_fails_with_execution_error_on_unwritable_target | Test | flext-cli/tests/unit/test_runtime_utilities_extra.py | 126-144 |
| test_run_to_file_fails_with_execution_error_on_invalid_env | Test | flext-cli/tests/unit/test_runtime_utilities_extra.py | 146-159 |
| test_settings_singleton_satisfies_contract | Test | flext-cli/tests/unit/test_settings.py | 33-36 |
| test_reset_for_testing_restores_usable_defaults | Test | flext-cli/tests/unit/test_settings.py | 144-150 |
| test_lifecycle_service_initialization | Test | flext-core/tests/integration/service_lifecycle_cases.py | 32-43 |
| test_container_resolve_unknown_name_fails_with_error | Test | flext-core/tests/integration/test_integration.py | 143-153 |
| test_fail_result_carries_error_message | Test | flext-core/tests/integration/test_migration_validation.py | 49-56 |
| test_flat_map_chains_fallible_operations | Test | flext-core/tests/integration/test_migration_validation.py | 85-100 |
| test_version_pattern_captures_semver | Test | flext-grpc/tests/unit/test_constants.py | 98-103 |
| test_create_client_entity_wraps_channel_with_target | Test | flext-grpc/tests/unit/test_utilities.py | 202-206 |
| test_rope_project_wrapper | Test | flext-infra/tests/refactor/test_rope_stubs.py | 17-24 |
| test_mypy_hint_pattern_matches_valid_hint | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 12-16 |
| test_mypy_hint_pattern_captures_package_name | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 18-22 |
| test_mypy_hint_pattern_matches_stub_package_wording | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 24-28 |
| test_mypy_stub_pattern_matches_missing_stubs | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 35-39 |
| test_mypy_stub_pattern_captures_library_name | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 41-45 |
| test_markdown_link_pattern_matches_link | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 58-63 |
| test_markdown_link_pattern_captures_text_and_url | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 65-70 |
| test_markdown_link_url_pattern_captures_url_only | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 79-83 |
| test_markdown_link_url_pattern_ignores_text | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 85-89 |
| test_heading_pattern_matches_h1 | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 91-95 |
| test_heading_pattern_matches_h6 | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 97-101 |
| test_heading_h2_h3_pattern_matches_h2 | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 110-115 |
| test_heading_h2_h3_pattern_matches_h3 | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 117-122 |
| test_anchor_link_pattern_matches_anchor | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 134-139 |
| test_anchor_link_pattern_captures_text_and_anchor | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 141-146 |
| test_inline_code_pattern_matches_backticks | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 148-152 |
| test_inline_code_pattern_empty_code | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 161-165 |
| test_make_assignment_matches_operators | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 167-171 |
| test_make_directive_and_conditional_match | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 173-179 |
| test_gitmodule_section_and_path_match | Test | flext-infra/tests/unit/test_infra_patterns_core.py | 181-186 |
| test_markdown_link_with_special_chars_in_url | Test | flext-infra/tests/unit/test_infra_patterns_extra.py | 41-45 |
| test_heading_with_trailing_whitespace | Test | flext-infra/tests/unit/test_infra_patterns_extra.py | 47-51 |
| test_inline_code_with_special_chars | Test | flext-infra/tests/unit/test_infra_patterns_extra.py | 53-57 |
| test_anchor_link_with_hyphens | Test | flext-infra/tests/unit/test_infra_patterns_extra.py | 59-63 |
| test_public_project_layout_uses_flext_for_core_exception | Test | flext-infra/tests/unit/validate/namespace_validator_tests.py | 51-60 |
| test_entry_lifecycle_is_observable_in_configured_runtime | Test | flext-target-ldap/tests/unit/test_client.py | 50-93 |
| FlextTestsFilesBatchMixin | Class | flext-tests/src/flext_tests/_utilities/_files/_batch.py | 13-125 |
| batch_files | Function | flext-tests/src/flext_tests/_utilities/_files/_batch.py | 16-125 |
| process_one | Function | flext-tests/src/flext_tests/_utilities/_files/_batch.py | 61-101 |
| FlextTestsFilesComparisonMixin | Class | flext-tests/src/flext_tests/_utilities/_files/_comparison_parts/comparison_part_01.py | 12-95 |
| _read_both | Function | flext-tests/src/flext_tests/_utilities/_files/_comparison_parts/comparison_part_01.py | 21-26 |
| _try_parse_both | Function | flext-tests/src/flext_tests/_utilities/_files/_comparison_parts/comparison_part_01.py | 28-64 |
| _apply_key_filtering | Function | flext-tests/src/flext_tests/_utilities/_files/_comparison_parts/comparison_part_01.py | 66-95 |
| FlextTestsFilesComparisonMixin | Class | flext-tests/src/flext_tests/_utilities/_files/_comparison_parts/comparison_part_02.py | 15-139 |

*... and 105 more members.*

## Execution Flows

- **ok** (criticality: 0.73, depth: 3)
- **fail** (criticality: 0.68, depth: 3)
- **read** (criticality: 0.56, depth: 3)

## Dependencies

### Outgoing

- `that` (99 edge(s))
- `AssertionError` (72 edge(s))
- `isinstance` (67 edge(s))
- `not_none` (58 edge(s))
- `format` (37 edge(s))
- `group` (30 edge(s))
- `search` (27 edge(s))
- `ok` (24 edge(s))
- `str` (23 edge(s))
- `fail` (22 edge(s))
- `items` (18 edge(s))
- `list` (15 edge(s))
- `getattr` (14 edge(s))
- `model_validate` (13 edge(s))
- `type` (13 edge(s))

### Incoming

- `that` (99 edge(s))
- `not_none` (58 edge(s))
- `group` (30 edge(s))
- `search` (24 edge(s))
- `flext-infra/tests/unit/test_infra_patterns_core.py::TestsFlextInfraInfraPatternsCore` (20 edge(s))
- `ok` (9 edge(s))
- `match` (9 edge(s))
- `fail` (7 edge(s))
- `Cli` (6 edge(s))
- `assert_success` (6 edge(s))
- `shared` (6 edge(s))
- `run_to_file` (5 edge(s))
- `lower` (5 edge(s))
- `tf` (5 edge(s))
- `close` (4 edge(s))
