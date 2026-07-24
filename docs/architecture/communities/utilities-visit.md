# utilities-visit

## Overview

Community of 29 nodes

- **Size**: 29 nodes
- **Cohesion**: 0.4427
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| _SilentFailureFinding | Class | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 16-22 |
| _SilentFailureAstVisitor | Class | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 25-328 |
| **init** | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 35-40 |
| analyze | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 42-49 |
| _enclosing_function | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 51-60 |
| _result_inner_type | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 62-76 |
| _line_offsets | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 78-81 |
| _indent_of | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 83-86 |
| _add_finding | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 88-107 |
| visit_Import | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 110-114 |
| visit_ImportFrom | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 117-124 |
| visit_Call | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 127-146 |
| visit_ExceptHandler | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 149-169 |
| visit_If | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 172-177 |
| _is_except_pass | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 179-184 |
| _is_broad_unhandled_except | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 186-192 |
| _is_except_sentinel | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 194-201 |
| _body_has_sentinel_return | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 203-210 |
| _is_sentinel_value | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 212-219 |
| _body_has_raise_or_fail | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 222-233 |
| _guard_info | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 235-252 |
| _add_guard_finding | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 254-286 |
| _add_except_sentinel_finding | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 288-319 |
| _first_sentinel_return | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 321-328 |
| _resolve_call_name | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 331-342 |
| _is_unwrap_or_call | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 345-360 |
| _expression_name | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 363-375 |
| collect_silent_failure_findings | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 378-383 |
| collect_silent_failure_fixes | Function | flext-infra/src/flext_infra/_utilities/silent_failure_ast.py | 386-398 |

## Execution Flows

- **refactor_files** (criticality: 0.76, depth: 15)
- **execute** (criticality: 0.76, depth: 13)
- **execute** (criticality: 0.76, depth: 14)
- **build_report** (criticality: 0.76, depth: 14)

## Dependencies

### Outgoing

- `isinstance` (28 edge(s))
- `get` (5 edge(s))
- `generic_visit` (5 edge(s))
- `walk` (4 edge(s))
- `len` (3 edge(s))
- `ast.NodeVisitor` (1 edge(s))
- `splitlines` (1 edge(s))
- `append` (1 edge(s))
- `strip` (1 edge(s))
- `replace` (1 edge(s))
- `removesuffix` (1 edge(s))
- `lstrip` (1 edge(s))
- `all` (1 edge(s))
- `any` (1 edge(s))
- `sum` (1 edge(s))

### Incoming

- `flext-infra/src/flext_infra/_utilities/silent_failure_ast.py` (7 edge(s))
- `flext-infra/src/flext_infra/detectors/silent_failure_detector.py::FlextInfraSilentFailureDetector.detect_file` (1 edge(s))
- `flext-infra/src/flext_infra/detectors/silent_failure_detector.py::FlextInfraSilentFailureDetector.detect_violations` (1 edge(s))
- `flext-infra/src/flext_infra/_utilities/rope_source.py::FlextInfraUtilitiesRopeSource.fix_silent_failure_sentinels` (1 edge(s))
