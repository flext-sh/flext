# utilities-flext

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 590 nodes

- **Size**: 590 nodes
- **Cohesion**: 0.1590
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| test_config_load_yaml_expands_env | Test | flext-cli/tests/unit/test_config_engine.py | 106-119 |
| FlextDecoratorsLogging | Class | flext-core/src/flext_core/_decorators/_logging.py | 23-156 |
| log_operation | Function | flext-core/src/flext_core/_decorators/_logging.py | 27-76 |
| decorator | Function | flext-core/src/flext_core/_decorators/_logging.py | 146-154 |
| wrapper | Function | flext-core/src/flext_core/_decorators/_logging.py | 150-152 |
| _resolve_correlation_id | Function | flext-core/src/flext_core/_decorators/_logging.py | 79-84 |
| _execute_logged_call | Function | flext-core/src/flext_core/_decorators/_logging.py | 87-138 |
| with_correlation | Function | flext-core/src/flext_core/_decorators/_logging.py | 141-156 |
| ContextRuntimeState | Class | flext-core/src/flext_core/_models/_context/__scope_parts/flextmodelscontextscope_part_02.py | 24-165 |
| create_default | Function | flext-core/src/flext_core/_models/_context/__scope_parts/flextmodelscontextscope_part_02.py | 87-112 |
| resolve_scope_var | Function | flext-core/src/flext_core/_models/_context/__scope_parts/flextmodelscontextscope_part_02.py | 114-133 |
| with_operation_update | Function | flext-core/src/flext_core/_models/_context/__scope_parts/flextmodelscontextscope_part_02.py | 135-165 |
| GuardCheckSpec | Class | flext-core/src/flext_core/_models/collections.py | 23-145 |
| _MappingRootBase | Class | flext-core/src/flext_core/_models/containers.py | 51-111 |
| **getitem** | Function | flext-core/src/flext_core/_models/containers.py | 60-61 |
| **setitem** | Function | flext-core/src/flext_core/_models/containers.py | 63-64 |
| **delitem** | Function | flext-core/src/flext_core/_models/containers.py | 66-67 |
| **contains** | Function | flext-core/src/flext_core/_models/containers.py | 69-70 |
| **len** | Function | flext-core/src/flext_core/_models/containers.py | 72-73 |
| **bool** | Function | flext-core/src/flext_core/_models/containers.py | 75-76 |
| keys | Function | flext-core/src/flext_core/_models/containers.py | 78-79 |
| values | Function | flext-core/src/flext_core/_models/containers.py | 81-82 |
| items | Function | flext-core/src/flext_core/_models/containers.py | 84-85 |
| get | Function | flext-core/src/flext_core/_models/containers.py | 87-90 |
| update | Function | flext-core/src/flext_core/_models/containers.py | 92-95 |
| clear | Function | flext-core/src/flext_core/_models/containers.py | 97-98 |
| pop | Function | flext-core/src/flext_core/_models/containers.py | 100-103 |
| popitem | Function | flext-core/src/flext_core/_models/containers.py | 105-106 |
| setdefault | Function | flext-core/src/flext_core/_models/containers.py | 108-111 |
| ConfigMap | Class | flext-core/src/flext_core/_models/containers.py | 121-127 |
| ObjectList | Class | flext-core/src/flext_core/_models/containers.py | 129-144 |
| **len** | Function | flext-core/src/flext_core/_models/containers.py | 140-141 |
| **bool** | Function | flext-core/src/flext_core/_models/containers.py | 143-144 |
| Entry | Class | flext-core/src/flext_core/_models/domain_event.py | 29-56 |
| Entity | Class | flext-core/src/flext_core/_models/entity.py | 37-74 |
| **eq** | Function | flext-core/src/flext_core/_models/entity.py | 60-64 |
| **hash** | Function | flext-core/src/flext_core/_models/entity.py | 66-68 |
| model_post_init | Function | flext-core/src/flext_core/_models/entity.py | 71-74 |
| HasModelDump | Class | flext-core/src/flext_core/_protocols/result.py | 173-176 |
| model_dump | Function | flext-core/src/flext_core/_protocols/result.py | 174-176 |
| FlextResultBase | Class | flext-core/src/flext_core/_result/base.py | 28-96 |
| reject_banned_result_parameterization | Function | flext-core/src/flext_core/_result/base.py | 42-54 |
| reject_banned_success_payload | Function | flext-core/src/flext_core/_result/base.py | 57-62 |
| validate_error_data | Function | flext-core/src/flext_core/_result/base.py | 65-73 |
| **init** | Function | flext-core/src/flext_core/_result/base.py | 75-96 |
| FlextRuntimeContainer | Class | flext-core/src/flext_core/_runtime/_container.py | 33-175 |
| _is_registerable_runtime_service | Function | flext-core/src/flext_core/_runtime/_container.py | 37-43 |
| _normalize_payload_item | Function | flext-core/src/flext_core/_runtime/_container.py | 46-83 |
| normalize_registerable_service | Function | flext-core/src/flext_core/_runtime/_container.py | 86-121 |
| validate_callable_input | Function | flext-core/src/flext_core/_runtime/_container.py | 124-129 |

*... and 540 more members.*

## Execution Flows

- ****hash**** (criticality: 0.69, depth: 1)
- **normalize_domain_event_data** (criticality: 0.68, depth: 3)
- **main** (criticality: 0.67, depth: 9)
- **_merge_deep** (criticality: 0.61, depth: 4)
- **_merge_append** (criticality: 0.60, depth: 3)
- **client** (criticality: 0.60, depth: 6)
- **discover_streams** (criticality: 0.58, depth: 6)
- **_parse_try_model** (criticality: 0.57, depth: 1)
- **validate_metadata_attributes** (criticality: 0.57, depth: 2)
- **run** (criticality: 0.57, depth: 7)
- *... and 3 more flows.*

## Dependencies

### Outgoing

- `that` (208 edge(s))
- `isinstance` (135 edge(s))
- `ok` (104 edge(s))
- `str` (57 edge(s))
- `validate_python` (52 edge(s))
- `len` (43 edge(s))
- `model_validate` (41 edge(s))
- `ConfigMap` (40 edge(s))
- `items` (39 edge(s))
- `fail` (38 edge(s))
- `TypeAdapter` (37 edge(s))
- `get` (33 edge(s))
- `dict` (30 edge(s))
- `pop` (28 edge(s))
- `getattr` (27 edge(s))

### Incoming

- `that` (208 edge(s))
- `ok` (49 edge(s))
- `ConfigMap` (38 edge(s))
- `len` (32 edge(s))
- `pop` (27 edge(s))
- `validate_python` (23 edge(s))
- `flext-core/tests/unit/test_models_container.py::TestsFlextCoreModelsContainer` (23 edge(s))
- `flext-core/tests/unit/test_runtime.py::TestsFlextCoreRuntime` (21 edge(s))
- `generate` (20 edge(s))
- `str` (17 edge(s))
- `fail` (15 edge(s))
- `flext-core/tests/unit/test_typings_new.py::TestsFlextCoreTypingsNew` (15 edge(s))
- `write_text` (14 edge(s))
- `flext-core/tests/unit/_utilities/test_guards.py::TestsFlextCoreGuards` (13 edge(s))
- `get` (13 edge(s))
