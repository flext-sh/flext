# utilities-extract

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 211 nodes

- **Size**: 211 nodes
- **Cohesion**: 0.2299
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextLdifUtilitiesACL | Class | flext-ldif/src/flext_ldif/_utilities/acl.py | 13-770 |
| _is_acl_subject_type | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 23-25 |
| _build_extensions | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 48-78 |
| extract_extra | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 60-64 |
| _build_subject_and_permissions | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 81-104 |
| _check_special_value | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 107-117 |
| _extract_from_match | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 120-131 |
| _extract_target_info | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 134-145 |
| _extract_version_and_name | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 148-167 |
| _normalize_permission | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 170-177 |
| _process_permission_list | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 180-194 |
| build_aci_subject | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 197-226 |
| build_aci_target_clause | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 229-239 |
| build_metadata_extensions | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 242-257 |
| build_permissions_dict | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 260-276 |
| extract_bind_rules | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 279-310 |
| extract_bind_rules_from_extensions | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 313-338 |
| _format_bind_rule_from_extension | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 341-368 |
| extract_component | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 371-397 |
| extract_permissions | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 400-442 |
| extract_target_extensions | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 445-463 |
| filter_supported_permissions | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 466-471 |
| format_aci_line | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 474-494 |
| format_aci_subject | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 497-509 |
| format_conversion_comments | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 512-537 |
| get_acl_attributes | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 540-561 |
| is_acl_attribute | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 564-568 |
| normalize_permission_key | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 571-573 |
| map_oid_to_oud_permissions | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 576-604 |
| map_oud_to_oid_permissions | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 607-630 |
| build_mapped_permissions_dict | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 633-640 |
| parse_aci | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 643-683 |
| parse_targetattr | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 686-697 |
| sanitize_acl_name | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 700-730 |
| sanitize_char | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 705-713 |
| split_acl_line | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 733-751 |
| validate_aci_format | Function | flext-ldif/src/flext_ldif/_utilities/acl.py | 754-770 |
| FlextLdifUtilitiesMetadata | Class | flext-ldif/src/flext_ldif/_utilities/metadata.py | 13-808 |
| dump_json_payload | Function | flext-ldif/src/flext_ldif/_utilities/metadata.py | 19-26 |
| dump_dynamic_metadata | Function | flext-ldif/src/flext_ldif/_utilities/metadata.py | 29-36 |
| _add_to_dict_metadata | Function | flext-ldif/src/flext_ldif/_utilities/metadata.py | 39-57 |
| _apply_category_update | Function | flext-ldif/src/flext_ldif/_utilities/metadata.py | 60-67 |
| _apply_filter_update | Function | flext-ldif/src/flext_ldif/_utilities/metadata.py | 70-74 |
| _apply_rejection_update | Function | flext-ldif/src/flext_ldif/_utilities/metadata.py | 77-81 |
| _build_schema_format_model | Function | flext-ldif/src/flext_ldif/_utilities/metadata.py | 84-111 |
| _extract_all_schema_details | Function | flext-ldif/src/flext_ldif/_utilities/metadata.py | 114-168 |
| _extract_desc_details | Function | flext-ldif/src/flext_ldif/_utilities/metadata.py | 171-189 |
| _extract_field_order | Function | flext-ldif/src/flext_ldif/_utilities/metadata.py | 192-216 |
| _extract_leading_trailing_spaces | Function | flext-ldif/src/flext_ldif/_utilities/metadata.py | 219-228 |
| _extract_matching_rule_details | Function | flext-ldif/src/flext_ldif/_utilities/metadata.py | 231-267 |

*... and 161 more members.*

## Execution Flows

- **validate_syntax_oid** (criticality: 0.69, depth: 1)
- **parse_attribute** (criticality: 0.63, depth: 2)
- **map_oid_to_oud_permissions** (criticality: 0.61, depth: 1)
- **map_oud_to_oid_permissions** (criticality: 0.61, depth: 1)

## Dependencies

### Outgoing

- `append` (62 edge(s))
- `group` (54 edge(s))
- `that` (54 edge(s))
- `search` (44 edge(s))
- `get` (37 edge(s))
- `isinstance` (32 edge(s))
- `strip` (31 edge(s))
- `len` (29 edge(s))
- `items` (25 edge(s))
- `lower` (25 edge(s))
- `str` (23 edge(s))
- `split` (16 edge(s))
- `dict` (15 edge(s))
- `fail` (15 edge(s))
- `startswith` (13 edge(s))

### Incoming

- `that` (54 edge(s))
- `flext-ldif/tests/unit/test_parser_utilities.py::TestsFlextLdifParserUtilities` (16 edge(s))
- `get_acl_attributes` (11 edge(s))
- `flext-ldif/tests/unit/test_acl_registry.py::TestsFlextLdifAclRegistry` (10 edge(s))
- `assert_success` (7 edge(s))
- `flext-ldif/tests/unit/test_oid_utilities.py::TestsFlextLdifOidUtilities` (7 edge(s))
- `flext-ldif/src/flext_ldif/utilities.py` (6 edge(s))
- `is_acl_attribute` (6 edge(s))
- `extract_from_definition` (5 edge(s))
- `extract_extensions` (5 edge(s))
- `flext-ldif/tests/unit/utilities/test_utilities_core.py::TestsFlextLdifUtilitiesCore` (5 edge(s))
- `flext-ldif/src/flext_ldif/_utilities/schema.py` (4 edge(s))
- `assert_failure` (4 edge(s))
- `unfold_lines` (4 edge(s))
- `flext-ldif/tests/unit/utilities/test_utilities_comprehensive.py::TestsFlextLdifUtilitiesComprehensive` (4 edge(s))
