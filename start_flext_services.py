#!/usr/bin/env python3
"""FLEXT Services Startup Script.

Start all FLEXT services for development:
- FastAPI server (flext-api)
- Development utilities
- Health monitoring

Usage:
    python start_flext_services.py [--port 8000] [--reload]
"""

import argparse
import logging
import sys

import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("flext_services")


def print_banner() -> None:
    """Print startup banner."""


def check_prerequisites() -> bool:
    """Check if all prerequisites are met."""
    # Check if we can import the API
    try:
        from flext_api.main import app
        return True
    except ImportError:
        return False


def start_api_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = True) -> None:
    """Start the FastAPI server."""
    try:
        uvicorn.run(
            "flext_api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
            access_log=True,
        )
    except KeyboardInterrupt:
        pass
    except Exception:
        sys.exit(1)


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(description="Start FLEXT development services")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")

    args = parser.parse_args()

    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    # Start the API server
    start_api_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
    )


if __name__ == "__main__":
    main()
