# flext-tests-compose


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 92 nodes

- **Size**: 92 nodes
- **Cohesion**: 0.1169
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| _endpoint | Function | flext-tests/src/flext_tests/_fixtures/connectivity.py | 32-41 |
| _unreachable_reason | Function | flext-tests/src/flext_tests/_fixtures/connectivity.py | 44-76 |
| pytest_collection_modifyitems | Function | flext-tests/src/flext_tests/_fixtures/connectivity.py | 79-91 |
| FlextTestsDocker | Class | flext-tests/src/flext_tests/docker.py | 27-642 |
| ci_disables_docker | Function | flext-tests/src/flext_tests/docker.py | 66-68 |
| skip_if_ci_disables_docker | Function | flext-tests/src/flext_tests/docker.py | 71-74 |
| _resolve_shared_target_config | Function | flext-tests/src/flext_tests/docker.py | 77-98 |
| _resolve_readiness_port | Function | flext-tests/src/flext_tests/docker.py | 101-113 |
| _extract_host_port | Function | flext-tests/src/flext_tests/docker.py | 116-120 |
| model_post_init | Function | flext-tests/src/flext_tests/docker.py | 123-130 |
| client | Function | flext-tests/src/flext_tests/docker.py | 133-156 |
| dirty_containers | Function | flext-tests/src/flext_tests/docker.py | 159-161 |
| container_dirty | Function | flext-tests/src/flext_tests/docker.py | 163-165 |
| mark_container_clean | Function | flext-tests/src/flext_tests/docker.py | 167-175 |
| mark_container_dirty | Function | flext-tests/src/flext_tests/docker.py | 177-185 |
| _load_dirty_state | Function | flext-tests/src/flext_tests/docker.py | 187-204 |
| _save_dirty_state | Function | flext-tests/src/flext_tests/docker.py | 206-216 |
| compose_down | Function | flext-tests/src/flext_tests/docker.py | 218-226 |
| compose_up | Function | flext-tests/src/flext_tests/docker.py | 228-247 |
| _compose_path | Function | flext-tests/src/flext_tests/docker.py | 249-256 |
| _compose_exception_types | Function | flext-tests/src/flext_tests/docker.py | 259-268 |
| compose_project_name | Function | flext-tests/src/flext_tests/docker.py | 271-281 |
| _compose_binding | Function | flext-tests/src/flext_tests/docker.py | 284-295 |
| _run_compose_down | Function | flext-tests/src/flext_tests/docker.py | 297-300 |
| _run_compose_up | Function | flext-tests/src/flext_tests/docker.py | 302-323 |
| _compose_down_current_file | Function | flext-tests/src/flext_tests/docker.py | 325-332 |
| fetch_container_info | Function | flext-tests/src/flext_tests/docker.py | 334-352 |
| fetch_container_status | Function | flext-tests/src/flext_tests/docker.py | 354-358 |
| start_existing_container | Function | flext-tests/src/flext_tests/docker.py | 360-372 |
| start_compose_stack | Function | flext-tests/src/flext_tests/docker.py | 374-382 |
| wait_for_port_ready | Function | flext-tests/src/flext_tests/docker.py | 384-406 |
| _container_info_from_sdk | Function | flext-tests/src/flext_tests/docker.py | 408-434 |
| _start_sdk_container | Function | flext-tests/src/flext_tests/docker.py | 437-447 |
| shared | Function | flext-tests/src/flext_tests/docker.py | 450-465 |
| compose | Function | flext-tests/src/flext_tests/docker.py | 468-485 |
| stack | Function | flext-tests/src/flext_tests/docker.py | 488-496 |
| up | Function | flext-tests/src/flext_tests/docker.py | 498-511 |
| down | Function | flext-tests/src/flext_tests/docker.py | 513-522 |
| ready | Function | flext-tests/src/flext_tests/docker.py | 524-542 |
| cleanup_dirty_containers | Function | flext-tests/src/flext_tests/docker.py | 544-565 |
| execute | Function | flext-tests/src/flext_tests/docker.py | 568-585 |
| _ensure_target_started | Function | flext-tests/src/flext_tests/docker.py | 587-616 |
| _ensure_target_ready | Function | flext-tests/src/flext_tests/docker.py | 618-642 |
| test_compose_resolves_relative_file_against_repository_root | Test | flext-tests/tests/integration/test_docker_integration.py | 77-86 |
| test_sibling_compose_files_use_distinct_projects | Test | flext-tests/tests/integration/test_docker_integration.py | 88-109 |
| test_compose_preserves_absolute_file_unchanged | Test | flext-tests/tests/integration/test_docker_integration.py | 111-120 |
| test_compose_builder_resolves_target_config | Test | flext-tests/tests/unit/_docker_parts/builders.py | 42-54 |
| test_stack_builder_resolves_target_config | Test | flext-tests/tests/unit/_docker_parts/builders.py | 56-69 |
| test_stack_builder_allows_stack_only_target | Test | flext-tests/tests/unit/_docker_parts/builders.py | 71-80 |
| test_compose_up_returns_flext_result | Test | flext-tests/tests/unit/_docker_parts/operations.py | 18-25 |

*... and 42 more members.*

## Execution Flows

- **pytest_collection_modifyitems** (criticality: 0.63, depth: 2)

## Dependencies

### Outgoing

- `that` (78 edge(s))
- `str` (24 edge(s))
- `fail` (21 edge(s))
- `assert_failure` (17 edge(s))
- `mark_container_dirty` (16 edge(s))
- `container_dirty` (16 edge(s))
- `ok` (12 edge(s))
- `tk` (12 edge(s))
- `get` (11 edge(s))
- `ContainerConfig` (11 edge(s))
- `assert_success` (11 edge(s))
- `setenv` (9 edge(s))
- `not_none` (8 edge(s))
- `stack` (8 edge(s))
- `Path` (6 edge(s))

### Incoming

- `that` (78 edge(s))
- `flext-tests/tests/unit/test_docker.py::TestsFlextTestsDocker` (24 edge(s))
- `assert_failure` (17 edge(s))
- `mark_container_dirty` (16 edge(s))
- `container_dirty` (16 edge(s))
- `tk` (12 edge(s))
- `assert_success` (11 edge(s))
- `ContainerConfig` (10 edge(s))
- `flext-tests/tests/unit/_docker_parts/operations.py::DockerOperationsMixin` (10 edge(s))
- `setenv` (9 edge(s))
- `not_none` (8 edge(s))
- `stack` (8 edge(s))
- `str` (7 edge(s))
- `compose` (6 edge(s))
- `mark_container_clean` (6 edge(s))
