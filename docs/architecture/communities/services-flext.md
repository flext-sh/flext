# services-flext

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 545 nodes

- **Size**: 545 nodes
- **Cohesion**: 0.3286
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
| ------ | ------ | ------ | ------- |
| main | Function | flext-web/examples/01_basic_service.py | 8-27 |
| TestsFlextWebSettings | Class | flext-web/tests/settings.py | 10-11 |
| TestsFlextWebApi | Class | flext-web/tests/unit/test_api.py | 11-85 |
| setup_method | Function | flext-web/tests/unit/test_api.py | 14-23 |
| test_create_fastapi_app_success | Test | flext-web/tests/unit/test_api.py | 25-28 |
| test_settings_factory_success | Test | flext-web/tests/unit/test_api.py | 30-40 |
| test_settings_factory_rejects_invalid_values | Test | flext-web/tests/unit/test_api.py | 42-51 |
| test_validate_settings_success | Test | flext-web/tests/unit/test_api.py | 53-64 |
| test_get_service_status | Test | flext-web/tests/unit/test_api.py | 66-73 |
| test_settings_property_uses_registered_namespace | Test | flext-web/tests/unit/test_api.py | 84-85 |
| TestsFlextWebApp | Class | flext-web/tests/unit/test_app.py | 11-60 |
| test_create_fastapi_app_uses_settings_defaults | Test | flext-web/tests/unit/test_app.py | 14-18 |
| test_create_flask_app_success | Test | flext-web/tests/unit/test_app.py | 20-32 |
| test_create_flask_app_health_route | Test | flext-web/tests/unit/test_app.py | 34-42 |
| test_fastapi_configuration_hooks_return_success | Test | flext-web/tests/unit/test_app.py | 44-56 |
| test_validate_business_rules_success | Test | flext-web/tests/unit/test_app.py | 58-60 |
| test_config_validation | Test | flext-web/tests/unit/test_typings.py | 98-103 |
| TestsFlextWebSettings | Class | flext-web/tests/unit/test_settings.py | 11-104 |
| setup_method | Function | flext-web/tests/unit/test_settings.py | 14-15 |
| test_default_settings | Test | flext-web/tests/unit/test_settings.py | 17-22 |
| test_host_validator_rejects_empty | Test | flext-web/tests/unit/test_settings.py | 24-27 |
| test_port_validator_rejects_out_of_range | Test | flext-web/tests/unit/test_settings.py | 29-32 |
| test_port_validator_classmethod_error | Test | flext-web/tests/unit/test_settings.py | 34-37 |
| test_secret_key_validator_rejects_empty | Test | flext-web/tests/unit/test_settings.py | 39-42 |
| test_secret_key_validator_classmethod_error | Test | flext-web/tests/unit/test_settings.py | 44-47 |
| test_optional_path_normalization | Test | flext-web/tests/unit/test_settings.py | 49-53 |
| test_debug_flags_synchronization | Test | flext-web/tests/unit/test_settings.py | 55-59 |
| test_protocol_computed_field | Test | flext-web/tests/unit/test_settings.py | 61-66 |
| test_base_url_computed_field | Test | flext-web/tests/unit/test_settings.py | 68-71 |
| test_create_web_config_success | Test | flext-web/tests/unit/test_settings.py | 73-84 |
| test_create_web_config_failure | Test | flext-web/tests/unit/test_settings.py | 86-90 |
| test_validate_settings_success | Test | flext-web/tests/unit/test_settings.py | 92-97 |
| test_validate_settings_failure | Test | flext-web/tests/unit/test_settings.py | 99-104 |
| TestsFlextWebApp | Class | flext-web/tests/unit/test_app_service.py | 10-99 |
| setup_method | Function | flext-web/tests/unit/test_app_service.py | 13-14 |
| test_execute | Test | flext-web/tests/unit/test_app_service.py | 16-21 |
| test_fastapi_factory_create_instance | Test | flext-web/tests/unit/test_app_service.py | 23-27 |
| test_create_fastapi_app_with_defaults | Test | flext-web/tests/unit/test_app_service.py | 29-34 |
| test_create_fastapi_app_with_custom_config | Test | flext-web/tests/unit/test_app_service.py | 36-42 |
| test_create_flask_app | Test | flext-web/tests/unit/test_app_service.py | 44-50 |
| test_configure_error_handlers | Test | flext-web/tests/unit/test_app_service.py | 52-59 |
| test_configure_middleware | Test | flext-web/tests/unit/test_app_service.py | 61-68 |
| test_configure_routes | Test | flext-web/tests/unit/test_app_service.py | 70-77 |
| test_health_handler | Test | flext-web/tests/unit/test_app_service.py | 79-84 |
| test_info_handler | Test | flext-web/tests/unit/test_app_service.py | 86-92 |
| test_validate_business_rules | Test | flext-web/tests/unit/test_app_service.py | 94-99 |
| test_create_service_with_settings | Test | flext-web/tests/unit/test_web_services_direct.py | 30-35 |
| TestsFlextWebConfig | Class | flext-web/tests/unit/test_config.py | 10-124 |
| test_initialization_with_test_environment | Test | flext-web/tests/unit/test_config.py | 13-20 |
| test_initialization_with_custom_values | Test | flext-web/tests/unit/test_config.py | 22-34 |

*... and 495 more members.*

## Execution Flows

- **find_by_capability** (criticality: 0.84, depth: 8)
- **dispatch** (criticality: 0.80, depth: 7)
- **_after_request_hook** (criticality: 0.79, depth: 6)
- **update_config** (criticality: 0.77, depth: 1)
- **fetch_one** (criticality: 0.77, depth: 4)
- **traced_request** (criticality: 0.76, depth: 5)
- **traced_async_request** (criticality: 0.76, depth: 5)

## Dependencies

### Outgoing

- `that` (188 edge(s))
- `ok` (110 edge(s))
- `fail` (61 edge(s))
- `get` (55 edge(s))
- `fail_op` (50 edge(s))
- `str` (44 edge(s))
- `isinstance` (25 edge(s))
- `validate_python` (24 edge(s))
- `time` (23 edge(s))
- `model_validate` (22 edge(s))
- `warning` (18 edge(s))
- `_Factory` (18 edge(s))
- `raises` (17 edge(s))
- `debug` (17 edge(s))
- `dict` (16 edge(s))

### Incoming

- `that` (188 edge(s))
- `ok` (34 edge(s))
- `_Factory` (18 edge(s))
- `raises` (17 edge(s))
- `create_web_config` (16 edge(s))
- `Dict` (14 edge(s))
- `FlextWebSettings` (14 edge(s))
- `flext-core/src/flext_core/_models/_base_parts/flextmodelsbase_part_01.py` (13 edge(s))
- `flext-observability/examples/02_solid_observability_demo.py` (12 edge(s))
- `flext-observability/src/flext_observability/api.py` (12 edge(s))
- `flext-observability/examples/01_functional.py` (10 edge(s))
- `validate_python` (9 edge(s))
- `model_validate` (8 edge(s))
- `flext-observability/tests/unit/test_factory.py` (8 edge(s))
- `create_metric` (8 edge(s))
