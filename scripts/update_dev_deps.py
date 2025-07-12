#!/usr/bin/env python3
"""
Script para padronizar dependências de desenvolvimento em todos os projetos FLEXT
"""

import re
from pathlib import Path

STANDARD_DEV_DEPS = {
    # Testing - Maximum strictness
    "pytest": "^8.4.0",
    "pytest-cov": "^6.2.0",
    "pytest-asyncio": "^0.24.0",
    "pytest-benchmark": "^4.0.0",
    "pytest-mock": "^3.14.0",
    "pytest-xdist": "^3.8.0",
    "pytest-timeout": "^2.4.0",
    "pytest-randomly": "^3.16.0",
    "pytest-sugar": "^1.0.0",
    "pytest-clarity": "^1.0.1",
    # Code quality - Latest versions
    "ruff": "^0.12.2",
    "mypy": "^1.16.1",
    "black": "^25.1.0",
    "isort": "^6.0.1",
    "bandit": '{extras = ["toml"], version = "^1.8.0"}',
    "pre-commit": "^4.2.0",
    "vulture": "^2.14",
    "radon": "^6.0.1",
    # Type stubs - Latest versions
    "types-requests": "^2.32.4",
    "types-setuptools": "^75.8.2",
    "types-pyyaml": "^6.0.12",
    "types-python-dateutil": "^2.9.0",
    # Documentation - Latest versions
    "mkdocs": "^1.6.1",
    "mkdocs-material": "^9.6.15",
    "sphinx": "^8.2.3",
    "sphinx-rtd-theme": "^3.0.2",
    "myst-parser": "^4.0.1",
    # Development tools - Latest versions
    "ipython": "^8.37.0",
    # Build & packaging
    "build": "^1.2.2",
    "twine": "^6.1.0",
    # Security
    "safety": "^3.2.0",
}

PROJECTS_TO_UPDATE = [
    "flext-api",
    "flext-auth",
    "flext-grpc",
    "flext-cli",
    "flext-meltano",
    "flext-observability",
    "flext-web",
    "flext-ldap",
    "flext-db-oracle",
    "flext-plugin",
    "flext-tap-ldap",
    "flext-tap-oracle-oic",
    "flext-tap-oracle-wms",
    "flext-target-ldap",
    "flext-target-oracle",
    "flext-target-oracle-oic",
    "flext-dbt-ldap",
    "flext-oracle-oic-ext",
    "flext-quality",
]


def update_project_deps(project_path: Path) -> bool:
    """Update dev dependencies for a single project"""
    pyproject_path = project_path / "pyproject.toml"

    if not pyproject_path.exists():
        print(f"❌ {project_path.name}: pyproject.toml not found")
        return False

    content = pyproject_path.read_text()

    # Find [tool.poetry.group.dev.dependencies] section
    dev_deps_pattern = (
        r"\[tool\.poetry\.group\.dev\.dependencies\](.*?)(?=\n\[|\n\n|\Z)"
    )
    match = re.search(dev_deps_pattern, content, re.DOTALL)

    if not match:
        print(f"❌ {project_path.name}: No dev dependencies section found")
        return False

    # Update individual dependencies
    updated_content = content
    updated_count = 0

    for dep, version in STANDARD_DEV_DEPS.items():
        # Pattern to match dependency line
        dep_pattern = rf"^{re.escape(dep)}\s*=.*$"
        new_line = f"{dep} = {version}"

        if re.search(dep_pattern, content, re.MULTILINE):
            updated_content = re.sub(
                dep_pattern, new_line, updated_content, flags=re.MULTILINE,
            )
            updated_count += 1

    if updated_count > 0:
        pyproject_path.write_text(updated_content)
        print(f"✅ {project_path.name}: Updated {updated_count} dependencies")
        return True
    print(f"⚠️ {project_path.name}: No dependencies to update")
    return False


def main() -> None:
    flext_root = Path("/home/marlonsc/flext")

    print("=== FLEXT DEV DEPENDENCIES STANDARDIZATION ===")

    updated_projects = []
    failed_projects = []

    for project_name in PROJECTS_TO_UPDATE:
        project_path = flext_root / project_name

        if not project_path.exists():
            print(f"❌ {project_name}: Directory not found")
            failed_projects.append(project_name)
            continue

        if update_project_deps(project_path):
            updated_projects.append(project_name)
        else:
            failed_projects.append(project_name)

    print("\n=== SUMMARY ===")
    print(f"✅ Updated: {len(updated_projects)} projects")
    print(f"❌ Failed: {len(failed_projects)} projects")

    if updated_projects:
        print(f"\nUpdated projects: {', '.join(updated_projects)}")

    if failed_projects:
        print(f"\nFailed projects: {', '.join(failed_projects)}")


if __name__ == "__main__":
    main()
