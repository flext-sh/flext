#!/usr/bin/env python3
"""FLEXT Documentation Generator Script.

This script uses the FLEXT documentation generation framework to create
comprehensive documentation for the FLEXT ecosystem using Jinja2 templates,
MkDocs integration, and automated content generation.
"""

import sys
from pathlib import Path

from flext_tools import DocumentationGenerator


def main() -> int:
    """Main entry point for the documentation generator script.

    Returns:
        int: Exit code (0 for success, non-zero for failure).

    """
    # Initialize generator with current directory
    generator = DocumentationGenerator(Path.cwd())

    # Run documentation generation
    result = generator.main()
    return result if isinstance(result, int) else 0


if __name__ == "__main__":
    sys.exit(main())
