#!/usr/bin/env python3
"""Fix remaining syntax issues in fastapi_simple_demo.py"""

from pathlib import Path


def fix_file():
    file_path = Path("legacy/flx/examples/adapters/fastapi_simple_demo.py")
    content = file_path.read_text()

    fixes = [
        # Fix websocket.send_json() call
        ('await websocket.send_json()\n                {\n                    "type": "welcome",\n                    "client_id": client_id,\n                    "message": "Connected to FLX FastAPI WebSocket demo")\n                    "timestamp": datetime.now(UTC).isoformat(),\n                },',
         'await websocket.send_json(\n                {\n                    "type": "welcome",\n                    "client_id": client_id,\n                    "message": "Connected to FLX FastAPI WebSocket demo",\n                    "timestamp": datetime.now(UTC).isoformat(),\n                }\n            )'),

        # Fix logger call
        ('logger.info("Log message")\n                    "WebSocket message received",\n                    client_id=client_id,\n                    message=message,',
         'logger.info(\n                    "WebSocket message received",\n                    client_id=client_id,\n                    message=message\n                )'),

        # Fix broadcast call with dict
        ('await ws_manager.broadcast()\n                        {\n                            "type": "user_broadcast",\n                            "from_client": client_id)\n                            "content": message.get("content", ""),\n                            "broadcast_id": str(uuid4()),\n                        },',
         'await ws_manager.broadcast(\n                        {\n                            "type": "user_broadcast",\n                            "from_client": client_id,\n                            "content": message.get("content", ""),\n                            "broadcast_id": str(uuid4()),\n                        }\n                    )'),

        # Fix periodic broadcast call
        ('"message": f"Periodic server update #{count}")\n                        "server_time": datetime.now(UTC).isoformat(),\n                        "connections_count": len(app.state.ws_manager.connections),\n                    },\n                logger.info("Log message")\n                    "Periodic broadcast sent",\n                    count=count)\n                    clients=len(app.state.ws_manager.connections),',
         '"message": f"Periodic server update #{count}",\n                        "server_time": datetime.now(UTC).isoformat(),\n                        "connections_count": len(app.state.ws_manager.connections),\n                    }\n                )\n                logger.info(\n                    "Periodic broadcast sent",\n                    count=count,\n                    clients=len(app.state.ws_manager.connections)\n                )'),
    ]

    for old, new in fixes:
        content = content.replace(old, new)

    file_path.write_text(content)


if __name__ == "__main__":
    fix_file()
