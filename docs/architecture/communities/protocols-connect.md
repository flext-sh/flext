# protocols-connect

## Overview

Community of 31 nodes

- **Size**: 31 nodes
- **Cohesion**: 0.3438
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
| ------ | ------ | ------ | ------- |
| TestsFlextApiTransportsCharacterization | Class | flext-api/tests/unit/test_transports_characterization.py | 20-151 |
| transport | Function | flext-api/tests/unit/test_transports_characterization.py | 24-26 |
| test_connect_rejects_empty_url | Test | flext-api/tests/unit/test_transports_characterization.py | 28-35 |
| test_connect_accepts_url_and_echoes_it | Test | flext-api/tests/unit/test_transports_characterization.py | 45-54 |
| test_connect_accepts_documented_client_options | Test | flext-api/tests/unit/test_transports_characterization.py | 66-76 |
| test_disconnect_after_connect_succeeds | Test | flext-api/tests/unit/test_transports_characterization.py | 78-87 |
| test_disconnect_without_connect_is_idempotent | Test | flext-api/tests/unit/test_transports_characterization.py | 89-96 |
| test_disconnect_twice_stays_successful | Test | flext-api/tests/unit/test_transports_characterization.py | 98-109 |
| test_send_without_connect_reports_disconnected_failure | Test | flext-api/tests/unit/test_transports_characterization.py | 111-118 |
| test_send_after_disconnect_reports_disconnected_failure | Test | flext-api/tests/unit/test_transports_characterization.py | 120-130 |
| test_request_model_without_connect_reports_disconnected_failure | Test | flext-api/tests/unit/test_transports_characterization.py | 132-145 |
| test_transport_satisfies_transport_plugin_protocol | Test | flext-api/tests/unit/test_transports_characterization.py | 147-151 |
| FlextApiTransportsConfigMixin | Class | flext-api/src/flext_api/_protocols/_transports_config.py | 15-48 |
| _client_timeout | Function | flext-api/src/flext_api/_protocols/_transports_config.py | 19-26 |
| _client_follow_redirects | Function | flext-api/src/flext_api/_protocols/_transports_config.py | 29-32 |
| _client_max_redirects | Function | flext-api/src/flext_api/_protocols/_transports_config.py | 35-38 |
| _response_mapping | Function | flext-api/src/flext_api/_protocols/_transports_config.py | 41-48 |
| FlextApiTransportsRequestMixin | Class | flext-api/src/flext_api/_protocols/_transports_request.py | 22-154 |
| _extract_request_params | Function | flext-api/src/flext_api/_protocols/_transports_request.py | 27-43 |
| _request_payload | Function | flext-api/src/flext_api/_protocols/_transports_request.py | 46-69 |
| _request_model | Function | flext-api/src/flext_api/_protocols/_transports_request.py | 71-86 |
| _httpx_response | Function | flext-api/src/flext_api/_protocols/_transports_request.py | 88-104 |
| _request_json_body | Function | flext-api/src/flext_api/_protocols/_transports_request.py | 107-124 |
| _request_content_body | Function | flext-api/src/flext_api/_protocols/_transports_request.py | 127-144 |
| _response_model | Function | flext-api/src/flext_api/_protocols/_transports_request.py | 147-154 |
| FlextWebTransport | Class | flext-api/src/flext_api/_protocols/transports.py | 31-102 |
| **init** | Function | flext-api/src/flext_api/_protocols/transports.py | 39-41 |
| connect | Function | flext-api/src/flext_api/_protocols/transports.py | 44-59 |
| disconnect | Function | flext-api/src/flext_api/_protocols/transports.py | 62-71 |
| send | Function | flext-api/src/flext_api/_protocols/transports.py | 74-95 |
| request_model | Function | flext-api/src/flext_api/_protocols/transports.py | 97-102 |

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `fail` (9 edge(s))
- `ok` (8 edge(s))
- `connect` (6 edge(s))
- `disconnect` (5 edge(s))
- `isinstance` (4 edge(s))
- `fail_op` (4 edge(s))
- `str` (4 edge(s))
- `get` (3 edge(s))
- `request` (2 edge(s))
- `send` (2 edge(s))
- `float` (1 edge(s))
- `model_validate` (1 edge(s))
- `create_response` (1 edge(s))
- `dict` (1 edge(s))
- `pb.TransportPlugin` (1 edge(s))

### Incoming

- `connect` (6 edge(s))
- `disconnect` (5 edge(s))
- `str` (4 edge(s))
- `flext-api/src/flext_api/_protocols/transports.py` (3 edge(s))
- `send` (2 edge(s))
- `flext-api/src/flext_api/_protocols/_transports_config.py` (1 edge(s))
- `flext-api/src/flext_api/_protocols/_transports_request.py` (1 edge(s))
- `flext-api/tests/unit/test_transports_characterization.py` (1 edge(s))
- `unwrap` (1 edge(s))
- `HttpRequest` (1 edge(s))
- `request_model` (1 edge(s))
- `isinstance` (1 edge(s))
