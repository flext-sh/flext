# utilities-oracle


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 78 nodes

- **Size**: 78 nodes
- **Cohesion**: 0.2665
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextTargetOracle | Class | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 15-266 |
| __init__ | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 20-26 |
| discover_catalog | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 28-63 |
| execute | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 65-77 |
| _ready_result | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 79-88 |
| _execute_payload | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 90-103 |
| _parse_singer_payload | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 105-123 |
| _parse_singer_mapping | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 125-154 |
| finalize | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 156-158 |
| get_implementation_metrics | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 160-166 |
| initialize | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 168-170 |
| process_singer_message | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 172-188 |
| process_singer_messages | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 190-215 |
| test_connection | Test | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 217-219 |
| write_record | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 221-227 |
| _handle_activate_version | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 229-237 |
| _handle_record | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 239-247 |
| _handle_schema | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 249-260 |
| _handle_state | Function | flext-target-oracle/src/flext_target_oracle/_utilities/client.py | 262-266 |
| FlextTargetOracleErrorMetadata | Class | flext-target-oracle/src/flext_target_oracle/_utilities/errors.py | 19-28 |
| OracleConnectionError | Class | flext-target-oracle/src/flext_target_oracle/_utilities/errors.py | 40-41 |
| AuthenticationError | Class | flext-target-oracle/src/flext_target_oracle/_utilities/errors.py | 46-47 |
| ProcessingError | Class | flext-target-oracle/src/flext_target_oracle/_utilities/errors.py | 49-50 |
| SchemaError | Class | flext-target-oracle/src/flext_target_oracle/_utilities/errors.py | 55-56 |
| FlextTargetOracleLoader | Class | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 25-791 |
| _default_record_buffers | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 33-38 |
| _normalize_log_value | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 60-62 |
| _oracle_timestamp_text | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 65-74 |
| _with_oracle_timestamp_binds | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 77-85 |
| _loader_columns | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 87-99 |
| _loader_columns_unchecked | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 101-165 |
| _schema_field_type | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 168-178 |
| _append_schema_column | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 180-216 |
| _sdc_columns | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 219-234 |
| _ordered_columns | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 236-296 |
| by_name | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 250-251 |
| __init__ | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 298-304 |
| _init_oracle_loader | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 306-326 |
| oracle_api | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 329-331 |
| record_buffers | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 334-338 |
| target_config | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 341-343 |
| total_records | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 346-348 |
| _run_connection_operation | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 350-361 |
| connect | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 363-370 |
| disconnect | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 372-376 |
| ensure_table_exists | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 378-391 |
| _ensure_table_exists_unchecked | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 393-435 |
| _prepare_existing_table | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 437-453 |
| _create_custom_indexes | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 455-490 |
| _custom_index_columns | Function | flext-target-oracle/src/flext_target_oracle/_utilities/loader.py | 493-507 |

*... and 28 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `ok` (38 edge(s))
- `get` (19 edge(s))
- `fail` (19 edge(s))
- `from_failure` (15 edge(s))
- `str` (15 edge(s))
- `upper` (12 edge(s))
- `fail_op` (12 edge(s))
- `json_mapping_adapter` (9 edge(s))
- `validate_python` (9 edge(s))
- `isinstance` (7 edge(s))
- `model_validate` (7 edge(s))
- `items` (7 edge(s))
- `append` (6 edge(s))
- `replace` (6 edge(s))
- `len` (6 edge(s))

### Incoming

- `ok` (11 edge(s))
- `flext-target-oracle/src/flext_target_oracle/_utilities/errors.py` (5 edge(s))
- `that` (5 edge(s))
- `flext-target-oracle/tests/unit/test_loader.py::TestsFlextTargetOracleLoader` (3 edge(s))
- `FlextTargetOracleLoader` (3 edge(s))
- `load_record` (3 edge(s))
- `fail_op` (2 edge(s))
- `str` (2 edge(s))
- `unwrap` (2 edge(s))
- `json_dumps` (2 edge(s))
- `model_validate` (2 edge(s))
- `finalize_all_streams` (2 edge(s))
- `flext-target-oracle/tests/unit/test_target.py::TestsFlextTargetOracleTarget` (2 edge(s))
- `flext-target-oracle/src/flext_target_oracle/_utilities/client.py` (1 edge(s))
- `test_connection` (1 edge(s))
