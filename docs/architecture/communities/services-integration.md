# services-integration


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 106 nodes

- **Size**: 106 nodes
- **Cohesion**: 0.3841
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextOracleOicClient | Class | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 25-426 |
| __init__ | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 33-49 |
| __enter__ | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 51-53 |
| __exit__ | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 55-66 |
| create_connection | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 68-73 |
| create_integration | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 75-81 |
| encode_client_credentials | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 83-88 |
| execute_file_transfer | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 90-96 |
| execute_scheduled_orchestration | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 98-104 |
| get_access_token | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 106-116 |
| get_connections | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 118-125 |
| get_integrations | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 127-136 |
| get_lookups | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 138-142 |
| get_oauth_request_body | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 144-153 |
| get_packages | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 155-159 |
| make_request | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 161-182 |
| paginate_request | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 184-193 |
| _paginate_request | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 195-222 |
| update_integration | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 224-230 |
| _build_client_with_token | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 232-251 |
| _create_authenticated_client | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 253-255 |
| _execute_api_request | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 257-272 |
| _run_api_request | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 274-299 |
| _execute_token_request | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 301-310 |
| _request_access_token | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 312-331 |
| _parse_api_response | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 333-340 |
| _parse_api_response_value | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 342-361 |
| _parse_token_response | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 363-370 |
| _parse_token_response_value | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 372-387 |
| _prepare_oauth_request | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 389-402 |
| _store_and_return_token | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 404-408 |
| _to_api_payload | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 410-420 |
| _validate_token_url | Function | flext-oracle-oic/src/flext_oracle_oic/ext_client.py | 422-426 |
| FlextOracleOicAuthMixin | Class | flext-oracle-oic/src/flext_oracle_oic/services/auth.py | 17-59 |
| refresh_auth_token | Function | flext-oracle-oic/src/flext_oracle_oic/services/auth.py | 20-37 |
| validate_auth_token | Function | flext-oracle-oic/src/flext_oracle_oic/services/auth.py | 39-59 |
| FlextOracleOicServiceBase | Class | flext-oracle-oic/src/flext_oracle_oic/services/base.py | 26-276 |
| __init__ | Function | flext-oracle-oic/src/flext_oracle_oic/services/base.py | 36-50 |
| __enter__ | Function | flext-oracle-oic/src/flext_oracle_oic/services/base.py | 52-54 |
| __exit__ | Function | flext-oracle-oic/src/flext_oracle_oic/services/base.py | 56-62 |
| _as_text | Function | flext-oracle-oic/src/flext_oracle_oic/services/base.py | 65-74 |
| _to_general_value | Function | flext-oracle-oic/src/flext_oracle_oic/services/base.py | 77-93 |
| _build_integration_info | Function | flext-oracle-oic/src/flext_oracle_oic/services/base.py | 95-109 |
| execute | Function | flext-oracle-oic/src/flext_oracle_oic/services/base.py | 112-119 |
| settings | Function | flext-oracle-oic/src/flext_oracle_oic/services/base.py | 123-125 |
| list_integrations | Function | flext-oracle-oic/src/flext_oracle_oic/services/base.py | 127-140 |
| _list_integrations | Function | flext-oracle-oic/src/flext_oracle_oic/services/base.py | 142-160 |
| _get_client | Function | flext-oracle-oic/src/flext_oracle_oic/services/base.py | 162-173 |
| _get_or_create_client | Function | flext-oracle-oic/src/flext_oracle_oic/services/base.py | 175-198 |
| validate_business_rules | Function | flext-oracle-oic/src/flext_oracle_oic/services/base.py | 200-241 |

*... and 56 more members.*

## Execution Flows

- **execute_app_driven_orchestration** (criticality: 0.68, depth: 6)
- **_parse_token_response** (criticality: 0.61, depth: 1)
- **execute_file_transfer** (criticality: 0.61, depth: 1)
- **execute_scheduled_orchestration** (criticality: 0.61, depth: 1)
- **get_lookups** (criticality: 0.60, depth: 7)
- **get_packages** (criticality: 0.60, depth: 7)
- **create_connection** (criticality: 0.59, depth: 5)
- **execute_file_transfer** (criticality: 0.59, depth: 5)
- **execute_scheduled_orchestration** (criticality: 0.59, depth: 5)
- **create_integration** (criticality: 0.56, depth: 5)
- *... and 1 more flows.*

## Dependencies

### Outgoing

- `fail` (48 edge(s))
- `ok` (26 edge(s))
- `exception` (23 edge(s))
- `get` (21 edge(s))
- `fail_op` (16 edge(s))
- `isinstance` (14 edge(s))
- `that` (14 edge(s))
- `str` (12 edge(s))
- `getattr` (9 edge(s))
- `from_failure` (9 edge(s))
- `Mapping` (6 edge(s))
- `flext-oracle-oic/src/flext_oracle_oic/services/integration_crud.py::FlextOracleOicIntegrationCrudMixin._as_text` (6 edge(s))
- `items` (5 edge(s))
- `map` (5 edge(s))
- `callable` (4 edge(s))

### Incoming

- `that` (14 edge(s))
- `flext-oracle-oic/src/flext_oracle_oic/service.py` (5 edge(s))
- `fail` (4 edge(s))
- `flext-oracle-oic/src/flext_oracle_oic/services/auth.py` (2 edge(s))
- `flext-oracle-oic/src/flext_oracle_oic/services/integration_crud.py` (2 edge(s))
- `flext-oracle-oic/src/flext_oracle_oic/services/integration_lifecycle.py` (2 edge(s))
- `flext-oracle-oic/src/flext_oracle_oic/services/orchestration.py` (2 edge(s))
- `flext-oracle-oic/tests/unit/test_ext_client.py` (2 edge(s))
- `flext-oracle-oic/src/flext_oracle_oic/ext_client.py` (1 edge(s))
- `flext-oracle-oic/src/flext_oracle_oic/services/base.py` (1 edge(s))
- `flext-oracle-oic/src/flext_oracle_oic/services/monitoring.py` (1 edge(s))
- `exception` (1 edge(s))
- `fail_op` (1 edge(s))
- `decode` (1 edge(s))
- `b64decode` (1 edge(s))
