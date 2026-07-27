# models-target

## Overview

Community of 114 nodes

- **Size**: 114 nodes
- **Cohesion**: 0.3349
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
| ------ | ------ | ------ | ------- |
| TestsFlextTargetLdapServiceBase | Class | flext-target-ldap/tests/base.py | 13-25 |
| fetch_settings | Function | flext-target-ldap/tests/base.py | 18-20 |
| _runtime_bootstrap_options | Function | flext-target-ldap/tests/base.py | 24-25 |
| ProcessTarget | Class | flext-target-ldap/tests/utilities.py | 52-70 |
| **init** | Function | flext-target-ldap/tests/utilities.py | 55-60 |
| process_record | Function | flext-target-ldap/tests/utilities.py | 63-70 |
| client | Function | flext-target-ldap/tests/unit/test_client.py | 17-20 |
| TestsFlextTargetLdapClient | Class | flext-target-ldap/tests/unit/test_client.py | 23-174 |
| test_client_initialization | Test | flext-target-ldap/tests/unit/test_client.py | 26-32 |
| test_server_uri_construction | Test | flext-target-ldap/tests/unit/test_client.py | 34-46 |
| test_connect_delegates_to_flext_ldap_api | Test | flext-target-ldap/tests/unit/test_client.py | 48-58 |
| test_disconnect_calls_flext_ldap_api | Test | flext-target-ldap/tests/unit/test_client.py | 60-68 |
| test_add_entry_uses_real_ldif_entry | Test | flext-target-ldap/tests/unit/test_client.py | 70-89 |
| test_modify_entry_uses_real_modify_changes | Test | flext-target-ldap/tests/unit/test_client.py | 91-111 |
| test_delete_entry_delegates_to_flext_ldap_api | Test | flext-target-ldap/tests/unit/test_client.py | 113-124 |
| test_search_entry_maps_search_results | Test | flext-target-ldap/tests/unit/test_client.py | 126-158 |
| test_search_entry_disconnects_after_search | Test | flext-target-ldap/tests/unit/test_client.py | 160-174 |
| TestsFlextTargetLdapTarget | Class | flext-target-ldap/tests/unit/test_target.py | 31-138 |
| test_get_sink_class | Test | flext-target-ldap/tests/unit/test_target.py | 42-49 |
| test_target_initialization | Test | flext-target-ldap/tests/unit/test_target.py | 51-57 |
| test_test_service_settings_include_tests_namespace | Test | flext-target-ldap/tests/unit/test_target.py | 59-63 |
| test_dn_template_processing | Test | flext-target-ldap/tests/unit/test_target.py | 65-79 |
| test_object_classes_processing | Test | flext-target-ldap/tests/unit/test_target.py | 81-93 |
| test_process_record | Test | flext-target-ldap/tests/unit/test_target.py | 95-108 |
| test_process_delete_record | Test | flext-target-ldap/tests/unit/test_target.py | 110-126 |
| test_sink_process_record_delegates_to_target_handler | Test | flext-target-ldap/tests/unit/test_target.py | 128-138 |
| TargetLdap | Class | flext-target-ldap/src/flext_target_ldap/utilities.py | 31-114 |
| build_singer_catalog | Function | flext-target-ldap/src/flext_target_ldap/utilities.py | 35-83 |
| TypeConversion | Class | flext-target-ldap/src/flext_target_ldap/utilities.py | 85-114 |
| extract_attribute_mapping | Function | flext-target-ldap/src/flext_target_ldap/utilities.py | 89-102 |
| extract_object_classes | Function | flext-target-ldap/src/flext_target_ldap/utilities.py | 105-114 |
| FlextTargetLdap | Class | flext-target-ldap/src/flext_target_ldap/api.py | 37-267 |
| **init** | Function | flext-target-ldap/src/flext_target_ldap/api.py | 47-56 |
| orchestrator | Function | flext-target-ldap/src/flext_target_ldap/api.py | 59-64 |
| singer_catalog | Function | flext-target-ldap/src/flext_target_ldap/api.py | 67-69 |
| get_sink | Function | flext-target-ldap/src/flext_target_ldap/api.py | 71-79 |
| get_sink_class | Function | flext-target-ldap/src/flext_target_ldap/api.py | 81-96 |
| setup | Function | flext-target-ldap/src/flext_target_ldap/api.py | 98-108 |
| teardown | Function | flext-target-ldap/src/flext_target_ldap/api.py | 110-118 |
| validate_config | Function | flext-target-ldap/src/flext_target_ldap/api.py | 120-123 |
| _load_config_from_file | Function | flext-target-ldap/src/flext_target_ldap/api.py | 126-136 |
| _construct_dn | Function | flext-target-ldap/src/flext_target_ldap/api.py | 139-152 |
| _process_record_message | Function | flext-target-ldap/src/flext_target_ldap/api.py | 155-190 |
| run_cli | Function | flext-target-ldap/src/flext_target_ldap/api.py | 193-199 |
| _run_cli | Function | flext-target-ldap/src/flext_target_ldap/api.py | 204-220 |
| _process_input_line | Function | flext-target-ldap/src/flext_target_ldap/api.py | 223-258 |
| _parse_input_line | Function | flext-target-ldap/src/flext_target_ldap/api.py | 261-267 |
| FlextTargetLdapOrchestrator | Class | flext-target-ldap/src/flext_target_ldap/application/orchestrator.py | 20-92 |
| orchestrate_data_loading | Function | flext-target-ldap/src/flext_target_ldap/application/orchestrator.py | 50-76 |
| validate_target_configuration | Function | flext-target-ldap/src/flext_target_ldap/application/orchestrator.py | 78-92 |

*... and 64 more members.*

## Execution Flows

- **run_cli** (criticality: 0.76, depth: 9)

## Dependencies

### Outgoing

- `get` (54 edge(s))
- `ok` (32 edge(s))
- `fail` (31 edge(s))
- `info` (21 edge(s))
- `isinstance` (19 edge(s))
- `items` (17 edge(s))
- `exception` (16 edge(s))
- `MagicMock` (16 edge(s))
- `fail_op` (15 edge(s))
- `str` (10 edge(s))
- `debug` (8 edge(s))
- `assert_called_once` (7 edge(s))
- `append` (6 edge(s))
- `flext-infra/src/flext_infra/_models/deps_toml.py::FlextInfraModelsDepsToml.Deps.Toml.PhaseConfig.Builder.list`
  (5 edge(s))
- `model_validate` (5 edge(s))

### Incoming

- `MagicMock` (16 edge(s))
- `flext-target-ldap/src/flext_target_ldap/_models/sinks.py` (12 edge(s))
- `ok` (7 edge(s))
- `assert_called_once` (7 edge(s))
- `isinstance` (6 edge(s))
- `FlextTargetLdap` (6 edge(s))
- `assert_called_once_with` (5 edge(s))
- `get_sink` (4 edge(s))
- `process_record` (3 edge(s))
- `flext-target-ldap/src/flext_target_ldap/api.py` (2 edge(s))
- `flext-target-ldap/src/flext_target_ldap/utilities.py` (2 edge(s))
- `flext-target-ldap/tests/unit/test_client.py` (2 edge(s))
- `search_entry` (2 edge(s))
- `flext-target-ldap/src/flext_target_ldap/_models/processing_result.py` (1 edge(s))
- `flext-target-ldap/src/flext_target_ldap/_utilities/client.py` (1 edge(s))
