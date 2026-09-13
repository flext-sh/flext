# servers-acl

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 94 nodes

- **Size**: 94 nodes
- **Cohesion**: 0.2565
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
| ------ | ------ | ------ | ------- |
| test_oid_acl_rule_models_carry_typed_subjects | Test | flext-ldif/tests/unit/test_collections_models.py | 122-142 |
| test_aci_rule_models_carry_typed_allows | Test | flext-ldif/tests/unit/test_collections_models.py | 144-163 |
| TestsFlextLdifOidAclConvertOud | Class | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 19-207 |
| _subject | Function | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 23-24 |
| _rule | Function | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 27-37 |
| test_subject_maps_to_expected_bind_rule | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 53-64 |
| test_converted_subject_leaves_permissions_empty | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 66-69 |
| test_subject_without_oud_equivalent_surfaces_failure | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 75-83 |
| test_convert_permissions_yields_ordered_allow_set | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 101-109 |
| test_convert_permissions_unknown_token_surfaces_failure | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 115-121 |
| test_get_targetattr | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 135-144 |
| test_scope_orclaci_without_anyone_is_default | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 148-154 |
| test_scope_orclaci_with_anyone_is_base | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 156-162 |
| test_scope_orclentrylevelaci_is_always_base | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 164-170 |
| test_regex_to_wildcard | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 184-185 |
| test_is_in_scope | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 198-199 |
| test_high_level_containers_are_base_relative_and_case_folded | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert_oud.py | 203-207 |
| TestsFlextLdifOidAclConvert | Class | flext-ldif/tests/unit/servers/test_oid_acl_convert.py | 27-199 |
| test_entry_rule_exposes_ordered_typed_subjects | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert.py | 34-53 |
| test_rule_preserves_raw_line_for_round_trip | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert.py | 55-60 |
| test_target_clause_shapes_map_to_public_target_fields | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert.py | 74-83 |
| test_filter_clause_is_extracted_via_balanced_paren_scan | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert.py | 85-96 |
| test_orclentrylevelaci_line_records_its_acl_type | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert.py | 98-105 |
| test_malformed_line_fails_with_descriptive_error | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert.py | 124-132 |
| test_subject_clause_maps_to_typed_subject | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert.py | 162-173 |
| test_constraint_modifier_populates_added_object_constraint | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert.py | 175-182 |
| test_unrecognized_subject_yields_unknown_type | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert.py | 184-189 |
| test_subject_matcher_catalog_returns_typed_non_empty_catalog | Test | flext-ldif/tests/unit/servers/test_oid_acl_convert.py | 195-199 |
| TestsFlextLdifOidAclAssemble | Class | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 27-477 |
| _build | Function | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 33-37 |
| test_render_aci_string_matches_oud_oracle | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 162-165 |
| test_group_with_deny_fallback_keeps_group_drops_anyone | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 169-181 |
| test_anyone_attr_rule_pins_targetscope_base | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 183-192 |
| test_deny_only_rule_yields_empty_allows_with_notes | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 194-201 |
| test_guidattr_dropped_with_note_other_subject_survives | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 203-212 |
| test_two_perm_groups_append_plus_count_to_acl_name | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 214-222 |
| test_unknown_permission_token_surfaces_failure | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 224-230 |
| test_cross_level_perm_grants_nothing_not_failure | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 232-241 |
| test_anyone_with_sensitive_perms_emits_review_note | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 243-252 |
| test_anyone_with_only_read_search_emits_no_sensitive_note | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 254-261 |
| test_bindmode_and_bindipfilter_become_authmethod_and_ip | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 263-282 |
| test_added_object_constraint_emits_review_note | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 284-293 |
| test_anyone_at_high_level_container_is_skipped | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 295-304 |
| test_out_of_scope_dn_is_excluded | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 306-314 |
| test_regex_dn_converts_to_wildcard_in_scope | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 316-324 |
| test_no_base_dn_skips_scope_filtering | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 326-333 |
| test_multiple_lines_produce_aci_values_without_prefix | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 337-349 |
| test_identical_aci_values_are_deduplicated | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 351-355 |
| test_deny_only_line_emits_no_value | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 357-363 |
| test_malformed_line_surfaces_failure | Test | flext-ldif/tests/unit/servers/test_oid_acl_assemble.py | 365-371 |

*... and 44 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (114 edge(s))
- `unwrap` (29 edge(s))
- `len` (17 edge(s))
- `ok` (15 edge(s))
- `fail` (13 edge(s))
- `strip` (13 edge(s))
- `tuple` (12 edge(s))
- `append` (12 edge(s))
- `startswith` (10 edge(s))
- `lower` (9 edge(s))
- `any` (9 edge(s))
- `m.FrozenModel` (8 edge(s))
- `set` (7 edge(s))
- `flext-cli/examples/protocols.py::ExamplesFlextCliProtocols.CliMainWithGroups.group` (7 edge(s))
- `replace` (4 edge(s))

### Incoming

- `that` (114 edge(s))
- `unwrap` (27 edge(s))
- `parse_oid_acl_line` (16 edge(s))
- `flext-ldif/tests/unit/servers/test_oid_acl_assemble.py` (14 edge(s))
- `len` (12 edge(s))
- `build_aci_rule` (10 edge(s))
- `flext-ldif/src/flext_ldif/_models/acl_convert.py` (9 edge(s))
- `any` (9 edge(s))
- `convert_acl_values` (8 edge(s))
- `ok` (5 edge(s))
- `startswith` (4 edge(s))
- `parse_subject` (3 edge(s))
- `convert_subject_to_oud` (3 edge(s))
- `calculate_targetscope` (3 edge(s))
- `render_aci_string` (2 edge(s))
