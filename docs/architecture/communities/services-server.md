# services-server

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 317 nodes

- **Size**: 317 nodes
- **Cohesion**: 0.2806
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| _create_entry_or_none | Function | flext-ldif/examples/05_schema_operations.py | 16-21 |
| intelligent_schema_building | Function | flext-ldif/examples/05_schema_operations.py | 24-88 |
| railway_schema_pipeline | Function | flext-ldif/examples/05_schema_operations.py | 334-436 |
| FlextLdif | Class | flext-ldif/src/flext_ldif/api.py | 27-283 |
| **init** | Function | flext-ldif/src/flext_ldif/api.py | 46-60 |
| **call** | Function | flext-ldif/src/flext_ldif/api.py | 62-71 |
| categorization | Function | flext-ldif/src/flext_ldif/api.py | 73-109 |
| filter_entry_attributes | Function | flext-ldif/src/flext_ldif/api.py | 111-121 |
| filter_schema_attribute_values | Function | flext-ldif/src/flext_ldif/api.py | 123-132 |
| acl | Function | flext-ldif/src/flext_ldif/api.py | 134-142 |
| entry | Function | flext-ldif/src/flext_ldif/api.py | 144-152 |
| resolve_base_server | Function | flext-ldif/src/flext_ldif/api.py | 154-158 |
| schema_server | Function | flext-ldif/src/flext_ldif/api.py | 160-168 |
| resolve_schema_server | Function | flext-ldif/src/flext_ldif/api.py | 170-178 |
| resolve_server_bundle | Function | flext-ldif/src/flext_ldif/api.py | 180-190 |
| resolve_server_constants | Function | flext-ldif/src/flext_ldif/api.py | 192-198 |
| list_registered_servers | Function | flext-ldif/src/flext_ldif/api.py | 200-203 |
| summarize_registry | Function | flext-ldif/src/flext_ldif/api.py | 205-210 |
| processing_pipeline | Function | flext-ldif/src/flext_ldif/api.py | 212-226 |
| migration_pipeline | Function | flext-ldif/src/flext_ldif/api.py | 228-253 |
| migrate | Function | flext-ldif/src/flext_ldif/api.py | 255-273 |
| validate_entries | Function | flext-ldif/src/flext_ldif/api.py | 276-283 |
| FlextLdifServerMethodsMixin | Class | flext-ldif/src/flext_ldif/servers/_base/mixins.py | 8-80 |
| project_processor_fields | Function | flext-ldif/src/flext_ldif/servers/_base/mixins.py | 12-32 |
| get_parent_server_from_instance | Function | flext-ldif/src/flext_ldif/servers/_base/mixins.py | 35-47 |
| get_priority_from_parent | Function | flext-ldif/src/flext_ldif/servers/_base/mixins.py | 50-60 |
| get_server_type_from_utilities | Function | flext-ldif/src/flext_ldif/servers/_base/mixins.py | 63-66 |
| _get_parent_server_safe | Function | flext-ldif/src/flext_ldif/servers/_base/mixins.py | 68-70 |
| _get_priority | Function | flext-ldif/src/flext_ldif/servers/_base/mixins.py | 72-76 |
| _get_server_type | Function | flext-ldif/src/flext_ldif/servers/_base/mixins.py | 78-80 |
| FlextLdifServersRfcAcl | Class | flext-ldif/src/flext_ldif/servers/_rfc/acl.py | 13-196 |
| **new** | Function | flext-ldif/src/flext_ldif/servers/_rfc/acl.py | 16-48 |
| **call** | Function | flext-ldif/src/flext_ldif/servers/_rfc/acl.py | 87-122 |
| can_handle_acl | Function | flext-ldif/src/flext_ldif/servers/_rfc/acl.py | 125-128 |
| can_handle_attribute | Function | flext-ldif/src/flext_ldif/servers/_rfc/acl.py | 131-134 |
| can_handle_objectclass | Function | flext-ldif/src/flext_ldif/servers/_rfc/acl.py | 137-140 |
| _denormalize_permission | Function | flext-ldif/src/flext_ldif/servers/_rfc/acl.py | 142-146 |
| _get_feature_fallback | Function | flext-ldif/src/flext_ldif/servers/_rfc/acl.py | 149-151 |
| _normalize_permission | Function | flext-ldif/src/flext_ldif/servers/_rfc/acl.py | 153-157 |
| _parse_acl | Function | flext-ldif/src/flext_ldif/servers/_rfc/acl.py | 160-175 |
| _preserve_unsupported_feature | Function | flext-ldif/src/flext_ldif/servers/_rfc/acl.py | 177-182 |
| _supports_feature | Function | flext-ldif/src/flext_ldif/servers/_rfc/acl.py | 185-187 |
| _write_acl | Function | flext-ldif/src/flext_ldif/servers/_rfc/acl.py | 190-196 |
| **call** | Function | flext-ldif/src/flext_ldif/servers/_rfc/schema.py | 132-170 |
| _ensure_trailing_newline | Function | flext-ldif/src/flext_ldif/servers/base.py | 17-19 |
| FlextLdifServersBase | Class | flext-ldif/src/flext_ldif/servers/base.py | 22-494 |
| **init** | Function | flext-ldif/src/flext_ldif/servers/base.py | 31-53 |
| **init_subclass** | Function | flext-ldif/src/flext_ldif/servers/base.py | 55-73 |
| acl | Function | flext-ldif/src/flext_ldif/servers/base.py | 76-79 |
| acl_server | Function | flext-ldif/src/flext_ldif/servers/base.py | 82-85 |

*... and 267 more members.*

## Execution Flows

- **validate_dns** (criticality: 0.61, depth: 1)

## Dependencies

### Outgoing

- `that` (167 edge(s))
- `ok` (122 edge(s))
- `isinstance` (64 edge(s))
- `fail` (39 edge(s))
- `unwrap` (33 edge(s))
- `len` (32 edge(s))
- `str` (25 edge(s))
- `get` (23 edge(s))
- `getattr` (22 edge(s))
- `exists` (22 edge(s))
- `lower` (21 edge(s))
- `model_validate` (18 edge(s))
- `create_real_entry` (18 edge(s))
- `append` (16 edge(s))
- `fail_op` (15 edge(s))

### Incoming

- `that` (166 edge(s))
- `ok` (86 edge(s))
- `unwrap` (29 edge(s))
- `isinstance` (21 edge(s))
- `len` (18 edge(s))
- `exists` (16 edge(s))
- `parse_attribute` (15 edge(s))
- `skip` (15 edge(s))
- `fail` (13 edge(s))
- `create_real_entry` (13 edge(s))
- `parse_ldif` (11 edge(s))
- `str` (10 edge(s))
- `flext-ldif/tests/unit/fixtures.py` (10 edge(s))
- `mkdir` (9 edge(s))
- `parse_server` (9 edge(s))
