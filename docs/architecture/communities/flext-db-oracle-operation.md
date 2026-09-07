# flext-db-oracle-operation


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
- **Cohesion**: 0.3415
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextDbOracleClient | Class | flext-db-oracle/src/flext_db_oracle/client.py | 21-561 |
| __init__ | Function | flext-db-oracle/src/flext_db_oracle/client.py | 47-51 |
| oracle_config | Function | flext-db-oracle/src/flext_db_oracle/client.py | 54-56 |
| run_cli_command | Function | flext-db-oracle/src/flext_db_oracle/client.py | 59-69 |
| _run_cli_command | Function | flext-db-oracle/src/flext_db_oracle/client.py | 72-88 |
| configure_preferences | Function | flext-db-oracle/src/flext_db_oracle/client.py | 90-104 |
| connect_to_oracle | Function | flext-db-oracle/src/flext_db_oracle/client.py | 106-140 |
| _connection_settings | Function | flext-db-oracle/src/flext_db_oracle/client.py | 142-182 |
| _connect_api | Function | flext-db-oracle/src/flext_db_oracle/client.py | 184-191 |
| disconnect | Function | flext-db-oracle/src/flext_db_oracle/client.py | 193-204 |
| execute | Function | flext-db-oracle/src/flext_db_oracle/client.py | 207-214 |
| execute_query | Function | flext-db-oracle/src/flext_db_oracle/client.py | 216-232 |
| health_check | Function | flext-db-oracle/src/flext_db_oracle/client.py | 234-241 |
| list_schemas | Function | flext-db-oracle/src/flext_db_oracle/client.py | 243-256 |
| list_tables | Function | flext-db-oracle/src/flext_db_oracle/client.py | 258-271 |
| _adapt_schemas | Function | flext-db-oracle/src/flext_db_oracle/client.py | 274-276 |
| _adapt_tables | Function | flext-db-oracle/src/flext_db_oracle/client.py | 279-281 |
| _adapt_health | Function | flext-db-oracle/src/flext_db_oracle/client.py | 284-291 |
| _adapt_data_for_table | Function | flext-db-oracle/src/flext_db_oracle/client.py | 293-308 |
| _adapt_data_root | Function | flext-db-oracle/src/flext_db_oracle/client.py | 310-327 |
| _build_table_string | Function | flext-db-oracle/src/flext_db_oracle/client.py | 329-337 |
| _execute_health_check | Function | flext-db-oracle/src/flext_db_oracle/client.py | 339-365 |
| _execute_operation | Function | flext-db-oracle/src/flext_db_oracle/client.py | 367-381 |
| _dispatch_operation | Function | flext-db-oracle/src/flext_db_oracle/client.py | 383-397 |
| _execute_with_chain | Function | flext-db-oracle/src/flext_db_oracle/client.py | 399-411 |
| _format_and_display_result | Function | flext-db-oracle/src/flext_db_oracle/client.py | 413-424 |
| _format_as_json | Function | flext-db-oracle/src/flext_db_oracle/client.py | 426-440 |
| _format_as_table | Function | flext-db-oracle/src/flext_db_oracle/client.py | 442-463 |
| _get_formatter_strategy | Function | flext-db-oracle/src/flext_db_oracle/client.py | 465-491 |
| _handle_health_check_operation | Function | flext-db-oracle/src/flext_db_oracle/client.py | 493-499 |
| _handle_list_schemas_operation | Function | flext-db-oracle/src/flext_db_oracle/client.py | 501-509 |
| _handle_list_tables_operation | Function | flext-db-oracle/src/flext_db_oracle/client.py | 511-522 |
| _handle_query_operation | Function | flext-db-oracle/src/flext_db_oracle/client.py | 524-548 |
| _validate_connection | Function | flext-db-oracle/src/flext_db_oracle/client.py | 550-561 |
| TestsFlextDbOracleCli | Class | flext-db-oracle/tests/unit/test_cli.py | 30-333 |
| test_construction_exposes_requested_debug_flag | Test | flext-db-oracle/tests/unit/test_cli.py | 36-39 |
| test_construction_starts_without_active_connection | Test | flext-db-oracle/tests/unit/test_cli.py | 41-44 |
| test_default_preferences_are_populated | Test | flext-db-oracle/tests/unit/test_cli.py | 56-61 |
| test_each_construction_yields_an_independent_client | Test | flext-db-oracle/tests/unit/test_cli.py | 63-69 |
| test_configure_preferences_updates_values_and_reports_success | Test | flext-db-oracle/tests/unit/test_cli.py | 73-85 |
| test_configure_preferences_preserves_untouched_defaults | Test | flext-db-oracle/tests/unit/test_cli.py | 87-97 |
| test_configure_preferences_tolerates_unknown_keys | Test | flext-db-oracle/tests/unit/test_cli.py | 99-105 |
| test_configure_preferences_accepts_empty_string_value | Test | flext-db-oracle/tests/unit/test_cli.py | 107-110 |
| test_privileged_operations_fail_without_connection | Test | flext-db-oracle/tests/unit/test_cli.py | 123-129 |
| test_execute_query_fails_without_connection | Test | flext-db-oracle/tests/unit/test_cli.py | 131-134 |
| test_connect_to_oracle_reports_failure_for_unreachable_host | Test | flext-db-oracle/tests/unit/test_cli.py | 138-153 |
| test_connect_to_oracle_from_settings_returns_string_error | Test | flext-db-oracle/tests/unit/test_cli.py | 155-176 |
| test_run_cli_command_returns_result | Test | flext-db-oracle/tests/unit/test_cli.py | 180-182 |
| test_run_cli_command_rejects_unknown_operation | Test | flext-db-oracle/tests/unit/test_cli.py | 184-187 |
| test_api_observability_metrics_are_available | Test | flext-db-oracle/tests/unit/test_cli.py | 238-243 |

*... and 15 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (38 edge(s))
- `ok` (20 edge(s))
- `fail` (19 edge(s))
- `str` (13 edge(s))
- `model_validate` (9 edge(s))
- `fail_op` (6 edge(s))
- `get` (6 edge(s))
- `validate_python` (5 edge(s))
- `ConfigMap` (5 edge(s))
- `map` (5 edge(s))
- `unwrap` (5 edge(s))
- `list` (4 edge(s))
- `info` (3 edge(s))
- `from_failure` (3 edge(s))
- `json_mapping_adapter` (3 edge(s))

### Incoming

- `that` (38 edge(s))
- `ok` (9 edge(s))
- `unwrap` (5 edge(s))
- `fail` (3 edge(s))
- `list_plugins` (3 edge(s))
- `flext-db-oracle/src/flext_db_oracle/client.py` (1 edge(s))
- `flext-db-oracle/tests/unit/test_cli.py` (1 edge(s))
- `fetch_observability_metrics` (1 edge(s))
- `optimize_query` (1 edge(s))
- `test_connection` (1 edge(s))
- `valid` (1 edge(s))
- `fetch_schemas` (1 edge(s))
- `fetch_tables` (1 edge(s))
- `model_validate` (1 edge(s))
- `any` (1 edge(s))
