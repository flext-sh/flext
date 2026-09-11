<!-- TOC START -->
- [Purpose](#purpose)
- [Significant Communities](#significant-communities)
- [Regeneration](#regeneration)
- [See Also](#see-also)
<!-- TOC END -->

# Code Communities

Structural communities of the FLEXT workspace, detected from the code knowledge graph
(call/import graph, Leiden community detection). Each page lists the member symbols of
one cohesive cluster — use it to navigate the architecture by responsibility instead of
by directory layout.

<!-- AUTO-GENERATED — DO NOT EDIT MANUALLY. Regenerate with: code-review-graph update && code-review-graph wiki -->
<!-- Source: CRG graph at .code-review-graph/graph.db → docs/architecture/communities/ -->

## Purpose

Code communities are discovered by running the Leiden community-detection algorithm
over the FLEXT call/import graph (maintained by `code-review-graph`). Each community is
a cohesive cluster of symbols that tend to be used together. The wiki pages below
list the member symbols, their locations, and line ranges so readers can navigate
the codebase by architectural responsibility instead of by directory layout.

Only significant non-test communities (>= 50 nodes) are published here. Smaller clusters
appear in the full CRG wiki at `.code-review-graph/wiki/`.

## Significant Communities

<!-- AUTO-GENERATED TABLE: commence -->

| Community | Size | Cohesion | Language | Page |
| --- | --- | --- | --- | --- |
| codegen-infra | 688 | 0.1638 | python | [codegen-infra.md](codegen-infra.md) |
| utilities-flext | 590 | 0.1590 | python | [utilities-flext.md](utilities-flext.md) |
| codegen-infra-flext | 345 | 0.2092 | python | [codegen-infra-flext.md](codegen-infra-flext.md) |
| services-server | 317 | 0.2806 | python | [services-server.md](services-server.md) |
| detectors-infra | 302 | 0.2328 | python | [detectors-infra.md](detectors-infra.md) |
| gates-check | 290 | 0.2685 | python | [gates-check.md](gates-check.md) |
| phases-apply | 240 | 0.3093 | python | [phases-apply.md](phases-apply.md) |
| utilities-extract | 211 | 0.2299 | python | [utilities-extract.md](utilities-extract.md) |
| utilities-files | 206 | 0.0579 | python | [utilities-files.md](utilities-files.md) |
| flext-core-container | 203 | 0.3788 | python | [flext-core-container.md](flext-core-container.md) |
| services-oracle | 198 | 0.1587 | python | [services-oracle.md](services-oracle.md) |
| transformers-import | 169 | 0.3028 | python | [transformers-import.md](transformers-import.md) |
| services-context | 169 | 0.4026 | python | [services-context.md](services-context.md) |
| matchers-validate | 155 | 0.1655 | python | [matchers-validate.md](matchers-validate.md) |
| flext-tap-oracle-wms-tap | 129 | 0.3043 | python | [flext-tap-oracle-wms-tap.md](flext-tap-oracle-wms-tap.md) |
| protocols-flext | 114 | 0.3371 | python | [protocols-flext.md](protocols-flext.md) |
| utilities-source | 114 | 0.3364 | python | [utilities-source.md](utilities-source.md) |
| tests-deps | 110 | 0.1808 | python | [tests-deps.md](tests-deps.md) |
| base-attribute | 109 | 0.3482 | python | [base-attribute.md](base-attribute.md) |
| services-integration | 106 | 0.3841 | python | [services-integration.md](services-integration.md) |
| flext-meltano-pipeline | 102 | 0.3087 | python | [flext-meltano-pipeline.md](flext-meltano-pipeline.md) |
| unit-wms | 98 | 0.1713 | python | [unit-wms.md](unit-wms.md) |
| services-ldif | 93 | 0.2896 | python | [services-ldif.md](services-ldif.md) |
| oud-acl | 93 | 0.2475 | python | [oud-acl.md](oud-acl.md) |
| unit-handler | 92 | 0.3545 | python | [unit-handler.md](unit-handler.md) |
| flext-tests-compose | 92 | 0.1169 | python | [flext-tests-compose.md](flext-tests-compose.md) |
| ldap3-entry | 91 | 0.4134 | python | [ldap3-entry.md](ldap3-entry.md) |
| utilities-dn | 89 | 0.2722 | python | [utilities-dn.md](utilities-dn.md) |
| utilities-plugin | 88 | 0.2505 | python | [utilities-plugin.md](utilities-plugin.md) |
| utilities-output | 86 | 0.0873 | python | [utilities-output.md](utilities-output.md) |
| utilities-oracle | 78 | 0.2665 | python | [utilities-oracle.md](utilities-oracle.md) |
| services-file | 77 | 0.1818 | python | [services-file.md](services-file.md) |
| services-server-grpc | 76 | 0.3352 | python | [services-server-grpc.md](services-server-grpc.md) |
| models-validate | 75 | 0.3223 | python | [models-validate.md](models-validate.md) |
| models-op | 74 | 0.0276 | python | [models-op.md](models-op.md) |
| json-json | 71 | 0.0188 | python | [json-json.md](json-json.md) |
| utilities-filter | 71 | 0.0776 | python | [utilities-filter.md](utilities-filter.md) |
| services-display | 70 | 0.0686 | python | [services-display.md](services-display.md) |
| services-project | 70 | 0.1734 | python | [services-project.md](services-project.md) |
| utilities-str | 69 | 0.0194 | python | [utilities-str.md](utilities-str.md) |
| unit-flext | 65 | 0.4016 | python | [unit-flext.md](unit-flext.md) |
| flext-db-oracle-operation | 65 | 0.3415 | python | [flext-db-oracle-operation.md](flext-db-oracle-operation.md) |
| flext-target-ldif-record | 64 | 0.3556 | python | [flext-target-ldif-record.md](flext-target-ldif-record.md) |
| toml-parts-toml | 61 | 0.0191 | python | [toml-parts-toml.md](toml-parts-toml.md) |
| servers-relaxed | 61 | 0.2354 | python | [servers-relaxed.md](servers-relaxed.md) |
| flext-core-dir | 60 | 0.2128 | python | [flext-core-dir.md](flext-core-dir.md) |
| utilities-oracle-engine | 60 | 0.0405 | python | [utilities-oracle-engine.md](utilities-oracle-engine.md) |
| check-project | 57 | 0.3089 | python | [check-project.md](check-project.md) |
| providers-validate | 56 | 0.3963 | python | [providers-validate.md](providers-validate.md) |
| models-config | 55 | 0.0785 | python | [models-config.md](models-config.md) |

<!-- AUTO-GENERATED TABLE: end -->

## Regeneration

From the workspace root:

```bash
code-review-graph update && code-review-graph wiki
```

The CRG graph is built by `code-review-graph build` and kept in sync incrementally
by `code-review-graph watch` (running as a background daemon). Community pages are
emitted to `.code-review-graph/wiki/` and copied into this directory during
`make gen`.

## See Also

- [Architecture Overview](README.md)
- [Code Communities Index](index.md)
- [Documentation Knowledge Index](../knowledge-index.md)
- [API Reference Overview](../../api-reference/generated/overview.md)
