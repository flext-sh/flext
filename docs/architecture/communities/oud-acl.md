# oud-acl


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 93 nodes

- **Size**: 93 nodes
- **Cohesion**: 0.2475
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextLdifServersBaseSchemaAcl | Class | flext-ldif/src/flext_ldif/servers/_base/acl.py | 11-296 |
| __init__ | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 35-44 |
| resolve_acl_attributes | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 48-50 |
| matches_acl_attribute | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 52-55 |
| can_handle | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 59-62 |
| can_handle_acl | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 64-67 |
| can_handle_attribute | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 69-72 |
| can_handle_objectclass | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 74-77 |
| create_metadata | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 79-94 |
| execute | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 97-114 |
| format_acl_value | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 116-148 |
| parse_server | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 150-152 |
| parse_input | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 154-156 |
| write | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 158-160 |
| _coerce_acl_data | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 162-180 |
| _coerce_operation | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 182-186 |
| _detect_operation | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 188-192 |
| _execute_acl_parse | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 194-199 |
| _execute_acl_write | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 201-206 |
| _execute_detected_operation | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 208-223 |
| _extract_acl_parameters | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 225-237 |
| _get_feature_fallback | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 239-241 |
| _hook_format_acl_name_pattern | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 243-249 |
| _hook_post_parse_acl | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 251-253 |
| _parse_acl | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 255-258 |
| _resolve_data | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 260-267 |
| _resolve_operation | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 269-278 |
| _parse_operation_kwarg | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 281-287 |
| _supports_feature | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 289-291 |
| _write_acl | Function | flext-ldif/src/flext_ldif/servers/_base/acl.py | 293-296 |
| FlextLdifServersOudAciMixin | Class | flext-ldif/src/flext_ldif/servers/_oud/aci.py | 20-178 |
| _find_aci_in_dict | Function | flext-ldif/src/flext_ldif/servers/_oud/aci.py | 24-33 |
| find_aci_values | Function | flext-ldif/src/flext_ldif/servers/_oud/aci.py | 36-83 |
| normalize_aci_value | Function | flext-ldif/src/flext_ldif/servers/_oud/aci.py | 86-90 |
| normalize_aci_value_simple | Function | flext-ldif/src/flext_ldif/servers/_oud/aci.py | 93-101 |
| process_aci_list_for_finalize | Function | flext-ldif/src/flext_ldif/servers/_oud/aci.py | 104-135 |
| process_single_aci_value | Function | flext-ldif/src/flext_ldif/servers/_oud/aci.py | 138-159 |
| _validate_aci_macros | Function | flext-ldif/src/flext_ldif/servers/_oud/aci.py | 162-164 |
| validate_aci_macros_in_entry | Function | flext-ldif/src/flext_ldif/servers/_oud/aci.py | 167-178 |
| FlextLdifServersOudAcl | Class | flext-ldif/src/flext_ldif/servers/_oud/acl.py | 15-469 |
| __init__ | Function | flext-ldif/src/flext_ldif/servers/_oud/acl.py | 26-51 |
| _extension_get_str | Function | flext-ldif/src/flext_ldif/servers/_oud/acl.py | 54-61 |
| _is_aci_start | Function | flext-ldif/src/flext_ldif/servers/_oud/acl.py | 64-68 |
| _is_ds_cfg_acl | Function | flext-ldif/src/flext_ldif/servers/_oud/acl.py | 71-75 |
| _scalar_or_list_value | Function | flext-ldif/src/flext_ldif/servers/_oud/acl.py | 78-80 |
| can_handle | Function | flext-ldif/src/flext_ldif/servers/_oud/acl.py | 83-85 |
| can_handle_acl | Function | flext-ldif/src/flext_ldif/servers/_oud/acl.py | 88-123 |
| resolve_acl_attributes | Function | flext-ldif/src/flext_ldif/servers/_oud/acl.py | 126-128 |
| _build_aci_permissions | Function | flext-ldif/src/flext_ldif/servers/_oud/acl.py | 130-214 |
| _build_aci_subject | Function | flext-ldif/src/flext_ldif/servers/_oud/acl.py | 216-242 |

*... and 43 more members.*

## Execution Flows

- **_add_transformation_comments** (criticality: 0.60, depth: 3)
- **process_single_aci_value** (criticality: 0.57, depth: 1)

## Dependencies

### Outgoing

- `isinstance` (45 edge(s))
- `get` (41 edge(s))
- `lower` (26 edge(s))
- `ok` (21 edge(s))
- `items` (21 edge(s))
- `to_str` (16 edge(s))
- `str` (15 edge(s))
- `validate_python` (15 edge(s))
- `fail` (13 edge(s))
- `bool` (13 edge(s))
- `list` (11 edge(s))
- `model_validate` (10 edge(s))
- `append` (10 edge(s))
- `model_copy` (9 edge(s))
- `extend` (9 edge(s))

### Incoming

- `flext-ldif/src/flext_ldif/servers/_oud/helpers.py` (5 edge(s))
- `flext-ldif/src/flext_ldif/servers/_base/acl.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/base.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/_oud/aci.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/_oud/acl.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/oud.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/_oud/acl_extract.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/_oud/acl_metadata.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/_oud/comments.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/_oud/transform.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/_oud/utilities.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/_rfc/acl.py::FlextLdifServersRfcAcl` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/rfc.py` (1 edge(s))
