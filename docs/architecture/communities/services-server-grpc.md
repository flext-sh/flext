# services-server-grpc


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 76 nodes

- **Size**: 76 nodes
- **Cohesion**: 0.3352
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| EchoResponse | Class | flext-grpc/src/flext_grpc/models.py | 44-51 |
| HealthResponse | Class | flext-grpc/src/flext_grpc/models.py | 58-62 |
| FlextGrpcServiceServicer | Class | flext-grpc/src/flext_grpc/proto/stubs.py | 18-19 |
| FlextGrpcServiceStub | Class | flext-grpc/src/flext_grpc/proto/stubs.py | 22-41 |
| __init__ | Function | flext-grpc/src/flext_grpc/proto/stubs.py | 25-27 |
| echo | Function | flext-grpc/src/flext_grpc/proto/stubs.py | 29-33 |
| health_check | Function | flext-grpc/src/flext_grpc/proto/stubs.py | 35-41 |
| add_flext_grpc_service_servicer_to_server | Function | flext-grpc/src/flext_grpc/proto/stubs.py | 44-48 |
| FlextGrpcClient | Class | flext-grpc/src/flext_grpc/services/client.py | 17-163 |
| GrpcClientManager | Class | flext-grpc/src/flext_grpc/services/client.py | 20-141 |
| __init__ | Function | flext-grpc/src/flext_grpc/services/client.py | 23-30 |
| connect | Function | flext-grpc/src/flext_grpc/services/client.py | 32-50 |
| disconnect | Function | flext-grpc/src/flext_grpc/services/client.py | 52-66 |
| client_status | Function | flext-grpc/src/flext_grpc/services/client.py | 68-76 |
| make_call | Function | flext-grpc/src/flext_grpc/services/client.py | 78-141 |
| connect_client | Function | flext-grpc/src/flext_grpc/services/client.py | 147-149 |
| disconnect_client | Function | flext-grpc/src/flext_grpc/services/client.py | 151-153 |
| client_status | Function | flext-grpc/src/flext_grpc/services/client.py | 155-157 |
| make_call | Function | flext-grpc/src/flext_grpc/services/client.py | 159-163 |
| ConnectionPool | Class | flext-grpc/src/flext_grpc/services/connection_pool.py | 18-57 |
| __init__ | Function | flext-grpc/src/flext_grpc/services/connection_pool.py | 21-31 |
| acquire | Function | flext-grpc/src/flext_grpc/services/connection_pool.py | 33-40 |
| cleanup | Function | flext-grpc/src/flext_grpc/services/connection_pool.py | 42-48 |
| release | Function | flext-grpc/src/flext_grpc/services/connection_pool.py | 50-57 |
| _MetricValueModel | Class | flext-grpc/src/flext_grpc/services/metrics.py | 13-16 |
| MetricsCollector | Class | flext-grpc/src/flext_grpc/services/metrics.py | 18-68 |
| __init__ | Function | flext-grpc/src/flext_grpc/services/metrics.py | 21-25 |
| all_metrics | Function | flext-grpc/src/flext_grpc/services/metrics.py | 27-31 |
| metric | Function | flext-grpc/src/flext_grpc/services/metrics.py | 33-42 |
| record_metric | Function | flext-grpc/src/flext_grpc/services/metrics.py | 44-68 |
| _normalize_value | Function | flext-grpc/src/flext_grpc/services/metrics.py | 53-58 |
| FlextGrpcServer | Class | flext-grpc/src/flext_grpc/services/server.py | 24-189 |
| _create_real_servicer | Function | flext-grpc/src/flext_grpc/services/server.py | 28-30 |
| GrpcServerManager | Class | flext-grpc/src/flext_grpc/services/server.py | 32-173 |
| __init__ | Function | flext-grpc/src/flext_grpc/services/server.py | 35-42 |
| server_metrics | Function | flext-grpc/src/flext_grpc/services/server.py | 44-61 |
| start_server | Function | flext-grpc/src/flext_grpc/services/server.py | 63-74 |
| stop_server | Function | flext-grpc/src/flext_grpc/services/server.py | 76-84 |
| _start_new_server | Function | flext-grpc/src/flext_grpc/services/server.py | 86-103 |
| _create_bound_runtime_server | Function | flext-grpc/src/flext_grpc/services/server.py | 105-126 |
| _register_services | Function | flext-grpc/src/flext_grpc/services/server.py | 129-135 |
| _activate_runtime_server | Function | flext-grpc/src/flext_grpc/services/server.py | 137-151 |
| _stop_active_server | Function | flext-grpc/src/flext_grpc/services/server.py | 153-173 |
| start_server | Function | flext-grpc/src/flext_grpc/services/server.py | 175-177 |
| stop_server | Function | flext-grpc/src/flext_grpc/services/server.py | 179-181 |
| server_status | Function | flext-grpc/src/flext_grpc/services/server.py | 183-185 |
| FlextGrpcStream | Class | flext-grpc/src/flext_grpc/services/stream.py | 17-133 |
| _StreamRuntimeState | Class | flext-grpc/src/flext_grpc/services/stream.py | 20-32 |
| _new_stream_buffer | Function | flext-grpc/src/flext_grpc/services/stream.py | 35-36 |
| GrpcStreamManager | Class | flext-grpc/src/flext_grpc/services/stream.py | 38-107 |

*... and 26 more members.*

## Execution Flows

- **disconnect_client** (criticality: 0.57, depth: 1)

## Dependencies

### Outgoing

- `ok` (19 edge(s))
- `that` (17 edge(s))
- `fail` (12 edge(s))
- `runtime_failure_message` (9 edge(s))
- `str` (7 edge(s))
- `unwrap` (7 edge(s))
- `fail_op` (6 edge(s))
- `super` (5 edge(s))
- `from_values` (5 edge(s))
- `time` (5 edge(s))
- `m.Value` (4 edge(s))
- `create_stream` (4 edge(s))
- `s` (3 edge(s))
- `run_runtime` (3 edge(s))
- `call_runtime` (3 edge(s))

### Incoming

- `that` (17 edge(s))
- `unwrap` (7 edge(s))
- `ok` (7 edge(s))
- `flext-grpc/src/flext_grpc/proto/stubs.py` (3 edge(s))
- `flext-grpc/src/flext_grpc/api.py` (3 edge(s))
- `flext-grpc/src/flext_grpc/services/stream.py` (3 edge(s))
- `create_stream` (3 edge(s))
- `fail` (3 edge(s))
- `flext-grpc/src/flext_grpc/models.py` (2 edge(s))
- `flext-grpc/src/flext_grpc/services/client.py` (2 edge(s))
- `flext-grpc/src/flext_grpc/services/connection_pool.py` (2 edge(s))
- `flext-grpc/src/flext_grpc/services/metrics.py` (2 edge(s))
- `flext-grpc/src/flext_grpc/services/server.py` (2 edge(s))
- `flext-grpc/tests/conftest.py` (2 edge(s))
- `parse_address` (2 edge(s))
