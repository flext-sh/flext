"""Poetry project validation utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextResult


class PoetryValidator:
    """Poetry project validation utilities."""

    def __init__(self) -> None:
        """Initialize PoetryValidator."""
        super().__init__()

    def check_dependencies(self, path: str | Path) -> FlextResult[dict]:
        """Check Poetry dependencies for a project."""
        try:
            path_obj = Path(path)
            pyproject_path = path_obj / "pyproject.toml"

            if not pyproject_path.exists():
                return FlextResult[dict].fail(f"pyproject.toml not found at {path}")

            # Read and validate pyproject.toml
            with pyproject_path.open("r", encoding="utf-8") as f:
                content = f.read()

            # Basic validation - check for required sections
            validation_result = {
                "path": str(path),
                "pyproject_exists": True,
                "has_tool_poetry": "[tool.poetry]" in content,
                "has_dependencies": "[tool.poetry.dependencies]" in content,
                "has_dev_dependencies": "[tool.poetry.group.dev.dependencies]"
                in content,
                "content_length": len(content),
            }

            return FlextResult[dict].ok(validation_result)

        except Exception as e:
            return FlextResult[dict].fail(f"Failed to check dependencies: {e}")


__all__ = [
    "PoetryValidator",
]
