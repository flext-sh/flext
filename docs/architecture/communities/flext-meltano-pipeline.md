# flext-meltano-pipeline

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 102 nodes

- **Size**: 102 nodes
- **Cohesion**: 0.3087
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextMeltanoCli | Class | flext-meltano/src/flext_meltano/cli.py | 13-293 |
| **init** | Function | flext-meltano/src/flext_meltano/cli.py | 19-26 |
| run | Function | flext-meltano/src/flext_meltano/cli.py | 28-30 |
| _register_commands | Function | flext-meltano/src/flext_meltano/cli.py | 32-39 |
| _register_version_command | Function | flext-meltano/src/flext_meltano/cli.py | 41-48 |
| _handle_version | Function | flext-meltano/src/flext_meltano/cli.py | 50-51 |
| _register_status_commands | Function | flext-meltano/src/flext_meltano/cli.py | 53-71 |
| _handle_status_show | Function | flext-meltano/src/flext_meltano/cli.py | 73-78 |
| _handle_status_health | Function | flext-meltano/src/flext_meltano/cli.py | 80-87 |
| _register_tap_command | Function | flext-meltano/src/flext_meltano/cli.py | 89-96 |
| _handle_tap | Function | flext-meltano/src/flext_meltano/cli.py | 98-101 |
| _register_target_command | Function | flext-meltano/src/flext_meltano/cli.py | 103-110 |
| _handle_target | Function | flext-meltano/src/flext_meltano/cli.py | 112-115 |
| _register_dbt_command | Function | flext-meltano/src/flext_meltano/cli.py | 117-124 |
| _handle_dbt | Function | flext-meltano/src/flext_meltano/cli.py | 126-134 |
| _register_plugin_commands | Function | flext-meltano/src/flext_meltano/cli.py | 136-161 |
| _handle_plugin_list | Function | flext-meltano/src/flext_meltano/cli.py | 163-184 |
| _handle_plugin_info | Function | flext-meltano/src/flext_meltano/cli.py | 186-194 |
| _handle_plugin_install | Function | flext-meltano/src/flext_meltano/cli.py | 196-199 |
| _register_pipeline_commands | Function | flext-meltano/src/flext_meltano/cli.py | 201-249 |
| _handle_pipeline_create | Function | flext-meltano/src/flext_meltano/cli.py | 251-267 |
| _handle_pipeline_run | Function | flext-meltano/src/flext_meltano/cli.py | 269-271 |
| _handle_pipeline_list | Function | flext-meltano/src/flext_meltano/cli.py | 273-278 |
| _handle_pipeline_status | Function | flext-meltano/src/flext_meltano/cli.py | 280-283 |
| _handle_pipeline_stop | Function | flext-meltano/src/flext_meltano/cli.py | 285-288 |
| _handle_pipeline_delete | Function | flext-meltano/src/flext_meltano/cli.py | 290-293 |
| main | Function | flext-meltano/src/flext_meltano/cli.py | 296-299 |
| FlextMeltanoPipelineManager | Class | flext-meltano/src/flext_meltano/pipeline_mgr.py | 26-319 |
| **init** | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 31-44 |
| fetch_fresh_settings | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 47-58 |
| _pipelines_root | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 60-67 |
| _pipeline_dir | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 69-70 |
| _config_path | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 72-76 |
| _pid_path | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 78-81 |
| _normalize_pipeline_name | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 84-88 |
| _load_pipeline_config | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 90-102 |
| _pipeline_command | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 104-119 |
| _read_pid | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 121-129 |
| _process_running | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 132-137 |
| create_pipeline | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 139-164 |
| execute_pipeline | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 166-187 |
| list_pipelines | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 189-191 |
| fetch_pipeline_status | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 193-207 |
| stop_pipeline | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 209-224 |
| delete_pipeline | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 226-237 |
| handle_command | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 239-247 |
| _create_pipeline | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 249-269 |
| _delete_pipeline | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 271-275 |
| _dispatch_pipeline | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 277-293 |
| _fetch_pipeline_status | Function | flext-meltano/src/flext_meltano/pipeline_mgr.py | 295-299 |

*... and 52 more members.*

## Execution Flows

- **_handle_pipeline_run** (criticality: 0.59, depth: 6)
- **execute_complete_elt_pipeline** (criticality: 0.58, depth: 3)

## Dependencies

### Outgoing

- `ok` (56 edge(s))
- `that` (53 edge(s))
- `fail` (22 edge(s))
- `from_failure` (20 edge(s))
- `register_result_command` (15 edge(s))
- `readouterr` (15 edge(s))
- `map` (10 edge(s))
- `validate_python` (7 edge(s))
- `model_validate` (6 edge(s))
- `fail_validation` (6 edge(s))
- `json_dumps` (6 edge(s))
- `exists` (6 edge(s))
- `join` (5 edge(s))
- `get` (5 edge(s))
- `str` (5 edge(s))

### Incoming

- `that` (53 edge(s))
- `ok` (33 edge(s))
- `readouterr` (15 edge(s))
- `execute_meltano_command` (3 edge(s))
- `fail` (3 edge(s))
- `run_cli` (3 edge(s))
- `str` (3 edge(s))
- `flext-meltano/src/flext_meltano/cli.py` (2 edge(s))
- `flext-meltano/src/flext_meltano/api.py` (2 edge(s))
- `flext-meltano/src/flext_meltano/services/library_runner.py` (2 edge(s))
- `json_loads` (2 edge(s))
- `validate_python` (2 edge(s))
- `create_cli_runner` (2 edge(s))
- `version` (2 edge(s))
- `json_dumps` (2 edge(s))
