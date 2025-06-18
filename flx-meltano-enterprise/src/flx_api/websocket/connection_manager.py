"""
WebSocket connection manager.
"""

import json
from typing import Dict, Set

import structlog
from fastapi import WebSocket

logger = structlog.get_logger()


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        """Initialize connection manager."""
        self._active_connections: Dict[str, WebSocket] = {}
        self._subscriptions: Dict[str, Set[str]] = {}
        self.logger = logger.bind(component="ws_manager")

    async def startup(self):
        """Startup tasks."""
        self.logger.info("WebSocket manager starting up")

    async def shutdown(self):
        """Shutdown tasks."""
        self.logger.info("WebSocket manager shutting down")

        # Close all connections
        for client_id in list(self._active_connections.keys()):
            await self.disconnect(client_id)

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new connection."""
        await websocket.accept()
        self._active_connections[client_id] = websocket
        self.logger.info("Client connected", client_id=client_id)

        # Send welcome message
        await self.send_personal_message(
            json.dumps(
                {
                    "type": "connected",
                    "message": "Welcome to FLX WebSocket",
                    "client_id": client_id,
                }
            ),
            client_id,
        )

    async def disconnect(self, client_id: str):
        """Disconnect a client."""
        if client_id in self._active_connections:
            del self._active_connections[client_id]

        # Remove all subscriptions
        self._subscriptions.pop(client_id, None)

        self.logger.info("Client disconnected", client_id=client_id)

    async def send_personal_message(self, message: str, client_id: str):
        """Send message to specific client."""
        if client_id in self._active_connections:
            websocket = self._active_connections[client_id]
            try:
                await websocket.send_text(message)
            except Exception as e:
                self.logger.error(
                    "Failed to send message",
                    client_id=client_id,
                    error=str(e),
                )
                await self.disconnect(client_id)

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients."""
        disconnected = []

        for client_id, websocket in self._active_connections.items():
            try:
                await websocket.send_text(message)
            except Exception as e:
                self.logger.error(
                    "Failed to broadcast message",
                    client_id=client_id,
                    error=str(e),
                )
                disconnected.append(client_id)

        # Remove disconnected clients
        for client_id in disconnected:
            await self.disconnect(client_id)

    async def broadcast_to_subscribers(self, event_type: str, message: str):
        """Broadcast message to subscribers of specific event."""
        disconnected = []

        for client_id, subscriptions in self._subscriptions.items():
            if event_type in subscriptions or "*" in subscriptions:
                try:
                    await self.send_personal_message(message, client_id)
                except Exception:
                    disconnected.append(client_id)

        # Remove disconnected clients
        for client_id in disconnected:
            await self.disconnect(client_id)

    async def subscribe(self, client_id: str, event_type: str):
        """Subscribe client to event type."""
        if client_id not in self._subscriptions:
            self._subscriptions[client_id] = set()

        self._subscriptions[client_id].add(event_type)

        self.logger.info(
            "Client subscribed",
            client_id=client_id,
            event_type=event_type,
        )

        # Send confirmation
        await self.send_personal_message(
            json.dumps(
                {
                    "type": "subscribed",
                    "event": event_type,
                }
            ),
            client_id,
        )

    async def unsubscribe(self, client_id: str, event_type: str):
        """Unsubscribe client from event type."""
        if client_id in self._subscriptions:
            self._subscriptions[client_id].discard(event_type)

            self.logger.info(
                "Client unsubscribed",
                client_id=client_id,
                event_type=event_type,
            )

            # Send confirmation
            await self.send_personal_message(
                json.dumps(
                    {
                        "type": "unsubscribed",
                        "event": event_type,
                    }
                ),
                client_id,
            )

    def get_connection_count(self) -> int:
        """Get number of active connections."""
        return len(self._active_connections)

    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for event type."""
        count = 0
        for subscriptions in self._subscriptions.values():
            if event_type in subscriptions:
                count += 1
        return count
