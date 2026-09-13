# models-infra

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 27 nodes

- **Size**: 27 nodes
- **Cohesion**: 0.3291
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
| ------ | ------ | ------ | ------- |
| Infra | Class | flext-infra/src/flext_infra/models.py | 34-52 |
| FlextInfraModelsDeps | Class | flext-infra/src/flext_infra/_models/deps.py | 17-329 |
| FlextInfraModelsMixins | Class | flext-infra/src/flext_infra/_models/mixins.py | 14-322 |
| FlextInfraModelsBase | Class | flext-infra/src/flext_infra/_models/base.py | 19-165 |
| FlextInfraModelsBasemk | Class | flext-infra/src/flext_infra/_models/basemk.py | 13-55 |
| FlextInfraModelsCensus | Class | flext-infra/src/flext_infra/_models/census.py | 14-469 |
| FlextInfraModelsCodegenRender | Class | flext-infra/src/flext_infra/_models/codegen_render.py | 11-105 |
| FlextInfraModelsDepsToml | Class | flext-infra/src/flext_infra/_models/deps_toml.py | 18-267 |
| FlextInfraModelsDepsToolSettings | Class | flext-infra/src/flext_infra/_models/deps_tool_config.py | 18-261 |
| FlextInfraModelsDepsToolConfigLinters | Class | flext-infra/src/flext_infra/_models/deps_tool_config_linters.py | 12-259 |
| FlextInfraModelsDepsToolConfigTypeCheckers | Class | flext-infra/src/flext_infra/_models/deps_tool_config_type_checkers.py | 13-317 |
| FlextInfraModelsDocs | Class | flext-infra/src/flext_infra/_models/docs.py | 13-206 |
| FlextInfraModelsGates | Class | flext-infra/src/flext_infra/_models/gates.py | 12-54 |
| FlextInfraModelsGithub | Class | flext-infra/src/flext_infra/_models/github.py | 13-233 |
| FlextInfraModelsMroScan | Class | flext-infra/src/flext_infra/_models/mro_scan.py | 10-65 |
| FlextInfraModelsRefactor | Class | flext-infra/src/flext_infra/_models/refactor.py | 22-251 |
| FlextInfraModelsRefactorGrep | Class | flext-infra/src/flext_infra/_models/refactor_ast_grep.py | 15-386 |
| FlextInfraModelsRefactorCensus | Class | flext-infra/src/flext_infra/_models/refactor_census.py | 13-178 |
| FlextInfraModelsNamespaceEnforcer | Class | flext-infra/src/flext_infra/_models/refactor_namespace_enforcer.py | 12-742 |
| FlextInfraModelsRefactorViolations | Class | flext-infra/src/flext_infra/_models/refactor_violations.py | 13-296 |
| FlextInfraModelsRelease | Class | flext-infra/src/flext_infra/_models/release.py | 12-89 |
| FlextInfraModelsRope | Class | flext-infra/src/flext_infra/_models/rope.py | 20-382 |
| FlextInfraModelsScan | Class | flext-infra/src/flext_infra/_models/scan.py | 22-94 |
| FlextInfraModelsCore | Class | flext-infra/src/flext_infra/_models/validate.py | 14-211 |
| FlextInfraModelsWorkspace | Class | flext-infra/src/flext_infra/_models/workspace.py | 16-132 |
| FlextInfraModelsCheck | Class | flext-infra/src/flext_infra/_models/check.py | 16-377 |
| FlextInfraModelsCodegen | Class | flext-infra/src/flext_infra/_models/codegen.py | 18-627 |

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Incoming

- `flext-infra/src/flext_infra/models.py` (17 edge(s))
- `flext-infra/src/flext_infra/_models/refactor.py` (5 edge(s))
- `flext-infra/src/flext_infra/_models/deps.py` (3 edge(s))
- `flext-infra/src/flext_infra/_models/deps_tool_config.py` (3 edge(s))
- `flext-infra/src/flext_infra/_models/codegen.py` (2 edge(s))
- `flext-infra/src/flext_infra/_models/refactor_ast_grep.py` (2 edge(s))
- `flext-infra/src/flext_infra/_models/base.py` (1 edge(s))
- `flext-infra/src/flext_infra/_models/basemk.py` (1 edge(s))
- `flext-infra/src/flext_infra/_models/census.py` (1 edge(s))
- `flext-infra/src/flext_infra/_models/check.py` (1 edge(s))
- `flext-infra/src/flext_infra/_models/codegen_render.py` (1 edge(s))
- `flext-infra/src/flext_infra/_models/deps_toml.py` (1 edge(s))
- `flext-infra/src/flext_infra/_models/deps_tool_config_linters.py` (1 edge(s))
- `flext-infra/src/flext_infra/_models/deps_tool_config_type_checkers.py` (1 edge(s))
- `flext-infra/src/flext_infra/_models/docs.py` (1 edge(s))
