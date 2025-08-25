#!/usr/bin/env python3
"""FLEXT Workspace Configuration Standardization Script.

This script standardizes configuration across all FLEXT subprojects:
1. Updates line-length to 88 characters (Python community standard)
2. Ensures consistent coverage thresholds (90%)
3. Updates projects to use shared configurations
4. Maintains project-specific settings where appropriate

Usage:
    python scripts/standardize_workspace_configs.py [--dry-run] [--project PROJECT_NAME]
"""

import argparse
import sys
from pathlib import Path

import tomlkit


class FlextConfigStandardizer:
    """Standardizes FLEXT workspace configurations professionally."""

    def __init__(self, workspace_root: Path, *, dry_run: bool = False) -> None:
        self.workspace_root = workspace_root
        self.dry_run = dry_run
        self.changes_made = 0

        # Projects that should maintain special configurations
        self.special_configs = {
            "flext-core": {
                "line_length": 88,  # Upgrade from 79 to modern standard
                "coverage_threshold": 90,  # Increase from 80 for foundation
                "reason": "Foundation library - upgraded to modern standards",
            },
            "flext-quality": {
                "line_length": 88,
                "coverage_threshold": 90,  # Increase from 85
                "reason": "Quality analysis tool - requires high standards",
            },
        }

    def find_subprojects(self) -> list[Path]:
        """Find all FLEXT subprojects with pyproject.toml files."""
        projects = [
            path
            for path in self.workspace_root.iterdir()
            if path.is_dir()
            and path.name.startswith(("flext-", "flexcore", "client-a-", "client-b-"))
            and (path / "pyproject.toml").exists()
        ]

        return sorted(projects)

    def load_pyproject(self, project_path: Path) -> dict[str, object] | None:
        """Load pyproject.toml file safely."""
        pyproject_file = project_path / "pyproject.toml"
        if not pyproject_file.exists():
            return None

        try:
            with Path(pyproject_file).open(encoding="utf-8") as f:
                data = tomlkit.load(f)
                return dict(
                    data,
                )  # Convert to regular dict for better type compatibility
        except (OSError, ValueError, TypeError):
            return None

    def save_pyproject(self, project_path: Path, content: dict[str, object]) -> bool:
        """Save pyproject.toml file safely."""
        if self.dry_run:
            return True

        pyproject_file = project_path / "pyproject.toml"
        try:
            with Path(pyproject_file).open("w", encoding="utf-8") as f:
                tomlkit.dump(content, f)
            return True
        except (OSError, ValueError, TypeError):
            return False

    def standardize_ruff_config(
        self,
        project_name: str,
        config: dict[str, object],
    ) -> bool:
        """Standardize Ruff configuration."""
        changed = False

        if "tool" not in config:
            config["tool"] = {}
        tool_config = config["tool"]
        if not isinstance(tool_config, dict):
            return False

        if "ruff" not in tool_config:
            tool_config["ruff"] = {}
        ruff_config = tool_config["ruff"]
        if not isinstance(ruff_config, dict):
            return False

        # Get target line length for this project
        target_length = self.special_configs.get(project_name, {}).get(
            "line_length",
            88,
        )

        # Update line-length
        if ruff_config.get("line-length") != target_length:
            ruff_config.get("line-length", "unset")
            ruff_config["line-length"] = target_length
            changed = True

        # Ensure extend reference to shared config
        if (
            "extend" not in ruff_config
            or ruff_config["extend"] != "../.ruff-shared.toml"
        ):
            ruff_config["extend"] = "../.ruff-shared.toml"
            changed = True

        # Keep project-specific overrides
        project_specific_ignores = {
            "flext-quality": ["DJ001", "DJ008"],  # Django-specific rules
            "flext-auth": ["S105", "S106"],  # Security rules for auth
        }

        if project_name in project_specific_ignores:
            if "lint" not in ruff_config:
                ruff_config["lint"] = {}
            if "ignore" not in ruff_config["lint"]:
                ruff_config["lint"]["ignore"] = []

            for ignore in project_specific_ignores[project_name]:
                if ignore not in ruff_config["lint"]["ignore"]:
                    ruff_config["lint"]["ignore"].append(ignore)
                    changed = True

        return changed

    def standardize_pytest_config(
        self,
        project_name: str,
        config: dict[str, object],
    ) -> bool:
        """Standardize pytest configuration."""
        changed = False

        if "tool" not in config:
            config["tool"] = {}
        tool_config = config["tool"]
        if not isinstance(tool_config, dict):
            return False

        if "pytest" not in tool_config:
            tool_config["pytest"] = {}
        pytest_section = tool_config["pytest"]
        if not isinstance(pytest_section, dict):
            return False

        if "ini_options" not in pytest_section:
            pytest_section["ini_options"] = {}
        pytest_config = pytest_section["ini_options"]
        if not isinstance(pytest_config, dict):
            return False

        # Get target coverage threshold
        target_coverage = self.special_configs.get(project_name, {}).get(
            "coverage_threshold",
            90,
        )

        # Update coverage threshold in addopts
        if "addopts" in pytest_config:
            addopts = pytest_config["addopts"]
            if isinstance(addopts, list):
                # Find and update --cov-fail-under
                for i, opt in enumerate(addopts):
                    if opt.startswith("--cov-fail-under="):
                        old_threshold = opt.split("=")[1]
                        if int(old_threshold) != target_coverage:
                            addopts[i] = f"--cov-fail-under={target_coverage}"
                            changed = True
                        break
                else:
                    # Add coverage threshold if not present
                    addopts.append(f"--cov-fail-under={target_coverage}")
                    changed = True

        # Add reference to shared pytest config
        # Note: pytest doesn't support extend like ruff, so we document the shared
        # standards
        if "minversion" not in pytest_config or pytest_config["minversion"] != "8.0":
            pytest_config["minversion"] = "8.0"
            changed = True

        return changed

    def standardize_mypy_config(
        self,
        project_name: str,
        config: dict[str, object],
    ) -> bool:
        """Standardize MyPy configuration."""
        changed = False

        if "tool" not in config:
            config["tool"] = {}
        tool_config = config["tool"]
        if not isinstance(tool_config, dict):
            return False

        if "mypy" not in tool_config:
            tool_config["mypy"] = {}
        mypy_config = tool_config["mypy"]
        if not isinstance(mypy_config, dict):
            return False

        # Ensure strict mode is enabled
        if mypy_config.get("strict") is not True:
            mypy_config["strict"] = True
            changed = True

        # Ensure Python 3.13
        if mypy_config.get("python_version") != "3.13":
            mypy_config["python_version"] = "3.13"
            changed = True

        return changed

    def standardize_project(self, project_path: Path) -> bool:
        """Standardize a single project."""
        project_name = project_path.name

        # Load current configuration
        config = self.load_pyproject(project_path)
        if not config:
            return False

        total_changes = 0

        # Standardize each configuration section
        if self.standardize_ruff_config(project_name, config):
            total_changes += 1

        if self.standardize_pytest_config(project_name, config):
            total_changes += 1

        if self.standardize_mypy_config(project_name, config):
            total_changes += 1

        # Save changes
        if total_changes > 0:
            if self.save_pyproject(project_path, config):
                self.changes_made += total_changes
                return True
            return False
        return True

    def run_standardization(self, specific_project: str | None = None) -> bool:
        """Run standardization on all or specific project."""
        if self.dry_run:
            pass

        projects = self.find_subprojects()

        if specific_project:
            projects = [p for p in projects if p.name == specific_project]
            if not projects:
                return False

        success_count = 0
        for project_path in projects:
            if self.standardize_project(project_path):
                success_count += 1

        if not self.dry_run and self.changes_made > 0:
            pass

        return success_count == len(projects)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Standardize FLEXT workspace configurations",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    parser.add_argument("--project", help="Standardize specific project only")

    args = parser.parse_args()

    workspace_root = Path("/home/marlonsc/flext")
    if not workspace_root.exists():
        sys.exit(1)

    standardizer = FlextConfigStandardizer(workspace_root, dry_run=args.dry_run)

    try:
        success = standardizer.run_standardization(args.project)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        sys.exit(1)
    except (OSError, ValueError, TypeError):
        sys.exit(1)


if __name__ == "__main__":
    main()
