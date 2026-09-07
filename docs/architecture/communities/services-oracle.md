# services-oracle


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 198 nodes

- **Size**: 198 nodes
- **Cohesion**: 0.1587
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextDbOracleApi | Class | flext-db-oracle/src/flext_db_oracle/api.py | 21-28 |
| __init__ | Function | flext-db-oracle/src/flext_db_oracle/api.py | 24-28 |
| FlextDbOracleApiRuntime | Class | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 28-427 |
| __init__ | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 36-44 |
| __repr__ | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 47-50 |
| __enter__ | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 52-58 |
| __exit__ | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 60-71 |
| _dispatch_enabled | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 74-76 |
| settings | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 80-82 |
| connection | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 85-87 |
| connected | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 90-92 |
| oracle_config | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 95-97 |
| oracle_services | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 100-102 |
| from_config | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 105-107 |
| _build_api_result | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 110-124 |
| _normalize_parameters | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 127-140 |
| _normalize_parameters_list | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 143-153 |
| from_env | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 156-186 |
| from_url | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 189-213 |
| connect | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 215-220 |
| convert_singer_type | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 222-226 |
| disconnect | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 228-231 |
| execute | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 234-236 |
| execute_many | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 238-247 |
| execute_sql | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 249-253 |
| execute_statement | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 255-265 |
| fetch_columns | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 267-271 |
| fetch_health_status | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 273-275 |
| fetch_observability_metrics | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 277-279 |
| fetch_plugin | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 281-283 |
| fetch_primary_keys | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 285-289 |
| fetch_schemas | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 291-293 |
| fetch_table_metadata | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 295-299 |
| fetch_tables | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 301-303 |
| valid | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 305-309 |
| list_plugins | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 311-315 |
| map_singer_schema | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 317-323 |
| optimize_query | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 325-329 |
| query | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 331-340 |
| query_one | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 342-350 |
| register_plugin | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 352-354 |
| test_connection | Test | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 356-358 |
| to_dict | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 360-374 |
| transaction | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 376-381 |
| unregister_plugin | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 383-385 |
| _convert_to_query_result | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 387-421 |
| _execute_query_sql | Function | flext-db-oracle/src/flext_db_oracle/services/api_runtime.py | 423-427 |
| FlextDbOracleServices | Class | flext-db-oracle/src/flext_db_oracle/services/facade.py | 16-40 |
| __init__ | Function | flext-db-oracle/src/flext_db_oracle/services/facade.py | 27-29 |
| settings | Function | flext-db-oracle/src/flext_db_oracle/services/facade.py | 33-35 |

*... and 148 more members.*

## Execution Flows

- **_execute_query_sql** (criticality: 0.61, depth: 1)

## Dependencies

### Outgoing

- `that` (215 edge(s))
- `ok` (94 edge(s))
- `fail` (24 edge(s))
- `model_validate` (16 edge(s))
- `lower` (15 edge(s))
- `len` (14 edge(s))
- `map` (14 edge(s))
- `query` (14 edge(s))
- `connected` (14 edge(s))
- `FlextDbOracleApi` (12 edge(s))
- `upper` (11 edge(s))
- `fetch_tables` (9 edge(s))
- `build_select` (9 edge(s))
- `disconnect` (9 edge(s))
- `str` (7 edge(s))

### Incoming

- `that` (214 edge(s))
- `ok` (83 edge(s))
- `fail` (17 edge(s))
- `lower` (15 edge(s))
- `connected` (13 edge(s))
- `query` (11 edge(s))
- `len` (9 edge(s))
- `fetch_tables` (9 edge(s))
- `FlextDbOracleApi` (9 edge(s))
- `build_select` (9 edge(s))
- `upper` (9 edge(s))
- `disconnect` (9 edge(s))
- `model_validate` (9 edge(s))
- `map` (8 edge(s))
- `fetch_schemas` (7 edge(s))
