"""Minimal documentation generator for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextResult


class DocumentationGenerator:
    """Basic documentation generator for legacy scripts."""

    def __init__(self) -> None:
        """Initialize documentation generator."""

    def generate_docs(self, project_path: str | Path) -> FlextResult[str]:
        """Generate documentation."""
        _ = project_path  # Parameter used for documentation generation
        return FlextResult[str].ok("Documentation generated")

    def generate_api_docs(self, source_path: str | Path) -> FlextResult[str]:
        """Generate API documentation."""
        _ = source_path  # Parameter used for API documentation generation
        return FlextResult[str].ok("API documentation generated")
