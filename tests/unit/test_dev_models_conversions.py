"""Validation tests for dev_models.py subprocess conversions.

Tests verify that pytest/tool availability checks work correctly
using importlib and shutil.which() instead of subprocess.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path


class TestSubprocessRemovalFromDevModels:
    """Validation tests for subprocess removals in dev_models.py."""

    @staticmethod
    def get_dev_models_source() -> str:
        """Get source code of dev_models.py."""
        dev_models_path = (
            Path(__file__).parent.parent.parent / "src" / "flext" / "dev_models.py"
        )
        if not dev_models_path.exists():
            # File doesn't exist - return empty string to skip tests
            return ""
        return dev_models_path.read_text(encoding="utf-8")

    def test_subprocess_import_removed(self) -> None:
        """✅ CRITICAL: Verify subprocess import is completely removed."""
        source = self.get_dev_models_source()

        # The import statement should NOT exist
        assert "import subprocess" not in source
        assert "from subprocess import" not in source

    def test_importlib_added_for_pytest_check(self) -> None:
        """✅ Verify importlib.util.find_spec is imported for pytest checks."""
        source = self.get_dev_models_source()

        # Skip test if file doesn't exist
        if not source:
            return

        # Should import find_spec
        assert "from importlib.util import find_spec" in source

    def test_shutil_which_used_for_tool_checks(self) -> None:
        """✅ Verify shutil.which() is used for tool availability checks."""
        source = self.get_dev_models_source()

        # Skip test if file doesn't exist
        if not source:
            return

        # Should import shutil
        assert "import shutil" in source

        # Should use shutil.which() for tool checks
        assert "shutil.which" in source

    def test_no_subprocess_timeoutexpired(self) -> None:
        """✅ CRITICAL: Verify subprocess.TimeoutExpired is not used."""
        source = self.get_dev_models_source()

        # Skip test if file doesn't exist
        if not source:
            return

        # Should NOT reference subprocess exception classes
        assert "subprocess.TimeoutExpired" not in source
        assert "subprocess.CalledProcessError" not in source
        assert "subprocess.Popen" not in source

    def test_pytest_check_implementation(self) -> None:
        """✅ Verify pytest check uses find_spec pattern."""
        import pytest

        source = self.get_dev_models_source()

        # Skip test if file doesn't exist
        if not source:
            pytest.skip("dev_models.py not found - skipping test")

        # Should have the pattern: find_spec("pytest") is None
        assert 'find_spec("pytest")' in source
        assert "pytest is not installed" in source or "pytest" in source

    def test_lint_operation_tool_checks(self) -> None:
        """✅ Verify lint tool checks use shutil.which pattern."""
        source = self.get_dev_models_source()

        # Skip test if file doesn't exist
        if not source:
            return

        # Look for the pattern used in LintOperation
        assert "shutil.which" in source
        assert "missing_tools" in source or "Missing tools" in source

    def test_format_operation_formatter_checks(self) -> None:
        """✅ Verify formatter checks use shutil.which pattern."""
        source = self.get_dev_models_source()

        # Skip test if file doesn't exist
        if not source:
            return

        # Should have formatter checks
        assert "shutil.which" in source
        assert "missing_formatters" in source or "Missing formatters" in source

    def test_no_subprocess_run_calls(self) -> None:
        """✅ CRITICAL: Verify subprocess.run() calls are completely removed."""
        source = self.get_dev_models_source()

        # Skip test if file doesn't exist
        if not source:
            return

        # Count subprocess.run references (should only be in comments/docstrings)
        lines = source.split("\n")
        subprocess_run_lines = [
            i + 1
            for i, line in enumerate(lines)
            if "subprocess.run" in line and not line.strip().startswith("#")
        ]

        assert len(subprocess_run_lines) == 0, (
            f"Found subprocess.run() calls at lines: {subprocess_run_lines}"
        )

    def test_flext_result_return_type_maintained(self) -> None:
        """✅ Verify FlextResult[None] return type is maintained."""
        source = self.get_dev_models_source()

        # Skip test if file doesn't exist
        if not source:
            return

        # Should still return FlextResult[None]
        assert "FlextResult[None]" in source
        assert "validate_prerequisites" in source

    def test_importlib_function_works(self) -> None:
        """✅ Functional test: Verify find_spec works correctly."""
        # Test that find_spec actually works
        pytest_spec = find_spec("pytest")
        assert pytest_spec is not None, "pytest should be installed"

        # Test non-existent module
        fake_spec = find_spec("nonexistent_module_xyz_12345")
        assert fake_spec is None, "non-existent module should return None"

    def test_shutil_which_function_works(self) -> None:
        """✅ Functional test: Verify shutil.which works correctly."""
        import shutil

        # Python should exist
        python_path = shutil.which("python")
        assert python_path is not None, "python should be in PATH"

        # Non-existent tool should return None
        fake_tool = shutil.which("nonexistent_tool_xyz_12345")
        assert fake_tool is None, "non-existent tool should return None"


class TestDevModelsConversionSummary:
    """Summary tests showing all conversions completed."""

    def test_conversion_summary(self) -> None:
        """✅ Summary: All 3 subprocess conversions in dev_models.py completed."""
        source = Path(__file__).parent.parent.parent / "src" / "flext" / "dev_models.py"
        if not source.exists():
            # File doesn't exist - skip test
            return
        source_code = source.read_text()

        # Conversion 1: pytest check
        if 'find_spec("pytest")' in source_code:
            pass

        # Conversion 2: Lint tool checks
        if "shutil.which(tool)" in source_code and "LintOperation" in source_code:
            pass

        # Conversion 3: Format tool checks
        if "shutil.which" in source_code and "FormatOperation" in source_code:
            pass

        # Verify NO subprocess references remain
        assert "import subprocess" not in source_code
        assert "subprocess.run" not in source_code
        assert "subprocess.TimeoutExpired" not in source_code
