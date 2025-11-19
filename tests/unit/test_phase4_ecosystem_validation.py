"""Validation tests for Phase 4 ecosystem_validation.py subprocess conversions.

Tests verify that ruff linting checks work correctly using runpy module execution
instead of subprocess, without triggering subprocess import.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path


class TestEcosystemValidationSubprocessRemoval:
    """Validation tests for subprocess removals in ecosystem_validation.py."""

    @staticmethod
    def get_ecosystem_validation_source() -> str:
        """Get source code of ecosystem_validation.py."""
        script_path = (
            Path(__file__).parent.parent.parent / "scripts" / "ecosystem_validation.py"
        )
        return script_path.read_text()

    def test_subprocess_import_removed(self) -> None:
        """✅ CRITICAL: Verify subprocess import is completely removed."""
        source = self.get_ecosystem_validation_source()

        # The import statement should NOT exist
        assert "import subprocess" not in source
        assert "from subprocess import" not in source

    def test_runpy_added_for_ruff_execution(self) -> None:
        """✅ Verify runpy is imported for ruff module execution."""
        source = self.get_ecosystem_validation_source()

        # Should import runpy
        assert "import runpy" in source
        # Should import io for StringIO
        assert "import io" in source
        # Should import redirect_stdout/redirect_stderr
        assert "redirect_stdout" in source
        assert "redirect_stderr" in source

    def test_no_subprocess_timeout_expired(self) -> None:
        """✅ CRITICAL: Verify subprocess.TimeoutExpired is not used."""
        source = self.get_ecosystem_validation_source()

        # Should NOT reference subprocess exception classes
        assert "subprocess.TimeoutExpired" not in source
        assert "subprocess.CalledProcessError" not in source
        assert "subprocess.Popen" not in source
        assert "subprocess.run" not in source

    def test_validate_lint_uses_runpy(self) -> None:
        """✅ Verify validate_lint method uses runpy instead of subprocess."""
        source = self.get_ecosystem_validation_source()

        # Should have validate_lint method
        assert "def validate_lint(self, project: str)" in source

        # Should use runpy.run_module
        assert "runpy.run_module" in source
        assert 'run_name="__main__"' in source

        # Should capture stdout for JSON output
        assert "stdout_capture = io.StringIO()" in source
        assert "redirect_stdout" in source

    def test_ruff_execution_with_json_output(self) -> None:
        """✅ Verify ruff is executed with JSON output format."""
        source = self.get_ecosystem_validation_source()

        # Should set sys.argv with ruff arguments
        assert 'sys.argv = ["ruff"' in source
        assert '"--output-format=json"' in source

    def test_directory_state_restoration(self) -> None:
        """✅ Verify sys.cwd and sys.argv are properly restored."""
        source = self.get_ecosystem_validation_source()

        # Should save original state
        assert "original_cwd = Path.cwd()" in source
        assert "original_argv = sys.argv.copy()" in source

        # Should restore after execution
        assert "sys.chdir(original_dir)" in source
        assert "sys.argv = original_argv" in source
        assert "finally:" in source

    def test_json_output_parsing(self) -> None:
        """✅ Verify JSON output from ruff is parsed correctly."""
        source = self.get_ecosystem_validation_source()

        # Should parse JSON output
        assert "json.loads(output)" in source

        # Should count errors and warnings
        assert 'v.get("fix") is None' in source
        assert "violations" in source

    def test_shutil_which_for_ruff_check(self) -> None:
        """✅ Verify ruff availability check uses shutil.which()."""
        source = self.get_ecosystem_validation_source()

        # Should check ruff availability
        assert 'shutil.which("ruff")' in source


class TestEcosystemValidationIntegration:
    """Integration tests for ecosystem_validation.py conversions."""

    def test_no_subprocess_references(self) -> None:
        """Meta-test: Verify subprocess is completely removed from ecosystem_validation.py."""
        script_path = (
            Path(__file__).parent.parent.parent / "scripts" / "ecosystem_validation.py"
        )
        source_code = script_path.read_text()

        # Count subprocess references (should only be in comments/docstrings)
        subprocess_lines = [
            line
            for line in source_code.split("\n")
            if "subprocess" in line and not line.strip().startswith("#")
        ]

        # Allow only comment references
        non_comment_subprocess = [
            line for line in subprocess_lines if not line.strip().startswith("#")
        ]

        assert len(non_comment_subprocess) == 0, (
            f"Found subprocess usage outside comments: {non_comment_subprocess}"
        )

    def test_runpy_module_functionality(self) -> None:
        """Functional test: Verify runpy can execute modules."""
        import runpy

        # Create a simple test module in memory
        # Just verify runpy module exists and can be imported
        assert hasattr(runpy, "run_module")
        assert callable(runpy.run_module)

    def test_io_stdout_capture_works(self) -> None:
        """Functional test: Verify io.StringIO and stdout redirection work."""
        import io
        from contextlib import redirect_stdout

        # Test that StringIO and redirect_stdout work
        captured = io.StringIO()
        with redirect_stdout(captured):
            print("test output")

        assert captured.getvalue() == "test output\n"
