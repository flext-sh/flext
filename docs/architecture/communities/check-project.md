# check-project

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 57 nodes

- **Size**: 57 nodes
- **Cohesion**: 0.3089
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| test_format_error_template_interpolates_placeholder | Test | flext-cli/tests/unit/test_constants.py | 165-168 |
| test_port_out_of_range_message_formats_with_named_fields | Test | flext-db-oracle/tests/unit/test_constants.py | 250-256 |
| FlextInfraWorkspaceChecker | Class | flext-infra/src/flext_infra/check/workspace_check.py | 19-205 |
| **init** | Function | flext-infra/src/flext_infra/check/workspace_check.py | 30-50 |
| parse_tool_args | Function | flext-infra/src/flext_infra/check/workspace_check.py | 53-57 |
| resolve_gates | Function | flext-infra/src/flext_infra/check/workspace_check.py | 60-71 |
| execute | Function | flext-infra/src/flext_infra/check/workspace_check.py | 74-76 |
| execute_payload | Function | flext-infra/src/flext_infra/check/workspace_check.py | 79-112 |
| _resolve_project_targets | Function | flext-infra/src/flext_infra/check/workspace_check.py | 115-140 |
| format | Function | flext-infra/src/flext_infra/check/workspace_check.py | 142-146 |
| lint | Function | flext-infra/src/flext_infra/check/workspace_check.py | 148-152 |
| run_project | Function | flext-infra/src/flext_infra/check/workspace_check.py | 154-158 |
| run_projects | Function | flext-infra/src/flext_infra/check/workspace_check.py | 160-189 |
| _project_targets | Function | flext-infra/src/flext_infra/check/workspace_check.py | 191-205 |
| TestGateErrorReportingPublicBehavior | Class | flext-infra/tests/unit/check/extended_error_reporting_tests.py | 26-135 |
| failing_markdown_run | Function | flext-infra/tests/unit/check/extended_error_reporting_tests.py | 30-38 |
| test_workspace_checker_emits_gate_process_failure | Test | flext-infra/tests/unit/check/extended_error_reporting_tests.py | 105-117 |
| test_workspace_checker_emits_parsed_gate_issue | Test | flext-infra/tests/unit/check/extended_error_reporting_tests.py | 119-135 |
| TestsExtendedProjectRunners | Class | flext-infra/tests/unit/check/extended_project_runners_tests.py | 22-80 |
| test_run_projects_records_requested_gates | Test | flext-infra/tests/unit/check/extended_project_runners_tests.py | 28-58 |
| test_public_method_returns_gate_result | Test | flext-infra/tests/unit/check/extended_project_runners_tests.py | 61-80 |
| TestWorkspaceCheckerResolveGates | Class | flext-infra/tests/unit/check/extended_resolve_gates_tests.py | 13-55 |
| test_resolve_gates_type_is_rejected | Test | flext-infra/tests/unit/check/extended_resolve_gates_tests.py | 16-18 |
| test_resolve_gates_rejects_empty_strings | Test | flext-infra/tests/unit/check/extended_resolve_gates_tests.py | 20-22 |
| test_resolve_gates_rejects_duplicate_entries | Test | flext-infra/tests/unit/check/extended_resolve_gates_tests.py | 24-31 |
| test_resolve_gates_invalid_gate_fails | Test | flext-infra/tests/unit/check/extended_resolve_gates_tests.py | 33-35 |
| test_resolve_gates_all_valid_types | Test | flext-infra/tests/unit/check/extended_resolve_gates_tests.py | 37-50 |
| test_resolve_gates_accepts_silent_failure | Test | flext-infra/tests/unit/check/extended_resolve_gates_tests.py | 52-55 |
| TestRunProjectsPublicBehavior | Class | flext-infra/tests/unit/check/extended_run_projects_tests.py | 22-191 |
| _install_fake_ruff | Function | flext-infra/tests/unit/check/extended_run_projects_tests.py | 26-61 |
| test_invalid_gates_fail | Test | flext-infra/tests/unit/check/extended_run_projects_tests.py | 63-68 |
| test_missing_projects_are_skipped | Test | flext-infra/tests/unit/check/extended_run_projects_tests.py | 70-76 |
| test_run_projects_creates_reports | Test | flext-infra/tests/unit/check/extended_run_projects_tests.py | 79-96 |
| test_run_projects_creates_project_scoped_reports_dir | Test | flext-infra/tests/unit/check/extended_run_projects_tests.py | 98-115 |
| test_fail_fast_stops_after_first_failed_project | Test | flext-infra/tests/unit/check/extended_run_projects_tests.py | 117-143 |
| test_run_projects_reports_mixed_project_errors | Test | flext-infra/tests/unit/check/extended_run_projects_tests.py | 145-176 |
| test_run_project_returns_single_project_result | Test | flext-infra/tests/unit/check/extended_run_projects_tests.py | 178-191 |
| test_init_creates_default_reports_dir | Test | flext-infra/tests/unit/check/extended_workspace_init_tests.py | 29-32 |
| test_execute_returns_failure | Test | flext-infra/tests/unit/check/extended_workspace_init_tests.py | 34-36 |
| test_resolve_gates_rejects_duplicate_explicit_gates | Test | flext-infra/tests/unit/check/extended_workspace_init_tests.py | 38-43 |
| test_resolve_gates_rejects_unknown_gate | Test | flext-infra/tests/unit/check/extended_workspace_init_tests.py | 45-47 |
| test_run_projects_fails_when_reports_dir_is_not_a_directory | Test | flext-infra/tests/unit/check/extended_workspace_init_tests.py | 52-62 |
| test_resolve_gates_rejects_duplicate_explicit_gate | Test | flext-infra/tests/unit/check/test_cli.py | 54-60 |
| TestFlextInfraWorkspaceChecker | Class | flext-infra/tests/unit/check/workspace_tests.py | 24-153 |
| _clear_make_ci_token | Function | flext-infra/tests/unit/check/workspace_tests.py | 30-32 |
| test_init_creates_instance | Test | flext-infra/tests/unit/check/workspace_tests.py | 34-37 |
| test_init_with_custom_repository_root | Test | flext-infra/tests/unit/check/workspace_tests.py | 39-42 |
| test_execute_returns_failure | Test | flext-infra/tests/unit/check/workspace_tests.py | 44-51 |
| test_cli_returns_error_without_discovered_projects | Test | flext-infra/tests/unit/check/workspace_tests.py | 53-58 |
| test_resolve_gates_with_valid_gates | Test | flext-infra/tests/unit/check/workspace_tests.py | 97-106 |

*... and 7 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (33 edge(s))
- `ok` (23 edge(s))
- `fail` (20 edge(s))
- `write_text` (14 edge(s))
- `mk_project` (8 edge(s))
- `restore_env` (6 edge(s))
- `tuple` (5 edge(s))
- `from_failure` (5 edge(s))
- `mkdir` (4 edge(s))
- `len` (4 edge(s))
- `append` (3 edge(s))
- `list` (3 edge(s))
- `get` (3 edge(s))
- `str` (3 edge(s))
- `exists` (3 edge(s))

### Incoming

- `that` (33 edge(s))
- `ok` (17 edge(s))
- `fail` (13 edge(s))
- `write_text` (11 edge(s))
- `mk_project` (7 edge(s))
- `restore_env` (6 edge(s))
- `flext-infra/tests/unit/check/extended_workspace_init_tests.py::TestWorkspaceChecker` (5 edge(s))
- `len` (4 edge(s))
- `exists` (3 edge(s))
- `FlextInfraWorkspaceChecker` (3 edge(s))
- `resolve_gates` (3 edge(s))
- `format` (2 edge(s))
- `command_runner` (2 edge(s))
- `readouterr` (2 edge(s))
- `mkdir` (2 edge(s))
