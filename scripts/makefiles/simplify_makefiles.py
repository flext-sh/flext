#!/usr/bin/env python3
"""Simplify Makefile structures across all FLEXT projects following KISS principle.

This script consolidates 62 complex Makefiles into a single standardized template
with project-specific overrides where needed.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import shutil
from pathlib import Path


def main() -> None:
    """Simplify Makefile structures across workspace following KISS principle."""
    workspace_root = Path(__file__).parent.parent.parent
    template_file = workspace_root / ".flext-makefile-template.mk"

    if not template_file.exists():
        return

    # Find all FLEXT project Makefiles
    makefile_files = list(workspace_root.glob("*/Makefile"))
    makefile_files = [
        f
        for f in makefile_files
        if not str(f).startswith(str(workspace_root / ".venv"))
    ]

    # Create backup directory for complex Makefiles
    backup_dir = workspace_root / "backups" / "makefiles_complex"
    backup_dir.mkdir(parents=True, exist_ok=True)

    simplified_count = 0

    for makefile_path in makefile_files:
        project_name = makefile_path.parent.name

        # Skip workspace root and cmd projects (they may need special handling)
        if project_name in {"flext", "cmd"} or "cmd/" in str(makefile_path):
            continue

        # Backup original complex Makefile
        backup_path = backup_dir / f"{project_name}_Makefile.bak"
        shutil.copy2(makefile_path, backup_path)

        # Create simplified Makefile using template
        simplified_makefile = _create_simplified_makefile(project_name, template_file)

        # Write simplified Makefile
        try:
            with Path(makefile_path).open("w", encoding="utf-8") as f:
                f.write(simplified_makefile)
            simplified_count += 1
        except (OSError, ValueError, TypeError):
            pass


def _create_simplified_makefile(project_name: str, template_file: Path) -> str:
    """Create simplified Makefile content for a specific project."""
    # Read template content
    template_file.read_text(encoding="utf-8")

    # Project-specific customizations based on KISS principle
    customizations = _get_project_customizations(project_name)

    # Build simplified Makefile
    makefile_content = f"""# {project_name} - FLEXT Simplified Makefile
# Following KISS principle - Single template, minimal complexity
# Generated from .flext-makefile-template.mk

# Include standardized template
include ../.flext-makefile-template.mk

# Project-specific overrides (KISS: only what's truly needed)
"""

    # Add project-specific customizations if any
    if customizations:
        makefile_content += "\n" + customizations + "\n"

    return makefile_content


def _get_project_customizations(project_name: str) -> str:
    """Get project-specific customizations based on KISS principle."""
    # KISS: Only add customizations for projects that truly need them
    customizations = {
        "flext-core": """
# Core project - foundation module
PROJECT_NAME := flext_core
""",
        "flext-api": """
# API project - FastAPI application
PROJECT_NAME := flext_api
SRC_MODULE := flext_api

# API-specific commands
dev: poetry-check ## Start development server
	@echo "$(BLUE)🚀 Starting FastAPI development server...$(NC)"
	@$(POETRY_RUN) uvicorn flext_api.main:app --reload --host 0.0.0.0 --port $${FLEXT_API_PORT:-8000}
""",
        "flext-web": """
# Web project - Django application
PROJECT_NAME := flext_web
SRC_MODULE := flext_web

# Django-specific commands
migrate: poetry-check ## Run Django migrations
	@echo "$(BLUE)🔄 Running Django migrations...$(NC)"
	@$(POETRY_RUN) python manage.py migrate

collectstatic: poetry-check ## Collect static files
	@echo "$(BLUE)📦 Collecting static files...$(NC)"
	@$(POETRY_RUN) python manage.py collectstatic --noinput
""",
        "flext-observability": """
# Observability project - Monitoring and logging
PROJECT_NAME := flext_observability
SRC_MODULE := flext_observability

# Monitoring-specific commands
setup-prometheus: ## Setup Prometheus configuration
	@echo "$(BLUE)📊 Setting up Prometheus...$(NC)"
	@$(POETRY_RUN) python -m flext_observability.setup prometheus

setup-grafana: ## Setup Grafana dashboards
	@echo "$(BLUE)📈 Setting up Grafana...$(NC)"
	@$(POETRY_RUN) python -m flext_observability.setup grafana
""",
        "client-a-oud-mig": """
# client-a OUD Migration project
PROJECT_NAME := client-a_oud_mig
SRC_MODULE := client-a_oud_mig

# client-a-specific commands
process-ldif: poetry-check ## Process LDIF files
	@echo "$(BLUE)🔄 Processing LDIF files...$(NC)"
	@$(POETRY_RUN) python -m client-a_oud_mig.cli process

validate-ldap: poetry-check ## Validate LDAP connection
	@echo "$(BLUE)🔍 Validating LDAP connection...$(NC)"
	@$(POETRY_RUN) python -m client-a_oud_mig.cli validate
""",
    }

    return customizations.get(project_name, "")


if __name__ == "__main__":
    main()
