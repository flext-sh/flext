"""Phase 6 Sprint 2 Validation Tests - flext-quality/tools/example_helper.py Conversion.

Tests verify that subprocess usage in example_helper.py has been properly converted:
1. Subprocess import removed
2. FlextUtilities imported and used
3. All three functions converted
4. subprocess.TimeoutExpired handlers removed
5. Error handling uses FlextResult pattern
6. Tool availability checks preserved
"""

from __future__ import annotations

import inspect
import pathlib
import sys

import pytest
from flext_quality.tools.example_helper import (
    check_example_structure,
    run_example_safely,
    validate_example_imports,
    validate_examples_directory,
)

# Add paths for testing
sys.path.insert(
    0, str(pathlib.Path(__file__).parent.parent.parent / "flext-quality" / "src")
)
sys.path.insert(
    0, str(pathlib.Path(__file__).parent.parent.parent / "flext-core" / "src")
)


class TestPhase6Sprint2ExampleHelperConversion:
    """Validate subprocess conversion in flext-quality/tools/example_helper.py."""

    EXAMPLE_HELPER_PATH = (
        pathlib.Path(__file__).parent.parent.parent
        / "flext-quality"
        / "src"
        / "flext_quality"
        / "tools"
        / "example_helper.py"
    )

    def test_subprocess_import_removed(self) -> None:
        """Verify subprocess module is not imported."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        lines = content.split("\n")
        for line in lines[:30]:  # Check first 30 lines for imports
            if line.startswith("import subprocess"):
                pytest.fail("subprocess import still present - must use FlextUtilities")

    def test_flext_utilities_imported(self) -> None:
        """Verify FlextUtilities is imported."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        assert "FlextUtilities" in content, "FlextUtilities not imported"
        assert "from flext_core import" in content and "FlextUtilities" in content, (
            "FlextUtilities must be imported from flext_core"
        )

    def test_validate_examples_directory_converted(self) -> None:
        """Verify validate_examples_directory uses FlextUtilities."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        # Find function and check conversion
        assert "def validate_examples_directory(" in content
        assert "FlextUtilities.CommandExecution.run_external_command" in content
        assert "python3" in content  # Should still run python3

    def test_validate_example_imports_converted(self) -> None:
        """Verify validate_example_imports uses FlextUtilities."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        # Find function and check conversion
        assert "def validate_example_imports(" in content
        assert "FlextUtilities.CommandExecution.run_external_command" in content

    def test_run_example_safely_converted(self) -> None:
        """Verify run_example_safely uses FlextUtilities."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        # Find function and check conversion
        assert "def run_example_safely(" in content
        assert "FlextUtilities.CommandExecution.run_external_command" in content

    def test_timeout_expired_handlers_removed(self) -> None:
        """Verify subprocess.TimeoutExpired handlers are removed."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        # Should not have TimeoutExpired exception handling
        assert "subprocess.TimeoutExpired" not in content

    def test_error_message_matching_used(self) -> None:
        """Verify error message matching replaces exception handling."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        # Should use "timed out" string matching instead of exceptions
        assert '("timed out" in' in content or (
            '"timed out" in' in content or "'timed out' in" in content
        )

    def test_all_subprocess_calls_replaced(self) -> None:
        """Verify all subprocess.run() calls have been replaced."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        # Should not have subprocess.run() calls
        assert "subprocess.run(" not in content

    def test_flext_result_pattern_used(self) -> None:
        """Verify FlextResult pattern is used in all functions."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        # Functions should return FlextResult
        assert "-> FlextResult[" in content

    def test_module_can_be_imported(self) -> None:
        """Verify the module can be imported without errors."""
        # Should be able to import all functions
        assert validate_examples_directory is not None
        assert check_example_structure is not None
        assert validate_example_imports is not None
        assert run_example_safely is not None

    def test_all_functions_callable(self) -> None:
        """Verify all functions are callable."""
        # All functions should be callable
        assert callable(validate_examples_directory)
        assert callable(check_example_structure)
        assert callable(validate_example_imports)
        assert callable(run_example_safely)

    def test_function_signatures_unchanged(self) -> None:
        """Verify function signatures are unchanged."""
        # Check validate_examples_directory signature
        sig = inspect.signature(validate_examples_directory)
        assert "examples_dir" in str(sig)

        # Check validate_example_imports signature
        sig = inspect.signature(validate_example_imports)
        assert "example_file" in str(sig)

        # Check run_example_safely signature
        sig = inspect.signature(run_example_safely)
        assert "example_file" in str(sig)
        assert "timeout" in str(sig)

    def test_check_example_structure_unchanged(self) -> None:
        """Verify check_example_structure is unchanged."""
        assert check_example_structure is not None
        assert callable(check_example_structure)

    def test_timeout_handling_preserved(self) -> None:
        """Verify timeout handling is preserved across all functions."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        # All three functions should have timeout parameters
        timeout_count = content.count("timeout=")
        assert timeout_count >= 3, "Expected at least 3 timeout specifications"

    def test_error_handling_consistent(self) -> None:
        """Verify consistent error handling pattern across functions."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        # Should have consistent "timed out" error detection
        timed_out_checks = content.count('"timed out" in')
        assert timed_out_checks >= 3, "Expected at least 3 'timed out' checks"

    def test_backward_compatibility_maintained(self) -> None:
        """Verify backward compatibility - return types unchanged."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        # Return types should still be FlextResult
        assert "FlextResult[dict[str, object]]" in content
        assert "FlextResult[" in content

    def test_imports_section_clean(self) -> None:
        """Verify imports section is clean."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        lines = content.split("\n")
        for i, line in enumerate(lines[10:50]):  # Check import section
            if line.startswith(("import subprocess", "from subprocess")):
                pytest.fail(f"subprocess import found at line {i + 10}: {line}")

    def test_wrapper_pattern_used(self) -> None:
        """Verify wrapper.unwrap() pattern is used correctly."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        # Should use wrapper.unwrap() pattern
        assert "wrapper = result.unwrap()" in content

    def test_python3_execution_preserved(self) -> None:
        """Verify python3 execution is preserved in commands."""
        content = self.EXAMPLE_HELPER_PATH.read_text()

        # Commands should still use python3
        assert '"python3"' in content or "'python3'" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
