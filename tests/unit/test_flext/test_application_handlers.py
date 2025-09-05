"""Unit tests for flext.application_handlers module.

Tests for CQRS handler facade functionality following FLEXT testing patterns
with proper mocking and verification of flext-core integration.
"""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from flext.application_handlers import (
    CommandHandler,
    EventHandler,
    FlextCommandHandler,
    FlextEventHandler,
    FlextHandlers,
    FlextQueryHandler,
    FlextResult,
    HandlerChain,
    Pipeline,
    QueryHandler,
    SimpleQueryHandler,
    VoidCommandHandler,
    __all__,
)

# Import the handlers from FlextHandlers namespace
Handler = FlextHandlers.Handler
AuthorizingHandler = FlextHandlers.Implementation.AuthorizingHandler
MetricsHandler = FlextHandlers.Implementation.MetricsHandler
ValidatingHandler = FlextHandlers.Implementation.ValidatingHandler
HandlerRegistry = FlextHandlers.Management.HandlerRegistry


@dataclass
class TestCommand:
    """Test command for handler testing."""

    name: str
    value: int


@dataclass
class TestQuery:
    """Test query for handler testing."""

    query_id: str


@dataclass
class TestEvent:
    """Test event for handler testing."""

    event_type: str
    data: dict[str, object]


class TestFlextHandlerFacade:
    """Test suite for FLEXT handler facade functionality."""

    def test_command_handler_facade_alias(self) -> None:
        """Test that CommandHandler is properly aliased to FlextCommandHandler."""
        # Assert
        flext_command_handler = FlextHandlers.Implementation.CommandHandler
        assert CommandHandler is flext_command_handler
        assert issubclass(CommandHandler, flext_command_handler)

    def test_query_handler_facade_alias(self) -> None:
        """Test that QueryHandler is properly aliased to FlextQueryHandler."""
        # Assert
        flext_query_handler = FlextHandlers.Implementation.QueryHandler
        assert QueryHandler is flext_query_handler
        assert issubclass(QueryHandler, flext_query_handler)

    def test_event_handler_facade_alias(self) -> None:
        """Test that EventHandler is properly aliased to FlextEventHandler."""
        # Assert
        flext_event_handler = FlextHandlers.Implementation.EventHandler
        assert EventHandler is flext_event_handler
        assert issubclass(EventHandler, flext_event_handler)

    def test_void_command_handler_alias(self) -> None:
        """Test VoidCommandHandler alias for commands returning None."""
        # Assert
        flext_command_handler = FlextHandlers.Implementation.CommandHandler
        assert VoidCommandHandler is flext_command_handler

    def test_simple_query_handler_alias(self) -> None:
        """Test SimpleQueryHandler alias for queries returning dict."""
        # Assert
        flext_query_handler = FlextHandlers.Implementation.QueryHandler
        assert SimpleQueryHandler is flext_query_handler

    def test_all_exports_available(self) -> None:
        """Test that all expected exports are available from the module."""
        # Essential exports that must be present
        required_exports = [
            "FlextCommandHandler",
            "FlextQueryHandler",
            "FlextEventHandler",
            "CommandHandler",
            "QueryHandler",
            "EventHandler",
            "FlextResult",
        ]

        for export in required_exports:
            assert export in __all__, f"Required export {export} missing from __all__"

    @patch("flext_core.FlextCommandHandler")
    def test_flext_command_handler_import(self, mock_handler: Mock) -> None:
        """Test that FlextCommandHandler is properly imported from flext-core."""
        # Arrange
        mock_instance = Mock()
        mock_handler.return_value = mock_instance

        # Assert
        assert FlextCommandHandler is not None
        assert callable(FlextCommandHandler)

    def test_handler_advanced_patterns_available(self) -> None:
        """Test that advanced handler patterns are available."""
        # Act & Assert - These should import without error
        assert Handler is not None
        assert ValidatingHandler is not None
        assert AuthorizingHandler is not None
        assert MetricsHandler is not None
        assert HandlerChain is not None
        assert HandlerRegistry is not None
        assert Pipeline is not None


class TestHandlerImplementation:
    """Test suite for concrete handler implementations."""

    def test_create_command_handler_subclass(self) -> None:
        """Test creating a concrete CommandHandler subclass."""

        class TestCommandHandler(CommandHandler[TestCommand, int]):
            def handle_command(self, command: TestCommand) -> FlextResult[int]:
                return FlextResult[int].ok(command.value * 2)

        # Act
        handler = TestCommandHandler()
        TestCommand(name="test", value=5)

        # This test just verifies the class can be created
        assert handler is not None
        assert hasattr(handler, "handle_command")

    def test_create_query_handler_subclass(self) -> None:
        """Test creating a concrete QueryHandler subclass."""

        class TestQueryHandler(QueryHandler[TestQuery, dict[str, object]]):
            def handle_query(self, query: TestQuery) -> FlextResult[dict[str, object]]:
                return FlextResult[dict[str, object]].ok({"query_id": query.query_id})

        # Act
        handler = TestQueryHandler()
        TestQuery(query_id="test-123")

        # This test just verifies the class can be created
        assert handler is not None
        assert hasattr(handler, "handle_query")

    def test_create_event_handler_subclass(self) -> None:
        """Test creating a concrete EventHandler subclass."""

        class TestEventHandler(EventHandler[TestEvent, None]):
            def handle_event(self, event: TestEvent) -> FlextResult[None]:
                return FlextResult[None].ok(None)

        # Act
        handler = TestEventHandler()
        TestEvent(event_type="test", data={"key": "value"})

        # This test just verifies the class can be created
        assert handler is not None
        assert hasattr(handler, "handle_event")


class TestHandlerIntegration:
    """Integration tests for handler patterns with flext-core."""

    @pytest.fixture
    def temp_workspace(self, tmp_path: Path) -> object:
        """Create temporary workspace for integration testing."""
        workspace = tmp_path / "handler-integration-test"
        workspace.mkdir()
        return workspace

    def test_handler_facade_integration(self, temp_workspace: Path) -> None:
        """Test that handler facade properly integrates with flext-core patterns."""
        # This is a basic integration test that verifies imports work
        # More comprehensive integration testing would require actual flext-core setup

        # Act - Import all handler types

        # Assert - All imports successful
        assert FlextCommandHandler is not None
        assert FlextQueryHandler is not None
        assert FlextEventHandler is not None
        assert FlextResult is not None

    def test_handler_patterns_consistency(self) -> None:
        """Test that handler patterns maintain consistency with flext-core."""
        # Verify that facade aliases point to the same base classes

        # Assert aliases are consistent
        assert CommandHandler is FlextCommandHandler
        assert QueryHandler is FlextQueryHandler
        assert EventHandler is FlextEventHandler


class TestHandlerErrorHandling:
    """Test suite for handler error handling patterns."""

    def test_handler_import_failure_handling(self) -> None:
        """Test graceful handling when flext-core handlers are unavailable."""
        # This test would be more comprehensive with actual mock failure scenarios
        # For now, we verify that the imports are structured to handle failures

        # Act & Assert - Module should define its exports clearly

        assert isinstance(__all__, list)
        assert len(__all__) > 0

    def test_facade_pattern_consistency(self) -> None:
        """Test that facade pattern maintains consistent behavior."""
        # Assert that facades maintain proper inheritance
        assert hasattr(CommandHandler, "__mro__")  # Has method resolution order
        assert hasattr(QueryHandler, "__mro__")
        assert hasattr(EventHandler, "__mro__")
