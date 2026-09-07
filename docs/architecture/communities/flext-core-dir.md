# flext-core-dir


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 60 nodes

- **Size**: 60 nodes
- **Cohesion**: 0.2128
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| _UniqueKeySafeLoader | Class | flext-core/src/flext_core/_config.py | 48-49 |
| StrictYamlConfigSource | Class | flext-core/src/flext_core/_config.py | 80-178 |
| __init__ | Function | flext-core/src/flext_core/_config.py | 89-106 |
| __call__ | Function | flext-core/src/flext_core/_config.py | 109-114 |
| _read_file | Function | flext-core/src/flext_core/_config.py | 117-130 |
| _read_files | Function | flext-core/src/flext_core/_config.py | 133-162 |
| _deep_merge_lists | Function | flext-core/src/flext_core/_config.py | 165-178 |
| FlextConfig | Class | flext-core/src/flext_core/_config.py | 181-352 |
| __init_subclass__ | Function | flext-core/src/flext_core/_config.py | 202-206 |
| _package_namespace | Function | flext-core/src/flext_core/_config.py | 209-218 |
| _config_dir | Function | flext-core/src/flext_core/_config.py | 221-249 |
| _user_config_dir | Function | flext-core/src/flext_core/_config.py | 252-259 |
| _yaml_files_in | Function | flext-core/src/flext_core/_config.py | 262-264 |
| _config_files | Function | flext-core/src/flext_core/_config.py | 267-296 |
| _transform_loaded_yaml | Function | flext-core/src/flext_core/_config.py | 299-306 |
| settings_customise_sources | Function | flext-core/src/flext_core/_config.py | 310-332 |
| fetch_global | Function | flext-core/src/flext_core/_config.py | 335-346 |
| reset_for_testing | Function | flext-core/src/flext_core/_config.py | 349-352 |
| _resolve_env_file | Function | flext-core/src/flext_core/_settings.py | 44-63 |
| _platform_cache_root | Function | flext-core/src/flext_core/_settings.py | 66-84 |
| _platform_data_root | Function | flext-core/src/flext_core/_settings.py | 87-104 |
| platform_config_root | Function | flext-core/src/flext_core/_settings.py | 107-120 |
| _platform_state_root | Function | flext-core/src/flext_core/_settings.py | 123-140 |
| app_env_prefix | Function | flext-core/src/flext_core/_settings.py | 143-146 |
| _validate_app_namespace | Function | flext-core/src/flext_core/_settings.py | 149-155 |
| _namespace_dir_name | Function | flext-core/src/flext_core/_settings.py | 158-164 |
| FlextSettings | Class | flext-core/src/flext_core/_settings.py | 167-439 |
| _resolve_env_file | Function | flext-core/src/flext_core/_settings.py | 186-188 |
| __init_subclass__ | Function | flext-core/src/flext_core/_settings.py | 205-209 |
| __new__ | Function | flext-core/src/flext_core/_settings.py | 211-224 |
| _initialized_instance | Function | flext-core/src/flext_core/_settings.py | 227-236 |
| singleton_disabled | Function | flext-core/src/flext_core/_settings.py | 240-248 |
| fetch_global | Function | flext-core/src/flext_core/_settings.py | 251-272 |
| _merge_overrides | Function | flext-core/src/flext_core/_settings.py | 275-292 |
| clone | Function | flext-core/src/flext_core/_settings.py | 294-302 |
| update_global | Function | flext-core/src/flext_core/_settings.py | 305-316 |
| _validate_overrides | Function | flext-core/src/flext_core/_settings.py | 319-326 |
| reset_for_testing | Function | flext-core/src/flext_core/_settings.py | 329-332 |
| set_app_namespace | Function | flext-core/src/flext_core/_settings.py | 335-340 |
| reset_app_namespace | Function | flext-core/src/flext_core/_settings.py | 343-346 |
| _owner_namespace | Function | flext-core/src/flext_core/_settings.py | 349-357 |
| _current_app_namespace | Function | flext-core/src/flext_core/_settings.py | 360-372 |
| _absolute_app_dir | Function | flext-core/src/flext_core/_settings.py | 375-382 |
| cache_dir | Function | flext-core/src/flext_core/_settings.py | 386-388 |
| work_dir | Function | flext-core/src/flext_core/_settings.py | 392-394 |
| data_dir | Function | flext-core/src/flext_core/_settings.py | 398-400 |
| state_dir | Function | flext-core/src/flext_core/_settings.py | 404-406 |
| config_dir | Function | flext-core/src/flext_core/_settings.py | 410-412 |
| runtime_dir | Function | flext-core/src/flext_core/_settings.py | 416-432 |
| _validate_settings | Function | flext-core/src/flext_core/_settings.py | 435-439 |

*... and 10 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `Path` (25 edge(s))
- `that` (17 edge(s))
- `get` (16 edge(s))
- `home` (12 edge(s))
- `str` (11 edge(s))
- `isinstance` (11 edge(s))
- `reset_for_testing` (9 edge(s))
- `env_vars_context` (8 edge(s))
- `set_app_namespace` (8 edge(s))
- `fetch_global` (8 edge(s))
- `super` (6 edge(s))
- `ValueError` (6 edge(s))
- `FlextSettings` (5 edge(s))
- `resolve` (4 edge(s))
- `join` (4 edge(s))

### Incoming

- `that` (17 edge(s))
- `flext-core/src/flext_core/_settings.py` (11 edge(s))
- `reset_for_testing` (9 edge(s))
- `env_vars_context` (8 edge(s))
- `set_app_namespace` (8 edge(s))
- `fetch_global` (8 edge(s))
- `str` (7 edge(s))
- `flext-core/tests/unit/test_settings.py::TestsFlextCoreSettingsWorkDir` (7 edge(s))
- `Path` (7 edge(s))
- `FlextSettings` (5 edge(s))
- `flext-core/src/flext_core/_config.py` (4 edge(s))
- `flext-core/tests/integration/test_settings_integration.py::TestsFlextSettingsIntegration` (2 edge(s))
- `singleton_disabled` (2 edge(s))
- `flext-core/tests/integration/settings_integration_precedence.py::TestsFlextFlextSettingsPrecedenceCase` (1 edge(s))
- `write_text` (1 edge(s))
