#!/usr/bin/env python3
"""Standalone FLX Daemon Runner.

This script runs the FLX daemon independently of any CLI framework.
Perfect for containers, systemd, or standalone deployment.

Usage:
    python run_daemon.py                    # Start with defaults
    python run_daemon.py --port 8000        # Custom port
    python run_daemon.py --help             # Show options
"""

import sys
from pathlib import Path

# Add the FLX source to Python path
flx_src = Path(__file__).parent / "flx" / "src"
if flx_src.exists():
    sys.path.insert(0, str(flx_src))

try:
    # Import daemon main module
    from flx.daemon.__main__ import main

    if __name__ == "__main__":
        main()

except ImportError:
    sys.exit(1)
