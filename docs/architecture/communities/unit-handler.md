# unit-handler


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 92 nodes

- **Size**: 92 nodes
- **Cohesion**: 0.3545
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| ConcreteTestHandler | Class | flext-core/tests/unit/_handlers_support.py | 20-92 |
| __init__ | Function | flext-core/tests/unit/_handlers_support.py | 23-24 |
| dispatch_message | Function | flext-core/tests/unit/_handlers_support.py | 27-68 |
| execute | Function | flext-core/tests/unit/_handlers_support.py | 71-78 |
| handle | Function | flext-core/tests/unit/_handlers_support.py | 81-84 |
| validate_message | Function | flext-core/tests/unit/_handlers_support.py | 87-92 |
| ValidationTestHandler | Class | flext-core/tests/unit/_handlers_support.py | 94-110 |
| __init__ | Function | flext-core/tests/unit/_handlers_support.py | 97-98 |
| validate_message | Function | flext-core/tests/unit/_handlers_support.py | 101-106 |
| handle | Function | flext-core/tests/unit/_handlers_support.py | 109-110 |
| FailingTestHandler | Class | flext-core/tests/unit/_handlers_support.py | 112-122 |
| __init__ | Function | flext-core/tests/unit/_handlers_support.py | 115-116 |
| handle | Function | flext-core/tests/unit/_handlers_support.py | 119-122 |
| TestsFlextHandlersDispatch | Class | flext-core/tests/unit/test_handlers_dispatch.py | 20-171 |
| _command_settings | Function | flext-core/tests/unit/test_handlers_dispatch.py | 24-30 |
| test_execute_returns_processed_payload_for_dict_message | Test | flext-core/tests/unit/test_handlers_dispatch.py | 32-51 |
| DictHandler | Class | flext-core/tests/unit/test_handlers_dispatch.py | 33-44 |
| execute | Function | flext-core/tests/unit/test_handlers_dispatch.py | 35-36 |
| handle | Function | flext-core/tests/unit/test_handlers_dispatch.py | 39-44 |
| test_execute_returns_processed_payload_for_string_message | Test | flext-core/tests/unit/test_handlers_dispatch.py | 53-60 |
| test_execute_rejects_none_message_via_validation | Test | flext-core/tests/unit/test_handlers_dispatch.py | 62-69 |
| test_dispatch_matching_operation_returns_processed_payload | Test | flext-core/tests/unit/test_handlers_dispatch.py | 71-78 |
| test_dispatch_incompatible_operation_fails | Test | flext-core/tests/unit/test_handlers_dispatch.py | 87-96 |
| test_dispatch_rejects_unhandleable_message_type | Test | flext-core/tests/unit/test_handlers_dispatch.py | 98-113 |
| RestrictiveHandler | Class | flext-core/tests/unit/test_handlers_dispatch.py | 99-103 |
| can_handle | Function | flext-core/tests/unit/test_handlers_dispatch.py | 101-103 |
| test_dispatch_propagates_validation_failure | Test | flext-core/tests/unit/test_handlers_dispatch.py | 115-131 |
| ValidationFailingHandler | Class | flext-core/tests/unit/test_handlers_dispatch.py | 116-120 |
| validate_message | Function | flext-core/tests/unit/test_handlers_dispatch.py | 118-120 |
| test_dispatch_converts_handler_exception_to_critical_failure | Test | flext-core/tests/unit/test_handlers_dispatch.py | 133-149 |
| ExceptionHandler | Class | flext-core/tests/unit/test_handlers_dispatch.py | 134-139 |
| handle | Function | flext-core/tests/unit/test_handlers_dispatch.py | 136-139 |
| test_flexible_handler_accepts_any_message_type | Test | flext-core/tests/unit/test_handlers_dispatch.py | 152-159 |
| test_validate_message_reports_success_and_failure | Test | flext-core/tests/unit/test_handlers_dispatch.py | 161-171 |
| TestsFlextCoreHandlersFactory | Class | flext-core/tests/unit/test_handlers_factory.py | 16-251 |
| test_callable_result_is_wrapped_in_success | Test | flext-core/tests/unit/test_handlers_factory.py | 19-35 |
| simple_handler | Function | flext-core/tests/unit/test_handlers_factory.py | 21-24 |
| test_callable_returning_result_is_passed_through | Test | flext-core/tests/unit/test_handlers_factory.py | 37-56 |
| result_handler | Function | flext-core/tests/unit/test_handlers_factory.py | 39-46 |
| test_callable_raising_produces_failure_result | Test | flext-core/tests/unit/test_handlers_factory.py | 58-74 |
| failing_handler | Function | flext-core/tests/unit/test_handlers_factory.py | 60-63 |
| test_invalid_mode_raises_validation_error | Test | flext-core/tests/unit/test_handlers_factory.py | 76-89 |
| invalid_handler | Function | flext-core/tests/unit/test_handlers_factory.py | 78-81 |
| test_handler_name_defaults_to_callable_name | Test | flext-core/tests/unit/test_handlers_factory.py | 91-102 |
| named_callable | Function | flext-core/tests/unit/test_handlers_factory.py | 93-96 |
| any_callable | Function | flext-core/tests/unit/test_handlers_factory.py | 128-129 |
| test_mode_reflects_requested_handler_type | Test | flext-core/tests/unit/test_handlers_factory.py | 124-137 |
| test_execute_returns_processed_success | Test | flext-core/tests/unit/test_handlers_factory.py | 139-148 |
| test_execute_propagates_validation_failure | Test | flext-core/tests/unit/test_handlers_factory.py | 150-159 |
| test_dispatch_message_runs_pipeline_to_success | Test | flext-core/tests/unit/test_handlers_factory.py | 172-186 |

*... and 42 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `assert_success` (20 edge(s))
- `create_handler_config` (16 edge(s))
- `create_from_callable` (14 edge(s))
- `assert_failure` (12 edge(s))
- `isinstance` (11 edge(s))
- `ok` (11 edge(s))
- `handle` (10 edge(s))
- `fail` (8 edge(s))
- `validate_message` (8 edge(s))
- `decode` (7 edge(s))
- `fail_op` (6 edge(s))
- `flext-core/tests/unit/test_handlers_dispatch.py::TestsFlextHandlersDispatch.ConcreteTestHandler` (6 edge(s))
- `TestsFlextFlextHandlers` (5 edge(s))
- `super` (4 edge(s))
- `format` (4 edge(s))

### Incoming

- `assert_success` (20 edge(s))
- `create_from_callable` (14 edge(s))
- `create_handler_config` (14 edge(s))
- `assert_failure` (12 edge(s))
- `handle` (10 edge(s))
- `validate_message` (8 edge(s))
- `flext-core/tests/unit/test_handlers_dispatch.py::TestsFlextHandlersDispatch.ConcreteTestHandler` (6 edge(s))
- `flext-core/tests/unit/test_handlers_dispatch.py` (5 edge(s))
- `flext-core/tests/unit/test_handlers_factory.py::TestsFlextCoreHandlersFactory.ConcreteTestHandler` (4 edge(s))
- `flext-core/tests/unit/test_handlers_validation_context.py` (4 edge(s))
- `flext-core/tests/unit/_handlers_support.py` (3 edge(s))
- `execute` (3 edge(s))
- `flext-core/tests/unit/test_handlers_lifecycle.py::TestsFlextHandlersLifecycle.ConcreteTestHandler` (3 edge(s))
- `ok` (3 edge(s))
- `that` (3 edge(s))
