# flext-target-ldif-record

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 64 nodes

- **Size**: 64 nodes
- **Cohesion**: 0.3556
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextTargetLdifWriterError | Class | flext-target-ldif/src/flext_target_ldif/errors.py | 14-28 |
| **init** | Function | flext-target-ldif/src/flext_target_ldif/errors.py | 19-23 |
| **str** | Function | flext-target-ldif/src/flext_target_ldif/errors.py | 26-28 |
| Sink | Class | flext-target-ldif/src/flext_target_ldif/models.py | 125-243 |
| **init** | Function | flext-target-ldif/src/flext_target_ldif/models.py | 132-148 |
| ldif_writer | Function | flext-target-ldif/src/flext_target_ldif/models.py | 151-153 |
| logger | Function | flext-target-ldif/src/flext_target_ldif/models.py | 156-160 |
| clean_up | Function | flext-target-ldif/src/flext_target_ldif/models.py | 162-173 |
| process_batch | Function | flext-target-ldif/src/flext_target_ldif/models.py | 175-180 |
| process_record | Function | flext-target-ldif/src/flext_target_ldif/models.py | 182-193 |
| _get_ldif_writer | Function | flext-target-ldif/src/flext_target_ldif/models.py | 195-224 |
| _get_output_file | Function | flext-target-ldif/src/flext_target_ldif/models.py | 226-243 |
| FlextTargetLdifWriter | Class | flext-target-ldif/src/flext_target_ldif/writer.py | 31-257 |
| **init** | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 35-66 |
| **enter** | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 68-71 |
| **exit** | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 73-80 |
| record_count | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 83-85 |
| close | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 87-106 |
| _run_close | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 90-100 |
| open | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 108-115 |
| write_record | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 117-137 |
| _run_write_record | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 120-132 |
| _convert_record_to_entry | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 139-170 |
| _run__convert_record_to_entry | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 144-163 |
| generate_dn | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 172-178 |
| needs_base64_encoding | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 180-188 |
| write_attribute | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 190-199 |
| _write_entries_to_file | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 201-220 |
| _write_entry_attributes | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 222-242 |
| write_line | Function | flext-target-ldif/src/flext_target_ldif/writer.py | 244-257 |
| TestsFlextTargetLdifWriter | Class | flext-target-ldif/tests/unit/test_writer.py | 25-536 |
| test_init_with_defaults | Test | flext-target-ldif/tests/unit/test_writer.py | 28-48 |
| test_init_with_custom_values | Test | flext-target-ldif/tests/unit/test_writer.py | 50-86 |
| test_init_with_string_path | Test | flext-target-ldif/tests/unit/test_writer.py | 88-95 |
| test_open_success | Test | flext-target-ldif/tests/unit/test_writer.py | 97-108 |
| test_open_failure | Test | flext-target-ldif/tests/unit/test_writer.py | 110-118 |
| test_close_success | Test | flext-target-ldif/tests/unit/test_writer.py | 120-130 |
| test_close_when_not_open | Test | flext-target-ldif/tests/unit/test_writer.py | 132-136 |
| test_close_failure_when_output_directory_unwritable | Test | flext-target-ldif/tests/unit/test_writer.py | 141-156 |
| test_write_simple_record | Test | flext-target-ldif/tests/unit/test_writer.py | 158-184 |
| test_write_record_with_attribute_mapping | Test | flext-target-ldif/tests/unit/test_writer.py | 186-204 |
| test_write_record_auto_open | Test | flext-target-ldif/tests/unit/test_writer.py | 206-219 |
| test_write_record_missing_dn_field | Test | flext-target-ldif/tests/unit/test_writer.py | 221-231 |
| test_write_multiple_records | Test | flext-target-ldif/tests/unit/test_writer.py | 233-260 |
| testneeds_base64_encoding_space_start | Function | flext-target-ldif/tests/unit/test_writer.py | 262-265 |
| testneeds_base64_encoding_colon_start | Function | flext-target-ldif/tests/unit/test_writer.py | 267-270 |
| testneeds_base64_encoding_non_ascii | Function | flext-target-ldif/tests/unit/test_writer.py | 272-276 |
| testneeds_base64_encoding_newlines | Function | flext-target-ldif/tests/unit/test_writer.py | 278-282 |
| testneeds_base64_encoding_normal_value | Function | flext-target-ldif/tests/unit/test_writer.py | 284-288 |
| test_write_base64_encoded_attribute | Test | flext-target-ldif/tests/unit/test_writer.py | 290-319 |

*... and 14 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `AssertionError` (37 edge(s))
- `Path` (24 edge(s))
- `that` (22 edge(s))
- `NamedTemporaryFile` (16 edge(s))
- `unlink` (16 edge(s))
- `write` (14 edge(s))
- `isinstance` (11 edge(s))
- `ok` (11 edge(s))
- `read_text` (11 edge(s))
- `get` (10 edge(s))
- `str` (8 edge(s))
- `items` (5 edge(s))
- `decode` (5 edge(s))
- `split` (5 edge(s))
- `strip` (4 edge(s))

### Incoming

- `AssertionError` (35 edge(s))
- `Path` (22 edge(s))
- `that` (22 edge(s))
- `NamedTemporaryFile` (16 edge(s))
- `unlink` (16 edge(s))
- `read_text` (11 edge(s))
- `ok` (8 edge(s))
- `split` (5 edge(s))
- `startswith` (4 edge(s))
- `fail` (3 edge(s))
- `strip` (3 edge(s))
- `flext-target-ldif/src/flext_target_ldif/writer.py` (2 edge(s))
- `chmod` (2 edge(s))
- `TemporaryDirectory` (2 edge(s))
- `len` (2 edge(s))
