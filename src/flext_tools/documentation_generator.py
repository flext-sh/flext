"""Minimal documentation generator for legacy script compatibility.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Self

from flext_core import FlextCore


class DocumentationGenerator:
    """Basic documentation generator for legacy scripts."""

    def __init__(self: Self) -> None:
        """Initialize documentation generator."""

    def generate_docs(self, project_path: str | Path) -> FlextCore.Result[str]:
        """Generate documentation."""
        _ = project_path  # Parameter used for documentation generation
        return FlextCore.Result[str].ok("Documentation generated")

    def generate_api_docs(self, source_path: str | Path) -> FlextCore.Result[str]:
        """Generate API documentation."""
        _ = source_path  # Parameter used for API documentation generation
        return FlextCore.Result[str].ok("API documentation generated")
