# phases-apply

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 240 nodes

- **Size**: 240 nodes
- **Cohesion**: 0.3093
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextInfraExtraPathsManager | Class | flext-infra/src/flext_infra/deps/extra_paths.py | 25-247 |
| model_post_init | Function | flext-infra/src/flext_infra/deps/extra_paths.py | 51-55 |
| workspace_project_names | Function | flext-infra/src/flext_infra/deps/extra_paths.py | 58-60 |
| analysis_excluded_top_dirs | Function | flext-infra/src/flext_infra/deps/extra_paths.py | 63-67 |
| execute | Function | flext-infra/src/flext_infra/deps/extra_paths.py | 70-77 |
| _existing_typings_paths | Function | flext-infra/src/flext_infra/deps/extra_paths.py | 80-91 |
| _search_path_set | Function | flext-infra/src/flext_infra/deps/extra_paths.py | 93-124 |
| pyright_extra_paths | Function | flext-infra/src/flext_infra/deps/extra_paths.py | 127-140 |
| pyrefly_search_paths | Function | flext-infra/src/flext_infra/deps/extra_paths.py | 143-182 |
| mypy_search_paths | Function | flext-infra/src/flext_infra/deps/extra_paths.py | 185-209 |
| pyrefly_project_includes | Function | flext-infra/src/flext_infra/deps/extra_paths.py | 211-242 |
| pyrefly_include_globs | Function | flext-infra/src/flext_infra/deps/extra_paths.py | 245-247 |
| FlextInfraConfigFixer | Class | flext-infra/src/flext_infra/deps/fix_pyrefly_config.py | 21-156 |
| **init** | Function | flext-infra/src/flext_infra/deps/fix_pyrefly_config.py | 26-30 |
| execute | Function | flext-infra/src/flext_infra/deps/fix_pyrefly_config.py | 33-35 |
| execute_payload | Function | flext-infra/src/flext_infra/deps/fix_pyrefly_config.py | 38-48 |
| process_file | Function | flext-infra/src/flext_infra/deps/fix_pyrefly_config.py | 50-114 |
| run | Function | flext-infra/src/flext_infra/deps/fix_pyrefly_config.py | 116-156 |
| FlextInfraEnsureCoverageConfigPhase | Class | flext-infra/src/flext_infra/deps/phases/ensure_coverage.py | 9-65 |
| **init** | Function | flext-infra/src/flext_infra/deps/phases/ensure_coverage.py | 12-14 |
| _phases | Function | flext-infra/src/flext_infra/deps/phases/ensure_coverage.py | 16-49 |
| apply | Function | flext-infra/src/flext_infra/deps/phases/ensure_coverage.py | 51-57 |
| apply_payload | Function | flext-infra/src/flext_infra/deps/phases/ensure_coverage.py | 59-65 |
| FlextInfraEnsureFormattingToolingPhase | Class | flext-infra/src/flext_infra/deps/phases/ensure_formatting.py | 9-104 |
| **init** | Function | flext-infra/src/flext_infra/deps/phases/ensure_formatting.py | 12-14 |
| _phases | Function | flext-infra/src/flext_infra/deps/phases/ensure_formatting.py | 16-68 |
| _remove_codespell_skip_doc | Function | flext-infra/src/flext_infra/deps/phases/ensure_formatting.py | 71-80 |
| _remove_codespell_skip_payload | Function | flext-infra/src/flext_infra/deps/phases/ensure_formatting.py | 83-90 |
| apply | Function | flext-infra/src/flext_infra/deps/phases/ensure_formatting.py | 92-96 |
| apply_payload | Function | flext-infra/src/flext_infra/deps/phases/ensure_formatting.py | 98-104 |
| FlextInfraEnsureMypyConfigPhase | Class | flext-infra/src/flext_infra/deps/phases/ensure_mypy.py | 9-69 |
| **init** | Function | flext-infra/src/flext_infra/deps/phases/ensure_mypy.py | 12-14 |
| _phase | Function | flext-infra/src/flext_infra/deps/phases/ensure_mypy.py | 16-61 |
| apply | Function | flext-infra/src/flext_infra/deps/phases/ensure_mypy.py | 63-65 |
| apply_payload | Function | flext-infra/src/flext_infra/deps/phases/ensure_mypy.py | 67-69 |
| FlextInfraEnsureNamespaceToolingPhase | Class | flext-infra/src/flext_infra/deps/phases/ensure_namespace.py | 11-50 |
| _phase | Function | flext-infra/src/flext_infra/deps/phases/ensure_namespace.py | 14-22 |
| apply | Function | flext-infra/src/flext_infra/deps/phases/ensure_namespace.py | 24-34 |
| apply_payload | Function | flext-infra/src/flext_infra/deps/phases/ensure_namespace.py | 36-50 |
| FlextInfraEnsurePackagingPhase | Class | flext-infra/src/flext_infra/deps/phases/ensure_packaging.py | 25-144 |
| **init** | Function | flext-infra/src/flext_infra/deps/phases/ensure_packaging.py | 28-30 |
| _phase | Function | flext-infra/src/flext_infra/deps/phases/ensure_packaging.py | 32-69 |
| apply_payload | Function | flext-infra/src/flext_infra/deps/phases/ensure_packaging.py | 71-144 |
| FlextInfraEnsurePydanticMypyConfigPhase | Class | flext-infra/src/flext_infra/deps/phases/ensure_pydantic_mypy.py | 9-44 |
| **init** | Function | flext-infra/src/flext_infra/deps/phases/ensure_pydantic_mypy.py | 12-14 |
| _phase | Function | flext-infra/src/flext_infra/deps/phases/ensure_pydantic_mypy.py | 16-36 |
| apply | Function | flext-infra/src/flext_infra/deps/phases/ensure_pydantic_mypy.py | 38-40 |
| apply_payload | Function | flext-infra/src/flext_infra/deps/phases/ensure_pydantic_mypy.py | 42-44 |
| FlextInfraEnsurePyreflyConfigPhase | Class | flext-infra/src/flext_infra/deps/phases/ensure_pyrefly.py | 15-180 |
| **init** | Function | flext-infra/src/flext_infra/deps/phases/ensure_pyrefly.py | 18-20 |

*... and 190 more members.*

## Execution Flows

- **apply_payload** (criticality: 0.59, depth: 6)

## Dependencies

### Outgoing

- `that` (167 edge(s))
- `write_text` (65 edge(s))
- `mkdir` (64 edge(s))
- `sorted` (37 edge(s))
- `list` (33 edge(s))
- `ok` (30 edge(s))
- `tuple` (28 edge(s))
- `set` (26 edge(s))
- `toml_document` (26 edge(s))
- `toml_unwrap_item` (26 edge(s))
- `value` (24 edge(s))
- `MutableMapping` (18 edge(s))
- `build` (16 edge(s))
- `table` (15 edge(s))
- `Builder` (15 edge(s))

### Incoming

- `that` (154 edge(s))
- `write_text` (58 edge(s))
- `mkdir` (58 edge(s))
- `ok` (24 edge(s))
- `toml_document` (22 edge(s))
- `toml_unwrap_item` (22 edge(s))
- `set` (20 edge(s))
- `read_text` (11 edge(s))
- `fail` (10 edge(s))
- `apply` (10 edge(s))
- `toml_strings` (10 edge(s))
- `sorted` (9 edge(s))
- `strings` (9 edge(s))
- `sync_one` (8 edge(s))
- `list` (8 edge(s))
