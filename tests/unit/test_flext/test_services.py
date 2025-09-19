"""Tests for flext.services module - FLEXT Unified Services.

Tests the unified service coordination pattern with proper flext-core integration.
"""

from unittest.mock import Mock, patch

from flext.application_handlers import FlextApplicationHandlerService
from flext.services import FlextUnifiedServices


class TestFlextUnifiedServices:
    """Test cases for FlextUnifiedServices unified class pattern."""

    def test_init(self) -> None:
        """Test service initialization."""
        service = FlextUnifiedServices()
        assert service is not None
        assert hasattr(service, "_logger")
        assert hasattr(service, "_core_services")

    def test_handler_services_init(self) -> None:
        """Test nested handler services initialization."""
        service = FlextUnifiedServices()
        handler_services = service._HandlerServices(service)
        assert handler_services is not None
        assert handler_services._services == service

    def test_create_command_handler(self) -> None:
        """Test command handler creation."""
        service = FlextUnifiedServices()
        handler_services = service._HandlerServices(service)

        # Test actual implementation without mocking - uses FlextApplicationHandlerService
        result = handler_services.create_command_handler()
        assert result is not None
        # Verify it returns the expected service type
        assert isinstance(result, FlextApplicationHandlerService)

    def test_create_event_handler(self) -> None:
        """Test event handler creation."""
        service = FlextUnifiedServices()
        handler_services = service._HandlerServices(service)

        # Test actual implementation without mocking - uses FlextApplicationHandlerService
        result = handler_services.create_event_handler()
        assert result is not None
        # Verify it returns the expected service type
        assert isinstance(result, FlextApplicationHandlerService)

    def test_create_query_handler(self) -> None:
        """Test query handler creation."""
        service = FlextUnifiedServices()
        handler_services = service._HandlerServices(service)

        # Test actual implementation without mocking - uses FlextApplicationHandlerService
        result = handler_services.create_query_handler()
        assert result is not None
        # Verify it returns the expected service type
        assert isinstance(result, FlextApplicationHandlerService)

    def test_pipeline_services_init(self) -> None:
        """Test nested pipeline services initialization."""
        service = FlextUnifiedServices()
        pipeline_services = service._PipelineServices(service)
        assert pipeline_services is not None
        assert pipeline_services._services == service

    def test_pipeline_service_property(self) -> None:
        """Test pipeline service property."""
        service = FlextUnifiedServices()
        pipeline_services = service._PipelineServices(service)

        # Test pipeline service property
        result = pipeline_services.pipeline_service
        assert result is not None

    def test_execute_pipeline_workflow(self) -> None:
        """Test execute pipeline workflow."""
        service = FlextUnifiedServices()
        pipeline_services = service._PipelineServices(service)

        # Mock the pipeline service execute_pipeline method
        mock_pipeline_service = Mock()
        mock_pipeline_service.execute_pipeline.return_value = Mock(
            is_success=True,
            value={"test": "result"},
        )
        pipeline_services._pipeline_service = mock_pipeline_service

        result = pipeline_services.execute_pipeline_workflow("test_pipeline")
        assert result is not None
        assert result.success

    def test_execute_pipeline_workflow_failure(self) -> None:
        """Test execute pipeline workflow with failure."""
        service = FlextUnifiedServices()
        pipeline_services = service._PipelineServices(service)

        # Mock the pipeline service execute_pipeline method to return failure
        mock_pipeline_service = Mock()
        mock_pipeline_service.execute_pipeline.return_value = Mock(
            is_success=False,
            error="Pipeline failed",
        )
        pipeline_services._pipeline_service = mock_pipeline_service

        result = pipeline_services.execute_pipeline_workflow("test_pipeline")
        assert result is not None
        assert not result.success

    def test_pipeline_command_classes(self) -> None:
        """Test pipeline command class attributes."""
        service = FlextUnifiedServices()
        pipeline_services = service._PipelineServices(service)

        # Test that command classes are accessible
        assert hasattr(pipeline_services, "CreatePipelineCommand")
        assert hasattr(pipeline_services, "ExecutePipelineCommand")
        assert hasattr(pipeline_services, "GetPipelineQuery")
        assert hasattr(pipeline_services, "ListPipelinesQuery")

    def test_core_services_init(self) -> None:
        """Test nested core services initialization."""
        service = FlextUnifiedServices()
        core_services = service._CoreServices(service)
        assert core_services is not None
        assert core_services._core_services == service._core_services

    def test_core_services_property(self) -> None:
        """Test core services property."""
        service = FlextUnifiedServices()
        core_services = service._CoreServices(service)

        # Test core_services property
        result = core_services.core_services
        assert result is None  # Should be None initially

    def test_test_services_init(self) -> None:
        """Test nested test services initialization."""
        service = FlextUnifiedServices()
        test_services = service._TestServices(service)
        assert test_services is not None
        assert test_services._services == service

    def test_execute_unified_test(self) -> None:
        """Test unified test execution."""
        service = FlextUnifiedServices()
        test_services = service._TestServices(service)

        # Mock subprocess.run to avoid actual test execution
        with patch("flext.services.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="test output", stderr="")
            result = test_services.execute_unified_test()
            assert result is not None
            assert result.success

    def test_execute_unified_test_with_module(self) -> None:
        """Test unified test execution with specific module."""
        service = FlextUnifiedServices()
        test_services = service._TestServices(service)

        # Mock subprocess.run to avoid actual test execution
        with patch("flext.services.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="test output", stderr="")
            result = test_services.execute_unified_test(module="test_module")
            assert result is not None
            assert result.success

    def test_execute_quality_check(self) -> None:
        """Test quality check execution."""
        service = FlextUnifiedServices()
        test_services = service._TestServices(service)

        # Mock subprocess.run to avoid actual command execution
        with patch("flext.services.subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="quality check output",
                stderr="",
            )
            result = test_services.execute_quality_check()
            assert result is not None
            assert result.success

    def test_execute_quality_check_with_fix(self) -> None:
        """Test quality check execution with fix option."""
        service = FlextUnifiedServices()
        test_services = service._TestServices(service)

        # Mock subprocess.run to avoid actual command execution
        with patch("flext.services.subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="quality check output",
                stderr="",
            )
            result = test_services.execute_quality_check(fix=True)
            assert result is not None
            assert result.success

    def test_execute_build_check(self) -> None:
        """Test build check execution."""
        service = FlextUnifiedServices()
        test_services = service._TestServices(service)

        # Mock subprocess.run and Path to avoid actual command execution
        with (
            patch("flext.services.subprocess.run") as mock_run,
            patch("flext.services.Path") as mock_path,
        ):
            mock_run.return_value = Mock(returncode=0, stdout="build output", stderr="")
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.__truediv__.return_value.exists.return_value = True

            result = test_services.execute_build_check()
            assert result is not None
            assert result.success

    def test_execute_build_check_with_module(self) -> None:
        """Test build check execution with specific module."""
        service = FlextUnifiedServices()
        test_services = service._TestServices(service)

        # Mock subprocess.run and Path to avoid actual command execution
        with (
            patch("flext.services.subprocess.run") as mock_run,
            patch("flext.services.Path") as mock_path,
        ):
            mock_run.return_value = Mock(returncode=0, stdout="build output", stderr="")
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.__truediv__.return_value.exists.return_value = True

            result = test_services.execute_build_check(module="test_module")
            assert result is not None
            assert result.success

    def test_service_integration(self) -> None:
        """Test integration between different service types."""
        service = FlextUnifiedServices()

        # Test that all nested services can be created
        handler_services = service._HandlerServices(service)
        pipeline_services = service._PipelineServices(service)
        core_services = service._CoreServices(service)
        test_services = service._TestServices(service)

        assert handler_services is not None
        assert pipeline_services is not None
        assert core_services is not None
        assert test_services is not None

    def test_create_test_services(self) -> None:
        """Test create test services method."""
        service = FlextUnifiedServices()
        result = service.create_test_services()
        assert result is not None
        assert isinstance(result, service._TestServices)

    def test_create_handler_services(self) -> None:
        """Test create handler services method."""
        service = FlextUnifiedServices()
        result = service.create_handler_services()
        assert result is not None
        assert isinstance(result, service._HandlerServices)

    def test_create_pipeline_services(self) -> None:
        """Test create pipeline services method."""
        service = FlextUnifiedServices()
        result = service.create_pipeline_services()
        assert result is not None
        assert isinstance(result, service._PipelineServices)

    def test_create_core_services(self) -> None:
        """Test create core services method."""
        service = FlextUnifiedServices()
        result = service.create_core_services()
        assert result is not None
        assert isinstance(result, service._CoreServices)

    def test_initialize_all_services(self) -> None:
        """Test initialize all services method."""
        service = FlextUnifiedServices()
        result = service.initialize_all_services()
        assert result is not None
        assert result.success
        assert "handler_services" in result.value
        assert "pipeline_services" in result.value
        assert "core_services" in result.value

    def test_service_with_data(self) -> None:
        """Test service initialization with data."""
        test_data = {"test_key": "test_value"}
        service = FlextUnifiedServices(**test_data)
        assert service is not None
