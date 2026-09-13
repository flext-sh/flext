# json-json

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 71 nodes

- **Size**: 71 nodes
- **Cohesion**: 0.0188
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextCliUtilitiesJsonCoreMixin | Class | flext-cli/src/flext_cli/_utilities/_json/_core.py | 26-170 |
| json_dumps | Function | flext-cli/src/flext_cli/_utilities/_json/_core.py | 32-45 |
| json_loads | Function | flext-cli/src/flext_cli/_utilities/_json/_core.py | 48-54 |
| json_sort_keys | Function | flext-cli/src/flext_cli/_utilities/_json/_core.py | 57-75 |
| normalize_json_value | Function | flext-cli/src/flext_cli/_utilities/_json/_core.py | 78-80 |
| _json_write_content | Function | flext-cli/src/flext_cli/_utilities/_json/_core.py | 83-96 |
| json_read | Function | flext-cli/src/flext_cli/_utilities/_json/_core.py | 99-119 |
| json_write | Function | flext-cli/src/flext_cli/_utilities/_json/_core.py | 122-141 |
| _write | Function | flext-cli/src/flext_cli/_utilities/_json/_core.py | 130-134 |
| json_parse | Function | flext-cli/src/flext_cli/_utilities/_json/_core.py | 144-150 |
| json_as_mapping | Function | flext-cli/src/flext_cli/_utilities/_json/_core.py | 153-160 |
| json_as_sequence | Function | flext-cli/src/flext_cli/_utilities/_json/_core.py | 163-170 |
| test_json_read_missing_file | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 22-26 |
| test_json_read_valid_file | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 28-34 |
| test_json_read_invalid_json | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 36-41 |
| test_json_read_non_object_root | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 43-48 |
| test_json_write_and_read_roundtrip | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 50-58 |
| test_json_write_with_sort_keys | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 60-79 |
| test_json_write_pydantic_model | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 81-89 |
| test_json_parse_valid | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 91-94 |
| test_json_parse_invalid | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 96-99 |
| test_json_as_mapping_none | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 101-104 |
| test_json_as_mapping_valid | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 106-109 |
| test_json_as_mapping_non_mapping | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 111-114 |
| test_json_as_sequence_none | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 116-119 |
| test_json_as_sequence_valid | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 121-124 |
| test_json_as_sequence_non_sequence | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 126-129 |
| test_json_walk_path_existing | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 146-152 |
| test_json_walk_path_missing_intermediate | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py | 154-160 |
| test_json_deep_mapping_valid | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_02.py | 12-18 |
| test_json_deep_mapping_list | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_02.py | 26-32 |
| test_json_pick_int_variants | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_02.py | 43-55 |
| test_json_pick_bool_variants | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_02.py | 57-78 |
| test_json_nested_int | Test | flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_02.py | 80-86 |
| test_json_read_missing_file_fails_loudly | Test | flext-cli/tests/unit/test_json_cov.py | 27-31 |
| test_json_read_valid_object_returns_parsed_mapping | Test | flext-cli/tests/unit/test_json_cov.py | 33-41 |
| test_json_read_rejects_invalid_content | Test | flext-cli/tests/unit/test_json_cov.py | 47-56 |
| test_json_write_then_read_roundtrips_payload | Test | flext-cli/tests/unit/test_json_cov.py | 60-68 |
| test_json_write_sort_keys_orders_nested_keys | Test | flext-cli/tests/unit/test_json_cov.py | 70-90 |
| test_json_write_serializes_pydantic_model_as_object | Test | flext-cli/tests/unit/test_json_cov.py | 92-101 |
| test_json_parse_valid_text_succeeds | Test | flext-cli/tests/unit/test_json_cov.py | 105-108 |
| test_json_parse_invalid_text_fails | Test | flext-cli/tests/unit/test_json_cov.py | 110-114 |
| test_json_as_mapping_coerces_to_mapping_or_empty | Test | flext-cli/tests/unit/test_json_cov.py | 121-125 |
| test_json_as_sequence_coerces_to_list_or_empty | Test | flext-cli/tests/unit/test_json_cov.py | 130-134 |
| test_json_walk_path_returns_leaf_for_existing_path | Test | flext-cli/tests/unit/test_json_cov.py | 147-150 |
| test_json_walk_path_returns_none_when_unreachable | Test | flext-cli/tests/unit/test_json_cov.py | 155-160 |
| test_json_deep_mapping_descends_into_nested_object | Test | flext-cli/tests/unit/test_json_cov.py | 164-169 |
| test_json_deep_mapping_list_returns_nested_list | Test | flext-cli/tests/unit/test_json_cov.py | 175-180 |
| test_json_pick_int_coerces_scalar_variants | Test | flext-cli/tests/unit/test_json_cov.py | 194-203 |
| test_json_pick_bool_coerces_truthy_variants | Test | flext-cli/tests/unit/test_json_cov.py | 222-233 |

*... and 21 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (93 edge(s))
- `ok` (41 edge(s))
- `json_as_mapping` (21 edge(s))
- `validate_python` (20 edge(s))
- `json_loads` (20 edge(s))
- `json_read` (16 edge(s))
- `json_pick_bool` (15 edge(s))
- `json_write` (11 edge(s))
- `unwrap` (10 edge(s))
- `write_text` (9 edge(s))
- `fail` (8 edge(s))
- `list` (8 edge(s))
- `model_validate` (8 edge(s))
- `isinstance` (7 edge(s))
- `read_text` (7 edge(s))

### Incoming

- `that` (93 edge(s))
- `ok` (40 edge(s))
- `json_as_mapping` (21 edge(s))
- `json_loads` (20 edge(s))
- `flext-cli/tests/unit/test_json_cov.py::TestsFlextCliJsonCov` (18 edge(s))
- `flext-cli/tests/unit/_cases/test_json_cov/testsflextclijsoncov_part_01.py::TestsFlextCliJsonCov` (17 edge(s))
- `json_read` (16 edge(s))
- `json_pick_bool` (15 edge(s))
- `validate_python` (13 edge(s))
- `json_write` (11 edge(s))
- `unwrap` (10 edge(s))
- `list` (8 edge(s))
- `write_text` (8 edge(s))
- `model_validate` (8 edge(s))
- `json_pick_int` (7 edge(s))
