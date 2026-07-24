# deps-infra

## Overview

Community of 289 nodes

- **Size**: 289 nodes
- **Cohesion**: 0.2664
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| Tests | Class | flext-infra/tests/utilities.py | 41-1302 |
| DeptrySelector | Class | flext-infra/tests/utilities.py | 44-69 |
| **init** | Function | flext-infra/tests/utilities.py | 49-53 |
| resolve_projects | Function | flext-infra/tests/utilities.py | 57-69 |
| TomlReaderSequence | Class | flext-infra/tests/utilities.py | 180-203 |
| read_plain | Function | flext-infra/tests/utilities.py | 191-203 |
| infra_mapping | Function | flext-infra/tests/utilities.py | 265-268 |
| infra_mapping_result | Function | flext-infra/tests/utilities.py | 271-276 |
| MigratorDiscovery | Class | flext-infra/tests/utilities.py | 329-348 |
| **init** | Function | flext-infra/tests/utilities.py | 332-339 |
| is_docker_available | Function | flext-infra/tests/utilities.py | 368-369 |
| is_project_valid | Function | flext-infra/tests/utilities.py | 372-382 |
| create_github_workspace | Function | flext-infra/tests/utilities.py | 465-501 |
| create_path_sync_workspace | Function | flext-infra/tests/utilities.py | 575-614 |
| create_path_sync_pyproject | Function | flext-infra/tests/utilities.py | 617-640 |
| src_module_files | Function | flext-infra/tests/utilities.py | 659-666 |
| create_scaffolder_test_project | Function | flext-infra/tests/utilities.py | 709-734 |
| create_migrator_project | Function | flext-infra/tests/utilities.py | 737-749 |
| create_migrator_dir_layout | Function | flext-infra/tests/utilities.py | 752-779 |
| create_project_info | Function | flext-infra/tests/utilities.py | 782-804 |
| create_command_output | Function | flext-infra/tests/utilities.py | 807-819 |
| create_deptry_service | Function | flext-infra/tests/utilities.py | 822-847 |
| create_migrator_discovery | Function | flext-infra/tests/utilities.py | 1026-1034 |
| create_migrator_generator | Function | flext-infra/tests/utilities.py | 1037-1045 |
| build_project_migrator | Function | flext-infra/tests/utilities.py | 1048-1066 |
| create_detector_deps_stub | Function | flext-infra/tests/utilities.py | 1079-1082 |
| setup_detector_runtime | Function | flext-infra/tests/utilities.py | 1085-1105 |
| write_migrator_project | Function | flext-infra/tests/utilities.py | 1108-1120 |
| make_issue | Function | flext-infra/tests/utilities.py | 1143-1158 |
| DetectorReportStub | Class | flext-infra/tests/utilities.py | 1222-1229 |
| **init** | Function | flext-infra/tests/utilities.py | 1225-1226 |
| DetectorDepsStub | Class | flext-infra/tests/utilities.py | 1231-1302 |
| **init** | Function | flext-infra/tests/utilities.py | 1237-1241 |
| discover_project_paths | Function | flext-infra/tests/utilities.py | 1244-1253 |
| run_deptry | Function | flext-infra/tests/utilities.py | 1256-1268 |
| build_project_report | Function | flext-infra/tests/utilities.py | 1271-1277 |
| get_required_typings | Function | flext-infra/tests/utilities.py | 1280-1293 |
| load_dependency_limits | Function | flext-infra/tests/utilities.py | 1296-1302 |
| TestsFlextInfraInfraSelection | Class | flext-infra/tests/unit/test_infra_selection.py | 24-199 |
| workspace_with_projects | Function | flext-infra/tests/unit/test_infra_selection.py | 28-41 |
| selector | Function | flext-infra/tests/unit/test_infra_selection.py | 44-47 |
| workspace_with_declared_names | Function | flext-infra/tests/unit/test_infra_selection.py | 50-66 |
| test_resolve_projects_all_projects | Test | flext-infra/tests/unit/test_infra_selection.py | 68-77 |
| test_resolve_projects_specific_names | Test | flext-infra/tests/unit/test_infra_selection.py | 79-88 |
| test_resolve_projects_single_project | Test | flext-infra/tests/unit/test_infra_selection.py | 90-99 |
| test_resolve_projects_unknown_project | Test | flext-infra/tests/unit/test_infra_selection.py | 101-108 |
| test_resolve_projects_mixed_known_unknown | Test | flext-infra/tests/unit/test_infra_selection.py | 110-120 |
| test_resolve_projects_discovery_failure | Test | flext-infra/tests/unit/test_infra_selection.py | 122-128 |
| test_resolve_projects_sorted_output | Test | flext-infra/tests/unit/test_infra_selection.py | 130-141 |
| test_resolve_projects_result_type | Test | flext-infra/tests/unit/test_infra_selection.py | 143-153 |

*... and 239 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (175 edge(s))
- `ok` (86 edge(s))
- `mkdir` (62 edge(s))
- `execute` (51 edge(s))
- `write_text` (49 edge(s))
- `fail` (37 edge(s))
- `str` (36 edge(s))
- `isinstance` (28 edge(s))
- `len` (28 edge(s))
- `any` (27 edge(s))
- `get` (23 edge(s))
- `read_text` (22 edge(s))
- `Path` (18 edge(s))
- `exists` (13 edge(s))
- `touch` (13 edge(s))

### Incoming

- `that` (174 edge(s))
- `ok` (69 edge(s))
- `execute` (51 edge(s))
- `mkdir` (38 edge(s))
- `create_migrator_project` (32 edge(s))
- `build_project_migrator` (31 edge(s))
- `any` (27 edge(s))
- `FlextInfraDependencyDetectionService` (26 edge(s))
- `write_text` (25 edge(s))
- `len` (24 edge(s))
- `str` (24 edge(s))
- `fail` (23 edge(s))
- `create_migrator_dir_layout` (21 edge(s))
- `read_text` (18 edge(s))
- `create_path_sync_pyproject` (17 edge(s))
