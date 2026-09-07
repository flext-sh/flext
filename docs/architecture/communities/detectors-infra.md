# detectors-infra


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 302 nodes

- **Size**: 302 nodes
- **Cohesion**: 0.2328
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextInfraEnforcementMetadata | Class | flext-infra/src/flext_infra/_enforcement/metadata.py | 16-71 |
| detect_declarative | Function | flext-infra/src/flext_infra/_enforcement/metadata.py | 20-24 |
| violation_kind | Function | flext-infra/src/flext_infra/_enforcement/metadata.py | 27-39 |
| object_kind | Function | flext-infra/src/flext_infra/_enforcement/metadata.py | 42-44 |
| object_name | Function | flext-infra/src/flext_infra/_enforcement/metadata.py | 47-58 |
| description | Function | flext-infra/src/flext_infra/_enforcement/metadata.py | 61-71 |
| FlextInfraEnforcementSelection | Class | flext-infra/src/flext_infra/_enforcement/selection.py | 13-105 |
| canonical_catalog | Function | flext-infra/src/flext_infra/_enforcement/selection.py | 19-22 |
| selected_rules | Function | flext-infra/src/flext_infra/_enforcement/selection.py | 25-48 |
| declarative_rules | Function | flext-infra/src/flext_infra/_enforcement/selection.py | 51-61 |
| supports_declarative | Function | flext-infra/src/flext_infra/_enforcement/selection.py | 64-66 |
| rule_requires_stub_file | Function | flext-infra/src/flext_infra/_enforcement/selection.py | 69-76 |
| _validate_requested_rules | Function | flext-infra/src/flext_infra/_enforcement/selection.py | 79-105 |
| FlextInfraClassPlacementDetector | Class | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 17-369 |
| detect_file | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 21-110 |
| _governed_classes_with_family | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 113-125 |
| _violation_for_class | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 128-142 |
| _in_canonical_location | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 145-165 |
| _suggestion_for_family | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 168-176 |
| _target_facade | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 179-183 |
| _public_classes | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 186-206 |
| _class_body_nodes | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 209-220 |
| _class_constants | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 223-250 |
| _namespace_constant_name | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 253-265 |
| _constant_info | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 268-275 |
| _annassign_constant | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 278-295 |
| _assign_constant | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 298-311 |
| _type_aliases | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 314-340 |
| _annotation_contains | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 343-350 |
| _classvar_value_permitted | Function | flext-infra/src/flext_infra/detectors/class_placement_detector.py | 353-369 |
| FlextInfraCompatibilityAliasDetector | Class | flext-infra/src/flext_infra/detectors/compatibility_alias_detector.py | 19-264 |
| fix_action_for | Function | flext-infra/src/flext_infra/detectors/compatibility_alias_detector.py | 23-37 |
| detect_file | Function | flext-infra/src/flext_infra/detectors/compatibility_alias_detector.py | 40-136 |
| _detect_foreign_canonical_aliases | Function | flext-infra/src/flext_infra/detectors/compatibility_alias_detector.py | 139-198 |
| _is_private_facade_implementation | Function | flext-infra/src/flext_infra/detectors/compatibility_alias_detector.py | 201-204 |
| _all_from_imports | Function | flext-infra/src/flext_infra/detectors/compatibility_alias_detector.py | 207-217 |
| _resolve_imported_module | Function | flext-infra/src/flext_infra/detectors/compatibility_alias_detector.py | 220-235 |
| _find_import_line | Function | flext-infra/src/flext_infra/detectors/compatibility_alias_detector.py | 238-254 |
| _local_alias_targets | Function | flext-infra/src/flext_infra/detectors/compatibility_alias_detector.py | 257-264 |
| FlextInfraCyclicImportDetector | Class | flext-infra/src/flext_infra/detectors/cyclic_import_detector.py | 18-99 |
| scan_project | Function | flext-infra/src/flext_infra/detectors/cyclic_import_detector.py | 22-79 |
| _prospective_import_targets | Function | flext-infra/src/flext_infra/detectors/cyclic_import_detector.py | 82-99 |
| FlextInfraFutureAnnotationsDetector | Class | flext-infra/src/flext_infra/detectors/future_annotations_detector.py | 17-64 |
| detect_file | Function | flext-infra/src/flext_infra/detectors/future_annotations_detector.py | 21-64 |
| FlextInfraImportAliasDetector | Class | flext-infra/src/flext_infra/detectors/import_alias_detector.py | 12-67 |
| detect_file | Function | flext-infra/src/flext_infra/detectors/import_alias_detector.py | 16-67 |
| FlextInfraInlineImportDetector | Class | flext-infra/src/flext_infra/detectors/inline_import_detector.py | 19-196 |
| fix_action_for | Function | flext-infra/src/flext_infra/detectors/inline_import_detector.py | 23-32 |
| detect_file | Function | flext-infra/src/flext_infra/detectors/inline_import_detector.py | 35-173 |
| _binding_offset | Function | flext-infra/src/flext_infra/detectors/inline_import_detector.py | 176-196 |

*... and 252 more members.*

## Execution Flows

- **_apply_supported_fixes** (criticality: 0.72, depth: 9)
- **detect_declarative** (criticality: 0.72, depth: 6)
- **_enforce_project** (criticality: 0.71, depth: 6)
- **_step** (criticality: 0.64, depth: 6)

## Dependencies

### Outgoing

- `that` (170 edge(s))
- `len` (72 edge(s))
- `append` (70 edge(s))
- `write_text` (61 edge(s))
- `str` (60 edge(s))
- `getattr` (52 edge(s))
- `tuple` (45 edge(s))
- `join` (35 edge(s))
- `detector_context` (31 edge(s))
- `isinstance` (30 edge(s))
- `startswith` (28 edge(s))
- `split` (26 edge(s))
- `strip` (24 edge(s))
- `FileFixOutcome` (24 edge(s))
- `mkdir` (23 edge(s))

### Incoming

- `that` (167 edge(s))
- `write_text` (48 edge(s))
- `detector_context` (31 edge(s))
- `len` (26 edge(s))
- `mkdir` (19 edge(s))
- `flext-infra/tests/unit/refactor/test_infra_refactor_namespace_enforcer.py::TestsFlextInfraRefactorInfraRefactorNamespaceEnforcer` (16 edge(s))
- `detect_file` (16 edge(s))
- `getattr` (10 edge(s))
- `enforcement_rule` (8 edge(s))
- `open_project` (8 edge(s))
- `read_text` (7 edge(s))
- `isinstance` (7 edge(s))
- `flext-infra/tests/unit/check/extended_runners_extra_tests.py::TestExtendedRunnerExtras` (6 edge(s))
- `create_checker_project` (6 edge(s))
- `run_gate_check` (6 edge(s))
