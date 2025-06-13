"""Example: FLX Async DDD Infrastructure Usage.

This example demonstrates how to use the new asynchronous Domain-Driven Design
infrastructure with Dramatiq for high-performance message processing.
"""

from __future__ import annotations

import asyncio
import importlib
import logging
from typing import Any
from uuid import uuid4

# Dynamic import for FLX async infrastructure
flx_async = importlib.import_module("flx.infrastructure.async")  # type: ignore[attr-defined]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExampleResourceService:
    """Example service that demonstrates async command and event handling."""

    def __init__(self, command_bus: Any) -> None:
        self.command_bus = command_bus
        self.resources: dict[str, dict[str, Any]] = {}

        # Register command handlers
        self.command_bus.register_command_handler(
            flx_async.FlxCreateResourceCommand, self.handle_create_resource,  # type: ignore[attr-defined]
        )
        self.command_bus.register_command_handler(
            flx_async.FlxProcessDataCommand, self.handle_process_data,  # type: ignore[attr-defined]
        )

        # Register event handlers
        self.command_bus.register_event_handler(
            flx_async.FlxResourceCreatedEvent, self.handle_resource_created_event,  # type: ignore[attr-defined]
        )
        self.command_bus.register_event_handler(
            flx_async.FlxDataProcessedEvent, self.handle_data_processed_event,  # type: ignore[attr-defined]
        )

    async def handle_create_resource(self, command: Any) -> dict[str, Any]:
        """Handle resource creation command."""
        logger.info(f"Creating resource: {command.resource_name}")

        # Simulate resource creation logic
        resource_id = str(uuid4())
        resource_data = {
            "id": resource_id,
            "name": command.resource_name,
            "type": command.resource_type,
            "configuration": command.configuration,
            "created_at": command.timestamp.isoformat(),
            "status": "active",
        }

        # Store in our "database"
        self.resources[resource_id] = resource_data

        # Publish resource created event
        event = flx_async.create_event(
            flx_async.FlxResourceCreatedEvent,
            correlation_id=command.correlation_id,
            causation_id=command.message_id,
            resource_id=uuid4(),  # Convert string to UUID
            resource_name=command.resource_name,
            resource_type=command.resource_type,
            created_by="system",
        )

        await self.command_bus.publish_event(event)

        return {
            "resource_id": resource_id,
            "status": "created",
            "message": f"Resource '{command.resource_name}' created successfully",
        }

    async def handle_process_data(self, command: Any) -> dict[str, Any]:
        """Handle data processing command."""
        logger.info(f"Processing data from: {command.data_source}")

        # Simulate data processing
        import random
        import time

        processing_start = time.time()

        # Simulate some processing time
        await asyncio.sleep(0.1)

        # Simulate processing results
        records_processed = random.randint(100, 1000)
        errors = []

        if random.random() < 0.1:  # 10% chance of errors
            errors = [f"Error processing record {random.randint(1, records_processed)}"]

        processing_time = time.time() - processing_start

        # Publish data processed event
        event = flx_async.create_event(
            flx_async.FlxDataProcessedEvent,
            correlation_id=command.correlation_id,
            causation_id=command.message_id,
            job_id=uuid4(),
            records_processed=records_processed,
            processing_time=processing_time,
            errors=errors,
        )

        await self.command_bus.publish_event(event)

        return {
            "job_id": str(uuid4()),
            "records_processed": records_processed,
            "processing_time": processing_time,
            "errors": errors,
            "status": "completed" if not errors else "completed_with_errors",
        }

    async def handle_resource_created_event(self, event: Any) -> None:
        """Handle resource created event for side effects."""
        logger.info(
            f"Resource created event received: {event.resource_name} "
            f"(ID: {event.resource_id})",
        )

        # Example side effects:
        # - Send notification
        # - Update search index
        # - Trigger dependent workflows

        logger.info("Side effects completed for resource creation")

    async def handle_data_processed_event(self, event: Any) -> None:
        """Handle data processed event for side effects."""
        logger.info(
            f"Data processing completed: {event.records_processed} records "
            f"in {event.processing_time:.2f}s",
        )

        if event.errors:
            logger.warning(f"Processing had {len(event.errors)} errors: {event.errors}")

        # Example side effects:
        # - Update dashboard metrics
        # - Send completion notification
        # - Trigger cleanup jobs


async def demonstrate_async_ddd_workflow() -> None:
    """Demonstrate the complete async DDD workflow."""
    logger.info("=== FLX Async DDD Infrastructure Demo ===")

    # Initialize command bus with configuration
    config = flx_async.AsyncCommandBusConfig(
        redis_url="redis://localhost:6379/0",
        result_ttl=3600,  # 1 hour
        enable_prometheus=False,  # Disable for demo
        enable_health_checks=True,
    )

    # Get command bus instance (in real app, this would be injected)
    command_bus = flx_async.get_command_bus(config)

    # Initialize our example service
    service = ExampleResourceService(command_bus)

    logger.info("Service initialized with command and event handlers")

    # Demonstrate command processing with correlation
    correlation_id = uuid4()

    # 1. Create Resource Command
    logger.info("1. Sending FlxCreateResourceCommand...")
    create_command_obj = flx_async.create_command(
        flx_async.FlxCreateResourceCommand,
        correlation_id=correlation_id,
        resource_name="example_database",
        resource_type="postgresql",
        configuration={
            "host": "localhost",
            "port": 5432,
            "database": "example_db",
        },
    )

    try:
        # In a real scenario, this would be sent to the queue
        # For demo purposes, we'll call the handler directly
        result = await service.handle_create_resource(create_command_obj)
        logger.info(f"Create resource result: {result}")
    except Exception as e:
        logger.exception(f"Create resource failed: {e}")

    # 2. Process Data Command
    logger.info("2. Sending FlxProcessDataCommand...")
    process_command_obj = flx_async.create_command(
        flx_async.FlxProcessDataCommand,
        correlation_id=correlation_id,
        causation_id=create_command_obj.message_id,
        data_source="example_data.csv",
        transformation_rules=["clean_nulls", "normalize_dates", "validate_schema"],
        output_format="parquet",
        batch_size=500,
    )

    try:
        # In a real scenario, this would be sent to the queue
        result = await service.handle_process_data(process_command_obj)
        logger.info(f"Process data result: {result}")
    except Exception as e:
        logger.exception(f"Process data failed: {e}")

    # 3. Demonstrate queue routing
    logger.info("3. Demonstrating message routing...")
    from flx_async import route_message

    # Show how commands are routed to different queues
    commands_to_route = [
        create_command_obj,
        process_command_obj,
        flx_async.create_command(
            flx_async.FlxCreateResourceCommand,
            resource_name="critical_system",
            resource_type="system",
            priority=1,  # High priority
        ),
    ]

    for cmd in commands_to_route:
        try:
            queue_config = route_message(cmd)
            logger.info(
                f"Command {cmd.__class__.__name__} routed to queue: "
                f"{queue_config.name} (priority: {queue_config.priority})",
            )
        except Exception as e:
            logger.exception(f"Routing failed for {cmd.__class__.__name__}: {e}")

    logger.info("=== Demo completed successfully ===")


async def demonstrate_error_handling() -> None:
    """Demonstrate error handling and retry mechanisms."""
    logger.info("=== Error Handling Demo ===")

    flx_async.get_command_bus()

    # Create a command that will simulate failure
    flx_async.create_command(
        flx_async.FlxProcessDataCommand,
        data_source="non_existent_file.csv",
        transformation_rules=["invalid_rule"],
        priority=1,  # High priority for faster processing
    )

    try:
        # This would normally be sent to queue and retried automatically
        logger.info("Simulating command that will fail...")

        # Simulate failure scenario
        msg = "Simulated processing error"
        raise ValueError(msg)

    except Exception as e:
        logger.exception(f"Command failed as expected: {e}")
        logger.info("In real scenario, this would be retried automatically by Dramatiq")

    logger.info("=== Error Handling Demo completed ===")


async def main() -> None:
    """Main demo function."""
    try:
        await demonstrate_async_ddd_workflow()
        await demonstrate_error_handling()

    except Exception as e:
        logger.exception(f"Demo failed: {e}")

    logger.info("Demo finished")


if __name__ == "__main__":
    # Note: In a real application, you would have Redis running
    # and Dramatiq workers processing the actual queues

    asyncio.run(main())
