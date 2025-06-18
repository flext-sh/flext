"""
WebSocket endpoints for real-time updates.
"""

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Global connection manager (imported from main)
from flx_api.main import manager


@router.websocket("/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "ping":
                    await manager.send_personal_message(
                        json.dumps({"type": "pong"}),
                        client_id,
                    )

                elif message.get("type") == "subscribe":
                    # Subscribe to events
                    event_type = message.get("event")
                    await manager.subscribe(client_id, event_type)

                elif message.get("type") == "unsubscribe":
                    # Unsubscribe from events
                    event_type = message.get("event")
                    await manager.unsubscribe(client_id, event_type)

                else:
                    # Echo unknown messages
                    await manager.send_personal_message(
                        json.dumps(
                            {
                                "type": "echo",
                                "data": message,
                            }
                        ),
                        client_id,
                    )

            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps(
                        {
                            "type": "error",
                            "message": "Invalid JSON",
                        }
                    ),
                    client_id,
                )

    except WebSocketDisconnect:
        await manager.disconnect(client_id)

    except Exception:
        await manager.disconnect(client_id)
        raise
