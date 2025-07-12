"""Development tools for FLEXT workspace."""

import subprocess
from pathlib import Path


class DevToolsManager:
    """Manages development tools across the FLEXT workspace."""

    def __init__(self, workspace_root: Path | None = None) -> None:
        """Initialize DevToolsManager with workspace root."""
        self.workspace_root = workspace_root or Path.cwd()

    def run_tests(self, project: str | None = None) -> int:
        """Run tests for a specific project or all projects."""
        if project:
            project_path = self.workspace_root / project
            if project_path.exists():
                return self._run_project_tests(project_path)
            return 1
        # Run tests for all projects
        return self._run_all_tests()

    def _run_project_tests(self, project_path: Path) -> int:
        """Run tests for a specific project."""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(project_path / "tests")],
                cwd=project_path,
                check=False,
            )
            return result.returncode
        except Exception:
            return 1

    def _run_all_tests(self) -> int:
        """Run tests for all projects in workspace."""
        exit_code = 0
        for project_dir in self.workspace_root.iterdir():
            if project_dir.is_dir() and project_dir.name.startswith("flext-"):
                tests_dir = project_dir / "tests"
                if tests_dir.exists():
                    result = self._run_project_tests(project_dir)
                    if result != 0:
                        exit_code = result
        return exit_code

    def lint_all(self) -> int:
        """Run linting on all projects."""
        try:
            result = subprocess.run(
                ["python", "-m", "ruff", "check", "."],
                cwd=self.workspace_root,
                check=False,
            )
            return result.returncode
        except Exception:
            return 1

    def format_all(self) -> int:
        """Format all projects."""
        try:
            result = subprocess.run(
                ["python", "-m", "ruff", "format", "."],
                cwd=self.workspace_root,
                check=False,
            )
            return result.returncode
        except Exception:
            return 1
