"""Workspace management module."""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict

from rich.console import Console

console = Console()


class WorkspaceManager:
    """Unified workspace management."""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.workspace_root = Path(__file__).parent.parent

    def get_comprehensive_status(self) -> dict[str, Any]:
        """Get comprehensive workspace status."""
        return {
            "modules": self._get_modules_status(),
            "quality": self._get_quality_metrics(),
            "infrastructure": self._get_infrastructure_status(),
            "git": self._get_git_status(),
        }

    def _get_modules_status(self) -> dict[str, dict[str, str]]:
        """Get status of all FLEXT modules."""
        modules = {}

        # Core modules
        core_modules = [
            "flext-core", "flext-auth", "flext-api", "flext-grpc",
            "flext-web", "flext-cli", "flext-meltano", "flext-plugin",
            "flext-observability", "flext-ldap", "flext-db-oracle",
            "flext-quality"
        ]

        for module in core_modules:
            module_path = self.workspace_root / module
            if module_path.exists():
                modules[module] = self._get_module_info(module_path)
            else:
                modules[module] = {
                    "status": "❌ Missing",
                    "version": "N/A",
                    "tests": "N/A"
                }

        # Migration projects
        migration_projects = ["algar-oud-mig", "gruponos-meltano-native"]
        for project in migration_projects:
            project_path = self.workspace_root / project
            if project_path.exists():
                modules[project] = self._get_module_info(project_path)

        return modules

    def _get_module_info(self, module_path: Path) -> dict[str, str]:
        """Get information about a specific module."""
        info = {"status": "✅ Active", "version": "N/A", "tests": "N/A"}

        # Check for pyproject.toml
        pyproject = module_path / "pyproject.toml"
        if pyproject.exists():
            try:
                import tomllib
                with open(pyproject, "rb") as f:
                    data = tomllib.load(f)
                    info["version"] = data.get("tool", {}).get("poetry", {}).get("version", "N/A")
            except:
                pass

        # Check for tests
        tests_dir = module_path / "tests"
        if tests_dir.exists():
            test_files = list(tests_dir.glob("test_*.py"))
            info["tests"] = f"{len(test_files)} files"

        return info

    def _get_quality_metrics(self) -> dict[str, float]:
        """Get quality metrics."""
        try:
            # Get ruff violations
            result = subprocess.run(
                ["ruff", "check", "--output-format=json"],
                check=False, cwd=self.workspace_root,
                capture_output=True,
                text=True
            )

            violations_count = 0
            if result.stdout:
                violations = json.loads(result.stdout)
                violations_count = len(violations)

            # Calculate compliance (rough estimate)
            estimated_baseline = 80000
            compliance = max(0, (estimated_baseline - violations_count) / estimated_baseline * 100)

            return {
                "compliance": compliance,
                "coverage": 85.0,  # Placeholder - would need actual coverage data
                "violations": violations_count
            }

        except Exception as e:
            if self.debug:
                console.print(f"🐛 Quality metrics error: {e}", style="red")
            return {"compliance": 0.0, "coverage": 0.0, "violations": 0}

    def _get_infrastructure_status(self) -> dict[str, str]:
        """Get infrastructure status."""
        status = {}

        # Check Docker
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
            status["docker"] = "✅ Available"
        except:
            status["docker"] = "❌ Not available"

        # Check Go
        try:
            subprocess.run(["go", "version"], capture_output=True, check=True)
            status["go"] = "✅ Available"
        except:
            status["go"] = "❌ Not available"

        # Check Python venv
        venv_path = self.workspace_root / ".venv"
        if venv_path.exists():
            status["python_venv"] = "✅ Active"
        else:
            status["python_venv"] = "❌ Missing"

        return status

    def _get_git_status(self) -> dict[str, str]:
        """Get Git repository status."""
        try:
            # Check if we're in a git repo
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=True
            )

            if result.stdout.strip():
                return {"status": "🔄 Changes pending", "files": len(result.stdout.strip().split("\n"))}
            return {"status": "✅ Clean", "files": 0}

        except subprocess.CalledProcessError:
            return {"status": "❌ Not a git repo", "files": 0}
        except Exception as e:
            if self.debug:
                console.print(f"🐛 Git status error: {e}", style="red")
            return {"status": "❓ Unknown", "files": 0}
