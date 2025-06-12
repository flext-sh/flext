#!/usr/bin/env python3
"""Validate pyproject.toml files against enterprise standards.

This script checks all pyproject.toml files in the workspace for compliance
with the standards defined in CLAUDE.md.

Usage:
    python scripts/utilities/validate_pyproject.py
    python scripts/utilities/validate_pyproject.py --fix
"""

import argparse
import sys
import tomllib
from pathlib import Path

# Enterprise standards from CLAUDE.md
REQUIRED_BUILD_SYSTEM = {
    "requires": ["poetry-core>=2.1.3"],
    "build-backend": "poetry.core.masonry.api"
}

REQUIRED_PYTHON = "^3.13"
REQUIRED_DEV_DEPS = {
    "pytest": "^8.4.0",
    "pytest-cov": "^6.1.1",
    "mypy": "^1.16.0",
    "ruff": "^0.11.13",
    "black": "^25.1.0",
    "pre-commit": "^4.2.0"
}

TOOL_VERSIONS = {
    "mypy": {"python_version": "3.13"},
    "black": {"target-version": ["py313"]},
    "ruff": {"target-version": "py313"}
}


class PyProjectValidator:
    """Validate pyproject.toml files against enterprise standards."""

    def __init__(self, fix: bool = False):
        self.fix = fix
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate_file(self, file_path: Path) -> bool:
        """Validate a single pyproject.toml file."""
        print(f"\n📋 Validating: {file_path}")

        try:
            with open(file_path, "rb") as f:
                data = tomllib.load(f)
        except Exception as e:
            self.errors.append(f"{file_path}: Failed to parse TOML - {e}")
            return False

        # Check build system
        self._check_build_system(file_path, data)

        # Check package naming
        self._check_package_naming(file_path, data)

        # Check Python version
        self._check_python_version(file_path, data)

        # Check dev dependencies
        self._check_dev_dependencies(file_path, data)

        # Check tool configurations
        self._check_tool_configs(file_path, data)

        # Check coverage requirements
        self._check_coverage_requirements(file_path, data)

        return len(self.errors) == 0

    def _check_build_system(self, file_path: Path, data: dict) -> None:
        """Check build system configuration."""
        build_system = data.get("build-system", {})

        if not build_system:
            self.errors.append(f"{file_path}: Missing [build-system] section")
            return

        requires = build_system.get("requires", [])
        if not any("poetry-core>=2.1.3" in req for req in requires):
            self.errors.append(
                f"{file_path}: Build system must use poetry-core>=2.1.3"
            )

        if build_system.get("build-backend") != "poetry.core.masonry.api":
            self.errors.append(
                f"{file_path}: Build backend must be poetry.core.masonry.api"
            )

    def _check_package_naming(self, file_path: Path, data: dict) -> None:
        """Check package name uses underscores."""
        poetry = data.get("tool", {}).get("poetry", {})
        name = poetry.get("name", "")

        if "-" in name:
            self.errors.append(
                f"{file_path}: Package name '{name}' must use underscores, not hyphens"
            )

        # Check packages configuration
        packages = poetry.get("packages", [])
        for pkg in packages:
            if isinstance(pkg, dict) and "-" in pkg.get("include", ""):
                self.errors.append(
                    f"{file_path}: Package include '{pkg['include']}' must use underscores"
                )

    def _check_python_version(self, file_path: Path, data: dict) -> None:
        """Check Python version requirement."""
        poetry = data.get("tool", {}).get("poetry", {})
        deps = poetry.get("dependencies", {})
        python_version = deps.get("python", "")

        if not python_version.startswith("^3.13"):
            self.errors.append(
                f"{file_path}: Python version must be ^3.13,<3.15 (found: {python_version})"
            )

    def _check_dev_dependencies(self, file_path: Path, data: dict) -> None:
        """Check required dev dependencies."""
        dev_deps = (
            data.get("tool", {})
            .get("poetry", {})
            .get("group", {})
            .get("dev", {})
            .get("dependencies", {})
        )

        if not dev_deps:
            # Try old format
            dev_deps = (
                data.get("tool", {})
                .get("poetry", {})
                .get("dev-dependencies", {})
            )
            if dev_deps:
                self.warnings.append(
                    f"{file_path}: Using deprecated dev-dependencies format"
                )

        for dep, _version in REQUIRED_DEV_DEPS.items():
            if dep not in dev_deps:
                self.errors.append(
                    f"{file_path}: Missing required dev dependency: {dep}"
                )

    def _check_tool_configs(self, file_path: Path, data: dict) -> None:
        """Check tool configurations match Python version."""
        tools = data.get("tool", {})

        # Check mypy
        mypy = tools.get("mypy", {})
        if mypy.get("python_version") != "3.13":
            self.errors.append(
                f"{file_path}: mypy.python_version must be 3.13"
            )

        # Check black
        black = tools.get("black", {})
        target_version = black.get("target-version", [])
        if "py313" not in target_version:
            self.errors.append(
                f"{file_path}: black.target-version must include py313"
            )

        # Check ruff
        ruff = tools.get("ruff", {})
        if ruff.get("target-version") not in {"py313", "py312"}:
            self.warnings.append(
                f"{file_path}: ruff.target-version should be py313"
            )

    def _check_coverage_requirements(self, file_path: Path, data: dict) -> None:
        """Check coverage requirements."""
        pytest_config = data.get("tool", {}).get("pytest.ini_options", {})
        addopts = pytest_config.get("addopts", [])

        has_coverage = any("--cov-fail-under" in opt for opt in addopts)
        if not has_coverage:
            self.warnings.append(
                f"{file_path}: Consider adding --cov-fail-under=90 for coverage requirement"
            )

    def validate_all(self) -> bool:
        """Validate all pyproject.toml files in workspace."""
        root = Path.cwd()
        files = list(root.rglob("pyproject.toml"))

        # Exclude certain directories
        exclude_dirs = {".venv", "venv", "node_modules", ".git", "__pycache__"}
        files = [
            f for f in files
            if not any(ex in f.parts for ex in exclude_dirs)
        ]

        print(f"🔍 Found {len(files)} pyproject.toml files")

        all_valid = True
        for file_path in sorted(files):
            if not self.validate_file(file_path):
                all_valid = False

        return all_valid

    def print_summary(self) -> None:
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)

        if self.errors:
            print(f"\n❌ Found {len(self.errors)} errors:")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  Found {len(self.warnings)} warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All pyproject.toml files are compliant!")

        print("\n" + "=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate pyproject.toml files against enterprise standards"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix issues where possible"
    )
    args = parser.parse_args()

    validator = PyProjectValidator(fix=args.fix)

    if validator.validate_all():
        print("\n✅ All validation checks passed!")
        sys.exit(0)
    else:
        validator.print_summary()
        sys.exit(1)


if __name__ == "__main__":
    main()
