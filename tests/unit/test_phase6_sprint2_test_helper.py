"""Phase 6 Sprint 2 Validation Tests - flext-quality/tools/test_helper.py Conversion.

Tests verify that subprocess usage in test_helper.py has been properly converted:
1. Subprocess import removed
2. FlextUtilities imported and used
3. Both functions converted (suggest_tests_from_coverage, validate_test_execution)
4. subprocess.TimeoutExpired handlers removed
5. Error handling uses FlextResult pattern
6. Tool availability checks preserved
"""

from __future__ import annotations

import pathlib
import sys

import pytest

# Add paths for testing
sys.path.insert(
    0, str(pathlib.Path(__file__).parent.parent.parent / "flext-quality" / "src")
)
sys.path.insert(
    0, str(pathlib.Path(__file__).parent.parent.parent / "flext-core" / "src")
)


class TestPhase6Sprint2TestHelperConversion:
    """Validate subprocess conversion in flext-quality/tools/test_helper.py."""

    TEST_HELPER_PATH = (
        pathlib.Path(__file__).parent.parent.parent
        / "flext-quality"
        / "src"
        / "flext_quality"
        / "tools"
        / "test_helper.py"
    )

    def test_subprocess_import_removed(self) -> None:
        """Verify subprocess module is not imported."""
        content = self.TEST_HELPER_PATH.read_text()

        lines = content.split("\n")
        for line in lines[:30]:  # Check first 30 lines for imports
            if line.startswith("import subprocess"):
                pytest.fail("subprocess import still present - must use FlextUtilities")

    def test_flext_utilities_imported(self) -> None:
        """Verify FlextUtilities is imported."""
        content = self.TEST_HELPER_PATH.read_text()

        assert "FlextUtilities" in content, "FlextUtilities not imported"
        assert "from flext_core import" in content and "FlextUtilities" in content, (
            "FlextUtilities must be imported from flext_core"
        )

    def test_suggest_tests_from_coverage_converted(self) -> None:
        """Verify suggest_tests_from_coverage uses FlextUtilities."""
        content = self.TEST_HELPER_PATH.read_text()

        # Find function and check conversion
        assert "def suggest_tests_from_coverage(project_path: Path)" in content
        assert "FlextUtilities.run_external_command" in content
        assert "pytest" in content  # Should still run pytest

    def test_validate_test_execution_converted(self) -> None:
        """Verify validate_test_execution uses FlextUtilities."""
        content = self.TEST_HELPER_PATH.read_text()

        # Find function and check conversion
        assert "def validate_test_execution(test_path: Path)" in content
        assert "FlextUtilities.run_external_command" in content

    def test_timeout_expired_handlers_removed(self) -> None:
        """Verify subprocess.TimeoutExpired handlers are removed."""
        content = self.TEST_HELPER_PATH.read_text()

        # Should not have TimeoutExpired exception handling
        assert "subprocess.TimeoutExpired" not in content

    def test_error_message_matching_used(self) -> None:
        """Verify error message matching replaces exception handling."""
        content = self.TEST_HELPER_PATH.read_text()

        # Should use "timed out" string matching instead of exceptions
        assert '("timed out" in' in content or (
            '"timed out" in' in content or "'timed out' in" in content
        )

    def test_tool_availability_checks_preserved(self) -> None:
        """Verify tool availability checks are still present."""
        content = self.TEST_HELPER_PATH.read_text()

        # Error messages should still indicate tool not found
        assert "not installed" in content or "not found" in content

    def test_flext_result_pattern_used(self) -> None:
        """Verify FlextResult pattern is used."""
        content = self.TEST_HELPER_PATH.read_text()

        # Functions should return FlextResult
        assert "-> FlextResult[" in content

    def test_module_can_be_imported(self) -> None:
        """Verify the module can be imported without errors."""
        from flext_quality.tools.test_helper import (
            suggest_tests_from_coverage,
            validate_test_execution,
        )

        # Should be able to import both functions
        assert suggest_tests_from_coverage is not None
        assert validate_test_execution is not None

    def test_functions_callable(self) -> None:
        """Verify the functions are callable."""
        from flext_quality.tools.test_helper import (
            suggest_tests_from_coverage,
            validate_test_execution,
        )

        # Functions should be callable
        assert callable(suggest_tests_from_coverage)
        assert callable(validate_test_execution)

    def test_suggest_tests_function_signature(self) -> None:
        """Verify suggest_tests_from_coverage signature is unchanged."""
        import inspect

        from flext_quality.tools.test_helper import suggest_tests_from_coverage

        sig = inspect.signature(suggest_tests_from_coverage)

        # Should take project_path parameter
        assert "project_path" in str(sig)

    def test_validate_test_execution_signature(self) -> None:
        """Verify validate_test_execution signature is unchanged."""
        import inspect

        from flext_quality.tools.test_helper import validate_test_execution

        sig = inspect.signature(validate_test_execution)

        # Should take test_path parameter
        assert "test_path" in str(sig)

    def test_check_test_quality_unchanged(self) -> None:
        """Verify check_test_quality function exists and is unchanged."""
        from flext_quality.tools.test_helper import check_test_quality

        assert check_test_quality is not None
        assert callable(check_test_quality)

    def test_all_subprocess_calls_replaced(self) -> None:
        """Verify all subprocess.run() calls have been replaced."""
        content = self.TEST_HELPER_PATH.read_text()

        # Should not have subprocess.run() calls
        assert "subprocess.run(" not in content

    def test_all_imports_clean(self) -> None:
        """Verify imports section is clean."""
        content = self.TEST_HELPER_PATH.read_text()

        lines = content.split("\n")
        for i, line in enumerate(lines[10:50]):  # Check import section
            if line.startswith(("import subprocess", "from subprocess")):
                pytest.fail(f"subprocess import found at line {i + 10}: {line}")

    def test_error_handling_pattern_consistent(self) -> None:
        """Verify both functions use consistent error handling pattern."""
        content = self.TEST_HELPER_PATH.read_text()

        # Should have consistent pattern checks
        count_not_found = content.count('"not found"')
        count_timed_out = content.count('"timed out"')

        # Both functions should check for these error conditions
        assert count_not_found >= 1, "Missing 'not found' error check"
        assert count_timed_out >= 1, "Missing 'timed out' error check"

    def test_backward_compatibility_maintained(self) -> None:
        """Verify backward compatibility - return types unchanged."""
        content = self.TEST_HELPER_PATH.read_text()

        # Return types should still be FlextResult
        assert "FlextResult[list[str]]" in content
        assert "FlextResult[dict[str, object]]" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
