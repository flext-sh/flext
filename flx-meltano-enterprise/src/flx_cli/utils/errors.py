"""
Error handling utilities for CLI.
"""

import asyncio
import functools
import sys

import grpc
from rich.console import Console

console = Console()


def handle_errors(func):
    """Decorator to handle common errors in CLI commands."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ctx = args[0]  # Click context is always first argument

        try:
            # Handle async functions
            if asyncio.iscoroutinefunction(func):
                return asyncio.run(func(*args, **kwargs))
            else:
                return func(*args, **kwargs)

        except grpc.RpcError as e:
            error_messages = {
                grpc.StatusCode.UNAVAILABLE: "Cannot connect to FLX daemon. Is it running?",
                grpc.StatusCode.NOT_FOUND: "Resource not found",
                grpc.StatusCode.ALREADY_EXISTS: "Resource already exists",
                grpc.StatusCode.PERMISSION_DENIED: "Permission denied",
                grpc.StatusCode.UNAUTHENTICATED: "Authentication failed. Check your token.",
                grpc.StatusCode.INVALID_ARGUMENT: "Invalid arguments provided",
                grpc.StatusCode.DEADLINE_EXCEEDED: "Request timed out",
                grpc.StatusCode.RESOURCE_EXHAUSTED: "Rate limit exceeded",
            }

            message = error_messages.get(e.code(), f"gRPC error: {e.details()}")
            console.print(f"[red]Error: {message}[/red]")

            if ctx.obj.get("debug"):
                console.print_exception()

            sys.exit(1)

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]")
            sys.exit(0)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

            if ctx.obj.get("debug"):
                console.print_exception()

            sys.exit(1)

    return wrapper
