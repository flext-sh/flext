#!/usr/bin/env python3
"""Test final REST API functionality."""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "flx" / "src"))


def test_api():
    """Test REST API creation."""
    try:
        from flx.adapters.inbound.fire_cli import create_cli
        from flx.adapters.inbound.rest_api import create_rest_api

        cli = create_cli()
        app = create_rest_api(cli=cli)

        # Count routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                for method in route.methods:
                    if method != 'HEAD':
                        routes.append(f"{method} {route.path}")

        # Show some example routes
        plugin_routes = [r for r in routes if '/database/' in r or '/monitoring/' in r]

        if plugin_routes:
            for route in plugin_routes[:5]:
                pass

        return True

    except Exception:
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_api()
    if success:
        pass
