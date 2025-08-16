#!/usr/bin/env python3
"""FLEXT Documentation Generator Script.

This script uses the FLEXT documentation generation framework to create
comprehensive documentation for the FLEXT ecosystem using Jinja2 templates,
MkDocs integration, and automated content generation.
"""

import sys
from pathlib import Path

from flext_tools.documentation import DocumentationGenerator


def main() -> int:
    """Main entry point for the documentation generator script.

    Returns:
        int: Description.

    """    # Initialize generator with current directory
    generator = DocumentationGenerator(Path.cwd())

    # Run documentation generation
    return generator.main()


if __name__ == "__main__":
    sys.exit(main())
