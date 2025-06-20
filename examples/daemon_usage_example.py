#!/usr/bin/env python3
"""FLX Daemon Usage Example.

This example demonstrates how to use the FLX daemon functionality
to run FLX as a background service with REST API and web interface.

Features demonstrated:
    - Starting daemon programmatically
    - Using CLI commands for daemon management
    - Accessing REST API endpoints
    - Web interface monitoring
    - Service installation and management

Usage:
    # Run daemon directly
    python daemon_usage_example.py

    # Or use CLI commands
    python -m flx daemon start --port 8000 --web-port 8080
    python -m flx daemon status
    python -m flx daemon stop
"""

import asyncio

import requests

from flx.daemon.core import DaemonConfig
from flx.daemon.infrastructure import DaemonServiceFactory
from flx.daemon.service import FlxDaemonService
from flx.utils.logging import get_logger

logger = get_logger(__name__)


async def example_programmatic_daemon() -> None:
    """Example of using daemon programmatically."""
    # Create daemon configuration
    config = DaemonConfig(
        host="127.0.0.1",
        port=8001,  # Use different port to avoid conflicts
        web_port=8081,
        web_enabled=True,
        pid_file="/tmp/flx_example.pid",
        work_dir="/tmp/flx_example",
        log_dir="/tmp/flx_example/logs",
    )

    try:
        # Create daemon and server manager using factory
        daemon, server_manager = DaemonServiceFactory.create_daemon_service(
            config)

        # Start servers in background
        asyncio.create_task(server_manager.start_all_servers())

        # Wait a bit for startup
        await asyncio.sleep(3)

        # Test if daemon is running
        daemon.get_status()

        # Test API endpoints
        await test_api_endpoints(config.host, config.port)

        # Let it run for a bit
        await asyncio.sleep(10)

    finally:
        await server_manager.stop_all_servers()
        await daemon.stop()


async def test_api_endpoints(host: str, port: int) -> None:
    """Test daemon API endpoints."""
    base_url = f"http://{host}:{port}"

    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            pass
    except Exception:
        pass

    # Test daemon status
    try:
        response = requests.get(f"{base_url}/api/daemon/status", timeout=5)
        if response.status_code == 200:
            response.json()
    except Exception:
        pass

    # Test system metrics
    try:
        response = requests.get(f"{base_url}/api/daemon/metrics", timeout=5)
        if response.status_code == 200:
            response.json()
    except Exception:
        pass

    # Test adapters endpoint
    try:
        response = requests.get(f"{base_url}/api/daemon/adapters", timeout=5)
        if response.status_code == 200:
            response.json()
    except Exception:
        pass


def example_cli_usage() -> None:
    """Example of using daemon via CLI commands."""


def example_service_management() -> None:
    """Example of systemd service management."""
    # Create service manager
    config = DaemonConfig()
    service = FlxDaemonService(config, user_service=True)

    # Check if service is installed
    status = service.get_service_status()

    if not status.get("installed"):
        pass


def example_web_interface() -> None:
    """Example of accessing web interface."""


def main() -> None:
    """Main example runner."""
    # Show CLI usage examples
    example_cli_usage()

    # Show service management
    example_service_management()

    # Show web interface info
    example_web_interface()

    # Ask user if they want to run the daemon
    response = input(
        "Do you want to run the daemon example? (y/N): ").lower().strip()

    if response in {"y", "yes"}:
        asyncio.run(example_programmatic_daemon())


if __name__ == "__main__":
    main()
