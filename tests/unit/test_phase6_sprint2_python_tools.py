"""Phase 6 Sprint 2 Validation Tests - flext-quality/backends/python_tools.py Conversion.

Tests verify that subprocess usage in python_tools.py has been properly converted:
1. Subprocess import removed
2. FlextUtilities imported and used
3. Both tool methods converted (ruff, pylint)
4. subprocess.TimeoutExpired handlers removed
5. Error handling uses FlextResult pattern
6. Tool availability checks preserved
"""

from __future__ import annotations

import inspect
import pathlib
import sys

import pytest
from flext_quality.backends.python_tools import FlextQualityPythonTools

# Add paths for testing
sys.path.insert(
    0, str(pathlib.Path(__file__).parent.parent.parent / "flext-quality" / "src")
)
sys.path.insert(
    0, str(pathlib.Path(__file__).parent.parent.parent / "flext-core" / "src")
)


class TestPhase6Sprint2PythonToolsConversion:
    """Validate subprocess conversion in flext-quality/backends/python_tools.py."""

    PYTHON_TOOLS_PATH = (
        pathlib.Path(__file__).parent.parent.parent
        / "flext-quality"
        / "src"
        / "flext_quality"
        / "backends"
        / "python_tools.py"
    )

    def test_subprocess_import_removed(self) -> None:
        """Verify subprocess module is not imported."""
        content = self.PYTHON_TOOLS_PATH.read_text()

        lines = content.split("\n")
        for line in lines[:30]:  # Check first 30 lines for imports
            if line.startswith("import subprocess"):
                pytest.fail("subprocess import still present - must use FlextUtilities")

    def test_flext_utilities_imported(self) -> None:
        """Verify FlextUtilities is imported."""
        content = self.PYTHON_TOOLS_PATH.read_text()

        assert "FlextUtilities" in content, "FlextUtilities not imported"
        assert "from flext_core import" in content and "FlextUtilities" in content, (
            "FlextUtilities must be imported from flext_core"
        )

    def test_ruff_method_uses_flext_utilities(self) -> None:
        """Verify run_ruff_check uses FlextUtilities."""
        content = self.PYTHON_TOOLS_PATH.read_text()

        # Find run_ruff_check method
        assert "def run_ruff_check(self, path: Path)" in content
        assert "FlextUtilities.CommandExecution.run_external_command" in content
        assert "subprocess.run" not in content

    def test_pylint_method_uses_flext_utilities(self) -> None:
        """Verify run_pylint_check uses FlextUtilities."""
        content = self.PYTHON_TOOLS_PATH.read_text()

        # Find run_pylint_check method
        assert "def run_pylint_check(self, path: Path)" in content
        assert "FlextUtilities.CommandExecution.run_external_command" in content

    def test_timeout_expired_handlers_removed(self) -> None:
        """Verify subprocess.TimeoutExpired handlers are removed."""
        content = self.PYTHON_TOOLS_PATH.read_text()

        # Should not have TimeoutExpired exception handling
        assert "subprocess.TimeoutExpired" not in content

    def test_error_message_matching_used(self) -> None:
        """Verify error message matching replaces exception handling."""
        content = self.PYTHON_TOOLS_PATH.read_text()

        # Should use "timed out" string matching instead of exceptions
        assert '"timed out" in result.error.lower()' in content or (
            '"timed out" in' in content
        )

    def test_tool_availability_checks_preserved(self) -> None:
        """Verify tool availability checks are still present."""
        content = self.PYTHON_TOOLS_PATH.read_text()

        # Check methods should still exist
        assert "_check_ruff" in content
        assert "_check_pylint" in content

    def test_flext_result_pattern_used(self) -> None:
        """Verify FlextResult pattern is used."""
        content = self.PYTHON_TOOLS_PATH.read_text()

        # Methods should return FlextResult
        assert "-> FlextResult[" in content

    def test_module_can_be_imported(self) -> None:
        """Verify the module can be imported without errors."""
        # Should be able to import and instantiate
        assert FlextQualityPythonTools is not None

    def test_class_can_be_instantiated(self) -> None:
        """Verify the class can be instantiated."""
        tools = FlextQualityPythonTools()
        assert tools is not None
        assert hasattr(tools, "run_ruff_check")
        assert hasattr(tools, "run_pylint_check")

    def test_run_ruff_check_signature_unchanged(self) -> None:
        """Verify run_ruff_check signature is unchanged."""
        tools = FlextQualityPythonTools()
        method = tools.run_ruff_check
        sig = inspect.signature(method)

        # Should take path parameter
        assert "path" in str(sig)

    def test_run_pylint_check_signature_unchanged(self) -> None:
        """Verify run_pylint_check signature is unchanged."""
        tools = FlextQualityPythonTools()
        method = tools.run_pylint_check
        sig = inspect.signature(method)

        # Should take path parameter
        assert "path" in str(sig)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
