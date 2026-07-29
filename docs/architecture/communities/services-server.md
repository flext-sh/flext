# services-server

## Overview

Community of 41 nodes

- **Size**: 41 nodes
- **Cohesion**: 0.2714
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
| ------ | ------ | ------ | ------- |
| TestsFlextLdifCrossDirectionConversion | Class | flext-ldif/tests/integration/test_cross_direction_conversion.py | 23-327 |
| server_registry | Function | flext-ldif/tests/integration/test_cross_direction_conversion.py | 27-29 |
| test_attribute_definition_conversion_normalizes_output | Test | flext-ldif/tests/integration/test_cross_direction_conversion.py | 83-108 |
| test_objectclass_definition_conversion_normalizes_output | Test | flext-ldif/tests/integration/test_cross_direction_conversion.py | 145-170 |
| test_oid_attribute_roundtrip_is_text_identical | Test | flext-ldif/tests/integration/test_cross_direction_conversion.py | 172-188 |
| test_parsed_attribute_field_is_canonicalized | Test | flext-ldif/tests/integration/test_cross_direction_conversion.py | 215-228 |
| test_oid_case_variant_matching_rule_normalizes_through_pipeline | Test | flext-ldif/tests/integration/test_cross_direction_conversion.py | 230-249 |
| test_oid_to_oud_entry_rewrites_embedded_schema_values | Test | flext-ldif/tests/integration/test_cross_direction_conversion.py | 254-294 |
| test_oud_to_oid_entry_preserves_generic_matching_rule | Test | flext-ldif/tests/integration/test_cross_direction_conversion.py | 296-327 |
| server | Function | flext-ldif/tests/integration/test_rfc_docker_real_integration.py | 27-29 |
| server_registry | Function | flext-ldif/tests/integration/test_rfc_docker_real.py | 37-39 |
| server | Function | flext-ldif/tests/unit/fixtures.py | 142-145 |
| oid_server | Function | flext-ldif/tests/unit/fixtures.py | 149-155 |
| TestsFlextLdifOidServers | Class | flext-ldif/tests/unit/servers/test_oid_servers.py | 18-209 |
| schema | Function | flext-ldif/tests/unit/servers/test_oid_servers.py | 22-26 |
| test_resolve_unknown_server_type_returns_none | Test | flext-ldif/tests/unit/servers/test_oid_servers.py | 28-30 |
| test_parse_attribute_normalizes_syntax_oid | Test | flext-ldif/tests/unit/servers/test_oid_servers.py | 49-58 |
| test_parse_attribute_normalizes_equality_matching_rule | Test | flext-ldif/tests/unit/servers/test_oid_servers.py | 80-94 |
| test_parse_attribute_derives_substr_from_substrings_rule | Test | flext-ldif/tests/unit/servers/test_oid_servers.py | 96-111 |
| test_parse_attribute_exposes_public_identity_fields | Test | flext-ldif/tests/unit/servers/test_oid_servers.py | 113-125 |
| test_parse_attribute_without_oid_fails_with_error_message | Test | flext-ldif/tests/unit/servers/test_oid_servers.py | 127-135 |
| test_parse_objectclass_normalizes_superior | Test | flext-ldif/tests/unit/servers/test_oid_servers.py | 154-163 |
| test_parse_objectclass_normalizes_auxiliary_typo | Test | flext-ldif/tests/unit/servers/test_oid_servers.py | 165-176 |
| test_write_attribute_round_trip_preserves_matching_rule_text | Test | flext-ldif/tests/unit/servers/test_oid_servers.py | 178-192 |
| test_write_objectclass_round_trip_preserves_identity | Test | flext-ldif/tests/unit/servers/test_oid_servers.py | 194-209 |
| FlextLdifServer | Class | flext-ldif/src/flext_ldif/services/server.py | 16-226 |
| model_post_init | Function | flext-ldif/src/flext_ldif/services/server.py | 35-41 |
| acl | Function | flext-ldif/src/flext_ldif/services/server.py | 43-49 |
| entry | Function | flext-ldif/src/flext_ldif/services/server.py | 51-57 |
| resolve_server_bundle | Function | flext-ldif/src/flext_ldif/services/server.py | 59-90 |
| resolve_base_server | Function | flext-ldif/src/flext_ldif/services/server.py | 92-94 |
| resolve_server_constants | Function | flext-ldif/src/flext_ldif/services/server.py | 96-116 |
| summarize_registry | Function | flext-ldif/src/flext_ldif/services/server.py | 118-142 |
| schema_server | Function | flext-ldif/src/flext_ldif/services/server.py | 144-146 |
| resolve_schema_server | Function | flext-ldif/src/flext_ldif/services/server.py | 148-157 |
| list_registered_servers | Function | flext-ldif/src/flext_ldif/services/server.py | 159-161 |
| server | Function | flext-ldif/src/flext_ldif/services/server.py | 164-173 |
| _auto_discover | Function | flext-ldif/src/flext_ldif/services/server.py | 175-183 |
| _is_discoverable_server | Function | flext-ldif/src/flext_ldif/services/server.py | 186-196 |
| _register_discovered_server | Function | flext-ldif/src/flext_ldif/services/server.py | 198-219 |
| fetch_global_instance | Function | flext-ldif/src/flext_ldif/services/server.py | 222-226 |

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `resolve_schema_server` (10 edge(s))
- `parse_attribute` (10 edge(s))
- `unwrap` (10 edge(s))
- `type` (7 edge(s))
- `getattr` (4 edge(s))
- `fail` (4 edge(s))
- `write_attribute` (4 edge(s))
- `parse_objectclass` (4 edge(s))
- `isinstance` (3 edge(s))
- `ok` (3 edge(s))
- `str` (3 edge(s))
- `write_objectclass` (2 edge(s))
- `model_validate` (2 edge(s))
- `convert_model` (2 edge(s))
- `s` (1 edge(s))

### Incoming

- `parse_attribute` (10 edge(s))
- `unwrap` (10 edge(s))
- `resolve_schema_server` (9 edge(s))
- `write_attribute` (4 edge(s))
- `parse_objectclass` (4 edge(s))
- `write_objectclass` (2 edge(s))
- `model_validate` (2 edge(s))
- `convert_model` (2 edge(s))
- `isinstance` (2 edge(s))
- `str` (2 edge(s))
- `flext-ldif/tests/unit/fixtures.py` (2 edge(s))
- `flext-ldif/src/flext_ldif/services/server.py` (1 edge(s))
- `flext-ldif/tests/integration/test_cross_direction_conversion.py` (1 edge(s))
- `getattr` (1 edge(s))
- `flext-ldif/tests/integration/test_rfc_docker_real.py::TestsFlextLdifRfcDockerReal` (1 edge(s))
