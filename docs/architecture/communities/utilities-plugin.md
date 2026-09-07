# utilities-plugin


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 88 nodes

- **Size**: 88 nodes
- **Cohesion**: 0.2505
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| Rules | Class | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 21-44 |
| validate_business_rules | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 25-44 |
| PluginExecution | Class | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 46-90 |
| __init__ | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 49-65 |
| create | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 68-75 |
| mark_completed | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 77-85 |
| mark_started | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 87-90 |
| PluginRegistry | Class | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 92-199 |
| __init__ | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 98-100 |
| create | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 103-120 |
| get | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 122-135 |
| list_plugins | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 137-155 |
| register | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 157-179 |
| unregister | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 181-187 |
| fetch_plugin | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 189-199 |
| Plugin | Class | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 201-213 |
| status | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 205-209 |
| active | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 211-213 |
| PluginPlatformService | Class | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 215-703 |
| _to_general_mapping | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 238-245 |
| _loader_payload_mapping | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 248-271 |
| __init__ | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 273-283 |
| with_discovery | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 285-288 |
| with_loader | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 290-293 |
| with_executor | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 295-298 |
| inject_execution | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 300-304 |
| reset_registry | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 306-308 |
| discovery | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 311-313 |
| executions | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 316-318 |
| executor | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 321-323 |
| platform_status | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 326-337 |
| loader | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 340-342 |
| plugins | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 345-347 |
| registry | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 350-354 |
| _get_service_config_type | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 357-359 |
| cleanup_executions | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 361-370 |
| discover_plugins | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 372-407 |
| discover_and_validate | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 377-391 |
| create_plugins_from_data | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 393-396 |
| execute | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 410-420 |
| execute_plugin | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 422-459 |
| get_plugin_result | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 430-433 |
| create_execution_from_plugin | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 435-438 |
| prepare_execution_result | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 440-443 |
| execute_with_executor_result | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 445-448 |
| fetch_execution | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 461-468 |
| fetch_plugin | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 470-473 |
| fetch_plugin_status | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 475-478 |
| list_running_executions | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 480-488 |
| resolve_plugin_active | Function | flext-plugin/src/flext_plugin/_utilities/plugin_platform.py | 490-493 |

*... and 38 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (34 edge(s))
- `str` (16 edge(s))
- `ok` (15 edge(s))
- `fail` (14 edge(s))
- `PluginPlatformService` (11 edge(s))
- `flat_map` (8 edge(s))
- `create` (8 edge(s))
- `len` (7 edge(s))
- `getattr` (6 edge(s))
- `validate_python` (5 edge(s))
- `json_mapping_adapter` (5 edge(s))
- `values` (5 edge(s))
- `inject_execution` (5 edge(s))
- `map` (4 edge(s))
- `from_result` (4 edge(s))

### Incoming

- `that` (34 edge(s))
- `flext-plugin/tests/unit/test_platform_service.py::TestsFlextPluginPlatformService` (11 edge(s))
- `PluginPlatformService` (11 edge(s))
- `create` (8 edge(s))
- `flext-plugin/src/flext_plugin/_utilities/plugin_platform.py` (5 edge(s))
- `inject_execution` (5 edge(s))
- `mark_completed` (4 edge(s))
- `mark_started` (4 edge(s))
- `str` (4 edge(s))
- `flext-plugin/tests/unit/test_platform_service.py::TestsFlextPluginPlatformExecution` (3 edge(s))
- `flext-plugin/tests/unit/test_platform_service.py::TestsFlextPluginPlatformService._make_plugin` (3 edge(s))
- `register_plugin` (3 edge(s))
- `fetch_execution` (3 edge(s))
- `load_plugin` (3 edge(s))
- `flext-plugin/src/flext_plugin/api.py` (2 edge(s))
