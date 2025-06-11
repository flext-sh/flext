#!/usr/bin/env python3
"""
Command-line interface for dc-code-analyzer.
"""

import sys
from pathlib import Path


def main() -> None:
    """Main CLI entry point."""
    print("DC Code Analyzer CLI")
    print("Starting Django management commands...")

    # Add the current directory to Python path
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))

    # Import and run Django management
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "code_analyzer_web.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
