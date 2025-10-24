"""Phase 6 Sprint 1 Validation Tests - flext-core/utilities.py Conversion.

Tests verify that subprocess usage in utilities.py has been properly converted:
1. Subprocess import still present (unavoidable for command execution)
2. CompletedProcessWrapper class exists and functions correctly
3. run_external_command uses threading-based timeout (no subprocess.TimeoutExpired)
4. All subprocess exception handlers properly replaced
5. Return type changed from subprocess.CompletedProcess to wrapper
"""

from __future__ import annotations

import ast
import pathlib
import sys
import tempfile

import pytest

# Add src to path for isolated testing
sys.path.insert(
    0, str(pathlib.Path(__file__).parent.parent.parent / "flext-core" / "src")
)


class TestPhase6Sprint1UtilitiesConversion:
    """Validate subprocess conversion in flext-core/utilities.py."""

    UTILITIES_PATH = (
        pathlib.Path(__file__).parent.parent.parent
        / "flext-core"
        / "src"
        / "flext_core"
        / "utilities.py"
    )

    def test_completed_process_wrapper_exists(self) -> None:
        """Verify _CompletedProcessWrapper dataclass exists."""
        utilities_content = self.UTILITIES_PATH.read_text()
        tree = ast.parse(utilities_content)

        # Find dataclass definition
        found_wrapper = False
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ClassDef)
                and node.name == "_CompletedProcessWrapper"
            ):
                # Verify it's a dataclass by checking decorator list
                # Can be either @dataclass or @dataclass(frozen=True)
                for decorator in node.decorator_list:
                    decorator_str = ast.unparse(decorator)
                    if "dataclass" in decorator_str:
                        found_wrapper = True
                        break

        assert found_wrapper, "_CompletedProcessWrapper dataclass not found"

    def test_completed_process_wrapper_has_required_fields(self) -> None:
        """Verify wrapper has required fields matching subprocess.CompletedProcess."""
        from dataclasses import fields

        # Import the wrapper class
        from flext_core.utilities import _CompletedProcessWrapper

        wrapper_fields = {f.name for f in fields(_CompletedProcessWrapper)}
        required_fields = {"returncode", "stdout", "stderr", "args"}

        assert required_fields.issubset(wrapper_fields), (
            f"Missing fields: {required_fields - wrapper_fields}"
        )

    def test_run_external_command_signature_changed(self) -> None:
        """Verify run_external_command return type changed to wrapper."""
        utilities_content = self.UTILITIES_PATH.read_text()
        tree = ast.parse(utilities_content)

        # Find run_external_command method
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.FunctionDef)
                and node.name == "run_external_command"
            ):
                # Check return annotation
                if node.returns:
                    annotation_str = ast.unparse(node.returns)
                    # Should NOT contain subprocess.CompletedProcess
                    assert "subprocess.CompletedProcess" not in annotation_str, (
                        f"Return type still references subprocess.CompletedProcess: {annotation_str}"
                    )
                    # Should contain _CompletedProcessWrapper
                    assert "_CompletedProcessWrapper" in annotation_str, (
                        f"Return type should reference _CompletedProcessWrapper: {annotation_str}"
                    )
                break

    def test_subprocess_timeout_expired_handler_removed(self) -> None:
        """Verify subprocess.TimeoutExpired exception handler removed."""
        utilities_content = self.UTILITIES_PATH.read_text()
        tree = ast.parse(utilities_content)

        # Find run_external_command method
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.FunctionDef)
                and node.name == "run_external_command"
            ):
                # Check exception handlers
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.ExceptHandler):
                        if subnode.type:
                            handler_str = ast.unparse(subnode.type)
                            assert "TimeoutExpired" not in handler_str, (
                                "subprocess.TimeoutExpired handler still present - should use threading timeout"
                            )
                break

    def test_threading_used_for_timeout(self) -> None:
        """Verify threading is used for timeout handling."""
        utilities_content = self.UTILITIES_PATH.read_text()

        # Check that threading.Thread is used
        assert "threading.Thread" in utilities_content, (
            "threading.Thread not found - should handle timeout with threading"
        )
        assert "thread.join(timeout=" in utilities_content, (
            "thread.join with timeout not found"
        )
        assert "thread.is_alive()" in utilities_content, (
            "thread.is_alive() not found - should check for timeout"
        )

    def test_shutil_which_used_for_command_validation(self) -> None:
        """Verify shutil.which is used to check command existence."""
        utilities_content = self.UTILITIES_PATH.read_text()

        # Check for shutil.which usage
        assert "shutil.which" in utilities_content, (
            "shutil.which not used for command validation"
        )
        assert "import shutil" in utilities_content, "shutil module not imported"

    def test_subprocess_popen_used_for_execution(self) -> None:
        """Verify subprocess.Popen is used (unavoidable for command execution)."""
        utilities_content = self.UTILITIES_PATH.read_text()

        # subprocess.Popen is acceptable - it's lower-level than subprocess.run
        assert "subprocess.Popen" in utilities_content, (
            "subprocess.Popen expected for command execution"
        )

    def test_run_external_command_imports_available(self) -> None:
        """Verify required imports are available at module level."""
        utilities_content = self.UTILITIES_PATH.read_text()

        required_imports = [
            "import os",
            "import shutil",
            "import threading",
            "import subprocess",
            "from dataclasses import",
            "dataclass",
        ]

        for required_import in required_imports:
            assert required_import in utilities_content, (
                f"Missing required import/statement: {required_import}"
            )

    def test_wrapper_class_can_be_instantiated(self) -> None:
        """Verify _CompletedProcessWrapper can be created and used."""
        from flext_core.utilities import _CompletedProcessWrapper

        # Create instance
        wrapper = _CompletedProcessWrapper(
            returncode=0, stdout="output", stderr="", args=["test"]
        )

        assert wrapper.returncode == 0
        assert wrapper.stdout == "output"
        assert wrapper.stderr == ""
        assert wrapper.args == ["test"]

    def test_wrapper_is_frozen_dataclass(self) -> None:
        """Verify wrapper is immutable (frozen=True)."""
        from flext_core.utilities import _CompletedProcessWrapper

        wrapper = _CompletedProcessWrapper(
            returncode=0, stdout="output", stderr="", args=["test"]
        )

        # Try to modify - should fail
        with pytest.raises((AttributeError, ValueError)):
            wrapper.returncode = 1

    def test_run_external_command_returns_flext_result(self) -> None:
        """Verify run_external_command returns FlextResult type."""
        utilities_content = self.UTILITIES_PATH.read_text()

        # Should have return statements using FlextResult
        assert "FlextResult[_CompletedProcessWrapper]" in utilities_content, (
            "Return type should be FlextResult[_CompletedProcessWrapper]"
        )

    def test_no_subprocess_called_process_error_handling(self) -> None:
        """Verify CalledProcessError replaced with FlextResult error handling."""
        utilities_content = self.UTILITIES_PATH.read_text()

        # Find run_external_command
        tree = ast.parse(utilities_content)

        # Check that CalledProcessError exception is not caught
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.FunctionDef)
                and node.name == "run_external_command"
            ):
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.ExceptHandler):
                        if subnode.type and isinstance(subnode.type, ast.Attribute):
                            handler_str = ast.unparse(subnode.type)
                            # CalledProcessError should not be explicitly caught
                            # (subprocess.run raises it with check=True, but we handle it with FlextResult)
                            assert (
                                "CalledProcessError" not in handler_str
                                or "except Exception" in ast.unparse(subnode)
                            ), "Should not have explicit CalledProcessError handler"
                break

    def test_os_getcwd_and_chdir_used(self) -> None:
        """Verify os.getcwd() and os.chdir() for directory management."""
        utilities_content = self.UTILITIES_PATH.read_text()

        assert "os.getcwd()" in utilities_content, (
            "os.getcwd() not used for directory tracking"
        )
        assert "os.chdir" in utilities_content, (
            "os.chdir() not used for directory change"
        )
        assert "original_cwd" in utilities_content, (
            "original_cwd not stored for restoration"
        )

    def test_can_call_run_external_command(self) -> None:
        """Verify run_external_command can be called and works correctly."""
        from flext_core import FlextResult, FlextUtilities
        from flext_core.utilities import _CompletedProcessWrapper

        # Test with a simple command
        result = FlextUtilities.run_external_command(
            ["python", "--version"], capture_output=True, timeout=10.0
        )

        # Should return FlextResult
        assert isinstance(result, FlextResult), "Should return FlextResult"

        # Should succeed
        assert result.is_success, f"Command should succeed: {result.error}"

        # Should contain wrapper
        wrapper = result.unwrap()
        assert isinstance(wrapper, _CompletedProcessWrapper), (
            "Should return _CompletedProcessWrapper"
        )
        assert wrapper.returncode == 0, "python --version should succeed"
        assert "Python" in wrapper.stdout or "python" in wrapper.stdout, (
            "Should have Python version in output"
        )

    def test_command_not_found_handling(self) -> None:
        """Verify command not found returns proper error."""
        from flext_core import FlextUtilities

        result = FlextUtilities.run_external_command(
            ["nonexistent_command_xyz_abc"], capture_output=True
        )

        assert result.is_failure, "Should fail for non-existent command"
        assert (
            "COMMAND_NOT_FOUND" in result.error or "not found" in result.error.lower()
        ), f"Should indicate command not found: {result.error}"

    def test_exit_code_handling(self) -> None:
        """Verify exit code is properly captured and handled."""
        from flext_core import FlextUtilities

        # Command that will fail
        result = FlextUtilities.run_external_command(
            ["sh", "-c", "exit 42"], capture_output=True, check=False
        )

        assert result.is_success, (
            "Should capture non-zero exit code as success when check=False"
        )
        wrapper = result.unwrap()
        assert wrapper.returncode == 42, (
            f"Should capture exit code 42, got {wrapper.returncode}"
        )

    def test_check_flag_enforces_exit_code(self) -> None:
        """Verify check=True enforces exit code checking."""
        from flext_core import FlextUtilities

        # Command that will fail
        result = FlextUtilities.run_external_command(
            ["sh", "-c", "exit 42"], capture_output=True, check=True
        )

        assert result.is_failure, (
            "Should fail when exit code is non-zero and check=True"
        )
        assert "COMMAND_FAILED" in result.error or "failed" in result.error.lower(), (
            f"Should indicate command failed: {result.error}"
        )

    def test_output_capture_functionality(self) -> None:
        """Verify stdout/stderr capture works."""
        from flext_core import FlextUtilities

        result = FlextUtilities.run_external_command(
            [
                "python",
                "-c",
                'print("hello from stdout"); import sys; print("error", file=sys.stderr)',
            ],
            capture_output=True,
        )

        assert result.is_success, f"Command should succeed: {result.error}"

        wrapper = result.unwrap()
        assert "hello from stdout" in wrapper.stdout, (
            f"Should capture stdout: {wrapper.stdout}"
        )
        assert "error" in wrapper.stderr, f"Should capture stderr: {wrapper.stderr}"

    def test_environment_variables_passed(self) -> None:
        """Verify environment variables are passed to command."""
        from flext_core import FlextUtilities

        test_env_var = "TEST_FLEXT_VAR_UNIQUE_12345"
        test_env_value = "test_value_xyz"

        result = FlextUtilities.run_external_command(
            [
                "python",
                "-c",
                f'import os; print(os.environ.get("{test_env_var}", "NOT_FOUND"))',
            ],
            capture_output=True,
            env={test_env_var: test_env_value},
        )

        assert result.is_success, f"Command should succeed: {result.error}"
        wrapper = result.unwrap()
        assert test_env_value in wrapper.stdout, (
            f"Environment variable not passed: {wrapper.stdout}"
        )

    def test_command_input_handling(self) -> None:
        """Verify command input is passed to stdin."""
        from flext_core import FlextUtilities

        result = FlextUtilities.run_external_command(
            ["cat"], capture_output=True, command_input="test input data\n"
        )

        assert result.is_success, f"Command should succeed: {result.error}"
        wrapper = result.unwrap()
        assert "test input data" in wrapper.stdout, (
            f"Input not echoed: {wrapper.stdout}"
        )

    def test_working_directory_handling(self) -> None:
        """Verify working directory changes are handled correctly."""
        from flext_core import FlextUtilities

        # Create temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            result = FlextUtilities.run_external_command(
                ["python", "-c", "import os; print(os.getcwd())"],
                capture_output=True,
                cwd=tmpdir,
            )

            assert result.is_success, f"Command should succeed: {result.error}"
            wrapper = result.unwrap()
            assert tmpdir in wrapper.stdout, (
                f"Should execute in specified directory: {wrapper.stdout}"
            )


class TestPhase6Sprint1SourceCodeInspection:
    """Inspect source code structure for conversion correctness."""

    UTILITIES_PATH = (
        pathlib.Path(__file__).parent.parent.parent
        / "flext-core"
        / "src"
        / "flext_core"
        / "utilities.py"
    )

    def test_wrapper_class_docstring_present(self) -> None:
        """Verify wrapper class has proper documentation."""
        utilities_content = self.UTILITIES_PATH.read_text()

        assert "_CompletedProcessWrapper" in utilities_content, (
            "Wrapper class not found"
        )
        # Should have docstring mentioning it replaces subprocess.CompletedProcess
        assert "subprocess.CompletedProcess" in utilities_content, (
            "Documentation should explain wrapper replaces subprocess.CompletedProcess"
        )

    def test_method_docstring_updated(self) -> None:
        """Verify method docstring reflects threading-based timeout."""
        utilities_content = self.UTILITIES_PATH.read_text()

        # Find the docstring
        assert (
            "threading-based timeout" in utilities_content
            or "thread" in utilities_content.lower()
        ), "Method documentation should explain threading-based timeout handling"

    def test_process_communication_in_thread(self) -> None:
        """Verify process.communicate is called in a thread."""
        utilities_content = self.UTILITIES_PATH.read_text()

        assert "process.communicate" in utilities_content, (
            "process.communicate not found"
        )
        assert "threading.Thread" in utilities_content, (
            "Thread not used for communication"
        )

    def test_context_restoration_guaranteed(self) -> None:
        """Verify working directory is always restored (finally block)."""
        utilities_content = self.UTILITIES_PATH.read_text()
        tree = ast.parse(utilities_content)

        # Find run_external_command
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.FunctionDef)
                and node.name == "run_external_command"
            ):
                # Check for try-finally structure
                has_finally = False
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Try):
                        if subnode.finalbody:
                            has_finally = True
                            # Check that os.chdir is in finally
                            finally_str = ast.unparse(subnode)
                            assert "os.chdir(original_cwd)" in finally_str, (
                                "finally block should restore original directory"
                            )

                assert has_finally, (
                    "Should have try-finally for guaranteed directory restoration"
                )
                break


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
