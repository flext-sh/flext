# codegen-infra-flext


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 345 nodes

- **Size**: 345 nodes
- **Cohesion**: 0.2092
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextInfraCodegenFixerResultsMixin | Class | flext-infra/src/flext_infra/codegen/_fixer_results.py | 18-91 |
| _empty_result | Function | flext-infra/src/flext_infra/codegen/_fixer_results.py | 22-29 |
| _build_result | Function | flext-infra/src/flext_infra/codegen/_fixer_results.py | 32-41 |
| _load_initial_violations | Function | flext-infra/src/flext_infra/codegen/_fixer_results.py | 44-65 |
| _classify_remaining_violations | Function | flext-infra/src/flext_infra/codegen/_fixer_results.py | 68-91 |
| FlextInfraCodegenPipelineStagesMixin | Class | flext-infra/src/flext_infra/codegen/_pipeline_stages.py | 22-260 |
| _run_stage | Function | flext-infra/src/flext_infra/codegen/_pipeline_stages.py | 34-39 |
| _stage_discover | Function | flext-infra/src/flext_infra/codegen/_pipeline_stages.py | 41-62 |
| _action | Function | flext-infra/src/flext_infra/codegen/_pipeline_stages.py | 246-251 |
| _emit | Function | flext-infra/src/flext_infra/codegen/_pipeline_stages.py | 253-258 |
| _stage_toolchain | Function | flext-infra/src/flext_infra/codegen/_pipeline_stages.py | 64-96 |
| _stage_deps | Function | flext-infra/src/flext_infra/codegen/_pipeline_stages.py | 98-134 |
| _stage_py_typed | Function | flext-infra/src/flext_infra/codegen/_pipeline_stages.py | 136-149 |
| _stage_census_before | Function | flext-infra/src/flext_infra/codegen/_pipeline_stages.py | 151-176 |
| _stage_scaffold | Function | flext-infra/src/flext_infra/codegen/_pipeline_stages.py | 178-197 |
| _stage_auto_fix | Function | flext-infra/src/flext_infra/codegen/_pipeline_stages.py | 199-218 |
| _stage_lazy_init | Function | flext-infra/src/flext_infra/codegen/_pipeline_stages.py | 220-239 |
| _stage_census_after | Function | flext-infra/src/flext_infra/codegen/_pipeline_stages.py | 241-260 |
| FlextInfraCodegenCensus | Class | flext-infra/src/flext_infra/codegen/census.py | 25-113 |
| execute | Function | flext-infra/src/flext_infra/codegen/census.py | 29-60 |
| run | Function | flext-infra/src/flext_infra/codegen/census.py | 62-82 |
| _run_project_census | Function | flext-infra/src/flext_infra/codegen/census.py | 84-98 |
| _census_project | Function | flext-infra/src/flext_infra/codegen/census.py | 100-113 |
| FlextInfraCodegenConsolidator | Class | flext-infra/src/flext_infra/codegen/consolidator.py | 16-151 |
| execute | Function | flext-infra/src/flext_infra/codegen/consolidator.py | 25-109 |
| _project_python_files | Function | flext-infra/src/flext_infra/codegen/consolidator.py | 111-136 |
| _selected_projects | Function | flext-infra/src/flext_infra/codegen/consolidator.py | 138-151 |
| FlextInfraCodegenQualityGate | Class | flext-infra/src/flext_infra/codegen/constants_quality_gate.py | 24-417 |
| execute | Function | flext-infra/src/flext_infra/codegen/constants_quality_gate.py | 28-36 |
| build_report | Function | flext-infra/src/flext_infra/codegen/constants_quality_gate.py | 38-99 |
| modified_python_files | Function | flext-infra/src/flext_infra/codegen/constants_quality_gate.py | 102-126 |
| run_static_check | Function | flext-infra/src/flext_infra/codegen/constants_quality_gate.py | 129-180 |
| _run_static_checks | Function | flext-infra/src/flext_infra/codegen/constants_quality_gate.py | 183-215 |
| after_metrics | Function | flext-infra/src/flext_infra/codegen/constants_quality_gate.py | 218-246 |
| build_checks | Function | flext-infra/src/flext_infra/codegen/constants_quality_gate.py | 249-301 |
| compute_verdict | Function | flext-infra/src/flext_infra/codegen/constants_quality_gate.py | 304-312 |
| project_findings | Function | flext-infra/src/flext_infra/codegen/constants_quality_gate.py | 315-336 |
| write_artifacts | Function | flext-infra/src/flext_infra/codegen/constants_quality_gate.py | 339-361 |
| render_text | Function | flext-infra/src/flext_infra/codegen/constants_quality_gate.py | 364-408 |
| successful_verdict | Function | flext-infra/src/flext_infra/codegen/constants_quality_gate.py | 411-417 |
| FlextInfraCodegenFixer | Class | flext-infra/src/flext_infra/codegen/fixer.py | 27-61 |
| execute | Function | flext-infra/src/flext_infra/codegen/fixer.py | 40-61 |
| FlextInfraCodegenLazyInit | Class | flext-infra/src/flext_infra/codegen/lazy_init.py | 29-281 |
| modified_files | Function | flext-infra/src/flext_infra/codegen/lazy_init.py | 41-43 |
| execute | Function | flext-infra/src/flext_infra/codegen/lazy_init.py | 46-67 |
| plan_files | Function | flext-infra/src/flext_infra/codegen/lazy_init.py | 69-95 |
| _plan_in_workspace | Function | flext-infra/src/flext_infra/codegen/lazy_init.py | 97-105 |
| _plan_open_workspace | Function | flext-infra/src/flext_infra/codegen/lazy_init.py | 107-202 |
| _package_dirs_for_target | Function | flext-infra/src/flext_infra/codegen/lazy_init.py | 205-237 |
| _detect_duplicate_class_names | Function | flext-infra/src/flext_infra/codegen/lazy_init.py | 240-281 |

*... and 295 more members.*

## Execution Flows

- **_apply_supported_fixes** (criticality: 0.72, depth: 9)
- **_stage_census_before** (criticality: 0.67, depth: 5)
- **_action** (criticality: 0.66, depth: 8)
- **_load_initial_violations** (criticality: 0.63, depth: 2)
- **_classify_remaining_violations** (criticality: 0.63, depth: 2)
- **check** (criticality: 0.63, depth: 2)
- **execute** (criticality: 0.60, depth: 2)

## Dependencies

### Outgoing

- `that` (477 edge(s))
- `write_text` (148 edge(s))
- `create_lazy_init_workspace` (73 edge(s))
- `mkdir` (71 edge(s))
- `ok` (61 edge(s))
- `len` (59 edge(s))
- `joinpath` (46 edge(s))
- `tuple` (43 edge(s))
- `resolve` (42 edge(s))
- `str` (40 edge(s))
- `read_text` (37 edge(s))
- `read_bytes` (37 edge(s))
- `write_lazy_init_namespace_module` (36 edge(s))
- `get` (32 edge(s))
- `exists` (29 edge(s))

### Incoming

- `that` (475 edge(s))
- `write_text` (129 edge(s))
- `create_lazy_init_workspace` (69 edge(s))
- `mkdir` (60 edge(s))
- `joinpath` (46 edge(s))
- `read_bytes` (36 edge(s))
- `ok` (34 edge(s))
- `read_text` (34 edge(s))
- `write_lazy_init_namespace_module` (32 edge(s))
- `run_lazy_init` (29 edge(s))
- `exists` (26 edge(s))
- `create_lazy_init_service` (25 edge(s))
- `rope_workspace` (20 edge(s))
- `resolve` (19 edge(s))
- `len` (14 edge(s))
