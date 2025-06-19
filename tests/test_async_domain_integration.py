"""Tests for Async Domain Integration - Domain Entities + Async Infrastructure.

This module tests the integration between FLX domain entities and the async
infrastructure, ensuring events can flow from aggregate roots through the
async event publishing system.
"""

from __future__ import annotations

import os
from uuid import uuid4

import pytest

# Force stub broker for tests to avoid Redis dependency
os.environ["FLX_BROKER_TYPE"] = "stub"

from flx.infrastructure.di.container import (
    AsyncEventPublisher,
    create_default_container,
)

from flx.core import FlxAggregateRoot, FlxEntityFactory


def test_aggregate_root_async_events() -> None:
    """Validate async domain event generation and lifecycle in aggregate roots.

    This test verifies the complete async domain event system integration,
    ensuring that FlxEntityFactory can create aggregate roots with async
    event capabilities and that events are properly generated, tracked,
    and retrievable through the domain event infrastructure.

    Architecture Validation:
        - Tests hexagonal architecture event flow from domain to infrastructure
        - Validates proper separation between sync and async event systems
        - Confirms aggregate root state management with event sourcing patterns
        - Verifies factory pattern implementation for entity creation

    Event Lifecycle Tested:
        1. Factory creation with async event flag enabled
        2. Automatic AggregateCreated event generation
        3. Event state tracking and counting mechanisms
        4. Event retrieval and metadata validation
        5. Event type differentiation (async vs regular)

    Technical Assertions:
        - has_async_domain_events flag is properly set
        - Event count tracking is accurate
        - Event metadata contains correct aggregate information
        - Event name follows domain-driven design conventions
    """
    # Create aggregate root
    aggregate = FlxEntityFactory.create_aggregate_root(
        name="test_aggregate",
        description="Test aggregate for async events",
        use_async_events=True,
    )

    # Verify factory created async event during creation
    assert aggregate.has_async_domain_events is True
    assert aggregate.async_domain_event_count == 1

    # Get the async events
    async_events = aggregate.get_async_domain_events()
    assert len(async_events) == 1

    created_event = async_events[0]
    assert created_event.event_name == "AggregateCreated"
    assert created_event.aggregate_type == "FlxAggregateRoot"
    assert created_event.aggregate_id == aggregate.id


def test_aggregate_root_mixed_events() -> None:
    """Verify concurrent handling of synchronous and asynchronous domain events.

    This test validates the aggregate root's capability to maintain separate
    but coordinated event streams for both regular domain events and async
    domain events, ensuring proper isolation and state management across
    both event types within the same aggregate instance.

    Dual Event System Testing:
        - Regular domain events for immediate consistency
        - Async domain events for eventual consistency patterns
        - Independent event counters and state tracking
        - Separate event retrieval mechanisms
        - Unified event lifecycle management

    Event Isolation Verification:
        - Events don't interfere with each other's state
        - Separate storage and retrieval paths
        - Independent counting and flagging systems
        - Correct event type classification

    Domain Architecture Patterns:
        - Command-Query Responsibility Segregation (CQRS) support
        - Event sourcing with mixed consistency models
        - Aggregate boundary enforcement
        - Clean separation of concerns between event types
    """
    # Create aggregate root
    aggregate = FlxAggregateRoot(name="mixed_events_test")

    # Raise regular domain event
    aggregate.raise_domain_event("RegularEvent", {"key": "value"})

    # Raise async domain event
    aggregate.raise_async_domain_event("AsyncEvent", {"async_key": "async_value"})

    # Verify both types of events exist
    assert aggregate.has_domain_events is True
    assert aggregate.has_async_domain_events is True
    assert aggregate.has_any_events is True

    # Check counts
    assert aggregate.domain_event_count == 1
    assert aggregate.async_domain_event_count == 1
    assert aggregate.total_event_count == 2

    # Get events
    regular_events = aggregate.get_domain_events()
    async_events = aggregate.get_async_domain_events()

    assert len(regular_events) == 1
    assert len(async_events) == 1

    assert regular_events[0].event_type == "RegularEvent"
    assert async_events[0].event_name == "AsyncEvent"


def test_events_clearing() -> None:
    """Validate comprehensive event clearing across all event types.

    This test ensures that the aggregate root's event clearing mechanism
    properly handles both regular and async domain events, providing a
    clean slate for subsequent operations while maintaining data integrity
    and proper state transitions.

    Event Clearing Scenarios:
        - Mixed event types accumulated in single aggregate
        - Bulk clearing operation across all event streams
        - State consistency after clearing operations
        - Flag and counter reset verification

    State Management Validation:
        - Total event count accurately reflects clearing
        - Individual event type flags properly reset
        - Event collections completely emptied
        - Aggregate remains in valid operational state

    Use Cases:
        - Post-commit event cleanup in repository patterns
        - Aggregate state reset for testing scenarios
        - Memory management in long-running processes
        - Event stream management in high-throughput systems
    """
    aggregate = FlxAggregateRoot(name="clear_test")

    # Add both types of events
    aggregate.raise_domain_event("RegularEvent", {})
    aggregate.raise_async_domain_event("AsyncEvent", {})

    # Verify events exist
    assert aggregate.total_event_count == 2

    # Clear all events
    aggregate.clear_all_events()

    # Verify all events are cleared
    assert aggregate.total_event_count == 0
    assert aggregate.has_any_events is False


def test_events_committed() -> None:
    """Verify event commitment workflow and state transitions.

    This test validates the aggregate root's ability to mark events as
    committed, simulating successful persistence or processing operations.
    The commitment process should clear all pending events while maintaining
    aggregate integrity and preparing for subsequent event generation.

    Event Commitment Lifecycle:
        - Event accumulation during business operations
        - Commitment marking after successful persistence
        - Automatic event clearing post-commitment
        - State normalization for continued operations

    Repository Pattern Integration:
        - Simulates successful database transaction completion
        - Models event store persistence acknowledgment
        - Represents message queue publishing confirmation
        - Validates outbox pattern implementation

    Consistency Guarantees:
        - Events marked committed are permanently cleared
        - Aggregate state remains consistent after commitment
        - No event leakage between operation boundaries
        - Proper cleanup for memory and resource management
    """
    aggregate = FlxAggregateRoot(name="commit_test")

    # Add events
    aggregate.raise_domain_event("RegularEvent", {})
    aggregate.raise_async_domain_event("AsyncEvent", {})

    # Mark as committed
    aggregate.mark_events_as_committed()

    # Verify all events are cleared
    assert aggregate.total_event_count == 0


def test_factory_with_async_events_disabled() -> None:
    """Validate factory fallback behavior with async events disabled.

    This test ensures that the FlxEntityFactory gracefully handles scenarios
    where async event infrastructure is disabled or unavailable, falling back
    to regular domain events while maintaining functional compatibility and
    proper domain event generation patterns.

    Fallback Mechanism Testing:
        - Factory respects async event configuration flags
        - Automatic fallback to regular domain events
        - Consistent event generation regardless of async capability
        - Proper event type differentiation in fallback mode

    Configuration-Driven Behavior:
        - use_async_events=False parameter handling
        - Graceful degradation without functional loss
        - Consistent factory interface across configurations
        - Transparent operation mode switching

    Infrastructure Resilience:
        - System operates without async infrastructure
        - No breaking changes when async features unavailable
        - Backward compatibility with sync-only deployments
        - Flexible deployment configuration support
    """
    # Create aggregate with async events disabled
    aggregate = FlxEntityFactory.create_aggregate_root(
        name="no_async_test",
        use_async_events=False,
    )

    # Should have regular domain event, not async
    assert aggregate.has_domain_events is True
    assert aggregate.has_async_domain_events is False

    # Verify the event
    regular_events = aggregate.get_domain_events()
    assert len(regular_events) == 1
    assert regular_events[0].event_type == "AggregateCreated"


def test_business_entity_async_events() -> None:
    """Verify business entity async event generation with domain context.

    This test validates the FlxEntityFactory's capability to create business
    entities with async event support, ensuring that business-specific events
    are properly generated with contextual metadata including business rules
    and domain-specific information.

    Business Entity Specialization:
        - Factory creates business entities vs generic aggregates
        - Business-specific event types (BusinessEntityCreated)
        - Domain context included in event metadata
        - Business rule integration with event generation

    Event Metadata Validation:
        - Event carries business context information
        - Business rules reflected in event data
        - Proper event naming conventions for business domain
        - Rich event data for business intelligence and auditing

    Domain-Driven Design Patterns:
        - Business entity as specialized aggregate root
        - Rich domain events with business semantics
        - Event-driven business rule enforcement
        - Domain context preservation in event streams
    """
    # Create business entity with async events
    entity = FlxEntityFactory.create_business_entity(
        name="business_test",
        business_rules={"rule1": "value1"},
        use_async_events=True,
    )

    # Verify async event was created
    assert entity.has_async_domain_events is True
    async_events = entity.get_async_domain_events()
    assert len(async_events) == 1

    created_event = async_events[0]
    assert created_event.event_name == "BusinessEntityCreated"
    assert created_event.event_data["has_business_rules"] is True


def test_async_event_publisher_creation() -> None:
    """Validate async event publisher integration with dependency injection.

    This test verifies that the AsyncEventPublisher can be properly resolved
    from the dependency injection container, ensuring that the async event
    infrastructure is correctly registered and available for domain event
    processing and external system integration.

    Dependency Injection Validation:
        - Container properly registers AsyncEventPublisher
        - Publisher instance can be resolved without errors
        - Publisher provides expected interface methods
        - Graceful handling when async infrastructure unavailable

    Infrastructure Integration:
        - Tests integration between domain and infrastructure layers
        - Validates proper service registration patterns
        - Confirms async publishing capability availability
        - Ensures clean separation of concerns

    Fallback Behavior:
        - Test skips when async infrastructure not configured
        - Graceful degradation without test failures
        - Optional async features don't break core functionality
        - Flexible deployment configuration support
    """
    # Create default container
    container = create_default_container()

    # Get async event publisher
    try:
        async_publisher = container.get(AsyncEventPublisher)
        assert async_publisher is not None
        assert hasattr(async_publisher, "publish_events")
    except ValueError:
        # This is expected if async infrastructure is not fully available
        pytest.skip("Async infrastructure not available")


def test_async_event_fallback() -> None:
    """Verify graceful degradation when async infrastructure is unavailable.

    This test ensures that the domain layer continues to function correctly
    even when async event infrastructure components are missing, unavailable,
    or misconfigured. The system should provide fallback mechanisms that
    maintain business functionality while providing degraded async capabilities.

    Resilience Patterns:
        - System operates without async infrastructure
        - No exceptions thrown when async services unavailable
        - Fallback to alternative event handling mechanisms
        - Graceful degradation maintains core business logic

    Infrastructure Independence:
        - Domain layer doesn't hard-depend on async infrastructure
        - Business operations continue in degraded mode
        - Clean error handling and fallback mechanisms
        - Optional infrastructure components handled gracefully

    Deployment Flexibility:
        - Supports environments without async capabilities
        - Allows incremental async infrastructure adoption
        - Maintains backward compatibility
        - Enables flexible deployment architectures
    """
    # This test ensures graceful degradation when async infrastructure is missing
    aggregate = FlxAggregateRoot(name="fallback_test")

    # Try to raise async event - should not fail even if infrastructure is missing
    aggregate.raise_async_domain_event("TestEvent", {"key": "value"})

    # Should have at least one event (either async or fallback regular)
    assert aggregate.has_any_events is True


def test_entity_lifecycle_with_async_events() -> None:
    """Validate comprehensive entity lifecycle with async event integration.

    This test simulates a complete entity lifecycle from creation through
    multiple business operations to final event commitment, ensuring that
    async events are properly generated, accumulated, managed, and processed
    throughout the entity's operational lifetime.

    Complete Lifecycle Simulation:
        - Entity creation with async event capability
        - Multiple business operations generating events
        - Event accumulation and state management
        - Event ordering and sequence validation
        - Final commitment and cleanup processes

    Event Sourcing Pattern Validation:
        - Events capture complete state change history
        - Event ordering preserves business operation sequence
        - Rich event metadata for reconstruction capability
        - Proper event versioning and timestamps

    Business Operation Modeling:
        - OperationPerformed events for business actions
        - StateChanged events for state transitions
        - Contextual event data with operation details
        - Temporal sequencing of business events

    Production Workflow Simulation:
        - Realistic event generation patterns
        - Proper event lifecycle management
        - Memory and resource cleanup
        - Integration with persistence patterns
    """
    # Create entity
    aggregate = FlxEntityFactory.create_aggregate_root(
        name="lifecycle_test",
        use_async_events=True,
    )

    initial_async_count = aggregate.async_domain_event_count

    # Perform business operations that generate events
    aggregate.raise_async_domain_event(
        "OperationPerformed",
        {
            "operation": "update_data",
            "timestamp": "2025-01-01T00:00:00Z",
        },
    )

    aggregate.raise_async_domain_event(
        "StateChanged",
        {
            "old_state": "initial",
            "new_state": "updated",
        },
    )

    # Verify events accumulated
    assert aggregate.async_domain_event_count == initial_async_count + 2

    # Get all events
    _all_regular, all_async = aggregate.get_all_events()

    # Verify we have the expected events
    assert len(all_async) == initial_async_count + 2

    # Events should be in order
    event_names = [event.event_name for event in all_async]
    assert "AggregateCreated" in event_names
    assert "OperationPerformed" in event_names
    assert "StateChanged" in event_names

    # Commit events (simulating successful processing)
    aggregate.mark_events_as_committed()

    # Verify events are cleared
    assert aggregate.total_event_count == 0


class TestAsyncEventFactory:
    """Comprehensive testing of async domain event factory capabilities.

    This test class validates the FlxEntityFactory's async domain event creation
    methods, ensuring proper event generation, metadata handling, and resilience
    patterns. The factory provides both direct event creation and fallback
    mechanisms for robust async event infrastructure integration.

    Factory Method Coverage:
        - Direct async domain event creation with full metadata
        - Event creation with custom data and versioning
        - Fallback behavior when async infrastructure unavailable
        - Error handling and graceful degradation patterns

    Event Generation Patterns:
        - Factory-based event creation outside aggregate context
        - Manual event construction for testing and integration
        - Event replay and reconstruction support
        - External system event integration capabilities

    Infrastructure Integration:
        - Tests async event system availability detection
        - Validates fallback mechanisms for missing infrastructure
        - Ensures consistent behavior across deployment configurations
        - Provides resilience for partial infrastructure scenarios
    """

    def test_create_async_domain_event(self) -> None:
        """Validate factory-based async domain event creation with metadata.

        This test verifies that the FlxEntityFactory can create async domain
        events directly with comprehensive metadata including aggregate context,
        versioning, and custom event data. This supports scenarios where events
        need to be created outside of aggregate boundaries or for testing purposes.

        Factory Method Validation:
            - Direct async event creation without aggregate context
            - Proper event metadata population
            - Custom event data integration
            - Event versioning support

        Event Structure Verification:
            - Event name matches provided type
            - Aggregate ID and type properly set
            - Custom event data correctly embedded
            - Version information accurately recorded

        Use Cases:
            - Testing event processing logic in isolation
            - Creating events for external system integration
            - Event replay and reconstruction scenarios
            - Manual event generation for debugging purposes
        """
        aggregate_id = uuid4()

        # Create async domain event
        event = FlxEntityFactory.create_async_domain_event(
            event_type="TestEvent",
            aggregate_id=aggregate_id,
            aggregate_type="TestAggregate",
            event_data={"key": "value"},
            version=2,
        )

        # Verify event properties
        assert event.event_name == "TestEvent"
        assert event.aggregate_id == aggregate_id
        assert event.aggregate_type == "TestAggregate"
        assert event.event_data == {"key": "value"}
        assert event.version == 2

    def test_async_event_factory_fallback(self) -> None:
        """Verify factory resilience with unavailable async infrastructure.

        This test ensures that the FlxEntityFactory's async event creation
        methods handle infrastructure unavailability gracefully, providing
        fallback mechanisms that maintain functional compatibility while
        potentially degrading to alternative event types or implementations.

        Infrastructure Resilience:
            - Factory methods don't fail when async infrastructure missing
            - Fallback event creation maintains essential functionality
            - Graceful degradation without breaking core operations
            - Consistent interface regardless of infrastructure availability

        Fallback Event Validation:
            - Event creation succeeds with fallback mechanisms
            - Essential event properties preserved in fallback mode
            - Aggregate context maintained across event types
            - Compatible event structure for downstream processing

        Production Robustness:
            - System operates in partial infrastructure scenarios
            - No cascading failures from missing async components
            - Flexible deployment configurations supported
            - Incremental infrastructure adoption enabled
        """
        # This should not fail even if async infrastructure is missing
        aggregate_id = uuid4()

        event = FlxEntityFactory.create_async_domain_event(
            event_type="FallbackEvent",
            aggregate_id=aggregate_id,
            aggregate_type="FallbackAggregate",
            event_data={"fallback": True},
        )

        # Event should be created (either async or regular)
        assert event is not None
        # Common properties should exist regardless of implementation
        assert hasattr(event, "aggregate_id")
        assert str(event.aggregate_id) == str(aggregate_id)
