"""Test Example: How external projects should use FLX async infrastructure.

This test demonstrates the CORRECT way for domain-specific projects to use
the generic FLX async infrastructure without making FLX aware of their
specific business logic.
"""

from __future__ import annotations

import os
from decimal import Decimal
from enum import StrEnum
from typing import Any

import pytest
from pydantic import Field

# Force stub broker for tests
os.environ["FLX_BROKER_TYPE"] = "stub"

# Import ONLY generic FLX infrastructure - no domain specifics
from flx.core import (
    FlxAggregateRoot,
    FlxCommand,
    flx_configure_logging,
    flx_create_application,
)


class ExampleOrderStatus(StrEnum):
    """Example order status - this is domain-specific, not in FLX."""

    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    SHIPPED = "SHIPPED"


class ExampleOrder(FlxAggregateRoot):
    """Example order entity using FLX infrastructure.

    This demonstrates how external projects should extend FLX entities
    with their own domain logic while leveraging async infrastructure.
    """

    # Domain-specific fields - NOT in FLX
    order_number: str = Field(description="Order number")
    customer_id: str = Field(description="Customer ID")
    status: ExampleOrderStatus = Field(default=ExampleOrderStatus.CREATED)
    total_amount: Decimal = Field(default=Decimal("0.00"))

    def validate_order(self) -> None:
        """Domain-specific business logic."""
        if self.status != ExampleOrderStatus.CREATED:
            msg = f"Cannot validate order in status {self.status}"
            raise ValueError(msg)

        self.status = ExampleOrderStatus.VALIDATED
        self.mark_updated()

        # Use FLX async infrastructure - this is the correct usage
        self.raise_async_domain_event(
            "OrderValidated",  # Domain-specific event name
            {
                "order_number": self.order_number,
                "customer_id": self.customer_id,
                "validation_timestamp": self.updated_at.isoformat(),
            },
        )


class ExampleCreateOrderCommand(FlxCommand):
    """Example command using FLX infrastructure."""

    order_number: str = Field(description="Order number")
    customer_id: str = Field(description="Customer ID")
    total_amount: Decimal = Field(default=Decimal("0.00"))


class TestExternalProjectUsage:
    """Test how external projects should use FLX infrastructure."""

    def test_domain_entity_with_async_events(self) -> None:
        """Test domain entity using FLX async infrastructure."""
        # Create domain-specific order using FLX base entity
        order = ExampleOrder(
            name="Example Order",  # Required by FlxAggregateRoot
            order_number="ORD-001",
            customer_id="CUST-123",
            total_amount=Decimal("199.99"),
        )

        # Verify FLX infrastructure works
        assert order.has_any_events is False  # No events yet

        # Execute domain business logic
        order.validate_order()

        # Verify async events were created using FLX infrastructure
        assert order.has_async_domain_events is True
        assert order.async_domain_event_count == 1

        # Get async events
        async_events = order.get_async_domain_events()
        event = async_events[0]

        # Verify event structure (FLX format but domain content)
        assert event.event_name == "OrderValidated"
        assert event.aggregate_id == order.id
        assert event.aggregate_type == "ExampleOrder"
        assert event.event_data["order_number"] == "ORD-001"
        assert event.event_data["customer_id"] == "CUST-123"

    def test_flx_application_with_domain_entities(self) -> None:
        """Test FLX application automatically handles domain entities."""
        # Configure logging first
        flx_configure_logging()  # Use defaults

        # Create FLX application (generic)
        flx_create_application(
            name="ExampleDomainApp",
            bind_dependencies=True,
        )

        # Simulate command execution that returns domain aggregate
        def simulate_command_execution() -> Any:
            # Domain-specific logic using FLX infrastructure
            order = ExampleOrder(
                name="Example Order 2",  # Required by FlxAggregateRoot
                order_number="ORD-002",
                customer_id="CUST-456",
            )

            order.validate_order()  # Creates async events

            # Return aggregate - FLX middleware will detect and publish events
            return order

        # This simulates how the FLX middleware would work
        result = simulate_command_execution()

        # Verify FLX can handle domain entities generically
        assert isinstance(result, FlxAggregateRoot)
        assert result.has_async_domain_events is True

    def test_domain_command_with_flx_infrastructure(self) -> None:
        """Test domain commands using FLX command infrastructure."""
        # Create domain-specific command using FLX base
        command = ExampleCreateOrderCommand(
            order_number="ORD-003",
            customer_id="CUST-789",
            total_amount=Decimal("299.99"),
        )

        # Verify FLX command infrastructure
        assert command.order_number == "ORD-003"
        assert command.customer_id == "CUST-789"
        assert command.total_amount == Decimal("299.99")

        # Verify FLX base properties are available
        assert hasattr(command, "model_dump")
        assert hasattr(command, "model_validate")

    def test_async_infrastructure_integration(self) -> None:
        """Test integration with FLX async infrastructure."""
        # Import only when needed to test availability
        try:
            from flx.core import flx_get_broker_info, flx_get_health_status

            # Test FLX async infrastructure status
            broker_info = flx_get_broker_info()
            assert "broker_type" in broker_info

            health_status = flx_get_health_status()
            # Check for actual keys in health status
            assert (
                "broker_connected" in health_status or "broker_status" in health_status
            )
            assert "broker_type" in health_status

        except ImportError:
            pytest.skip("Async infrastructure not available")

    def test_entity_factory_with_domain_logic(self) -> None:
        """Test using FLX entity factory for domain entities."""
        from flx.core import FlxEntityFactory

        # Create domain entity using FLX factory
        order = FlxEntityFactory.create_aggregate_root(
            name="ExampleOrder",
            description="Order created via FLX factory",
            use_async_events=True,
        )

        # Verify FLX factory created async event
        assert order.has_async_domain_events is True

        async_events = order.get_async_domain_events()
        assert len(async_events) == 1
        assert async_events[0].event_name == "AggregateCreated"
