"""CLI validation automation module for PyAuto enterprise workspace.

This module handles automated CLI testing, command validation, help text verification,
and interactive command testing across all CLI-based projects.
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from .base import CustomFixModule, Issue, Severity

console = Console()


class CLIValidationAutomationModule(CustomFixModule):
    """Module for automating CLI validation and testing."""

    name = "cli_validation_automation"
    description = "Automated CLI testing, command validation, and help verification"

    def __init__(
        self,
        dry_run: bool = True,
        interactive: bool = False,
        verbose: bool = False,
    ):
        """Initialize CLI validation automation module.

        Args:
            dry_run: If True, only simulate operations
            interactive: If True, prompt for confirmations
            verbose: If True, show detailed output
        """
        super().__init__(dry_run, interactive, verbose)
        self.cli_commands: dict[str, list[str]] = {}
        self.validation_results: dict[str, dict[str, Any]] = {}
        self.common_issues: list[str] = []

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze CLI-related files for issues.

        Args:
            file_path: Path to file being analyzed
            content: File content

        Returns:
            List of CLI-related issues found
        """
        issues: list = []

        # Check CLI implementation files
        if file_path.name == "cli.py" or file_path.name == "__main__.py":
            issues.extend(self._analyze_cli_file(file_path, content))
        elif file_path.name == "setup.py" and "console_scripts" in content:
            issues.extend(self._analyze_setup_entry_points(file_path, content))
        elif file_path.name == "pyproject.toml" and "[tool.poetry.scripts]" in content:
            issues.extend(self._analyze_pyproject_scripts(file_path, content))
        elif "click" in content or "typer" in content or "argparse" in content:
            issues.extend(self._analyze_cli_usage(file_path, content))

        return issues

    def _analyze_cli_file(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze main CLI file for common issues."""
        issues: list = []
        lines = content.splitlines()

        # Check for proper error handling
        has_error_handling = any("try:" in line for line in lines)
        if not has_error_handling:
            issues.append(
                Issue(
                    severity=Severity.MEDIUM,
                    message="CLI missing error handling",
                    file_path=file_path,
                    line=None,
                    fix_description="Add try/except blocks for error handling",
                ),
            )

        # Check for help documentation
        if "@click.command()" in content or "@app.command()" in content:
            # Check Click/Typer commands for help text
            command_pattern = r"@\w+\.command\(\)"
            help_pattern = r"help\s*="

            commands_found = len(re.findall(command_pattern, content))
            help_found = len(re.findall(help_pattern, content))

            if commands_found > help_found:
                issues.append(
                    Issue(
                        severity=Severity.LOW,
                        message="Some CLI commands missing help text",
                        file_path=file_path,
                        line=None,
                        fix_description="Add help parameter to all commands",
                    ),
                )

        # Check for version command
        if "--version" not in content and "-V" not in content:
            issues.append(
                Issue(
                    severity=Severity.LOW,
                    message="CLI missing version command",
                    file_path=file_path,
                    line=None,
                    fix_description="Add --version flag to show version info",
                ),
            )

        # Check for proper import structure
        if "if __name__ == '__main__':" not in content:
            issues.append(
                Issue(
                    severity=Severity.MEDIUM,
                    message="CLI missing proper entry point guard",
                    file_path=file_path,
                    line=None,
                    fix_description="Add if __name__ == '__main__': guard",
                ),
            )

        # Check for logging setup
        if "logging" not in content and "logger" not in content:
            issues.append(
                Issue(
                    severity=Severity.LOW,
                    message="CLI missing logging configuration",
                    file_path=file_path,
                    line=None,
                    fix_description="Add logging configuration for debugging",
                ),
            )

        return issues

    def _analyze_setup_entry_points(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze setup.py entry points."""
        issues: list = []

        # Extract console_scripts section
        match = re.search(r"console_scripts.*?=.*?\[(.*?)\]", content, re.DOTALL)
        if match:
            scripts_content = match.group(1)
            scripts = re.findall(r'"([^"]+)"', scripts_content)

            for script in scripts:
                if "=" in script:
                    name, entry = script.split("=", 1)
                    name = name.strip()
                    entry = entry.strip()

                    # Check entry point format
                    if not re.match(r"[\w\.]+:[\w]+", entry):
                        issues.append(
                            Issue(
                                severity=Severity.HIGH,
                                message=f"Invalid entry point format: {entry}",
                                file_path=file_path,
                                line=None,
                                fix_description="Use format 'module.path:function'",
                            ),
                        )

                    # Store for validation
                    project_name = file_path.parent.name
                    if project_name not in self.cli_commands:
                        self.cli_commands[project_name] = []
                    self.cli_commands[project_name].append(name)

        return issues

    def _analyze_pyproject_scripts(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze pyproject.toml scripts section."""
        issues: list = []

        # Extract scripts section
        scripts_match = re.search(
            r"\[tool\.poetry\.scripts\](.*?)(?:\[|$)",
            content,
            re.DOTALL,
        )
        if scripts_match:
            scripts_content = scripts_match.group(1)
            scripts = re.findall(r'(\w+)\s*=\s*"([^"]+)"', scripts_content)

            for name, entry in scripts:
                # Check entry point format
                if not re.match(r"[\w\.]+:[\w]+", entry):
                    issues.append(
                        Issue(
                            severity=Severity.HIGH,
                            message=f"Invalid script entry point: {entry}",
                            file_path=file_path,
                            line=None,
                            fix_description="Use format 'module.path:function'",
                        ),
                    )

                # Store for validation
                project_name = file_path.parent.name
                if project_name not in self.cli_commands:
                    self.cli_commands[project_name] = []
                self.cli_commands[project_name].append(name)

        return issues

    def _analyze_cli_usage(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze files using CLI frameworks."""
        issues: list = []

        # Check for common CLI anti-patterns
        if "print(" in content and "cli" in file_path.name.lower():
            # Count print statements
            print_count = content.count("print(")
            if print_count > 10:
                issues.append(
                    Issue(
                        severity=Severity.MEDIUM,
                        message=f"Excessive print statements ({print_count}) in CLI code",
                        file_path=file_path,
                        line=None,
                        fix_description="Use proper logging or Rich console for output",
                    ),
                )

        # Check for sys.exit usage
        if "sys.exit" in content:
            # Check if it's wrapped in proper error handling
            exit_lines = [
                i for i, line in enumerate(content.splitlines()) if "sys.exit" in line
            ]
            for line_num in exit_lines:
                # Simple check for try/except around exit
                lines = content.splitlines()
                in_try_block = False
                for i in range(max(0, line_num - 5), line_num):
                    if "try:" in lines[i]:
                        in_try_block = True
                        break

                if not in_try_block:
                    issues.append(
                        Issue(
                            severity=Severity.LOW,
                            message="sys.exit() without proper error handling",
                            file_path=file_path,
                            line=line_num + 1,
                            fix_description="Wrap sys.exit() in proper error handling",
                        ),
                    )

        # Check for hardcoded values that should be arguments
        hardcoded_patterns = [
            (r"localhost:\d+", "Hardcoded host/port"),
            (r"/home/\w+/", "Hardcoded home directory path"),
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
        ]

        for pattern, message in hardcoded_patterns:
            if re.search(pattern, content):
                issues.append(
                    Issue(
                        severity=Severity.MEDIUM,
                        message=f"{message} in CLI code",
                        file_path=file_path,
                        line=None,
                        fix_description="Make hardcoded values configurable via CLI arguments",
                    ),
                )

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply CLI-related fixes to content.

        Args:
            content: Original file content
            issues: List of issues to fix

        Returns:
            Fixed content
        """
        # Most CLI fixes require manual intervention
        # This could be extended to add basic templates
        return content

    def validate_cli_commands(self, project_path: Path) -> dict[str, Any]:
        """Validate all CLI commands in a project.

        Args:
            project_path: Path to project directory

        Returns:
            Validation results
        """
        results = {
            "project": project_path.name,
            "commands": {},
            "success": True,
            "issues": [],
        }

        # Find all CLI entry points
        cli_commands = self._find_cli_commands(project_path)

        for command in cli_commands:
            command_results = self._validate_single_command(project_path, command)
            results["commands"][command] = command_results
            if not command_results["success"]:
                results["success"] = False
                results["issues"].extend(command_results["issues"])

        self.validation_results[project_path.name] = results
        return results

    def _find_cli_commands(self, project_path: Path) -> list[str]:
        """Find all CLI commands in a project."""
        commands: list = []

        # Check pyproject.toml
        pyproject = project_path / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text()
            if "[tool.poetry.scripts]" in content:
                scripts_match = re.search(
                    r"\[tool\.poetry\.scripts\](.*?)(?:\[|$)",
                    content,
                    re.DOTALL,
                )
                if scripts_match:
                    scripts = re.findall(r"(\w+)\s*=", scripts_match.group(1))
                    commands.extend(scripts)

        # Check setup.py
        setup_py = project_path / "setup.py"
        if setup_py.exists():
            content = setup_py.read_text()
            if "console_scripts" in content:
                match = re.search(
                    r"console_scripts.*?=.*?\[(.*?)\]",
                    content,
                    re.DOTALL,
                )
                if match:
                    scripts = re.findall(r'"([^"=]+)\s*=', match.group(1))
                    commands.extend(scripts)

        # Also check for direct CLI files
        for cli_file in ["cli.py", "__main__.py"]:
            if (project_path / cli_file).exists():
                commands.append(f"python -m {project_path.name}")

        return list(set(commands))  # Remove duplicates

    def _validate_single_command(
        self,
        project_path: Path,
        command: str,
    ) -> dict[str, Any]:
        """Validate a single CLI command."""
        results = {
            "command": command,
            "success": True,
            "issues": [],
            "help_available": False,
            "version_available": False,
            "exit_code": None,
        }

        if self.dry_run:
            console.print(f"[yellow]DRY RUN: Would validate {command}[/yellow]")
            return results

        # Test help command
        help_result = self._test_command(project_path, command, ["--help"])
        if help_result["success"]:
            results["help_available"] = True
            if len(help_result["output"]) < 50:
                results["issues"].append("Help text too short")
            results["success"] = False
            results["issues"].append("Help command failed")

        # Test version command
        version_result = self._test_command(project_path, command, ["--version"])
        if version_result["success"]:
            results["version_available"] = True

        # Test basic invocation
        basic_result = self._test_command(project_path, command, [])
        results["exit_code"] = basic_result["exit_code"]

        if basic_result["exit_code"] not in [
            0,
            1,
            2,
        ]:  # 1 and 2 are common for missing args
            results["success"] = False
            results["issues"].append(
                f"Unexpected exit code: {basic_result['exit_code']}",
            )

        return results

    def _test_command(
        self,
        project_path: Path,
        command: str,
        args: list[str],
    ) -> dict[str, Any]:
        """Test a CLI command with given arguments."""
        result = {"success": False, "exit_code": None, "output": "", "error": ""}

        try:
            # Build command
            if command.startswith("python -m"):
                cmd = [sys.executable] + command.split()[1:] + args
                cmd = [command] + args

            # Run command
            proc = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            result["exit_code"] = proc.returncode
            result["output"] = proc.stdout
            result["error"] = proc.stderr
            result["success"] = proc.returncode in [0, 1, 2]  # Common success codes

        except subprocess.TimeoutExpired:
            result["error"] = "Command timed out"
        except FileNotFoundError:
            result["error"] = f"Command not found: {command}"
        except Exception as e:
            result["error"] = str(e)

        return result

    def generate_cli_tests(self, project_path: Path) -> str:
        """Generate automated CLI tests for a project.

        Args:
            project_path: Path to project directory

        Returns:
            Generated test code
        """
        cli_commands = self._find_cli_commands(project_path)

        test_code = f'''"""Automated CLI tests for {project_path.name}."""

import subprocess
import sys
from pathlib import Path

import pytest


class TestCLI:
    """Test CLI commands for {project_path.name}."""

    @pytest.fixture
    def project_root(self):
        """Get project root directory."""
        return Path(__file__).parent.parent
'''

        for command in cli_commands:
            # Generate test for help
            test_code += f'''

    def test_{command.replace("-", "_")}_help(self, project_root):
        """Test {command} --help command."""
        result = subprocess.run(
            ["{command}", "--help"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        assert result.returncode == 0
        assert len(result.stdout) > 50
        assert "{command}" in result.stdout.lower()
'''

            # Generate test for version
            test_code += f'''

    def test_{command.replace("-", "_")}_version(self, project_root):
        """Test {command} --version command."""
        result = subprocess.run(
            ["{command}", "--version"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        # Version might not be implemented
        if result.returncode == 0:
            assert len(result.stdout) > 0
'''

            # Generate test for error handling
            test_code += f'''

    def test_{command.replace("-", "_")}_invalid_args(self, project_root):
        """Test {command} with invalid arguments."""
        result = subprocess.run(
            ["{command}", "--invalid-argument"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        assert result.returncode != 0
        assert result.stderr or result.stdout  # Should show error message
'''

        return test_code

    def run_interactive_cli_test(self, project_path: Path, command: str) -> None:
        """Run interactive CLI test session.

        Args:
            project_path: Path to project directory
            command: CLI command to test
        """
        console.print(f"\n[bold cyan]Interactive CLI Test: {command}[/bold cyan]")
        console.print(
            "[yellow]Type 'exit' to quit, 'help' for test commands[/yellow]\n",
        )

        while True:
            # Get user input
            user_input = console.input(f"[green]{command}>[/green] ")

            if user_input.lower() == "exit":
                break
            if user_input.lower() == "help":
                self._show_test_help()
                continue

            # Parse and run command
            args = user_input.split()
            result = self._test_command(project_path, command, args)

            # Display results
            if result["output"]:
                console.print("[bold]Output:[/bold]")
                console.print(result["output"])

            if result["error"]:
                console.print("[bold red]Error:[/bold red]")
                console.print(result["error"])

            console.print(f"[dim]Exit code: {result['exit_code']}[/dim]\n")

    def _show_test_help(self) -> None:
        """Show interactive test help."""
        help_text = """
[bold]Interactive CLI Test Commands:[/bold]
  exit          - Exit interactive test
  help          - Show this help
  --help        - Test help command
  --version     - Test version command
  [args...]     - Test with custom arguments

[bold]Common test scenarios:[/bold]
  - Test with no arguments
  - Test with --help flag
  - Test with invalid arguments
  - Test with valid arguments
  - Test error handling
"""
        console.print(help_text)

    def generate_cli_validation_report(self) -> None:
        """Generate CLI validation summary report."""
        table = Table(title="CLI Validation Report")
        table.add_column("Project", style="cyan")
        table.add_column("Commands", style="magenta")
        table.add_column("Help", style="green")
        table.add_column("Version", style="blue")
        table.add_column("Issues", style="red")
        table.add_column("Status", style="yellow")

        for project, results in self.validation_results.items():
            command_count = len(results["commands"])
            help_count = sum(
                1 for cmd in results["commands"].values() if cmd["help_available"]
            )
            version_count = sum(
                1 for cmd in results["commands"].values() if cmd["version_available"]
            )
            issue_count = len(results["issues"])
            status = "✓" if results["success"] else "✗"

            table.add_row(
                project,
                str(command_count),
                f"{help_count}/{command_count}",
                f"{version_count}/{command_count}",
                str(issue_count),
                f"[{'green' if status == '✓' else 'red'}]{status}[/]",
            )

        console.print(table)

        # Show common issues
        if self.common_issues:
            console.print("\n[bold yellow]Common Issues Found:[/bold yellow]")
            for issue in set(self.common_issues):
                console.print(f"  • {issue}")
