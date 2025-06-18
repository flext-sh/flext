"""
Event Bus implementation for asynchronous event processing.

Provides a central hub for publishing and subscribing to events across
the FLX platform, supporting both in-memory and distributed event processing.
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Optional
from uuid import UUID, uuid4

import structlog
from aio_pika import ExchangeType, connect_robust
from aio_pika.abc import AbstractChannel, AbstractExchange, AbstractQueue

from flx.config import settings

logger = structlog.get_logger()


@dataclass
class Event:
    """Base event class."""

    id: UUID
    type: str
    timestamp: datetime
    data: dict[str, Any]
    metadata: dict[str, Any]

    @classmethod
    def create(
        cls,
        event_type: str,
        data: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> "Event":
        """Create a new event."""
        return cls(
            id=uuid4(),
            type=event_type,
            timestamp=datetime.now(timezone.utc),
            data=data,
            metadata=metadata or {},
        )

    def to_json(self) -> str:
        """Serialize event to JSON."""
        return json.dumps(
            {
                "id": str(self.id),
                "type": self.type,
                "timestamp": self.timestamp.isoformat(),
                "data": self.data,
                "metadata": self.metadata,
            }
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Event":
        """Deserialize event from JSON."""
        data = json.loads(json_str)
        return cls(
            id=UUID(data["id"]),
            type=data["type"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            data=data["data"],
            metadata=data["metadata"],
        )


EventHandler = Callable[[Event], asyncio.Future[None]]


class EventBus:
    """Central event bus for the FLX platform."""

    def __init__(self) -> None:
        """Initialize the event bus."""
        self.logger = logger.bind(component="event_bus")
        self._handlers: dict[str, list[EventHandler]] = {}
        self._running = False
        self._tasks: set[asyncio.Task] = set()
        self._connection = None
        self._channel: Optional[AbstractChannel] = None
        self._exchange: Optional[AbstractExchange] = None
        self._queues: dict[str, AbstractQueue] = {}

    async def start(self) -> None:
        """Start the event bus."""
        self.logger.info("Starting event bus")

        # Connect to RabbitMQ if configured
        if settings.amqp_url:
            await self._connect_amqp()

        self._running = True
        self.logger.info("Event bus started")

    async def stop(self) -> None:
        """Stop the event bus."""
        self.logger.info("Stopping event bus")
        self._running = False

        # Cancel all pending tasks
        for task in self._tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

        # Close AMQP connection
        if self._connection:
            await self._connection.close()

        self.logger.info("Event bus stopped")

    async def _connect_amqp(self) -> None:
        """Connect to RabbitMQ."""
        try:
            self.logger.info("Connecting to RabbitMQ", url=settings.amqp_url)

            self._connection = await connect_robust(
                settings.amqp_url,
                heartbeat=settings.amqp_heartbeat,
                connection_attempts=settings.amqp_connection_attempts,
                retry_delay=settings.amqp_retry_delay,
            )

            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=10)

            # Declare exchange
            self._exchange = await self._channel.declare_exchange(
                "flx.events",
                ExchangeType.TOPIC,
                durable=True,
            )

            self.logger.info("Connected to RabbitMQ successfully")

        except Exception as e:
            self.logger.error("Failed to connect to RabbitMQ", error=str(e))
            # Continue without AMQP (in-memory only)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)

        # If AMQP is connected, create queue for this event type
        if self._channel and event_type not in self._queues:
            asyncio.create_task(self._create_amqp_consumer(event_type))

        self.logger.info("Handler subscribed", event_type=event_type)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)

            if not self._handlers[event_type]:
                del self._handlers[event_type]

                # Remove AMQP queue if no more handlers
                if event_type in self._queues:
                    asyncio.create_task(self._queues[event_type].delete())
                    del self._queues[event_type]

        self.logger.info("Handler unsubscribed", event_type=event_type)

    async def publish(self, event: Event) -> None:
        """Publish an event."""
        if not self._running:
            raise RuntimeError("Event bus is not running")

        self.logger.debug(
            "Publishing event", event_type=event.type, event_id=str(event.id)
        )

        # Publish to AMQP if connected
        if self._exchange:
            try:
                await self._exchange.publish(
                    event.to_json().encode(),
                    routing_key=event.type,
                )
            except Exception as e:
                self.logger.error("Failed to publish to AMQP", error=str(e))

        # Always dispatch locally
        await self._dispatch_local(event)

    async def _dispatch_local(self, event: Event) -> None:
        """Dispatch event to local handlers."""
        handlers = self._handlers.get(event.type, [])

        # Also dispatch to wildcard handlers
        handlers.extend(self._handlers.get("*", []))

        for handler in handlers:
            # Create task for each handler
            task = asyncio.create_task(self._handle_event(handler, event))
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)

    async def _handle_event(self, handler: EventHandler, event: Event) -> None:
        """Handle a single event with error handling."""
        try:
            await handler(event)
        except Exception as e:
            self.logger.error(
                "Event handler failed",
                event_type=event.type,
                event_id=str(event.id),
                error=str(e),
            )

    async def _create_amqp_consumer(self, event_type: str) -> None:
        """Create AMQP queue and consumer for event type."""
        if not self._channel or not self._exchange:
            return

        try:
            # Declare queue
            queue = await self._channel.declare_queue(
                f"flx.events.{event_type}",
                durable=True,
            )

            # Bind to exchange
            await queue.bind(self._exchange, routing_key=event_type)

            # Start consuming
            await queue.consume(self._on_amqp_message)

            self._queues[event_type] = queue

            self.logger.info("AMQP consumer created", event_type=event_type)

        except Exception as e:
            self.logger.error(
                "Failed to create AMQP consumer", event_type=event_type, error=str(e)
            )

    async def _on_amqp_message(self, message) -> None:
        """Handle incoming AMQP message."""
        async with message.process():
            try:
                event = Event.from_json(message.body.decode())
                await self._dispatch_local(event)
            except Exception as e:
                self.logger.error("Failed to process AMQP message", error=str(e))
