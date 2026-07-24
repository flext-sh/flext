# protocols-plugin

## Overview

Community of 1715 nodes

- **Size**: 1715 nodes
- **Cohesion**: 0.6455
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| EntityFactory | Class | flext-tests/src/flext_tests/_protocols/valuefactory.py | 17-32 |
| **call** | Function | flext-tests/src/flext_tests/_protocols/valuefactory.py | 25-32 |
| ValueFactory | Class | flext-tests/src/flext_tests/_protocols/valuefactory.py | 35-45 |
| **call** | Function | flext-tests/src/flext_tests/_protocols/valuefactory.py | 43-45 |
| EnforcementBuildContext | Class | flext-tests/src/flext_tests/_protocols/enforcement.py | 21-41 |
| infra_report | Function | flext-tests/src/flext_tests/_protocols/enforcement.py | 29-31 |
| validator_targets | Function | flext-tests/src/flext_tests/_protocols/enforcement.py | 34-36 |
| workspace_root | Function | flext-tests/src/flext_tests/_protocols/enforcement.py | 39-41 |
| NamespaceEnforcer | Class | flext-tests/src/flext_tests/_protocols/enforcement.py | 58-67 |
| enforce | Function | flext-tests/src/flext_tests/_protocols/enforcement.py | 61-67 |
| Infra | Class | flext-infra/src/flext_infra/protocols.py | 31-38 |
| _WorkspaceOrchestratorProtocol | Class | flext-infra/src/flext_infra/workspace/_orchestrator_discovery.py | 23-28 |
| root | Function | flext-infra/src/flext_infra/workspace/_orchestrator_discovery.py | 25-25 |
| project_names | Function | flext-infra/src/flext_infra/workspace/_orchestrator_discovery.py | 28-28 |
| FlextInfraProtocolsCheck | Class | flext-infra/src/flext_infra/_protocols/check.py | 19-29 |
| WorkspaceLoopOutcome | Class | flext-infra/src/flext_infra/_protocols/check.py | 23-29 |
| FlextInfraProtocolsRope | Class | flext-infra/src/flext_infra/_protocols/rope.py | 23-242 |
| ChangeTracker | Class | flext-infra/src/flext_infra/_protocols/rope.py | 27-32 |
| apply_to_source | Function | flext-infra/src/flext_infra/_protocols/rope.py | 32-32 |
| RopeScopeDsl | Class | flext-infra/src/flext_infra/_protocols/rope.py | 35-44 |
| get_scopes | Function | flext-infra/src/flext_infra/_protocols/rope.py | 38-38 |
| get_names | Function | flext-infra/src/flext_infra/_protocols/rope.py | 40-40 |
| get_start | Function | flext-infra/src/flext_infra/_protocols/rope.py | 42-42 |
| get_end | Function | flext-infra/src/flext_infra/_protocols/rope.py | 44-44 |
| RopeWorkspaceDsl | Class | flext-infra/src/flext_infra/_protocols/rope.py | 47-153 |
| rope_workspace_root | Function | flext-infra/src/flext_infra/_protocols/rope.py | 53-53 |
| rope_project | Function | flext-infra/src/flext_infra/_protocols/rope.py | 56-56 |
| workspace_index | Function | flext-infra/src/flext_infra/_protocols/rope.py | 59-59 |
| refresh | Function | flext-infra/src/flext_infra/_protocols/rope.py | 61-66 |
| reload | Function | flext-infra/src/flext_infra/_protocols/rope.py | 68-68 |
| **enter** | Function | flext-infra/src/flext_infra/_protocols/rope.py | 70-70 |
| **exit** | Function | flext-infra/src/flext_infra/_protocols/rope.py | 72-77 |
| close | Function | flext-infra/src/flext_infra/_protocols/rope.py | 79-79 |
| resource | Function | flext-infra/src/flext_infra/_protocols/rope.py | 81-84 |
| module | Function | flext-infra/src/flext_infra/_protocols/rope.py | 86-89 |
| package | Function | flext-infra/src/flext_infra/_protocols/rope.py | 91-94 |
| modules | Function | flext-infra/src/flext_infra/_protocols/rope.py | 96-100 |
| source | Function | flext-infra/src/flext_infra/_protocols/rope.py | 102-102 |
| name_index | Function | flext-infra/src/flext_infra/_protocols/rope.py | 104-106 |
| objects | Function | flext-infra/src/flext_infra/_protocols/rope.py | 108-114 |
| projects | Function | flext-infra/src/flext_infra/_protocols/rope.py | 116-116 |
| layout | Function | flext-infra/src/flext_infra/_protocols/rope.py | 118-121 |
| package_context | Function | flext-infra/src/flext_infra/_protocols/rope.py | 123-126 |
| policy | Function | flext-infra/src/flext_infra/_protocols/rope.py | 128-134 |
| convention | Function | flext-infra/src/flext_infra/_protocols/rope.py | 136-141 |
| semantic | Function | flext-infra/src/flext_infra/_protocols/rope.py | 143-146 |
| exports | Function | flext-infra/src/flext_infra/_protocols/rope.py | 148-153 |
| RopePostHook | Class | flext-infra/src/flext_infra/_protocols/rope.py | 156-166 |
| **call** | Function | flext-infra/src/flext_infra/_protocols/rope.py | 159-166 |
| PatchingASTWalker | Class | flext-infra/src/flext_infra/_protocols/rope.py | 169-205 |

*... and 1665 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (42 edge(s))
- `ok` (36 edge(s))
- `fail` (22 edge(s))
- `str` (9 edge(s))
- `FlextProtocolsBase.Base` (7 edge(s))
- `setenv` (7 edge(s))
- `p.Base` (5 edge(s))
- `ABC` (5 edge(s))
- `ValueError` (5 edge(s))
- `settings_snapshot` (5 edge(s))
- `mkdir` (5 edge(s))
- `Response` (3 edge(s))
- `Base` (3 edge(s))
- `map` (3 edge(s))
- `p.Model` (2 edge(s))

### Incoming

- `flext-ldif/src/flext_ldif/_protocols/base.py` (46 edge(s))
- `that` (42 edge(s))
- `flext-infra/src/flext_infra/_protocols/base.py` (34 edge(s))
- `make_prompts` (33 edge(s))
- `ok` (32 edge(s))
- `flext-ldap/src/flext_ldap/protocols.py` (28 edge(s))
- `flext-grpc/src/flext_grpc/protocols.py` (27 edge(s))
- `flext-observability/src/flext_observability/protocols.py` (23 edge(s))
- `flext-infra/src/flext_infra/_protocols/rope_runtime.py` (20 edge(s))
- `fail` (18 edge(s))
- `flext-target-oracle/src/flext_target_oracle/_protocols/base.py` (15 edge(s))
- `flext-core/src/flext_core/_protocols/base.py` (15 edge(s))
- `flext-plugin/src/flext_plugin/protocols.py` (14 edge(s))
- `flext-meltano/src/flext_meltano/_protocols/services.py` (12 edge(s))
- `flext-meltano/src/flext_meltano/_protocols/singer.py` (11 edge(s))
