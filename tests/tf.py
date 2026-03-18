"""Test file helpers module for workspace tests.

Provides tf alias for file creation and assertion helpers.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path


class TestFiles:
    """Test file helpers."""

    @staticmethod
    def create_in(content: str, filename: str, directory: Path) -> Path:
        """Create a file with content in directory."""
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / filename
        file_path.write_text(content)
        return file_path

    @staticmethod
    def assert_exists(path: Path) -> None:
        """Assert file exists."""
        if not path.exists():
            msg = f"Expected file to exist: {path}"
            raise AssertionError(msg)


tf = TestFiles
__all__ = ["tf"]
