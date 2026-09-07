# utilities-source


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
- **Cohesion**: 0.3364
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextInfraUtilitiesRopeAnalysis | Class | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 23-2011 |
| _resource_cache_key | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 40-53 |
| package_name_for_module | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 56-62 |
| _package_name_for_module | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 65-74 |
| resolve_import_module | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 77-83 |
| _resolve_import_module | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 86-94 |
| get_module_semantic_state | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 97-117 |
| _empty_module_semantic_state | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 120-124 |
| _module_semantic_state_from_pymodule | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 127-152 |
| _module_class_infos | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 155-186 |
| superclass_name | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 189-191 |
| _superclass_name | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 194-221 |
| _module_import_maps | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 224-245 |
| _merge_import_statement | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 248-271 |
| _resolved_import_module | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 274-284 |
| _merge_import_alias | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 287-310 |
| find_definition_offset | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 313-321 |
| _definition_offset_from_pymodule | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 324-342 |
| get_semantic_module_imports | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 345-354 |
| get_declared_module_imports | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 357-366 |
| get_module_classes | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 369-378 |
| scope_definitions | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 381-398 |
| _collect_scope_definitions | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 401-422 |
| _scope_kind | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 425-431 |
| _scope_name | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 434-437 |
| get_module_export_names | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 440-472 |
| module_export_names_source | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 475-589 |
| bound_names | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 485-492 |
| collect | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 494-559 |
| _module_export_names | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 592-616 |
| _dunder_export_names | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 619-635 |
| _explicit_export_names | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 638-656 |
| _implicit_export_names | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 659-681 |
| _script_guard_spans | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 684-712 |
| _is_export_name | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 715-747 |
| _explicit_all_names | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 750-768 |
| public_export_names_source | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 771-775 |
| _is_local_name | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 778-787 |
| is_pyclass | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 790-792 |
| is_pyfunction | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 795-797 |
| module_has_docstring_source | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 800-803 |
| module_docstring_summary_source | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 806-814 |
| symbol_has_docstring_source | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 817-828 |
| assignment_docstrings_source | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 831-858 |
| module_body_nodes_source | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 861-864 |
| module_reachable_nodes_source | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 867-870 |
| literal_string_sequence | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 873-895 |
| _sequence_constructor_ref_source | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 898-912 |
| module_assignment_strings_source | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 915-934 |
| module_mapping_assignment_source | Function | flext-infra/src/flext_infra/_utilities/rope_analysis.py | 937-946 |

*... and 64 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `getattr` (60 edge(s))
- `isinstance` (48 edge(s))
- `tuple` (33 edge(s))
- `append` (24 edge(s))
- `len` (24 edge(s))
- `strip` (23 edge(s))
- `fromkeys` (14 edge(s))
- `startswith` (12 edge(s))
- `get` (10 edge(s))
- `extend` (8 edge(s))
- `that` (8 edge(s))
- `get_attributes` (7 edge(s))
- `endswith` (7 edge(s))
- `splitlines` (6 edge(s))
- `find` (6 edge(s))

### Incoming

- `that` (8 edge(s))
- `flext-infra/tests/refactor/test_rope_semantic.py::TestsFlextInfraRefactorRopeSemantic` (6 edge(s))
- `not_none` (4 edge(s))
- `get_class_bases` (3 edge(s))
- `get_semantic_module_imports` (2 edge(s))
- `find_definition_offset` (2 edge(s))
- `write_text` (2 edge(s))
- `flext-infra/src/flext_infra/_utilities/rope_analysis.py` (1 edge(s))
- `read` (1 edge(s))
- `flext-infra/tests/refactor/test_rope_stubs.py::TestsFlextInfraRefactorRopeStubs` (1 edge(s))
- `mkdir` (1 edge(s))
- `init_rope_project` (1 edge(s))
- `get_resource_from_path` (1 edge(s))
- `find_occurrences` (1 edge(s))
- `close` (1 edge(s))
