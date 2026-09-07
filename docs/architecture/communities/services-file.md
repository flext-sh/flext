# services-file


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 77 nodes

- **Size**: 77 nodes
- **Cohesion**: 0.1818
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextCliAuth | Class | flext-cli/src/flext_cli/services/auth.py | 21-85 |
| validate_credentials | Function | flext-cli/src/flext_cli/services/auth.py | 27-29 |
| save_auth_token | Function | flext-cli/src/flext_cli/services/auth.py | 31-40 |
| fetch_auth_token | Function | flext-cli/src/flext_cli/services/auth.py | 42-47 |
| authenticate | Function | flext-cli/src/flext_cli/services/auth.py | 49-55 |
| _resolve_token | Function | flext-cli/src/flext_cli/services/auth.py | 57-65 |
| _persist_token | Function | flext-cli/src/flext_cli/services/auth.py | 67-78 |
| clear_auth_tokens | Function | flext-cli/src/flext_cli/services/auth.py | 80-85 |
| FlextCliFileTools | Class | flext-cli/src/flext_cli/services/file_tools.py | 11-118 |
| read_json_file | Function | flext-cli/src/flext_cli/services/file_tools.py | 15-17 |
| read_text_file | Function | flext-cli/src/flext_cli/services/file_tools.py | 20-22 |
| read_json_model | Function | flext-cli/src/flext_cli/services/file_tools.py | 25-29 |
| read_yaml_file | Function | flext-cli/src/flext_cli/services/file_tools.py | 32-37 |
| read_yaml_model | Function | flext-cli/src/flext_cli/services/file_tools.py | 40-44 |
| read_yaml_model_chain | Function | flext-cli/src/flext_cli/services/file_tools.py | 47-51 |
| write_json_file | Function | flext-cli/src/flext_cli/services/file_tools.py | 54-60 |
| write_yaml_file | Function | flext-cli/src/flext_cli/services/file_tools.py | 63-67 |
| write_csv_file | Function | flext-cli/src/flext_cli/services/file_tools.py | 70-74 |
| read_csv_file_with_headers | Function | flext-cli/src/flext_cli/services/file_tools.py | 77-81 |
| read_binary_file | Function | flext-cli/src/flext_cli/services/file_tools.py | 84-86 |
| write_binary_file | Function | flext-cli/src/flext_cli/services/file_tools.py | 89-91 |
| copy_file | Function | flext-cli/src/flext_cli/services/file_tools.py | 94-98 |
| detect_file_format | Function | flext-cli/src/flext_cli/services/file_tools.py | 101-103 |
| delete_path | Function | flext-cli/src/flext_cli/services/file_tools.py | 106-108 |
| list_directory_names | Function | flext-cli/src/flext_cli/services/file_tools.py | 111-113 |
| load_file_auto_dict | Function | flext-cli/src/flext_cli/services/file_tools.py | 116-118 |
| test_files_detect_format_known | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_01.py | 25-31 |
| test_files_detect_format_unknown | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_01.py | 34-37 |
| test_files_read_write_json | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_01.py | 58-64 |
| test_files_read_json_missing | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_01.py | 66-69 |
| test_files_read_json_model | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_01.py | 71-77 |
| test_files_read_write_yaml | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_01.py | 93-99 |
| test_files_read_yaml_missing | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_01.py | 101-104 |
| test_files_read_yaml_empty_path | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_01.py | 106-109 |
| test_files_write_read_csv | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_01.py | 111-119 |
| test_files_read_csv_missing | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_01.py | 121-124 |
| test_files_write_read_binary | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_01.py | 126-133 |
| test_files_read_binary_missing | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_01.py | 135-138 |
| test_files_copy | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_01.py | 140-147 |
| test_files_load_auto_mapping_json | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_02.py | 73-78 |
| test_files_load_auto_mapping_yaml | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_02.py | 80-85 |
| test_files_load_auto_mapping_unsupported | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_02.py | 87-92 |
| test_files_load_auto_mapping_non_mapping_json | Test | flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_02.py | 94-99 |
| test_load_file_auto_dict_reads_supported_mappings | Test | flext-cli/tests/unit/test_file_derived_contracts.py | 34-44 |
| test_load_file_auto_dict_rejects_unsupported_extension | Test | flext-cli/tests/unit/test_file_derived_contracts.py | 46-53 |
| test_load_file_auto_dict_rejects_non_mapping_payload | Test | flext-cli/tests/unit/test_file_derived_contracts.py | 55-62 |
| test_missing_file_fails_loud | Test | flext-cli/tests/unit/test_file_tools_yaml.py | 67-73 |
| test_detect_file_format_returns_known_format | Test | flext-cli/tests/unit/test_files_cov.py | 32-38 |
| test_detect_file_format_fails_for_unknown_extension | Test | flext-cli/tests/unit/test_files_cov.py | 41-46 |
| test_write_then_read_json_round_trips | Test | flext-cli/tests/unit/test_files_cov.py | 64-70 |

*... and 27 more members.*

## Execution Flows

- **_persist_token** (criticality: 0.56, depth: 2)

## Dependencies

### Outgoing

- `ok` (39 edge(s))
- `that` (36 edge(s))
- `fail` (24 edge(s))
- `Path` (16 edge(s))
- `write_text` (11 edge(s))
- `exists` (7 edge(s))
- `load_file_auto_dict` (7 edge(s))
- `read_yaml_file` (6 edge(s))
- `detect_file_format` (4 edge(s))
- `read_binary_file` (4 edge(s))
- `read_csv_file_with_headers` (4 edge(s))
- `read_json_file` (4 edge(s))
- `auth_token_file_path` (3 edge(s))
- `s` (2 edge(s))
- `map` (2 edge(s))

### Incoming

- `ok` (37 edge(s))
- `that` (35 edge(s))
- `fail` (21 edge(s))
- `flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_01.py::TestsFlextCliFilesCov` (13 edge(s))
- `flext-cli/tests/unit/test_files_cov.py::TestsFlextCliFilesCov` (13 edge(s))
- `write_text` (11 edge(s))
- `load_file_auto_dict` (7 edge(s))
- `read_yaml_file` (6 edge(s))
- `exists` (6 edge(s))
- `detect_file_format` (4 edge(s))
- `read_binary_file` (4 edge(s))
- `read_csv_file_with_headers` (4 edge(s))
- `read_json_file` (4 edge(s))
- `flext-cli/tests/unit/_cases/test_files_cov/testsflextclifilescov_part_02.py::TestsFlextCliFilesCov` (4 edge(s))
- `flext-cli/tests/unit/test_file_derived_contracts.py::TestsFileDerivedContracts` (3 edge(s))
