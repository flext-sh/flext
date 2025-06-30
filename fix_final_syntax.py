#!/usr/bin/env python3
"""Final targeted syntax fix for fastapi_client_demo.py"""

from pathlib import Path


def fix_file():
    file_path = Path("legacy/flx/examples/adapters/fastapi_client_demo.py")
    content = file_path.read_text()

    # Replace the problematic patterns with correct syntax
    fixes = [
        # Fix GraphQL client creation
        ("transport=transport, fetch_schema_from_transport=True)return self",
         "transport=transport,\n            fetch_schema_from_transport=True\n        )\n\n        return self"),

        # Fix headers parameter
        ("headers=headers)response.raise_for_status()",
         "headers=headers\n        )\n\n        response.raise_for_status()"),

        # Fix multiline function calls that got mangled
        ('""")result = await', '"""\n            )\n\n            result = await'),
        ('""")variables =', '"""\n            )\n\n            variables ='),
        ("variable_values=variables)start_result =", "variable_values=variables\n            )\n\n            start_result ="),
        ('""")result = await self.graphql_client.execute_async(app_query)',
         '"""\n            )\n\n            result = await self.graphql_client.execute_async(app_query)'),

        # Fix async wait calls
        ("[message_task, timeout_task])\n                            return_when=asyncio.FIRST_COMPLETED)if message_task",
         "[message_task, timeout_task],\n                            return_when=asyncio.FIRST_COMPLETED\n                        )\n\n                        if message_task"),

        # Fix timeout calls
        ("await asyncio.wait_for()\n                asyncio.gather(consume_log_stream(), consume_metrics_stream()),\n                timeout=duration)except TimeoutError:",
         "await asyncio.wait_for(\n                asyncio.gather(consume_log_stream(), consume_metrics_stream()),\n                timeout=duration\n            )\n        except TimeoutError:"),

        # Fix params dict
        ('"task_name": "demo_task")\n                "parameters": json.dumps({"demo": True, "duration": 5}),\n            })response.raise_for_status()',
         '"task_name": "demo_task",\n                "parameters": json.dumps({"demo": True, "duration": 5}),\n            }\n        )\n\n        response.raise_for_status()'),

        # Fix WebSocket stats call
        ('f"{self.base_url}/api/v2/websockets/stats")response.raise_for_status()',
         'f"{self.base_url}/api/v2/websockets/stats"\n        )\n\n        response.raise_for_status()'),

        # Fix broadcast call
        ("headers=headers)response.raise_for_status()",
         "headers=headers\n        )\n\n        response.raise_for_status()"),
    ]

    for old, new in fixes:
        content = content.replace(old, new)

    file_path.write_text(content)


if __name__ == "__main__":
    fix_file()
