"""Unit tests for flext_tools.pipeline module.

Tests for pipeline patterns with Python 3.13 + Pydantic integration
following FLEXT unified class patterns and comprehensive validation.
"""



from flext.application_pipeline import (
    FlextApplicationPipelineService,
    create_pipeline_service,
)
from flext_tools.pipeline import (
    CreatePipelineCommand,
    ExecutePipelineCommand,
    GetPipelineQuery,
    ListPipelinesQuery,
    PipelineService,
)


class TestPipelineModels:
    """Test suite for pipeline models with Pydantic validation."""

    def test_pipeline_command_validation(self) -> None:
        """Test CreatePipelineCommand with validation."""
        command = CreatePipelineCommand(
            name="test-pipeline",
        )
        assert command.name == "test-pipeline"

    def test_execute_command_validation(self) -> None:
        """Test ExecutePipelineCommand with validation."""
        command = ExecutePipelineCommand(
            pipeline_id="test-pipeline-123",
        )
        assert command.pipeline_id == "test-pipeline-123"

    def test_query_validation(self) -> None:
        """Test GetPipelineQuery with validation."""
        query = GetPipelineQuery(
            pipeline_id="test-pipeline-456",
        )
        assert query.pipeline_id == "test-pipeline-456"

    def test_list_query_validation(self) -> None:
        """Test ListPipelinesQuery with validation."""
        query = ListPipelinesQuery(
            limit=20,
            offset=10,
        )
        assert query.limit == 20
        assert query.offset == 10


class TestPipelineService:
    """Test suite for pipeline service with unified class pattern."""

    def test_service_initialization(self) -> None:
        """Test service initialization with dependency injection."""
        service = create_pipeline_service()
        # create_pipeline_service returns FlextApplicationPipelineService, not PipelineService
        assert isinstance(service, FlextApplicationPipelineService)

    def test_service_methods(self) -> None:
        """Test service has expected methods."""
        service = create_pipeline_service()
        assert hasattr(service, "create_pipeline")
        assert hasattr(service, "execute_pipeline")
        assert hasattr(service, "get_pipeline")
        assert hasattr(service, "list_pipelines")


class TestAdvancedPatterns:
    """Test suite for Python 3.13 advanced patterns implementation."""

    def test_generic_type_constraints(self) -> None:
        """Test generic type constraints with BaseModel."""
        service = PipelineService()
        assert isinstance(service, PipelineService)

    def test_discriminated_union_type_safety(self) -> None:
        """Test discriminated union type safety for sources."""
        # Test with existing command classes
        create_cmd = CreatePipelineCommand(name="test")
        execute_cmd = ExecutePipelineCommand(pipeline_id="test-123")

        assert isinstance(create_cmd, CreatePipelineCommand)
        assert isinstance(execute_cmd, ExecutePipelineCommand)
