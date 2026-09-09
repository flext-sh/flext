# services-ldif

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 93 nodes

- **Size**: 93 nodes
- **Cohesion**: 0.2896
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextDbtLdif | Class | flext-dbt-ldif/src/flext_dbt_ldif/api.py | 21-91 |
| **init** | Function | flext-dbt-ldif/src/flext_dbt_ldif/api.py | 34-39 |
| fetch_instance | Function | flext-dbt-ldif/src/flext_dbt_ldif/api.py | 42-46 |
| service | Function | flext-dbt-ldif/src/flext_dbt_ldif/api.py | 49-51 |
| execute | Function | flext-dbt-ldif/src/flext_dbt_ldif/api.py | 53-55 |
| generate_ldif_models | Function | flext-dbt-ldif/src/flext_dbt_ldif/api.py | 57-71 |
| process_ldif_file | Function | flext-dbt-ldif/src/flext_dbt_ldif/api.py | 73-85 |
| validate_ldif_quality | Function | flext-dbt-ldif/src/flext_dbt_ldif/api.py | 87-91 |
| Client | Class | flext-dbt-ldif/src/flext_dbt_ldif/services/client.py | 19-111 |
| **init** | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/client.py | 24-26 |
| settings | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/client.py | 29-31 |
| parse_ldif_file | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/client.py | 33-46 |
| run_full_pipeline | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/client.py | 48-71 |
| transform_with_dbt | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/client.py | 73-89 |
| validate_ldif_data | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/client.py | 91-111 |
| Service | Class | flext-dbt-ldif/src/flext_dbt_ldif/services/service.py | 17-126 |
| **init** | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/service.py | 20-35 |
| generate_and_write_models | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/service.py | 37-57 |
| parse_and_validate_ldif | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/service.py | 59-78 |
| run_complete_workflow | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/service.py | 80-120 |
| run_data_quality_assessment | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/service.py | 122-126 |
| UnifiedService | Class | flext-dbt-ldif/src/flext_dbt_ldif/services/unified_service.py | 14-86 |
| **init** | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/unified_service.py | 27-40 |
| execute | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/unified_service.py | 43-50 |
| generate_analytics_models | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/unified_service.py | 52-68 |
| generate_staging_models | Function | flext-dbt-ldif/src/flext_dbt_ldif/services/unified_service.py | 70-86 |
| TestsFlextDbtLdifServicesDataQuality | Class | flext-dbt-ldif/tests/unit/_services_parts/data_quality.py | 20-51 |
| test_run_data_quality_assessment | Test | flext-dbt-ldif/tests/unit/_services_parts/data_quality.py | 23-51 |
| _parse_ldif_file | Function | flext-dbt-ldif/tests/unit/_services_parts/data_quality.py | 32-33 |
| _validate_ldif_data | Function | flext-dbt-ldif/tests/unit/_services_parts/data_quality.py | 35-42 |
| TestsFlextDbtLdifApiSurface | Class | flext-dbt-ldif/tests/unit/test_api_surface.py | 29-224 |
| client | Function | flext-dbt-ldif/tests/unit/test_api_surface.py | 33-35 |
| test_version_is_nonempty_string | Test | flext-dbt-ldif/tests/unit/test_api_surface.py | 37-40 |
| test_parse_uses_configured_path_when_none_given | Test | flext-dbt-ldif/tests/unit/test_api_surface.py | 42-56 |
| test_parse_prefers_explicit_path_over_settings | Test | flext-dbt-ldif/tests/unit/test_api_surface.py | 58-71 |
| test_validate_reports_quality_for_populated_entries | Test | flext-dbt-ldif/tests/unit/test_api_surface.py | 73-89 |
| test_validate_fails_on_empty_entries | Test | flext-dbt-ldif/tests/unit/test_api_surface.py | 91-96 |
| test_validate_passes_at_maximum_threshold_boundary | Test | flext-dbt-ldif/tests/unit/test_api_surface.py | 98-117 |
| test_transform_reports_records_and_selected_models | Test | flext-dbt-ldif/tests/unit/test_api_surface.py | 127-139 |
| test_full_pipeline_composes_parse_validate_transform | Test | flext-dbt-ldif/tests/unit/test_api_surface.py | 141-156 |
| test_full_pipeline_propagates_parse_failure | Test | flext-dbt-ldif/tests/unit/test_api_surface.py | 158-169 |
| test_service_parse_and_validate_reports_entry_count | Test | flext-dbt-ldif/tests/unit/test_api_surface.py | 171-187 |
| test_facade_execute_returns_settings | Test | flext-dbt-ldif/tests/unit/test_api_surface.py | 189-196 |
| test_facade_service_is_bound_workflow_service | Test | flext-dbt-ldif/tests/unit/test_api_surface.py | 198-207 |
| test_fetch_instance_is_shared_singleton | Test | flext-dbt-ldif/tests/unit/test_api_surface.py | 209-211 |
| test_process_ldif_file_runs_end_to_end_workflow | Test | flext-dbt-ldif/tests/unit/test_api_surface.py | 213-224 |
| TestsFlextDbtLdifClient | Class | flext-dbt-ldif/tests/unit/test_dbt_client.py | 20-167 |
| test_default_construction_yields_usable_global_settings | Test | flext-dbt-ldif/tests/unit/test_dbt_client.py | 25-28 |
| test_explicit_settings_are_the_ones_used | Test | flext-dbt-ldif/tests/unit/test_dbt_client.py | 30-33 |
| test_parse_with_explicit_path_returns_entry_tagged_with_source | Test | flext-dbt-ldif/tests/unit/test_dbt_client.py | 37-45 |

*... and 43 more members.*

## Execution Flows

- **validate_ldif_quality** (criticality: 0.56, depth: 3)

## Dependencies

### Outgoing

- `that` (103 edge(s))
- `ok` (41 edge(s))
- `unwrap` (23 edge(s))
- `from_failure` (12 edge(s))
- `fail` (11 edge(s))
- `str` (11 edge(s))
- `FlextDbtLdif` (10 edge(s))
- `len` (9 edge(s))
- `model_dump` (9 edge(s))
- `list` (7 edge(s))
- `fetch_global` (5 edge(s))
- `FlextDbtLdifSettings` (4 edge(s))
- `lower` (4 edge(s))
- `flext-dbt-ldif/src/flext_dbt_ldif/__init__.py::FlextDbtLdifSettings.fetch_global` (3 edge(s))
- `validate_python` (3 edge(s))

### Incoming

- `that` (103 edge(s))
- `ok` (26 edge(s))
- `unwrap` (23 edge(s))
- `FlextDbtLdif` (10 edge(s))
- `model_dump` (9 edge(s))
- `flext-dbt-ldif/tests/unit/test_services_and_api.py::TestsFlextDbtLdifServicesAndApi` (8 edge(s))
- `fail` (7 edge(s))
- `list` (7 edge(s))
- `str` (6 edge(s))
- `flext-dbt-ldif/tests/unit/test_services.py` (4 edge(s))
- `fetch_global` (4 edge(s))
- `lower` (4 edge(s))
- `fetch_instance` (3 edge(s))
- `model_validate` (3 edge(s))
- `process_ldif_file` (3 edge(s))
