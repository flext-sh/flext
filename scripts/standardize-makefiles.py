#!/usr/bin/env python3
"""
FLEXT Makefile Standardization Script
====================================
Standardizes all project Makefiles to follow the same pattern as flext-core
"""

import shutil
from pathlib import Path

# Project structure mapping
PROJECT_TYPES = {
    "core": ["flext-core"],
    "api": ["flext-api", "flext-auth", "flext-grpc", "flext-web"],
    "cli": ["flext-cli"],
    "data": [
        "flext-tap-ldap",
        "flext-tap-oracle-oic",
        "flext-tap-oracle-wms",
        "flext-target-ldap",
        "flext-target-oracle",
        "flext-target-oracle-oic",
        "flext-dbt-ldap",
    ],
    "infra": [
        "flext-observability",
        "flext-quality",
        "flext-plugin",
        "flext-meltano",
        "flext-ldap",
        "flext-db-oracle",
        "flext-meltano-bridge",
    ],
    "extension": ["flext-oracle-oic-ext"],
    "project": ["client-a-oud-mig", "client-b-poc-oic-wms", "client-b-meltano-native"],
}


def get_project_type(project_name: str) -> str:
    """Determine project type based on name."""
    for ptype, projects in PROJECT_TYPES.items():
        if project_name in projects:
            return ptype
    return "generic"


def get_project_display_name(project_name: str) -> str:
    """Get display name for project."""
    name_parts = project_name.replace("-", " ").title()
    if "Flext" in name_parts:
        return name_parts
    return f"FLEXT {name_parts}"


def get_project_description(project_name: str, project_type: str) -> str:
    """Get project description based on type."""
    descriptions = {
        "core": "Foundation Framework",
        "api": "API Service",
        "cli": "Command Line Interface",
        "data": "Data Integration Pipeline",
        "infra": "Infrastructure Component",
        "extension": "Enterprise Extension",
        "project": "Enterprise Application",
    }
    return descriptions.get(project_type, "FLEXT Component")


def create_makefile_template(project_name: str, project_type: str) -> str:
    """Create standardized Makefile content."""
    display_name = get_project_display_name(project_name)
    description = get_project_description(project_name, project_type)

    template = f"""# {project_name.upper()} Makefile - {description}
# {'=' * (len(project_name) + len(description) + 15)}

.PHONY: help install test clean lint format build docs dev security type-check pre-commit

# Default target
help: ## Show this help message
	@echo "🏗️  {display_name} - {description}"
	@echo "{'=' * (len(display_name) + len(description) + 5)}"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}}'

# Installation & Setup
install: ## Install dependencies with Poetry
	@echo "📦 Installing dependencies for {project_name}..."
	poetry install --all-extras

install-dev: ## Install with dev dependencies
	@echo "🛠️  Installing dev dependencies..."
	poetry install --all-extras --group dev --group test --group security

# Testing
test: ## Run tests
	@echo "🧪 Running tests for {project_name}..."
	@if [ -d tests ]; then \\
		python -m pytest tests/ -v; \\
	else \\
		echo "No tests directory found"; \\
	fi

test-coverage: ## Run tests with coverage
	@echo "🧪 Running tests with coverage for {project_name}..."
	@python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

# Code Quality - Maximum Strictness
lint: ## Run all linters with maximum strictness
	@echo "🔍 Running maximum strictness linting for {project_name}..."
	poetry run ruff check . --output-format=verbose
	@echo "✅ Ruff linting complete"

format: ## Format code with strict standards
	@echo "🎨 Formatting code with strict standards..."
	poetry run black .
	poetry run ruff check --fix .
	@echo "✅ Code formatting complete"

type-check: ## Run strict type checking
	@echo "🎯 Running strict MyPy type checking..."
	poetry run mypy src/{project_name.replace('-', '_')} --strict --show-error-codes
	@echo "✅ Type checking complete"

security: ## Run security analysis
	@echo "🔒 Running security analysis..."
	poetry run bandit -r src/ -f json -o reports/security.json || true
	poetry run bandit -r src/ -f txt
	@echo "✅ Security analysis complete"

pre-commit: ## Run pre-commit hooks
	@echo "🎣 Running pre-commit hooks..."
	poetry run pre-commit run --all-files
	@echo "✅ Pre-commit checks complete"

check: lint type-check security test ## Run all quality checks
	@echo "✅ All quality checks complete for {project_name}!"

# Build & Distribution
build: ## Build the package with Poetry
	@echo "🔨 Building {project_name} package..."
	poetry build
	@echo "📦 Package built successfully"

build-clean: clean build ## Clean then build
	@echo "🔄 Clean build for {project_name}..."

publish-test: build ## Publish to TestPyPI
	@echo "🚀 Publishing to TestPyPI..."
	poetry publish --repository testpypi

publish: build ## Publish to PyPI
	@echo "🚀 Publishing {project_name} to PyPI..."
	poetry publish

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation for {project_name}..."
	@if [ -f docs/conf.py ]; then \\
		cd docs && make html; \\
	else \\
		echo "No docs configuration found"; \\
	fi

# Cleanup
clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts for {project_name}..."
	@rm -rf build/ dist/ *.egg-info/
	@find . -type d -name "__pycache__" -exec rm -rf {{}} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true

# Development Workflow
dev-setup: install-dev ## Complete development setup
	@echo "🎯 Setting up development environment for {project_name}..."
	poetry run pre-commit install
	mkdir -p reports
	@echo "✅ Development setup complete!"

dev: ## Run in development mode
	@echo "🔧 Starting {project_name} in development mode..."
	PYTHONPATH=src poetry run python -m {project_name.replace('-', '_')} --debug

dev-test: ## Quick development test cycle
	@echo "⚡ Quick test cycle for development..."
	poetry run pytest tests/ -v --tb=short

# Environment variables
export PYTHONPATH := $(PWD)/src:$(PYTHONPATH)
export {project_name.upper().replace('-', '_')}_DEV := true
"""

    # Add project-specific commands based on type
    if project_type == "api":
        template += """
# API-specific commands
api-dev: ## Run API in development mode
	@echo "🚀 Starting API development server..."
	PYTHONPATH=src poetry run uvicorn {project_name.replace('-', '_')}.main:app --reload --host 0.0.0.0 --port 8000

api-test: ## Test API endpoints
	@echo "🧪 Testing API endpoints..."
	poetry run pytest tests/ -v -m "not slow"
"""

    elif project_type == "cli":
        template += """
# CLI-specific commands
cli-install: ## Install CLI globally
	@echo "📦 Installing CLI globally..."
	pip install -e .

cli-test: ## Test CLI commands
	@echo "🧪 Testing CLI commands..."
	poetry run pytest tests/ -v
"""

    elif project_type == "data":
        template += """
# Data Integration commands
validate-schema: ## Validate data schemas
	@echo "🔍 Validating data schemas..."
	PYTHONPATH=src poetry run python -m {project_name.replace('-', '_')}.validate

test-connection: ## Test data source connection
	@echo "🔌 Testing data source connection..."
	PYTHONPATH=src poetry run python -m {project_name.replace('-', '_')}.test_connection
"""

    return template


def backup_makefile(project_path: Path) -> bool:
    """Backup existing Makefile."""
    makefile_path = project_path / "Makefile"
    if makefile_path.exists():
        backup_path = project_path / "Makefile.bak"
        shutil.copy2(makefile_path, backup_path)
        print(f"    📋 Backed up existing Makefile to {backup_path}")
        return True
    return False


def standardize_project(project_name: str, workspace_root: Path) -> bool:
    """Standardize a single project's Makefile."""
    project_path = workspace_root / project_name

    if not project_path.exists():
        print(f"    ❌ Project directory {project_name} not found")
        return False

    print(f"    🔧 Standardizing {project_name}...")

    # Backup existing Makefile
    backup_makefile(project_path)

    # Determine project type and create new Makefile
    project_type = get_project_type(project_name)
    makefile_content = create_makefile_template(project_name, project_type)

    # Write new Makefile
    makefile_path = project_path / "Makefile"
    with open(makefile_path, "w") as f:
        f.write(makefile_content)

    print(f"    ✅ Standardized {project_name} ({project_type} type)")
    return True


def main() -> None:
    """Main standardization process."""
    print("🚀 FLEXT Makefile Standardization")
    print("=================================")

    workspace_root = Path.cwd()

    # Get all projects to standardize
    all_projects = []
    for projects in PROJECT_TYPES.values():
        all_projects.extend(projects)

    print(f"📊 Found {len(all_projects)} projects to standardize")
    print()

    success_count = 0

    for project_name in all_projects:
        if standardize_project(project_name, workspace_root):
            success_count += 1

    print()
    print("📊 Standardization Summary")
    print("=========================")
    print(f"✅ Successfully standardized: {success_count}/{len(all_projects)} projects")

    if success_count == len(all_projects):
        print("🎉 All projects successfully standardized!")
    else:
        print(f"⚠️  {len(all_projects) - success_count} projects need manual attention")

    print()
    print("🔧 Next Steps:")
    print("1. Review generated Makefiles")
    print("2. Test with: make -C [project] help")
    print("3. Run workspace tests: make test-all")
    print("4. Commit changes when satisfied")


if __name__ == "__main__":
    main()
