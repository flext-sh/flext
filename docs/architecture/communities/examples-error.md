# examples-error

## Overview

Community of 30 nodes

- **Size**: 30 nodes
- **Cohesion**: 0.1765
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
| ------ | ------ | ------ | ------- |
| validate_user_input | Function | flext-grpc/examples/03_error_handling_patterns.py | 29-48 |
| _raise_username_error | Function | flext-grpc/examples/03_error_handling_patterns.py | 32-34 |
| _raise_email_error | Function | flext-grpc/examples/03_error_handling_patterns.py | 36-38 |
| create_server_config | Function | flext-grpc/examples/03_error_handling_patterns.py | 51-79 |
| _raise_port_error | Function | flext-grpc/examples/03_error_handling_patterns.py | 54-56 |
| _raise_workers_error | Function | flext-grpc/examples/03_error_handling_patterns.py | 58-60 |
| _validate_config | Function | flext-grpc/examples/03_error_handling_patterns.py | 62-67 |
| simulate_connection_error | Function | flext-grpc/examples/03_error_handling_patterns.py | 82-93 |
| _raise_connection_error | Function | flext-grpc/examples/03_error_handling_patterns.py | 85-87 |
| simulate_timeout_error | Function | flext-grpc/examples/03_error_handling_patterns.py | 96-107 |
| _raise_timeout_error | Function | flext-grpc/examples/03_error_handling_patterns.py | 99-101 |
| handle_generic_grpc_error | Function | flext-grpc/examples/03_error_handling_patterns.py | 110-121 |
| _raise_generic_error | Function | flext-grpc/examples/03_error_handling_patterns.py | 113-115 |
| comprehensive_error_handling_pipeline | Function | flext-grpc/examples/03_error_handling_patterns.py | 124-149 |
| error_recovery_patterns | Function | flext-grpc/examples/03_error_handling_patterns.py | 152-175 |
| demonstrate_error_context | Function | flext-grpc/examples/03_error_handling_patterns.py | 178-202 |
| error_handling | Function | flext-grpc/examples/03_error_handling_patterns.py | 205-221 |
| _raise_timeout | Function | flext-grpc/examples/03_error_handling_patterns.py | 209-211 |
| main | Function | flext-grpc/examples/03_error_handling_patterns.py | 224-256 |
| TestsFlextGrpcErrors | Class | flext-grpc/tests/unit/test_errors.py | 20-116 |
| test_base_error_carries_message_and_raises | Test | flext-grpc/tests/unit/test_errors.py | 23-28 |
| test_every_error_raises_as_base_and_reports_message | Test | flext-grpc/tests/unit/test_errors.py | 40-49 |
| test_specialized_error_keeps_its_semantic_category | Test | flext-grpc/tests/unit/test_errors.py | 60-67 |
| test_connection_error_is_not_a_validation_error | Test | flext-grpc/tests/unit/test_errors.py | 69-74 |
| test_validation_error_exposes_field_state | Test | flext-grpc/tests/unit/test_errors.py | 80-87 |
| test_validation_error_field_defaults_to_none | Test | flext-grpc/tests/unit/test_errors.py | 89-92 |
| test_configuration_error_exposes_config_key_state | Test | flext-grpc/tests/unit/test_errors.py | 98-111 |
| test_configuration_error_config_key_defaults_to_none | Test | flext-grpc/tests/unit/test_errors.py | 113-116 |
| GrpcConnectionError | Class | flext-grpc/src/flext_grpc/errors.py | 29-30 |
| GrpcTimeoutError | Class | flext-grpc/src/flext_grpc/errors.py | 32-33 |

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `info` (23 edge(s))
- `str` (12 edge(s))
- `that` (12 edge(s))
- `fail` (10 edge(s))
- `exception` (7 edge(s))
- `error` (6 edge(s))
- `ValidationError` (5 edge(s))
- `ConfigurationError` (5 edge(s))
- `ok` (5 edge(s))
- `warning` (3 edge(s))
- `raises` (3 edge(s))
- `Error` (2 edge(s))
- `type` (2 edge(s))
- `factory` (2 edge(s))
- `scenario_func` (1 edge(s))

### Incoming

- `flext-grpc/examples/03_error_handling_patterns.py` (20 edge(s))
- `that` (12 edge(s))
- `str` (4 edge(s))
- `raises` (3 edge(s))
- `flext-grpc/src/flext_grpc/errors.py` (2 edge(s))
- `ConfigurationError` (2 edge(s))
- `factory` (2 edge(s))
- `ValidationError` (2 edge(s))
- `flext-grpc/tests/unit/test_errors.py` (1 edge(s))
- `Error` (1 edge(s))
- `GrpcConnectionError` (1 edge(s))
- `isinstance` (1 edge(s))
