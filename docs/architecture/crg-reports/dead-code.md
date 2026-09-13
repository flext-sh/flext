<!-- AUTO-GENERATED — DO NOT EDIT MANUALLY. Source: code-review-graph → docs/architecture/crg-reports/dead-code.md -->
<!-- Run `make docs` to regenerate. -->

# CRG Dead Code

<!-- TOC START -->
- [Summary](#summary)
- [Findings](#findings)
- [Raw Output](#raw-output)
<!-- TOC END -->

## Summary

**Total items: 137**

## Findings

- employees (`/home/marlonsc/flext/docker/oracle-db/init.sql`:8)
- departments (`/home/marlonsc/flext/docker/oracle-db/init.sql`:16)
- jobs (`/home/marlonsc/flext/docker/oracle-db/init.sql`:21)
- FlextApiVersion (`/home/marlonsc/flext/flext-api/src/flext_api/__version__.py`:19)
- FlextAuthVersion (`/home/marlonsc/flext/flext-auth/src/flext_auth/__version__.py`:19)
- _KerberosAuthManager (`/home/marlonsc/flext/flext-auth/src/flext_auth/providers/kerberos_support.py`:66)
- FlextCliVersion (`/home/marlonsc/flext/flext-cli/src/flext_cli/__version__.py`:19)
- CliValidationError (`/home/marlonsc/flext/flext-cli/src/flext_cli/_constants/exceptions.py`:33)
- FlextCliUtilitiesCli (`/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_cli_namespace.py`:40)
- _IoCounters (`/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_runtime_windows_job_start.py`:28)
- _BasicLimitInformation (`/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_runtime_windows_job_start.py`:38)
- FlextCliUtilitiesXlsxFormulaCodec (`/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_xlxx/xlsx_formula_codec.py`:9)
- ScriptsFlextConstants (`/home/marlonsc/flext/flext-core/scripts/constants.py`:9)
- ScriptsFlextModels (`/home/marlonsc/flext/flext-core/scripts/models.py`:9)
- ScriptsFlextTypes (`/home/marlonsc/flext/flext-core/scripts/typings.py`:8)
- ScriptsFlextUtilities (`/home/marlonsc/flext/flext-core/scripts/utilities.py`:9)
- FlextConstantsEnforcementCatalogInfraRowsExtended (`/home/marlonsc/flext/flext-core/src/flext_core/_constants/_enforcement_catalog_rows_parts/flextconstantsenforcementcatalogrows_part_05.py`:12)
- FlextSmellViolation (`/home/marlonsc/flext/flext-core/src/flext_core/_constants/enforcement.py`:43)
- FlextDecorators (`/home/marlonsc/flext/flext-core/src/flext_core/_decorators/__init__.py`:12)
- IdentifiableMixin (`/home/marlonsc/flext/flext-core/src/flext_core/_models/_base_parts/flextmodelsbase_part_02.py`:153)
- VersionableMixin (`/home/marlonsc/flext/flext-core/src/flext_core/_models/_base_parts/flextmodelsbase_part_03.py`:65)
- FlextResultBehavior (`/home/marlonsc/flext/flext-core/src/flext_core/_result/behavior.py`:10)
- FlextResultUnwrap (`/home/marlonsc/flext/flext-core/src/flext_core/_result/unwrap.py`:15)
- DependencyIntegration (`/home/marlonsc/flext/flext-core/src/flext_core/_runtime/_dependency.py`:15)
- DynamicContainerWithConfig (`/home/marlonsc/flext/flext-core/src/flext_core/_runtime/_dependency_types.py`:26)
- BridgeContainer (`/home/marlonsc/flext/flext-core/src/flext_core/_runtime/_dependency_types.py`:31)
- FlextTypesAnnotateds (`/home/marlonsc/flext/flext-core/src/flext_core/_typings/annotateds.py`:16)
- FlextTypesPydantic (`/home/marlonsc/flext/flext-core/src/flext_core/_typings/pydantic.py`:23)
- FlextUtilitiesBeartypeAliasVisitor (`/home/marlonsc/flext/flext-core/src/flext_core/_utilities/_beartype/_alias_visitor.py`:16)
- FlextUtilitiesBeartypeLibraryVisitor (`/home/marlonsc/flext/flext-core/src/flext_core/_utilities/_beartype/_library_visitor.py`:13)
- FlextModels (`/home/marlonsc/flext/flext-core/src/flext_core/models.py`:38)
- FlextUtilities (`/home/marlonsc/flext/flext-core/src/flext_core/utilities.py`:45)
- FlextDbOracleVersion (`/home/marlonsc/flext/flext-db-oracle/src/flext_db_oracle/__version__.py`:19)
- StrictIntValue (`/home/marlonsc/flext/flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py`:43)
- CountValue (`/home/marlonsc/flext/flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py`:48)
- FlextDbtLdapVersion (`/home/marlonsc/flext/flext-dbt-ldap/src/flext_dbt_ldap/__version__.py`:19)
- FlextDbtLdifVersion (`/home/marlonsc/flext/flext-dbt-ldif/src/flext_dbt_ldif/__version__.py`:19)
- FlextDbtOracleVersion (`/home/marlonsc/flext/flext-dbt-oracle/src/flext_dbt_oracle/__version__.py`:19)
- ModelBuilder (`/home/marlonsc/flext/flext-dbt-oracle/src/flext_dbt_oracle/utilities.py`:75)
- FlextDbtOracleWmsVersion (`/home/marlonsc/flext/flext-dbt-oracle-wms/src/flext_dbt_oracle_wms/__version__.py`:19)
- ModelBuilder (`/home/marlonsc/flext/flext-dbt-oracle-wms/src/flext_dbt_oracle_wms/utilities.py`:128)
- FlextGrpcVersion (`/home/marlonsc/flext/flext-grpc/src/flext_grpc/__version__.py`:19)
- FlextInfraVersion (`/home/marlonsc/flext/flext-infra/src/flext_infra/__version__.py`:19)
- CensusPatterns (`/home/marlonsc/flext/flext-infra/src/flext_infra/_constants/census.py`:15)
- ReadMixin (`/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py`:73)
- WriteMixin (`/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py`:102)
- VersionTagMixin (`/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py`:153)
- AbsoluteFilePathTextMixin (`/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py`:166)
- RequiredNonNegativeLineMixin (`/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py`:176)
- NonNegativeLineMixin (`/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py`:181)
- ... and 87 more

## Raw Output

<details>

```json
[
  {
    "name": "employees",
    "qualified_name": "/home/marlonsc/flext/docker/oracle-db/init.sql::employees",
    "kind": "Class",
    "file": "/home/marlonsc/flext/docker/oracle-db/init.sql",
    "file_path": "/home/marlonsc/flext/docker/oracle-db/init.sql",
    "relative_path": "docker/oracle-db/init.sql",
    "line": 8,
    "language": "sql"
  },
  {
    "name": "departments",
    "qualified_name": "/home/marlonsc/flext/docker/oracle-db/init.sql::departments",
    "kind": "Class",
    "file": "/home/marlonsc/flext/docker/oracle-db/init.sql",
    "file_path": "/home/marlonsc/flext/docker/oracle-db/init.sql",
    "relative_path": "docker/oracle-db/init.sql",
    "line": 16,
    "language": "sql"
  },
  {
    "name": "jobs",
    "qualified_name": "/home/marlonsc/flext/docker/oracle-db/init.sql::jobs",
    "kind": "Class",
    "file": "/home/marlonsc/flext/docker/oracle-db/init.sql",
    "file_path": "/home/marlonsc/flext/docker/oracle-db/init.sql",
    "relative_path": "docker/oracle-db/init.sql",
    "line": 21,
    "language": "sql"
  },
  {
    "name": "FlextApiVersion",
    "qualified_name": "/home/marlonsc/flext/flext-api/src/flext_api/__version__.py::FlextApiVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-api/src/flext_api/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-api/src/flext_api/__version__.py",
    "relative_path": "flext-api/src/flext_api/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "FlextAuthVersion",
    "qualified_name": "/home/marlonsc/flext/flext-auth/src/flext_auth/__version__.py::FlextAuthVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-auth/src/flext_auth/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-auth/src/flext_auth/__version__.py",
    "relative_path": "flext-auth/src/flext_auth/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "_KerberosAuthManager",
    "qualified_name": "/home/marlonsc/flext/flext-auth/src/flext_auth/providers/kerberos_support.py::FlextAuthKerberosSupport._KerberosAuthManager",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-auth/src/flext_auth/providers/kerberos_support.py",
    "file_path": "/home/marlonsc/flext/flext-auth/src/flext_auth/providers/kerberos_support.py",
    "relative_path": "flext-auth/src/flext_auth/providers/kerberos_support.py",
    "line": 66,
    "language": "python"
  },
  {
    "name": "FlextCliVersion",
    "qualified_name": "/home/marlonsc/flext/flext-cli/src/flext_cli/__version__.py::FlextCliVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-cli/src/flext_cli/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-cli/src/flext_cli/__version__.py",
    "relative_path": "flext-cli/src/flext_cli/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "CliValidationError",
    "qualified_name": "/home/marlonsc/flext/flext-cli/src/flext_cli/_constants/exceptions.py::CliValidationError",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-cli/src/flext_cli/_constants/exceptions.py",
    "file_path": "/home/marlonsc/flext/flext-cli/src/flext_cli/_constants/exceptions.py",
    "relative_path": "flext-cli/src/flext_cli/_constants/exceptions.py",
    "line": 33,
    "language": "python"
  },
  {
    "name": "FlextCliUtilitiesCli",
    "qualified_name": "/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_cli_namespace.py::FlextCliUtilitiesCli",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_cli_namespace.py",
    "file_path": "/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_cli_namespace.py",
    "relative_path": "flext-cli/src/flext_cli/_utilities/_cli_namespace.py",
    "line": 40,
    "language": "python"
  },
  {
    "name": "_IoCounters",
    "qualified_name": "/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_runtime_windows_job_start.py::FlextCliUtilitiesRuntimeWindowsJobStartMixin._IoCounters",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_runtime_windows_job_start.py",
    "file_path": "/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_runtime_windows_job_start.py",
    "relative_path": "flext-cli/src/flext_cli/_utilities/_runtime_windows_job_start.py",
    "line": 28,
    "language": "python"
  },
  {
    "name": "_BasicLimitInformation",
    "qualified_name": "/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_runtime_windows_job_start.py::FlextCliUtilitiesRuntimeWindowsJobStartMixin._BasicLimitInformation",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_runtime_windows_job_start.py",
    "file_path": "/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_runtime_windows_job_start.py",
    "relative_path": "flext-cli/src/flext_cli/_utilities/_runtime_windows_job_start.py",
    "line": 38,
    "language": "python"
  },
  {
    "name": "FlextCliUtilitiesXlsxFormulaCodec",
    "qualified_name": "/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_xlxx/xlsx_formula_codec.py::FlextCliUtilitiesXlsxFormulaCodec",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_xlxx/xlsx_formula_codec.py",
    "file_path": "/home/marlonsc/flext/flext-cli/src/flext_cli/_utilities/_xlxx/xlsx_formula_codec.py",
    "relative_path": "flext-cli/src/flext_cli/_utilities/_xlxx/xlsx_formula_codec.py",
    "line": 9,
    "language": "python"
  },
  {
    "name": "ScriptsFlextConstants",
    "qualified_name": "/home/marlonsc/flext/flext-core/scripts/constants.py::ScriptsFlextConstants",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/scripts/constants.py",
    "file_path": "/home/marlonsc/flext/flext-core/scripts/constants.py",
    "relative_path": "flext-core/scripts/constants.py",
    "line": 9,
    "language": "python"
  },
  {
    "name": "ScriptsFlextModels",
    "qualified_name": "/home/marlonsc/flext/flext-core/scripts/models.py::ScriptsFlextModels",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/scripts/models.py",
    "file_path": "/home/marlonsc/flext/flext-core/scripts/models.py",
    "relative_path": "flext-core/scripts/models.py",
    "line": 9,
    "language": "python"
  },
  {
    "name": "ScriptsFlextTypes",
    "qualified_name": "/home/marlonsc/flext/flext-core/scripts/typings.py::ScriptsFlextTypes",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/scripts/typings.py",
    "file_path": "/home/marlonsc/flext/flext-core/scripts/typings.py",
    "relative_path": "flext-core/scripts/typings.py",
    "line": 8,
    "language": "python"
  },
  {
    "name": "ScriptsFlextUtilities",
    "qualified_name": "/home/marlonsc/flext/flext-core/scripts/utilities.py::ScriptsFlextUtilities",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/scripts/utilities.py",
    "file_path": "/home/marlonsc/flext/flext-core/scripts/utilities.py",
    "relative_path": "flext-core/scripts/utilities.py",
    "line": 9,
    "language": "python"
  },
  {
    "name": "FlextConstantsEnforcementCatalogInfraRowsExtended",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/_constants/_enforcement_catalog_rows_parts/flextconstantsenforcementcatalogrows_part_05.py::FlextConstantsEnforcementCatalogInfraRowsExtended",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/_constants/_enforcement_catalog_rows_parts/flextconstantsenforcementcatalogrows_part_05.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/_constants/_enforcement_catalog_rows_parts/flextconstantsenforcementcatalogrows_part_05.py",
    "relative_path": "flext-core/src/flext_core/_constants/_enforcement_catalog_rows_parts/flextconstantsenforcementcatalogrows_part_05.py",
    "line": 12,
    "language": "python"
  },
  {
    "name": "FlextSmellViolation",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/_constants/enforcement.py::FlextSmellViolation",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/_constants/enforcement.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/_constants/enforcement.py",
    "relative_path": "flext-core/src/flext_core/_constants/enforcement.py",
    "line": 43,
    "language": "python"
  },
  {
    "name": "FlextDecorators",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/_decorators/__init__.py::FlextDecorators",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/_decorators/__init__.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/_decorators/__init__.py",
    "relative_path": "flext-core/src/flext_core/_decorators/__init__.py",
    "line": 12,
    "language": "python"
  },
  {
    "name": "IdentifiableMixin",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/_models/_base_parts/flextmodelsbase_part_02.py::FlextModelsBase.IdentifiableMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/_models/_base_parts/flextmodelsbase_part_02.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/_models/_base_parts/flextmodelsbase_part_02.py",
    "relative_path": "flext-core/src/flext_core/_models/_base_parts/flextmodelsbase_part_02.py",
    "line": 153,
    "language": "python"
  },
  {
    "name": "VersionableMixin",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/_models/_base_parts/flextmodelsbase_part_03.py::FlextModelsBase.VersionableMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/_models/_base_parts/flextmodelsbase_part_03.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/_models/_base_parts/flextmodelsbase_part_03.py",
    "relative_path": "flext-core/src/flext_core/_models/_base_parts/flextmodelsbase_part_03.py",
    "line": 65,
    "language": "python"
  },
  {
    "name": "FlextResultBehavior",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/_result/behavior.py::FlextResultBehavior",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/_result/behavior.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/_result/behavior.py",
    "relative_path": "flext-core/src/flext_core/_result/behavior.py",
    "line": 10,
    "language": "python"
  },
  {
    "name": "FlextResultUnwrap",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/_result/unwrap.py::FlextResultUnwrap",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/_result/unwrap.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/_result/unwrap.py",
    "relative_path": "flext-core/src/flext_core/_result/unwrap.py",
    "line": 15,
    "language": "python"
  },
  {
    "name": "DependencyIntegration",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/_runtime/_dependency.py::FlextRuntimeDependencyIntegration.DependencyIntegration",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/_runtime/_dependency.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/_runtime/_dependency.py",
    "relative_path": "flext-core/src/flext_core/_runtime/_dependency.py",
    "line": 15,
    "language": "python"
  },
  {
    "name": "DynamicContainerWithConfig",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/_runtime/_dependency_types.py::FlextRuntimeDependencyTypes.DynamicContainerWithConfig",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/_runtime/_dependency_types.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/_runtime/_dependency_types.py",
    "relative_path": "flext-core/src/flext_core/_runtime/_dependency_types.py",
    "line": 26,
    "language": "python"
  },
  {
    "name": "BridgeContainer",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/_runtime/_dependency_types.py::FlextRuntimeDependencyTypes.BridgeContainer",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/_runtime/_dependency_types.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/_runtime/_dependency_types.py",
    "relative_path": "flext-core/src/flext_core/_runtime/_dependency_types.py",
    "line": 31,
    "language": "python"
  },
  {
    "name": "FlextTypesAnnotateds",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/_typings/annotateds.py::FlextTypesAnnotateds",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/_typings/annotateds.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/_typings/annotateds.py",
    "relative_path": "flext-core/src/flext_core/_typings/annotateds.py",
    "line": 16,
    "language": "python"
  },
  {
    "name": "FlextTypesPydantic",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/_typings/pydantic.py::FlextTypesPydantic",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/_typings/pydantic.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/_typings/pydantic.py",
    "relative_path": "flext-core/src/flext_core/_typings/pydantic.py",
    "line": 23,
    "language": "python"
  },
  {
    "name": "FlextUtilitiesBeartypeAliasVisitor",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/_utilities/_beartype/_alias_visitor.py::FlextUtilitiesBeartypeAliasVisitor",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/_utilities/_beartype/_alias_visitor.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/_utilities/_beartype/_alias_visitor.py",
    "relative_path": "flext-core/src/flext_core/_utilities/_beartype/_alias_visitor.py",
    "line": 16,
    "language": "python"
  },
  {
    "name": "FlextUtilitiesBeartypeLibraryVisitor",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/_utilities/_beartype/_library_visitor.py::FlextUtilitiesBeartypeLibraryVisitor",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/_utilities/_beartype/_library_visitor.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/_utilities/_beartype/_library_visitor.py",
    "relative_path": "flext-core/src/flext_core/_utilities/_beartype/_library_visitor.py",
    "line": 13,
    "language": "python"
  },
  {
    "name": "FlextModels",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/models.py::FlextModels",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/models.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/models.py",
    "relative_path": "flext-core/src/flext_core/models.py",
    "line": 38,
    "language": "python"
  },
  {
    "name": "FlextUtilities",
    "qualified_name": "/home/marlonsc/flext/flext-core/src/flext_core/utilities.py::FlextUtilities",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-core/src/flext_core/utilities.py",
    "file_path": "/home/marlonsc/flext/flext-core/src/flext_core/utilities.py",
    "relative_path": "flext-core/src/flext_core/utilities.py",
    "line": 45,
    "language": "python"
  },
  {
    "name": "FlextDbOracleVersion",
    "qualified_name": "/home/marlonsc/flext/flext-db-oracle/src/flext_db_oracle/__version__.py::FlextDbOracleVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-db-oracle/src/flext_db_oracle/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-db-oracle/src/flext_db_oracle/__version__.py",
    "relative_path": "flext-db-oracle/src/flext_db_oracle/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "StrictIntValue",
    "qualified_name": "/home/marlonsc/flext/flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py::FlextDbOracleUtilitiesDbOracle.StrictIntValue",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py",
    "file_path": "/home/marlonsc/flext/flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py",
    "relative_path": "flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py",
    "line": 43,
    "language": "python"
  },
  {
    "name": "CountValue",
    "qualified_name": "/home/marlonsc/flext/flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py::FlextDbOracleUtilitiesDbOracle.CountValue",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py",
    "file_path": "/home/marlonsc/flext/flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py",
    "relative_path": "flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py",
    "line": 48,
    "language": "python"
  },
  {
    "name": "FlextDbtLdapVersion",
    "qualified_name": "/home/marlonsc/flext/flext-dbt-ldap/src/flext_dbt_ldap/__version__.py::FlextDbtLdapVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-dbt-ldap/src/flext_dbt_ldap/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-dbt-ldap/src/flext_dbt_ldap/__version__.py",
    "relative_path": "flext-dbt-ldap/src/flext_dbt_ldap/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "FlextDbtLdifVersion",
    "qualified_name": "/home/marlonsc/flext/flext-dbt-ldif/src/flext_dbt_ldif/__version__.py::FlextDbtLdifVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-dbt-ldif/src/flext_dbt_ldif/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-dbt-ldif/src/flext_dbt_ldif/__version__.py",
    "relative_path": "flext-dbt-ldif/src/flext_dbt_ldif/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "FlextDbtOracleVersion",
    "qualified_name": "/home/marlonsc/flext/flext-dbt-oracle/src/flext_dbt_oracle/__version__.py::FlextDbtOracleVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-dbt-oracle/src/flext_dbt_oracle/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-dbt-oracle/src/flext_dbt_oracle/__version__.py",
    "relative_path": "flext-dbt-oracle/src/flext_dbt_oracle/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "ModelBuilder",
    "qualified_name": "/home/marlonsc/flext/flext-dbt-oracle/src/flext_dbt_oracle/utilities.py::FlextDbtOracleUtilities.DbtOracle.ModelBuilder",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-dbt-oracle/src/flext_dbt_oracle/utilities.py",
    "file_path": "/home/marlonsc/flext/flext-dbt-oracle/src/flext_dbt_oracle/utilities.py",
    "relative_path": "flext-dbt-oracle/src/flext_dbt_oracle/utilities.py",
    "line": 75,
    "language": "python"
  },
  {
    "name": "FlextDbtOracleWmsVersion",
    "qualified_name": "/home/marlonsc/flext/flext-dbt-oracle-wms/src/flext_dbt_oracle_wms/__version__.py::FlextDbtOracleWmsVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-dbt-oracle-wms/src/flext_dbt_oracle_wms/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-dbt-oracle-wms/src/flext_dbt_oracle_wms/__version__.py",
    "relative_path": "flext-dbt-oracle-wms/src/flext_dbt_oracle_wms/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "ModelBuilder",
    "qualified_name": "/home/marlonsc/flext/flext-dbt-oracle-wms/src/flext_dbt_oracle_wms/utilities.py::FlextDbtOracleWmsUtilities.DbtOracleWms.ModelBuilder",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-dbt-oracle-wms/src/flext_dbt_oracle_wms/utilities.py",
    "file_path": "/home/marlonsc/flext/flext-dbt-oracle-wms/src/flext_dbt_oracle_wms/utilities.py",
    "relative_path": "flext-dbt-oracle-wms/src/flext_dbt_oracle_wms/utilities.py",
    "line": 128,
    "language": "python"
  },
  {
    "name": "FlextGrpcVersion",
    "qualified_name": "/home/marlonsc/flext/flext-grpc/src/flext_grpc/__version__.py::FlextGrpcVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-grpc/src/flext_grpc/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-grpc/src/flext_grpc/__version__.py",
    "relative_path": "flext-grpc/src/flext_grpc/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "FlextInfraVersion",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/__version__.py::FlextInfraVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/__version__.py",
    "relative_path": "flext-infra/src/flext_infra/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "CensusPatterns",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_constants/census.py::FlextInfraConstantsCensus.CensusPatterns",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_constants/census.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_constants/census.py",
    "relative_path": "flext-infra/src/flext_infra/_constants/census.py",
    "line": 15,
    "language": "python"
  },
  {
    "name": "ReadMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.ReadMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 73,
    "language": "python"
  },
  {
    "name": "WriteMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.WriteMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 102,
    "language": "python"
  },
  {
    "name": "VersionTagMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.VersionTagMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 153,
    "language": "python"
  },
  {
    "name": "AbsoluteFilePathTextMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.AbsoluteFilePathTextMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 166,
    "language": "python"
  },
  {
    "name": "RequiredNonNegativeLineMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.RequiredNonNegativeLineMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 176,
    "language": "python"
  },
  {
    "name": "NonNegativeLineMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.NonNegativeLineMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 181,
    "language": "python"
  },
  {
    "name": "NestedClassPathMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.NestedClassPathMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 186,
    "language": "python"
  },
  {
    "name": "FileLineViolationMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.FileLineViolationMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 191,
    "language": "python"
  },
  {
    "name": "CurrentImportMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.CurrentImportMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 194,
    "language": "python"
  },
  {
    "name": "ViolationDetailMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.ViolationDetailMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 201,
    "language": "python"
  },
  {
    "name": "ErrorDetailMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.ErrorDetailMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 206,
    "language": "python"
  },
  {
    "name": "ConfidenceLevelMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.ConfidenceLevelMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 211,
    "language": "python"
  },
  {
    "name": "ProjectNameMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.ProjectNameMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 218,
    "language": "python"
  },
  {
    "name": "ProjectEntryNameMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.ProjectEntryNameMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 223,
    "language": "python"
  },
  {
    "name": "ProjectNameFieldMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.ProjectNameFieldMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 228,
    "language": "python"
  },
  {
    "name": "RepositoryRootPathMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.RepositoryRootPathMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 233,
    "language": "python"
  },
  {
    "name": "CheckpointRefMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.CheckpointRefMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 238,
    "language": "python"
  },
  {
    "name": "ProjectNamesOptionalMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.ProjectNamesOptionalMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 245,
    "language": "python"
  },
  {
    "name": "ProjectNamesListMixin",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py::FlextInfraModelsMixins.ProjectNamesListMixin",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_models/mixins.py",
    "relative_path": "flext-infra/src/flext_infra/_models/mixins.py",
    "line": 252,
    "language": "python"
  },
  {
    "name": "FlextInfraUtilitiesPrivateImportValidation",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/_utilities/private_import_validation.py::FlextInfraUtilitiesPrivateImportValidation",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/_utilities/private_import_validation.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/_utilities/private_import_validation.py",
    "relative_path": "flext-infra/src/flext_infra/_utilities/private_import_validation.py",
    "line": 15,
    "language": "python"
  },
  {
    "name": "FlextInfraProjectSelectionServiceBase",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/base_selection.py::FlextInfraProjectSelectionServiceBase",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/base_selection.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/base_selection.py",
    "relative_path": "flext-infra/src/flext_infra/base_selection.py",
    "line": 11,
    "language": "python"
  },
  {
    "name": "CodegenRoutes",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/services/cli_routes_codegen.py::CodegenRoutes",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/services/cli_routes_codegen.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/services/cli_routes_codegen.py",
    "relative_path": "flext-infra/src/flext_infra/services/cli_routes_codegen.py",
    "line": 32,
    "language": "python"
  },
  {
    "name": "ValidationRoutes",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/services/cli_routes_validate.py::ValidationRoutes",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/services/cli_routes_validate.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/services/cli_routes_validate.py",
    "relative_path": "flext-infra/src/flext_infra/services/cli_routes_validate.py",
    "line": 20,
    "language": "python"
  },
  {
    "name": "WorkspaceRoutes",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/services/cli_routes_workspace.py::WorkspaceRoutes",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/services/cli_routes_workspace.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/services/cli_routes_workspace.py",
    "relative_path": "flext-infra/src/flext_infra/services/cli_routes_workspace.py",
    "line": 21,
    "language": "python"
  },
  {
    "name": "FlextInfraCensusImportDiscoveryVisitor",
    "qualified_name": "/home/marlonsc/flext/flext-infra/src/flext_infra/transformers/census_visitors.py::FlextInfraCensusImportDiscoveryVisitor",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-infra/src/flext_infra/transformers/census_visitors.py",
    "file_path": "/home/marlonsc/flext/flext-infra/src/flext_infra/transformers/census_visitors.py",
    "relative_path": "flext-infra/src/flext_infra/transformers/census_visitors.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "FlextLdapVersion",
    "qualified_name": "/home/marlonsc/flext/flext-ldap/src/flext_ldap/__version__.py::FlextLdapVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-ldap/src/flext_ldap/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-ldap/src/flext_ldap/__version__.py",
    "relative_path": "flext-ldap/src/flext_ldap/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "FlextLdapUtilitiesValidation",
    "qualified_name": "/home/marlonsc/flext/flext-ldap/src/flext_ldap/_utilities/validation.py::FlextLdapUtilitiesValidation",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-ldap/src/flext_ldap/_utilities/validation.py",
    "file_path": "/home/marlonsc/flext/flext-ldap/src/flext_ldap/_utilities/validation.py",
    "relative_path": "flext-ldap/src/flext_ldap/_utilities/validation.py",
    "line": 10,
    "language": "python"
  },
  {
    "name": "SearchExecutor",
    "qualified_name": "/home/marlonsc/flext/flext-ldap/src/flext_ldap/adapters/_ldap3/search_executor.py::SearchExecutor",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-ldap/src/flext_ldap/adapters/_ldap3/search_executor.py",
    "file_path": "/home/marlonsc/flext/flext-ldap/src/flext_ldap/adapters/_ldap3/search_executor.py",
    "relative_path": "flext-ldap/src/flext_ldap/adapters/_ldap3/search_executor.py",
    "line": 15,
    "language": "python"
  },
  {
    "name": "FlextLdapService",
    "qualified_name": "/home/marlonsc/flext/flext-ldap/src/flext_ldap/base.py::FlextLdapService",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-ldap/src/flext_ldap/base.py",
    "file_path": "/home/marlonsc/flext/flext-ldap/src/flext_ldap/base.py",
    "relative_path": "flext-ldap/src/flext_ldap/base.py",
    "line": 27,
    "language": "python"
  },
  {
    "name": "FlextLdifVersion",
    "qualified_name": "/home/marlonsc/flext/flext-ldif/src/flext_ldif/__version__.py::FlextLdifVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-ldif/src/flext_ldif/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-ldif/src/flext_ldif/__version__.py",
    "relative_path": "flext-ldif/src/flext_ldif/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "FlextLdifUtilitiesTransformer",
    "qualified_name": "/home/marlonsc/flext/flext-ldif/src/flext_ldif/_utilities/_transformer_base.py::FlextLdifUtilitiesTransformer",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-ldif/src/flext_ldif/_utilities/_transformer_base.py",
    "file_path": "/home/marlonsc/flext/flext-ldif/src/flext_ldif/_utilities/_transformer_base.py",
    "relative_path": "flext-ldif/src/flext_ldif/_utilities/_transformer_base.py",
    "line": 10,
    "language": "python"
  },
  {
    "name": "SchemaConstants",
    "qualified_name": "/home/marlonsc/flext/flext-ldif/src/flext_ldif/_utilities/object_class.py::FlextLdifUtilitiesObjectClass.SchemaConstants",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-ldif/src/flext_ldif/_utilities/object_class.py",
    "file_path": "/home/marlonsc/flext/flext-ldif/src/flext_ldif/_utilities/object_class.py",
    "relative_path": "flext-ldif/src/flext_ldif/_utilities/object_class.py",
    "line": 16,
    "language": "python"
  },
  {
    "name": "OperationalAttributes",
    "qualified_name": "/home/marlonsc/flext/flext-ldif/src/flext_ldif/constants.py::FlextLdifConstants.Ldif.OperationalAttributes",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-ldif/src/flext_ldif/constants.py",
    "file_path": "/home/marlonsc/flext/flext-ldif/src/flext_ldif/constants.py",
    "relative_path": "flext-ldif/src/flext_ldif/constants.py",
    "line": 511,
    "language": "python"
  },
  {
    "name": "FlextMeltanoVersion",
    "qualified_name": "/home/marlonsc/flext/flext-meltano/src/flext_meltano/__version__.py::FlextMeltanoVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-meltano/src/flext_meltano/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-meltano/src/flext_meltano/__version__.py",
    "relative_path": "flext-meltano/src/flext_meltano/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "FlextObservabilityVersion",
    "qualified_name": "/home/marlonsc/flext/flext-observability/src/flext_observability/__version__.py::FlextObservabilityVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-observability/src/flext_observability/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-observability/src/flext_observability/__version__.py",
    "relative_path": "flext-observability/src/flext_observability/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "Storage",
    "qualified_name": "/home/marlonsc/flext/flext-observability/src/flext_observability/constants.py::FlextObservabilityConstants.Observability.Storage",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-observability/src/flext_observability/constants.py",
    "file_path": "/home/marlonsc/flext/flext-observability/src/flext_observability/constants.py",
    "relative_path": "flext-observability/src/flext_observability/constants.py",
    "line": 142,
    "language": "python"
  },
  {
    "name": "MonitoringDecorators",
    "qualified_name": "/home/marlonsc/flext/flext-observability/src/flext_observability/services/monitoring.py::FlextObservabilityMonitor.MonitoringDecorators",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-observability/src/flext_observability/services/monitoring.py",
    "file_path": "/home/marlonsc/flext/flext-observability/src/flext_observability/services/monitoring.py",
    "relative_path": "flext-observability/src/flext_observability/services/monitoring.py",
    "line": 317,
    "language": "python"
  },
  {
    "name": "FlextOracleOicVersion",
    "qualified_name": "/home/marlonsc/flext/flext-oracle-oic/src/flext_oracle_oic/__version__.py::FlextOracleOicVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-oracle-oic/src/flext_oracle_oic/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-oracle-oic/src/flext_oracle_oic/__version__.py",
    "relative_path": "flext-oracle-oic/src/flext_oracle_oic/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "OracleOicValidation",
    "qualified_name": "/home/marlonsc/flext/flext-oracle-oic/src/flext_oracle_oic/constants.py::FlextOracleOicConstants.OracleOicValidation",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-oracle-oic/src/flext_oracle_oic/constants.py",
    "file_path": "/home/marlonsc/flext/flext-oracle-oic/src/flext_oracle_oic/constants.py",
    "relative_path": "flext-oracle-oic/src/flext_oracle_oic/constants.py",
    "line": 189,
    "language": "python"
  },
  {
    "name": "FlextOracleWmsVersion",
    "qualified_name": "/home/marlonsc/flext/flext-oracle-wms/src/flext_oracle_wms/__version__.py::FlextOracleWmsVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-oracle-wms/src/flext_oracle_wms/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-oracle-wms/src/flext_oracle_wms/__version__.py",
    "relative_path": "flext-oracle-wms/src/flext_oracle_wms/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "WmsEntities",
    "qualified_name": "/home/marlonsc/flext/flext-oracle-wms/src/flext_oracle_wms/constants.py::FlextOracleWmsConstants.OracleWms.WmsEntities",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-oracle-wms/src/flext_oracle_wms/constants.py",
    "file_path": "/home/marlonsc/flext/flext-oracle-wms/src/flext_oracle_wms/constants.py",
    "relative_path": "flext-oracle-wms/src/flext_oracle_wms/constants.py",
    "line": 124,
    "language": "python"
  },
  {
    "name": "WmsProcessing",
    "qualified_name": "/home/marlonsc/flext/flext-oracle-wms/src/flext_oracle_wms/constants.py::FlextOracleWmsConstants.OracleWms.WmsProcessing",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-oracle-wms/src/flext_oracle_wms/constants.py",
    "file_path": "/home/marlonsc/flext/flext-oracle-wms/src/flext_oracle_wms/constants.py",
    "relative_path": "flext-oracle-wms/src/flext_oracle_wms/constants.py",
    "line": 129,
    "language": "python"
  },
  {
    "name": "FlextPluginVersion",
    "qualified_name": "/home/marlonsc/flext/flext-plugin/src/flext_plugin/__version__.py::FlextPluginVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-plugin/src/flext_plugin/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-plugin/src/flext_plugin/__version__.py",
    "relative_path": "flext-plugin/src/flext_plugin/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "PluginValidation",
    "qualified_name": "/home/marlonsc/flext/flext-plugin/src/flext_plugin/constants.py::FlextPluginConstants.Plugin.PluginValidation",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-plugin/src/flext_plugin/constants.py",
    "file_path": "/home/marlonsc/flext/flext-plugin/src/flext_plugin/constants.py",
    "relative_path": "flext-plugin/src/flext_plugin/constants.py",
    "line": 123,
    "language": "python"
  },
  {
    "name": "FlextQualityVersion",
    "qualified_name": "/home/marlonsc/flext/flext-quality/src/flext_quality/__version__.py::FlextQualityVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-quality/src/flext_quality/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-quality/src/flext_quality/__version__.py",
    "relative_path": "flext-quality/src/flext_quality/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "FlextQualityMcpTools",
    "qualified_name": "/home/marlonsc/flext/flext-quality/src/flext_quality/mcp/tools.py::FlextQualityMcpTools",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-quality/src/flext_quality/mcp/tools.py",
    "file_path": "/home/marlonsc/flext/flext-quality/src/flext_quality/mcp/tools.py",
    "relative_path": "flext-quality/src/flext_quality/mcp/tools.py",
    "line": 21,
    "language": "python"
  },
  {
    "name": "FlextTapLdapVersion",
    "qualified_name": "/home/marlonsc/flext/flext-tap-ldap/src/flext_tap_ldap/__version__.py::FlextTapLdapVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-tap-ldap/src/flext_tap_ldap/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-tap-ldap/src/flext_tap_ldap/__version__.py",
    "relative_path": "flext-tap-ldap/src/flext_tap_ldap/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "FlextTapLdapServiceBase",
    "qualified_name": "/home/marlonsc/flext/flext-tap-ldap/src/flext_tap_ldap/base.py::FlextTapLdapServiceBase",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-tap-ldap/src/flext_tap_ldap/base.py",
    "file_path": "/home/marlonsc/flext/flext-tap-ldap/src/flext_tap_ldap/base.py",
    "relative_path": "flext-tap-ldap/src/flext_tap_ldap/base.py",
    "line": 18,
    "language": "python"
  },
  {
    "name": "FlextTapLdifVersion",
    "qualified_name": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/__version__.py::FlextTapLdifVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/__version__.py",
    "relative_path": "flext-tap-ldif/src/flext_tap_ldif/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "TapLdifPerformance",
    "qualified_name": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/constants.py::FlextTapLdifConstants.TapLdif.TapLdifPerformance",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/constants.py",
    "file_path": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/constants.py",
    "relative_path": "flext-tap-ldif/src/flext_tap_ldif/constants.py",
    "line": 56,
    "language": "python"
  },
  {
    "name": "EntrySchema",
    "qualified_name": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/constants.py::FlextTapLdifConstants.TapLdif.EntrySchema",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/constants.py",
    "file_path": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/constants.py",
    "relative_path": "flext-tap-ldif/src/flext_tap_ldif/constants.py",
    "line": 61,
    "language": "python"
  },
  {
    "name": "TapLdif",
    "qualified_name": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/models.py::FlextTapLdifModels.TapLdif",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/models.py",
    "file_path": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/models.py",
    "relative_path": "flext-tap-ldif/src/flext_tap_ldif/models.py",
    "line": 22,
    "language": "python"
  },
  {
    "name": "TapLdif",
    "qualified_name": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/utilities.py::FlextTapLdifUtilities.TapLdif",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/utilities.py",
    "file_path": "/home/marlonsc/flext/flext-tap-ldif/src/flext_tap_ldif/utilities.py",
    "relative_path": "flext-tap-ldif/src/flext_tap_ldif/utilities.py",
    "line": 24,
    "language": "python"
  },
  {
    "name": "FlextTapOracleVersion",
    "qualified_name": "/home/marlonsc/flext/flext-tap-oracle/src/flext_tap_oracle/__version__.py::FlextTapOracleVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-tap-oracle/src/flext_tap_oracle/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-tap-oracle/src/flext_tap_oracle/__version__.py",
    "relative_path": "flext-tap-oracle/src/flext_tap_oracle/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "Extraction",
    "qualified_name": "/home/marlonsc/flext/flext-tap-oracle/src/flext_tap_oracle/constants.py::FlextTapOracleConstants.TapOracle.Extraction",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-tap-oracle/src/flext_tap_oracle/constants.py",
    "file_path": "/home/marlonsc/flext/flext-tap-oracle/src/flext_tap_oracle/constants.py",
    "relative_path": "flext-tap-oracle/src/flext_tap_oracle/constants.py",
    "line": 55,
    "language": "python"
  },
  {
    "name": "FlextTapOracleOicVersion",
    "qualified_name": "/home/marlonsc/flext/flext-tap-oracle-oic/src/flext_tap_oracle_oic/__version__.py::FlextTapOracleOicVersion",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-tap-oracle-oic/src/flext_tap_oracle_oic/__version__.py",
    "file_path": "/home/marlonsc/flext/flext-tap-oracle-oic/src/flext_tap_oracle_oic/__version__.py",
    "relative_path": "flext-tap-oracle-oic/src/flext_tap_oracle_oic/__version__.py",
    "line": 19,
    "language": "python"
  },
  {
    "name": "FlextTapOracleOicConnection",
    "qualified_name": "/home/marlonsc/flext/flext-tap-oracle-oic/src/flext_tap_oracle_oic/_models/_oic_connection.py::FlextTapOracleOicConnection",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-tap-oracle-oic/src/flext_tap_oracle_oic/_models/_oic_connection.py",
    "file_path": "/home/marlonsc/flext/flext-tap-oracle-oic/src/flext_tap_oracle_oic/_models/_oic_connection.py",
    "relative_path": "flext-tap-oracle-oic/src/flext_tap_oracle_oic/_models/_oic_connection.py",
    "line": 18,
    "language": "python"
  },
  {
    "name": "FlextTapOracleOicExecutionSummary",
    "qualified_name": "/home/marlonsc/flext/flext-tap-oracle-oic/src/flext_tap_oracle_oic/_models/_oic_execution_summary.py::FlextTapOracleOicExecutionSummary",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-tap-oracle-oic/src/flext_tap_oracle_oic/_models/_oic_execution_summary.py",
    "file_path": "/home/marlonsc/flext/flext-tap-oracle-oic/src/flext_tap_oracle_oic/_models/_oic_execution_summary.py",
    "relative_path": "flext-tap-oracle-oic/src/flext_tap_oracle_oic/_models/_oic_execution_summary.py",
    "line": 18,
    "language": "python"
  },
  {
    "name": "FlextTapOracleOicIntegration",
    "qualified_name": "/home/marlonsc/flext/flext-tap-oracle-oic/src/flext_tap_oracle_oic/_models/_oic_integration.py::FlextTapOracleOicIntegration",
    "kind": "Class",
    "file": "/home/marlonsc/flext/flext-tap-or


... (truncated, 17183 chars omitted)
```

</details>
