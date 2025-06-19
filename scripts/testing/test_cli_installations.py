#!/usr/bin/env python3
"""
Test CLI installations for PYAUTO projects.

This script creates isolated virtual environments for each project,
installs them, and tests their CLI functionality.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

# Main PYAUTO projects to test
PROJECTS_TO_TEST = [
    "flx",
    "flx-database-oracle",
    "flx-http-oracle-oic",
    "flx-http-oracle-wms",
    "tap-oracle-wms",
    "tap-oracle-oic",
    "target-oracle-oic",
    "target-oracle-wms",
    "tap-ldap",
    "target-ldap",
    "flx-ldap",
    "flx-oracle-wms",
    "flx-oracle-oic",
]


def run_command(
    cmd: list[str], cwd: Path | None = None, capture_output: bool = True
) -> tuple[int, str, str]:
    """Execute a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            timeout=300,  # 5 minutes timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out after 5 minutes"
    except Exception as e:
        return -1, "", str(e)


def get_project_info(project_path: Path) -> dict[str, Any]:
    """Get project information from pyproject.toml."""
    pyproject_file = project_path / "pyproject.toml"
    if not pyproject_file.exists():
        return {"has_pyproject": False}

    try:
        import tomli

        with open(pyproject_file, "rb") as f:
            data = tomli.load(f)

        return {
            "has_pyproject": True,
            "name": data.get("project", {}).get("name", project_path.name),
            "scripts": data.get("project", {}).get("scripts", {}),
            "entry_points": data.get("project", {}).get("entry-points", {}),
            "tool_poetry_scripts": data.get("tool", {})
            .get("poetry", {})
            .get("scripts", {}),
        }

    except Exception as e:
        return {"has_pyproject": True, "error": str(e)}


def create_test_venv(project_name: str, base_dir: Path) -> Path:
    """Create a virtual environment for testing."""
    venv_path = base_dir / f"test_venv_{project_name.replace('-', '_')}"

    if venv_path.exists():
        shutil.rmtree(venv_path)

    # Create venv
    returncode, stdout, stderr = run_command(
        [sys.executable, "-m", "venv", str(venv_path)]
    )

    if returncode != 0:
        raise RuntimeError(f"Failed to create venv: {stderr}")

    return venv_path


def install_project(project_path: Path, venv_path: Path) -> tuple[bool, str]:
    """Install project in the virtual environment."""
    python_exe = venv_path / "bin" / "python"
    if not python_exe.exists():
        python_exe = venv_path / "Scripts" / "python.exe"  # Windows

    # Upgrade pip first
    returncode, stdout, stderr = run_command(
        [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"]
    )

    if returncode != 0:
        return False, f"Failed to upgrade pip: {stderr}"

    # Install project in editable mode
    returncode, stdout, stderr = run_command(
        [str(python_exe), "-m", "pip", "install", "-e", str(project_path)]
    )

    if returncode == 0:
        return True, "Installation successful"
    return False, f"Installation failed: {stderr}"


def test_cli_commands(project_info: dict, venv_path: Path) -> dict[str, Any]:
    """Test CLI commands for the project."""
    python_exe = venv_path / "bin" / "python"
    if not python_exe.exists():
        python_exe = venv_path / "Scripts" / "python.exe"  # Windows

    results = {}

    # Test script entries
    scripts = project_info.get("scripts", {})
    for script_name, script_entry in scripts.items():
        returncode, stdout, stderr = run_command(
            [str(python_exe), "-m", script_entry.split(".")[0], "--help"]
        )

        results[f"script_{script_name}"] = {
            "command": f"{script_entry} --help",
            "success": returncode == 0,
            "stdout": stdout[:500],  # Limit output
            "stderr": stderr[:500],
        }

    # Test poetry scripts
    poetry_scripts = project_info.get("tool_poetry_scripts", {})
    for script_name, script_entry in poetry_scripts.items():
        returncode, stdout, stderr = run_command(
            [str(venv_path / "bin" / script_name), "--help"]
        )

        results[f"poetry_script_{script_name}"] = {
            "command": f"{script_name} --help",
            "success": returncode == 0,
            "stdout": stdout[:500],
            "stderr": stderr[:500],
        }

    # Test direct module execution for known CLI patterns
    project_name = project_info.get("name", "").replace("-", "_")
    if project_name:
        # Try common CLI patterns
        cli_patterns = [
            f"{project_name}.cli",
            f"{project_name}.main",
            f"{project_name}",
        ]

        for pattern in cli_patterns:
            returncode, stdout, stderr = run_command(
                [str(python_exe), "-m", pattern, "--help"]
            )

            if returncode == 0:
                results[f"module_{pattern}"] = {
                    "command": f"python -m {pattern} --help",
                    "success": True,
                    "stdout": stdout[:500],
                    "stderr": stderr[:500],
                }
                break

    return results


def test_project(
    project_name: str, workspace_root: Path, temp_dir: Path
) -> dict[str, Any]:
    """Test a single project installation and CLI."""
    print(f"\n🔍 Testing project: {project_name}")

    project_path = workspace_root / project_name
    if not project_path.exists():
        return {
            "project": project_name,
            "exists": False,
            "error": "Project directory not found",
        }

    # Get project info
    project_info = get_project_info(project_path)
    if not project_info.get("has_pyproject"):
        return {
            "project": project_name,
            "has_pyproject": False,
            "error": "No pyproject.toml found",
        }

    try:
        # Create test environment
        print("  📦 Creating virtual environment...")
        venv_path = create_test_venv(project_name, temp_dir)

        # Install project
        print("  🔧 Installing project...")
        install_success, install_message = install_project(project_path, venv_path)

        result = {
            "project": project_name,
            "exists": True,
            "has_pyproject": True,
            "project_info": project_info,
            "installation": {"success": install_success, "message": install_message},
            "cli_tests": {},
        }

        if install_success:
            print("  🧪 Testing CLI commands...")
            cli_results = test_cli_commands(project_info, venv_path)
            result["cli_tests"] = cli_results

            # Summary
            working_clis = sum(1 for r in cli_results.values() if r.get("success"))
            total_clis = len(cli_results)
            print(f"  ✅ CLI tests: {working_clis}/{total_clis} working")
        else:
            print(f"  ❌ Installation failed: {install_message}")

        return result

    except Exception as e:
        return {"project": project_name, "exists": True, "error": str(e)}


def generate_report(results: list[dict]) -> None:
    """Generate comprehensive test report."""
    print("\n" + "=" * 80)
    print("🎯 PYAUTO CLI INSTALLATION TEST REPORT")
    print("=" * 80)

    # Summary statistics
    total_projects = len(results)
    successful_installs = sum(
        1 for r in results if r.get("installation", {}).get("success")
    )
    projects_with_clis = sum(1 for r in results if r.get("cli_tests"))
    working_clis = sum(
        sum(1 for cli in r.get("cli_tests", {}).values() if cli.get("success"))
        for r in results
    )
    total_clis = sum(len(r.get("cli_tests", {})) for r in results)

    print("\n📊 SUMMARY:")
    print(f"   Total projects tested: {total_projects}")
    print(f"   Successful installations: {successful_installs}")
    print(f"   Projects with CLIs: {projects_with_clis}")
    print(f"   Working CLI commands: {working_clis}/{total_clis}")
    print(
        f"   Installation success rate: {(successful_installs / total_projects) * 100:.1f}%"
    )
    if total_clis > 0:
        print(f"   CLI success rate: {(working_clis / total_clis) * 100:.1f}%")

    # Detailed results
    print("\n📋 DETAILED RESULTS:")
    print(f"{'Project':<25} {'Install':<10} {'CLIs':<8} {'Status'}")
    print("-" * 60)

    for result in results:
        project = result["project"]
        install_status = "✅" if result.get("installation", {}).get("success") else "❌"
        cli_count = len(result.get("cli_tests", {}))
        working_cli_count = sum(
            1 for cli in result.get("cli_tests", {}).values() if cli.get("success")
        )
        cli_status = f"{working_cli_count}/{cli_count}" if cli_count > 0 else "N/A"

        status = "OK" if result.get("installation", {}).get("success") else "FAILED"
        if "error" in result:
            status = "ERROR"

        print(f"{project:<25} {install_status:<10} {cli_status:<8} {status}")

    # Failed installations
    failed_projects = [
        r for r in results if not r.get("installation", {}).get("success")
    ]
    if failed_projects:
        print("\n❌ FAILED INSTALLATIONS:")
        for result in failed_projects:
            project = result["project"]
            error = result.get("installation", {}).get(
                "message", result.get("error", "Unknown error")
            )
            print(f"   {project}: {error}")

    # CLI details for successful installations
    successful_projects = [
        r for r in results if r.get("installation", {}).get("success")
    ]
    if successful_projects:
        print("\n🔧 CLI COMMAND DETAILS:")
        for result in successful_projects:
            project = result["project"]
            cli_tests = result.get("cli_tests", {})
            if cli_tests:
                print(f"\n   {project}:")
                for cli_name, cli_result in cli_tests.items():
                    status = "✅" if cli_result.get("success") else "❌"
                    command = cli_result.get("command", "")
                    print(f"     {status} {cli_name}: {command}")


def main() -> None:
    """Main test execution."""
    print("🚀 Starting PYAUTO CLI Installation Tests")
    print("=" * 50)

    workspace_root = Path.cwd()

    # Install tomli if needed
    try:
        import tomli
    except ImportError:
        print("📦 Installing tomli for TOML parsing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "tomli"], check=True)

    # Create temporary directory for test environments
    with tempfile.TemporaryDirectory(prefix="pyauto_cli_test_") as temp_dir:
        temp_path = Path(temp_dir)
        print(f"🗂️  Using temp directory: {temp_path}")

        results = []

        for project_name in PROJECTS_TO_TEST:
            try:
                result = test_project(project_name, workspace_root, temp_path)
                results.append(result)
            except KeyboardInterrupt:
                print("\n⚠️  Test interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error testing {project_name}: {e}")
                results.append({"project": project_name, "error": str(e)})

        # Generate report
        generate_report(results)

        # Save detailed results
        results_file = workspace_root / "CLI_INSTALLATION_TEST_RESULTS.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n💾 Detailed results saved to: {results_file}")


if __name__ == "__main__":
    main()
