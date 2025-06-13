#!/usr/bin/env python3
"""Simple REST API test without problematic imports."""

import asyncio
import sys
from pathlib import Path

# Add FLX to path
sys.path.insert(0, str(Path(__file__).parent / "flx" / "src"))


def test_rest_api() -> bool:
    """Test REST API creation and basic functionality."""

    try:
        # Import required modules
        from flx.adapters.inbound.fire_cli import create_cli
        from flx.adapters.inbound.rest_api import create_rest_api

        # Create CLI with plugins
        cli = create_cli()

        # Create REST API
        app = create_rest_api(cli=cli)

        # Check app configuration

        # Get routes information
        routes = []
        for route in app.routes:
            if hasattr(route, "path") and hasattr(route, "methods"):
                for method in route.methods:
                    if method != "HEAD":  # Skip HEAD methods
                        routes.append(f"{method} {route.path}")

        # Group routes by category
        core_routes = []
        plugin_routes = []
        other_routes = []

        for route in sorted(routes):
            if (
                "/api/v1/database/" in route
                or "/api/v1/monitoring/" in route
                or "/api/v1/system-report" in route
            ):
                plugin_routes.append(route)
            elif "/api/v1/" in route:
                core_routes.append(route)
            else:
                other_routes.append(route)

        for _route in core_routes:
            pass

        for _route in plugin_routes:
            pass

        for _route in other_routes:
            pass

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success: bool  # type: ignore
    success = asyncio.run(test_rest_api())
    if success:
        pass
