# services-display


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 70 nodes

- **Size**: 70 nodes
- **Cohesion**: 0.0686
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextCliFormatters | Class | flext-cli/src/flext_cli/services/formatters.py | 16-45 |
| print | Function | flext-cli/src/flext_cli/services/formatters.py | 20-22 |
| render_rule | Function | flext-cli/src/flext_cli/services/formatters.py | 25-27 |
| render_panel | Function | flext-cli/src/flext_cli/services/formatters.py | 30-32 |
| render_table | Function | flext-cli/src/flext_cli/services/formatters.py | 35-45 |
| FlextCliOutput | Class | flext-cli/src/flext_cli/services/output.py | 16-133 |
| emit_stdout | Function | flext-cli/src/flext_cli/services/output.py | 30-32 |
| display_message | Function | flext-cli/src/flext_cli/services/output.py | 35-46 |
| display_text | Function | flext-cli/src/flext_cli/services/output.py | 49-51 |
| display_message_plain | Function | flext-cli/src/flext_cli/services/output.py | 54-73 |
| print_message | Function | flext-cli/src/flext_cli/services/output.py | 76-79 |
| display_header | Function | flext-cli/src/flext_cli/services/output.py | 82-84 |
| display_progress | Function | flext-cli/src/flext_cli/services/output.py | 87-93 |
| display_status | Function | flext-cli/src/flext_cli/services/output.py | 96-103 |
| display_summary | Function | flext-cli/src/flext_cli/services/output.py | 106-113 |
| display_gate | Function | flext-cli/src/flext_cli/services/output.py | 116-119 |
| display_metrics | Function | flext-cli/src/flext_cli/services/output.py | 122-125 |
| display_debug | Function | flext-cli/src/flext_cli/services/output.py | 128-133 |
| FlextCliTables | Class | flext-cli/src/flext_cli/services/tables.py | 17-60 |
| format_table | Function | flext-cli/src/flext_cli/services/tables.py | 21-31 |
| show_table | Function | flext-cli/src/flext_cli/services/tables.py | 34-60 |
| _render_with_title | Function | flext-cli/src/flext_cli/services/tables.py | 41-44 |
| _print_error | Function | flext-cli/src/flext_cli/services/tables.py | 46-49 |
| test_print_renders_message_to_stdout | Test | flext-cli/tests/unit/test_formatters_cov.py | 34-44 |
| test_public_cli_print_renders_message_to_stdout | Test | flext-cli/tests/unit/test_formatters_cov.py | 46-52 |
| test_render_rule_renders_label_to_stdout | Test | flext-cli/tests/unit/test_formatters_cov.py | 57-66 |
| test_render_panel_renders_content_to_stdout | Test | flext-cli/tests/unit/test_formatters_cov.py | 71-78 |
| test_render_table_renders_columns_and_cells | Test | flext-cli/tests/unit/test_formatters_cov.py | 85-102 |
| test_display_message_prefixes_type_marker_and_keeps_text | Test | flext-cli/tests/unit/test_services_output_cov.py | 41-52 |
| test_display_text_emits_text_regardless_of_style | Test | flext-cli/tests/unit/test_services_output_cov.py | 57-66 |
| test_display_text_is_repeatable | Test | flext-cli/tests/unit/test_services_output_cov.py | 68-73 |
| test_display_header_renders_label_in_rule | Test | flext-cli/tests/unit/test_services_output_cov.py | 89-95 |
| test_display_progress_zero_pads_counter_to_total_width | Test | flext-cli/tests/unit/test_services_output_cov.py | 103-111 |
| test_display_progress_appends_detail_when_present | Test | flext-cli/tests/unit/test_services_output_cov.py | 113-119 |
| test_display_progress_omits_detail_when_empty | Test | flext-cli/tests/unit/test_services_output_cov.py | 121-126 |
| test_display_status_symbol_reflects_outcome | Test | flext-cli/tests/unit/test_services_output_cov.py | 133-142 |
| test_display_status_formats_elapsed_to_two_decimals | Test | flext-cli/tests/unit/test_services_output_cov.py | 147-153 |
| test_display_status_omits_timing_when_elapsed_absent | Test | flext-cli/tests/unit/test_services_output_cov.py | 155-161 |
| test_display_summary_reports_all_counters | Test | flext-cli/tests/unit/test_services_output_cov.py | 165-174 |
| test_display_summary_reflects_explicit_skipped | Test | flext-cli/tests/unit/test_services_output_cov.py | 176-180 |
| test_display_gate_passed_shows_success_symbol_and_name | Test | flext-cli/tests/unit/test_services_output_cov.py | 184-192 |
| test_display_gate_failed_shows_failure_symbol_name_and_message | Test | flext-cli/tests/unit/test_services_output_cov.py | 194-203 |
| test_display_metrics_emits_each_key_value_pair | Test | flext-cli/tests/unit/test_services_output_cov.py | 207-214 |
| test_display_metrics_empty_mapping_emits_nothing | Test | flext-cli/tests/unit/test_services_output_cov.py | 216-220 |
| test_display_debug_is_noop_when_not_verbose | Test | flext-cli/tests/unit/test_services_output_cov.py | 224-228 |
| test_display_debug_emits_labelled_line_when_verbose | Test | flext-cli/tests/unit/test_services_output_cov.py | 230-238 |
| test_format_table_default_config_succeeds_with_rendered_content | Test | flext-cli/tests/unit/test_services_tables_branch_cov.py | 37-48 |
| test_format_table_list_payload_renders_all_cells | Test | flext-cli/tests/unit/test_services_tables_branch_cov.py | 50-61 |
| test_format_table_is_idempotent_for_equal_input | Test | flext-cli/tests/unit/test_services_tables_branch_cov.py | 81-90 |
| test_format_table_rejects_invalid_format_string | Test | flext-cli/tests/unit/test_services_tables_branch_cov.py | 95-102 |

*... and 20 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (82 edge(s))
- `readouterr` (30 edge(s))
- `format_table` (19 edge(s))
- `ok` (13 edge(s))
- `unwrap` (9 edge(s))
- `show_table` (8 edge(s))
- `flat_map` (4 edge(s))
- `display_text` (4 edge(s))
- `s` (3 edge(s))
- `print` (3 edge(s))
- `display_progress` (3 edge(s))
- `display_status` (3 edge(s))
- `tables_resolve_config` (2 edge(s))
- `tables_normalize_data` (2 edge(s))
- `tables_render` (2 edge(s))

### Incoming

- `that` (82 edge(s))
- `readouterr` (30 edge(s))
- `format_table` (19 edge(s))
- `flext-cli/tests/unit/test_services_output_cov.py::TestsFlextCliServicesOutputCov` (18 edge(s))
- `ok` (13 edge(s))
- `unwrap` (9 edge(s))
- `flext-cli/tests/unit/test_tables.py::TestsFlextCliTables` (9 edge(s))
- `flext-cli/tests/unit/test_services_tables_branch_cov.py::TestsFlextCliServicesTablesBranchCov` (8 edge(s))
- `show_table` (8 edge(s))
- `flext-cli/tests/unit/test_services_tables_cov.py::TestsFlextCliServicesTablesCov` (7 edge(s))
- `flext-cli/tests/unit/test_formatters_cov.py::TestsFlextCliFormattersCov` (5 edge(s))
- `display_text` (4 edge(s))
- `flext-cli/src/flext_cli/api.py` (3 edge(s))
- `print` (3 edge(s))
- `display_progress` (3 edge(s))
