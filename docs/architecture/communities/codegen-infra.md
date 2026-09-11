# codegen-infra

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 688 nodes

- **Size**: 688 nodes
- **Cohesion**: 0.1638
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextInfraUtilitiesDiscovery | Class | flext-infra/src/flext_infra/_utilities/discovery.py | 26-603 |
| _workspace_project_roots | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 37-49 |
| _discover_project_root_from_path | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 52-73 |
| _relative_path_parts | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 76-83 |
| _normalized_python_parts | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 86-92 |
| _package_name_from_wrapper_parts | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 95-105 |
| _package_name_from_src_dir | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 108-117 |
| is_pytest_test_module | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 120-127 |
| project_root | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 130-135 |
| _discover_package_from_path | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 138-170 |
| package_name | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 173-175 |
| alias_migration_context | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 178-197 |
| package_importable | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 200-209 |
| installed_package_exports | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 213-228 |
| discover_python_dirs | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 231-260 |
| discover_python_targets | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 263-278 |
| _walk_python_files | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 281-302 |
| _python_file_belongs_to_project | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 305-312 |
| analyzer_python_roots | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 315-349 |
| _workspace_excluded_top_dirs | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 352-360 |
| package_init_path | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 363-392 |
| package_source_priority | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 395-404 |
| rope_repository_root | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 407-453 |
| find_all_pyproject_files | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 456-508 |
| resolve_parent_constants_flext | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 511-538 |
| resolve_transitive_parent_packages | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 541-564 |
| visit | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 548-559 |
| contextual_runtime_alias_sources | Function | flext-infra/src/flext_infra/_utilities/discovery.py | 567-603 |
| FlextInfraUtilitiesRepository | Class | flext-infra/src/flext_infra/_utilities/repository.py | 14-166 |
| derived_repository_ref | Function | flext-infra/src/flext_infra/_utilities/repository.py | 18-44 |
| configured_repository_ref | Function | flext-infra/src/flext_infra/_utilities/repository.py | 47-65 |
| repository_provider | Function | flext-infra/src/flext_infra/_utilities/repository.py | 68-79 |
| resolve_integration_branch | Function | flext-infra/src/flext_infra/_utilities/repository.py | 82-88 |
| gitmodule_branch_is_governed | Function | flext-infra/src/flext_infra/_utilities/repository.py | 91-102 |
| repository_baseline_branch | Function | flext-infra/src/flext_infra/_utilities/repository.py | 105-142 |
| workspace_spec_load | Function | flext-infra/src/flext_infra/_utilities/repository.py | 145-149 |
| repository_conform_target | Function | flext-infra/src/flext_infra/_utilities/repository.py | 152-166 |
| FlextInfraCodegenLayoutGitignoreMixin | Class | flext-infra/src/flext_infra/codegen/_layout_gitignore.py | 20-110 |
| _apply_gitignore | Function | flext-infra/src/flext_infra/codegen/_layout_gitignore.py | 23-33 |
| _apply_gitignore_managed | Function | flext-infra/src/flext_infra/codegen/_layout_gitignore.py | 35-59 |
| _apply_gitignore_append | Function | flext-infra/src/flext_infra/codegen/_layout_gitignore.py | 61-90 |
| _managed_profile | Function | flext-infra/src/flext_infra/codegen/_layout_gitignore.py | 93-110 |
| FlextInfraCodegenTransaction | Class | flext-infra/src/flext_infra/codegen/codegen_transaction.py | 29-724 |
| **init** | Function | flext-infra/src/flext_infra/codegen/codegen_transaction.py | 32-38 |
| validate | Function | flext-infra/src/flext_infra/codegen/codegen_transaction.py | 40-47 |
| validate_locked | Function | flext-infra/src/flext_infra/codegen/codegen_transaction.py | 49-82 |
| validate_phase_analysis_locked | Function | flext-infra/src/flext_infra/codegen/codegen_transaction.py | 85-89 |
| run_locked | Function | flext-infra/src/flext_infra/codegen/codegen_transaction.py | 91-109 |
| _run_locked_operation | Function | flext-infra/src/flext_infra/codegen/codegen_transaction.py | 111-123 |
| begin_locked | Function | flext-infra/src/flext_infra/codegen/codegen_transaction.py | 125-284 |

*... and 638 more members.*

## Execution Flows

- **_action** (criticality: 0.66, depth: 8)
- **validate** (criticality: 0.61, depth: 6)
- **execute_command** (criticality: 0.61, depth: 1)
- **apply_payload** (criticality: 0.59, depth: 6)

## Dependencies

### Outgoing

- `that` (770 edge(s))
- `ok` (454 edge(s))
- `fail` (248 edge(s))
- `from_failure` (248 edge(s))
- `write_text` (215 edge(s))
- `mkdir` (162 edge(s))
- `tuple` (154 edge(s))
- `str` (80 edge(s))
- `Path` (74 edge(s))
- `read_text` (69 edge(s))
- `is_file` (62 edge(s))
- `exists` (59 edge(s))
- `append` (58 edge(s))
- `run_checked` (56 edge(s))
- `as_posix` (55 edge(s))

### Incoming

- `that` (757 edge(s))
- `ok` (251 edge(s))
- `write_text` (160 edge(s))
- `mkdir` (106 edge(s))
- `read_text` (63 edge(s))
- `fail` (61 edge(s))
- `str` (52 edge(s))
- `exists` (44 edge(s))
- `create_docs_workspace` (34 edge(s))
- `tuple` (32 edge(s))
- `toml_mapping` (30 edge(s))
- `run_checked` (28 edge(s))
- `read_bytes` (26 edge(s))
- `Path` (25 edge(s))
- `is_file` (24 edge(s))
