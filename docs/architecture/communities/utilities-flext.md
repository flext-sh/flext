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

Community of 3956 nodes

- **Size**: 3956 nodes
- **Cohesion**: 0.3414
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
| ------ | ------ | ------ | ------- |
| parse_semver | Function | libs/versioning.py | 19-29 |
| bump_version | Function | libs/versioning.py | 32-42 |
| current_workspace_version | Function | libs/versioning.py | 59-73 |
| replace_project_version | Function | libs/versioning.py | 76-91 |
| test_read_nonexistent_file | Test | flext-tests/tests/unit/_files_parts/read.py | 80-96 |
| _find_project_root | Function | flext-tests/src/flext_tests/_fixtures/project_metadata.py | 24-32 |
| project_metadata | Function | flext-tests/src/flext_tests/_fixtures/project_metadata.py | 36-38 |
| project_tool_flext | Function | flext-tests/src/flext_tests/_fixtures/project_metadata.py | 42-44 |
| project_namespace_config | Function | flext-tests/src/flext_tests/_fixtures/project_metadata.py | 48-50 |
| MarkdownCodeBlockItem | Class | flext-tests/src/flext_tests/_fixtures/markdown_validation.py | 41-85 |
| **init** | Function | flext-tests/src/flext_tests/_fixtures/markdown_validation.py | 44-51 |
| runtest | Function | flext-tests/src/flext_tests/_fixtures/markdown_validation.py | 54-70 |
| repr_failure | Function | flext-tests/src/flext_tests/_fixtures/markdown_validation.py | 73-80 |
| reportinfo | Function | flext-tests/src/flext_tests/_fixtures/markdown_validation.py | 83-85 |
| pytest_collect_file | Function | flext-tests/src/flext_tests/_fixtures/markdown_validation.py | 103-114 |
| MarkdownValidationError | Class | flext-tests/src/flext_tests/_fixtures/markdown_validation.py | 117-118 |
| FlextTestsFixturesDSLMixin | Class | flext-tests/src/flext_tests/_utilities/fixtures_dsl.py | 17-126 |
| _root | Function | flext-tests/src/flext_tests/_utilities/fixtures_dsl.py | 41-45 |
| _resolve_path | Function | flext-tests/src/flext_tests/_utilities/fixtures_dsl.py | 48-51 |
| path | Function | flext-tests/src/flext_tests/_utilities/fixtures_dsl.py | 54-58 |
| load | Function | flext-tests/src/flext_tests/_utilities/fixtures_dsl.py | 61-62 |
| exists | Function | flext-tests/src/flext_tests/_utilities/fixtures_dsl.py | 65-66 |
| servers | Function | flext-tests/src/flext_tests/_utilities/fixtures_dsl.py | 69-73 |
| kinds | Function | flext-tests/src/flext_tests/_utilities/fixtures_dsl.py | 76-89 |
| for_group | Function | flext-tests/src/flext_tests/_utilities/fixtures_dsl.py | 92-94 |
| for_kind | Function | flext-tests/src/flext_tests/_utilities/fixtures_dsl.py | 97-103 |
| all_fixtures | Function | flext-tests/src/flext_tests/_utilities/fixtures_dsl.py | 106-108 |
| pytest_params | Function | flext-tests/src/flext_tests/_utilities/fixtures_dsl.py | 111-117 |
| all_pytest_params | Function | flext-tests/src/flext_tests/_utilities/fixtures_dsl.py | 120-126 |
| FlextTestsValidatorUtilitiesMixin | Class | flext-tests/src/flext_tests/_utilities/validator.py | 15-205 |
| create_violation | Function | flext-tests/src/flext_tests/_utilities/validator.py | 19-50 |
| find_line_number | Function | flext-tests/src/flext_tests/_utilities/validator.py | 53-58 |
| split_import_targets | Function | flext-tests/src/flext_tests/_utilities/validator.py | 61-69 |
| approved | Function | flext-tests/src/flext_tests/_utilities/validator.py | 72-96 |
| code_match | Function | flext-tests/src/flext_tests/_utilities/validator.py | 99-144 |
| real_comment | Function | flext-tests/src/flext_tests/_utilities/validator.py | 147-163 |
| except_block_only_pass | Function | flext-tests/src/flext_tests/_utilities/validator.py | 166-205 |
| FlextValidatorBypass | Class | flext-tests/src/flext_tests/_validator/bypass.py | 23-149 |
| _check_exception_swallowing | Function | flext-tests/src/flext_tests/_validator/bypass.py | 32-67 |
| _check_noqa | Function | flext-tests/src/flext_tests/_validator/bypass.py | 70-92 |
| _check_pragma_no_cover | Function | flext-tests/src/flext_tests/_validator/bypass.py | 95-121 |
| _scan_file | Function | flext-tests/src/flext_tests/_validator/bypass.py | 125-149 |
| FlextValidatorImports | Class | flext-tests/src/flext_tests/_validator/imports.py | 23-198 |
| _check_import_error_handling | Function | flext-tests/src/flext_tests/_validator/imports.py | 29-51 |

*... and 3906 more members.*

## Execution Flows

- **execute** (criticality: 0.91, depth: 10)
- **fetch_integration** (criticality: 0.89, depth: 9)
- **execute** (criticality: 0.88, depth: 9)
- **get** (criticality: 0.87, depth: 5)
- **post** (criticality: 0.87, depth: 5)
- **_execute_test_command** (criticality: 0.87, depth: 8)
- **execute** (criticality: 0.87, depth: 9)
- **check** (criticality: 0.87, depth: 5)
- **_execute_tap_command** (criticality: 0.86, depth: 8)
- **auth_headers** (criticality: 0.86, depth: 5)
- *... and 140 more flows.*

## Dependencies

### Outgoing

- `append` (662 edge(s))
- `that` (661 edge(s))
- `len` (554 edge(s))
- `write_text` (519 edge(s))
- `isinstance` (502 edge(s))
- `str` (426 edge(s))
- `tuple` (402 edge(s))
- `get` (383 edge(s))
- `getattr` (381 edge(s))
- `strip` (328 edge(s))
- `ok` (310 edge(s))
- `fail` (272 edge(s))
- `startswith` (255 edge(s))
- `extend` (223 edge(s))
- `mkdir` (217 edge(s))

### Incoming

- `that` (660 edge(s))
- `write_text` (428 edge(s))
- `mkdir` (166 edge(s))
- `len` (118 edge(s))
- `read_text` (80 edge(s))
- `flext-infra/src/flext_infra/_constants/source_code.py` (74 edge(s))
- `exists` (63 edge(s))
- `isinstance` (61 edge(s))
- `ok` (61 edge(s))
- `flext-infra/src/flext_infra/utilities.py` (48 edge(s))
- `detect_file` (47 edge(s))
- `DetectorContext` (47 edge(s))
- `apply_to_source` (43 edge(s))
- `flext-ldif/src/flext_ldif/_constants/base.py` (41 edge(s))
- `Path` (36 edge(s))
