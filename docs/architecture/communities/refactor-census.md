# refactor-census

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 569 nodes

- **Size**: 569 nodes
- **Cohesion**: 0.3489
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
| ------ | ------ | ------ | ------- |
| TestsFlextTestsEnforcementPlugin | Class | flext-tests/tests/unit/test_enforcement_plugin.py | 33-239 |
| test_split_csv_parses_and_normalizes_tokens | Test | flext-tests/tests/unit/test_enforcement_plugin.py | 51-57 |
| test_split_csv_is_idempotent_under_rejoin | Test | flext-tests/tests/unit/test_enforcement_plugin.py | 59-63 |
| _stamp_workspace_markers | Function | flext-tests/tests/unit/test_enforcement_plugin.py | 68-72 |
| test_discover_workspace_root_returns_marked_root | Test | flext-tests/tests/unit/test_enforcement_plugin.py | 74-80 |
| test_discover_workspace_root_walks_upward_from_nested_start | Test | flext-tests/tests/unit/test_enforcement_plugin.py | 82-90 |
| test_discover_workspace_root_returns_none_without_markers | Test | flext-tests/tests/unit/test_enforcement_plugin.py | 92-99 |
| _config | Function | flext-tests/tests/unit/test_enforcement_plugin.py | 104-115 |
| test_active_rules_returns_only_enabled_rules | Test | flext-tests/tests/unit/test_enforcement_plugin.py | 117-121 |
| test_active_rules_include_restricts_to_allow_list | Test | flext-tests/tests/unit/test_enforcement_plugin.py | 123-128 |
| test_active_rules_exclude_removes_blocked_rule | Test | flext-tests/tests/unit/test_enforcement_plugin.py | 130-136 |
| test_active_rules_include_unknown_id_yields_empty | Test | flext-tests/tests/unit/test_enforcement_plugin.py | 138-140 |
| _write_violation_module | Function | flext-tests/tests/unit/test_enforcement_plugin.py | 145-161 |
| _make_workspace_sandbox | Function | flext-tests/tests/unit/test_enforcement_plugin.py | 164-170 |
| test_dispatcher_records_warning_and_prints_summary | Test | flext-tests/tests/unit/test_enforcement_plugin.py | 172-187 |
| test_strict_mode_promotes_warning_to_failure | Test | flext-tests/tests/unit/test_enforcement_plugin.py | 189-205 |
| test_dispatcher_inactive_outside_workspace | Test | flext-tests/tests/unit/test_enforcement_plugin.py | 207-217 |
| test_external_pytest11_plugins_are_loaded_in_subprocess | Test | flext-tests/tests/unit/test_enforcement_plugin.py | 219-239 |
| TestsFlextTestsEnforcementDispatcher | Class | flext-tests/tests/unit/test_enforcement_dispatcher.py | 26-290 |
| workspace | Function | flext-tests/tests/unit/test_enforcement_dispatcher.py | 34-40 |
| rule | Function | flext-tests/tests/unit/test_enforcement_dispatcher.py | 43-45 |
| violation | Function | flext-tests/tests/unit/test_enforcement_dispatcher.py | 48-58 |
| _cfg | Function | flext-tests/tests/unit/test_enforcement_dispatcher.py | 61-71 |
| test_discovers_root_from_nested_descendant | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 77-81 |
| test_returns_workspace_itself_when_start_is_root | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 83-84 |
| test_returns_none_when_no_marker_present | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 86-90 |
| test_returns_none_when_a_single_marker_is_missing | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 92-99 |
| test_sub_project_root_resolves_to_workspace_not_itself | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 101-111 |
| test_split_csv_empty_input_yields_empty_set | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 118-119 |
| test_split_csv_strips_whitespace_and_drops_blank_fields | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 121-124 |
| test_split_csv_deduplicates_repeated_ids | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 126-127 |
| test_active_rules_returns_only_enabled_rules | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 133-137 |
| test_active_rules_excludes_disabled_skill_pointer_rules | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 139-143 |
| test_include_narrows_to_the_listed_ids | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 145-148 |
| test_include_of_unknown_id_yields_no_rules | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 150-155 |
| test_exclude_removes_the_listed_id | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 157-165 |
| test_exclude_takes_precedence_over_include | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 167-175 |
| test_active_rules_is_idempotent | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 177-181 |
| test_runtest_raises_violation_error_when_violations_present | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 187-210 |
| test_runtest_is_a_noop_when_no_violations | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 212-228 |
| test_violation_error_is_an_exception | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 263-264 |
| test_addoption_registers_flext_enforce_cli_options | Test | flext-tests/tests/unit/test_enforcement_dispatcher.py | 271-290 |
| EnforcementDispatcherConfig | Class | flext-tests/src/flext_tests/_models/validator.py | 93-121 |
| discover_workspace_root | Function | flext-tests/src/flext_tests/_fixtures/_enforcement_parts/config.py | 21-29 |
| split_csv | Function | flext-tests/src/flext_tests/_fixtures/_enforcement_parts/config.py | 32-35 |
| resolve_config | Function | flext-tests/src/flext_tests/_fixtures/_enforcement_parts/config.py | 85-115 |
| active_rules | Function | flext-tests/src/flext_tests/_fixtures/_enforcement_parts/config.py | 118-131 |
| pytest_configure | Function | flext-tests/src/flext_tests/_fixtures/_enforcement_parts/config.py | 134-151 |
| build_items | Function | flext-tests/src/flext_tests/_fixtures/_enforcement_parts/build.py | 30-67 |
| _load_infra_report_if_needed | Function | flext-tests/src/flext_tests/_fixtures/_enforcement_parts/build.py | 70-84 |

*... and 519 more members.*

## Execution Flows

- **execute** (criticality: 0.77, depth: 14)
- **_action** (criticality: 0.77, depth: 12)
- **execute** (criticality: 0.77, depth: 13)
- **execute_command** (criticality: 0.76, depth: 15)
- **execute** (criticality: 0.76, depth: 14)
- **_assemble_report** (criticality: 0.76, depth: 15)
- **build_report** (criticality: 0.76, depth: 14)
- **execute** (criticality: 0.76, depth: 12)
- **execute** (criticality: 0.75, depth: 11)

## Dependencies

### Outgoing

- `write_text` (141 edge(s))
- `str` (82 edge(s))
- `len` (72 edge(s))
- `tuple` (64 edge(s))
- `mkdir` (59 edge(s))
- `read_text` (56 edge(s))
- `append` (53 edge(s))
- `extend` (40 edge(s))
- `frozenset` (39 edge(s))
- `unwrap` (37 edge(s))
- `resolve` (35 edge(s))
- `execute` (30 edge(s))
- `joinpath` (29 edge(s))
- `getattr` (28 edge(s))
- `setattr` (26 edge(s))

### Incoming

- `write_text` (125 edge(s))
- `create_lazy_init_workspace` (66 edge(s))
- `len` (52 edge(s))
- `read_text` (52 edge(s))
- `mkdir` (48 edge(s))
- `str` (46 edge(s))
- `run_lazy_init` (45 edge(s))
- `unwrap` (32 edge(s))
- `build_canonical_catalog` (29 edge(s))
- `write_lazy_init_namespace_module` (29 edge(s))
- `execute` (29 edge(s))
- `FlextInfraRefactorCensus` (29 edge(s))
- `setattr` (26 edge(s))
- `joinpath` (25 edge(s))
- `rope_workspace` (25 edge(s))
