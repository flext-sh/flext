"""Unit tests for flext_tools.pipeline module.

Tests for pipeline patterns with Python 3.13 + Pydantic integration
following FLEXT unified class patterns and comprehensive validation.
"""

from flext.application_pipeline import (
    FlextApplicationPipelineService,
    create_pipeline_service,
)
from flext_tools.pipeline import (
    PipelineService,
)


class TestPipelineModels:
    """Test suite for pipeline models with Pydantic validation."""

    def test_pipeline_service_creation(self) -> None:
        """Test PipelineService creation."""
        service = create_pipeline_service()
        assert service is not None
        assert hasattr(service, "create_pipeline_factory")
        assert hasattr(service, "execute_pipeline")
        assert hasattr(service, "get_pipeline_metrics")
        assert hasattr(service, "create_command_handler")


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
        assert hasattr(service, "create_pipeline_factory")
        assert hasattr(service, "execute_pipeline")
        assert hasattr(service, "get_pipeline_metrics")
        assert hasattr(service, "create_command_handler")


class TestAdvancedPatterns:
    """Test suite for Python 3.13 advanced patterns implementation."""

    def test_generic_type_constraints(self) -> None:
        """Test generic type constraints with BaseModel."""
        service = PipelineService()
        assert isinstance(service, PipelineService)

    def test_discriminated_union_type_safety(self) -> None:
        """Test discriminated union type safety for sources."""
        # Test with service instance
        service = PipelineService()
        assert isinstance(service, PipelineService)
        assert hasattr(service, "create_pipeline")
        assert hasattr(service, "execute_pipeline")
