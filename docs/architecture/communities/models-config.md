# models-config

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 55 nodes

- **Size**: 55 nodes
- **Cohesion**: 0.0785
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextMeltanoModelsCore | Class | flext-meltano/src/flext_meltano/_models/core.py | 11-77 |
| protect_sensitive_config | Function | flext-meltano/src/flext_meltano/_models/core.py | 15-37 |
| is_sensitive | Function | flext-meltano/src/flext_meltano/_models/core.py | 21-32 |
| _validated_string_list | Function | flext-meltano/src/flext_meltano/_models/core.py | 40-44 |
| DataSinkConfig | Class | flext-meltano/src/flext_meltano/_models/instances_data.py | 19-82 |
| max_records_capacity | Function | flext-meltano/src/flext_meltano/_models/instances_data.py | 39-43 |
| processing_efficiency | Function | flext-meltano/src/flext_meltano/_models/instances_data.py | 46-58 |
| sink_identifier | Function | flext-meltano/src/flext_meltano/_models/instances_data.py | 61-63 |
| serialize_connection_config | Function | flext-meltano/src/flext_meltano/_models/instances_data.py | 66-70 |
| validate_sink_config | Function | flext-meltano/src/flext_meltano/_models/instances_data.py | 73-82 |
| TapConfig | Class | flext-meltano/src/flext_meltano/_models/sources.py | 21-77 |
| config_size | Function | flext-meltano/src/flext_meltano/_models/sources.py | 37-41 |
| has_stream_config | Function | flext-meltano/src/flext_meltano/_models/sources.py | 44-46 |
| tap_identifier | Function | flext-meltano/src/flext_meltano/_models/sources.py | 49-51 |
| serialize_connection_config | Function | flext-meltano/src/flext_meltano/_models/sources.py | 54-58 |
| freeze_stream_config | Function | flext-meltano/src/flext_meltano/_models/sources.py | 62-66 |
| validate_tap_config | Function | flext-meltano/src/flext_meltano/_models/sources.py | 69-77 |
| TargetConfig | Class | flext-meltano/src/flext_meltano/_models/sources.py | 79-136 |
| config_size | Function | flext-meltano/src/flext_meltano/_models/sources.py | 101-103 |
| has_connection_config | Function | flext-meltano/src/flext_meltano/_models/sources.py | 106-108 |
| target_identifier | Function | flext-meltano/src/flext_meltano/_models/sources.py | 111-113 |
| serialize_connection_config | Function | flext-meltano/src/flext_meltano/_models/sources.py | 116-120 |
| freeze_connection_config | Function | flext-meltano/src/flext_meltano/_models/sources.py | 124-128 |
| validate_target_config | Function | flext-meltano/src/flext_meltano/_models/sources.py | 131-136 |
| DataSourceConfig | Class | flext-meltano/src/flext_meltano/_models/sources.py | 138-196 |
| config_size | Function | flext-meltano/src/flext_meltano/_models/sources.py | 156-160 |
| has_stream_config | Function | flext-meltano/src/flext_meltano/_models/sources.py | 163-165 |
| source_identifier | Function | flext-meltano/src/flext_meltano/_models/sources.py | 168-170 |
| serialize_connection_config | Function | flext-meltano/src/flext_meltano/_models/sources.py | 173-177 |
| freeze_stream_config | Function | flext-meltano/src/flext_meltano/_models/sources.py | 181-185 |
| validate_source_config | Function | flext-meltano/src/flext_meltano/_models/sources.py | 188-196 |
| test_tap_config_exposes_defaults_for_optional_fields | Test | flext-meltano/tests/unit/test_models.py | 51-58 |
| test_tap_config_retains_full_supplied_state | Test | flext-meltano/tests/unit/test_models.py | 60-76 |
| test_tap_config_computed_fields_derive_from_state | Test | flext-meltano/tests/unit/test_models.py | 78-88 |
| test_tap_config_has_stream_config_false_when_absent | Test | flext-meltano/tests/unit/test_models.py | 90-95 |
| test_tap_config_rejects_blank_tap_type | Test | flext-meltano/tests/unit/test_models.py | 98-102 |
| test_tap_config_rejects_empty_connection_config | Test | flext-meltano/tests/unit/test_models.py | 104-108 |
| test_tap_and_target_configs_are_independent | Test | flext-meltano/tests/unit/test_models.py | 299-311 |
| test_stream_name_maps_into_tap_stream_config | Test | flext-meltano/tests/unit/test_models.py | 313-326 |
| test_tap_config_validation | Test | flext-meltano/tests/unit/test_tap_abstractions.py | 25-41 |
| test_tap_instance_validation | Test | flext-meltano/tests/unit/test_tap_abstractions.py | 60-82 |
| test_serviceprocessor_process_method | Test | flext-meltano/tests/unit/test_tap_abstractions.py | 95-105 |
| test_serviceprocessor_build_method | Test | flext-meltano/tests/unit/test_tap_abstractions.py | 107-121 |
| test_fetch_stream_config | Test | flext-meltano/tests/unit/test_tap_abstractions.py | 123-139 |
| test_validate_tap_instance | Test | flext-meltano/tests/unit/test_tap_abstractions.py | 160-189 |
| test_discover_streams_postgres | Test | flext-meltano/tests/unit/test_tap_abstractions.py | 191-207 |
| test_discover_streams_csv | Test | flext-meltano/tests/unit/test_tap_abstractions.py | 209-223 |
| test_discover_streams_default | Test | flext-meltano/tests/unit/test_tap_abstractions.py | 225-242 |
| test_generate_catalog_success | Test | flext-meltano/tests/unit/test_tap_abstractions.py | 244-260 |
| test_catalog_entry_structure | Test | flext-meltano/tests/unit/test_tap_abstractions.py | 262-279 |

*... and 5 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (48 edge(s))
- `TapConfig` (25 edge(s))
- `model_validate` (16 edge(s))
- `object` (9 edge(s))
- `FlextMeltanoAbstractions` (9 edge(s))
- `ok` (8 edge(s))
- `ValueError` (7 edge(s))
- `bool` (7 edge(s))
- `list` (5 edge(s))
- `m.Entity` (4 edge(s))
- `strip` (4 edge(s))
- `keys` (4 edge(s))
- `discover_streams` (4 edge(s))
- `process_tap_config` (4 edge(s))
- `MappingProxyType` (3 edge(s))

### Incoming

- `that` (48 edge(s))
- `TapConfig` (25 edge(s))
- `flext-meltano/tests/unit/test_tap_abstractions.py::TestFlextMeltanoAbstractionsComplete` (16 edge(s))
- `model_validate` (14 edge(s))
- `object` (9 edge(s))
- `flext-meltano/tests/unit/test_models.py::TestsFlextMeltanoModelsUnit` (8 edge(s))
- `ok` (7 edge(s))
- `discover_streams` (4 edge(s))
- `bool` (4 edge(s))
- `process_tap_config` (4 edge(s))
- `flext-meltano/src/flext_meltano/_models/sources.py` (3 edge(s))
- `fail` (3 edge(s))
- `fetch_stream_config` (3 edge(s))
- `isinstance` (3 edge(s))
- `StreamInfo` (2 edge(s))
