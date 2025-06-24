#!/usr/bin/env python3
"""Apply PEP8 standards to all PyAuto projects.

This script:
1. Updates pyproject.toml files with standard PEP8 configuration
2. Runs Black for code formatting
3. Runs isort for import sorting
4. Runs Ruff for linting and auto-fixes
5. Validates the results
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def get_project_dirs() -> list[Path]:
    """Get all project directories with pyproject.toml."""
    root = Path.cwd()
    exclude_dirs = {
        ".venv",
        "venv",
        "__pycache__",
        ".git",
        "dist",
        "build",
        "htmlcov",
        "node_modules",
        "reference",
        "docs",
        "logs",
        "scripts",
        "reports",
        "schemas",
        "temp_workflows",
        "junit",
        "src",
        "tests",
        "data",
        "meltano",
        "singer-sdk",
    }

    projects: list = []
    for item in root.iterdir():
        if item.is_dir() and item.name not in exclude_dirs:
            if (item / "pyproject.toml").exists():
                projects.append(item)

    return sorted(projects)


def update_pyproject_toml(project_path: Path, dry_run: bool = False) -> None:
    """Update project's pyproject.toml with standard PEP8 configuration."""
    pyproject_file = project_path / "pyproject.toml"

    if not pyproject_file.exists():
        print(f"⚠️  No pyproject.toml in {project_path.name}")
        return

    print(f"\n📝 Updating {project_path.name}/pyproject.toml...")

    if dry_run:
        print("  → Would update with standard PEP8 configuration")
        return

    # Read existing content
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

    try:
        with open(pyproject_file, "rb") as f:
            config = tomllib.load(f)
    except Exception as e:
        print(f"  ❌ Error reading pyproject.toml: {e}")
        return

    # Load standard configuration
    standard_file = Path.cwd() / "pyproject.toml.standard"
    if not standard_file.exists():
        print("  ❌ Standard configuration not found")
        return

    try:
        with open(standard_file, "rb") as f:
            standard_config = tomllib.load(f)
    except Exception as e:
        print(f"  ❌ Error reading standard config: {e}")
        return

    # Update with standard tool configurations
    for tool in ["black", "isort", "ruff", "mypy", "pytest", "coverage"]:
        if f"tool.{tool}" in standard_config.get("tool", {}):
            if "tool" not in config:
                config["tool"] = {}
            config["tool"][tool] = standard_config["tool"][tool]

    # Write back using tomlkit for better formatting
    try:
        import tomlkit

        # Read original file to preserve formatting
        with open(pyproject_file, encoding="utf-8") as f:
            doc = tomlkit.parse(f.read())

        # Update tool configurations
        if "tool" not in doc:
            doc["tool"] = {}

        for section in ["black", "isort", "ruff", "mypy", "pytest", "coverage"]:
            if section in standard_config.get("tool", {}):
                doc["tool"][section] = standard_config["tool"][section]

        # Write back
        with open(pyproject_file, "w", encoding="utf-8") as f:
            f.write(tomlkit.dumps(doc))

        print("  ✅ Updated with standard PEP8 configuration")
    except ImportError:
        print("  ⚠️  tomlkit not available, skipping pyproject.toml update")
    except Exception as e:
        print(f"  ❌ Error writing pyproject.toml: {e}")


def run_black(project_path: Path, dry_run: bool = False) -> bool:
    """Run Black formatter on project."""
    print(f"\n⚫ Running Black on {project_path.name}...")

    cmd = ["black", str(project_path)]
    if dry_run:
        cmd.append("--check")
        cmd.append("--diff")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("  ✅ Black formatting complete")
            return True
        print(f"  ⚠️  Black found issues:\n{result.stdout}")
        return False
    except Exception as e:
        print(f"  ❌ Error running Black: {e}")
        return False


def run_isort(project_path: Path, dry_run: bool = False) -> bool:
    """Run isort on project."""
    print(f"\n🔤 Running isort on {project_path.name}...")

    cmd = ["isort", str(project_path)]
    if dry_run:
        cmd.append("--check-only")
        cmd.append("--diff")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("  ✅ Import sorting complete")
            return True
        print(f"  ⚠️  isort found issues:\n{result.stdout}")
        return False
    except Exception as e:
        print(f"  ❌ Error running isort: {e}")
        return False


def run_ruff(project_path: Path, dry_run: bool = False, fix: bool = True) -> bool:
    """Run Ruff linter on project."""
    print(f"\n🦀 Running Ruff on {project_path.name}...")

    cmd = ["ruff", "check", str(project_path)]
    if fix and not dry_run:
        cmd.append("--fix")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("  ✅ Ruff linting complete")
            return True
        print(f"  ⚠️  Ruff found issues:\n{result.stderr or result.stdout}")
        return False
    except Exception as e:
        print(f"  ❌ Error running Ruff: {e}")
        return False


def validate_project(project_path: Path) -> dict:
    """Validate project meets PEP8 standards."""
    print(f"\n✅ Validating {project_path.name}...")

    results = {
        "black": False,
        "isort": False,
        "ruff": False,
        "overall": False,
    }

    # Check Black
    result = subprocess.run(
        ["black", "--check", str(project_path)],
        capture_output=True,
        check=False,
    )
    results["black"] = result.returncode == 0
    print(f"  {'✅' if results['black'] else '❌'} Black check")

    # Check isort
    result = subprocess.run(
        ["isort", "--check-only", str(project_path)],
        capture_output=True,
        check=False,
    )
    results["isort"] = result.returncode == 0
    print(f"  {'✅' if results['isort'] else '❌'} isort check")

    # Check Ruff
    result = subprocess.run(
        ["ruff", "check", str(project_path)],
        capture_output=True,
        check=False,
    )
    results["ruff"] = result.returncode == 0
    print(f"  {'✅' if results['ruff'] else '❌'} Ruff check")

    results["overall"] = all([results["black"], results["isort"], results["ruff"]])
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply PEP8 standards to PyAuto projects"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )
    parser.add_argument("--project", help="Apply to specific project only")
    parser.add_argument("--no-fix", action="store_true", help="Don't auto-fix issues")
    parser.add_argument(
        "--validate-only", action="store_true", help="Only validate, don't modify"
    )

    args = parser.parse_args()

    print("🎯 PyAuto PEP8 Standardization")
    print("==============================")

    # Get projects
    if args.project:
        project_path = Path.cwd() / args.project
        if not project_path.exists():
            print(f"❌ Project {args.project} not found")
            return 1
        projects = [project_path]
        projects = get_project_dirs()

    print(f"\n📦 Found {len(projects)} projects to process:")
    for project in projects:
        print(f"  - {project.name}")

    # Process each project
    all_results: dict = {}

    for project in projects:
        print(f"\n{'=' * 60}")
        print(f"Processing {project.name}")
        print(f"{'=' * 60}")

        if args.validate_only:
            results = validate_project(project)
            all_results[project.name] = results
            continue

        # Update pyproject.toml
        update_pyproject_toml(project, args.dry_run)

        # Run formatters and linters
        run_black(project, args.dry_run)
        run_isort(project, args.dry_run)
        run_ruff(project, args.dry_run, fix=not args.no_fix)

        # Validate
        if not args.dry_run:
            results = validate_project(project)
            all_results[project.name] = results

    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)

    if all_results:
        total_pass = sum(1 for r in all_results.values() if r.get("overall", False))
        print(f"\n✅ Passed: {total_pass}/{len(all_results)}")

        for project, results in all_results.items():
            status = "✅" if results.get("overall", False) else "❌"
            print(f"{status} {project}")

    # Save results
    if not args.dry_run and all_results:
        results_file = Path.cwd() / "reports" / "pep8_results.json"
        results_file.parent.mkdir(exist_ok=True)
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2)
        print(f"\n📄 Results saved to {results_file}")

    return 0 if all(r.get("overall", False) for r in all_results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
