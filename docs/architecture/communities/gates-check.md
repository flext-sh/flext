# gates-check


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 290 nodes

- **Size**: 290 nodes
- **Cohesion**: 0.2685
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextInfraGateRegistry | Class | flext-infra/src/flext_infra/check/workspace_check_gates.py | 37-111 |
| __init__ | Function | flext-infra/src/flext_infra/check/workspace_check_gates.py | 40-67 |
| _gate_classes | Function | flext-infra/src/flext_infra/check/workspace_check_gates.py | 70-93 |
| get | Function | flext-infra/src/flext_infra/check/workspace_check_gates.py | 95-97 |
| create | Function | flext-infra/src/flext_infra/check/workspace_check_gates.py | 99-106 |
| default | Function | flext-infra/src/flext_infra/check/workspace_check_gates.py | 109-111 |
| FlextInfraWorkspaceCheckGatesMixin | Class | flext-infra/src/flext_infra/check/workspace_check_gates.py | 114-336 |
| _isolate_context | Function | flext-infra/src/flext_infra/check/workspace_check_gates.py | 122-134 |
| _run_single_project | Function | flext-infra/src/flext_infra/check/workspace_check_gates.py | 136-164 |
| _run_project_loop | Function | flext-infra/src/flext_infra/check/workspace_check_gates.py | 166-198 |
| _gate_ctx | Function | flext-infra/src/flext_infra/check/workspace_check_gates.py | 200-205 |
| _run_gate | Function | flext-infra/src/flext_infra/check/workspace_check_gates.py | 207-229 |
| _check_project_with_ctx | Function | flext-infra/src/flext_infra/check/workspace_check_gates.py | 231-258 |
| _make_gate_handler | Function | flext-infra/src/flext_infra/check/workspace_check_gates.py | 264-325 |
| _handler | Function | flext-infra/src/flext_infra/check/workspace_check_gates.py | 279-323 |
| _execute_gate | Function | flext-infra/src/flext_infra/check/workspace_check_gates.py | 328-336 |
| FlextInfraModGateEngine | Class | flext-infra/src/flext_infra/codemod/batch_gates.py | 20-488 |
| validate_rule_fixtures | Function | flext-infra/src/flext_infra/codemod/batch_gates.py | 24-75 |
| _rule_documents | Function | flext-infra/src/flext_infra/codemod/batch_gates.py | 78-88 |
| _materialize_split_rule_files | Function | flext-infra/src/flext_infra/codemod/batch_gates.py | 91-136 |
| _sync_rule_fixture_root | Function | flext-infra/src/flext_infra/codemod/batch_gates.py | 139-168 |
| _run_tool | Function | flext-infra/src/flext_infra/codemod/batch_gates.py | 171-223 |
| _is_apply_receipt | Function | flext-infra/src/flext_infra/codemod/batch_gates.py | 226-228 |
| _path_depth | Function | flext-infra/src/flext_infra/codemod/batch_gates.py | 231-233 |
| _validate_finding_receipt | Function | flext-infra/src/flext_infra/codemod/batch_gates.py | 236-247 |
| _parse_findings | Function | flext-infra/src/flext_infra/codemod/batch_gates.py | 250-350 |
| _report_evidence | Function | flext-infra/src/flext_infra/codemod/batch_gates.py | 353-373 |
| validate | Function | flext-infra/src/flext_infra/codemod/batch_gates.py | 376-404 |
| scan | Function | flext-infra/src/flext_infra/codemod/batch_gates.py | 407-488 |
| FlextInfraCodemodSnapshotReconciler | Class | flext-infra/src/flext_infra/codemod/snapshot_reconciler.py | 11-59 |
| config_root | Function | flext-infra/src/flext_infra/codemod/snapshot_reconciler.py | 15-21 |
| reconcile | Function | flext-infra/src/flext_infra/codemod/snapshot_reconciler.py | 24-59 |
| FlextInfraDeferredSelfReferenceDetector | Class | flext-infra/src/flext_infra/detectors/deferred_self_reference_detector.py | 14-44 |
| detect_file | Function | flext-infra/src/flext_infra/detectors/deferred_self_reference_detector.py | 18-44 |
| FlextInfraLspDiagnosticsDetector | Class | flext-infra/src/flext_infra/detectors/lsp_diagnostics.py | 17-231 |
| validate | Function | flext-infra/src/flext_infra/detectors/lsp_diagnostics.py | 27-219 |
| remaining | Function | flext-infra/src/flext_infra/detectors/lsp_diagnostics.py | 49-50 |
| reject | Function | flext-infra/src/flext_infra/detectors/lsp_diagnostics.py | 52-62 |
| send | Function | flext-infra/src/flext_infra/detectors/lsp_diagnostics.py | 64-65 |
| receive | Function | flext-infra/src/flext_infra/detectors/lsp_diagnostics.py | 67-94 |
| record | Function | flext-infra/src/flext_infra/detectors/lsp_diagnostics.py | 96-117 |
| _frame | Function | flext-infra/src/flext_infra/detectors/lsp_diagnostics.py | 222-231 |
| FlextInfraSilentFailureDetector | Class | flext-infra/src/flext_infra/detectors/silent_failure_detector.py | 14-72 |
| detect_file | Function | flext-infra/src/flext_infra/detectors/silent_failure_detector.py | 18-42 |
| detect_violations | Function | flext-infra/src/flext_infra/detectors/silent_failure_detector.py | 45-67 |
| fixable_kinds | Function | flext-infra/src/flext_infra/detectors/silent_failure_detector.py | 70-72 |
| _rope_module_ast | Function | flext-infra/src/flext_infra/detectors/silent_failure_detector.py | 75-81 |
| FlextInfraGateFixerAdapter | Class | flext-infra/src/flext_infra/fixers/gate_fixer.py | 22-215 |
| __init__ | Function | flext-infra/src/flext_infra/fixers/gate_fixer.py | 32-34 |
| _registry | Function | flext-infra/src/flext_infra/fixers/gate_fixer.py | 36-38 |

*... and 240 more members.*

## Execution Flows

- **check** (criticality: 0.70, depth: 5)
- **check** (criticality: 0.56, depth: 1)

## Dependencies

### Outgoing

- `that` (78 edge(s))
- `str` (55 edge(s))
- `append` (47 edge(s))
- `isinstance` (43 edge(s))
- `tuple` (42 edge(s))
- `strip` (39 edge(s))
- `Issue` (39 edge(s))
- `len` (36 edge(s))
- `fail` (36 edge(s))
- `write_text` (35 edge(s))
- `get` (31 edge(s))
- `json_pick_str` (29 edge(s))
- `ok` (26 edge(s))
- `from_failure` (23 edge(s))
- `unwrap` (22 edge(s))

### Incoming

- `that` (78 edge(s))
- `write_text` (25 edge(s))
- `mk_project` (13 edge(s))
- `len` (12 edge(s))
- `check` (11 edge(s))
- `mkdir` (10 edge(s))
- `gate_context` (6 edge(s))
- `str` (4 edge(s))
- `flext-infra/src/flext_infra/transformers/smells/boolean_logic.py` (3 edge(s))
- `flext-infra/src/flext_infra/services/cli_routes_validate_commands.py` (3 edge(s))
- `GateContext` (3 edge(s))
- `flext-infra/tests/unit/check/direnv_gate_tests.py` (3 edge(s))
- `command_runner` (3 edge(s))
- `any` (3 edge(s))
- `flext-infra/tests/unit/validate/silent_failure_tests.py` (3 edge(s))
