# utilities-dn

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 89 nodes

- **Size**: 89 nodes
- **Cohesion**: 0.2722
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextLdifUtilitiesNormalizeDnTransformer | Class | flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py | 12-92 |
| **init** | Function | flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py | 19-30 |
| validate_dn_components | Function | flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py | 33-47 |
| apply | Function | flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py | 50-82 |
| validate_dn | Function | flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py | 60-68 |
| update_entry | Function | flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py | 70-78 |
| _normalize_dn_case_and_spaces | Function | flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py | 84-92 |
| FlextLdifUtilitiesCollectionLdif | Class | flext-ldif/src/flext_ldif/_utilities/collection_ldif.py | 13-72 |
| find | Function | flext-ldif/src/flext_ldif/_utilities/collection_ldif.py | 17-24 |
| normalize_ldif | Function | flext-ldif/src/flext_ldif/_utilities/collection_ldif.py | 27-70 |
| normalize_single | Function | flext-ldif/src/flext_ldif/_utilities/collection_ldif.py | 45-53 |
| FlextLdifUtilitiesDispatch | Class | flext-ldif/src/flext_ldif/_utilities/dispatch.py | 17-191 |
| as_entry | Function | flext-ldif/src/flext_ldif/_utilities/dispatch.py | 28-31 |
| as_entries | Function | flext-ldif/src/flext_ldif/_utilities/dispatch.py | 34-43 |
| as_acl | Function | flext-ldif/src/flext_ldif/_utilities/dispatch.py | 46-49 |
| as_acls | Function | flext-ldif/src/flext_ldif/_utilities/dispatch.py | 52-59 |
| parse | Function | flext-ldif/src/flext_ldif/_utilities/dispatch.py | 79-106 |
| validate | Function | flext-ldif/src/flext_ldif/_utilities/dispatch.py | 109-154 |
| _validate_entries | Function | flext-ldif/src/flext_ldif/_utilities/dispatch.py | 157-166 |
| _is_entry_sequence | Function | flext-ldif/src/flext_ldif/_utilities/dispatch.py | 169-182 |
| find | Function | flext-ldif/src/flext_ldif/_utilities/dispatch.py | 187-191 |
| FlextLdifUtilitiesDN | Class | flext-ldif/src/flext_ldif/_utilities/dn.py | 16-1002 |
| _advance_rdn_position | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 85-91 |
| _apply_dn_transformations | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 94-181 |
| _has_double_unescaped_commas | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 184-195 |
| _normalize_dns_for_comparison | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 198-210 |
| _process_rdn_char | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 213-245 |
| _process_rdn_escape | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 248-257 |
| _validate_basic_format | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 260-262 |
| _validate_components | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 265-276 |
| is_valid_component | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 268-273 |
| _validate_dn_structure | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 279-295 |
| _validate_escape_sequences | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 298-336 |
| clean_dn | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 347-368 |
| clean_dn_with_statistics | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 371-429 |
| compare_dns | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 432-437 |
| _compare_dns_core | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 440-453 |
| esc | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 456-489 |
| escape_char | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 476-485 |
| get_dn_value | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 492-496 |
| is_lutf1_char | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 499-509 |
| is_sutf1_char | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 512-522 |
| is_tutf1_char | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 525-535 |
| is_under_base | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 538-548 |
| is_valid_dn_string | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 551-582 |
| norm | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 593-622 |
| norm_or_fallback | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 625-670 |
| parse_dn | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 681-702 |
| parse_rdn | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 705-717 |
| _parse_dn_components | Function | flext-ldif/src/flext_ldif/_utilities/dn.py | 720-734 |

*... and 39 more members.*

## Execution Flows

- **validate** (criticality: 0.75, depth: 3)

## Dependencies

### Outgoing

- `len` (24 edge(s))
- `that` (24 edge(s))
- `fail` (23 edge(s))
- `append` (20 edge(s))
- `ok` (16 edge(s))
- `strip` (15 edge(s))
- `isinstance` (13 edge(s))
- `lower` (11 edge(s))
- `bool` (10 edge(s))
- `get` (10 edge(s))
- `sub_pattern` (5 edge(s))
- `ord` (5 edge(s))
- `compare_dns` (5 edge(s))
- `str` (4 edge(s))
- `model_copy` (4 edge(s))

### Incoming

- `that` (24 edge(s))
- `flext-ldif/tests/unit/utilities/test_utilities_core.py::TestsFlextLdifUtilitiesCore` (9 edge(s))
- `flext-ldif/tests/unit/utilities/test_utilities_comprehensive.py::TestsFlextLdifUtilitiesComprehensive` (8 edge(s))
- `compare_dns` (5 edge(s))
- `flext-ldif/src/flext_ldif/utilities.py` (4 edge(s))
- `clean_dn` (4 edge(s))
- `esc` (4 edge(s))
- `ok` (4 edge(s))
- `unesc` (3 edge(s))
- `flext-ldif/src/flext_ldif/_utilities/pipeline.py` (2 edge(s))
- `norm` (2 edge(s))
- `parse_dn` (2 edge(s))
- `flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/_utilities/collection_ldif.py` (1 edge(s))
- `flext-ldif/src/flext_ldif/_utilities/dispatch.py` (1 edge(s))
