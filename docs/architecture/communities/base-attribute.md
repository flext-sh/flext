# base-attribute

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 109 nodes

- **Size**: 109 nodes
- **Cohesion**: 0.3482
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextLdifServersBaseSchema | Class | flext-ldif/src/flext_ldif/servers/_base/schema.py | 13-600 |
| **new** | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 78-89 |
| **init** | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 91-106 |
| _extract_metadata_extensions | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 111-131 |
| _preserve_formatting | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 134-140 |
| _resolve_server_type | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 143-152 |
| build_attribute_metadata | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 155-208 |
| validate_and_track_oid | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 211-237 |
| can_handle_attribute | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 239-244 |
| can_handle_objectclass | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 246-251 |
| execute | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 254-274 |
| _coerce_schema_data | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 276-319 |
| _coerce_operation | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 321-325 |
| _detect_schema_type | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 327-335 |
| _is_objectclass_schema_type | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 337-340 |
| _coerce_attribute_model | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 342-352 |
| _coerce_objectclass_model | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 354-364 |
| _resolve_data | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 366-374 |
| _resolve_operation | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 376-385 |
| _parse_operation_kwarg | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 388-394 |
| parse_server | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 396-400 |
| parse_input | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 402-406 |
| parse_attribute | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 408-410 |
| parse_objectclass | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 412-414 |
| route_parse | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 416-438 |
| write | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 440-449 |
| write_attribute | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 451-454 |
| write_objectclass | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 456-459 |
| _auto_detect_operation | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 461-469 |
| _handle_parse_operation | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 471-491 |
| _handle_write_operation | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 493-513 |
| _hook_post_parse_attribute | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 515-519 |
| _hook_post_parse_objectclass | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 521-525 |
| _hook_validate_attributes | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 527-535 |
| _parse_attribute | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 537-542 |
| _parse_objectclass | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 544-549 |
| _route_operation | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 551-590 |
| _write_attribute | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 592-595 |
| _write_objectclass | Function | flext-ldif/src/flext_ldif/servers/_base/schema.py | 597-600 |
| FlextLdifServersOidSchema | Class | flext-ldif/src/flext_ldif/servers/_oid/schema.py | 14-498 |
| **init** | Function | flext-ldif/src/flext_ldif/servers/_oid/schema.py | 19-42 |
| extract_schemas_from_ldif | Function | flext-ldif/src/flext_ldif/servers/_oid/schema.py | 45-57 |
| _add_target_metadata | Function | flext-ldif/src/flext_ldif/servers/_oid/schema.py | 59-90 |
| _capture_attribute_values | Function | flext-ldif/src/flext_ldif/servers/_oid/schema.py | 92-102 |
| _hook_post_parse_attribute | Function | flext-ldif/src/flext_ldif/servers/_oid/schema.py | 105-115 |
| _normalize_oid_attribute | Function | flext-ldif/src/flext_ldif/servers/_oid/schema.py | 117-143 |
| _hook_post_parse_objectclass | Function | flext-ldif/src/flext_ldif/servers/_oid/schema.py | 146-158 |
| _normalize_oid_objectclass | Function | flext-ldif/src/flext_ldif/servers/_oid/schema.py | 160-193 |
| _normalize_attribute_names | Function | flext-ldif/src/flext_ldif/servers/_oid/schema.py | 195-202 |
| _normalize_auxiliary_typo | Function | flext-ldif/src/flext_ldif/servers/_oid/schema.py | 204-230 |

*... and 59 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `get` (57 edge(s))
- `isinstance` (42 edge(s))
- `ok` (28 edge(s))
- `str` (24 edge(s))
- `fail` (21 edge(s))
- `model_validate` (13 edge(s))
- `model_copy` (13 edge(s))
- `items` (12 edge(s))
- `debug` (11 edge(s))
- `fail_op` (10 edge(s))
- `super` (8 edge(s))
- `strip` (8 edge(s))
- `__setattr__` (7 edge(s))
- `exception` (7 edge(s))
- `unwrap` (6 edge(s))

### Incoming

- `flext-ldif/src/flext_ldif/servers/_base/schema.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/base.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/_oid/schema.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/oid.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/_oud/schema.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/oud.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/_rfc/schema.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/servers/rfc.py` (1 edge(s))
