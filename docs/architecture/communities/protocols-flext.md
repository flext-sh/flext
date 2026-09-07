# protocols-flext


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 114 nodes

- **Size**: 114 nodes
- **Cohesion**: 0.3371
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| ConfigObject | Class | flext-core/src/flext_core/_protocols/base.py | 102-117 |
| get | Function | flext-core/src/flext_core/_protocols/base.py | 105-109 |
| keys | Function | flext-core/src/flext_core/_protocols/base.py | 111-113 |
| items | Function | flext-core/src/flext_core/_protocols/base.py | 115-117 |
| Result | Class | flext-core/src/flext_core/_protocols/result.py | 61-148 |
| error | Function | flext-core/src/flext_core/_protocols/result.py | 65-65 |
| error_code | Function | flext-core/src/flext_core/_protocols/result.py | 67-67 |
| error_data | Function | flext-core/src/flext_core/_protocols/result.py | 69-69 |
| success | Function | flext-core/src/flext_core/_protocols/result.py | 71-71 |
| exception | Function | flext-core/src/flext_core/_protocols/result.py | 73-73 |
| failure | Function | flext-core/src/flext_core/_protocols/result.py | 75-75 |
| value | Function | flext-core/src/flext_core/_protocols/result.py | 77-77 |
| __enter__ | Function | flext-core/src/flext_core/_protocols/result.py | 79-79 |
| __exit__ | Function | flext-core/src/flext_core/_protocols/result.py | 81-86 |
| __or__ | Function | flext-core/src/flext_core/_protocols/result.py | 88-88 |
| unwrap | Function | flext-core/src/flext_core/_protocols/result.py | 90-90 |
| unwrap_or | Function | flext-core/src/flext_core/_protocols/result.py | 91-91 |
| unwrap_or_else | Function | flext-core/src/flext_core/_protocols/result.py | 92-92 |
| flat_map | Function | flext-core/src/flext_core/_protocols/result.py | 94-96 |
| fold | Function | flext-core/src/flext_core/_protocols/result.py | 98-100 |
| lash | Function | flext-core/src/flext_core/_protocols/result.py | 102-104 |
| map | Function | flext-core/src/flext_core/_protocols/result.py | 106-108 |
| flow_through | Function | flext-core/src/flext_core/_protocols/result.py | 110-112 |
| map_error | Function | flext-core/src/flext_core/_protocols/result.py | 114-116 |
| map_or | Function | flext-core/src/flext_core/_protocols/result.py | 124-126 |
| tap | Function | flext-core/src/flext_core/_protocols/result.py | 128-130 |
| tap_error | Function | flext-core/src/flext_core/_protocols/result.py | 132-134 |
| filter | Function | flext-core/src/flext_core/_protocols/result.py | 136-138 |
| recover | Function | flext-core/src/flext_core/_protocols/result.py | 140-142 |
| to_model | Function | flext-core/src/flext_core/_protocols/result.py | 144-146 |
| __bool__ | Function | flext-core/src/flext_core/_protocols/result.py | 148-148 |
| _peer_first_allowed | Function | flext-core/src/flext_core/_utilities/_beartype/_class_visitor_parts/_parts/class_visitor_part_02_01.py | 15-33 |
| _requires_alias_first | Function | flext-core/src/flext_core/_utilities/_beartype/_class_visitor_parts/_parts/class_visitor_part_02_01.py | 36-53 |
| alias_first_violation | Function | flext-core/src/flext_core/_utilities/_beartype/_class_visitor_parts/_parts/class_visitor_part_02_01.py | 56-159 |
| FlextUtilitiesChecker | Class | flext-core/src/flext_core/_utilities/_checker_parts/checker_part_03.py | 27-138 |
| _extract_generic_message_types | Function | flext-core/src/flext_core/_utilities/_checker_parts/checker_part_03.py | 29-56 |
| _extract_message_type_from_handle | Function | flext-core/src/flext_core/_utilities/_checker_parts/checker_part_03.py | 59-81 |
| can_handle_message_type | Function | flext-core/src/flext_core/_utilities/_checker_parts/checker_part_03.py | 84-95 |
| compute_accepted_message_types | Function | flext-core/src/flext_core/_utilities/_checker_parts/checker_part_03.py | 98-109 |
| resolve_message_route | Function | flext-core/src/flext_core/_utilities/_checker_parts/checker_part_03.py | 112-138 |
| FlextUtilitiesEnforcementCollect | Class | flext-core/src/flext_core/_utilities/_enforcement_collect_parts/enforcement_collect_part_01.py | 30-226 |
| _owning_project_root | Function | flext-core/src/flext_core/_utilities/_enforcement_collect_parts/enforcement_collect_part_01.py | 34-58 |
| _resolve_target_source_file | Function | flext-core/src/flext_core/_utilities/_enforcement_collect_parts/enforcement_collect_part_01.py | 61-69 |
| _discover_src_package | Function | flext-core/src/flext_core/_utilities/_enforcement_collect_parts/enforcement_collect_part_01.py | 72-95 |
| _project | Function | flext-core/src/flext_core/_utilities/_enforcement_collect_parts/enforcement_collect_part_01.py | 98-127 |
| _iter_inner | Function | flext-core/src/flext_core/_utilities/_enforcement_collect_parts/enforcement_collect_part_01.py | 130-133 |
| _iter_effective | Function | flext-core/src/flext_core/_utilities/_enforcement_collect_parts/enforcement_collect_part_01.py | 136-148 |
| _field_items | Function | flext-core/src/flext_core/_utilities/_enforcement_collect_parts/enforcement_collect_part_01.py | 151-163 |
| _attr_filter | Function | flext-core/src/flext_core/_utilities/_enforcement_collect_parts/enforcement_collect_part_01.py | 166-182 |
| accept_utility | Function | flext-core/src/flext_core/_utilities/_enforcement_collect_parts/enforcement_collect_part_01.py | 172-174 |

*... and 64 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `getattr` (18 edge(s))
- `startswith` (14 edge(s))
- `split` (12 edge(s))
- `isinstance` (10 edge(s))
- `derive_class_stem` (8 edge(s))
- `lower` (7 edge(s))
- `attr_accept_constants` (7 edge(s))
- `endswith` (5 edge(s))
- `set` (4 edge(s))
- `vars` (4 edge(s))
- `tuple` (3 edge(s))
- `any` (3 edge(s))
- `fail` (3 edge(s))
- `extend` (3 edge(s))
- `RuntimeError` (3 edge(s))

### Incoming

- `flext-core/tests/unit/test_beartype_engine.py::TestsFlextCoreBeartypeEngine` (11 edge(s))
- `derive_class_stem` (8 edge(s))
- `attr_accept_constants` (7 edge(s))
- `flext-core/src/flext_core/_utilities/_beartype/_class_visitor_parts/_parts/class_visitor_part_02_01.py` (3 edge(s))
- `flext-core/tests/unit/test_models_project_metadata.py::TestsFlextModelsProjectMetadata` (3 edge(s))
- `flext-core/tests/unit/test_project_metadata_facade_access.py::TestsFlextFacadeFlatSsotAccess` (3 edge(s))
- `flext-core/src/flext_core/_utilities/beartype_engine.py` (2 edge(s))
- `defined_in_function_scope` (2 edge(s))
- `defined_inside` (2 edge(s))
- `contains_any` (2 edge(s))
- `flext-core/tests/unit/test_enforcement_namespace.py::TestsFlextCoreEnforcementNamespace` (2 edge(s))
- `catch_warnings` (2 edge(s))
- `simplefilter` (2 edge(s))
- `run_layer` (2 edge(s))
- `flext-core/tests/unit/test_utilities_project_metadata_read.py::TestsFlextUtilitiesProjectMetadataRead` (2 edge(s))
