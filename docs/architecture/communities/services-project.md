# services-project


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 70 nodes

- **Size**: 70 nodes
- **Cohesion**: 0.1734
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextMeltanoAbstractions | Class | flext-meltano/src/flext_meltano/services/abstractions.py | 15-222 |
| create_abstractions_instance | Function | flext-meltano/src/flext_meltano/services/abstractions.py | 19-23 |
| process_tap_config | Function | flext-meltano/src/flext_meltano/services/abstractions.py | 27-31 |
| build_tap_instance | Function | flext-meltano/src/flext_meltano/services/abstractions.py | 33-38 |
| discover_streams | Function | flext-meltano/src/flext_meltano/services/abstractions.py | 40-82 |
| _run_discover_streams | Function | flext-meltano/src/flext_meltano/services/abstractions.py | 45-72 |
| sync_stream | Function | flext-meltano/src/flext_meltano/services/abstractions.py | 84-132 |
| _run_sync_stream | Function | flext-meltano/src/flext_meltano/services/abstractions.py | 92-118 |
| create_tap_from_config | Function | flext-meltano/src/flext_meltano/services/abstractions.py | 134-160 |
| generate_catalog | Function | flext-meltano/src/flext_meltano/services/abstractions.py | 162-187 |
| fetch_stream_by_name | Function | flext-meltano/src/flext_meltano/services/abstractions.py | 189-205 |
| list_streams | Function | flext-meltano/src/flext_meltano/services/abstractions.py | 207-215 |
| _extract_raw_streams | Function | flext-meltano/src/flext_meltano/services/abstractions.py | 218-222 |
| FlextMeltanoPluginDiscoveryMixin | Class | flext-meltano/src/flext_meltano/services/meltano_plugin_discovery.py | 14-147 |
| _is_meltano_project | Function | flext-meltano/src/flext_meltano/services/meltano_plugin_discovery.py | 18-22 |
| _build_plugin_info | Function | flext-meltano/src/flext_meltano/services/meltano_plugin_discovery.py | 25-37 |
| _extract_plugin_info | Function | flext-meltano/src/flext_meltano/services/meltano_plugin_discovery.py | 40-60 |
| discover_plugins | Function | flext-meltano/src/flext_meltano/services/meltano_plugin_discovery.py | 62-71 |
| _discover_plugins | Function | flext-meltano/src/flext_meltano/services/meltano_plugin_discovery.py | 73-114 |
| fetch_plugin_info | Function | flext-meltano/src/flext_meltano/services/meltano_plugin_discovery.py | 116-147 |
| _run_fetch_plugin_info | Function | flext-meltano/src/flext_meltano/services/meltano_plugin_discovery.py | 121-140 |
| FlextMeltanoComponentService | Class | flext-meltano/src/flext_meltano/services/meltano_plugins.py | 18-99 |
| _validate_plugin_type | Function | flext-meltano/src/flext_meltano/services/meltano_plugins.py | 26-33 |
| add_plugin | Function | flext-meltano/src/flext_meltano/services/meltano_plugins.py | 35-51 |
| execute | Function | flext-meltano/src/flext_meltano/services/meltano_plugins.py | 54-56 |
| _build_plugin_addition_result | Function | flext-meltano/src/flext_meltano/services/meltano_plugins.py | 58-73 |
| _execute_plugin_addition | Function | flext-meltano/src/flext_meltano/services/meltano_plugins.py | 75-88 |
| _log_plugin_addition_start | Function | flext-meltano/src/flext_meltano/services/meltano_plugins.py | 90-99 |
| FlextMeltanoProjectService | Class | flext-meltano/src/flext_meltano/services/project_service.py | 28-246 |
| _abstractions | Function | flext-meltano/src/flext_meltano/services/project_service.py | 32-34 |
| _validate_project_creation_params | Function | flext-meltano/src/flext_meltano/services/project_service.py | 37-52 |
| _validate_project_parameters | Function | flext-meltano/src/flext_meltano/services/project_service.py | 55-66 |
| _validate_project_path | Function | flext-meltano/src/flext_meltano/services/project_service.py | 69-75 |
| validate_project | Function | flext-meltano/src/flext_meltano/services/project_service.py | 78-80 |
| create_project | Function | flext-meltano/src/flext_meltano/services/project_service.py | 82-101 |
| _write_project_files | Function | flext-meltano/src/flext_meltano/services/project_service.py | 104-122 |
| create_temporary_project | Function | flext-meltano/src/flext_meltano/services/project_service.py | 124-170 |
| build_service_execution_payload | Function | flext-meltano/src/flext_meltano/services/project_service.py | 173-185 |
| execute | Function | flext-meltano/src/flext_meltano/services/project_service.py | 188-197 |
| initialize_project | Function | flext-meltano/src/flext_meltano/services/project_service.py | 199-218 |
| _build_creation_result | Function | flext-meltano/src/flext_meltano/services/project_service.py | 220-238 |
| _initialize_project_instance | Function | flext-meltano/src/flext_meltano/services/project_service.py | 240-242 |
| _load_project_from_path | Function | flext-meltano/src/flext_meltano/services/project_service.py | 244-246 |
| FlextMeltanoValidators | Class | flext-meltano/src/flext_meltano/services/validators.py | 17-87 |
| validate_component_rules | Function | flext-meltano/src/flext_meltano/services/validators.py | 21-29 |
| validate_pipeline_project_business_rules | Function | flext-meltano/src/flext_meltano/services/validators.py | 32-40 |
| validate_pipeline_project_structure | Function | flext-meltano/src/flext_meltano/services/validators.py | 43-66 |
| validate_plugin_config | Function | flext-meltano/src/flext_meltano/services/validators.py | 69-71 |
| validate_transformation_business_rules | Function | flext-meltano/src/flext_meltano/services/validators.py | 74-82 |
| execute | Function | flext-meltano/src/flext_meltano/services/validators.py | 85-87 |

*... and 20 more members.*

## Execution Flows

- **validate_project** (criticality: 0.69, depth: 1)

## Dependencies

### Outgoing

- `ok` (39 edge(s))
- `that` (30 edge(s))
- `fail` (19 edge(s))
- `from_failure` (14 edge(s))
- `str` (14 edge(s))
- `validate_plugin_config` (10 edge(s))
- `exception` (7 edge(s))
- `exists` (7 edge(s))
- `model_validate` (6 edge(s))
- `info` (6 edge(s))
- `flext-meltano/src/flext_meltano/__init__.py::settings` (6 edge(s))
- `get` (5 edge(s))
- `strip` (5 edge(s))
- `fail_operation` (5 edge(s))
- `validate_pipeline_project_business_rules` (5 edge(s))

### Incoming

- `that` (30 edge(s))
- `flext-meltano/tests/unit/test_validators.py::TestsFlextMeltanoValidators` (14 edge(s))
- `ok` (13 edge(s))
- `validate_plugin_config` (10 edge(s))
- `fail` (9 edge(s))
- `validate_pipeline_project_business_rules` (5 edge(s))
- `flext-meltano/src/flext_meltano/api.py` (4 edge(s))
- `flext-meltano/tests/unit/test_api.py::TestsFlextMeltanoApi` (3 edge(s))
- `create_project` (3 edge(s))
- `flext-meltano/tests/unit/test_tap_abstractions.py::TestFlextMeltanoAbstractionsComplete` (3 edge(s))
- `hasattr` (3 edge(s))
- `validate_transformation_business_rules` (3 edge(s))
- `flext-meltano/src/flext_meltano/services/meltano_plugins.py` (2 edge(s))
- `Path` (2 edge(s))
- `flext-meltano/src/flext_meltano/services/abstractions.py` (1 edge(s))
