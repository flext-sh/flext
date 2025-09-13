"""Unit tests for flext.application_handlers module.

Tests for advanced CQRS handler patterns with Python 3.13 + Pydantic integration
following FLEXT unified class patterns and advanced type safety.
"""

from unittest.mock import patch

import pytest
from pydantic import BaseModel, ValidationError

from flext.application_handlers import (
    CommandHandler,
    EventHandler,
    FlextAdvancedHandlerModels,
    FlextAdvancedHandlerService,
    HandlerId,
    HandlerStatus,
    HandlerType,
    Priority,
    QueryHandler,
    __all__,
    create_handler_service,
)


class TestFlextAdvancedHandlerModels:
    """Test suite for advanced handler models with Pydantic validation."""

    def test_handler_context_creation(self) -> None:
        """Test HandlerContext with UUID generation and validation."""
        context = FlextAdvancedHandlerModels.HandlerContext(
            user_id="test_user", priority=Priority.HIGH
        )

        assert context.user_id == "test_user"
        assert context.priority == Priority.HIGH
        assert context.correlation_id is not None
        assert len(str(context.correlation_id)) == 36  # UUID format

    def test_data_processing_command_validation(self) -> None:
        """Test DataProcessingCommand with Pydantic v2 validation."""
        command = FlextAdvancedHandlerModels.DataProcessingCommand(
            data_source="file:///test/data.csv",
            batch_size=1000,
            enable_validation=True,
            target_format="json",
        )

        assert command.type == "data_processing"
        assert command.data_source == "file:///test/data.csv"
        assert command.batch_size == 1000
        assert command.enable_validation is True

    def test_data_processing_command_uri_validation(self) -> None:
        """Test DataProcessingCommand URI validation."""
        with pytest.raises(ValidationError, match="Data source must be a valid URI"):
            FlextAdvancedHandlerModels.DataProcessingCommand(
                data_source="invalid_uri", batch_size=1000
            )

    def test_data_processing_command_business_rules(self) -> None:
        """Test DataProcessingCommand business rule validation."""
        command = FlextAdvancedHandlerModels.DataProcessingCommand(
            data_source="file:///test/data.csv",
            batch_size=60000,  # Large batch
            enable_validation=True,
        )

        result = command.validate_business_rules()
        assert result.is_failure
        assert result.error
        assert "Large batch sizes require validation to be disabled" in result.error

    def test_user_management_command_validation(self) -> None:
        """Test UserManagementCommand with email and action validation."""
        command = FlextAdvancedHandlerModels.UserManagementCommand(
            user_email="test@example.com",
            action="create",
            user_data={"name": "Test User", "role": "user"},
        )

        assert command.type == "user_management"
        assert command.user_email == "test@example.com"
        assert command.action == "create"

    def test_user_management_command_email_validation(self) -> None:
        """Test UserManagementCommand email validation."""
        with pytest.raises(ValidationError, match="regex"):
            FlextAdvancedHandlerModels.UserManagementCommand(
                user_email="invalid_email", action="create"
            )

    def test_user_management_command_business_rules(self) -> None:
        """Test UserManagementCommand REDACTED_LDAP_BIND_PASSWORD deletion protection."""
        command = FlextAdvancedHandlerModels.UserManagementCommand(
            user_email="REDACTED_LDAP_BIND_PASSWORD@REDACTED_LDAP_BIND_PASSWORD.com", action="delete"
        )

        result = command.validate_business_rules()
        assert result.is_failure
        assert result.error
        assert "Cannot delete REDACTED_LDAP_BIND_PASSWORD users" in result.error

    def test_data_retrieval_query_validation(self) -> None:
        """Test DataRetrievalQuery with filtering and pagination."""
        query = FlextAdvancedHandlerModels.DataRetrievalQuery(
            filters={"status": "active", "type": "premium"},
            sort_by="created_at",
            sort_direction="desc",
            limit=50,
            offset=100,
        )

        assert query.type == "data_retrieval"
        assert query.filters["status"] == "active"
        assert query.sort_by == "created_at"
        assert query.limit == 50

    def test_aggregation_query_validation(self) -> None:
        """Test AggregationQuery with metric calculation."""
        query = FlextAdvancedHandlerModels.AggregationQuery(
            group_by=["category", "status"], metrics=["count", "sum"], date_range=30
        )

        assert query.type == "aggregation"
        assert query.group_by == ["category", "status"]
        assert query.metrics == ["count", "sum"]
        assert query.date_range == 30

    def test_data_processed_event_validation(self) -> None:
        """Test DataProcessedEvent with processing metrics."""
        event = FlextAdvancedHandlerModels.DataProcessedEvent(
            records_processed=1000,
            processing_time_ms=5000,
            error_count=2,
            success_rate=99.8,
        )

        assert event.type == "data_processed"
        assert event.records_processed == 1000
        assert event.processing_time_ms == 5000
        assert event.success_rate == 99.8

    def test_discriminated_unions(self) -> None:
        """Test discriminated union functionality for commands."""
        data_command = FlextAdvancedHandlerModels.DataProcessingCommand(
            data_source="file:///test.csv", batch_size=1000
        )

        user_command = FlextAdvancedHandlerModels.UserManagementCommand(
            user_email="test@example.com", action="create", user_data={"name": "Test"}
        )

        # Test that discriminator works
        assert data_command.type == "data_processing"
        assert user_command.type == "user_management"
        assert isinstance(
            data_command, FlextAdvancedHandlerModels.DataProcessingCommand
        )
        assert isinstance(
            user_command, FlextAdvancedHandlerModels.UserManagementCommand
        )


class TestFlextAdvancedHandlerService:
    """Test suite for advanced handler service with unified class pattern."""

    def test_service_initialization(self) -> None:
        """Test service initialization with dependency injection."""
        service = create_handler_service()

        assert isinstance(service, FlextAdvancedHandlerService)
        assert hasattr(service, "_logger")
        assert hasattr(service, "_container")

    def test_command_handler_creation(self) -> None:
        """Test nested command handler creation."""
        service = create_handler_service()
        command_handler = service.create_command_handler()

        assert command_handler is not None
        assert hasattr(command_handler, "handle_data_processing")
        assert hasattr(command_handler, "handle_user_management")

    def test_query_handler_creation(self) -> None:
        """Test nested query handler creation."""
        service = create_handler_service()
        query_handler = service.create_query_handler()

        assert query_handler is not None
        assert hasattr(query_handler, "handle_data_retrieval")
        assert hasattr(query_handler, "handle_aggregation")

    def test_event_handler_creation(self) -> None:
        """Test nested event handler creation."""
        service = create_handler_service()
        event_handler = service.create_event_handler()

        assert event_handler is not None
        assert hasattr(event_handler, "handle_data_processed")

    def test_data_processing_command_handling(self) -> None:
        """Test data processing command handling."""
        service = create_handler_service()
        command = FlextAdvancedHandlerModels.DataProcessingCommand(
            data_source="file:///test/data.csv",
            batch_size=1000,
            enable_validation=True,
            target_format="json",
        )

        result = service.handle_command(command)

        assert result.is_success
        data = result.unwrap()
        assert data["command_type"] == "data_processing"
        assert data["batch_size"] == 1000
        assert data["status"] == "processed"

    def test_user_management_command_handling(self) -> None:
        """Test user management command handling."""
        service = create_handler_service()
        command = FlextAdvancedHandlerModels.UserManagementCommand(
            user_email="test@example.com",
            action="create",
            user_data={"name": "Test User", "role": "user"},
        )

        result = service.handle_command(command)

        assert result.is_success
        data = result.unwrap()
        assert data["command_type"] == "user_management"
        assert data["user_email"] == "test@example.com"
        assert data["status"] == "completed"

    def test_data_retrieval_query_handling(self) -> None:
        """Test data retrieval query handling."""
        service = create_handler_service()
        query = FlextAdvancedHandlerModels.DataRetrievalQuery(
            filters={"status": "active"},
            sort_by="created_at",
            sort_direction="desc",
            limit=100,
            offset=0,
        )

        result = service.handle_query(query)

        assert result.is_success
        data = result.unwrap()
        assert data["query_type"] == "data_retrieval"
        assert "data" in data
        assert "total_count" in data

    def test_aggregation_query_handling(self) -> None:
        """Test aggregation query handling."""
        service = create_handler_service()
        query = FlextAdvancedHandlerModels.AggregationQuery(
            group_by=["status"], metrics=["count", "average"], date_range=30
        )

        result = service.handle_query(query)

        assert result.is_success
        data = result.unwrap()
        assert data["query_type"] == "aggregation"
        assert "aggregates" in data

    def test_unknown_command_handling(self) -> None:
        """Test handling of unknown command types."""
        service = create_handler_service()

        # Create a mock command that doesn't match discriminated union
        class UnknownCommand:
            type = "unknown"

        unknown_command = UnknownCommand()
        result = service.handle_command(unknown_command)

        assert result.is_failure
        assert result.error
        assert "Unknown command type" in result.error

    @patch("flext.application_handlers.FlextLogger")
    def test_error_handling_in_handlers(self, mock_logger: object) -> None:
        """Test error handling within handlers."""
        # Note: mock_logger parameter unused in this test implementation
        _ = mock_logger  # Acknowledge unused parameter
        service = create_handler_service()

        # Test with command that might cause business rule violation
        command = FlextAdvancedHandlerModels.DataProcessingCommand(
            data_source="file:///test/data.csv",
            batch_size=60000,  # This should trigger business rule failure
            enable_validation=True,
        )

        # The service should handle this gracefully
        result = service.handle_command(command)
        assert result.is_success  # Handler should process despite business rule warning


class TestLegacyCompatibility:
    """Test suite for backward compatibility aliases."""

    def test_command_handler_alias(self) -> None:
        """Test that CommandHandler alias works."""
        handler = CommandHandler()
        assert isinstance(handler, FlextAdvancedHandlerService)

    def test_query_handler_alias(self) -> None:
        """Test that QueryHandler alias works."""
        handler = QueryHandler()
        assert isinstance(handler, FlextAdvancedHandlerService)

    def test_event_handler_alias(self) -> None:
        """Test that EventHandler alias works."""
        handler = EventHandler()
        assert isinstance(handler, FlextAdvancedHandlerService)


class TestExportsAndAll:
    """Test suite for module exports and __all__ completeness."""

    def test_all_exports_exist(self) -> None:
        """Test that all items in __all__ are actually exported."""
        # Test main exports
        expected_exports = [
            "FlextAdvancedHandlerService",
            "create_handler_service",
            "FlextAdvancedHandlerModels",
            "HandlerStatus",
            "HandlerType",
            "Priority",
            "HandlerId",
            "CommandHandler",
            "QueryHandler",
            "EventHandler",
        ]

        for export in expected_exports:
            assert export in __all__, f"Export {export} missing from __all__"

    def test_enums_functionality(self) -> None:
        """Test enum types functionality."""
        assert HandlerStatus.ACTIVE == "active"
        assert HandlerType.COMMAND == "command"
        assert Priority.HIGH == "high"

    def test_handler_id_type_alias(self) -> None:
        """Test HandlerId type alias."""
        handler_id: HandlerId = "test-handler-123"
        assert isinstance(handler_id, str)
        assert handler_id == "test-handler-123"


class TestAdvancedPatterns:
    """Test suite for Python 3.13 advanced patterns implementation."""

    def test_generic_type_constraints(self) -> None:
        """Test generic type constraints with BaseModel."""
        service = FlextAdvancedHandlerService[BaseModel]()
        assert isinstance(service, FlextAdvancedHandlerService)

    def test_protocol_compliance(self) -> None:
        """Test that handlers implement expected protocols."""
        service = create_handler_service()
        command_handler = service.create_command_handler()

        # Test that handler has expected methods (Protocol compliance)
        assert callable(getattr(command_handler, "handle_data_processing", None))
        assert callable(getattr(command_handler, "handle_user_management", None))

    def test_discriminated_union_pattern(self) -> None:
        """Test discriminated union type safety."""
        # Create different command types
        data_cmd = FlextAdvancedHandlerModels.DataProcessingCommand(
            data_source="file:///test.csv", batch_size=1000
        )

        user_cmd = FlextAdvancedHandlerModels.UserManagementCommand(
            user_email="test@example.com", action="create", user_data={"name": "Test"}
        )

        service = create_handler_service()

        # Test that discriminated union routing works
        data_result = service.handle_command(data_cmd)
        user_result = service.handle_command(user_cmd)

        assert data_result.is_success
        assert user_result.is_success
        assert data_result.unwrap()["command_type"] == "data_processing"
        assert user_result.unwrap()["command_type"] == "user_management"

    def test_pydantic_v2_validation_features(self) -> None:
        """Test Pydantic v2 advanced validation features."""
        # Test field validation
        with pytest.raises(ValidationError):
            FlextAdvancedHandlerModels.DataRetrievalQuery(
                limit=20000  # Exceeds maximum of 10000
            )

        # Test model validation
        with pytest.raises(ValidationError, match="Create action requires user data"):
            FlextAdvancedHandlerModels.UserManagementCommand(
                user_email="test@example.com",
                action="create",
                # Missing user_data
            )
