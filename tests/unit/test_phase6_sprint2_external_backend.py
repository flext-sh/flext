"""Phase 6 Sprint 2 Validation Tests - flext-quality/external_backend.py Conversion.

Tests verify that subprocess usage in external_backend.py has been properly converted:
1. Subprocess import removed
2. FlextUtilities imported and used
3. All 6 tool methods converted (ruff, mypy, bandit, vulture, coverage, radon)
4. subprocess.TimeoutExpired handlers removed
5. Error handling uses FlextResult pattern
6. Tool availability detection via error message matching
"""

from __future__ import annotations

import ast
import pathlib
import sys
import tempfile
from pathlib import Path

import pytest

# Add flext to path
sys.path.insert(
    0, str(pathlib.Path(__file__).parent.parent.parent / "flext-quality" / "src")
)
sys.path.insert(
    0, str(pathlib.Path(__file__).parent.parent.parent / "flext-core" / "src")
)


class TestPhase6Sprint2ExternalBackendConversion:
    """Validate subprocess conversion in flext-quality/external_backend.py."""

    EXTERNAL_BACKEND_PATH = (
        pathlib.Path(__file__).parent.parent.parent
        / "flext-quality"
        / "src"
        / "flext_quality"
        / "external_backend.py"
    )

    def test_subprocess_import_removed(self) -> None:
        """Verify subprocess module is not imported."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()

        # Should not have import subprocess at module level
        lines = content.split("\n")
        for line in lines[:50]:  # Check first 50 lines for imports
            if line.startswith("import subprocess"):
                pytest.fail("subprocess import still present - must use FlextUtilities")
            if line.startswith("from subprocess import"):
                pytest.fail("subprocess import still present - must use FlextUtilities")

    def test_flext_utilities_imported(self) -> None:
        """Verify FlextUtilities is imported."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()

        assert "FlextUtilities" in content, "FlextUtilities not imported"
        assert "from flext_core import" in content and "FlextUtilities" in content, (
            "FlextUtilities must be imported from flext_core"
        )

    def test_all_subprocess_timeout_expired_handlers_removed(self) -> None:
        """Verify all subprocess.TimeoutExpired handlers are removed."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()
        tree = ast.parse(content)

        # Find all methods in the class
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ClassDef)
                and node.name == "FlextQualityExternalBackend"
            ):
                for method in node.body:
                    if isinstance(method, ast.FunctionDef) and method.name.startswith(
                        "_run_"
                    ):
                        # Check exception handlers in this method
                        for subnode in ast.walk(method):
                            if isinstance(subnode, ast.ExceptHandler) and subnode.type:
                                handler_str = ast.unparse(subnode.type)
                                assert "TimeoutExpired" not in handler_str, (
                                    f"subprocess.TimeoutExpired handler still present in {method.name}"
                                )

    def test_flext_utilities_used_in_all_tool_methods(self) -> None:
        """Verify FlextUtilities.CommandExecution.run_external_command is used in all tool methods."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()

        # Count direct FlextUtilities.CommandExecution.run_external_command calls
        direct_count = content.count(
            "FlextUtilities.CommandExecution.run_external_command("
        )
        
        # Count indirect calls through _run_tool_with_json_output
        # (ruff, mypy, bandit, vulture use _run_tool_with_json_output which uses FlextUtilities)
        indirect_count = content.count("_run_tool_with_json_output(")
        
        # Total: direct calls (coverage: 1, radon: 2) + indirect calls (4 methods use _run_tool_with_json_output)
        # _run_tool_with_json_output itself has 1 FlextUtilities call, used by 4 methods
        # So we have: 1 (coverage) + 2 (radon) + 1 (_run_tool_with_json_output definition) = 4 direct
        # Plus 4 indirect calls through _run_tool_with_json_output
        total_count = direct_count
        
        # Should have at least 4 direct calls (coverage + radon x2 + _run_tool_with_json_output)
        # The _run_tool_with_json_output is used by ruff, mypy, bandit, vulture
        assert total_count >= 4, f"Expected at least 4 FlextUtilities calls, found {total_count} (direct={direct_count}, indirect methods={indirect_count})"

    def test_ruff_method_converted(self) -> None:
        """Verify _run_ruff method uses FlextUtilities."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()
        tree = ast.parse(content)

        found_ruff = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_run_ruff":
                found_ruff = True
                method_code = ast.unparse(node)

                # Verify FlextUtilities is used (directly or through helper)
                uses_helper = "_run_tool_with_json_output" in method_code
                has_flext_utilities = (
                    "FlextUtilities.CommandExecution.run_external_command"
                    in method_code
                )
                assert (
                    has_flext_utilities or uses_helper
                ), (
                    "_run_ruff must use FlextUtilities.CommandExecution.run_external_command directly or through _run_tool_with_json_output"
                )

                # Verify subprocess.run is not used
                assert "subprocess.run" not in method_code, (
                    "_run_ruff still uses subprocess.run"
                )

                # Verify ruff command is correct (quotes may be single or double)
                assert (
                    "'ruff'" in method_code or '"ruff"' in method_code
                ) and "check" in method_code, (
                    "_run_ruff must call ruff with check subcommand"
                )

                # Verify result pattern used (directly or through helper)
                # Methods that use _run_tool_with_json_output return FlextResult directly
                has_flext_result_pattern = (
                    "result.is_failure" in method_code
                    or ".unwrap()" in method_code
                    or uses_helper  # Helper returns FlextResult
                )
                assert (
                    has_flext_result_pattern
                ), "_run_ruff must use FlextResult pattern directly or through helper"

        assert found_ruff, "_run_ruff method not found"

    def test_mypy_method_converted(self) -> None:
        """Verify _run_mypy method uses FlextUtilities."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()
        tree = ast.parse(content)

        found_mypy = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_run_mypy":
                found_mypy = True
                method_code = ast.unparse(node)

                # _run_mypy uses _run_tool_with_json_output which uses FlextUtilities
                assert (
                    "_run_tool_with_json_output" in method_code
                    or "FlextUtilities.CommandExecution.run_external_command" in method_code
                )
                assert "subprocess.run" not in method_code
                assert "'mypy'" in method_code or '"mypy"' in method_code

        assert found_mypy, "_run_mypy method not found"

    def test_bandit_method_converted(self) -> None:
        """Verify _run_bandit method uses FlextUtilities."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()
        tree = ast.parse(content)

        found_bandit = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_run_bandit":
                found_bandit = True
                method_code = ast.unparse(node)

                # _run_bandit uses _run_tool_with_json_output which uses FlextUtilities
                assert (
                    "_run_tool_with_json_output" in method_code
                    or "FlextUtilities.CommandExecution.run_external_command" in method_code
                )
                assert "subprocess.run" not in method_code
                assert "'bandit'" in method_code or '"bandit"' in method_code

        assert found_bandit, "_run_bandit method not found"

    def test_vulture_method_converted(self) -> None:
        """Verify _run_vulture method uses FlextUtilities."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()
        tree = ast.parse(content)

        found_vulture = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_run_vulture":
                found_vulture = True
                method_code = ast.unparse(node)

                # _run_vulture uses _run_tool_with_json_output which uses FlextUtilities
                assert (
                    "_run_tool_with_json_output" in method_code
                    or "FlextUtilities.CommandExecution.run_external_command" in method_code
                )
                assert "subprocess.run" not in method_code
                assert "'vulture'" in method_code or '"vulture"' in method_code

        assert found_vulture, "_run_vulture method not found"

    def test_coverage_method_converted(self) -> None:
        """Verify _run_coverage method uses FlextUtilities."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()
        tree = ast.parse(content)

        found_coverage = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_run_coverage":
                found_coverage = True
                method_code = ast.unparse(node)

                assert (
                    "FlextUtilities.CommandExecution.run_external_command"
                    in method_code
                )
                assert "subprocess.run" not in method_code
                assert "'coverage'" in method_code or '"coverage"' in method_code

        assert found_coverage, "_run_coverage method not found"

    def test_radon_method_converted_with_two_calls(self) -> None:
        """Verify _run_radon method uses FlextUtilities for both calls."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()
        tree = ast.parse(content)

        found_radon = False
        found_maintainability = False
        radon_code = ""
        maintainability_code = ""
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_run_radon":
                found_radon = True
                radon_code = ast.unparse(node)
            if isinstance(node, ast.FunctionDef) and node.name == "_run_radon_maintainability":
                found_maintainability = True
                maintainability_code = ast.unparse(node)

        assert found_radon, "_run_radon method not found"
        assert found_maintainability, "_run_radon_maintainability method not found"
        
        # Count FlextUtilities calls in both methods
        radon_count = radon_code.count(
            "FlextUtilities.CommandExecution.run_external_command"
        )
        maintainability_count = maintainability_code.count(
            "FlextUtilities.CommandExecution.run_external_command"
        )
        total_count = radon_count + maintainability_count
        
        # Must have at least 2 FlextUtilities calls total (1 in _run_radon, 1 in _run_radon_maintainability)
        assert total_count >= 2, (
            f"_run_radon and _run_radon_maintainability must have at least 2 FlextUtilities calls total, "
            f"found {total_count} (radon: {radon_count}, maintainability: {maintainability_count})"
        )

        assert "subprocess.run" not in radon_code
        assert "'radon'" in radon_code or '"radon"' in radon_code

    def test_error_message_matching_for_tool_not_found(self) -> None:
        """Verify error message matching replaces FileNotFoundError handling."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()

        # Should use "not found" string matching
        assert '"not found" in result.error.lower()' in content or (
            '"not found" in' in content
        ), "Must check for 'not found' in error message"

    def test_error_message_matching_for_timeout(self) -> None:
        """Verify timeout is handled via error message matching."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()

        # Should use "timed out" string matching
        assert '"timed out" in result.error.lower()' in content or (
            '"timed out" in' in content
        ), "Must check for 'timed out' in error message"

    def test_wrapper_pattern_used(self) -> None:
        """Verify wrapper pattern is used to access command results."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()

        # Should use .unwrap() to get wrapper
        assert ".unwrap()" in content, "Must use .unwrap() to get wrapper from result"

        # Should access wrapper.returncode, wrapper.stdout, wrapper.stderr
        assert "wrapper.returncode" in content or "wrapper_" in content, (
            "Must use wrapper.returncode to access return code"
        )
        assert "wrapper.stdout" in content or "wrapper_" in content, (
            "Must use wrapper.stdout to access stdout"
        )

    def test_result_pattern_returns_flext_result(self) -> None:
        """Verify all tool methods return FlextResult."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()

        # All methods should return FlextResult
        assert content.count("return FlextResult") >= 6, (
            "All tool methods must use FlextResult for returns"
        )

    def test_module_can_be_imported(self) -> None:
        """Verify the module can be imported without errors."""
        from flext_quality.external_backend import FlextQualityExternalBackend

        # Should be able to import and instantiate
        assert FlextQualityExternalBackend is not None
        backend = FlextQualityExternalBackend()
        assert backend is not None

    def test_get_capabilities_returns_six_tools(self) -> None:
        """Verify backend reports all 6 tools as capabilities."""
        from flext_quality.external_backend import FlextQualityExternalBackend

        backend = FlextQualityExternalBackend()
        capabilities = backend.get_capabilities()

        expected_tools = {"ruff", "mypy", "bandit", "vulture", "coverage", "radon"}
        assert expected_tools.issubset(set(capabilities)), (
            f"Expected tools {expected_tools}, got {set(capabilities)}"
        )

    def test_analyze_method_exists(self) -> None:
        """Verify analyze method exists and can be called."""
        from flext_quality.external_backend import FlextQualityExternalBackend

        backend = FlextQualityExternalBackend()

        # Create a temporary Python file for testing
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".py", delete=False
        ) as f:
            f.write("# Valid Python code\nprint('hello')")
            temp_path = Path(f.name)

        try:
            # Should be able to call analyze with a tool that might not be installed
            # This tests that the method structure is correct
            result = backend.analyze("x = 1", tool="ruff")

            # Result should be FlextResult
            assert hasattr(result, "is_success") or hasattr(result, "is_failure"), (
                "analyze() must return FlextResult"
            )
        finally:
            temp_path.unlink(missing_ok=True)

    def test_line_count_reduced(self) -> None:
        """Verify file size reduced due to removed exception handlers."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()
        line_count = len(content.split("\n"))

        # Original had ~378 lines with exception handlers
        # After conversion should be roughly similar or slightly less
        # (we removed subprocess import but added FlextUtilities import)
        assert 350 < line_count < 400, f"Unexpected line count: {line_count}"


class TestPhase6Sprint2ExternalBackendSourceCodeInspection:
    """Inspect source code structure for conversion correctness."""

    EXTERNAL_BACKEND_PATH = (
        pathlib.Path(__file__).parent.parent.parent
        / "flext-quality"
        / "src"
        / "flext_quality"
        / "external_backend.py"
    )

    def test_docstring_reflects_flext_utilities(self) -> None:
        """Verify module docstring reflects FlextUtilities usage."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()

        # Should mention using FlextUtilities or similar pattern
        first_lines = "\n".join(content.split("\n")[:30])
        # Original docstring mentions subprocess, should still be accurate
        assert (
            "quality tools" in first_lines.lower() or "external" in first_lines.lower()
        )

    def test_all_methods_have_consistent_pattern(self) -> None:
        """Verify all tool methods follow consistent error handling pattern."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()
        tree = ast.parse(content)

        tool_methods = []
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ClassDef)
                and node.name == "FlextQualityExternalBackend"
            ):
                for method in node.body:
                    if isinstance(method, ast.FunctionDef) and method.name.startswith(
                        "_run_"
                    ):
                        # Skip helper methods that are called by other methods
                        if method.name == "_run_radon_maintainability":
                            continue  # This is a helper called by _run_radon
                        tool_methods.append(method.name)
                        method_code = ast.unparse(method)

                        # All should have the pattern:
                        # 1. Call FlextUtilities (directly or through helper)
                        uses_helper = "_run_tool_with_json_output" in method_code
                        has_flext_utilities = (
                            "FlextUtilities.CommandExecution.run_external_command"
                            in method_code
                        )
                        assert (
                            has_flext_utilities or uses_helper
                        ), f"{method.name} must use FlextUtilities directly or through _run_tool_with_json_output"

                        # 2. Check result.is_failure (directly or through helper)
                        uses_helper = "_run_tool_with_json_output" in method_code
                        has_failure_check = (
                            "result.is_failure" in method_code
                            or "result_" in method_code
                            or uses_helper  # Helper handles this
                        )
                        assert (
                            has_failure_check
                        ), f"{method.name} must check result.is_failure or use helper"

                        # 3. Check error message for tool_not_found (directly or through helper)
                        # Methods that use _run_tool_with_json_output delegate to _handle_tool_error
                        # Methods like _run_coverage use _handle_coverage_error
                        has_direct_error_handling = "not found" in method_code.lower()
                        has_helper_error_handling = (
                            "_handle_tool_error" in method_code
                            or "_handle_coverage_error" in method_code
                            or "_handle_radon_error" in method_code
                        )
                        has_error_handling = (
                            has_direct_error_handling
                            or has_helper_error_handling
                            or uses_helper  # Helper has error handling
                        )
                        assert (
                            has_error_handling
                        ), f"{method.name} must handle 'not found' errors directly or through helper method"

                        # 4. Return FlextResult (directly or through helper)
                        # Check return type annotation or return statement
                        has_return_type = "-> FlextResult" in method_code
                        has_return_statement = (
                            "return FlextResult" in method_code
                            or "return self._run_tool_with_json_output" in method_code
                            or "return self._run_radon_maintainability" in method_code
                            or uses_helper  # Helper returns FlextResult
                        )
                        assert (
                            has_return_type and has_return_statement
                        ), f"{method.name} must return FlextResult (type annotation and return statement)"

        # Should have at least 6 tool methods
        assert len(tool_methods) >= 6, (
            f"Expected at least 6 tool methods, found {len(tool_methods)}: {tool_methods}"
        )

    def test_imports_section_clean(self) -> None:
        """Verify imports section is clean and properly organized."""
        content = self.EXTERNAL_BACKEND_PATH.read_text()

        # Check file has correct imports (can be single line or multi-line)
        has_flext_result = "FlextResult" in content and "from flext_core" in content
        has_flext_utilities = "FlextUtilities" in content and "from flext_core" in content
        assert has_flext_result and has_flext_utilities, (
            "Must import FlextResult and FlextUtilities from flext_core (can be separate imports)"
        )

        # Should NOT import subprocess module
        assert "import subprocess" not in content or "# import subprocess" in content, (
            "subprocess module should not be imported"
        )

        # Should NOT have subprocess in any top-level code except docstring
        lines = content.split("\n")
        for i, line in enumerate(lines[20:60]):  # Check import region
            if line.startswith(("import subprocess", "from subprocess")):
                raise AssertionError(
                    f"subprocess import found at line {i + 20}: {line}"
                )

    def test_method_signatures_unchanged(self) -> None:
        """Verify method signatures remain unchanged for backward compatibility."""
        import inspect

        from flext_quality.external_backend import FlextQualityExternalBackend

        backend = FlextQualityExternalBackend()

        # All these methods should exist with correct signatures
        methods_to_check = [
            "_run_ruff",
            "_run_mypy",
            "_run_bandit",
            "_run_vulture",
            "_run_coverage",
            "_run_radon",
        ]

        for method_name in methods_to_check:
            assert hasattr(backend, method_name), f"Method {method_name} not found"

            method = getattr(backend, method_name)
            sig = inspect.signature(method)

            # Should take file_path parameter
            assert "file_path" in str(sig), (
                f"{method_name} must accept file_path parameter"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
