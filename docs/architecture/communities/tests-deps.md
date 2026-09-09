# tests-deps

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 110 nodes

- **Size**: 110 nodes
- **Cohesion**: 0.1808
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextInfraDependencyDetectionService | Class | flext-infra/src/flext_infra/deps/detection.py | 15-132 |
| **init** | Function | flext-infra/src/flext_infra/deps/detection.py | 20-24 |
| _read_plain | Function | flext-infra/src/flext_infra/deps/detection.py | 27-36 |
| _run_raw | Function | flext-infra/src/flext_infra/deps/detection.py | 39-50 |
| classify_issues | Function | flext-infra/src/flext_infra/deps/detection.py | 53-81 |
| build_project_report | Function | flext-infra/src/flext_infra/deps/detection.py | 83-108 |
| _module_names | Function | flext-infra/src/flext_infra/deps/detection.py | 89-97 |
| discover_project_paths | Function | flext-infra/src/flext_infra/deps/detection.py | 110-132 |
| test_markdown_prefers_local_config_when_root_is_missing | Test | flext-infra/tests/unit/check/extended_gate_bandit_markdown_tests.py | 144-155 |
| test_markdown_never_inherits_parent_config | Test | flext-infra/tests/unit/check/extended_gate_bandit_markdown_tests.py | 157-172 |
| test_markdown_excludes_operational_beads_storage | Test | flext-infra/tests/unit/check/extended_gate_bandit_markdown_tests.py | 174-188 |
| test_markdown_excludes_agentsctl_provider_projections | Test | flext-infra/tests/unit/check/extended_gate_bandit_markdown_tests.py | 194-210 |
| test_markdown_keeps_project_owned_github_markdown | Test | flext-infra/tests/unit/check/extended_gate_bandit_markdown_tests.py | 212-225 |
| test_markdown_fix_applies_the_auto_fixable_rules | Test | flext-infra/tests/unit/check/extended_gate_bandit_markdown_tests.py | 307-333 |
| test_pyright_uses_project_config_target_when_configured | Test | flext-infra/tests/unit/check/extended_runners_extra_tests.py | 63-94 |
| test_over_cap_module_is_flagged | Test | flext-infra/tests/unit/check/loc_cap_gate_tests.py | 62-73 |
| test_under_cap_module_passes | Test | flext-infra/tests/unit/check/loc_cap_gate_tests.py | 75-85 |
| TestsFlextInfraDepsDetectionClassify | Class | flext-infra/tests/unit/deps/test_detection_classify.py | 14-116 |
| test_classify_dep001 | Test | flext-infra/tests/unit/deps/test_detection_classify.py | 17-23 |
| test_classify_dep002 | Test | flext-infra/tests/unit/deps/test_detection_classify.py | 25-31 |
| test_classify_dep003 | Test | flext-infra/tests/unit/deps/test_detection_classify.py | 33-39 |
| test_classify_dep004 | Test | flext-infra/tests/unit/deps/test_detection_classify.py | 41-47 |
| test_non_dict_error_skipped | Test | flext-infra/tests/unit/deps/test_detection_classify.py | 49-53 |
| test_missing_code_skipped | Test | flext-infra/tests/unit/deps/test_detection_classify.py | 55-61 |
| test_unknown_code_skipped | Test | flext-infra/tests/unit/deps/test_detection_classify.py | 63-73 |
| test_multiple_issues | Test | flext-infra/tests/unit/deps/test_detection_classify.py | 75-85 |
| test_classify_issues_with_missing_error_field | Test | flext-infra/tests/unit/deps/test_detection_classify.py | 87-91 |
| test_builds_report | Test | flext-infra/tests/unit/deps/test_detection_classify.py | 93-102 |
| test_success | Test | flext-infra/tests/unit/deps/test_detection_deptry.py | 31-43 |
| test_failure | Test | flext-infra/tests/unit/deps/test_detection_deptry.py | 45-49 |
| test_filters_without_pyproject | Test | flext-infra/tests/unit/deps/test_detection_deptry.py | 51-62 |
| test_success_with_issues | Test | flext-infra/tests/unit/deps/test_detection_deptry.py | 64-83 |
| test_no_config_file | Test | flext-infra/tests/unit/deps/test_detection_deptry.py | 85-96 |
| test_invalid_and_empty_json_output_surfaces_failure | Test | flext-infra/tests/unit/deps/test_detection_deptry.py | 107-127 |
| test_with_extend_exclude_and_cleanup | Test | flext-infra/tests/unit/deps/test_detection_deptry.py | 129-147 |
| TestsFlextInfraDepsDetectionDiscover | Class | flext-infra/tests/unit/deps/test_detection_discover.py | 16-48 |
| test_success | Test | flext-infra/tests/unit/deps/test_detection_discover.py | 19-29 |
| test_failure | Test | flext-infra/tests/unit/deps/test_detection_discover.py | 31-35 |
| test_filters_without_pyproject | Test | flext-infra/tests/unit/deps/test_detection_discover.py | 37-48 |
| TestsFlextInfraDepsDetectionModels | Class | flext-infra/tests/unit/deps/test_detection_models.py | 15-163 |
| test_service_initialization | Test | flext-infra/tests/unit/deps/test_detection_models.py | 65-67 |
| test_default_module_to_types_package_mapping | Test | flext-infra/tests/unit/deps/test_detection_models.py | 69-81 |
| TestsFlextInfraDepsDetectionPipCheck | Class | flext-infra/tests/unit/deps/test_detection_pip_check.py | 18-62 |
| test_run_pip_check | Test | flext-infra/tests/unit/deps/test_detection_pip_check.py | 36-62 |
| _StubToml | Class | flext-infra/tests/unit/deps/test_detection_typings.py | 15-25 |
| **init** | Function | flext-infra/tests/unit/deps/test_detection_typings.py | 16-18 |
| read_plain | Function | flext-infra/tests/unit/deps/test_detection_typings.py | 20-25 |
| TestsFlextInfraDepsDetectionTypings | Class | flext-infra/tests/unit/deps/test_detection_typings.py | 28-79 |
| test_success | Test | flext-infra/tests/unit/deps/test_detection_typings.py | 31-37 |
| test_failure_fails_loud | Test | flext-infra/tests/unit/deps/test_detection_typings.py | 39-44 |

*... and 60 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (83 edge(s))
- `ok` (46 edge(s))
- `write_text` (23 edge(s))
- `create_command_output` (16 edge(s))
- `len` (15 edge(s))
- `mkdir` (14 edge(s))
- `fail` (14 edge(s))
- `create_deptry_service` (12 edge(s))
- `str` (10 edge(s))
- `Path` (9 edge(s))
- `infra_mapping_result` (9 edge(s))
- `from_failure` (8 edge(s))
- `mk_project` (7 edge(s))
- `get` (6 edge(s))
- `sequence_runner` (6 edge(s))

### Incoming

- `that` (83 edge(s))
- `ok` (29 edge(s))
- `write_text` (22 edge(s))
- `create_command_output` (16 edge(s))
- `mkdir` (14 edge(s))
- `len` (12 edge(s))
- `create_deptry_service` (12 edge(s))
- `infra_mapping_result` (9 edge(s))
- `mk_project` (7 edge(s))
- `str` (7 edge(s))
- `flext-infra/tests/unit/deps/test_detection_deptry.py::TestsFlextInfraDepsDetectionDeptry` (7 edge(s))
- `fail` (7 edge(s))
- `Path` (7 edge(s))
- `flext-infra/tests/unit/check/extended_gate_bandit_markdown_tests.py::TestBanditAndMarkdownGates` (6 edge(s))
- `sequence_runner` (6 edge(s))
