# flext-tap-oracle-wms-tap


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 129 nodes

- **Size**: 129 nodes
- **Cohesion**: 0.3043
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextMeltanoSingerTapAdapter | Class | flext-meltano/src/flext_meltano/services/singer_sdk.py | 15-81 |
| __init__ | Function | flext-meltano/src/flext_meltano/services/singer_sdk.py | 18-20 |
| settings | Function | flext-meltano/src/flext_meltano/services/singer_sdk.py | 23-39 |
| _normalize_recursive | Function | flext-meltano/src/flext_meltano/services/singer_sdk.py | 42-62 |
| run_cli | Function | flext-meltano/src/flext_meltano/services/singer_sdk.py | 64-72 |
| discover_streams | Function | flext-meltano/src/flext_meltano/services/singer_sdk.py | 74-77 |
| sync_all | Function | flext-meltano/src/flext_meltano/services/singer_sdk.py | 79-81 |
| FlextTapLdifService | Class | flext-tap-ldif/src/flext_tap_ldif/api.py | 20-39 |
| create_tap_instance | Function | flext-tap-ldif/src/flext_tap_ldif/api.py | 28-39 |
| main | Function | flext-tap-oracle-wms/examples/01_basic_usage.py | 14-52 |
| FlextTapOracleWmsService | Class | flext-tap-oracle-wms/src/flext_tap_oracle_wms/api.py | 23-49 |
| create_tap_instance | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/api.py | 31-49 |
| main | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/cli.py | 19-21 |
| FlextTapOracleWmsError | Class | flext-tap-oracle-wms/src/flext_tap_oracle_wms/errors.py | 8-9 |
| FlextTapOracleWmsConfigurationError | Class | flext-tap-oracle-wms/src/flext_tap_oracle_wms/errors.py | 16-17 |
| FlextTapOracleWmsStream | Class | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 22-303 |
| __init__ | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 38-71 |
| schema | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 75-80 |
| client | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 83-93 |
| page_size | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 101-107 |
| normalize_json_value | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 110-135 |
| normalize_scalar_value | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 138-146 |
| get_primary_keys | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 148-150 |
| get_records | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 153-176 |
| get_replication_key | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 178-180 |
| post_process | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 183-234 |
| build_operation_kwargs | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 236-250 |
| _fetch_page_data | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 252-275 |
| _process_page_records | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 277-300 |
| _run | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/streams.py | 302-303 |
| FlextTapOracleWms | Class | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 16-305 |
| from_settings | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 41-58 |
| settings | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 61-65 |
| catalog_dict_typed | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 68-80 |
| _to_typed_catalog | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 83-155 |
| flext_config | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 158-170 |
| wms_client | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 173-198 |
| _schema_for_entity | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 201-203 |
| discovercatalog_typed | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 205-238 |
| discover_streams | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 241-261 |
| execute | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 263-268 |
| get_implementation_metrics | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 270-276 |
| get_implementation_name | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 278-280 |
| get_implementation_version | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 282-284 |
| validate_configuration | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 286-292 |
| initialize | Function | flext-tap-oracle-wms/src/flext_tap_oracle_wms/tap.py | 294-305 |
| sample_config | Function | flext-tap-oracle-wms/tests/conftest.py | 55-70 |
| real_config | Function | flext-tap-oracle-wms/tests/conftest.py | 74-81 |
| sample_catalog | Function | flext-tap-oracle-wms/tests/conftest.py | 85-98 |
| tap_instance | Function | flext-tap-oracle-wms/tests/conftest.py | 102-106 |

*... and 79 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (84 edge(s))
- `info` (67 edge(s))
- `isinstance` (43 edge(s))
- `get` (35 edge(s))
- `str` (25 edge(s))
- `skip` (20 edge(s))
- `append` (18 edge(s))
- `len` (16 edge(s))
- `ok` (16 edge(s))
- `model_dump` (14 edge(s))
- `time` (14 edge(s))
- `model_validate` (13 edge(s))
- `validate_python` (12 edge(s))
- `Mapping` (11 edge(s))
- `list` (11 edge(s))

### Incoming

- `that` (78 edge(s))
- `info` (63 edge(s))
- `skip` (20 edge(s))
- `get` (18 edge(s))
- `append` (15 edge(s))
- `isinstance` (14 edge(s))
- `str` (13 edge(s))
- `time` (12 edge(s))
- `len` (10 edge(s))
- `model_validate` (9 edge(s))
- `model_dump` (7 edge(s))
- `next` (7 edge(s))
- `list` (7 edge(s))
- `keys` (7 edge(s))
- `get_records` (7 edge(s))
