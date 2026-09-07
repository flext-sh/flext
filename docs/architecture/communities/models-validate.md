# models-validate


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 75 nodes

- **Size**: 75 nodes
- **Cohesion**: 0.3223
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| Attributes | Class | flext-ldif/src/flext_ldif/_models/domain_attributes.py | 24-168 |
| __getitem__ | Function | flext-ldif/src/flext_ldif/_models/domain_attributes.py | 48-61 |
| __setitem__ | Function | flext-ldif/src/flext_ldif/_models/domain_attributes.py | 63-71 |
| __len__ | Function | flext-ldif/src/flext_ldif/_models/domain_attributes.py | 73-75 |
| __contains__ | Function | flext-ldif/src/flext_ldif/_models/domain_attributes.py | 77-79 |
| add_attribute | Function | flext-ldif/src/flext_ldif/_models/domain_attributes.py | 81-93 |
| get | Function | flext-ldif/src/flext_ldif/_models/domain_attributes.py | 95-113 |
| has_attribute | Function | flext-ldif/src/flext_ldif/_models/domain_attributes.py | 115-125 |
| items | Function | flext-ldif/src/flext_ldif/_models/domain_attributes.py | 127-134 |
| iter_attributes | Function | flext-ldif/src/flext_ldif/_models/domain_attributes.py | 136-143 |
| keys | Function | flext-ldif/src/flext_ldif/_models/domain_attributes.py | 145-148 |
| remove_attribute | Function | flext-ldif/src/flext_ldif/_models/domain_attributes.py | 150-161 |
| values | Function | flext-ldif/src/flext_ldif/_models/domain_attributes.py | 163-168 |
| DN | Class | flext-ldif/src/flext_ldif/_models/domain_dn.py | 119-186 |
| _validate_dn_components | Function | flext-ldif/src/flext_ldif/_models/domain_dn.py | 145-167 |
| __str__ | Function | flext-ldif/src/flext_ldif/_models/domain_dn.py | 170-172 |
| from_value | Function | flext-ldif/src/flext_ldif/_models/domain_dn.py | 175-181 |
| empty | Function | flext-ldif/src/flext_ldif/_models/domain_dn.py | 184-186 |
| Entry | Class | flext-ldif/src/flext_ldif/_models/domain_entry.py | 306-1010 |
| coerce_attributes_from_dict | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 378-396 |
| coerce_dn_from_string | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 400-415 |
| coerce_record_kind | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 419-421 |
| coerce_changetype | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 432-436 |
| attributes_dict | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 471-478 |
| dn_str | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 482-489 |
| is_change_record | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 493-495 |
| unconverted_attributes | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 499-506 |
| ensure_metadata_initialized | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 510-556 |
| model_post_init | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 559-569 |
| normalize_record_kind | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 572-584 |
| validate_entry_consistency | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 587-600 |
| validate_entry_rfc_compliance | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 603-662 |
| validate_server_specific_rules | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 665-707 |
| _empty_validation_results | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 710-722 |
| _build_rfc_validation_context | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 725-739 |
| has_validation_errors | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 743-754 |
| is_acl_entry | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 758-767 |
| is_schema_entry | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 771-783 |
| _build_extension_kwargs | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 786-801 |
| _build_metadata | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 804-829 |
| _normalize_attributes | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 832-862 |
| _update_existing_metadata | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 865-880 |
| create | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 883-941 |
| _build_entry_data | Function | flext-ldif/src/flext_ldif/_models/domain_entry.py | 944-1010 |
| FlextLdifUtilitiesEntry | Class | flext-ldif/src/flext_ldif/_utilities/entry.py | 12-798 |
| get_attribute_values | Function | flext-ldif/src/flext_ldif/_utilities/entry.py | 20-42 |
| get_dn_components | Function | flext-ldif/src/flext_ldif/_utilities/entry.py | 45-54 |
| get_objectclass_names | Function | flext-ldif/src/flext_ldif/_utilities/entry.py | 57-61 |
| has_attribute | Function | flext-ldif/src/flext_ldif/_utilities/entry.py | 64-75 |
| has_object_class | Function | flext-ldif/src/flext_ldif/_utilities/entry.py | 78-91 |

*... and 25 more members.*

## Execution Flows

- **validate_entry_rfc_compliance** (criticality: 0.66, depth: 1)

## Dependencies

### Outgoing

- `lower` (28 edge(s))
- `append` (24 edge(s))
- `isinstance` (18 edge(s))
- `any` (13 edge(s))
- `extend` (12 edge(s))
- `strip` (11 edge(s))
- `model_validate` (11 edge(s))
- `str` (10 edge(s))
- `split` (9 edge(s))
- `bool` (8 edge(s))
- `len` (7 edge(s))
- `list` (7 edge(s))
- `match` (6 edge(s))
- `items` (6 edge(s))
- `dict` (5 edge(s))

### Incoming

- `flext-ldif/src/flext_ldif/_models/domain_attributes.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/_models/domain_dn.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/_models/domain_entry.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/_utilities/entry.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/utilities.py` (1 edge(s))
