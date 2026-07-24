# Code Communities

Structural communities of the FLEXT workspace, detected from the code knowledge graph
(call/import graph, Leiden community detection). Each page lists the member symbols of
one cohesive cluster — use it to navigate the architecture by responsibility instead of
by directory layout.

Only significant non-test communities (>= 25 nodes) are published. Test-support clusters
are excluded as navigation noise.

Regenerate from the workspace root:

```bash
code-review-graph update && code-review-graph wiki
```

| Community | Size | Link |
| --- | --- | --- |
| utilities-flext | 3956 | [utilities-flext.md](utilities-flext.md) |
| protocols-plugin | 1715 | [protocols-plugin.md](protocols-plugin.md) |
| check-flext | 3 | [check-flext.md](check-flext.md) |
| refactor-census | 569 | [refactor-census.md](refactor-census.md) |
| services-flext | 545 | [services-flext.md](services-flext.md) |
| integration-parse | 314 | [integration-parse.md](integration-parse.md) |
| api-cases-auth | 308 | [api-cases-auth.md](api-cases-auth.md) |
| deps-infra | 289 | [deps-infra.md](deps-infra.md) |
| models-target | 114 | [models-target.md](models-target.md) |
| servers-acl | 94 | [servers-acl.md](servers-acl.md) |
| services-server | 41 | [services-server.md](services-server.md) |
| refactor-import | 34 | [refactor-import.md](refactor-import.md) |
| protocols-connect | 31 | [protocols-connect.md](protocols-connect.md) |
| examples-error | 30 | [examples-error.md](examples-error.md) |
| utilities-visit | 29 | [utilities-visit.md](utilities-visit.md) |
| result-parts-error | 28 | [result-parts-error.md](result-parts-error.md) |
| models-infra | 27 | [models-infra.md](models-infra.md) |
| integration-user | 25 | [integration-user.md](integration-user.md) |
