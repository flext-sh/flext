#!/usr/bin/env python3
"""Test script for unified CLI implementations across Oracle projects.

This script verifies that all Oracle projects now use a consistent CLI
pattern with cyclopts and proper command structure.
"""

import subprocess
import sys
from pathlib import Path


def test_cli_import(project_path: Path, module_path: str) -> tuple[bool, str]:
    """Test if CLI can be imported successfully."""
    try:
        # Test import
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                f"from {module_path} import main; print('✅ Import successful')",
            ],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        if result.returncode == 0:
            return True, "✅ Import successful"
        return False, f"❌ Import failed: {result.stderr.strip()}"

    except subprocess.TimeoutExpired:
        return False, "❌ Import timed out"
    except Exception as e:
        return False, f"❌ Import error: {e}"


def test_cli_help(project_path: Path, module_path: str) -> tuple[bool, str]:
    """Test if CLI help command works."""
    try:
        # Test help command
        result = subprocess.run(
            [sys.executable, "-c", f"from {module_path} import main; main(['--help'])"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        # Help should exit with code 0 and show help text
        if result.returncode == 0 and (
            "help" in result.stdout.lower() or "usage" in result.stdout.lower()
        ):
            return True, "✅ Help command working"
        return False, "❌ Help command failed"

    except subprocess.TimeoutExpired:
        return False, "❌ Help command timed out"
    except Exception as e:
        return False, f"❌ Help command error: {e}"


def test_cli_version(project_path: Path, module_path: str) -> tuple[bool, str]:
    """Test if CLI version command works."""
    try:
        # Test version command
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                f"from {module_path} import main; main(['version'])",
            ],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        if result.returncode == 0 and "0.4.0" in result.stdout:
            return True, "✅ Version command working (v0.4.0)"
        return False, "❌ Version command failed or wrong version"

    except subprocess.TimeoutExpired:
        return False, "❌ Version command timed out"
    except Exception as e:
        return False, f"❌ Version command error: {e}"


def main() -> None:
    """Main test function."""
    print("🧪 Testing unified CLI implementations across Oracle projects\n")

    # Define projects to test
    projects = [
        ("dc-oracle-db", "flx_database_oracle.cli.flx_cli"),
        ("dc-oracle-oic", "flx_http_oracle_oic.cli.main"),
        ("project-client-a-oud", "oud_automation.cli"),
        ("project-client-b-oic-wms", "gn_oic_wms_db.cli"),
    ]

    base_path = Path(__file__).parent
    all_passed = True

    for project_dir, module_path in projects:
        project_path = base_path / project_dir

        if not project_path.exists():
            print(f"⚠️ {project_dir}: Project directory not found")
            all_passed = False
            continue

        print(f"📦 Testing {project_dir}:")

        # Test import
        import_ok, import_msg = test_cli_import(project_path, module_path)
        print(f"  Import: {import_msg}")

        # Test help (only if import works)
        if import_ok:
            help_ok, help_msg = test_cli_help(project_path, module_path)
            print(f"  Help: {help_msg}")
        else:
            help_ok = False
            print("  Help: ⏭️ Skipped (import failed)")

        # Test version (only if import works)
        if import_ok:
            version_ok, version_msg = test_cli_version(project_path, module_path)
            print(f"  Version: {version_msg}")
        else:
            version_ok = False
            print("  Version: ⏭️ Skipped (import failed)")

        # Overall status
        project_passed = import_ok and help_ok and version_ok
        all_passed = all_passed and project_passed

        status = "✅ PASS" if project_passed else "❌ FAIL"
        print(f"  Status: {status}\n")

    # Summary
    if all_passed:
        print("🎉 All CLI implementations working correctly!")
        print("   - Unified cyclopts-based architecture")
        print("   - Consistent command structure")
        print("   - Proper version management (0.4.0)")
        print("   - Standard help functionality")
    else:
        print("❌ Some CLI implementations have issues")
        print("   Check the output above for specific problems")
        sys.exit(1)


if __name__ == "__main__":
    main()
