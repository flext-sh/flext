#!/usr/bin/env python
"""
Validate imports for all submodule projects.

Per CLAUDE.md RULE 4: Complete delivery with zero tolerance for violations.
Test ALL projects to identify real broken imports vs path issues.
"""

import subprocess
from pathlib import Path


class ProjectImportValidator:
    """Validate imports for all projects systematically."""

    def __init__(self):
        """Initialize validator."""
        self.workspace_root = Path("/home/marlonsc/pyauto")
        self.submodules = self._get_submodules()
        self.working_projects = []
        self.broken_projects = []

    def _get_submodules(self) -> list[str]:
        """Get all git submodules."""
        try:
            result = subprocess.run(
                ["git", "submodule", "status"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=True,
            )
            submodules = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        submodules.append(parts[1])
            return sorted(submodules)
        except subprocess.CalledProcessError:
            return []

    def get_project_module_name(self, project_name: str) -> str:
        """Get expected Python module name for project."""
        return project_name.replace("-", "_")

    def test_project_import(self, project_name: str) -> tuple[bool, str]:
        """Test if project module can be imported."""
        project_path = self.workspace_root / project_name
        src_path = project_path / "src"
        module_name = self.get_project_module_name(project_name)

        if not project_path.exists():
            return False, f"Project directory {project_path} does not exist"

        if not src_path.exists():
            return False, f"Source directory {src_path} does not exist"

        module_path = src_path / module_name
        if not module_path.exists():
            return False, f"Module directory {module_path} does not exist"

        init_file = module_path / "__init__.py"
        if not init_file.exists():
            return False, f"Module __init__.py {init_file} does not exist"

        # Test actual import
        try:
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    f"import sys; sys.path.insert(0, '{src_path}'); import {module_name}; print('✅ Success')",
                ],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return True, "Import successful"
            return False, f"Import error: {result.stderr.strip()}"

        except subprocess.TimeoutExpired:
            return False, "Import timeout"
        except Exception as e:
            return False, f"Test error: {e}"

    def test_poetry_install(self, project_name: str) -> tuple[bool, str]:
        """Test if project can be installed with poetry."""
        project_path = self.workspace_root / project_name

        if not (project_path / "pyproject.toml").exists():
            return False, "No pyproject.toml found"

        try:
            result = subprocess.run(
                ["poetry", "check"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return True, "Poetry check passed"
            return False, f"Poetry check failed: {result.stderr.strip()}"

        except subprocess.TimeoutExpired:
            return False, "Poetry check timeout"
        except Exception as e:
            return False, f"Poetry test error: {e}"

    def validate_all_projects(self) -> None:
        """Validate all projects systematically."""

        for project_name in self.submodules:
            # Test import
            import_success, import_msg = self.test_project_import(project_name)

            # Test poetry
            poetry_success, poetry_msg = self.test_poetry_install(project_name)

            # Categorize project
            if import_success and poetry_success:
                self.working_projects.append(project_name)
            else:
                self.broken_projects.append(
                    {
                        "name": project_name,
                        "import_error": None if import_success else import_msg,
                        "poetry_error": None if poetry_success else poetry_msg,
                    }
                )

        # Summary

        if self.broken_projects:
            for project in self.broken_projects:
                if project["import_error"]:
                    pass
                if project["poetry_error"]:
                    pass

        # Log to token
        with open(self.workspace_root / ".token", "a") as f:
            f.write(
                f"PROJECT-VALIDATION-003: {len(self.working_projects)}/{len(self.submodules)} projects working\n"
            )

        return self.working_projects, self.broken_projects


if __name__ == "__main__":
    validator = ProjectImportValidator()
    working, broken = validator.validate_all_projects()
