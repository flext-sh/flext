# flext-core-container

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 203 nodes

- **Size**: 203 nodes
- **Cohesion**: 0.3788
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextContainer | Class | flext-core/src/flext_core/container.py | 41-637 |
| **new** | Function | flext-core/src/flext_core/container.py | 83-91 |
| settings | Function | flext-core/src/flext_core/container.py | 95-97 |
| context | Function | flext-core/src/flext_core/container.py | 101-103 |
| provide | Function | flext-core/src/flext_core/container.py | 107-110 |
| reset_for_testing | Function | flext-core/src/flext_core/container.py | 113-116 |
| logger | Function | flext-core/src/flext_core/container.py | 119-130 |
| _matches_service_type | Function | flext-core/src/flext_core/container.py | 133-137 |
| _resolve_callable | Function | flext-core/src/flext_core/container.py | 139-155 |
| resolve | Function | flext-core/src/flext_core/container.py | 168-203 |
| snapshot | Function | flext-core/src/flext_core/container.py | 206-211 |
| has | Function | flext-core/src/flext_core/container.py | 214-220 |
| initialize_di_components | Function | flext-core/src/flext_core/container.py | 222-232 |
| initialize_registrations | Function | flext-core/src/flext_core/container.py | 234-274 |
| names | Function | flext-core/src/flext_core/container.py | 277-287 |
| bind | Function | flext-core/src/flext_core/container.py | 290-299 |
| factory | Function | flext-core/src/flext_core/container.py | 302-336 |
| normalized_factory | Function | flext-core/src/flext_core/container.py | 313-321 |
| resource | Function | flext-core/src/flext_core/container.py | 339-355 |
| _update_registered_object_service | Function | flext-core/src/flext_core/container.py | 357-368 |
| register_existing_providers | Function | flext-core/src/flext_core/container.py | 370-393 |
| register_core_services | Function | flext-core/src/flext_core/container.py | 396-411 |
| scope | Function | flext-core/src/flext_core/container.py | 414-471 |
| sync_config_to_di | Function | flext-core/src/flext_core/container.py | 473-479 |
| drop | Function | flext-core/src/flext_core/container.py | 482-499 |
| wire | Function | flext-core/src/flext_core/container.py | 502-512 |
| dispatcher | Function | flext-core/src/flext_core/container.py | 515-526 |
| **init** | Function | flext-core/src/flext_core/container.py | 528-541 |
| shared | Function | flext-core/src/flext_core/container.py | 544-562 |
| _resolve_caller_module | Function | flext-core/src/flext_core/container.py | 565-570 |
| _auto_register_module_factories | Function | flext-core/src/flext_core/container.py | 573-584 |
| _apply_explicit_bootstrap | Function | flext-core/src/flext_core/container.py | 586-600 |
| clear | Function | flext-core/src/flext_core/container.py | 603-623 |
| apply | Function | flext-core/src/flext_core/container.py | 626-637 |
| FlextContext | Class | flext-core/src/flext_core/context.py | 29-308 |
| set | Function | flext-core/src/flext_core/context.py | 52-55 |
| get | Function | flext-core/src/flext_core/context.py | 57-64 |
| has | Function | flext-core/src/flext_core/context.py | 66-68 |
| keys | Function | flext-core/src/flext_core/context.py | 70-72 |
| values | Function | flext-core/src/flext_core/context.py | 74-76 |
| items | Function | flext-core/src/flext_core/context.py | 78-80 |
| resolve_metadata | Function | flext-core/src/flext_core/context.py | 82-87 |
| apply_metadata | Function | flext-core/src/flext_core/context.py | 89-99 |
| remove | Function | flext-core/src/flext_core/context.py | 101-103 |
| clear | Function | flext-core/src/flext_core/context.py | 105-107 |
| merge | Function | flext-core/src/flext_core/context.py | 109-115 |
| clone | Function | flext-core/src/flext_core/context.py | 117-121 |
| export | Function | flext-core/src/flext_core/context.py | 123-127 |
| create | Function | flext-core/src/flext_core/context.py | 130-135 |
| resolve_container | Function | flext-core/src/flext_core/context.py | 138-143 |

*... and 153 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (77 edge(s))
- `ok` (30 edge(s))
- `str` (25 edge(s))
- `get` (22 edge(s))
- `set` (21 edge(s))
- `FlextContext` (18 edge(s))
- `isinstance` (15 edge(s))
- `fail` (15 edge(s))
- `FlextContainer` (14 edge(s))
- `items` (12 edge(s))
- `hasattr` (10 edge(s))
- `model_copy` (9 edge(s))
- `update` (8 edge(s))
- `assert_success` (8 edge(s))
- `from_result` (7 edge(s))

### Incoming

- `that` (77 edge(s))
- `ok` (20 edge(s))
- `set` (20 edge(s))
- `FlextContext` (18 edge(s))
- `get` (17 edge(s))
- `flext-core/tests/unit/test_context.py::TestsFlextCoreContext` (16 edge(s))
- `FlextContainer` (14 edge(s))
- `fail` (11 edge(s))
- `assert_success` (8 edge(s))
- `inject` (6 edge(s))
- `log_operation` (6 edge(s))
- `callable` (6 edge(s))
- `resolve` (5 edge(s))
- `create_factory` (5 edge(s))
- `assert_failure` (5 edge(s))
