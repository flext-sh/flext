<!-- AUTO-GENERATED — DO NOT EDIT MANUALLY. Source: code-review-graph → docs/architecture/crg-reports/architecture.md -->
<!-- Run `make docs` to regenerate. -->

# CRG Architecture Risk

<!-- TOC START -->

- [Summary](#summary)
- [Architecture Warnings](#architecture-warnings)
- [Top Communities](#top-communities)
- [Raw Output](#raw-output)

<!-- TOC END -->

## Summary

Architecture: 2469 communities, 2437 cross-community edges, showing 100 of 2437, 42
warning(s)

## Architecture Warnings

- High coupling (52 edges) between 'utilities-filter' and 'unit-records'
- High coupling (31 edges) between 'codegen-infra' and 'phases-apply'
- High coupling (24 edges) between 'flext-tests-compose' and
  'unit-tests-flext-tests-docker'
- High coupling (23 edges) between 'utilities-flext' and 'unit-tests-flext-core-models'
- High coupling (22 edges) between 'utilities-output' and 'unit-fake'
- High coupling (21 edges) between 'utilities-flext' and 'unit-tests-flext-core-runtime'
- High coupling (21 edges) between 'docs-config' and 'unit-tests-flext-quality'
- High coupling (20 edges) between 'codegen-infra-flext' and 'codegen-flext'
- High coupling (20 edges) between 'unit-tests-flext-infra-infra-patterns' and
  'matchers-validate'
- High coupling (18 edges) between 'json-json' and 'unit-tests-flext-cli-json-cov'
- High coupling (18 edges) between 'cli-parts-cli' and 'unit-options'
- High coupling (18 edges) between 'services-display' and
  'unit-tests-flext-cli-services'
- High coupling (17 edges) between 'codegen-infra' and 'release-release'
- High coupling (17 edges) between 'flext-quality-hook' and 'unit-flext-quality'
- High coupling (16 edges) between 'flext-core-container' and
  'unit-tests-flext-core-context'
- High coupling (16 edges) between 'utilities-flext' and 'unit-color'
- High coupling (16 edges) between 'codegen-infra' and 'codegen-conform'
- High coupling (16 edges) between 'detectors-infra' and 'refactor-infra'
- High coupling (16 edges) between 'models-config' and 'unit-test-flext-meltano'
- High coupling (16 edges) between 'utilities-flext' and
  'unit-tests-flext-target-oracle-wms-schema'
- High coupling (15 edges) between 'unit-handler' and
  'utilities-flext-tests-handler-helpers'
- High coupling (15 edges) between 'utilities-str' and
  'unit-tests-flext-core-utilities-domain'
- High coupling (15 edges) between 'utilities-oracle-engine' and
  'flext-db-oracle-operation'
- High coupling (15 edges) between 'utilities-flext' and 'unit-record-msg'
- High coupling (14 edges) between 'tests-deps' and 'deps-infra'
- High coupling (14 edges) between 'utilities-auth' and 'unit-wms'
- High coupling (14 edges) between 'utilities-plugin' and 'flext-plugin-plugin'
- High coupling (13 edges) between 'utilities-cli-matches' and
  'unit-tests-flext-cli-matching-cov'
- High coupling (13 edges) between 'utilities-flext' and 'utilities-sample-model'
- High coupling (13 edges) between 'flext-grpc-flext-grpc' and
  'unit-tests-flext-grpc-api'
- High coupling (13 edges) between 'docs-quality' and
  'unit-tests-flext-quality-documentation'
- High coupling (13 edges) between 'flext-web-app' and 'unit-tests-flext-web-settings'
- High coupling (12 edges) between 'protocols-flext' and 'unit-flext-engine'
- High coupling (12 edges) between 'gates-check' and 'tests-deps'
- High coupling (12 edges) between 'utilities-attributes' and 'unit-search'
- High coupling (12 edges) between 'utilities-filter' and
  'unit-tests-flext-oracle-wms-helpers'
- High coupling (12 edges) between 'flext-tests-fixture' and 'unit-flext-domains'
- High coupling (11 edges) between 'utilities-tables' and
  'unit-tests-flext-cli-tables-branch'
- High coupling (11 edges) between 'utilities-violation' and 'unit-flext-utilities'
- High coupling (11 edges) between 'services-oracle' and 'integration-oracle'
- High coupling (11 edges) between 'mro-nwc-19-target' and
  'mro-nwc-19-tests-flext-target-oracle-wms'
- High coupling (11 edges) between 'utilities-flext' and 'unit-msg-wms'

## Top Communities

- codegen-infra (688 nodes)
- utilities-flext (590 nodes)
- codegen-infra-flext (345 nodes)
- services-server (317 nodes)
- detectors-infra (302 nodes)
- gates-check (290 nodes)
- phases-apply (240 nodes)
- utilities-extract (211 nodes)
- utilities-files (206 nodes)
- flext-core-container (203 nodes)
- services-oracle (198 nodes)
- transformers-import (169 nodes)
- services-context (169 nodes)
- matchers-validate (155 nodes)
- flext-tap-oracle-wms-tap (129 nodes)
- protocols-flext (114 nodes)
- utilities-source (114 nodes)
- tests-deps (110 nodes)
- base-attribute (109 nodes)
- services-integration (106 nodes)
- ... and 2449 more

## Raw Output

<details>

```json
{
  "status": "ok",
  "summary": "Architecture: 2469 communities, 2437 cross-community edges, showing 100 of 2437, 42 warning(s)",
  "communities": [
    {
      "id": 84954,
      "name": "codegen-infra",
      "level": 0,
      "cohesion": 0.1638,
      "size": 688,
      "dominant_language": "python",
      "description": "Community of 688 nodes",
      "members": [
        "~/flext/flext-infra/src/flext_infra/_utilities/discovery.py::FlextInfraUtilitiesDiscovery",
        "~/flext/flext-infra/src/flext_infra/_utilities/discovery.py::FlextInfraUtilitiesDiscovery._workspace_project_roots",
        "~/flext/flext-infra/src/flext_infra/_utilities/discovery.py::FlextInfraUtilitiesDiscovery._discover_project_root_from_path",
        "~/flext/flext-infra/src/flext_infra/_utilities/discovery.py::FlextInfraUtilitiesDiscovery._relative_path_parts",
        "~/flext/flext-infra/src/flext_infra/_utilities/discovery.py::FlextInfraUtilitiesDiscovery._normalized_python_parts",
        "~/flext/flext-infra/src/flext_infra/_utilities/discovery.py::FlextInfraUtilitiesDiscovery._package_name_from_wrapper_parts",
        "~/flext/flext-infra/src/flext_infra/_utilities/discovery.py::FlextInfraUtilitiesDiscovery._package_name_from_src_dir",
        "~/flext/flext-infra/src/flext_infra/_utilities/discovery.py::FlextInfraUtilitiesDiscovery.is_pytest_test_module",
        "~/flext/flext-infra/src/flext_infra/_utilities/discovery.py::FlextInfraUtilitiesDiscovery.project_root",
        "~/flext/flext-infra/src/flext_infra/_utilities/discovery.py::FlextInfraUtilitiesDiscovery._discover_package_from_path"
      ],
      "members_total": 688,
      "members_truncated": true
    },
    {
      "id": 84169,
      "name": "utilities-flext",
      "level": 0,
      "cohesion": 0.159,
      "size": 590,
      "dominant_language": "python",
      "description": "Community of 590 nodes",
      "members": [
        "~/flext/flext-cli/tests/unit/test_config_engine.py::TestsFlextCliConfigEngine.test_config_load_yaml_expands_env",
        "~/flext/flext-core/src/flext_core/_decorators/_logging.py::FlextDecoratorsLogging",
        "~/flext/flext-core/src/flext_core/_decorators/_logging.py::FlextDecoratorsLogging.log_operation",
        "~/flext/flext-core/src/flext_core/_decorators/_logging.py::FlextDecoratorsLogging.decorator",
        "~/flext/flext-core/src/flext_core/_decorators/_logging.py::FlextDecoratorsLogging.wrapper",
        "~/flext/flext-core/src/flext_core/_decorators/_logging.py::FlextDecoratorsLogging._resolve_correlation_id",
        "~/flext/flext-core/src/flext_core/_decorators/_logging.py::FlextDecoratorsLogging._execute_logged_call",
        "~/flext/flext-core/src/flext_core/_decorators/_logging.py::FlextDecoratorsLogging.with_correlation",
        "~/flext/flext-core/src/flext_core/_models/_context/__scope_parts/flextmodelscontextscope_part_02.py::FlextModelsContextScope.ContextRuntimeState",
        "~/flext/flext-core/src/flext_core/_models/_context/__scope_parts/flextmodelscontextscope_part_02.py::FlextModelsContextScope.ContextRuntimeState.create_default"
      ],
      "members_total": 590,
      "members_truncated": true
    },
    {
      "id": 85036,
      "name": "codegen-infra-flext",
      "level": 0,
      "cohesion": 0.2092,
      "size": 345,
      "dominant_language": "python",
      "description": "Community of 345 nodes",
      "members": [
        "~/flext/flext-infra/src/flext_infra/codegen/_fixer_results.py::FlextInfraCodegenFixerResultsMixin",
        "~/flext/flext-infra/src/flext_infra/codegen/_fixer_results.py::FlextInfraCodegenFixerResultsMixin._empty_result",
        "~/flext/flext-infra/src/flext_infra/codegen/_fixer_results.py::FlextInfraCodegenFixerResultsMixin._build_result",
        "~/flext/flext-infra/src/flext_infra/codegen/_fixer_results.py::FlextInfraCodegenFixerResultsMixin._load_initial_violations",
        "~/flext/flext-infra/src/flext_infra/codegen/_fixer_results.py::FlextInfraCodegenFixerResultsMixin._classify_remaining_violations",
        "~/flext/flext-infra/src/flext_infra/codegen/_pipeline_stages.py::FlextInfraCodegenPipelineStagesMixin",
        "~/flext/flext-infra/src/flext_infra/codegen/_pipeline_stages.py::FlextInfraCodegenPipelineStagesMixin._run_stage",
        "~/flext/flext-infra/src/flext_infra/codegen/_pipeline_stages.py::FlextInfraCodegenPipelineStagesMixin._stage_discover",
        "~/flext/flext-infra/src/flext_infra/codegen/_pipeline_stages.py::FlextInfraCodegenPipelineStagesMixin._action",
        "~/flext/flext-infra/src/flext_infra/codegen/_pipeline_stages.py::FlextInfraCodegenPipelineStagesMixin._emit"
      ],
      "members_total": 345,
      "members_truncated": true
    },
    {
      "id": 85375,
      "name": "services-server",
      "level": 0,
      "cohesion": 0.2806,
      "size": 317,
      "dominant_language": "python",
      "description": "Community of 317 nodes",
      "members": [
        "~/flext/flext-ldif/examples/05_schema_operations.py::_create_entry_or_none",
        "~/flext/flext-ldif/examples/05_schema_operations.py::intelligent_schema_building",
        "~/flext/flext-ldif/examples/05_schema_operations.py::railway_schema_pipeline",
        "~/flext/flext-ldif/src/flext_ldif/api.py::FlextLdif",
        "~/flext/flext-ldif/src/flext_ldif/api.py::FlextLdif.__init__",
        "~/flext/flext-ldif/src/flext_ldif/api.py::FlextLdif.__call__",
        "~/flext/flext-ldif/src/flext_ldif/api.py::FlextLdif.categorization",
        "~/flext/flext-ldif/src/flext_ldif/api.py::FlextLdif.filter_entry_attributes",
        "~/flext/flext-ldif/src/flext_ldif/api.py::FlextLdif.filter_schema_attribute_values",
        "~/flext/flext-ldif/src/flext_ldif/api.py::FlextLdif.acl"
      ],
      "members_total": 317,
      "members_truncated": true
    },
    {
      "id": 84735,
      "name": "detectors-infra",
      "level": 0,
      "cohesion": 0.2328,
      "size": 302,
      "dominant_language": "python",
      "description": "Community of 302 nodes",
      "members": [
        "~/flext/flext-infra/src/flext_infra/_enforcement/metadata.py::FlextInfraEnforcementMetadata",
        "~/flext/flext-infra/src/flext_infra/_enforcement/metadata.py::FlextInfraEnforcementMetadata.detect_declarative",
        "~/flext/flext-infra/src/flext_infra/_enforcement/metadata.py::FlextInfraEnforcementMetadata.violation_kind",
        "~/flext/flext-infra/src/flext_infra/_enforcement/metadata.py::FlextInfraEnforcementMetadata.object_kind",
        "~/flext/flext-infra/src/flext_infra/_enforcement/metadata.py::FlextInfraEnforcementMetadata.object_name",
        "~/flext/flext-infra/src/flext_infra/_enforcement/metadata.py::FlextInfraEnforcementMetadata.description",
        "~/flext/flext-infra/src/flext_infra/_enforcement/selection.py::FlextInfraEnforcementSelection",
        "~/flext/flext-infra/src/flext_infra/_enforcement/selection.py::FlextInfraEnforcementSelection.canonical_catalog",
        "~/flext/flext-infra/src/flext_infra/_enforcement/selection.py::FlextInfraEnforcementSelection.selected_rules",
        "~/flext/flext-infra/src/flext_infra/_enforcement/selection.py::FlextInfraEnforcementSelection.declarative_rules"
      ],
      "members_total": 302,
      "members_truncated": true
    },
    {
      "id": 85025,
      "name": "gates-check",
      "level": 0,
      "cohesion": 0.2685,
      "size": 290,
      "dominant_language": "python",
      "description": "Community of 290 nodes",
      "members": [
        "~/flext/flext-infra/src/flext_infra/check/workspace_check_gates.py::FlextInfraGateRegistry",
        "~/flext/flext-infra/src/flext_infra/check/workspace_check_gates.py::FlextInfraGateRegistry.__init__",
        "~/flext/flext-infra/src/flext_infra/check/workspace_check_gates.py::FlextInfraGateRegistry._gate_classes",
        "~/flext/flext-infra/src/flext_infra/check/workspace_check_gates.py::FlextInfraGateRegistry.get",
        "~/flext/flext-infra/src/flext_infra/check/workspace_check_gates.py::FlextInfraGateRegistry.create",
        "~/flext/flext-infra/src/flext_infra/check/workspace_check_gates.py::FlextInfraGateRegistry.default",
        "~/flext/flext-infra/src/flext_infra/check/workspace_check_gates.py::FlextInfraWorkspaceCheckGatesMixin",
        "~/flext/flext-infra/src/flext_infra/check/workspace_check_gates.py::FlextInfraWorkspaceCheckGatesMixin._isolate_context",
        "~/flext/flext-infra/src/flext_infra/check/workspace_check_gates.py::FlextInfraWorkspaceCheckGatesMixin._run_single_project",
        "~/flext/flext-infra/src/flext_infra/check/workspace_check_gates.py::FlextInfraWorkspaceCheckGatesMixin._run_project_loop"
      ],
      "members_total": 290,
      "members_truncated": true
    },
    {
      "id": 85076,
      "name": "phases-apply",
      "level": 0,
      "cohesion": 0.3093,
      "size": 240,
      "dominant_language": "python",
      "description": "Community of 240 nodes",
      "members": [
        "~/flext/flext-infra/src/flext_infra/deps/extra_paths.py::FlextInfraExtraPathsManager",
        "~/flext/flext-infra/src/flext_infra/deps/extra_paths.py::FlextInfraExtraPathsManager.model_post_init",
        "~/flext/flext-infra/src/flext_infra/deps/extra_paths.py::FlextInfraExtraPathsManager.workspace_project_names",
        "~/flext/flext-infra/src/flext_infra/deps/extra_paths.py::FlextInfraExtraPathsManager.analysis_excluded_top_dirs",
        "~/flext/flext-infra/src/flext_infra/deps/extra_paths.py::FlextInfraExtraPathsManager.execute",
        "~/flext/flext-infra/src/flext_infra/deps/extra_paths.py::FlextInfraExtraPathsManager._existing_typings_paths",
        "~/flext/flext-infra/src/flext_infra/deps/extra_paths.py::FlextInfraExtraPathsManager._search_path_set",
        "~/flext/flext-infra/src/flext_infra/deps/extra_paths.py::FlextInfraExtraPathsManager.pyright_extra_paths",
        "~/flext/flext-infra/src/flext_infra/deps/extra_paths.py::FlextInfraExtraPathsManager.pyrefly_search_paths",
        "~/flext/flext-infra/src/flext_infra/deps/extra_paths.py::FlextInfraExtraPathsManager.mypy_search_paths"
      ],
      "members_total": 240,
      "members_truncated": true
    },
    {
      "id": 85447,
      "name": "utilities-extract",
      "level": 0,
      "cohesion": 0.2299,
      "size": 211,
      "dominant_language": "python",
      "description": "Community of 211 nodes",
      "members": [
        "~/flext/flext-ldif/src/flext_ldif/_utilities/acl.py::FlextLdifUtilitiesACL",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/acl.py::FlextLdifUtilitiesACL._is_acl_subject_type",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/acl.py::FlextLdifUtilitiesACL._build_extensions",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/acl.py::FlextLdifUtilitiesACL.extract_extra",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/acl.py::FlextLdifUtilitiesACL._build_subject_and_permissions",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/acl.py::FlextLdifUtilitiesACL._check_special_value",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/acl.py::FlextLdifUtilitiesACL._extract_from_match",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/acl.py::FlextLdifUtilitiesACL._extract_target_info",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/acl.py::FlextLdifUtilitiesACL._extract_version_and_name",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/acl.py::FlextLdifUtilitiesACL._normalize_permission"
      ],
      "members_total": 211,
      "members_truncated": true
    },
    {
      "id": 83947,
      "name": "utilities-files",
      "level": 0,
      "cohesion": 0.0579,
      "size": 206,
      "dominant_language": "python",
      "description": "Community of 206 nodes",
      "members": [
        "~/flext/flext-cli/src/flext_cli/_utilities/_file_test_helper_parts/flextcliutilitiesfiletesthelpersmixin_part_01.py::FlextCliUtilitiesFileTestHelpersMixin",
        "~/flext/flext-cli/src/flext_cli/_utilities/_file_test_helper_parts/flextcliutilitiesfiletesthelpersmixin_part_01.py::FlextCliUtilitiesFileTestHelpersMixin.files_context",
        "~/flext/flext-cli/src/flext_cli/_utilities/_file_test_helper_parts/flextcliutilitiesfiletesthelpersmixin_part_01.py::FlextCliUtilitiesFileTestHelpersMixin._files_write_structured",
        "~/flext/flext-cli/src/flext_cli/_utilities/_file_test_helper_parts/flextcliutilitiesfiletesthelpersmixin_part_04.py::FlextCliUtilitiesFileTestHelpersMixin",
        "~/flext/flext-cli/src/flext_cli/_utilities/_file_test_helper_parts/flextcliutilitiesfiletesthelpersmixin_part_04.py::FlextCliUtilitiesFileTestHelpersMixin.files_parse_content",
        "~/flext/flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py::FlextCliUtilitiesFiles",
        "~/flext/flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py::FlextCliUtilitiesFiles.files_delete",
        "~/flext/flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py::FlextCliUtilitiesFiles._delete",
        "~/flext/flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py::FlextCliUtilitiesFiles.files_read_text",
        "~/flext/flext-cli/src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py::FlextCliUtilitiesFiles.files_write_text"
      ],
      "members_total": 206,
      "members_truncated": true
    },
    {
      "id": 84354,
      "name": "flext-core-container",
      "level": 0,
      "cohesion": 0.3788,
      "size": 203,
      "dominant_language": "python",
      "description": "Community of 203 nodes",
      "members": [
        "~/flext/flext-core/src/flext_core/container.py::FlextContainer",
        "~/flext/flext-core/src/flext_core/container.py::FlextContainer.__new__",
        "~/flext/flext-core/src/flext_core/container.py::FlextContainer.settings",
        "~/flext/flext-core/src/flext_core/container.py::FlextContainer.context",
        "~/flext/flext-core/src/flext_core/container.py::FlextContainer.provide",
        "~/flext/flext-core/src/flext_core/container.py::FlextContainer.reset_for_testing",
        "~/flext/flext-core/src/flext_core/container.py::FlextContainer.logger",
        "~/flext/flext-core/src/flext_core/container.py::FlextContainer._matches_service_type",
        "~/flext/flext-core/src/flext_core/container.py::FlextContainer._resolve_callable",
        "~/flext/flext-core/src/flext_core/container.py::FlextContainer.resolve"
      ],
      "members_total": 203,
      "members_truncated": true
    },
    {
      "id": 84561,
      "name": "services-oracle",
      "level": 0,
      "cohesion": 0.1587,
      "size": 198,
      "dominant_language": "python",
      "description": "Community of 198 nodes",
      "members": [
        "~/flext/flext-db-oracle/src/flext_db_oracle/api.py::FlextDbOracleApi",
        "~/flext/flext-db-oracle/src/flext_db_oracle/api.py::FlextDbOracleApi.__init__",
        "~/flext/flext-db-oracle/src/flext_db_oracle/services/api_runtime.py::FlextDbOracleApiRuntime",
        "~/flext/flext-db-oracle/src/flext_db_oracle/services/api_runtime.py::FlextDbOracleApiRuntime.__init__",
        "~/flext/flext-db-oracle/src/flext_db_oracle/services/api_runtime.py::FlextDbOracleApiRuntime.__repr__",
        "~/flext/flext-db-oracle/src/flext_db_oracle/services/api_runtime.py::FlextDbOracleApiRuntime.__enter__",
        "~/flext/flext-db-oracle/src/flext_db_oracle/services/api_runtime.py::FlextDbOracleApiRuntime.__exit__",
        "~/flext/flext-db-oracle/src/flext_db_oracle/services/api_runtime.py::FlextDbOracleApiRuntime._dispatch_enabled",
        "~/flext/flext-db-oracle/src/flext_db_oracle/services/api_runtime.py::FlextDbOracleApiRuntime.settings",
        "~/flext/flext-db-oracle/src/flext_db_oracle/services/api_runtime.py::FlextDbOracleApiRuntime.connection"
      ],
      "members_total": 198,
      "members_truncated": true
    },
    {
      "id": 85001,
      "name": "transformers-import",
      "level": 0,
      "cohesion": 0.3028,
      "size": 169,
      "dominant_language": "python",
      "description": "Community of 169 nodes",
      "members": [
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_imports.py::FlextInfraUtilitiesRopeImports",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_imports.py::FlextInfraUtilitiesRopeImports.import_statements",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_imports.py::FlextInfraUtilitiesRopeImports.import_statement_module_name",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_imports.py::FlextInfraUtilitiesRopeImports.import_statement_names_and_aliases",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_imports.py::FlextInfraUtilitiesRopeImports.imported_module_paths",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_imports.py::FlextInfraUtilitiesRopeImports.find_occurrences",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_imports.py::FlextInfraUtilitiesRopeImports.location_file_path",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_imports.py::FlextInfraUtilitiesRopeImports.indexed_search_resources",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_imports.py::FlextInfraUtilitiesRopeImports.organize_imports",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_imports.py::FlextInfraUtilitiesRopeImports.normalize_imports"
      ],
      "members_total": 169,
      "members_truncated": true
    },
    {
      "id": 85678,
      "name": "services-context",
      "level": 0,
      "cohesion": 0.4026,
      "size": 169,
      "dominant_language": "python",
      "description": "Community of 169 nodes",
      "members": [
        "~/flext/flext-observability/src/flext_observability/services/advanced_context.py::FlextObservabilityAdvancedContext",
        "~/flext/flext-observability/src/flext_observability/services/advanced_context.py::FlextObservabilityAdvancedContext.Context",
        "~/flext/flext-observability/src/flext_observability/services/advanced_context.py::FlextObservabilityAdvancedContext.Context.__init__",
        "~/flext/flext-observability/src/flext_observability/services/advanced_context.py::FlextObservabilityAdvancedContext.Context.clear",
        "~/flext/flext-observability/src/flext_observability/services/advanced_context.py::FlextObservabilityAdvancedContext.Context.baggage",
        "~/flext/flext-observability/src/flext_observability/services/advanced_context.py::FlextObservabilityAdvancedContext.Context.metadata",
        "~/flext/flext-observability/src/flext_observability/services/advanced_context.py::FlextObservabilityAdvancedContext.Context.resolve_baggage",
        "~/flext/flext-observability/src/flext_observability/services/advanced_context.py::FlextObservabilityAdvancedContext.Context.resolve_metadata",
        "~/flext/flext-observability/src/flext_observability/services/advanced_context.py::FlextObservabilityAdvancedContext.Context.merge",
        "~/flext/flext-observability/src/flext_observability/services/advanced_context.py::FlextObservabilityAdvancedContext.Context.restore"
      ],
      "members_total": 169,
      "members_truncated": true
    },
    {
      "id": 86059,
      "name": "matchers-validate",
      "level": 0,
      "cohesion": 0.1655,
      "size": 155,
      "dominant_language": "python",
      "description": "Community of 155 nodes",
      "members": [
        "~/flext/flext-cli/tests/unit/test_base.py::TestsFlextCliBase.test_canonical_settings_satisfies_cli_protocol",
        "~/flext/flext-cli/tests/unit/test_runtime_streamed_process.py::TestsFlextCliRuntimeStreamedProcess.test_legacy_timeout_contract_remains_a_failure",
        "~/flext/flext-cli/tests/unit/test_runtime_streamed_process.py::TestsFlextCliRuntimeStreamedProcess.test_broken_live_sink_fails_after_complete_durable_log",
        "~/flext/flext-cli/tests/unit/test_runtime_utilities_extra.py::TestsFlextCliRuntimeUtilitiesExtra.test_run_checked_fails_with_error_naming_failure",
        "~/flext/flext-cli/tests/unit/test_runtime_utilities_extra.py::TestsFlextCliRuntimeUtilitiesExtra.test_run_to_file_fails_with_timeout_error_on_slow_command",
        "~/flext/flext-cli/tests/unit/test_runtime_utilities_extra.py::TestsFlextCliRuntimeUtilitiesExtra.test_run_to_file_fails_with_execution_error_on_unwritable_target",
        "~/flext/flext-cli/tests/unit/test_runtime_utilities_extra.py::TestsFlextCliRuntimeUtilitiesExtra.test_run_to_file_fails_with_execution_error_on_invalid_env",
        "~/flext/flext-cli/tests/unit/test_settings.py::TestsFlextCliSettingsUnit.test_settings_singleton_satisfies_contract",
        "~/flext/flext-cli/tests/unit/test_settings.py::TestsFlextCliSettingsUnit.test_reset_for_testing_restores_usable_defaults",
        "~/flext/flext-core/tests/integration/service_lifecycle_cases.py::TestsFlextFlextServiceLifecycleCases.test_lifecycle_service_initialization"
      ],
      "members_total": 155,
      "members_truncated": true
    },
    {
      "id": 85645,
      "name": "flext-tap-oracle-wms-tap",
      "level": 0,
      "cohesion": 0.3043,
      "size": 129,
      "dominant_language": "python",
      "description": "Community of 129 nodes",
      "members": [
        "~/flext/flext-meltano/src/flext_meltano/services/singer_sdk.py::FlextMeltanoSingerTapAdapter",
        "~/flext/flext-meltano/src/flext_meltano/services/singer_sdk.py::FlextMeltanoSingerTapAdapter.__init__",
        "~/flext/flext-meltano/src/flext_meltano/services/singer_sdk.py::FlextMeltanoSingerTapAdapter.settings",
        "~/flext/flext-meltano/src/flext_meltano/services/singer_sdk.py::FlextMeltanoSingerTapAdapter._normalize_recursive",
        "~/flext/flext-meltano/src/flext_meltano/services/singer_sdk.py::FlextMeltanoSingerTapAdapter.run_cli",
        "~/flext/flext-meltano/src/flext_meltano/services/singer_sdk.py::FlextMeltanoSingerTapAdapter.discover_streams",
        "~/flext/flext-meltano/src/flext_meltano/services/singer_sdk.py::FlextMeltanoSingerTapAdapter.sync_all",
        "~/flext/flext-tap-ldif/src/flext_tap_ldif/api.py::FlextTapLdifService",
        "~/flext/flext-tap-ldif/src/flext_tap_ldif/api.py::FlextTapLdifService.create_tap_instance",
        "~/flext/flext-tap-oracle-wms/examples/01_basic_usage.py::main"
      ],
      "members_total": 129,
      "members_truncated": true
    },
    {
      "id": 84266,
      "name": "protocols-flext",
      "level": 0,
      "cohesion": 0.3371,
      "size": 114,
      "dominant_language": "python",
      "description": "Community of 114 nodes",
      "members": [
        "~/flext/flext-core/src/flext_core/_protocols/base.py::FlextProtocolsBase.ConfigObject",
        "~/flext/flext-core/src/flext_core/_protocols/base.py::FlextProtocolsBase.ConfigObject.get",
        "~/flext/flext-core/src/flext_core/_protocols/base.py::FlextProtocolsBase.ConfigObject.keys",
        "~/flext/flext-core/src/flext_core/_protocols/base.py::FlextProtocolsBase.ConfigObject.items",
        "~/flext/flext-core/src/flext_core/_protocols/result.py::FlextProtocolsResult.Result",
        "~/flext/flext-core/src/flext_core/_protocols/result.py::FlextProtocolsResult.Result.error",
        "~/flext/flext-core/src/flext_core/_protocols/result.py::FlextProtocolsResult.Result.error_code",
        "~/flext/flext-core/src/flext_core/_protocols/result.py::FlextProtocolsResult.Result.error_data",
        "~/flext/flext-core/src/flext_core/_protocols/result.py::FlextProtocolsResult.Result.success",
        "~/flext/flext-core/src/flext_core/_protocols/result.py::FlextProtocolsResult.Result.exception"
      ],
      "members_total": 114,
      "members_truncated": true
    },
    {
      "id": 84995,
      "name": "utilities-source",
      "level": 0,
      "cohesion": 0.3364,
      "size": 114,
      "dominant_language": "python",
      "description": "Community of 114 nodes",
      "members": [
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_analysis.py::FlextInfraUtilitiesRopeAnalysis",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_analysis.py::FlextInfraUtilitiesRopeAnalysis._resource_cache_key",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_analysis.py::FlextInfraUtilitiesRopeAnalysis.package_name_for_module",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_analysis.py::FlextInfraUtilitiesRopeAnalysis._package_name_for_module",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_analysis.py::FlextInfraUtilitiesRopeAnalysis.resolve_import_module",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_analysis.py::FlextInfraUtilitiesRopeAnalysis._resolve_import_module",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_analysis.py::FlextInfraUtilitiesRopeAnalysis.get_module_semantic_state",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_analysis.py::FlextInfraUtilitiesRopeAnalysis._empty_module_semantic_state",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_analysis.py::FlextInfraUtilitiesRopeAnalysis._module_semantic_state_from_pymodule",
        "~/flext/flext-infra/src/flext_infra/_utilities/rope_analysis.py::FlextInfraUtilitiesRopeAnalysis._module_class_infos"
      ],
      "members_total": 114,
      "members_truncated": true
    },
    {
      "id": 85073,
      "name": "tests-deps",
      "level": 0,
      "cohesion": 0.1808,
      "size": 110,
      "dominant_language": "python",
      "description": "Community of 110 nodes",
      "members": [
        "~/flext/flext-infra/src/flext_infra/deps/detection.py::FlextInfraDependencyDetectionService",
        "~/flext/flext-infra/src/flext_infra/deps/detection.py::FlextInfraDependencyDetectionService.__init__",
        "~/flext/flext-infra/src/flext_infra/deps/detection.py::FlextInfraDependencyDetectionService._read_plain",
        "~/flext/flext-infra/src/flext_infra/deps/detection.py::FlextInfraDependencyDetectionService._run_raw",
        "~/flext/flext-infra/src/flext_infra/deps/detection.py::FlextInfraDependencyDetectionService.classify_issues",
        "~/flext/flext-infra/src/flext_infra/deps/detection.py::FlextInfraDependencyDetectionService.build_project_report",
        "~/flext/flext-infra/src/flext_infra/deps/detection.py::FlextInfraDependencyDetectionService._module_names",
        "~/flext/flext-infra/src/flext_infra/deps/detection.py::FlextInfraDependencyDetectionService.discover_project_paths",
        "~/flext/flext-infra/tests/unit/check/extended_gate_bandit_markdown_tests.py::TestBanditAndMarkdownGates.test_markdown_prefers_local_config_when_root_is_missing",
        "~/flext/flext-infra/tests/unit/check/extended_gate_bandit_markdown_tests.py::TestBanditAndMarkdownGates.test_markdown_never_inherits_parent_config"
      ],
      "members_total": 110,
      "members_truncated": true
    },
    {
      "id": 85459,
      "name": "base-attribute",
      "level": 0,
      "cohesion": 0.3482,
      "size": 109,
      "dominant_language": "python",
      "description": "Community of 109 nodes",
      "members": [
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/schema.py::FlextLdifServersBaseSchema",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/schema.py::FlextLdifServersBaseSchema.__new__",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/schema.py::FlextLdifServersBaseSchema.__init__",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/schema.py::FlextLdifServersBaseSchema._extract_metadata_extensions",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/schema.py::FlextLdifServersBaseSchema._preserve_formatting",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/schema.py::FlextLdifServersBaseSchema._resolve_server_type",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/schema.py::FlextLdifServersBaseSchema.build_attribute_metadata",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/schema.py::FlextLdifServersBaseSchema.validate_and_track_oid",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/schema.py::FlextLdifServersBaseSchema.can_handle_attribute",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/schema.py::FlextLdifServersBaseSchema.can_handle_objectclass"
      ],
      "members_total": 109,
      "members_truncated": true
    },
    {
      "id": 85693,
      "name": "services-integration",
      "level": 0,
      "cohesion": 0.3841,
      "size": 106,
      "dominant_language": "python",
      "description": "Community of 106 nodes",
      "members": [
        "~/flext/flext-oracle-oic/src/flext_oracle_oic/ext_client.py::FlextOracleOicClient",
        "~/flext/flext-oracle-oic/src/flext_oracle_oic/ext_client.py::FlextOracleOicClient.__init__",
        "~/flext/flext-oracle-oic/src/flext_oracle_oic/ext_client.py::FlextOracleOicClient.__enter__",
        "~/flext/flext-oracle-oic/src/flext_oracle_oic/ext_client.py::FlextOracleOicClient.__exit__",
        "~/flext/flext-oracle-oic/src/flext_oracle_oic/ext_client.py::FlextOracleOicClient.create_connection",
        "~/flext/flext-oracle-oic/src/flext_oracle_oic/ext_client.py::FlextOracleOicClient.create_integration",
        "~/flext/flext-oracle-oic/src/flext_oracle_oic/ext_client.py::FlextOracleOicClient.encode_client_credentials",
        "~/flext/flext-oracle-oic/src/flext_oracle_oic/ext_client.py::FlextOracleOicClient.execute_file_transfer",
        "~/flext/flext-oracle-oic/src/flext_oracle_oic/ext_client.py::FlextOracleOicClient.execute_scheduled_orchestration",
        "~/flext/flext-oracle-oic/src/flext_oracle_oic/ext_client.py::FlextOracleOicClient.get_access_token"
      ],
      "members_total": 106,
      "members_truncated": true
    },
    {
      "id": 85634,
      "name": "flext-meltano-pipeline",
      "level": 0,
      "cohesion": 0.3087,
      "size": 102,
      "dominant_language": "python",
      "description": "Community of 102 nodes",
      "members": [
        "~/flext/flext-meltano/src/flext_meltano/cli.py::FlextMeltanoCli",
        "~/flext/flext-meltano/src/flext_meltano/cli.py::FlextMeltanoCli.__init__",
        "~/flext/flext-meltano/src/flext_meltano/cli.py::FlextMeltanoCli.run",
        "~/flext/flext-meltano/src/flext_meltano/cli.py::FlextMeltanoCli._register_commands",
        "~/flext/flext-meltano/src/flext_meltano/cli.py::FlextMeltanoCli._register_version_command",
        "~/flext/flext-meltano/src/flext_meltano/cli.py::FlextMeltanoCli._handle_version",
        "~/flext/flext-meltano/src/flext_meltano/cli.py::FlextMeltanoCli._register_status_commands",
        "~/flext/flext-meltano/src/flext_meltano/cli.py::FlextMeltanoCli._handle_status_show",
        "~/flext/flext-meltano/src/flext_meltano/cli.py::FlextMeltanoCli._handle_status_health",
        "~/flext/flext-meltano/src/flext_meltano/cli.py::FlextMeltanoCli._register_tap_command"
      ],
      "members_total": 102,
      "members_truncated": true
    },
    {
      "id": 85734,
      "name": "unit-wms",
      "level": 0,
      "cohesion": 0.1713,
      "size": 98,
      "dominant_language": "python",
      "description": "Community of 98 nodes",
      "members": [
        "~/flext/flext-oracle-wms/tests/_factories.py::_basic_username",
        "~/flext/flext-oracle-wms/tests/_factories.py::_basic_password",
        "~/flext/flext-oracle-wms/tests/_factories.py::_basic_token",
        "~/flext/flext-oracle-wms/tests/_factories.py::_wms_password",
        "~/flext/flext-oracle-wms/tests/_factories.py::_wms_password_underscore",
        "~/flext/flext-oracle-wms/tests/_factories.py::_test_pass",
        "~/flext/flext-oracle-wms/tests/_factories.py::_custom_password",
        "~/flext/flext-oracle-wms/tests/_factories.py::_short_password",
        "~/flext/flext-oracle-wms/tests/_factories.py::_secret",
        "~/flext/flext-oracle-wms/tests/_factories.py::_oauth_secret"
      ],
      "members_total": 98,
      "members_truncated": true
    },
    {
      "id": 84640,
      "name": "services-ldif",
      "level": 0,
      "cohesion": 0.2896,
      "size": 93,
      "dominant_language": "python",
      "description": "Community of 93 nodes",
      "members": [
        "~/flext/flext-dbt-ldif/src/flext_dbt_ldif/api.py::FlextDbtLdif",
        "~/flext/flext-dbt-ldif/src/flext_dbt_ldif/api.py::FlextDbtLdif.__init__",
        "~/flext/flext-dbt-ldif/src/flext_dbt_ldif/api.py::FlextDbtLdif.fetch_instance",
        "~/flext/flext-dbt-ldif/src/flext_dbt_ldif/api.py::FlextDbtLdif.service",
        "~/flext/flext-dbt-ldif/src/flext_dbt_ldif/api.py::FlextDbtLdif.execute",
        "~/flext/flext-dbt-ldif/src/flext_dbt_ldif/api.py::FlextDbtLdif.generate_ldif_models",
        "~/flext/flext-dbt-ldif/src/flext_dbt_ldif/api.py::FlextDbtLdif.process_ldif_file",
        "~/flext/flext-dbt-ldif/src/flext_dbt_ldif/api.py::FlextDbtLdif.validate_ldif_quality",
        "~/flext/flext-dbt-ldif/src/flext_dbt_ldif/services/client.py::FlextDbtLdifClient.Client",
        "~/flext/flext-dbt-ldif/src/flext_dbt_ldif/services/client.py::FlextDbtLdifClient.Client.__init__"
      ],
      "members_total": 93,
      "members_truncated": true
    },
    {
      "id": 85457,
      "name": "oud-acl",
      "level": 0,
      "cohesion": 0.2475,
      "size": 93,
      "dominant_language": "python",
      "description": "Community of 93 nodes",
      "members": [
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/acl.py::FlextLdifServersBaseSchemaAcl",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/acl.py::FlextLdifServersBaseSchemaAcl.__init__",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/acl.py::FlextLdifServersBaseSchemaAcl.resolve_acl_attributes",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/acl.py::FlextLdifServersBaseSchemaAcl.matches_acl_attribute",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/acl.py::FlextLdifServersBaseSchemaAcl.can_handle",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/acl.py::FlextLdifServersBaseSchemaAcl.can_handle_acl",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/acl.py::FlextLdifServersBaseSchemaAcl.can_handle_attribute",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/acl.py::FlextLdifServersBaseSchemaAcl.can_handle_objectclass",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/acl.py::FlextLdifServersBaseSchemaAcl.create_metadata",
        "~/flext/flext-ldif/src/flext_ldif/servers/_base/acl.py::FlextLdifServersBaseSchemaAcl.execute"
      ],
      "members_total": 93,
      "members_truncated": true
    },
    {
      "id": 84438,
      "name": "unit-handler",
      "level": 0,
      "cohesion": 0.3545,
      "size": 92,
      "dominant_language": "python",
      "description": "Community of 92 nodes",
      "members": [
        "~/flext/flext-core/tests/unit/_handlers_support.py::TestsFlextFlextHandlers.ConcreteTestHandler",
        "~/flext/flext-core/tests/unit/_handlers_support.py::TestsFlextFlextHandlers.ConcreteTestHandler.__init__",
        "~/flext/flext-core/tests/unit/_handlers_support.py::TestsFlextFlextHandlers.ConcreteTestHandler.dispatch_message",
        "~/flext/flext-core/tests/unit/_handlers_support.py::TestsFlextFlextHandlers.ConcreteTestHandler.execute",
        "~/flext/flext-core/tests/unit/_handlers_support.py::TestsFlextFlextHandlers.ConcreteTestHandler.handle",
        "~/flext/flext-core/tests/unit/_handlers_support.py::TestsFlextFlextHandlers.ConcreteTestHandler.validate_message",
        "~/flext/flext-core/tests/unit/_handlers_support.py::TestsFlextFlextHandlers.ValidationTestHandler",
        "~/flext/flext-core/tests/unit/_handlers_support.py::TestsFlextFlextHandlers.ValidationTestHandler.__init__",
        "~/flext/flext-core/tests/unit/_handlers_support.py::TestsFlextFlextHandlers.ValidationTestHandler.validate_message",
        "~/flext/flext-core/tests/unit/_handlers_support.py::TestsFlextFlextHandlers.ValidationTestHandler.handle"
      ],
      "members_total": 92,
      "members_truncated": true
    },
    {
      "id": 86031,
      "name": "flext-tests-compose",
      "level": 0,
      "cohesion": 0.1169,
      "size": 92,
      "dominant_language": "python",
      "description": "Community of 92 nodes",
      "members": [
        "~/flext/flext-tests/src/flext_tests/_fixtures/connectivity.py::_endpoint",
        "~/flext/flext-tests/src/flext_tests/_fixtures/connectivity.py::_unreachable_reason",
        "~/flext/flext-tests/src/flext_tests/_fixtures/connectivity.py::pytest_collection_modifyitems",
        "~/flext/flext-tests/src/flext_tests/docker.py::FlextTestsDocker",
        "~/flext/flext-tests/src/flext_tests/docker.py::FlextTestsDocker.ci_disables_docker",
        "~/flext/flext-tests/src/flext_tests/docker.py::FlextTestsDocker.skip_if_ci_disables_docker",
        "~/flext/flext-tests/src/flext_tests/docker.py::FlextTestsDocker._resolve_shared_target_config",
        "~/flext/flext-tests/src/flext_tests/docker.py::FlextTestsDocker._resolve_readiness_port",
        "~/flext/flext-tests/src/flext_tests/docker.py::FlextTestsDocker._extract_host_port",
        "~/flext/flext-tests/src/flext_tests/docker.py::FlextTestsDocker.model_post_init"
      ],
      "members_total": 92,
      "members_truncated": true
    },
    {
      "id": 85330,
      "name": "ldap3-entry",
      "level": 0,
      "cohesion": 0.4134,
      "size": 91,
      "dominant_language": "python",
      "description": "Community of 91 nodes",
      "members": [
        "~/flext/flext-ldap/src/flext_ldap/adapters/_ldap3/connection_manager.py::ConnectionManager",
        "~/flext/flext-ldap/src/flext_ldap/adapters/_ldap3/connection_manager.py::ConnectionManager.create_connection",
        "~/flext/flext-ldap/src/flext_ldap/adapters/_ldap3/connection_manager.py::ConnectionManager.create_server",
        "~/flext/flext-ldap/src/flext_ldap/adapters/_ldap3/connection_manager.py::ConnectionManager.handle_tls",
        "~/flext/flext-ldap/src/flext_ldap/adapters/_ldap3/operation_executor.py::OperationExecutor",
        "~/flext/flext-ldap/src/flext_ldap/adapters/_ldap3/operation_executor.py::OperationExecutor._execute",
        "~/flext/flext-ldap/src/flext_ldap/adapters/_ldap3/operation_executor.py::OperationExecutor._extract_error_result",
        "~/flext/flext-ldap/src/flext_ldap/adapters/_ldap3/operation_executor.py::OperationExecutor.execute_add",
        "~/flext/flext-ldap/src/flext_ldap/adapters/_ldap3/operation_executor.py::OperationExecutor.execute_delete",
        "~/flext/flext-ldap/src/flext_ldap/adapters/_ldap3/operation_executor.py::OperationExecutor.execute_modify"
      ],
      "members_total": 91,
      "members_truncated": true
    },
    {
      "id": 85446,
      "name": "utilities-dn",
      "level": 0,
      "cohesion": 0.2722,
      "size": 89,
      "dominant_language": "python",
      "description": "Community of 89 nodes",
      "members": [
        "~/flext/flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py::FlextLdifUtilitiesNormalizeDnTransformer",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py::FlextLdifUtilitiesNormalizeDnTransformer.__init__",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py::FlextLdifUtilitiesNormalizeDnTransformer.validate_dn_components",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py::FlextLdifUtilitiesNormalizeDnTransformer.apply",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py::FlextLdifUtilitiesNormalizeDnTransformer.validate_dn",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py::FlextLdifUtilitiesNormalizeDnTransformer.update_entry",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/_transformer_dn.py::FlextLdifUtilitiesNormalizeDnTransformer._normalize_dn_case_and_spaces",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/collection_ldif.py::FlextLdifUtilitiesCollectionLdif",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/collection_ldif.py::FlextLdifUtilitiesCollectionLdif.find",
        "~/flext/flext-ldif/src/flext_ldif/_utilities/collection_ldif.py::FlextLdifUtilitiesCollectionLdif.normalize_ldif"
      ],
      "members_total": 89,
      "members_truncated": true
    },
    {
      "id": 85757,
      "name": "utilities-plugin",
      "level": 0,
      "cohesion": 0.2505,
      "size": 88,
      "dominant_language": "python",
      "description": "Community of 88 nodes",
      "members": [
        "~/flext/flext-plugin/src/flext_plugin/_utilities/plugin_platform.py::FlextPluginPlatform.Rules",
        "~/flext/flext-plugin/src/flext_plugin/_utilities/plugin_platform.py::FlextPluginPlatform.Rules.validate_business_rules",
        "~/flext/flext-plugin/src/flext_plugin/_utilities/plugin_platform.py::FlextPluginPlatform.PluginExecution",
        "~/flext/flext-plugin/src/flext_plugin/_utilities/plugin_platform.py::FlextPluginPlatform.PluginExecution.__init__",
        "~/flext/flext-plugin/src/flext_plugin/_utilities/plugin_platform.py::FlextPluginPlatform.PluginExecution.create",
        "~/flext/flext-plugin/src/flext_plugin/_utilities/plugin_platform.py::FlextPluginPlatform.PluginExecution.mark_completed",
        "~/flext/flext-plugin/src/flext_plugin/_utilities/plugin_platform.py::FlextPluginPlatform.PluginExecution.mark_started",
        "~/flext/flext-plugin/src/flext_plugin/_utilities/plugin_platform.py::FlextPluginPlatform.PluginRegistry",
        "~/flext/flext-plugin/src/flext_plugin/_utilities/plugin_platform.py::FlextPluginPlatform.PluginRegistry.__init__",
        "~/flext/flext-plugin/src/flext_plugin/_utilities/plugin_platform.py::FlextPluginPlatform.PluginRegistry.create"
      ],
      "members_total": 88,
      "members_truncated": true
    },
    {
      "id": 84025,
      "name": "utilities-output",
      "level": 0,
      "cohesion": 0.0873,
      "size": 86,
      "dominant_language": "python",
      "description": "Community of 86 nodes",
      "members": [
        "~/flext/flext-cli/src/flext_cli/_utilities/commands.py::FlextCliUtilitiesCommands",
        "~/flext/flext-cli/src/flext_cli/_utilities/commands.py::FlextCliUtilitiesCommands.commands_resolve_success_message",
        "~/flext/flext-cli/src/flext_cli/_utilities/commands.py::FlextCliUtilitiesCommands.commands_emit_success_message",
        "~/flext/flext-cli/src/flext_cli/_utilities/commands.py::FlextCliUtilitiesCommands.commands_emit_result_error",
        "~/flext/flext-cli/src/flext_cli/_utilities/output.py::FlextCliUtilitiesOutput",
        "~/flext/flext-cli/src/flext_cli/_utilities/output.py::FlextCliUtilitiesOutput.output_resolve_message_type",
        "~/flext/flext-cli/src/flext_cli/_utilities/output.py::FlextCliUtilitiesOutput.output_resolve_style",
        "~/flext/flext-cli/src/flext_cli/_utilities/output.py::FlextCliUtilitiesOutput.output_message_payload",
        "~/flext/flext-cli/src/flext_cli/_utilities/output.py::FlextCliUtilitiesOutput.output_progress_line",
        "~/flext/flext-cli/src/flext_cli/_utilities/output.py::FlextCliUtilitiesOutput.output_summary_content"
      ],
      "members_total": 86,
      "members_truncated": true
    },
    {
      "id": 85979,
      "name": "utilities-oracle",
      "level": 0,
      "cohesion": 0.2665,
      "size": 78,
      "dominant_language": "python",
      "description": "Community of 78 nodes",
      "members": [
        "~/flext/flext-target-oracle/src/flext_target_oracle/_utilities/client.py::FlextTargetOracle",
        "~/flext/flext-target-oracle/src/flext_target_oracle/_utilities/client.py::FlextTargetOracle.__init__",
        "~/flext/flext-target-oracle/src/flext_target_oracle/_utilities/client.py::FlextTargetOracle.discover_catalog",
        "~/flext/flext-target-oracle/src/flext_target_oracle/_utilities/client.py::FlextTargetOracle.execute",
        "~/flext/flext-target-oracle/src/flext_target_oracle/_utilities/client.py::FlextTargetOracle._ready_result",
        "~/flext/flext-target-oracle/src/flext_target_oracle/_utilities/client.py::FlextTargetOracle._execute_payload",
        "~/flext/flext-target-oracle/src/flext_target_oracle/_utilities/client.py::FlextTargetOracle._parse_singer_payload",
        "~/flext/flext-target-oracle/src/flext_target_oracle/_utilities/client.py::FlextTargetOracle._parse_singer_mapping",
        "~/flext/flext-target-oracle/src/flext_target_oracle/_utilities/client.py::FlextTargetOracle.finalize",
        "~/flext/flext-target-oracle/src/flext_target_oracle/_utilities/client.py::FlextTargetOracle.get_implementation_metrics"
      ],
      "members_total": 78,
      "members_truncated": true
    },
    {
      "id": 84050,
      "name": "services-file",
      "level": 0,
      "cohesion": 0.1818,
      "size": 77,
      "dominant_language": "python",
      "description": "Community of 77 nodes",
      "members": [
        "~/flext/flext-cli/src/flext_cli/services/auth.py::FlextCliAuth",
        "~/flext/flext-cli/src/flext_cli/services/auth.py::FlextCliAuth.validate_credentials",
        "~/flext/flext-cli/src/flext_cli/services/auth.py::FlextCliAuth.save_auth_token",
        "~/flext/flext-cli/src/flext_cli/services/auth.py::FlextCliAuth.fetch_auth_token",
        "~/flext/flext-cli/src/flext_cli/services/auth.py::FlextCliAuth.authenticate",
        "~/flext/flext-cli/src/flext_cli/services/auth.py::FlextCliAuth._resolve_token",
        "~/flext/flext-cli/src/flext_cli/services/auth.py::FlextCliAuth._persist_token",
        "~/flext/flext-cli/src/flext_cli/services/auth.py::FlextCliAuth.clear_auth_tokens",
        "~/flext/flext-cli/src/flext_cli/services/file_tools.py::FlextCliFileTools",
        "~/flext/flext-cli/src/flext_cli/services/file_tools.py::FlextCliFileTools.read_json_file"
      ],
      "members_total": 77,
      "members_truncated": true
    },
    {
      "id": 84687,
      "name": "services-ser


... (truncated, 2520618 chars omitted)
```

</details>
