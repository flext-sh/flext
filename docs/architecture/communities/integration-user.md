# integration-user

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 25 nodes

- **Size**: 25 nodes
- **Cohesion**: 0.2185
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
| ------ | ------ | ------ | ------- |
| mock_external_service | Function | flext-core/tests/conftest.py | 40-42 |
| TestsFlextUserServiceEntity | Class | flext-core/tests/integration/service_fixtures.py | 22-28 |
| TestsFlextUserQueryService | Class | flext-core/tests/integration/service_fixtures.py | 31-73 |
| execute | Function | flext-core/tests/integration/service_fixtures.py | 41-45 |
| fetch_user | Function | flext-core/tests/integration/service_fixtures.py | 47-60 |
| apply_user_data | Function | flext-core/tests/integration/service_fixtures.py | 62-64 |
| configure_failure_mode | Function | flext-core/tests/integration/service_fixtures.py | 66-68 |
| call_count | Function | flext-core/tests/integration/service_fixtures.py | 71-73 |
| TestsFlextCoreService | Class | flext-core/tests/integration/test_service.py | 28-225 |
| test_user_service_execute_reports_available | Test | flext-core/tests/integration/test_service.py | 40-47 |
| test_user_service_execute_reports_unavailable_in_failure_mode | Test | flext-core/tests/integration/test_service.py | 49-58 |
| test_fetch_user_derives_default_entity | Test | flext-core/tests/integration/test_service.py | 67-78 |
| test_fetch_user_returns_applied_custom_entity | Test | flext-core/tests/integration/test_service.py | 80-95 |
| test_fetch_user_fails_in_failure_mode | Test | flext-core/tests/integration/test_service.py | 97-106 |
| test_fetch_user_counts_each_call | Test | flext-core/tests/integration/test_service.py | 108-117 |
| test_fetch_user_result_supports_combinators | Test | flext-core/tests/integration/test_service.py | 119-131 |
| test_notification_execute_reports_sent | Test | flext-core/tests/integration/test_service.py | 136-143 |
| test_notification_send_records_recipient | Test | flext-core/tests/integration/test_service.py | 145-155 |
| test_notification_send_fails_in_failure_mode | Test | flext-core/tests/integration/test_service.py | 157-167 |
| test_container_resolves_bound_services_functionally | Test | flext-core/tests/integration/test_service.py | 172-207 |
| test_external_service_processes_user_email | Test | flext-core/tests/integration/test_service.py | 212-225 |
| FunctionalExternalService | Class | flext-core/tests/_utilities/contracts.py | 59-91 |
| **init** | Function | flext-core/tests/_utilities/contracts.py | 66-69 |
| process | Function | flext-core/tests/_utilities/contracts.py | 71-87 |
| get_call_count | Function | flext-core/tests/_utilities/contracts.py | 89-91 |

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `assert_success` (11 edge(s))
- `UserQueryService` (9 edge(s))
- `ok` (4 edge(s))
- `NotificationService` (4 edge(s))
- `fail` (3 edge(s))
- `send` (3 edge(s))
- `configure_failure_mode` (3 edge(s))
- `assert_failure` (3 edge(s))
- `execute` (3 edge(s))
- `UserServiceEntity` (2 edge(s))
- `bind` (2 edge(s))
- `resolve` (2 edge(s))
- `append` (1 edge(s))
- `m.BaseModel` (1 edge(s))
- `_ServiceLifecycleCases` (1 edge(s))

### Incoming

- `assert_success` (11 edge(s))
- `UserQueryService` (9 edge(s))
- `fetch_user` (8 edge(s))
- `NotificationService` (4 edge(s))
- `send` (3 edge(s))
- `configure_failure_mode` (3 edge(s))
- `assert_failure` (3 edge(s))
- `execute` (3 edge(s))
- `flext-core/tests/integration/service_fixtures.py` (2 edge(s))
- `apply_user_data` (2 edge(s))
- `UserServiceEntity` (2 edge(s))
- `bind` (2 edge(s))
- `resolve` (2 edge(s))
- `flext-core/tests/_utilities/contracts.py` (1 edge(s))
- `flext-core/tests/conftest.py` (1 edge(s))
