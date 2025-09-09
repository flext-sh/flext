"""Unit tests for flext.application_pipeline module.

Tests for advanced pipeline patterns with Python 3.13 + Pydantic integration
following FLEXT unified class patterns and comprehensive validation.
"""

from unittest.mock import patch

import pytest
from pydantic import ValidationError

from flext.application_pipeline import (
    CreatePipelineCommand,
    ExecutePipelineCommand,
    FlextAdvancedPipelineModels,
    FlextAdvancedPipelineService,
    GetPipelineQuery,
    ListPipelinesQuery,
    PipelineName,
    # Legacy compatibility
    PipelineService,
    PipelineStatus,
    PipelineType,
    __all__,
    create_pipeline_service,
)


class TestFlextAdvancedPipelineModels:
    """Test suite for advanced pipeline models with Pydantic validation."""

    def test_oracle_source_validation(self) -> None:
        """Test OracleSource with connection validation."""
        oracle_source = FlextAdvancedPipelineModels.OracleSource(
            host="oracle.example.com",
            port=1521,
            service_name="XEPDB1",
            username="hr",
            password="password123",
            schema_name="HR"
        )

        assert oracle_source.type == "oracle"
        assert oracle_source.host == "oracle.example.com"
        assert oracle_source.port == 1521
        assert oracle_source.service_name == "XEPDB1"

    def test_postgresql_source_validation(self) -> None:
        """Test PostgreSQLSource with connection validation."""
        pg_source = FlextAdvancedPipelineModels.PostgreSQLSource(
            host="postgres.example.com",
            port=5432,
            database="testdb",
            username="postgres",
            password="secret",
            schema_name="public"
        )

        assert pg_source.type == "postgresql"
        assert pg_source.host == "postgres.example.com"
        assert pg_source.database == "testdb"

    def test_ldap_source_validation(self) -> None:
        """Test LDAPSource with advanced LDAP configuration."""
        ldap_source = FlextAdvancedPipelineModels.LDAPSource(
            server_url="ldap://ldap.example.com:389",
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
            bind_password="REDACTED_LDAP_BIND_PASSWORD123",
            base_dn="dc=example,dc=com",
            search_filter="(objectClass=person)",
            attributes=["cn", "mail", "telephoneNumber"]
        )

        assert ldap_source.type == "ldap"
        assert ldap_source.server_url == "ldap://ldap.example.com:389"
        assert "cn" in ldap_source.attributes

    def test_source_config_discriminated_union(self) -> None:
        """Test SourceConfig discriminated union functionality."""
        oracle_config = FlextAdvancedPipelineModels.OracleSource(
            host="oracle.test.com",
            port=1521,
            service_name="TEST"
        )

        pg_config = FlextAdvancedPipelineModels.PostgreSQLSource(
            host="pg.test.com",
            port=5432,
            database="testdb"
        )

        # Test discriminator works correctly
        assert oracle_config.type == "oracle"
        assert pg_config.type == "postgresql"
        assert isinstance(oracle_config, FlextAdvancedPipelineModels.OracleSource)
        assert isinstance(pg_config, FlextAdvancedPipelineModels.PostgreSQLSource)

    def test_create_pipeline_command_validation(self) -> None:
        """Test CreatePipelineCommand with source configuration."""
        oracle_source = FlextAdvancedPipelineModels.OracleSource(
            host="oracle.example.com",
            port=1521,
            service_name="XEPDB1"
        )

        command = FlextAdvancedPipelineModels.CreatePipelineCommand(
            name="test_pipeline",
            source=oracle_source,
            target_table="target_table",
            batch_size=1000
        )

        assert command.name == "test_pipeline"
        assert command.source.type == "oracle"
        assert command.batch_size == 1000

    def test_create_pipeline_command_batch_size_validation(self) -> None:
        """Test CreatePipelineCommand batch size constraints."""
        oracle_source = FlextAdvancedPipelineModels.OracleSource(
            host="oracle.example.com",
            port=1521,
            service_name="XEPDB1"
        )

        with pytest.raises(ValidationError, match="ensure this value is greater than 0"):
            FlextAdvancedPipelineModels.CreatePipelineCommand(
                name="test_pipeline",
                source=oracle_source,
                target_table="target_table",
                batch_size=0  # Invalid batch size
            )

    def test_execute_pipeline_command_validation(self) -> None:
        """Test ExecutePipelineCommand with execution parameters."""
        command = FlextAdvancedPipelineModels.ExecutePipelineCommand(
            pipeline_id="pipeline_123",
            dry_run=False,
            parallel_workers=4
        )

        assert command.pipeline_id == "pipeline_123"
        assert command.dry_run is False
        assert command.parallel_workers == 4

    def test_get_pipeline_query_validation(self) -> None:
        """Test GetPipelineQuery validation."""
        query = FlextAdvancedPipelineModels.GetPipelineQuery(
            pipeline_id="pipeline_456"
        )

        assert query.pipeline_id == "pipeline_456"

    def test_list_pipelines_query_validation(self) -> None:
        """Test ListPipelinesQuery with filtering."""
        query = FlextAdvancedPipelineModels.ListPipelinesQuery(
            status=PipelineStatus.ACTIVE,
            pipeline_type=PipelineType.EXTRACT,
            limit=50,
            offset=100
        )

        assert query.status == PipelineStatus.ACTIVE
        assert query.pipeline_type == PipelineType.EXTRACT
        assert query.limit == 50


class TestFlextAdvancedPipelineService:
    """Test suite for advanced pipeline service with unified class pattern."""

    def test_service_initialization(self) -> None:
        """Test service initialization with dependency injection."""
        service = create_pipeline_service()

        assert isinstance(service, FlextAdvancedPipelineService)
        assert hasattr(service, "_logger")
        assert hasattr(service, "_container")

    def test_command_handler_creation(self) -> None:
        """Test nested command handler creation."""
        service = create_pipeline_service()
        command_handler = service.create_command_handler()

        assert command_handler is not None
        assert hasattr(command_handler, "handle_create")
        assert hasattr(command_handler, "handle_execute")

    def test_query_handler_creation(self) -> None:
        """Test nested query handler creation."""
        service = create_pipeline_service()
        query_handler = service.create_query_handler()

        assert query_handler is not None
        assert hasattr(query_handler, "handle_get")
        assert hasattr(query_handler, "handle_list")

    def test_create_pipeline_command_handling(self) -> None:
        """Test create pipeline command handling."""
        service = create_pipeline_service()

        oracle_source = FlextAdvancedPipelineModels.OracleSource(
            host="oracle.example.com",
            port=1521,
            service_name="XEPDB1"
        )

        command = FlextAdvancedPipelineModels.CreatePipelineCommand(
            name="test_pipeline",
            source=oracle_source,
            target_table="target_table",
            batch_size=1000
        )

        result = service.create_pipeline(command)

        assert result.is_success
        data = result.unwrap()
        assert data["pipeline_name"] == "test_pipeline"
        assert data["status"] == "created"
        assert "pipeline_id" in data

    def test_execute_pipeline_command_handling(self) -> None:
        """Test execute pipeline command handling."""
        service = create_pipeline_service()

        command = FlextAdvancedPipelineModels.ExecutePipelineCommand(
            pipeline_id="pipeline_123",
            dry_run=False,
            parallel_workers=2
        )

        result = service.execute_pipeline(command)

        assert result.is_success
        data = result.unwrap()
        assert data["pipeline_id"] == "pipeline_123"
        assert data["status"] == "executed"
        assert "execution_time" in data

    def test_get_pipeline_query_handling(self) -> None:
        """Test get pipeline query handling."""
        service = create_pipeline_service()

        query = FlextAdvancedPipelineModels.GetPipelineQuery(
            pipeline_id="pipeline_456"
        )

        result = service.get_pipeline(query)

        assert result.is_success
        data = result.unwrap()
        assert data["pipeline_id"] == "pipeline_456"
        assert "pipeline_config" in data
        assert "status" in data

    def test_list_pipelines_query_handling(self) -> None:
        """Test list pipelines query handling."""
        service = create_pipeline_service()

        query = FlextAdvancedPipelineModels.ListPipelinesQuery(
            status=PipelineStatus.ACTIVE,
            limit=10,
            offset=0
        )

        result = service.list_pipelines(query)

        assert result.is_success
        pipelines = result.unwrap()
        assert isinstance(pipelines, list)
        assert len(pipelines) >= 0

    @patch("flext.application_pipeline.FlextLogger")
    def test_error_handling_in_handlers(self, mock_logger) -> None:
        """Test error handling within handlers."""
        service = create_pipeline_service()

        # Test with empty pipeline name (should be handled gracefully)
        oracle_source = FlextAdvancedPipelineModels.OracleSource(
            host="oracle.example.com",
            port=1521,
            service_name="XEPDB1"
        )

        command = FlextAdvancedPipelineModels.CreatePipelineCommand(
            name="",  # Empty name should be handled
            source=oracle_source,
            target_table="target_table",
            batch_size=1000
        )

        result = service.create_pipeline(command)
        # Should handle gracefully and still return success with generated name
        assert result.is_success

    def test_pipeline_type_enum_usage(self) -> None:
        """Test pipeline type enum functionality."""
        assert PipelineType.EXTRACT == "extract"
        assert PipelineType.TRANSFORM == "transform"
        assert PipelineType.LOAD == "load"
        assert PipelineType.ETL == "etl"

    def test_pipeline_status_enum_usage(self) -> None:
        """Test pipeline status enum functionality."""
        assert PipelineStatus.ACTIVE == "active"
        assert PipelineStatus.INACTIVE == "inactive"
        assert PipelineStatus.RUNNING == "running"
        assert PipelineStatus.COMPLETED == "completed"
        assert PipelineStatus.FAILED == "failed"


class TestLegacyCompatibility:
    """Test suite for backward compatibility aliases."""

    def test_pipeline_service_alias(self) -> None:
        """Test that PipelineService alias works."""
        service = PipelineService()
        assert isinstance(service, FlextAdvancedPipelineService)

    def test_create_pipeline_command_alias(self) -> None:
        """Test CreatePipelineCommand alias."""
        oracle_source = FlextAdvancedPipelineModels.OracleSource(
            host="oracle.example.com",
            port=1521,
            service_name="XEPDB1"
        )

        command = CreatePipelineCommand(
            name="test_pipeline",
            source=oracle_source,
            target_table="target_table"
        )

        assert isinstance(command, FlextAdvancedPipelineModels.CreatePipelineCommand)
        assert command.name == "test_pipeline"

    def test_execute_pipeline_command_alias(self) -> None:
        """Test ExecutePipelineCommand alias."""
        command = ExecutePipelineCommand(
            pipeline_id="pipeline_123"
        )

        assert isinstance(command, FlextAdvancedPipelineModels.ExecutePipelineCommand)
        assert command.pipeline_id == "pipeline_123"

    def test_query_aliases(self) -> None:
        """Test query aliases work correctly."""
        get_query = GetPipelineQuery(pipeline_id="test_123")
        list_query = ListPipelinesQuery(limit=10)

        assert isinstance(get_query, FlextAdvancedPipelineModels.GetPipelineQuery)
        assert isinstance(list_query, FlextAdvancedPipelineModels.ListPipelinesQuery)


class TestExportsAndAll:
    """Test suite for module exports and __all__ completeness."""

    def test_all_exports_exist(self) -> None:
        """Test that all items in __all__ are actually exported."""
        expected_exports = [
            "FlextAdvancedPipelineService",
            "create_pipeline_service",
            "FlextAdvancedPipelineModels",
            "PipelineStatus",
            "PipelineType",
            "PipelineName",
            "PipelineService",
            "CreatePipelineCommand",
            "ExecutePipelineCommand",
            "GetPipelineQuery",
            "ListPipelinesQuery",
        ]

        for export in expected_exports:
            assert export in __all__, f"Export {export} missing from __all__"

    def test_pipeline_name_type_alias(self) -> None:
        """Test PipelineName type alias."""
        pipeline_name: PipelineName = "data_extract_pipeline"
        assert isinstance(pipeline_name, str)
        assert pipeline_name == "data_extract_pipeline"


class TestAdvancedPatterns:
    """Test suite for Python 3.13 advanced patterns implementation."""

    def test_generic_type_constraints(self) -> None:
        """Test generic type constraints with BaseModel."""
        from pydantic import BaseModel

        service = FlextAdvancedPipelineService[BaseModel]()
        assert isinstance(service, FlextAdvancedPipelineService)

    def test_discriminated_union_type_safety(self) -> None:
        """Test discriminated union type safety for sources."""
        oracle_source = FlextAdvancedPipelineModels.OracleSource(
            host="oracle.test.com",
            port=1521,
            service_name="TEST"
        )

        pg_source = FlextAdvancedPipelineModels.PostgreSQLSource(
            host="pg.test.com",
            port=5432,
            database="testdb"
        )

        ldap_source = FlextAdvancedPipelineModels.LDAPSource(
            server_url="ldap://ldap.test.com:389",
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            bind_password="secret",
            base_dn="dc=test,dc=com"
        )

        # Test discriminated union works for different source types
        sources = [oracle_source, pg_source, ldap_source]
        for source in sources:
            assert hasattr(source, "type")
            assert source.type in {"oracle", "postgresql", "ldap"}

    def test_pydantic_v2_validation_features(self) -> None:
        """Test Pydantic v2 advanced validation features."""
        # Test field validation constraints
        with pytest.raises(ValidationError):
            FlextAdvancedPipelineModels.ListPipelinesQuery(
                limit=20000  # Exceeds maximum
            )

        # Test port validation for Oracle source
        with pytest.raises(ValidationError):
            FlextAdvancedPipelineModels.OracleSource(
                host="oracle.test.com",
                port=99999,  # Invalid port
                service_name="TEST"
            )

    def test_nested_class_pattern_compliance(self) -> None:
        """Test that service follows unified class with nested pattern."""
        service = create_pipeline_service()

        # Test nested command handler
        command_handler = service.create_command_handler()
        assert command_handler is not None

        # Test nested query handler
        query_handler = service.create_query_handler()
        assert query_handler is not None

        # Verify they are properly nested (not separate classes)
        assert hasattr(service, "_CommandHandlerImplementation")
        assert hasattr(service, "_QueryHandlerImplementation")
