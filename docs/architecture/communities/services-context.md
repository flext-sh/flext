# services-context


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 169 nodes

- **Size**: 169 nodes
- **Cohesion**: 0.4026
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextObservabilityAdvancedContext | Class | flext-observability/src/flext_observability/services/advanced_context.py | 24-278 |
| Context | Class | flext-observability/src/flext_observability/services/advanced_context.py | 53-235 |
| __init__ | Function | flext-observability/src/flext_observability/services/advanced_context.py | 56-61 |
| clear | Function | flext-observability/src/flext_observability/services/advanced_context.py | 63-77 |
| baggage | Function | flext-observability/src/flext_observability/services/advanced_context.py | 80-87 |
| metadata | Function | flext-observability/src/flext_observability/services/advanced_context.py | 90-97 |
| resolve_baggage | Function | flext-observability/src/flext_observability/services/advanced_context.py | 99-111 |
| resolve_metadata | Function | flext-observability/src/flext_observability/services/advanced_context.py | 113-123 |
| merge | Function | flext-observability/src/flext_observability/services/advanced_context.py | 125-143 |
| restore | Function | flext-observability/src/flext_observability/services/advanced_context.py | 145-167 |
| update_baggage | Function | flext-observability/src/flext_observability/services/advanced_context.py | 169-185 |
| update_metadata | Function | flext-observability/src/flext_observability/services/advanced_context.py | 187-213 |
| snapshot | Function | flext-observability/src/flext_observability/services/advanced_context.py | 215-235 |
| active_context | Function | flext-observability/src/flext_observability/services/advanced_context.py | 238-249 |
| resolve_metadata | Function | flext-observability/src/flext_observability/services/advanced_context.py | 252-263 |
| update_metadata | Function | flext-observability/src/flext_observability/services/advanced_context.py | 266-278 |
| FlextObservabilityContext | Class | flext-observability/src/flext_observability/services/context.py | 22-392 |
| clear_baggage | Function | flext-observability/src/flext_observability/services/context.py | 61-63 |
| clear_context | Function | flext-observability/src/flext_observability/services/context.py | 66-87 |
| clear_correlation_id | Function | flext-observability/src/flext_observability/services/context.py | 90-96 |
| clear_span_id | Function | flext-observability/src/flext_observability/services/context.py | 99-101 |
| clear_trace_id | Function | flext-observability/src/flext_observability/services/context.py | 104-106 |
| from_headers | Function | flext-observability/src/flext_observability/services/context.py | 109-141 |
| _apply_headers | Function | flext-observability/src/flext_observability/services/context.py | 144-155 |
| resolve_baggage | Function | flext-observability/src/flext_observability/services/context.py | 158-186 |
| context_payload | Function | flext-observability/src/flext_observability/services/context.py | 189-228 |
| correlation_id | Function | flext-observability/src/flext_observability/services/context.py | 231-247 |
| span_id | Function | flext-observability/src/flext_observability/services/context.py | 250-252 |
| trace_id | Function | flext-observability/src/flext_observability/services/context.py | 255-257 |
| update_baggage | Function | flext-observability/src/flext_observability/services/context.py | 260-286 |
| _update_baggage_value | Function | flext-observability/src/flext_observability/services/context.py | 289-298 |
| update_correlation_id | Function | flext-observability/src/flext_observability/services/context.py | 301-326 |
| update_span_id | Function | flext-observability/src/flext_observability/services/context.py | 329-334 |
| update_trace_id | Function | flext-observability/src/flext_observability/services/context.py | 337-353 |
| to_headers | Function | flext-observability/src/flext_observability/services/context.py | 356-392 |
| FlextObservabilityCustomMetrics | Class | flext-observability/src/flext_observability/services/custom_metrics.py | 26-399 |
| Registry | Class | flext-observability/src/flext_observability/services/custom_metrics.py | 62-327 |
| __init__ | Function | flext-observability/src/flext_observability/services/custom_metrics.py | 65-71 |
| clear_metrics | Function | flext-observability/src/flext_observability/services/custom_metrics.py | 73-86 |
| _clear_metrics | Function | flext-observability/src/flext_observability/services/custom_metrics.py | 88-101 |
| resolve_metrics | Function | flext-observability/src/flext_observability/services/custom_metrics.py | 103-120 |
| resolve_metric | Function | flext-observability/src/flext_observability/services/custom_metrics.py | 122-139 |
| resolve_metric_info | Function | flext-observability/src/flext_observability/services/custom_metrics.py | 141-163 |
| resolve_metrics_by_type | Function | flext-observability/src/flext_observability/services/custom_metrics.py | 165-181 |
| list_metrics | Function | flext-observability/src/flext_observability/services/custom_metrics.py | 183-190 |
| register_metric | Function | flext-observability/src/flext_observability/services/custom_metrics.py | 192-228 |
| _register_metric_definition | Function | flext-observability/src/flext_observability/services/custom_metrics.py | 230-268 |
| _validate_metric_definition_input | Function | flext-observability/src/flext_observability/services/custom_metrics.py | 271-296 |
| unregister_metric | Function | flext-observability/src/flext_observability/services/custom_metrics.py | 298-327 |
| resolve_metric | Function | flext-observability/src/flext_observability/services/custom_metrics.py | 330-344 |

*... and 119 more members.*

## Execution Flows

- **setup_instrumentation** (criticality: 0.62, depth: 2)
- **setup_instrumentation** (criticality: 0.62, depth: 2)
- **setup_instrumentation** (criticality: 0.62, depth: 2)
- **setup_instrumentation** (criticality: 0.62, depth: 2)
- **_after_request_hook** (criticality: 0.62, depth: 6)
- **_dispatch_request** (criticality: 0.61, depth: 6)
- **traced_async_request** (criticality: 0.59, depth: 5)
- **traced_request** (criticality: 0.59, depth: 5)
- **traced_request** (criticality: 0.59, depth: 5)
- **_error_handler** (criticality: 0.57, depth: 5)

## Dependencies

### Outgoing

- `ok` (47 edge(s))
- `get` (31 edge(s))
- `that` (25 edge(s))
- `fail` (23 edge(s))
- `debug` (20 edge(s))
- `str` (18 edge(s))
- `time` (16 edge(s))
- `dict` (11 edge(s))
- `items` (10 edge(s))
- `Dict` (10 edge(s))
- `fail_op` (10 edge(s))
- `getattr` (10 edge(s))
- `model_validate` (9 edge(s))
- `set` (9 edge(s))
- `fail_operation` (7 edge(s))

### Incoming

- `that` (25 edge(s))
- `ok` (15 edge(s))
- `flext-observability/src/flext_observability/api.py` (9 edge(s))
- `update_metadata` (4 edge(s))
- `should_sample` (4 edge(s))
- `fail` (4 edge(s))
- `flext-observability/src/flext_observability/services/http_client_instrumentation.py` (3 edge(s))
- `flext-observability/src/flext_observability/services/http_instrumentation.py` (3 edge(s))
- `record_error` (3 edge(s))
- `flext-observability/src/flext_observability/services/advanced_context.py` (2 edge(s))
- `flext-observability/src/flext_observability/services/custom_metrics.py` (2 edge(s))
- `flext-observability/src/flext_observability/services/error_handling.py` (2 edge(s))
- `flext-observability/src/flext_observability/services/performance.py` (2 edge(s))
- `flext-observability/src/flext_observability/services/sampling.py` (2 edge(s))
- `resolve_metadata` (2 edge(s))
