#!/usr/bin/env python
"""
Validate ALL 21 projects install and run correctly.

Following CLAUDE.md RULE 4: Complete Delivery - ABSOLUTE ZERO TOLERANCE
"""

import subprocess
import sys
from pathlib import Path


class InstallationValidator:
    """Validate all projects install and CLIs work."""

    def __init__(self):
        """Initialize validator."""
        self.workspace_root = Path("/home/marlonsc/pyauto")
        self.submodules = [
            "client-a-oud-mig",
            "dbt-ldap",
            "dc-code-analyzer",
            "flx",
            "flx-adapter-example",
            "flx-database-oracle",
            "flx-http-oracle-oic",
            "flx-http-oracle-wms",
            "flx-ldap",
            "flx-meltano-enterprise",
            "flx-oracle-oic",
            "flx-oracle-wms",
            "client-b-poc-oic-wms",
            "ldap-core-shared",
            "oracle-oic-ext",
            "tap-ldap",
            "tap-oracle-oic",
            "tap-oracle-wms",
            "target-ldap",
            "target-oracle-oic",
            "target-oracle-wms"]
        self.results = {}

    def validate_project(self, project_name: str) -> dict:
        """Validate a single project installation and CLI."""
        project_path = self.workspace_root / project_name

        result = {
            "exists": False,
            "poetry_install": False,
            "imports": False,
            "cli_works": False,
            "errors": []
        }

        if not project_path.exists():
            result["errors"].append("Project directory not found")
            return result

        result["exists"] = True

        # 1. Check poetry install
        try:
            install_result = subprocess.run(
                ["poetry", "install", "--no-interaction"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120
            )

            if install_result.returncode == 0:
                result["poetry_install"] = True
                result["errors"].append(
                    f"Poetry install failed: {
                        install_result.stderr}")
        except subprocess.TimeoutExpired:
            result["errors"].append("Poetry install timeout")
        except Exception as e:
            result["errors"].append(f"Poetry install error: {str(e)}")

        # 2. Check if module imports
        if result["poetry_install"]:
            module_name = project_name.replace("-", "_")

            try:
                import_test = subprocess.run(
                    ["poetry", "run", "python", "-c", f"import {module_name}; logger.info('Import successful')"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if import_test.returncode == 0:
                    result["imports"] = True
                    result["errors"].append(
                        f"Import failed: {import_test.stderr}")
            except Exception as e:
                result["errors"].append(f"Import test error: {str(e)}")

        # 3. Check if CLI works
        cli_commands = self._get_cli_command(project_name)

        for cli_cmd in cli_commands:
            try:
                cli_test = subprocess.run(
                    ["poetry", "run"] + cli_cmd,
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                # Success if returns 0 or shows help (exit code 2)
                if cli_test.returncode in [
                        0, 2] or "--help" in cli_test.stdout or "Usage:" in cli_test.stdout:
                    result["cli_works"] = True
                    break
            except Exception:
                continue

        if not result["cli_works"]:
            pass

        return result

    def _get_cli_command(self, project_name: str) -> list:
        """Get CLI commands to test for each project."""
        cli_map = {
            "tap-ldap": [["tap-ldap", "--help"], ["tap-ldap", "--version"]],
            "target-ldap": [["target-ldap", "--help"], ["target-ldap", "--version"]],
            "tap-oracle-oic": [["tap-oracle-oic", "--help"]],
            "tap-oracle-wms": [["tap-oracle-wms", "--help"]],
            "target-oracle-oic": [["target-oracle-oic", "--help"]],
            "target-oracle-wms": [["target-oracle-wms", "--help"]],
            "flx": [["flx", "--help"], ["python", "-m", "flx", "--help"]],
            "dbt-ldap": [["dbt", "--help"]],
            "dc-code-analyzer": [["dc-analyzer", "--help"], ["python", "-m", "dc_code_analyzer"]],
            "client-a-oud-mig": [["client-a-oud-mig", "--help"], ["oud-mig", "--help"]],
        }

        # Default commands
        default_cmds = [
            [project_name, "--help"],
            [project_name.replace("-", "_"), "--help"],
            ["python", "-m", project_name.replace("-", "_"), "--help"]
        ]

        return cli_map.get(project_name, default_cmds)

    def validate_all(self) -> None:
        """Validate all projects."""

        total_success = 0
        total_partial = 0
        total_failed = 0

        for project in self.submodules:
            result = self.validate_project(project)
            self.results[project] = result

            # Categorize result
            if result["poetry_install"] and result["imports"]:
                if result["cli_works"]:
                    total_success += 1
                    status = "✅ FULLY WORKING"
                    total_partial += 1
                    status = "⚠️  PARTIAL (no CLI)"
                total_failed += 1
                status = "❌ FAILED"

            # Log to token
            with open(self.workspace_root / ".token", "a") as f:
                f.write(f"INSTALL-VALIDATION-001 {project}: {status}\n")

        # Print summary

        # Detailed report

        for project, result in self.results.items():
            pass

        # List problems
        if total_failed > 0:
            for project, result in self.results.items():
                if not (result["poetry_install"] and result["imports"]):
                    for _error in result["errors"]:
                        pass

        return total_failed == 0 and total_partial == 0


if __name__ == "__main__":
    validator = InstallationValidator()
    success = validator.validate_all()

    if success:
        sys.exit(0)
        sys.exit(1)
