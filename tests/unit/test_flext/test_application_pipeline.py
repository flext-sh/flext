"""Unit tests for flext.application_pipeline module.

Tests for pipeline application services following FLEXT testing patterns
with comprehensive coverage of CQRS commands, queries, and handlers.
"""
from typing import Any

import pytest
from flext_core import FlextResult

from flext.application_pipeline import (
    CreatePipelineCommand,
    ExecutePipelineCommand,
    FlextPipelineApplicationServices,
    GetPipelineQuery,
    ListPipelinesQuery,
    PipelineService,
)


class TestFlextPipelineApplicationServices:
    """Test suite for FlextPipelineApplicationServices following enterprise patterns."""

    @pytest.fixture
    def pipeline_service(self) -> FlextPipelineApplicationServices:
        """Create pipeline service instance for testing."""
        return FlextPipelineApplicationServices()

    def test_pipeline_service_initialization(
        self,
        pipeline_service: FlextPipelineApplicationServices
    ) -> None:
        """Test pipeline service initialization."""
        # Assert
        assert pipeline_service is not None
        assert isinstance(pipeline_service, FlextPipelineApplicationServices)

    def test_backward_compatibility_alias(self) -> None:
        """Test that PipelineService alias works correctly."""
        # Assert
        assert PipelineService is FlextPipelineApplicationServices

        # Test instantiation through alias
        service = PipelineService()
        assert isinstance(service, FlextPipelineApplicationServices)

    @pytest.mark.asyncio
    async def test_create_pipeline_command_handler(
        self,
        pipeline_service: FlextPipelineApplicationServices
    ) -> None:
        """Test create pipeline command handling."""
        # Arrange
        command = CreatePipelineCommand(name="test-pipeline")

        # Act
        result = await pipeline_service.handle_create_command(command)

        # Assert
        assert result.is_success is True
        assert isinstance(result.value, dict)
        assert "message" in result.value

    @pytest.mark.asyncio
    async def test_execute_pipeline_command_handler(
        self,
        pipeline_service: FlextPipelineApplicationServices
    ) -> None:
        """Test execute pipeline command handling."""
        # Arrange
        command = ExecutePipelineCommand(pipeline_id="pipeline-123")

        # Act
        result = await pipeline_service.handle_execute_command(command)

        # Assert
        assert result.is_success is True
        assert isinstance(result.value, dict)
        assert "message" in result.value

    @pytest.mark.asyncio
    async def test_get_pipeline_query_handler(
        self,
        pipeline_service: FlextPipelineApplicationServices
    ) -> None:
        """Test get pipeline query handling."""
        # Arrange
        query = GetPipelineQuery(pipeline_id="pipeline-123")

        # Act
        result = await pipeline_service.handle_get_query(query)

        # Assert
        assert result.is_success is True
        assert isinstance(result.value, dict)
        assert "message" in result.value

    @pytest.mark.asyncio
    async def test_list_pipelines_query_handler(
        self,
        pipeline_service: FlextPipelineApplicationServices
    ) -> None:
        """Test list pipelines query handling."""
        # Arrange
        query = ListPipelinesQuery(limit=5, offset=10)

        # Act
        result = await pipeline_service.handle_list_query(query)

        # Assert
        assert result.is_success is True
        assert isinstance(result.value, list)
        assert len(result.value) == 0  # Empty list for current implementation

    @pytest.mark.asyncio
    async def test_create_pipeline_service_method(
        self,
        pipeline_service: FlextPipelineApplicationServices
    ) -> None:
        """Test high-level create pipeline service method."""
        # Arrange
        command = CreatePipelineCommand(name="integration-pipeline")

        # Act
        result = await pipeline_service.create_pipeline(command)

        # Assert
        assert result.is_success is True
        assert isinstance(result.value, dict)

    @pytest.mark.asyncio
    async def test_execute_pipeline_service_method(
        self,
        pipeline_service: FlextPipelineApplicationServices
    ) -> None:
        """Test high-level execute pipeline service method."""
        # Arrange
        command = ExecutePipelineCommand(pipeline_id="exec-pipeline-456")

        # Act
        result = await pipeline_service.execute_pipeline(command)

        # Assert
        assert result.is_success is True
        assert isinstance(result.value, dict)

    @pytest.mark.asyncio
    async def test_get_pipeline_service_method(
        self,
        pipeline_service: FlextPipelineApplicationServices
    ) -> None:
        """Test high-level get pipeline service method."""
        # Arrange
        query = GetPipelineQuery(pipeline_id="get-pipeline-789")

        # Act
        result = await pipeline_service.get_pipeline(query)

        # Assert
        assert result.is_success is True
        assert isinstance(result.value, dict)

    @pytest.mark.asyncio
    async def test_list_pipelines_service_method(
        self,
        pipeline_service: FlextPipelineApplicationServices
    ) -> None:
        """Test high-level list pipelines service method."""
        # Arrange
        query = ListPipelinesQuery(limit=20, offset=5)

        # Act
        result = await pipeline_service.list_pipelines(query)

        # Assert
        assert result.is_success is True
        assert isinstance(result.value, list)


class TestPipelineCommands:
    """Test suite for pipeline command models."""

    def test_create_pipeline_command_validation(self) -> None:
        """Test CreatePipelineCommand validation."""
        # Arrange & Act
        command = CreatePipelineCommand(name="valid-pipeline")

        # Assert
        assert command.name == "valid-pipeline"
        assert len(command.name) <= 100

    def test_create_pipeline_command_max_length(self) -> None:
        """Test CreatePipelineCommand name length validation."""
        # Arrange
        long_name = "a" * 101  # Exceeds max_length=100

        # Act & Assert
        with pytest.raises(ValueError):
            CreatePipelineCommand(name=long_name)

    def test_execute_pipeline_command_validation(self) -> None:
        """Test ExecutePipelineCommand validation."""
        # Arrange & Act
        command = ExecutePipelineCommand(pipeline_id="exec-12345")

        # Assert
        assert command.pipeline_id == "exec-12345"

    def test_execute_pipeline_command_required_field(self) -> None:
        """Test ExecutePipelineCommand requires pipeline_id."""
        # Act & Assert
        with pytest.raises(ValueError):
            ExecutePipelineCommand()  # type: ignore[call-arg]


class TestPipelineQueries:
    """Test suite for pipeline query models."""

    def test_get_pipeline_query_validation(self) -> None:
        """Test GetPipelineQuery validation."""
        # Arrange & Act
        query = GetPipelineQuery(pipeline_id="query-12345")

        # Assert
        assert query.pipeline_id == "query-12345"

    def test_get_pipeline_query_required_field(self) -> None:
        """Test GetPipelineQuery requires pipeline_id."""
        # Act & Assert
        with pytest.raises(ValueError):
            GetPipelineQuery()  # type: ignore[call-arg]

    def test_list_pipelines_query_defaults(self) -> None:
        """Test ListPipelinesQuery default values."""
        # Arrange & Act
        query = ListPipelinesQuery()

        # Assert
        assert query.limit == 10  # Default value
        assert query.offset == 0  # Default value

    def test_list_pipelines_query_custom_values(self) -> None:
        """Test ListPipelinesQuery with custom values."""
        # Arrange & Act
        query = ListPipelinesQuery(limit=50, offset=25)

        # Assert
        assert query.limit == 50
        assert query.offset == 25

    def test_list_pipelines_query_validation_limits(self) -> None:
        """Test ListPipelinesQuery validation constraints."""
        # Test limit constraints
        with pytest.raises(ValueError):
            ListPipelinesQuery(limit=0)  # Below minimum ge=1

        with pytest.raises(ValueError):
            ListPipelinesQuery(limit=101)  # Above maximum le=100

        # Test offset constraints
        with pytest.raises(ValueError):
            ListPipelinesQuery(offset=-1)  # Below minimum ge=0


class TestPipelineServiceIntegration:
    """Integration tests for pipeline service components."""

    @pytest.fixture
    def temp_workspace(self, tmp_path) -> Any:
        """Create temporary workspace for integration testing."""
        workspace = tmp_path / "pipeline-integration-test"
        workspace.mkdir()
        return workspace

    @pytest.mark.asyncio
    async def test_pipeline_service_complete_workflow(self, temp_workspace) -> None:
        """Test complete pipeline service workflow."""
        # Arrange
        service = FlextPipelineApplicationServices()

        # Act - Create pipeline
        create_command = CreatePipelineCommand(name="workflow-test-pipeline")
        create_result = await service.create_pipeline(create_command)

        # Act - List pipelines
        list_query = ListPipelinesQuery(limit=10)
        list_result = await service.list_pipelines(list_query)

        # Act - Get pipeline (using mock ID since creation doesn't return real ID yet)
        get_query = GetPipelineQuery(pipeline_id="mock-pipeline-id")
        get_result = await service.get_pipeline(get_query)

        # Act - Execute pipeline
        execute_command = ExecutePipelineCommand(pipeline_id="mock-pipeline-id")
        execute_result = await service.execute_pipeline(execute_command)

        # Assert all operations successful
        assert create_result.is_success is True
        assert list_result.is_success is True
        assert get_result.is_success is True
        assert execute_result.is_success is True

    @pytest.mark.asyncio
    async def test_pipeline_service_error_handling(self) -> None:
        """Test pipeline service error handling capabilities."""
        # This test demonstrates the structure for error handling
        # Actual error scenarios would be added as the implementation matures

        service = FlextPipelineApplicationServices()

        # Test with valid commands - should not raise exceptions
        try:
            command = CreatePipelineCommand(name="error-test")
            result = await service.create_pipeline(command)
            assert isinstance(result, FlextResult)
        except Exception as e:
            pytest.fail(f"Service should handle errors gracefully: {e}")

    def test_backward_compatibility_aliases(self) -> None:
        """Test that all backward compatibility aliases work correctly."""
        # Test service alias
        assert PipelineService is FlextPipelineApplicationServices

        # Test command aliases
        assert CreatePipelineCommand is FlextPipelineApplicationServices.CreatePipelineCommand
        assert ExecutePipelineCommand is FlextPipelineApplicationServices.ExecutePipelineCommand

        # Test query aliases
        assert GetPipelineQuery is FlextPipelineApplicationServices.GetPipelineQuery
        assert ListPipelinesQuery is FlextPipelineApplicationServices.ListPipelinesQuery

    def test_consolidated_pattern_structure(self) -> None:
        """Test that the consolidated pattern structure is properly implemented."""
        # Verify nested classes exist
        service_class = FlextPipelineApplicationServices

        assert hasattr(service_class, "CreatePipelineCommand")
        assert hasattr(service_class, "ExecutePipelineCommand")
        assert hasattr(service_class, "GetPipelineQuery")
        assert hasattr(service_class, "ListPipelinesQuery")

        # Verify handler methods exist
        service = service_class()
        assert hasattr(service, "handle_create_command")
        assert hasattr(service, "handle_execute_command")
        assert hasattr(service, "handle_get_query")
        assert hasattr(service, "handle_list_query")

        # Verify high-level service methods exist
        assert hasattr(service, "create_pipeline")
        assert hasattr(service, "execute_pipeline")
        assert hasattr(service, "get_pipeline")
        assert hasattr(service, "list_pipelines")
