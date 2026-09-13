# servers-relaxed

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 61 nodes

- **Size**: 61 nodes
- **Cohesion**: 0.2354
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| Schema | Class | flext-ldif/src/flext_ldif/servers/relaxed.py | 61-397 |
| _enhance_schema_item_metadata | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 64-86 |
| can_handle_attribute | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 89-95 |
| can_handle_objectclass | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 98-104 |
| _enhance_objectclass_metadata | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 106-116 |
| _extract_must_may_from_objectclass | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 118-152 |
| _extract_oid_with_fallback_patterns | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 154-184 |
| _extract_sup_from_objectclass | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 186-206 |
| _parse_attribute | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 209-233 |
| _parse_relaxed_attribute | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 235-279 |
| _parse_objectclass | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 282-299 |
| _parse_objectclass_relaxed | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 301-343 |
| _write_attribute | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 346-368 |
| _write_objectclass | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 371-397 |
| Acl | Class | flext-ldif/src/flext_ldif/servers/relaxed.py | 399-512 |
| can_handle | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 403-407 |
| can_handle_acl | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 410-413 |
| can_handle_attribute | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 416-419 |
| can_handle_objectclass | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 422-425 |
| _parse_acl | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 428-436 |
| _parse_relaxed_acl | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 438-447 |
| _with_relaxed_acl_metadata | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 449-473 |
| _build_relaxed_acl | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 475-497 |
| _write_acl | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 500-512 |
| Entry | Class | flext-ldif/src/flext_ldif/servers/relaxed.py | 514-774 |
| can_handle | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 518-524 |
| can_handle_attribute | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 527-530 |
| can_handle_objectclass | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 533-536 |
| normalize_dn | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 538-551 |
| process_entry | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 553-555 |
| _adapted_parse_entry_relaxed | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 557-585 |
| _parse_content | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 588-606 |
| _parse_relaxed_content | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 608-637 |
| _prepare_relaxed_raw_entry | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 640-651 |
| _parse_entry | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 653-663 |
| _parse_relaxed_entry | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 665-688 |
| _decode_relaxed_attributes | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 691-709 |
| _build_relaxed_entry_metadata | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 712-735 |
| _write_entry | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 738-750 |
| _write_relaxed_entry | Function | flext-ldif/src/flext_ldif/servers/relaxed.py | 753-774 |
| TestsFlextLdifRelaxed | Class | flext-ldif/tests/unit/servers/test_relaxed_servers.py | 22-375 |
| schema_server | Function | flext-ldif/tests/unit/servers/test_relaxed_servers.py | 33-35 |
| acl_server | Function | flext-ldif/tests/unit/servers/test_relaxed_servers.py | 38-40 |
| entry_server | Function | flext-ldif/tests/unit/servers/test_relaxed_servers.py | 43-45 |
| test_parse_attribute_scenarios | Test | flext-ldif/tests/unit/servers/test_relaxed_servers.py | 52-80 |
| test_parse_objectclass_scenarios | Test | flext-ldif/tests/unit/servers/test_relaxed_servers.py | 87-99 |
| test_parse_attribute_stores_original_definition | Test | flext-ldif/tests/unit/servers/test_relaxed_servers.py | 101-108 |
| test_write_attribute_to_rfc | Test | flext-ldif/tests/unit/servers/test_relaxed_servers.py | 110-133 |
| test_parse_acl_scenarios | Test | flext-ldif/tests/unit/servers/test_relaxed_servers.py | 140-151 |
| test_write_acl_preserves_raw_content | Test | flext-ldif/tests/unit/servers/test_relaxed_servers.py | 153-167 |

*... and 11 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `strip` (30 edge(s))
- `ok` (24 edge(s))
- `that` (24 edge(s))
- `fail` (17 edge(s))
- `group` (17 edge(s))
- `model_validate` (13 edge(s))
- `debug` (10 edge(s))
- `get` (10 edge(s))
- `super` (8 edge(s))
- `search` (8 edge(s))
- `split` (6 edge(s))
- `isinstance` (5 edge(s))
- `append` (5 edge(s))
- `flext-ldif/src/flext_ldif/servers/relaxed.py::FlextLdifServersRelaxed.Acl._get_server_type` (4 edge(s))
- `flext-ldif/src/flext_ldif/servers/relaxed.py::FlextLdifServersRelaxed.Schema._get_server_type` (4 edge(s))

### Incoming

- `that` (24 edge(s))
- `ok` (7 edge(s))
- `get` (5 edge(s))
- `parse_attribute` (4 edge(s))
- `flext-ldif/src/flext_ldif/servers/relaxed.py` (3 edge(s))
- `parse_input` (3 edge(s))
- `parse_objectclass` (3 edge(s))
- `SchemaAttribute` (2 edge(s))
- `write_attribute` (2 edge(s))
- `flext-ldif/tests/unit/servers/test_relaxed_servers.py` (1 edge(s))
- `SchemaObjectClass` (1 edge(s))
- `write_objectclass` (1 edge(s))
- `can_handle` (1 edge(s))
- `can_handle_attribute` (1 edge(s))
- `can_handle_objectclass` (1 edge(s))
