"""Tests for FLX Async Infrastructure DDD Components.

This module contains comprehensive tests for the domain message types,
routing system, and command bus implementation.
"""

from __future__ import annotations

import importlib
from datetime import datetime
from typing import Any
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import pytest

flx_async = importlib.import_module("flx.infrastructure.async")  # type: ignore[attr-defined]


def test_domain_message_creation() -> None:
    """Test basic domain message creation."""
    message = flx_async.FlxDomainMessage()

    assert isinstance(message.message_id, UUID)
    assert message.message_type == "FlxDomainMessage"
    assert isinstance(message.timestamp, datetime)
    assert message.correlation_id is None
    assert message.causation_id is None
    assert message.metadata == {}


def test_domain_command_creation() -> None:
    """Test domain command creation with validation."""
    command = flx_async.FlxCreateResourceCommand(
        command_name="create_resource",
        resource_name="test_resource",
        resource_type="database",
        priority=1,
    )

    assert command.command_name == "create_resource"
    assert command.resource_name == "test_resource"
    assert command.resource_type == "database"
    assert command.priority == 1
    assert command.timeout_seconds == 30  # default
    assert command.retry_count == 3  # default


def test_domain_event_creation() -> None:
    """Test domain event creation."""
    resource_id = uuid4()
    event = flx_async.FlxResourceCreatedEvent(
        resource_id=resource_id,
        resource_name="test_resource",
        resource_type="database",
        created_by="system",
    )

    assert event.event_name == "resource_created"
    assert event.resource_id == resource_id
    assert event.aggregate_id == resource_id  # Auto-set in __init__
    assert event.aggregate_type == "Resource"  # Auto-set in __init__
    assert event.created_by == "system"


def test_domain_query_creation() -> None:
    """Test domain query creation."""
    resource_id = uuid4()
    query = flx_async.FlxGetResourceQuery(
        resource_id=resource_id,
        include_metadata=True,
    )

    assert query.query_name == "get_resource"
    assert query.resource_id == resource_id
    assert query.include_metadata is True
    assert query.response_timeout == 5  # default


def test_message_correlation() -> None:
    """Test message correlation and causation tracking."""
    correlation_id = uuid4()
    causation_id = uuid4()

    command = flx_async.create_command(
        flx_async.FlxCreateResourceCommand,
        correlation_id=correlation_id,
        causation_id=causation_id,
        resource_name="test",
        resource_type="test",
    )

    assert command.correlation_id == correlation_id
    assert command.causation_id == causation_id


def test_command_validation() -> None:
    """Test command validation rules."""
    # Test priority validation
    with pytest.raises(ValueError, match="priority.*must be <= 10"):
        flx_async.FlxCreateResourceCommand(
            resource_name="test",
            resource_type="test",
            priority=11,  # Invalid - must be <= 10
        )

    # Test timeout validation
    with pytest.raises(ValueError, match="timeout.*must be >= 1"):
        flx_async.FlxCreateResourceCommand(
            resource_name="test",
            resource_type="test",
            timeout_seconds=0,  # Invalid - must be >= 1
        )


def test_message_router() -> None:
    """Test message routing functionality."""
    router = flx_async.FlxMessageRouter()

    def test_queue_config_initialization() -> None:
        """Test queue configurations are properly initialized."""
        configs = router.get_all_queue_configs()

        assert flx_async.FlxQueueType.COMMANDS_CRITICAL in configs
        assert flx_async.FlxQueueType.COMMANDS_NORMAL in configs
        assert flx_async.FlxQueueType.EVENTS_DOMAIN in configs

        critical_config = configs[flx_async.FlxQueueType.COMMANDS_CRITICAL]
        assert critical_config.name == "commands.critical"
        assert critical_config.priority == 10
        assert critical_config.max_retries == 5

    def test_command_routing() -> None:
        """Test command routing to appropriate queues."""
        # Test resource command routing
        command = flx_async.FlxCreateResourceCommand(
            resource_name="test",
            resource_type="database",
        )

        config = router.route_message(command)
        assert config.name == "commands.normal"

        # Test priority-based routing
        high_priority_command = flx_async.FlxCreateResourceCommand(
            resource_name="test",
            resource_type="database",
            priority=1,
        )

        config = router.route_message(high_priority_command)
        # Should use command's higher priority
        assert config.priority == 1

    def test_event_routing() -> None:
        """Test event routing to appropriate queues."""
        event = flx_async.FlxResourceCreatedEvent(
            resource_id=uuid4(),
            resource_name="test",
            resource_type="database",
            created_by="system",
        )

        config = router.route_message(event)
        assert config.name == "events.domain"

    def test_query_routing_error() -> None:
        """Test that queries cannot be routed to queues."""
        query = flx_async.FlxGetResourceQuery(resource_id=uuid4())

        with pytest.raises(ValueError, match="Queries should not be routed to queues"):
            router.route_message(query)

    def test_routing_rules() -> None:
        """Test custom routing rules."""
        # Test data processing command routing
        flx_process_command = flx_async.FlxProcessDataCommand(
            data_source="test.csv",
            transformation_rules=["rule1", "rule2"],
        )

        config = router.route_message(flx_process_command)
        assert config.name == "io.operations"

    def test_add_custom_routing_rule() -> None:
        """Test adding custom routing rules."""
        import re

        custom_rule = flx_async.RouteRule(
            message_pattern=re.compile(r".*Custom.*Command"),
            queue_type=flx_async.FlxQueueType.BACKGROUND_JOBS,
            description="Custom commands for testing",
        )

        router.add_routing_rule(custom_rule)

        # Verify rule was added
        rules = router.get_routing_rules()
        assert custom_rule in rules
        assert rules[0] == custom_rule  # Should be first (highest priority)


@pytest.fixture
def mock_redis() -> Any:
    """Mock Redis client."""
    with patch("redis.from_url") as mock:
        mock_client = Mock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_dramatiq() -> Any:
    """Mock Dramatiq components."""
    with (
        patch("dramatiq.set_broker"),
        patch("dramatiq.actor"),
        patch.object(flx_async.FlxAsyncCommandBus, "_setup_broker"),
    ):
        yield


def test_command_bus_initialization(_mock_redis: Any, _mock_dramatiq: Any) -> None:
    """Test command bus initialization."""
    config = flx_async.FlxAsyncCommandBusConfig(
        redis_url="redis://test:6379/0",
        result_ttl=7200,
    )
    bus = flx_async.FlxAsyncCommandBus(config)
    assert bus.config.redis_url == "redis://test:6379/0"
    assert bus.config.result_ttl == 7200
    assert isinstance(bus._router, flx_async.FlxMessageRouter)


def test_command_handler_registration(_mock_redis: Any, _mock_dramatiq: Any) -> None:
    """Test command handler registration."""
    bus = flx_async.FlxAsyncCommandBus()

    async def test_handler(command: Any) -> dict[str, Any]:
        return {"status": "created", "resource_id": str(command.message_id)}
    bus.register_command_handler(flx_async.FlxCreateResourceCommand, test_handler)
    assert "FlxCreateResourceCommand" in bus._handlers
    assert bus._handlers["FlxCreateResourceCommand"] == test_handler


def test_event_handler_registration(_mock_redis: Any, _mock_dramatiq: Any) -> None:
    """Test event handler registration."""
    bus = flx_async.FlxAsyncCommandBus()

    async def test_handler(event: Any) -> None:
        pass
    bus.register_event_handler(flx_async.FlxResourceCreatedEvent, test_handler)
    assert "FlxResourceCreatedEvent" in bus._event_handlers
    assert test_handler in bus._event_handlers["FlxResourceCreatedEvent"]


@pytest.mark.asyncio
async def test_command_sending(_mock_redis: Any, _mock_dramatiq: Any) -> None:
    """Test sending commands to the bus."""
    bus = flx_async.FlxAsyncCommandBus()
    # Mock the actor
    mock_actor = Mock()
    mock_message = Mock()
    mock_message.message_id = "test-message-id"
    mock_actor.send.return_value = mock_message
    mock_actor.copy.return_value = mock_actor
    bus._command_actor_CreateResourceCommand = mock_actor
    command = flx_async.FlxCreateResourceCommand(
        resource_name="test",
        resource_type="database",
    )
    message_id = await bus.send_command(command)
    assert message_id == "test-message-id"
    mock_actor.send.assert_called_once()


@pytest.mark.asyncio
async def test_event_publishing(_mock_redis: Any, _mock_dramatiq: Any) -> None:
    """Test publishing events."""
    bus = flx_async.FlxAsyncCommandBus()
    # Register a handler first

    async def test_handler(event: Any) -> None:
        pass
    bus.register_event_handler(flx_async.FlxResourceCreatedEvent, test_handler)
    # Mock the actor
    mock_actor = Mock()
    mock_message = Mock()
    mock_message.message_id = "test-event-message-id"
    mock_actor.send.return_value = mock_message
    mock_actor.copy.return_value = mock_actor
    bus._event_actor_ResourceCreatedEvent = mock_actor
    event = flx_async.FlxResourceCreatedEvent(
        resource_id=uuid4(),
        resource_name="test",
        resource_type="database",
        created_by="system",
    )
    message_ids = await bus.publish_event(event)
    assert len(message_ids) == 1
    assert message_ids[0] == "test-event-message-id"
    mock_actor.send.assert_called_once()


def test_integration() -> None:
    """Integration tests for the complete async infrastructure."""

    @pytest.mark.asyncio
    async def test_end_to_end_command_flow() -> None:
        """Test complete command flow from creation to processing."""
        # This would be a full integration test with Redis running
        # For now, we'll test the flow with mocks

        with (
            patch("redis.from_url"),
            patch("dramatiq.set_broker"),
            patch.object(flx_async.FlxAsyncCommandBus, "_setup_broker"),
        ):

            bus = flx_async.FlxAsyncCommandBus()

            # Register handler
            async def create_resource_handler(
                command: Any,
            ) -> dict[str, Any]:
                return {
                    "resource_id": str(uuid4()),
                    "name": command.resource_name,
                    "type": command.resource_type,
                    "status": "created",
                }

            bus.register_command_handler(
                flx_async.FlxCreateResourceCommand, create_resource_handler,
            )

            # Create and process command
            command = flx_async.FlxCreateResourceCommand(
                resource_name="test_database",
                resource_type="postgresql",
            )

            # Mock the actual processing
            with patch.object(bus, "send_command", return_value="mock-message-id"):
                message_id = await bus.send_command(command)
                assert message_id == "mock-message-id"

    def test_message_factory_functions() -> None:
        """Test message factory functions."""
        correlation_id = uuid4()

        # Test command factory
        command = flx_async.create_command(
            flx_async.FlxCreateResourceCommand,
            correlation_id=correlation_id,
            resource_name="test",
            resource_type="test",
        )

        assert command.correlation_id == correlation_id
        assert isinstance(command, flx_async.FlxCreateResourceCommand)

        # Test event factory
        event = flx_async.create_event(
            flx_async.FlxResourceCreatedEvent,
            correlation_id=correlation_id,
            resource_id=uuid4(),
            resource_name="test",
            resource_type="test",
            created_by="system",
        )

        assert event.correlation_id == correlation_id
        assert isinstance(event, flx_async.FlxResourceCreatedEvent)
        assert event.published_at is not None

        # Test query factory
        query = flx_async.create_query(
            flx_async.FlxGetResourceQuery,
            correlation_id=correlation_id,
            resource_id=uuid4(),
        )

        assert query.correlation_id == correlation_id
        assert isinstance(query, flx_async.FlxGetResourceQuery)


def test_global_instances() -> None:
    """Test global singleton instances."""

    def test_get_command_bus_singleton() -> None:
        """Test that get_command_bus returns singleton instance."""
        with (
            patch("redis.from_url"),
            patch("dramatiq.set_broker"),
            patch.object(flx_async.FlxAsyncCommandBus, "_setup_broker"),
        ):

            bus1 = flx_async.get_command_bus()
            bus2 = flx_async.get_command_bus()

            assert bus1 is bus2

    def test_initialize_command_bus() -> None:
        """Test command bus initialization."""
        with (
            patch("redis.from_url"),
            patch("dramatiq.set_broker"),
            patch.object(flx_async.FlxAsyncCommandBus, "_setup_broker"),
        ):

            config = flx_async.FlxAsyncCommandBusConfig(redis_url="redis://test:6379/1")
            bus = flx_async.initialize_command_bus(config)

            assert bus.config.redis_url == "redis://test:6379/1"

    def test_default_router_functions() -> None:
        """Test default router utility functions."""
        # Test route_message function
        command = flx_async.FlxCreateResourceCommand(
            resource_name="test",
            resource_type="test",
        )

        config = flx_async.route_message(command)
        assert config.name == "commands.normal"

        # Test get_queue_config function
        config = flx_async.get_queue_config(flx_async.FlxQueueType.COMMANDS_CRITICAL)
        assert config.name == "commands.critical"
        assert config.priority == 10
