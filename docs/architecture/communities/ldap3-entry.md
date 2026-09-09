# ldap3-entry

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 91 nodes

- **Size**: 91 nodes
- **Cohesion**: 0.4134
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| ConnectionManager | Class | flext-ldap/src/flext_ldap/adapters/_ldap3/connection_manager.py | 16-129 |
| create_connection | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/connection_manager.py | 20-56 |
| create_server | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/connection_manager.py | 59-89 |
| handle_tls | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/connection_manager.py | 92-129 |
| OperationExecutor | Class | flext-ldap/src/flext_ldap/adapters/_ldap3/operation_executor.py | 19-120 |
| _execute | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/operation_executor.py | 46-64 |
| _extract_error_result | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/operation_executor.py | 67-78 |
| execute_add | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/operation_executor.py | 81-94 |
| execute_delete | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/operation_executor.py | 97-106 |
| execute_modify | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/operation_executor.py | 109-120 |
| ResultConverter | Class | flext-ldap/src/flext_ldap/adapters/_ldap3/result_converter.py | 17-77 |
| convert_ldap3_results | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/result_converter.py | 32-48 |
| convert_parsed_entries | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/result_converter.py | 51-77 |
| ResultConverterExtractMixin | Class | flext-ldap/src/flext_ldap/adapters/_ldap3/result_extract.py | 16-151 |
| extract_dn | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/result_extract.py | 20-38 |
| extract_attributes | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/result_extract.py | 41-57 |
| extract_attrs_dict | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/result_extract.py | 60-80 |
| extract_metadata | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/result_extract.py | 83-115 |
| _normalize_attr_values | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/result_extract.py | 118-138 |
| _normalize_metadata | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/result_extract.py | 141-151 |
| SearchExecutor | Class | flext-ldap/src/flext_ldap/adapters/_ldap3/search_executor.py | 15-71 |
| execute | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/search_executor.py | 24-71 |
| FlextLdapLdap3Wrappers | Class | flext-ldap/src/flext_ldap/adapters/_ldap3/wrappers.py | 17-126 |
| value_to_str_list | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/wrappers.py | 21-25 |
| _ldap3_method | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/wrappers.py | 28-37 |
| add | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/wrappers.py | 40-51 |
| delete | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/wrappers.py | 54-57 |
| is_bound | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/wrappers.py | 60-63 |
| modify | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/wrappers.py | 66-71 |
| search | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/wrappers.py | 74-110 |
| start_tls | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/wrappers.py | 113-120 |
| unbind | Function | flext-ldap/src/flext_ldap/adapters/_ldap3/wrappers.py | 123-126 |
| FlextLdapEntryAdapter | Class | flext-ldap/src/flext_ldap/adapters/entry.py | 38-339 |
| _ConversionHelpers | Class | flext-ldap/src/flext_ldap/adapters/entry.py | 52-81 |
| convert_value_to_strings | Function | flext-ldap/src/flext_ldap/adapters/entry.py | 62-65 |
| is_base64_encoded | Function | flext-ldap/src/flext_ldap/adapters/entry.py | 68-73 |
| normalize_original_attr_value | Function | flext-ldap/src/flext_ldap/adapters/entry.py | 76-81 |
| **init** | Function | flext-ldap/src/flext_ldap/adapters/entry.py | 85-93 |
| _build_conversion_metadata | Function | flext-ldap/src/flext_ldap/adapters/entry.py | 96-105 |
| _track_conversion_differences | Function | flext-ldap/src/flext_ldap/adapters/entry.py | 108-122 |
| execute | Function | flext-ldap/src/flext_ldap/adapters/entry.py | 125-149 |
| ldap3_to_ldif_entry | Function | flext-ldap/src/flext_ldap/adapters/entry.py | 151-197 |
| _build_ldif_entry_from_ldap3 | Function | flext-ldap/src/flext_ldap/adapters/entry.py | 199-227 |
| ldif_entry_to_ldap3_attributes | Function | flext-ldap/src/flext_ldap/adapters/entry.py | 229-288 |
| _convert_ldap3_value_to_list | Function | flext-ldap/src/flext_ldap/adapters/entry.py | 290-339 |
| FlextLdapLdap3Adapter | Class | flext-ldap/src/flext_ldap/adapters/ldap3.py | 30-203 |
| _is_bound | Function | flext-ldap/src/flext_ldap/adapters/ldap3.py | 41-44 |
| **init** | Function | flext-ldap/src/flext_ldap/adapters/ldap3.py | 55-59 |
| connection | Function | flext-ldap/src/flext_ldap/adapters/ldap3.py | 62-64 |
| is_connected | Function | flext-ldap/src/flext_ldap/adapters/ldap3.py | 67-71 |

*... and 41 more members.*

## Execution Flows

- **connect** (criticality: 0.70, depth: 2)
- **execute** (criticality: 0.58, depth: 2)

## Dependencies

### Outgoing

- `ok` (20 edge(s))
- `isinstance` (17 edge(s))
- `that` (17 edge(s))
- `fail` (14 edge(s))
- `list` (10 edge(s))
- `getattr` (10 edge(s))
- `items` (8 edge(s))
- `append` (6 edge(s))
- `str` (6 edge(s))
- `flat_map` (6 edge(s))
- `empty` (5 edge(s))
- `not_none` (5 edge(s))
- `fail_operation` (4 edge(s))
- `Attributes` (4 edge(s))
- `get` (4 edge(s))

### Incoming

- `that` (17 edge(s))
- `ok` (8 edge(s))
- `fail` (6 edge(s))
- `not_none` (5 edge(s))
- `flext-ldap/tests/unit/test_entry_adapter.py` (3 edge(s))
- `list` (3 edge(s))
- `flext-ldap/src/flext_ldap/adapters/_ldap3/result_converter.py` (2 edge(s))
- `flext-ldap/src/flext_ldap/adapters/entry.py` (2 edge(s))
- `flext-ldap/src/flext_ldap/adapters/ldap3.py` (2 edge(s))
- `getattr` (2 edge(s))
- `flext-ldap/src/flext_ldap/adapters/_ldap3/connection_manager.py` (1 edge(s))
- `flext-ldap/src/flext_ldap/adapters/_ldap3/operation_executor.py` (1 edge(s))
- `flext-ldap/src/flext_ldap/adapters/_ldap3/result_extract.py` (1 edge(s))
- `flext-ldap/src/flext_ldap/adapters/_ldap3/search_executor.py` (1 edge(s))
- `flext-ldap/src/flext_ldap/adapters/_ldap3/wrappers.py` (1 edge(s))
