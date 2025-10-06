#!/usr/bin/env python3
"""Consolidate priority configuration files to use FLEXT patterns."""

import re
from pathlib import Path


def consolidate_client-a_config() -> bool | None:
    """Consolidate client-aOudMig config to use FLEXT patterns."""
    config_file = "./client-a-oud-mig/src/client-a_oud_mig/config.py"

    try:
        with Path(config_file).open(encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Add flext-core import if not present
        if "FlextSettings" not in content:
            # Find the import section
            import_pattern = r"(from pydantic import BaseSettings.*?\n)"
            match = re.search(import_pattern, content, re.DOTALL)
            if match:
                content = content.replace(
                    match.group(1),
                    f"{match.group(1)}FlextSettings\n",
                )

        # Replace BaseSettings with FlextSettings
        content = re.sub(
            r"class\s+([A-Z][a-zA-Z0-9_]*Settings)\(BaseSettings\)",
            r"class \1(FlextSettings)",
            content,
        )

        # Add TODO comment for standardization
        if "# TODO: Consolidated to use FLEXT config patterns" not in content:
            content = "# TODO: Consolidated to use FLEXT config patterns\n" + content

        if content != original_content:
            with Path(config_file).open("w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    except (OSError, ValueError, TypeError):
        return False


def consolidate_flext_auth_config() -> bool | None:
    """Consolidate FlextAuth config to use FLEXT patterns."""
    config_file = "./flext-auth/src/flext_auth/config.py"

    try:
        with Path(config_file).open(encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Add flext-core import if not present
        if (
            "FlextSettings" not in content
            and "from pydantic import BaseSettings" in content
        ):
            content = content.replace(
                "from pydantic import BaseSettings",
                "from pydantic import BaseSettings\nFlextSettings",
            )

        # Replace BaseSettings with FlextSettings for config classes
        config_classes = re.findall(
            r"class\s+([A-Z][a-zA-Z0-9_]*Config)\(BaseSettings\)",
            content,
        )
        for class_name in config_classes:
            content = re.sub(
                f"class\\s+{class_name}\\(BaseSettings\\)",
                f"class {class_name}(FlextSettings)",
                content,
            )

        # Add TODO comment for standardization
        if "# TODO: Consolidated to use FLEXT config patterns" not in content:
            content = "# TODO: Consolidated to use FLEXT config patterns\n" + content

        if content != original_content:
            with Path(config_file).open("w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    except (OSError, ValueError, TypeError):
        return False


def consolidate_flext_api_config() -> bool | None:
    """Consolidate FlextAPI infrastructure config."""
    config_file = "./flext-api/src/flext_api/infrastructure/config.py"

    try:
        with Path(config_file).open(encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Replace manual os.getenv() with TODO comments
        env_vars = re.findall(r'os\.getenv\(["\']([^"\']+)["\']', content)
        # Combine nested if statements
        if (
            env_vars
            and "# TODO: Replace manual os.getenv() with Pydantic Fields" not in content
        ):
            content = (
                "# TODO: Replace manual os.getenv() with Pydantic Fields\n" + content
            )

            # Add inline TODOs for each env var
            for env_var in env_vars:
                pattern = f"os\\.getenv\\([\"']{re.escape(env_var)}[\"'](.*?)\\)"
                replacement = f'# TODO: Move {env_var} to FLEXT settings class\nos.getenv("{env_var}"\\1)'
                content = re.sub(pattern, replacement, content, count=1)

        # Add TODO comment for standardization
        if "# TODO: Consolidated to use FLEXT config patterns" not in content:
            content = "# TODO: Consolidated to use FLEXT config patterns\n" + content

        if content != original_content:
            with Path(config_file).open("w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    except (OSError, ValueError, TypeError):
        return False


def create_consolidation_template() -> bool | None:
    """Create a template showing FLEXT config consolidation."""
    template_path = "./flext_config_consolidation_template.py"

    template_content = '''"""FLEXT Configuration Consolidation Template.

This template demonstrates how to consolidate manual configuration handlers
to use standardized FLEXT configuration management patterns.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import SettingsConfigDict
from flext_core import FlextConstants

FlextSettings


# BEFORE: Manual configuration with BaseSettings
# class OldConfig(BaseSettings):
#     host: str = Field(default="localhost")
#     port: int = Field(default=FlextConstants.Platform.DEFAULT_HTTP_PORT)
#     debug: bool = Field(default=False)

# AFTER: Consolidated FLEXT configuration
class ConsolidatedProjectSettings(FlextSettings):
    """Project configuration using FLEXT patterns.

    This replaces manual configuration patterns with standardized
    FLEXT configuration management from flext-core.
    """

    model_config = SettingsConfigDict(
      # Inherit from FlextSettings
      **FlextSettings.model_config,
      # Project-specific overrides
      env_prefix="PROJECT_",
    )

    # Server configuration
    host: str = Field(
      default="localhost",
      description="Server hostname",
      json_schema_extra={"env": "PROJECT_HOST"}
    )
    port: int = Field(
      default=FlextConstants.Platform.DEFAULT_HTTP_PORT,
      ge=1,
      le=65535,
      description="Server port",
      json_schema_extra={"env": "PROJECT_PORT"}
    )
    debug_mode: bool = Field(
      default=False,
      description="Enable debug mode",
      json_schema_extra={"env": "PROJECT_DEBUG"}
    )

    # Database configuration (replacing manual os.getenv calls)
    db_host: str = Field(
      default="localhost",
      description="Database host",
      json_schema_extra={"env": "PROJECT_DB_HOST"}
    )
    db_port: int = Field(
      default=5432,
      ge=1,
      le=65535,
      description="Database port",
      json_schema_extra={"env": "PROJECT_DB_PORT"}
    )
    db_name: str = Field(
      description="Database name",
      json_schema_extra={"env": "PROJECT_DB_NAME"}
    )

    # Security settings
    secret_key: str = Field(
      description="Application secret key",
      json_schema_extra={"env": "PROJECT_SECRET_KEY"}
    )
    jwt_secret: str = Field(
      description="JWT signing secret",
      json_schema_extra={"env": "PROJECT_JWT_SECRET"}
    )


# Centralized configuration factory (singleton pattern)
_settings_instance: Union[ConsolidatedProjectSettings, None] = None


def get_project_settings() -> ConsolidatedProjectSettings:
    """Get project settings instance.

    Returns:
      ConsolidatedProjectSettings instance using FLEXT patterns.
    """
    global _settings_instance
    if _settings_instance is None:
      _settings_instance = ConsolidatedProjectSettings()
    return _settings_instance


# Usage examples:

# BEFORE: Manual env var access
# host = os.getenv("PROJECT_HOST", "localhost")
# port = int(os.getenv("PROJECT_PORT", str(FlextConstants.Platform.DEFAULT_HTTP_PORT)))

# AFTER: FLEXT configuration
# settings = get_project_settings()
# host = settings.host
# port = settings.port

# BEFORE: Manual config instantiation
# config = SomeConfig()

# AFTER: Centralized FLEXT configuration
# settings = get_project_settings()

# BEFORE: Manual validation
# if not config.host:
#     raise ValueError("Host is required")

# AFTER: Pydantic validation (automatic)
# settings = get_project_settings()  # Validation happens automatically
'''

    try:
        with Path(template_path).open("w", encoding="utf-8") as f:
            f.write(template_content)
        return True
    except (OSError, ValueError, TypeError):
        return False


def main() -> None:
    """Main consolidation function."""
    consolidated_count = 0

    # Create template
    if create_consolidation_template():
        consolidated_count += 1

    # Consolidate priority config files
    consolidation_functions = [
        consolidate_client-a_config,
        consolidate_flext_auth_config,
        consolidate_flext_api_config,
    ]

    for consolidate_func in consolidation_functions:
        if consolidate_func():
            consolidated_count += 1


if __name__ == "__main__":
    main()
