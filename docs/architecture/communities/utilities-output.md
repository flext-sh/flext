# utilities-output


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 86 nodes

- **Size**: 86 nodes
- **Cohesion**: 0.0873
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextCliUtilitiesCommands | Class | flext-cli/src/flext_cli/_utilities/commands.py | 17-85 |
| commands_resolve_success_message | Function | flext-cli/src/flext_cli/_utilities/commands.py | 21-38 |
| commands_emit_success_message | Function | flext-cli/src/flext_cli/_utilities/commands.py | 41-50 |
| commands_emit_result_error | Function | flext-cli/src/flext_cli/_utilities/commands.py | 53-85 |
| FlextCliUtilitiesOutput | Class | flext-cli/src/flext_cli/_utilities/output.py | 13-210 |
| output_resolve_message_type | Function | flext-cli/src/flext_cli/_utilities/output.py | 24-32 |
| output_resolve_style | Function | flext-cli/src/flext_cli/_utilities/output.py | 35-37 |
| output_message_payload | Function | flext-cli/src/flext_cli/_utilities/output.py | 40-52 |
| output_progress_line | Function | flext-cli/src/flext_cli/_utilities/output.py | 55-61 |
| output_summary_content | Function | flext-cli/src/flext_cli/_utilities/output.py | 64-70 |
| output_debug_line | Function | flext-cli/src/flext_cli/_utilities/output.py | 73-75 |
| output_table_error | Function | flext-cli/src/flext_cli/_utilities/output.py | 78-81 |
| output_status_line | Function | flext-cli/src/flext_cli/_utilities/output.py | 84-94 |
| output_gate_line | Function | flext-cli/src/flext_cli/_utilities/output.py | 97-104 |
| emit_raw | Function | flext-cli/src/flext_cli/_utilities/output.py | 107-111 |
| info | Function | flext-cli/src/flext_cli/_utilities/output.py | 114-116 |
| error | Function | flext-cli/src/flext_cli/_utilities/output.py | 119-123 |
| warning | Function | flext-cli/src/flext_cli/_utilities/output.py | 126-128 |
| debug | Function | flext-cli/src/flext_cli/_utilities/output.py | 131-133 |
| header | Function | flext-cli/src/flext_cli/_utilities/output.py | 136-139 |
| progress | Function | flext-cli/src/flext_cli/_utilities/output.py | 142-145 |
| status | Function | flext-cli/src/flext_cli/_utilities/output.py | 148-151 |
| summary | Function | flext-cli/src/flext_cli/_utilities/output.py | 154-164 |
| gate_result | Function | flext-cli/src/flext_cli/_utilities/output.py | 167-172 |
| project_failure | Function | flext-cli/src/flext_cli/_utilities/output.py | 175-190 |
| resolve_report_dir | Function | flext-cli/src/flext_cli/_utilities/output.py | 193-203 |
| resolve_report_path | Function | flext-cli/src/flext_cli/_utilities/output.py | 206-210 |
| test_output_resolve_message_type_with_none | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 14-17 |
| test_output_resolve_message_type_with_value | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 19-22 |
| test_output_resolve_style_with_none | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 24-27 |
| test_output_resolve_style_with_value | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 29-32 |
| test_output_message_payload_types | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 44-50 |
| test_output_progress_line_with_detail | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 52-58 |
| test_output_progress_line_no_detail | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 60-64 |
| test_output_status_line_success | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 66-73 |
| test_output_status_line_failure_no_elapsed | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 75-81 |
| test_output_gate_line_passed | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 83-87 |
| test_output_gate_line_failed_no_message | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 89-92 |
| test_output_summary_content | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 94-99 |
| test_output_debug_line | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 101-105 |
| test_output_table_error_with_message | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 107-110 |
| test_output_table_error_none | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 112-115 |
| test_emit_raw | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 117-121 |
| test_header | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 154-158 |
| test_progress | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py | 160-164 |
| test_gate_result | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_02.py | 24-28 |
| test_resolve_report_dir_workspace_scope | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_02.py | 30-36 |
| test_resolve_report_dir_project_scope | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_02.py | 38-41 |
| test_resolve_report_path | Test | flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_02.py | 43-48 |
| test_formatter_result_wins_over_all_fallbacks | Test | flext-cli/tests/unit/test_commands_utils_cov.py | 28-41 |

*... and 36 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (113 edge(s))
- `str` (18 edge(s))
- `readouterr` (12 edge(s))
- `Path` (9 edge(s))
- `resolve_report_dir` (9 edge(s))
- `resolve_report_path` (6 edge(s))
- `output_resolve_message_type` (5 edge(s))
- `output_gate_line` (4 edge(s))
- `output_progress_line` (4 edge(s))
- `output_resolve_style` (4 edge(s))
- `output_status_line` (4 edge(s))
- `output_table_error` (4 edge(s))
- `endswith` (3 edge(s))
- `commands_resolve_success_message` (3 edge(s))
- `isinstance` (2 edge(s))

### Incoming

- `that` (113 edge(s))
- `flext-cli/tests/unit/test_output_cov.py::TestsFlextCliOutputCov` (22 edge(s))
- `flext-cli/tests/unit/_cases/test_output_cov/testsflextclioutputcov_part_01.py::TestsFlextCliOutputCov` (18 edge(s))
- `str` (16 edge(s))
- `readouterr` (12 edge(s))
- `resolve_report_dir` (9 edge(s))
- `flext-cli/tests/unit/test_commands_utils_cov.py::TestsFlextCliCommands` (7 edge(s))
- `resolve_report_path` (6 edge(s))
- `flext-infra/tests/unit/test_infra_reporting_core.py::TestsFlextInfraInfraReportingCore` (6 edge(s))
- `output_resolve_message_type` (5 edge(s))
- `output_gate_line` (4 edge(s))
- `output_progress_line` (4 edge(s))
- `output_resolve_style` (4 edge(s))
- `output_status_line` (4 edge(s))
- `output_table_error` (4 edge(s))
