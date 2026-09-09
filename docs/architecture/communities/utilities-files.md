# utilities-files

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 206 nodes

- **Size**: 206 nodes
- **Cohesion**: 0.0579
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextCliUtilitiesFileTestHelpersMixin | Class | flext-cli/src/flext_cli/_utilities/_file_test_helper_parts/flextcliutilitiesfiletesthelpersmixin_part_01.py | 24-98 |
| files_context | Function | flext-cli/src/flext_cli/_utilities/_file_test_helper_parts/flextcliutilitiesfiletesthelpersmixin_part_01.py | 29-84 |
| _files_write_structured | Function | flext-cli/src/flext_cli/_utilities/_file_test_helper_parts/flextcliutilitiesfiletesthelpersmixin_part_01.py | 87-98 |
| FlextCliUtilitiesFileTestHelpersMixin | Class | flext-cli/src/flext_cli/_utilities/_file_test_helper_parts/flextcliutilitiesfiletesthelpersmixin_part_04.py | 22-44 |
| files_parse_content | Function | flext-cli/src/flext_cli/_utilities/_file_test_helper_parts/flextcliutilitiesfiletesthelpersmixin_part_04.py | 26-44 |
| FlextCliUtilitiesFiles | Class | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 19-188 |
| files_delete | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 32-47 |
| _delete | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 36-43 |
| files_read_text | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 50-55 |
| files_write_text | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 58-67 |
| _write | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 177-184 |
| files_read_json | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 70-79 |
| _load | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 124-132 |
| files_read_json_model | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 82-95 |
| files_read_first_json_model | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 98-116 |
| files_read_json_lines_model | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 119-136 |
| files_read_yaml | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 139-143 |
| files_read_yaml_model | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 146-150 |
| files_read_yaml_model_chain | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 153-169 |
| files_write_csv | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py | 172-188 |
| FlextCliUtilitiesFiles | Class | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_04.py | 23-162 |
| files_detect_format | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_04.py | 27-35 |
| files_detect_format_from_content | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_04.py | 38-66 |
| files_detect_format_from_path | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_04.py | 69-78 |
| files_load_auto_mapping | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_04.py | 81-99 |
| csv_loads | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_04.py | 102-108 |
| files_copy_directory | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_04.py | 111-129 |
| _copy | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_04.py | 120-125 |
| files_create_temporary_directory | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_04.py | 132-145 |
| _create | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_04.py | 140-141 |
| files_remove_directory | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_04.py | 148-162 |
| _remove | Function | flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_04.py | 156-158 |
| FlextCliUtilitiesRulesLoadersMixin | Class | flext-cli/src/flext_cli/_utilities/_rules/_loaders.py | 26-185 |
| rules_resolve_scope | Function | flext-cli/src/flext_cli/_utilities/_rules/_loaders.py | 30-39 |
| rules_load_scoped_config | Function | flext-cli/src/flext_cli/_utilities/_rules/_loaders.py | 42-54 |
| rules_load_registry | Function | flext-cli/src/flext_cli/_utilities/_rules/_loaders.py | 57-85 |
| rules_load_local_definitions | Function | flext-cli/src/flext_cli/_utilities/_rules/_loaders.py | 88-185 |
| FlextCliUtilitiesToml | Class | flext-cli/src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_06.py | 21-119 |
| toml_read | Function | flext-cli/src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_06.py | 25-38 |
| toml_read_document | Function | flext-cli/src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_06.py | 41-50 |
| toml_read_json | Function | flext-cli/src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_06.py | 53-68 |
| _resolve_taplo_config | Function | flext-cli/src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_06.py | 71-78 |
| _format_pyproject | Function | flext-cli/src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_06.py | 81-104 |
| toml_write_document | Function | flext-cli/src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_06.py | 107-119 |
| FlextCliUtilitiesXlsxRecalc | Class | flext-cli/src/flext_cli/_utilities/_xlxx/xlsx_recalc.py | 15-139 |
| xlsx_recalc | Function | flext-cli/src/flext_cli/_utilities/_xlxx/xlsx_recalc.py | 24-34 |
| _xlsx_recalc_unchecked | Function | flext-cli/src/flext_cli/_utilities/_xlxx/xlsx_recalc.py | 37-83 |
| xlsx_recalc_parity | Function | flext-cli/src/flext_cli/_utilities/_xlxx/xlsx_recalc.py | 86-139 |
| FlextCliUtilitiesConfig | Class | flext-cli/src/flext_cli/_utilities/config.py | 30-115 |
| _read_by_suffix | Function | flext-cli/src/flext_cli/_utilities/config.py | 34-43 |

*... and 156 more members.*

## Execution Flows

- **config_load_dir** (criticality: 0.57, depth: 4)

## Dependencies

### Outgoing

- `that` (168 edge(s))
- `ok` (111 edge(s))
- `fail` (80 edge(s))
- `write_text` (75 edge(s))
- `Path` (57 edge(s))
- `mkdir` (30 edge(s))
- `exists` (23 edge(s))
- `str` (22 edge(s))
- `read_text` (17 edge(s))
- `TemporaryDirectory` (14 edge(s))
- `dict` (12 edge(s))
- `not_none` (12 edge(s))
- `validate_python` (11 edge(s))
- `from_failure` (11 edge(s))
- `isinstance` (11 edge(s))

### Incoming

- `that` (168 edge(s))
- `ok` (78 edge(s))
- `write_text` (72 edge(s))
- `fail` (33 edge(s))
- `Path` (32 edge(s))
- `mkdir` (25 edge(s))
- `flext-cli/tests/unit/test_yaml_cov.py::TestsFlextCliYamlCov` (22 edge(s))
- `exists` (16 edge(s))
- `TemporaryDirectory` (13 edge(s))
- `not_none` (12 edge(s))
- `files_read_text` (11 edge(s))
- `read_text` (11 edge(s))
- `yaml_parse` (11 edge(s))
- `rules_load_local_definitions` (10 edge(s))
- `unwrap` (9 edge(s))
