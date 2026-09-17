<!-- AUTO-GENERATED — DO NOT EDIT MANUALLY. Source: code-review-graph → docs/architecture/crg-reports/large-functions.md -->
<!-- Run `make docs` to regenerate. -->

# CRG Large Functions

<!-- TOC START -->

- [Summary](#summary)
- [Total Found](#total-found)
- [Min Lines](#min-lines)
- [Results](#results)
- [Raw Output](#raw-output)

<!-- TOC END -->

## Summary

Found 50 node(s) with >= 100 lines (kind=Function):
401 lines | Function | **mise_bootstrap (flext-api/bin/mise:4)
401 lines | Function |**mise_bootstrap (flext-auth/bin/mise:4)
401 lines | Function | **mise_bootstrap (flext-cli/bin/mise:4)
401 lines | Function |**mise_bootstrap (flext-core/bin/mise:4)
401 lines | Function | **mise_bootstrap (flext-db-oracle/bin/mise:4)
401 lines | Function |**mise_bootstrap (flext-dbt-ldap/bin/mise:4)
401 lines | Function | **mise_bootstrap (flext-dbt-ldif/bin/mise:4)
401 lines | Function |**mise_bootstrap (flext-dbt-oracle/bin/mise:4)
401 lines | Function | **mise_bootstrap (flext-dbt-oracle-wms/bin/mise:4)
401 lines | Function |**mise_bootstrap (flext-grpc/bin/mise:4)
... and 40 more

## Total Found

50

## Min Lines

100

## Results

- \_\_mise_bootstrap (`~/flext/flext-api/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-auth/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-cli/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-core/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-db-oracle/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-dbt-ldap/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-dbt-ldif/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-dbt-oracle/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-dbt-oracle-wms/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-grpc/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-infra/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-infra/src/flext_infra/templates/bootstrap/mise`)
- \_\_mise_bootstrap (`~/flext/flext-ldap/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-ldif/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-meltano/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-observability/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-oracle-oic/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-oracle-wms/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-plugin/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-quality/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-tap-ldap/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-tap-ldif/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-tap-oracle/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-tap-oracle-oic/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-tap-oracle-wms/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-target-ldap/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-target-ldif/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-target-oracle/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-target-oracle-oic/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-target-oracle-wms/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-tests/bin/mise`)
- \_\_mise_bootstrap (`~/flext/flext-web/bin/mise`)
- install (`~/flext/flext-api/bin/mise`)
- install (`~/flext/flext-auth/bin/mise`)
- install (`~/flext/flext-cli/bin/mise`)
- install (`~/flext/flext-core/bin/mise`)
- install (`~/flext/flext-db-oracle/bin/mise`)
- install (`~/flext/flext-dbt-ldap/bin/mise`)
- install (`~/flext/flext-dbt-ldif/bin/mise`)
- install (`~/flext/flext-dbt-oracle/bin/mise`)
- install (`~/flext/flext-dbt-oracle-wms/bin/mise`)
- install (`~/flext/flext-grpc/bin/mise`)
- install (`~/flext/flext-infra/bin/mise`)
- install (`~/flext/flext-infra/src/flext_infra/templates/bootstrap/mise`)
- install (`~/flext/flext-ldap/bin/mise`)
- install (`~/flext/flext-ldif/bin/mise`)
- install (`~/flext/flext-meltano/bin/mise`)
- install (`~/flext/flext-observability/bin/mise`)
- install (`~/flext/flext-oracle-oic/bin/mise`)
- install (`~/flext/flext-oracle-wms/bin/mise`)

## Raw Output

<details>

```json
{
  "status": "ok",
  "summary": "Found 50 node(s) with >= 100 lines (kind=Function):\n   401 lines | Function | __mise_bootstrap (flext-api/bin/mise:4)\n   401 lines | Function | __mise_bootstrap (flext-auth/bin/mise:4)\n   401 lines | Function | __mise_bootstrap (flext-cli/bin/mise:4)\n   401 lines | Function | __mise_bootstrap (flext-core/bin/mise:4)\n   401 lines | Function | __mise_bootstrap (flext-db-oracle/bin/mise:4)\n   401 lines | Function | __mise_bootstrap (flext-dbt-ldap/bin/mise:4)\n   401 lines | Function | __mise_bootstrap (flext-dbt-ldif/bin/mise:4)\n   401 lines | Function | __mise_bootstrap (flext-dbt-oracle/bin/mise:4)\n   401 lines | Function | __mise_bootstrap (flext-dbt-oracle-wms/bin/mise:4)\n   401 lines | Function | __mise_bootstrap (flext-grpc/bin/mise:4)\n  ... and 40 more",
  "total_found": 50,
  "min_lines": 100,
  "results": [
    {
      "id": 66933,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-api/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-api/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-api/bin/mise"
    },
    {
      "id": 67320,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-auth/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-auth/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-auth/bin/mise"
    },
    {
      "id": 68096,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-cli/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-cli/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-cli/bin/mise"
    },
    {
      "id": 71429,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-core/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-core/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-core/bin/mise"
    },
    {
      "id": 76820,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-db-oracle/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-db-oracle/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-db-oracle/bin/mise"
    },
    {
      "id": 77707,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-dbt-ldap/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-dbt-ldap/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-dbt-ldap/bin/mise"
    },
    {
      "id": 78010,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-dbt-ldif/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-dbt-ldif/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-dbt-ldif/bin/mise"
    },
    {
      "id": 78460,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-dbt-oracle/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-dbt-oracle/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-dbt-oracle/bin/mise"
    },
    {
      "id": 78659,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-dbt-oracle-wms/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-dbt-oracle-wms/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-dbt-oracle-wms/bin/mise"
    },
    {
      "id": 78885,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-grpc/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-grpc/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-grpc/bin/mise"
    },
    {
      "id": 79504,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-infra/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-infra/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-infra/bin/mise"
    },
    {
      "id": 83887,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-infra/src/flext_infra/templates/bootstrap/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-infra/src/flext_infra/templates/bootstrap/mise",
      "line_start": 5,
      "line_end": 405,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-infra/src/flext_infra/templates/bootstrap/mise"
    },
    {
      "id": 87918,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-ldap/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-ldap/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-ldap/bin/mise"
    },
    {
      "id": 88681,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-ldif/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-ldif/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-ldif/bin/mise"
    },
    {
      "id": 91554,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-meltano/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-meltano/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-meltano/bin/mise"
    },
    {
      "id": 92757,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-observability/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-observability/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-observability/bin/mise"
    },
    {
      "id": 93210,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-oracle-oic/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-oracle-oic/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-oracle-oic/bin/mise"
    },
    {
      "id": 93594,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-oracle-wms/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-oracle-wms/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-oracle-wms/bin/mise"
    },
    {
      "id": 94213,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-plugin/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-plugin/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-plugin/bin/mise"
    },
    {
      "id": 94780,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-quality/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-quality/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-quality/bin/mise"
    },
    {
      "id": 95678,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-tap-ldap/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-tap-ldap/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-tap-ldap/bin/mise"
    },
    {
      "id": 95819,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-tap-ldif/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-tap-ldif/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-tap-ldif/bin/mise"
    },
    {
      "id": 95990,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-tap-oracle/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-tap-oracle/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-tap-oracle/bin/mise"
    },
    {
      "id": 96142,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-tap-oracle-oic/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-tap-oracle-oic/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-tap-oracle-oic/bin/mise"
    },
    {
      "id": 96422,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-tap-oracle-wms/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-tap-oracle-wms/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-tap-oracle-wms/bin/mise"
    },
    {
      "id": 96697,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-target-ldap/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-target-ldap/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-target-ldap/bin/mise"
    },
    {
      "id": 96970,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-target-ldif/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-target-ldif/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-target-ldif/bin/mise"
    },
    {
      "id": 97189,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-target-oracle/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-target-oracle/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-target-oracle/bin/mise"
    },
    {
      "id": 97599,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-target-oracle-oic/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-target-oracle-oic/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-target-oracle-oic/bin/mise"
    },
    {
      "id": 97794,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-target-oracle-wms/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-target-oracle-wms/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-target-oracle-wms/bin/mise"
    },
    {
      "id": 98176,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-tests/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-tests/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-tests/bin/mise"
    },
    {
      "id": 99529,
      "kind": "Function",
      "name": "__mise_bootstrap",
      "qualified_name": "~/flext/flext-web/bin/mise::__mise_bootstrap",
      "file_path": "~/flext/flext-web/bin/mise",
      "line_start": 4,
      "line_end": 404,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 401,
      "relative_path": "flext-web/bin/mise"
    },
    {
      "id": 66934,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-api/bin/mise::install",
      "file_path": "~/flext/flext-api/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-api/bin/mise"
    },
    {
      "id": 67321,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-auth/bin/mise::install",
      "file_path": "~/flext/flext-auth/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-auth/bin/mise"
    },
    {
      "id": 68097,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-cli/bin/mise::install",
      "file_path": "~/flext/flext-cli/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-cli/bin/mise"
    },
    {
      "id": 71430,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-core/bin/mise::install",
      "file_path": "~/flext/flext-core/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-core/bin/mise"
    },
    {
      "id": 76821,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-db-oracle/bin/mise::install",
      "file_path": "~/flext/flext-db-oracle/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-db-oracle/bin/mise"
    },
    {
      "id": 77708,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-dbt-ldap/bin/mise::install",
      "file_path": "~/flext/flext-dbt-ldap/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-dbt-ldap/bin/mise"
    },
    {
      "id": 78011,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-dbt-ldif/bin/mise::install",
      "file_path": "~/flext/flext-dbt-ldif/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-dbt-ldif/bin/mise"
    },
    {
      "id": 78461,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-dbt-oracle/bin/mise::install",
      "file_path": "~/flext/flext-dbt-oracle/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-dbt-oracle/bin/mise"
    },
    {
      "id": 78660,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-dbt-oracle-wms/bin/mise::install",
      "file_path": "~/flext/flext-dbt-oracle-wms/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-dbt-oracle-wms/bin/mise"
    },
    {
      "id": 78886,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-grpc/bin/mise::install",
      "file_path": "~/flext/flext-grpc/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-grpc/bin/mise"
    },
    {
      "id": 79505,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-infra/bin/mise::install",
      "file_path": "~/flext/flext-infra/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-infra/bin/mise"
    },
    {
      "id": 83888,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-infra/src/flext_infra/templates/bootstrap/mise::install",
      "file_path": "~/flext/flext-infra/src/flext_infra/templates/bootstrap/mise",
      "line_start": 28,
      "line_end": 402,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-infra/src/flext_infra/templates/bootstrap/mise"
    },
    {
      "id": 87919,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-ldap/bin/mise::install",
      "file_path": "~/flext/flext-ldap/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-ldap/bin/mise"
    },
    {
      "id": 88682,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-ldif/bin/mise::install",
      "file_path": "~/flext/flext-ldif/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-ldif/bin/mise"
    },
    {
      "id": 91555,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-meltano/bin/mise::install",
      "file_path": "~/flext/flext-meltano/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-meltano/bin/mise"
    },
    {
      "id": 92758,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-observability/bin/mise::install",
      "file_path": "~/flext/flext-observability/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-observability/bin/mise"
    },
    {
      "id": 93211,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-oracle-oic/bin/mise::install",
      "file_path": "~/flext/flext-oracle-oic/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-oracle-oic/bin/mise"
    },
    {
      "id": 93595,
      "kind": "Function",
      "name": "install",
      "qualified_name": "~/flext/flext-oracle-wms/bin/mise::install",
      "file_path": "~/flext/flext-oracle-wms/bin/mise",
      "line_start": 27,
      "line_end": 401,
      "language": "bash",
      "parent_name": null,
      "is_test": false,
      "line_count": 375,
      "relative_path": "flext-oracle-wms/bin/mise"
    }
  ]
}
```

</details>
