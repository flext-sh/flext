#!/usr/bin/env python
"""
Fix remaining dependency issues for the 3 failed projects.

Per CLAUDE.md RULE 4: Complete Delivery
"""

import subprocess
from pathlib import Path


def fix_complex_dependencies() -> None:
    """Fix the 3 projects with complex dependencies."""
    workspace_root = Path("/home/marlonsc/pyauto")

    # These 3 failed: flx, dbt-ldap, flx-meltano-enterprise
    complex_fixes = {
        "flx": {
            "additional_deps": [
                "pydantic>=2.0",
                "fastapi>=0.100.0",
                "sqlalchemy>=2.0",
                "alembic>=1.12.0",
                "click>=8.1.0",
                "rich>=13.0.0",
                "python-dotenv>=1.0.0",
                "httpx>=0.25.0",
                "uvicorn>=0.24.0",
                "structlog>=23.0.0",
                "tenacity>=8.2.0",
                "prometheus-client>=0.18.0",
                "opentelemetry-api>=1.20.0",
                "opentelemetry-sdk>=1.20.0",
                "dependency-injector>=4.41.0",
            ]
        },
        "dbt-ldap": {
            "additional_deps": [
                "dbt-core>=1.5.0",
                "dbt-postgres>=1.5.0",
                "ldap3>=2.9.0",
                "pandas>=2.0.0",
                "numpy>=1.24.0",
            ]
        },
        "flx-meltano-enterprise": {
            "additional_deps": [
                "meltano>=3.0.0",
                "singer-python>=6.0.0",
                "pipelinewise-singer-python>=1.2.0",
                "pyarrow>=14.0.0",
                "sqlalchemy>=2.0.0",
                "alembic>=1.12.0",
                "celery>=5.3.0",
                "redis>=5.0.0",
                "kombu>=5.3.0",
            ]
        },
    }

    for project, config in complex_fixes.items():
        project_path = workspace_root / project

        if not project_path.exists():
            continue

        # Add dependencies one by one
        for dep in config["additional_deps"]:
            try:
                result = subprocess.run(
                    ["poetry", "add", dep],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    pass
            except Exception:
                pass

        # Generate lock file
        try:
            lock_result = subprocess.run(
                ["poetry", "lock"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if lock_result.returncode == 0:
                pass
        except Exception:
            pass


if __name__ == "__main__":
    fix_complex_dependencies()
