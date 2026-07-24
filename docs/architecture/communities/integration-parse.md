# integration-parse

## Overview

Community of 314 nodes

- **Size**: 314 nodes
- **Cohesion**: 0.2870
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FileLock | Class | flext-tests/src/flext_tests/_utilities/testcontext.py | 16-47 |
| **init** | Function | flext-tests/src/flext_tests/_utilities/testcontext.py | 24-27 |
| **exit** | Function | flext-tests/src/flext_tests/_utilities/testcontext.py | 36-47 |
| build_tests_validator_items | Function | flext-tests/src/flext_tests/_fixtures/_enforcement_parts/validators.py | 63-78 |
| _items_from_grouped | Function | flext-tests/src/flext_tests/_fixtures/_enforcement_parts/validators.py | 81-100 |
| _collect_tests_validator_violations | Function | flext-tests/src/flext_tests/_fixtures/_enforcement_parts/validators.py | 103-137 |
| _validator_dispatch_target | Function | flext-tests/src/flext_tests/_fixtures/_enforcement_parts/validators.py | 140-149 |
| _merge_tests_validator_result | Function | flext-tests/src/flext_tests/_fixtures/_enforcement_parts/validators.py | 152-174 |
| _violation_project | Function | flext-tests/src/flext_tests/_fixtures/_enforcement_parts/validators.py | 177-190 |
| method | Function | flext-observability/src/flext_observability/protocols.py | 438-440 |
| parse_input | Function | flext-ldif/tests/protocols.py | 37-44 |
| parse_server | Function | flext-ldif/tests/protocols.py | 83-88 |
| write | Function | flext-ldif/tests/protocols.py | 94-99 |
| Tests | Class | flext-ldif/tests/utilities.py | 26-512 |
| create_server_from_url | Function | flext-ldif/tests/utilities.py | 43-52 |
| create_bare_server | Function | flext-ldif/tests/utilities.py | 55-66 |
| create_connection | Function | flext-ldif/tests/utilities.py | 69-91 |
| parametrize_real_data | Function | flext-ldif/tests/utilities.py | 147-160 |
| fixture_metadata | Function | flext-ldif/tests/utilities.py | 163-184 |
| get_docker_control | Function | flext-ldif/tests/utilities.py | 187-211 |
| get_admin_credentials | Function | flext-ldif/tests/utilities.py | 214-241 |
| _probe_admin_credentials | Function | flext-ldif/tests/utilities.py | 244-273 |
| _assert_field_eq | Function | flext-ldif/tests/utilities.py | 276-291 |
| assert_server_schema_parse_and_properties | Function | flext-ldif/tests/utilities.py | 294-361 |
| server_parse_and_unwrap | Function | flext-ldif/tests/utilities.py | 370-410 |
| acl_parse_and_unwrap | Function | flext-ldif/tests/utilities.py | 413-438 |
| _assert_must_contain | Function | flext-ldif/tests/utilities.py | 441-447 |
| server_write_and_unwrap | Function | flext-ldif/tests/utilities.py | 450-494 |
| acl_write_and_unwrap | Function | flext-ldif/tests/utilities.py | 497-512 |
| _Frozen | Class | flext-ldif/tests/models.py | 22-25 |
| _CanHandleCase | Class | flext-ldif/tests/models.py | 27-34 |
| _SchemaCase | Class | flext-ldif/tests/models.py | 36-46 |
| LdifTestData | Class | flext-ldif/tests/models.py | 48-66 |
| FixtureMetadata | Class | flext-ldif/tests/models.py | 68-91 |
| AttributeTestCase | Class | flext-ldif/tests/models.py | 93-96 |
| ObjectClassTestCase | Class | flext-ldif/tests/models.py | 98-105 |
| EntryTestCase | Class | flext-ldif/tests/models.py | 107-114 |
| ProtocolServer | Class | flext-ldif/tests/models.py | 116-125 |
| AclTestCase | Class | flext-ldif/tests/models.py | 127-139 |
| _probe_ldap_bind | Function | flext-ldif/tests/integration/fixtures.py | 21-42 |
| ldap_container | Function | flext-ldif/tests/integration/fixtures.py | 46-84 |
| make_test_username | Function | flext-ldif/tests/integration/fixtures.py | 99-105 |
| ldap_connection | Function | flext-ldif/tests/integration/fixtures.py | 119-147 |
| TestsFlextLdifAclMetadataPreservation | Class | flext-ldif/tests/integration/test_acl_metadata_preservation.py | 28-304 |
| api | Function | flext-ldif/tests/integration/test_acl_metadata_preservation.py | 32-34 |
| _extensions | Function | flext-ldif/tests/integration/test_acl_metadata_preservation.py | 37-46 |
| _parse_single | Function | flext-ldif/tests/integration/test_acl_metadata_preservation.py | 48-61 |
| test_oid_feature_preserved_in_extensions | Test | flext-ldif/tests/integration/test_acl_metadata_preservation.py | 100-115 |
| test_oid_all_features_preserved_together | Test | flext-ldif/tests/integration/test_acl_metadata_preservation.py | 117-138 |
| test_oud_feature_preserved_in_extensions | Test | flext-ldif/tests/integration/test_acl_metadata_preservation.py | 210-225 |

*... and 264 more members.*

## Execution Flows

- **validate_entry** (criticality: 0.82, depth: 7)
- **execute_command** (criticality: 0.76, depth: 15)

## Dependencies

### Outgoing

- `that` (94 edge(s))
- `parse_ldif` (78 edge(s))
- `len` (57 edge(s))
- `get` (43 edge(s))
- `isinstance` (43 edge(s))
- `unwrap` (37 edge(s))
- `assert_success` (27 edge(s))
- `str` (20 edge(s))
- `lower` (19 edge(s))
- `add` (17 edge(s))
- `ok` (15 edge(s))
- `search` (15 edge(s))
- `AssertionError` (15 edge(s))
- `fail` (13 edge(s))
- `parse_string` (13 edge(s))

### Incoming

- `that` (94 edge(s))
- `parse_ldif` (74 edge(s))
- `len` (51 edge(s))
- `write` (46 edge(s))
- `flext-ldif/tests/constants.py` (37 edge(s))
- `get` (36 edge(s))
- `isinstance` (28 edge(s))
- `unwrap` (27 edge(s))
- `assert_success` (25 edge(s))
- `FlextLdifServersApache` (20 edge(s))
- `make_test_username` (18 edge(s))
- `add` (15 edge(s))
- `ok` (14 edge(s))
- `lower` (13 edge(s))
- `parse_string` (12 edge(s))
