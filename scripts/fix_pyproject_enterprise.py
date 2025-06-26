#!/usr/bin/env python
"""Fix ALL pyproject.toml files to PEP8 strict standards and reorganize file structure.

Per CLAUDE.md RULE 4: Complete delivery with zero tolerance for violations.
ABSOLUTELY ZERO warnings/errors, PEP8 TOTAL compliance.
"""

import shutil
import subprocess
from pathlib import Path


class PyProjectEnterpriseStandardizer:
    """Fix pyproject.toml files to enterprise PEP8 strict standards."""

    def __init__(self, workspace_root: Path):
        """Initialize standardizer."""
        self.workspace_root = workspace_root
        self.template_path = workspace_root / "pyproject-template.toml"
        self.submodules = self._get_submodules()
        self.fixed_projects = []
        self.errors = []

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

    def load_template(self) -> dict:
        """Load enterprise template configuration."""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

        return toml.load(self.template_path)

    def identify_project_type(self, project_name: str) -> str:
        """Identify project type for specific configurations."""
        if project_name.startswith("tap-"):
            return "singer_tap"
        if project_name.startswith("target-"):
            return "singer_target"
        if project_name.startswith("flx-"):
            return "flx_component"
        if project_name.startswith("dbt-"):
            return "dbt_package"
        return "library"

    def get_project_module_name(self, project_name: str) -> str:
        """Get correct Python module name."""
        return project_name.replace("-", "_")

    def analyze_current_structure(self, project_path: Path) -> dict:
        """Analyze current project structure for reorganization needs."""
        structure_issues = []

        # Check for src/ directory
        if not (project_path / "src").exists():
            structure_issues.append("missing_src_directory")

        # Check for tests/ directory
        if not (project_path / "tests").exists():
            structure_issues.append("missing_tests_directory")

        # Check for README.md
        if not (project_path / "README.md").exists():
            structure_issues.append("missing_readme")

        # Check for proper package structure in src/
        module_name = self.get_project_module_name(project_path.name)
        expected_module_path = project_path / "src" / module_name
        if not expected_module_path.exists():
            # Check if module exists in wrong location
            for potential_path in [
                project_path / module_name,
                project_path / project_path.name,
                project_path / "src" / project_path.name,
            ]:
                if potential_path.exists():
                    structure_issues.append(
                        f"module_in_wrong_location:{potential_path}",
                    )
                    break
                structure_issues.append("missing_module_directory")

        return {
            "issues": structure_issues,
            "needs_reorganization": len(structure_issues) > 0,
        }

    def reorganize_file_structure(self, project_path: Path) -> bool:
        """Reorganize files to correct PEP8 structure."""
        module_name = self.get_project_module_name(project_path.name)
        src_dir = project_path / "src"
        tests_dir = project_path / "tests"
        correct_module_path = src_dir / module_name

        try:
            # Create src/ directory if missing
            if not src_dir.exists():
                src_dir.mkdir(exist_ok=True)

            # Create tests/ directory if missing
            if not tests_dir.exists():
                tests_dir.mkdir(exist_ok=True)
                (tests_dir / "__init__.py").write_text(
                    '"""Tests for ' + project_path.name + '."""\n',
                )
                (tests_dir / "conftest.py").write_text(
                    '"""Test configuration."""\n\nimport pytest\n',
                )
                (tests_dir / f"test_{module_name}.py").write_text(
                    f'"""Tests for {module_name}."""\n\n\ndef test_import():\n    """Test that module imports correctly."""\n    import {module_name}\n    assert {module_name}\n',
                )

            # Move module to correct location
            wrong_locations = [
                project_path / module_name,
                project_path / project_path.name,
                src_dir / project_path.name,
            ]

            for wrong_location in wrong_locations:
                if wrong_location.exists() and wrong_location != correct_module_path:
                    if correct_module_path.exists():
                        shutil.rmtree(correct_module_path)
                    shutil.move(str(wrong_location), str(correct_module_path))
                    break

            # Ensure module directory exists with __init__.py
            if not correct_module_path.exists():
                correct_module_path.mkdir(parents=True, exist_ok=True)

            if not (correct_module_path / "__init__.py").exists():
                init_content = f'"""Module {module_name}."""\n\nfrom {module_name}.__version__ import __version__\n\n__all__ = ["__version__"]\n'
                (correct_module_path / "__init__.py").write_text(init_content)

            # Ensure __version__.py exists
            version_file = correct_module_path / "__version__.py"
            if not version_file.exists():
                version_content = f'"""Version information for {module_name}."""\n\n__version__ = "0.5.0"\n__version_info__ = tuple(int(x) for x in __version__.split("."))\n'
                version_file.write_text(version_content)

            # Create README.md if missing
            readme_path = project_path / "README.md"
            if not readme_path.exists():
                readme_content = f"""# {project_path.name}

PyAuto Enterprise - {project_path.name} component

## Installation

```bash
poetry install
```

## Usage

```python
import {module_name}
```

## Development

```bash
make install
make test
make lint
```

## License

MIT
"""
                readme_path.write_text(readme_content)

            return True

        except Exception as e:
            self.errors.append(f"{project_path.name}: {e}")
            return False

    def create_enterprise_pyproject(self, project_path: Path) -> bool:
        """Create enterprise-standard pyproject.toml."""
        try:
            template = self.load_template()
            project_name = project_path.name
            module_name = self.get_project_module_name(project_name)
            project_type = self.identify_project_type(project_name)

            # Build new configuration
            config = {}

            # 1. Build system (MUST be first per PEP 621)
            config["build-system"] = template["build-system"]

            # 2. Project metadata
            config["tool"] = {"poetry": {}}
            poetry_config = config["tool"]["poetry"]

            # Basic metadata
            poetry_config["name"] = project_name
            poetry_config["version"] = "0.5.0"
            poetry_config["description"] = (
                f"PyAuto Enterprise - {project_name} component"
            )
            poetry_config["authors"] = ["Marlon Costa <marlon.costa@datacosmos.com.br>"]
            poetry_config["license"] = "MIT"
            poetry_config["readme"] = "README.md"
            poetry_config["repository"] = (
                f"https://github.com/datacosmos-br/{project_name}"
            )
            poetry_config["documentation"] = (
                f"https://github.com/datacosmos-br/{project_name}/blob/main/README.md"
            )
            poetry_config["keywords"] = ["pyauto", "enterprise", "data", "integration"]

            # Classifiers
            poetry_config["classifiers"] = [
                "Development Status :: 4 - Beta",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.9",
                "Programming Language :: Python :: 3.10",
                "Programming Language :: Python :: 3.11",
                "Programming Language :: Python :: 3.12",
                "Programming Language :: Python :: 3.13",
                "Topic :: Software Development :: Libraries :: Python Modules",
                "Topic :: Database",
                "Topic :: System :: Systems Administration",
                "Typing :: Typed",
            ]

            # Package configuration
            poetry_config["packages"] = [{"include": module_name, "from": "src"}]

            # Dependencies
            poetry_config["dependencies"] = {
                "python": "^3.9,<4.0",
                "pydantic": "^2.11.0",
                "typing-extensions": "^4.12.0",
            }

            # Project-specific dependencies
            if project_type == "singer_tap":
                poetry_config["dependencies"]["singer-sdk"] = "^0.39.0"
                poetry_config["dependencies"]["requests"] = "^2.32.0"
            elif project_type == "singer_target":
                poetry_config["dependencies"]["singer-sdk"] = "^0.39.0"
                poetry_config["dependencies"]["sqlalchemy"] = "^2.0.0"
            elif project_type == "flx_component":
                poetry_config["dependencies"]["structlog"] = "^24.4.0"
                poetry_config["dependencies"]["httpx"] = "^0.28.1"

            # Development dependencies
            poetry_config["group"] = {
                "dev": {
                    "dependencies": template["tool"]["poetry"]["group"]["dev"][
                        "dependencies"
                    ],
                },
                "security": {
                    "dependencies": template["tool"]["poetry"]["group"]["security"][
                        "dependencies"
                    ],
                },
                "build": {
                    "dependencies": template["tool"]["poetry"]["group"]["build"][
                        "dependencies"
                    ],
                },
            }

            # URLs
            poetry_config["urls"] = {
                "Bug Tracker": f"https://github.com/datacosmos-br/{project_name}/issues",
                "Changelog": f"https://github.com/datacosmos-br/{project_name}/blob/main/CHANGELOG.md",
            }

            # CLI scripts for taps/targets
            if project_type in ["singer_tap", "singer_target"]:
                poetry_config["scripts"] = {project_name: f"{module_name}.cli:main"}

            # 3. All tool configurations from template
            for tool_name, tool_config in template["tool"].items():
                if tool_name != "poetry":  # Already handled above
                    config["tool"][tool_name] = tool_config.copy()

            # Update tool-specific configurations
            if (
                "ruff" in config["tool"]
                and "lint" in config["tool"]["ruff"]
                and "isort" in config["tool"]["ruff"]["lint"]
            ):
                config["tool"]["ruff"]["lint"]["isort"]["known-first-party"] = [
                    module_name,
                ]

            if "isort" in config["tool"]:
                config["tool"]["isort"]["known_first_party"] = [module_name]

            if "coverage" in config["tool"] and "html" in config["tool"]["coverage"]:
                config["tool"]["coverage"]["html"][
                    "title"
                ] = f"{project_name} Coverage Report"

            # Replace PROJECT_MODULE placeholders
            config_str = toml.dumps(config)
            config_str = config_str.replace("PROJECT_MODULE", module_name)
            config_str = config_str.replace("PROJECT_NAME", project_name)

            # Write the new pyproject.toml
            pyproject_path = project_path / "pyproject.toml"
            backup_path = project_path / "pyproject.toml.backup"

            # Backup existing file
            if pyproject_path.exists():
                shutil.copy2(pyproject_path, backup_path)

            # Write new configuration
            with open(pyproject_path, "w", encoding="utf-8") as f:
                f.write(config_str)

            return True

        except Exception as e:
            self.errors.append(f"{project_path.name}: {e}")
            return False

    def validate_project(self, project_path: Path) -> bool:
        """Validate project after standardization."""
        try:
            # Check poetry check
            result = subprocess.run(
                ["poetry", "check"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            if result.returncode != 0:
                return False

            # Check if module imports
            module_name = self.get_project_module_name(project_path.name)
            result = subprocess.run(
                [
                    "poetry",
                    "run",
                    "python",
                    "-c",
                    f"import {module_name}; print('✅ Import successful')",
                ],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode != 0:
                return False

            return True

        except Exception:
            return False

    def standardize_all_projects(self) -> None:
        """Standardize all projects to enterprise standards."""
        for submodule in self.submodules:
            project_path = self.workspace_root / submodule

            if not project_path.exists():
                continue

            # Step 1: Reorganize file structure
            if self.reorganize_file_structure(project_path):
                # Step 2: Create enterprise pyproject.toml
                if self.create_enterprise_pyproject(project_path):
                    # Step 3: Validate
                    if self.validate_project(project_path):
                        self.fixed_projects.append(submodule)

        # Summary

        if self.fixed_projects:
            for _project in self.fixed_projects:
                pass

        if self.errors:
            for _error in self.errors:
                pass

        # Log to token
        with open(self.workspace_root / ".token", "a") as f:
            f.write(
                f"PYPROJECT-ENTERPRISE-STANDARDIZATION: {len(self.fixed_projects)}/{len(self.submodules)} projects standardized\\n",
            )

        if len(self.fixed_projects) == len(self.submodules):
            pass


if __name__ == "__main__":
    workspace_root = Path("/home/marlonsc/pyauto")
    standardizer = PyProjectEnterpriseStandardizer(workspace_root)
    standardizer.standardize_all_projects()
