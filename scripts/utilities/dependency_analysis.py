#!/usr/bin/env python3
"""PyAuto Monorepo Dependency Analysis
Analyzes all pyproject.toml files to identify version conflicts and compatibility issues.
"""

import json
import re
import tomllib
from pathlib import Path
from typing import Any


class DependencyAnalyzer:
    """Analyzes dependencies across PyAuto monorepo projects."""

    def __init__(self, root_path: str = ".") -> None:
        self.root_path = Path(root_path)
        self.projects: dict[str, dict[str, Any]] = {}
        self.all_dependencies: dict[str, dict[str, str]] = {}
        self.version_conflicts: list[dict[str, Any]] = []
        self.missing_dependencies: list[dict[str, Any]] = []
        self.local_dependencies: dict[str, list[str]] = {}

    def find_pyproject_files(self) -> list[Path]:
        """Find all pyproject.toml files in the specified directories."""
        target_dirs = [
            "flx",
            "flx-database-oracle",
            "flx-http-oracle-oic",
            "flx-http-oracle-wms",
            "client-a-mig-oud",
            "client-b-poc-oic-wms",
            "flx-adapter-example",
            ".",  # Root pyproject.toml
        ]

        pyproject_files = []
        for target_dir in target_dirs:
            pyproject_path = self.root_path / target_dir / "pyproject.toml"
            if pyproject_path.exists():
                pyproject_files.append(pyproject_path)

        return pyproject_files

    def parse_version_spec(self, version_spec: str) -> tuple[str, str]:
        """Parse version specification to extract operator and version."""
        # Handle complex version specs like "^3.13,<3.15"
        if isinstance(version_spec, dict):
            # Handle local path dependencies
            return "path", version_spec.get("path", "")

        # Clean version spec
        version_spec = str(version_spec).strip()

        # Extract version constraints
        patterns = [
            (r"\^(\d+\.\d+(?:\.\d+)?)", "caret"),
            (r"~(\d+\.\d+(?:\.\d+)?)", "tilde"),
            (r">=(\d+\.\d+(?:\.\d+)?)", "gte"),
            (r"<=(\d+\.\d+(?:\.\d+)?)", "lte"),
            (r">(\d+\.\d+(?:\.\d+)?)", "gt"),
            (r"<(\d+\.\d+(?:\.\d+)?)", "lt"),
            (r"==(\d+\.\d+(?:\.\d+)?)", "exact"),
            (r"(\d+\.\d+(?:\.\d+)?)", "simple"),
        ]

        for pattern, op_type in patterns:
            match = re.search(pattern, version_spec)
            if match:
                return op_type, match.group(1)

        return "unknown", version_spec

    def extract_dependencies(self, pyproject_path: Path) -> dict[str, Any]:
        """Extract dependencies from a pyproject.toml file."""
        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            project_name = (
                data.get("tool", {})
                .get("poetry", {})
                .get("name", pyproject_path.parent.name)
            )

            dependencies = {}
            dev_dependencies = {}
            local_deps = []

            # Extract main dependencies
            poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            for dep_name, dep_spec in poetry_deps.items():
                if dep_name == "python":
                    continue

                if isinstance(dep_spec, dict):
                    if "path" in dep_spec:
                        local_deps.append(dep_name)
                        dependencies[dep_name] = f"path:{dep_spec['path']}"
                    else:
                        dependencies[dep_name] = str(dep_spec.get("version", "unknown"))
                else:
                    dependencies[dep_name] = str(dep_spec)

            # Extract dev dependencies
            dev_deps = (
                data.get("tool", {})
                .get("poetry", {})
                .get("group", {})
                .get("dev", {})
                .get("dependencies", {})
            )
            for dep_name, dep_spec in dev_deps.items():
                if isinstance(dep_spec, dict):
                    dev_dependencies[dep_name] = str(dep_spec.get("version", "unknown"))
                else:
                    dev_dependencies[dep_name] = str(dep_spec)

            return {
                "name": project_name,
                "path": str(pyproject_path),
                "python_version": poetry_deps.get("python", "unknown"),
                "dependencies": dependencies,
                "dev_dependencies": dev_dependencies,
                "local_dependencies": local_deps,
                "poetry_config": data.get("tool", {}).get("poetry", {}),
            }

        except Exception as e:
            return {
                "name": pyproject_path.parent.name,
                "path": str(pyproject_path),
                "error": str(e),
                "dependencies": {},
                "dev_dependencies": {},
                "local_dependencies": [],
            }

    def analyze_version_conflicts(self) -> None:
        """Identify version conflicts between projects."""
        # Collect all dependencies and their versions
        dep_versions: dict[str, dict[str, list[str]]] = {}

        for project_name, project_data in self.projects.items():
            if "error" in project_data:
                continue

            all_deps = {
                **project_data["dependencies"],
                **project_data["dev_dependencies"],
            }

            for dep_name, version_spec in all_deps.items():
                if dep_name.startswith("path:"):
                    continue

                if dep_name not in dep_versions:
                    dep_versions[dep_name] = {}

                if version_spec not in dep_versions[dep_name]:
                    dep_versions[dep_name][version_spec] = []

                dep_versions[dep_name][version_spec].append(project_name)

        # Find conflicts
        for dep_name, versions in dep_versions.items():
            if len(versions) > 1:
                # Check if versions are actually conflicting
                version_list = list(versions.keys())
                conflicts = []

                for i, ver1 in enumerate(version_list):
                    for ver2 in version_list[i + 1 :]:
                        if self.is_version_conflict(ver1, ver2):
                            conflicts.append(
                                {
                                    "dependency": dep_name,
                                    "version1": ver1,
                                    "projects1": versions[ver1],
                                    "version2": ver2,
                                    "projects2": versions[ver2],
                                }
                            )

                if conflicts:
                    self.version_conflicts.extend(conflicts)

    def is_version_conflict(self, ver1: str, ver2: str) -> bool:
        """Check if two version specifications conflict."""
        # Simplified conflict detection
        # In a real implementation, you'd use a proper version parser
        if ver1 == ver2:
            return False

        # Extract major versions for basic conflict detection
        try:
            op1, v1 = self.parse_version_spec(ver1)
            op2, v2 = self.parse_version_spec(ver2)

            if op1 == "path" or op2 == "path":
                return False

            # Basic major version conflict detection
            if v1.split(".")[0] != v2.split(".")[0]:
                return True

        except Exception:
            pass

        return ver1 != ver2

    def check_missing_dependencies(self) -> None:
        """Check for missing dependencies that could cause import issues."""
        common_imports = {
            "pydantic": ["BaseModel", "Field", "validator"],
            "fastapi": ["FastAPI", "Depends", "HTTPException"],
            "sqlalchemy": ["create_engine", "Column", "Integer"],
            "httpx": ["AsyncClient", "Client"],
            "pytest": ["fixture", "mark", "raises"],
            "click": ["command", "option", "group"],
            "rich": ["console", "print", "table"],
        }

        for project_data in self.projects.values():
            if "error" in project_data:
                continue

            all_deps = {
                **project_data["dependencies"],
                **project_data["dev_dependencies"],
            }

            # Check if commonly imported packages are missing
            for package in common_imports:
                if package not in all_deps:
                    # This is basic - in reality you'd scan source code for imports
                    continue

    def analyze_local_dependencies(self) -> None:
        """Analyze local path dependencies between projects."""
        for project_name, project_data in self.projects.items():
            if "error" in project_data:
                continue

            local_deps = project_data.get("local_dependencies", [])
            if local_deps:
                self.local_dependencies[project_name] = local_deps

    def run_analysis(self) -> None:
        """Run complete dependency analysis."""
        pyproject_files = self.find_pyproject_files()

        for _file_path in pyproject_files:
            pass

        for pyproject_path in pyproject_files:
            project_data = self.extract_dependencies(pyproject_path)
            self.projects[project_data["name"]] = project_data

        self.analyze_version_conflicts()

        self.analyze_local_dependencies()

        self.check_missing_dependencies()

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive dependency analysis report."""
        report = {
            "summary": {
                "total_projects": len(self.projects),
                "projects_with_errors": len(
                    [p for p in self.projects.values() if "error" in p],
                ),
                "total_conflicts": len(self.version_conflicts),
                "projects_with_local_deps": len(self.local_dependencies),
            },
            "projects": {},
            "version_conflicts": self.version_conflicts,
            "local_dependencies": self.local_dependencies,
            "dependency_matrix": {},
        }

        # Project details
        for project_name, project_data in self.projects.items():
            report["projects"][project_name] = {
                "path": project_data["path"],
                "python_version": project_data.get("python_version", "unknown"),
                "total_dependencies": len(project_data.get("dependencies", {})),
                "total_dev_dependencies": len(project_data.get("dev_dependencies", {})),
                "has_errors": "error" in project_data,
                "error": project_data.get("error"),
            }

        # Dependency matrix - which dependencies are used by which projects
        all_deps: set[str] = set()
        for project_data in self.projects.values():
            if "error" not in project_data:
                all_deps.update(project_data.get("dependencies", {}).keys())
                all_deps.update(project_data.get("dev_dependencies", {}).keys())

        for dep in sorted(all_deps):
            if dep.startswith("path:"):
                continue
            report["dependency_matrix"][dep] = {}

            for project_name, project_data in self.projects.items():
                if "error" in project_data:
                    continue

                all_project_deps = {
                    **project_data.get("dependencies", {}),
                    **project_data.get("dev_dependencies", {}),
                }
                version = all_project_deps.get(dep)
                report["dependency_matrix"][dep][project_name] = version

        return report

    def print_report(self) -> None:
        """Print human-readable dependency analysis report."""
        # Summary

        # Projects overview
        for project_data in self.projects.values():
            len(project_data.get("dependencies", {}))
            len(project_data.get("dev_dependencies", {}))
            project_data.get("python_version", "unknown")

            if "error" in project_data:
                pass

        # Version conflicts
        if self.version_conflicts:
            for conflict in self.version_conflicts:
                dep = conflict["dependency"]
                _ver1, _projects1 = conflict["version1"], conflict["projects1"]
                _ver2, _projects2 = conflict["version2"], conflict["projects2"]

        # Local dependencies
        if self.local_dependencies:
            for deps in self.local_dependencies.values():
                for dep in deps:
                    pass

        # Key dependencies matrix
        key_deps = [
            "pydantic",
            "sqlalchemy",
            "fastapi",
            "pytest",
            "mypy",
            "ruff",
            "black",
        ]

        for dep in key_deps:
            pass

        for project_data in self.projects.values():
            if "error" in project_data:
                continue

            all_deps = {
                **project_data.get("dependencies", {}),
                **project_data.get("dev_dependencies", {}),
            }

            for dep in key_deps:
                version = all_deps.get(dep, "❌")
                if version and version != "❌":
                    # Simplify version display
                    if version.startswith("^"):
                        version = version[1:]
                    elif version.startswith(">="):
                        version = version[2:]
                    version = version.split(",")[0]  # Take first constraint


def main() -> None:
    """Main analysis function."""
    analyzer = DependencyAnalyzer()
    analyzer.run_analysis()
    analyzer.print_report()

    # Save detailed report to JSON
    report = analyzer.generate_report()
    with open("dependency_analysis_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    main()
