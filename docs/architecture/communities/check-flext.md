# check-flext

## Overview

Community of 901 nodes

- **Size**: 901 nodes
- **Cohesion**: 0.3311
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| test_temporary_directory | Test | flext-tests/tests/unit/_files_parts/models.py | 54-61 |
| Tests | Class | flext-tests/src/flext_tests/typings.py | 27-37 |
| FlextTestsBaseTypesMixin | Class | flext-tests/src/flext_tests/_typings/base.py | 28-130 |
| FlextTestsFilesTypesMixin | Class | flext-tests/src/flext_tests/_typings/files.py | 14-23 |
| FlextTestsMakeTypesMixin | Class | flext-tests/src/flext_tests/_typings/make.py | 15-29 |
| FlextTestsMatchersTypesMixin | Class | flext-tests/src/flext_tests/_typings/matchers.py | 19-106 |
| FlextTestsGuardsTypesMixin | Class | flext-tests/src/flext_tests/_typings/guards.py | 17-28 |
| general_value | Function | flext-tests/src/flext_tests/_typings/guards.py | 19-28 |
| env_vars_context | Function | flext-tests/src/flext_tests/_utilities/settings.py | 38-47 |
| Matchers | Class | flext-tests/src/flext_tests/_utilities/_matchers/_scope.py | 32-121 |
| scope | Function | flext-tests/src/flext_tests/_utilities/_matchers/_scope.py | 37-121 |
| temporary_directory | Function | flext-tests/src/flext_tests/_utilities/_files/_contexts.py | 89-97 |
| infra_safe_command_output | Function | flext-infra/tests/conftest.py | 155-166 |
| infra_git_repo | Function | flext-infra/tests/conftest.py | 170-185 |
| DeptryRunner | Class | flext-infra/tests/utilities.py | 71-178 |
| __init__ | Function | flext-infra/tests/utilities.py | 74-78 |
| run_raw | Function | flext-infra/tests/utilities.py | 81-91 |
| run | Function | flext-infra/tests/utilities.py | 94-110 |
| capture | Function | flext-infra/tests/utilities.py | 113-130 |
| run_checked | Function | flext-infra/tests/utilities.py | 133-150 |
| run_to_file | Function | flext-infra/tests/utilities.py | 153-178 |
| SequenceRunner | Class | flext-infra/tests/utilities.py | 205-262 |
| _next_result | Function | flext-infra/tests/utilities.py | 216-227 |
| run_raw | Function | flext-infra/tests/utilities.py | 230-241 |
| run | Function | flext-infra/tests/utilities.py | 244-262 |
| command_runner | Function | flext-infra/tests/utilities.py | 313-327 |
| stub_run | Function | flext-infra/tests/utilities.py | 385-395 |
| mk_project | Function | flext-infra/tests/utilities.py | 398-413 |
| create_release_workspace | Function | flext-infra/tests/utilities.py | 504-572 |
| initialize_git_repo | Function | flext-infra/tests/utilities.py | 643-652 |
| detect_command | Function | flext-infra/tests/utilities.py | 1069-1076 |
| create_gate_execution | Function | flext-infra/tests/utilities.py | 1123-1140 |
| make_project | Function | flext-infra/tests/utilities.py | 1161-1173 |
| create_checker_project | Function | flext-infra/tests/utilities.py | 1176-1189 |
| create_gate_context | Function | flext-infra/tests/utilities.py | 1192-1200 |
| run_gate_check | Function | flext-infra/tests/utilities.py | 1203-1220 |
| _read_fixture | Function | flext-infra/tests/unit/fixtures.py | 26-27 |
| _modernizer_pyproject | Function | flext-infra/tests/unit/fixtures.py | 30-31 |
| _modernizer_workspace_pyproject | Function | flext-infra/tests/unit/fixtures.py | 34-39 |
| deptry_report_payload | Function | flext-infra/tests/unit/fixtures.py | 43-47 |
| modernizer_workspace | Function | flext-infra/tests/unit/fixtures.py | 137-144 |
| modernizer_workspace_with_projects | Function | flext-infra/tests/unit/fixtures.py | 148-163 |
| _project | Function | flext-infra/tests/unit/check/abstraction_boundary_gate_tests.py | 23-30 |
| TestAbstractionBoundaryGate | Class | flext-infra/tests/unit/check/abstraction_boundary_gate_tests.py | 33-101 |
| test_gate_identity | Test | flext-infra/tests/unit/check/abstraction_boundary_gate_tests.py | 34-36 |
| test_banned_cli_lib_is_flagged | Test | flext-infra/tests/unit/check/abstraction_boundary_gate_tests.py | 38-53 |
| test_click_allowed_in_singer_boundary | Test | flext-infra/tests/unit/check/abstraction_boundary_gate_tests.py | 55-69 |
| test_concrete_flext_cli_import_flagged | Test | flext-infra/tests/unit/check/abstraction_boundary_gate_tests.py | 71-85 |
| test_concrete_flext_cli_allowed_in_extension_file | Test | flext-infra/tests/unit/check/abstraction_boundary_gate_tests.py | 87-101 |
| FakeGate | Class | flext-infra/tests/unit/check/enforcement_fixer_orchestrator_tests.py | 420-464 |

*... and 851 more members.*

## Execution Flows

- **execute** (criticality: 0.88, depth: 9)
- **execute** (criticality: 0.87, depth: 9)
- **check** (criticality: 0.87, depth: 5)
- **main** (criticality: 0.85, depth: 9)
- **main** (criticality: 0.85, depth: 12)
- **main** (criticality: 0.84, depth: 12)
- **main** (criticality: 0.83, depth: 14)
- **main** (criticality: 0.83, depth: 12)
- **execute** (criticality: 0.83, depth: 13)
- **check** (criticality: 0.83, depth: 13)
- *... and 110 more flows.*

## Dependencies

### Outgoing

- `that` (216 edge(s))
- `ok` (155 edge(s))
- `write_text` (149 edge(s))
- `fail` (113 edge(s))
- `mkdir` (105 edge(s))
- `str` (97 edge(s))
- `get` (85 edge(s))
- `len` (67 edge(s))
- `Path` (61 edge(s))
- `append` (57 edge(s))
- `isinstance` (48 edge(s))
- `exists` (40 edge(s))
- `Issue` (36 edge(s))
- `validate_python` (29 edge(s))
- `strip` (26 edge(s))

### Incoming

- `that` (216 edge(s))
- `write_text` (128 edge(s))
- `ok` (84 edge(s))
- `mkdir` (80 edge(s))
- `FlextInfraInternalDependencySyncService` (51 edge(s))
- `len` (45 edge(s))
- `Path` (44 edge(s))
- `str` (41 edge(s))
- `run_gate_check` (33 edge(s))
- `mk_project` (33 edge(s))
- `fail` (27 edge(s))
- `json_as_mapping` (25 edge(s))
- `create_release_workspace` (24 edge(s))
- `read_text` (22 edge(s))
- `create_checker_project` (21 edge(s))
