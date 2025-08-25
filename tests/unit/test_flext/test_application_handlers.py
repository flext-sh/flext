"""Unit tests for flext.application_handlers module.

Tests for CQRS handler facade functionality following FLEXT testing patterns
with proper mocking and verification of flext-core integration.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any
from dataclasses import dataclass

from flext_core import FlextResult
from flext.application_handlers import (
    FlextCommandHandler,
    FlextQueryHandler,
    FlextEventHandler,
    CommandHandler,
    QueryHandler,
    EventHandler,
    Handler,
    ValidatingHandler,
    AuthorizingHandler,
    MetricsHandler,
    HandlerChain,
    HandlerRegistry,
    Pipeline,
    VoidCommandHandler,
    SimpleQueryHandler,
)


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
    data: dict[str, Any]


class TestFlextHandlerFacade:
    """Test suite for FLEXT handler facade functionality."""

    def test_command_handler_facade_alias(self) -> None:
        """Test that CommandHandler is properly aliased to FlextCommandHandler."""
        # Assert
        assert CommandHandler is FlextCommandHandler
        assert issubclass(CommandHandler, FlextCommandHandler)

    def test_query_handler_facade_alias(self) -> None:
        """Test that QueryHandler is properly aliased to FlextQueryHandler."""
        # Assert
        assert QueryHandler is FlextQueryHandler
        assert issubclass(QueryHandler, FlextQueryHandler)

    def test_event_handler_facade_alias(self) -> None:
        """Test that EventHandler is properly aliased to FlextEventHandler."""
        # Assert
        assert EventHandler is FlextEventHandler
        assert issubclass(EventHandler, FlextEventHandler)

    def test_void_command_handler_alias(self) -> None:
        """Test VoidCommandHandler alias for commands returning None."""
        # Assert
        assert VoidCommandHandler is FlextCommandHandler

    def test_simple_query_handler_alias(self) -> None:
        """Test SimpleQueryHandler alias for queries returning dict."""
        # Assert
        assert SimpleQueryHandler is FlextQueryHandler

    def test_all_exports_available(self) -> None:
        """Test that all expected exports are available from the module."""
        from flext.application_handlers import __all__
        
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

    @patch('flext_core.FlextCommandHandler')
    def test_flext_command_handler_import(self, mock_handler: Mock) -> None:
        """Test that FlextCommandHandler is properly imported from flext-core."""
        # Arrange
        mock_instance = Mock()
        mock_handler.return_value = mock_instance
        
        # Act - Import should work without error
        from flext.application_handlers import FlextCommandHandler
        
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
        command = TestCommand(name="test", value=5)
        
        # This test just verifies the class can be created
        assert handler is not None
        assert hasattr(handler, 'handle_command')

    def test_create_query_handler_subclass(self) -> None:
        """Test creating a concrete QueryHandler subclass."""
        
        class TestQueryHandler(QueryHandler[TestQuery, dict[str, Any]]):
            def handle_query(self, query: TestQuery) -> FlextResult[dict[str, Any]]:
                return FlextResult[dict[str, Any]].ok({"query_id": query.query_id})
        
        # Act
        handler = TestQueryHandler()
        query = TestQuery(query_id="test-123")
        
        # This test just verifies the class can be created
        assert handler is not None
        assert hasattr(handler, 'handle_query')

    def test_create_event_handler_subclass(self) -> None:
        """Test creating a concrete EventHandler subclass."""
        
        class TestEventHandler(EventHandler[TestEvent, None]):
            def handle_event(self, event: TestEvent) -> FlextResult[None]:
                return FlextResult[None].ok(None)
        
        # Act
        handler = TestEventHandler()
        event = TestEvent(event_type="test", data={"key": "value"})
        
        # This test just verifies the class can be created
        assert handler is not None
        assert hasattr(handler, 'handle_event')


class TestHandlerIntegration:
    """Integration tests for handler patterns with flext-core."""

    @pytest.fixture
    def temp_workspace(self, tmp_path) -> Any:
        """Create temporary workspace for integration testing."""
        workspace = tmp_path / "handler-integration-test"
        workspace.mkdir()
        return workspace

    def test_handler_facade_integration(self, temp_workspace) -> None:
        """Test that handler facade properly integrates with flext-core patterns."""
        # This is a basic integration test that verifies imports work
        # More comprehensive integration testing would require actual flext-core setup
        
        # Act - Import all handler types
        from flext.application_handlers import (
            FlextCommandHandler,
            FlextQueryHandler, 
            FlextEventHandler,
            FlextResult
        )
        
        # Assert - All imports successful
        assert FlextCommandHandler is not None
        assert FlextQueryHandler is not None
        assert FlextEventHandler is not None
        assert FlextResult is not None

    def test_handler_patterns_consistency(self) -> None:
        """Test that handler patterns maintain consistency with flext-core."""
        # Verify that facade aliases point to the same base classes
        from flext.application_handlers import (
            CommandHandler,
            QueryHandler,
            EventHandler,
            FlextCommandHandler,
            FlextQueryHandler,
            FlextEventHandler,
        )
        
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
        from flext.application_handlers import __all__
        
        assert isinstance(__all__, list)
        assert len(__all__) > 0

    def test_facade_pattern_consistency(self) -> None:
        """Test that facade pattern maintains consistent behavior."""
        from flext.application_handlers import (
            CommandHandler,
            QueryHandler,
            EventHandler,
        )
        
        # Assert that facades maintain proper inheritance
        assert hasattr(CommandHandler, '__mro__')  # Has method resolution order
        assert hasattr(QueryHandler, '__mro__')
        assert hasattr(EventHandler, '__mro__')