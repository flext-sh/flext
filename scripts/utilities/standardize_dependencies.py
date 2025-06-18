#!/usr/bin/env python3
"""PyAuto Monorepo Dependency Standardization
Standardizes dependencies across all projects to resolve conflicts.
"""

import shutil
import tomllib
from pathlib import Path
from typing import Any

import toml


class DependencyStandardizer:
    """Standardizes dependencies across PyAuto monorepo projects."""

    # Standard dependency versions (highest compatible versions)
    STANDARD_VERSIONS = {
        # Core Python
        "python": "^3.13,<3.15",
        # Core framework dependencies
        "pydantic": "^2.11.5",
        "pydantic-settings": "^2.9.1",
        "pydantic-core": "^2.27.0",
        "sqlalchemy": "^2.0.0",
        "fastapi": "^0.115.0",
        "uvicorn": "^0.30.0",
        "httpx": "^0.28.1",
        "anyio": "^4.9.0",
        # Database
        "oracledb": "^2.5.0",
        "alembic": "^1.14.0",
        "aiosqlite": "^0.21.0",
        # Authentication & Security
        "PyJWT": "^2.10.1",
        "cryptography": "^43.0.0",
        "authlib": "^1.3.0",
        # CLI & UI
        "click": "^8.2.1",
        "typer": "^0.9.0",
        "rich": "^14.0.0",
        "cyclopts": "^3.1.0",
        # Data processing
        "pandas": "^2.2.0",
        "pyarrow": "^18.0.0",
        "openpyxl": "^3.1.0",
        "tabulate": "^0.9.0",
        "lxml": "^5.3.0",
        "xmltodict": "^0.13.0",
        # Configuration & environment
        "python-dotenv": "^1.1.0",
        "pyyaml": "^6.0.2",
        "jinja2": "^3.1.0",
        "jsonschema": "^4.24.0",
        # Logging & monitoring
        "loguru": "^0.7.3",
        "structlog": "^25.4.0",
        "python-json-logger": "^3.3.0",
        "opentelemetry-api": "^1.34.0",
        "opentelemetry-sdk": "^1.34.0",
        "opentelemetry-instrumentation": "^0.55b0",
        # Async & concurrency
        "asyncio": "^3.4.3",
        "aiofiles": "^24.1.0",
        "aiohttp": "^3.12.11",
        "dramatiq": "^1.18.0",
        "tenacity": "^9.1.2",
        # Messaging & caching
        "redis": "^6.2.0",
        "paramiko": "^3.3.1",
        # LDAP
        "ldap3": "^2.9.1",
        # Development dependencies
        "pytest": "^8.4.0",
        "pytest-asyncio": "^0.23.5.post1,<0.24.0",
        "pytest-cov": "^6.1.1",
        "pytest-mock": "^3.14.1",
        "pytest-xdist": "^3.7.0",
        "pytest-benchmark": "^4.0.0",
        "pytest-html": "^4.1.1",
        "pytest-timeout": "^2.4.0",
        "coverage": "^7.8.2",
        # Type checking
        "mypy": "^1.16.0",
        "types-requests": "^2.32.0.20241016",
        "types-sqlalchemy": "^1.4.53.38",
        "types-pyyaml": "^6.0.12.20250516",
        "types-redis": "^4.6.0.20240903",
        "types-setuptools": "^75.7.0.20250106",
        "types-python-dateutil": "^2.9.0.20241206",
        # Code formatting & linting
        "black": "^25.1.0",
        "isort": "^6.0.1",
        "ruff": "^0.11.13",
        "bandit": "^1.8.0",
        "vulture": "^2.12",
        "autoflake": "^2.2.1",
        "pyupgrade": "^3.1.0",
        "flake8": "^7.2.0",
        # Additional linting tools
        "pycodestyle": "^2.12.0",
        "pydocstyle": "^6.3.0",
        "pylint": "^3.0.0",
        # Pre-commit and development tools
        "pre-commit": "^4.2.0",
        "setuptools": "^80.9.0",
        "wheel": "^0.42.0",
        # Documentation
        "mkdocs": "^1.6.0",
        "mkdocs-material": "^9.5.0",
        # Jupyter
        "ipykernel": "^6.0.0",
        "ipython": "^8.0.0",
        # Optional dependencies
        "attrs": "^25.3.0",
        "fire": "^0.7.0",
        "pluggy": "^1.6.0",
        "lato": "^0.12.0",
        "twisted": "^25.5.0",
    }

    # Dependencies that should be in dev group only
    DEV_ONLY_DEPS = {
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock",
        "pytest-xdist",
        "pytest-benchmark",
        "pytest-html",
        "pytest-timeout",
        "coverage",
        "mypy",
        "types-requests",
        "types-sqlalchemy",
        "types-pyyaml",
        "types-redis",
        "types-setuptools",
        "types-python-dateutil",
        "black",
        "isort",
        "ruff",
        "bandit",
        "vulture",
        "autoflake",
        "pyupgrade",
        "flake8",
        "pycodestyle",
        "pydocstyle",
        "pylint",
        "pre-commit",
        "setuptools",
        "wheel",
        "mkdocs",
        "mkdocs-material",
        "ipykernel",
        "ipython",
    }

    def __init__(self, root_path: str = ".") -> None:
        self.root_path = Path(root_path)
        self.backup_dir = self.root_path / "pyproject_backups"

    def create_backup(self, pyproject_path: Path) -> None:
        """Create backup of pyproject.toml file."""
        self.backup_dir.mkdir(exist_ok=True)
        backup_name = f"{pyproject_path.parent.name}_pyproject.toml"
        backup_path = self.backup_dir / backup_name
        shutil.copy2(pyproject_path, backup_path)

    def find_pyproject_files(self) -> list[Path]:
        """Find all pyproject.toml files to standardize."""
        target_dirs = [
            "flx",
            "flx-database-oracle",
            "flx-http-oracle-oic",
            "flx-http-oracle-wms",
            "algar-mig-oud",
            "gruponos-poc-oic-wms",
            "flx-adapter-example",
        ]

        pyproject_files = []
        for target_dir in target_dirs:
            pyproject_path = self.root_path / target_dir / "pyproject.toml"
            if pyproject_path.exists():
                pyproject_files.append(pyproject_path)

        return pyproject_files

    def load_pyproject(self, pyproject_path: Path) -> dict[str, Any]:
        """Load pyproject.toml file."""
        with open(pyproject_path, "rb") as f:
            return tomllib.load(f)

    def save_pyproject(self, pyproject_path: Path, data: dict[str, Any]) -> None:
        """Save pyproject.toml file."""
        with open(pyproject_path, "w", encoding="utf-8") as f:
            toml.dump(data, f)

    def standardize_project(self, pyproject_path: Path) -> dict[str, Any]:
        """Standardize dependencies for a single project."""
        # Create backup
        self.create_backup(pyproject_path)

        # Load current data
        data = self.load_pyproject(pyproject_path)
        data.get("tool", {}).get("poetry", {}).get("name", pyproject_path.parent.name)

        changes = {
            "updated_dependencies": [],
            "moved_to_dev": [],
            "standardized_versions": [],
        }

        # Get current dependencies
        poetry_section = data.get("tool", {}).get("poetry", {})
        dependencies = poetry_section.get("dependencies", {})
        dev_deps = (
            poetry_section.setdefault("group", {})
            .setdefault("dev", {})
            .setdefault("dependencies", {})
        )
        # Ensure Python version is standardized
        if "python" in dependencies:
            old_python = dependencies["python"]
            dependencies["python"] = self.STANDARD_VERSIONS["python"]
            if old_python != dependencies["python"]:
                changes["standardized_versions"].append(
                    f"python: {old_python} → {dependencies['python']}",
                )

        # Process all dependencies
        deps_to_move = []
        for dep_name, dep_spec in list(dependencies.items()):
            if dep_name == "python":
                continue

            # Skip local path dependencies
            if isinstance(dep_spec, dict) and "path" in dep_spec:
                continue

            # Check if dependency should be in dev group
            if dep_name in self.DEV_ONLY_DEPS:
                deps_to_move.append(dep_name)
                continue

            # Standardize version if we have a standard for it
            if dep_name in self.STANDARD_VERSIONS:
                old_version = (
                    str(dep_spec)
                    if not isinstance(dep_spec, dict)
                    else str(dep_spec.get("version", dep_spec))
                )
                new_version = self.STANDARD_VERSIONS[dep_name]

                if old_version != new_version:
                    dependencies[dep_name] = new_version
                    changes["standardized_versions"].append(
                        f"{dep_name}: {old_version} → {new_version}",
                    )

        # Move dev-only dependencies to dev group
        for dep_name in deps_to_move:
            dep_spec = dependencies.pop(dep_name)
            dev_deps[dep_name] = self.STANDARD_VERSIONS.get(dep_name, dep_spec)
            changes["moved_to_dev"].append(dep_name)

        # Standardize dev dependencies
        for dep_name, dep_spec in list(dev_deps.items()):
            if dep_name in self.STANDARD_VERSIONS:
                old_version = (
                    str(dep_spec)
                    if not isinstance(dep_spec, dict)
                    else str(dep_spec.get("version", dep_spec))
                )
                new_version = self.STANDARD_VERSIONS[dep_name]

                if old_version != new_version:
                    dev_deps[dep_name] = new_version
                    changes["standardized_versions"].append(
                        f"{dep_name} (dev): {old_version} → {new_version}",
                    )

        # Update build system to latest
        data.setdefault("build-system", {})["requires"] = ["poetry-core>=2.1.3"]

        # Ensure mypy configuration is standardized
        if "mypy" in dev_deps:
            mypy_config = data.setdefault("tool", {}).setdefault("mypy", {})
            mypy_config.update(
                {
                    "python_version": "3.13",
                    "strict": True,
                    "warn_return_any": True,
                    "warn_unused_configs": True,
                    "warn_redundant_casts": True,
                    "warn_unused_ignores": True,
                    "show_error_codes": True,
                    "pretty": True,
                }
            )

        # Ensure ruff configuration is standardized
        if "ruff" in dev_deps:
            ruff_config = data.setdefault("tool", {}).setdefault("ruff", {})
            ruff_config.update(
                {
                    "target-version": "py313",
                    "line-length": 120,  # Standardize to FLX framework standard
                    "src": ["src", "tests"],
                }
            )

        # Ensure black configuration is standardized
        if "black" in dev_deps:
            black_config = data.setdefault("tool", {}).setdefault("black", {})
            black_config.update(
                {
                    "line-length": 88,  # Black default
                    "target-version": ["py313"],
                    "include": "\\.pyi?$",
                }
            )

        # Ensure pytest configuration is standardized
        if "pytest" in dev_deps:
            pytest_config = (
                data.setdefault("tool", {})
                .setdefault("pytest", {})
                .setdefault("ini_options", {})
            )
            pytest_config.update(
                {
                    "testpaths": ["tests"],
                    "python_files": ["test_*.py", "*_test.py"],
                    "python_functions": ["test_*"],
                    "python_classes": ["Test*"],
                    "asyncio_mode": "auto",
                    "addopts": [
                        "--strict-markers",
                        "--strict-config",
                        "--cov-report=term-missing",
                        "--cov-report=html:reports/coverage",
                        "--cov-report=xml",
                        "--junitxml=reports/junit.xml",
                    ],
                    "markers": [
                        "unit: Unit tests",
                        "integration: Integration tests",
                        "e2e: End-to-end tests",
                        "slow: Slow tests",
                    ],
                }
            )

        # Save updated data
        self.save_pyproject(pyproject_path, data)

        # Report changes
        if changes["standardized_versions"]:
            for _change in changes["standardized_versions"][:5]:  # Show first 5
                pass
            if len(changes["standardized_versions"]) > 5:
                pass

        if changes["moved_to_dev"]:
            for _dep in changes["moved_to_dev"]:
                pass

        if not any(changes.values()):
            pass

        return changes

    def generate_dependency_report(self) -> None:
        """Generate report of standardized dependencies."""
        report_path = self.root_path / "dependency_standardization_report.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# PyAuto Dependency Standardization Report\n\n")
            f.write(f"Generated on: {Path().cwd()}\n\n")

            f.write("## Standard Dependency Versions\n\n")
            f.write("| Dependency | Version | Category |\n")
            f.write("|------------|---------|----------|\n")

            categories = {
                "Core Framework": ["pydantic", "sqlalchemy", "fastapi", "httpx"],
                "Database": ["oracledb", "alembic", "aiosqlite"],
                "CLI & UI": ["click", "typer", "rich", "cyclopts"],
                "Testing": ["pytest", "pytest-asyncio", "pytest-cov", "mypy"],
                "Code Quality": ["black", "isort", "ruff", "bandit"],
                "Data Processing": ["pandas", "pyarrow", "openpyxl"],
                "Configuration": ["python-dotenv", "pyyaml", "jinja2"],
            }

            for category, deps in categories.items():
                for dep in deps:
                    if dep in self.STANDARD_VERSIONS:
                        version = self.STANDARD_VERSIONS[dep]
                        dev_marker = " (dev)" if dep in self.DEV_ONLY_DEPS else ""
                        f.write(f"| {dep}{dev_marker} | {version} | {category} |\n")

            f.write("\n## Benefits of Standardization\n\n")
            f.write("- ✅ Eliminates version conflicts between projects\n")
            f.write("- 🔧 Ensures compatibility across the monorepo\n")
            f.write("- 📦 Simplifies dependency management\n")
            f.write("- 🚀 Enables shared tooling and configurations\n")
            f.write("- 🔒 Improves security through consistent updates\n")

            f.write("\n## Local Path Dependencies\n\n")
            f.write("The following projects maintain local path dependencies:\n\n")
            f.write("- `flx-database-oracle` → depends on `flx`\n")
            f.write("- `flx-http-oracle-oic` → depends on `flx`\n")
            f.write("- `flx-http-oracle-wms` → depends on `flx`\n")
            f.write("- `algar-mig-oud` → depends on `flx`\n")
            f.write("- `gruponos-poc-oic-wms` → depends on all FLX adapters\n")

    def run_standardization(self) -> None:
        """Run complete dependency standardization."""
        pyproject_files = self.find_pyproject_files()
        for _file_path in pyproject_files:
            pass

        total_changes = {"standardized_versions": 0, "moved_to_dev": 0}

        for pyproject_path in pyproject_files:
            changes = self.standardize_project(pyproject_path)
            total_changes["standardized_versions"] += len(
                changes["standardized_versions"]
            )
            total_changes["moved_to_dev"] += len(changes["moved_to_dev"])

        self.generate_dependency_report()


def main() -> None:
    """Main standardization function."""
    standardizer = DependencyStandardizer()
    standardizer.run_standardization()


if __name__ == "__main__":
    main()
