# models-op


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 74 nodes

- **Size**: 74 nodes
- **Cohesion**: 0.0276
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| test_str_sequence_adapter_accepts_string_sequences | Test | flext-cli/tests/unit/test_typings.py | 31-36 |
| test_process_returns_mapped_values_on_success | Test | flext-cli/tests/unit/test_utilities_cov.py | 35-39 |
| test_process_skip_policy_drops_failing_items | Test | flext-cli/tests/unit/test_utilities_cov.py | 47-51 |
| test_process_predicate_excludes_items_before_processing | Test | flext-cli/tests/unit/test_utilities_cov.py | 53-57 |
| test_roundtrip_load_text_is_thread_safe | Test | flext-cli/tests/unit/test_yaml_roundtrip.py | 120-151 |
| test_domain_enums_are_string_valued_for_routing | Test | flext-core/tests/unit/test_constants_new.py | 65-78 |
| test_clear_is_idempotent | Test | flext-core/tests/unit/test_container_lifecycle.py | 62-73 |
| test_build_map_produces_flat_sorted_import_map | Test | flext-core/tests/unit/test_lazy_exports.py | 334-344 |
| test_register_handlers_batch_reports_every_success | Test | flext-core/tests/unit/test_registry.py | 53-63 |
| test_register_bindings_batch_reports_every_success | Test | flext-core/tests/unit/test_registry.py | 65-77 |
| test_instance_plugin_roundtrips_then_unregisters | Test | flext-core/tests/unit/test_registry.py | 86-95 |
| test_server_add_service_appends_to_public_services | Test | flext-grpc/tests/unit/test_entities.py | 72-81 |
| test_service_exposes_name_and_methods | Test | flext-grpc/tests/unit/test_entities.py | 190-196 |
| SetOp | Class | flext-infra/src/flext_infra/_models/deps_toml.py | 26-35 |
| ListOp | Class | flext-infra/src/flext_infra/_models/deps_toml.py | 37-56 |
| RemoveOp | Class | flext-infra/src/flext_infra/_models/deps_toml.py | 58-72 |
| PhaseConfig | Class | flext-infra/src/flext_infra/_models/deps_toml.py | 78-251 |
| Builder | Class | flext-infra/src/flext_infra/_models/deps_toml.py | 101-251 |
| __init__ | Function | flext-infra/src/flext_infra/_models/deps_toml.py | 104-109 |
| build | Function | flext-infra/src/flext_infra/_models/deps_toml.py | 112-117 |
| _nested_operations | Function | flext-infra/src/flext_infra/_models/deps_toml.py | 120-147 |
| operation | Function | flext-infra/src/flext_infra/_models/deps_toml.py | 149-169 |
| root | Function | flext-infra/src/flext_infra/_models/deps_toml.py | 171-174 |
| table | Function | flext-infra/src/flext_infra/_models/deps_toml.py | 176-179 |
| value | Function | flext-infra/src/flext_infra/_models/deps_toml.py | 181-187 |
| list | Function | flext-infra/src/flext_infra/_models/deps_toml.py | 189-204 |
| deprecated | Function | flext-infra/src/flext_infra/_models/deps_toml.py | 206-212 |
| nested | Function | flext-infra/src/flext_infra/_models/deps_toml.py | 214-244 |
| handler | Function | flext-infra/src/flext_infra/_models/deps_toml.py | 246-251 |
| test_empty_file_returns_zero_empty | Test | flext-infra/tests/unit/_utilities/test_log_parser.py | 28-35 |
| test_file_with_only_whitespace_returns_zero_empty | Test | flext-infra/tests/unit/_utilities/test_log_parser.py | 37-44 |
| test_parse_tool_args | Test | flext-infra/tests/unit/check/extended_workspace_init_tests.py | 26-27 |
| test_json_list_adapter_validates_mixed_cli_values | Test | flext-infra/tests/unit/test_infra_typings.py | 26-30 |
| test_str_seq_adapter_validates_project_name_sequences | Test | flext-infra/tests/unit/test_infra_typings.py | 44-47 |
| test_search_options_preserves_custom_values | Test | flext-ldap/tests/unit/test_models_search.py | 48-62 |
| test_extract_objectclass_category_maps_expected | Test | flext-ldap/tests/unit/test_models_search.py | 253-267 |
| test_conversion_metadata_tracks_changes | Test | flext-ldap/tests/unit/test_models_sync.py | 117-135 |
| test_norm_join | Test | flext-ldap/tests/unit/test_utilities.py | 60-63 |
| test_map_str | Test | flext-ldap/tests/unit/test_utilities.py | 78-81 |
| test_attr_to_str_list_scenarios | Test | flext-ldap/tests/unit/test_utilities.py | 144-164 |
| test_find_existing_values_found_case_insensitive | Test | flext-ldap/tests/unit/test_utilities.py | 250-254 |
| test_map_str_with_join | Test | flext-ldap/tests/unit/test_utilities.py | 378-381 |
| test_map_str_with_case_and_join | Test | flext-ldap/tests/unit/test_utilities.py | 383-386 |
| test_empty_content_parses_to_no_entries | Test | flext-ldif/tests/unit/services/test_servers_standardization.py | 110-116 |
| test_unparseable_content_is_empty_success_not_failure | Test | flext-ldif/tests/unit/services/test_servers_standardization.py | 123-129 |
| test_all_entries_are_unique | Test | flext-ldif/tests/unit/test_api_freeze.py | 106-108 |
| test_parse_returns_attribute_value_pairs | Test | flext-ldif/tests/unit/utilities/test_utilities_core.py | 96-101 |
| test_public_fields_reflect_constructor_arguments | Test | flext-meltano/tests/unit/test_execution_result.py | 59-83 |
| test_model_dump_json_round_trips_through_public_schema | Test | flext-meltano/tests/unit/test_execution_result.py | 176-203 |
| test_translate_tap_run_is_idempotent | Test | flext-meltano/tests/unit/test_singer_cli_translator.py | 108-118 |

*... and 24 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (89 edge(s))
- `list` (63 edge(s))
- `unwrap` (14 edge(s))
- `ok` (12 edge(s))
- `len` (9 edge(s))
- `tuple` (7 edge(s))
- `write_text` (7 edge(s))
- `discover_plugins` (6 edge(s))
- `glob` (6 edge(s))
- `attr_to_str_list` (5 edge(s))
- `mkdir` (5 edge(s))
- `discover` (5 edge(s))
- `Path` (5 edge(s))
- `m.ContractModel` (4 edge(s))
- `read_text` (4 edge(s))

### Incoming

- `that` (89 edge(s))
- `list` (63 edge(s))
- `unwrap` (14 edge(s))
- `ok` (12 edge(s))
- `len` (9 edge(s))
- `flext-plugin/tests/unit/test_domain_ports.py::TestsFlextPluginDomainPorts` (9 edge(s))
- `write_text` (7 edge(s))
- `flext-ldap/tests/unit/test_utilities.py::TestsFlextLdapUtilitiesUnit` (6 edge(s))
- `discover_plugins` (6 edge(s))
- `flext-target-oracle-wms/tests/examples/test_examples.py::TestsFlextTargetOracleWmsExamples` (6 edge(s))
- `glob` (6 edge(s))
- `flext-infra/src/flext_infra/_models/deps_toml.py` (5 edge(s))
- `attr_to_str_list` (5 edge(s))
- `mkdir` (5 edge(s))
- `discover` (5 edge(s))
