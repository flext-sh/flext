#!/usr/bin/env python3
"""Script to consolidate manual configuration handlers to use FLEXT patterns.

This script identifies and refactors manual configuration handling patterns
to use standardized FLEXT configuration management from flext-core.
"""

from __future__ import annotations

import functools
import operator
import re
import shutil
import subprocess
from pathlib import Path

from flext_core import FlextResult, get_logger

logger = get_logger(__name__)


def find_manual_config_patterns() -> FlextResult[dict[str, list[str]]]:
    """Find files with manual configuration patterns.

    Returns:
        FlextResult containing dict of pattern types to file lists.

    """
    try:
        patterns: dict[str, list[str]] = {
            "manual_env_vars": [],
            "manual_pydantic": [],
            "manual_file_loading": [],
            "manual_validation": [],
        }

        # Find manual os.getenv() usage
        cmd = [
            "find",
            ".",
            "-name",
            "*.py",
            "-type",
            "f",
            "-exec",
            "grep",
            "-l",
            "os\\.getenv\\|os\\.environ\\.get",
            "{}",
            ";",
        ]
        if not shutil.which("find") or not shutil.which("grep"):
            return FlextResult.fail("find or grep not found")

        # Security: cmd is hardcoded, not user input
        result = subprocess.run(  # noqa: S603
            cmd,
            capture_output=True,
            text=True,
            check=False,
            shell=False,  # Validated: cmd is hardcoded
        )
        if result.returncode == 0:
            patterns["manual_env_vars"] = [
                f.strip() for f in result.stdout.split("\n") if f.strip()
            ]

        # Find manual Pydantic instantiation (Config(), Settings(), etc.)
        cmd = [
            "find",
            ".",
            "-name",
            "*.py",
            "-type",
            "f",
            "-exec",
            "grep",
            "-l",
            "Settings()\\|Config()\\|.*Config()",
            "{}",
            ";",
        ]
        # Security: cmd is hardcoded, not user input
        result = subprocess.run(  # noqa: S603
            cmd,
            capture_output=True,
            text=True,
            check=False,
            shell=False,  # Validated: cmd is hardcoded
        )
        if result.returncode == 0:
            patterns["manual_pydantic"] = [
                f.strip() for f in result.stdout.split("\n") if f.strip()
            ]

        # Find manual file loading (json.load, yaml.load)
        cmd = [
            "find",
            ".",
            "-name",
            "*.py",
            "-type",
            "f",
            "-exec",
            "grep",
            "-l",
            "json\\.load\\|yaml\\.load\\|yaml\\.safe_load",
            "{}",
            ";",
        ]
        # Security: cmd is hardcoded, not user input
        result = subprocess.run(  # noqa: S603
            cmd,
            capture_output=True,
            text=True,
            check=False,
            shell=False,  # Validated: cmd is hardcoded
        )
        if result.returncode == 0:
            patterns["manual_file_loading"] = [
                f.strip() for f in result.stdout.split("\n") if f.strip()
            ]

        # Find manual validation patterns
        cmd = [
            "find",
            ".",
            "-name",
            "*.py",
            "-type",
            "f",
            "-exec",
            "grep",
            "-l",
            "if not.*config\\|assert.*config",
            "{}",
            ";",
        ]
        # Security: cmd is hardcoded, not user input
        result = subprocess.run(  # noqa: S603
            cmd,
            capture_output=True,
            text=True,
            check=False,
            shell=False,  # Validated: cmd is hardcoded
        )
        if result.returncode == 0:
            patterns["manual_validation"] = [
                f.strip() for f in result.stdout.split("\n") if f.strip()
            ]

        total_files = len(set(functools.reduce(operator.iadd, patterns.values(), [])))
        logger.info(f"Found {total_files} files with manual config patterns")

        return FlextResult.ok(patterns)

    except (OSError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Failed to find manual config patterns: {e}")


def refactor_manual_env_vars(file_path: str) -> FlextResult[bool]:
    """Refactor manual os.getenv() usage to use FLEXT config patterns.

    Args:
        file_path: Path to file to refactor.

    Returns:
        FlextResult indicating success and whether changes were made.

    """
    try:
        with Path(file_path).open(encoding="utf-8") as f:
            content = f.read()

        changes_made = False

        # Pattern 1: os.getenv("VAR", default) -> use Pydantic Field
        env_pattern = r'os\.getenv\(["\']([^"\']+)["\'],\s*["\']?([^"\']*)["\']?\)'
        matches = re.findall(env_pattern, content)

        # Combine nested if statements
        if matches and "# TODO: Consolidate to FLEXT config patterns" not in content:
            # Find import section and add comment
            import_section = re.search(
                r"(from __future__ import annotations\n\n)",
                content,
            )
            if import_section:
                content = content.replace(
                    import_section.group(1),
                    f"{import_section.group(1)}"
                    f"# TODO: Consolidate manual env vars to FLEXT config patterns\n",
                )
                changes_made = True

        # Pattern 2: Replace simple os.getenv() with commented alternatives
        simple_env_pattern = (
            r'(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*os\.getenv\(["\']([^"\']+)["\']'
            r'(?:,\s*["\']?([^"\']*)["\']?)?\)'
        )

        def replace_env_var(match: re.Match[str]) -> str:
            indent = match.group(1)
            var_name = match.group(2)
            env_name = match.group(3)
            default_val = match.group(4) or '""'

            return (
                f"{indent}# TODO: Move to FLEXT settings class: {env_name}\n"
                f"{indent}{var_name} = os.getenv('{env_name}', {default_val!r})"
            )

        new_content = re.sub(simple_env_pattern, replace_env_var, content)
        if new_content != content:
            content = new_content
            changes_made = True

        if changes_made:
            with Path(file_path).open("w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"✅ Added FLEXT config TODOs to: {file_path}")
            return FlextResult.ok(data=True)
        logger.info(f"⏭️ No env var changes needed: {file_path}")
        return FlextResult.ok(data=False)

    except (OSError, ValueError, TypeError) as e:
        logger.exception(f"❌ Error refactoring env vars in {file_path}")
        return FlextResult.fail(f"Failed to refactor env vars: {e}")


def refactor_manual_pydantic(file_path: str) -> FlextResult[bool]:
    """Refactor manual Pydantic instantiation to use FLEXT patterns.

    Args:
        file_path: Path to file to refactor.

    Returns:
        FlextResult indicating success and whether changes were made.

    """
    try:
        with Path(file_path).open(encoding="utf-8") as f:
            content = f.read()

        changes_made = False

        # Pattern: direct Settings/Config instantiation
        config_instantiation = (
            r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*"
            r"([A-Z][a-zA-Z0-9_]*(?:Settings|Config))\(\)"
        )

        def replace_config_instantiation(match: re.Match[str]) -> str:
            indent = match.group(1)
            var_name = match.group(2)
            class_name = match.group(3)

            return (
                f"{indent}# TODO: Use FLEXT configuration factory pattern\n"
                f"{indent}{var_name} = {class_name}()"
            )

        new_content = re.sub(
            config_instantiation,
            replace_config_instantiation,
            content,
        )
        if new_content != content:
            content = new_content
            changes_made = True

        if changes_made:
            with Path(file_path).open("w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"✅ Added FLEXT config TODOs to: {file_path}")
            return FlextResult.ok(data=True)
        logger.info(f"⏭️ No Pydantic changes needed: {file_path}")
        return FlextResult.ok(data=False)

    except (OSError, ValueError, TypeError) as e:
        logger.exception(f"❌ Error refactoring Pydantic in {file_path}")
        return FlextResult.fail(f"Failed to refactor Pydantic: {e}")


def refactor_manual_file_loading(file_path: str) -> FlextResult[bool]:
    """Refactor manual file loading to use FLEXT config patterns.

    Args:
        file_path: Path to file to refactor.

    Returns:
        FlextResult indicating success and whether changes were made.

    """
    try:
        with Path(file_path).open(encoding="utf-8") as f:
            content = f.read()

        changes_made = False

        # Pattern: json.load() or yaml.load()
        file_load_pattern = (
            r"(\s+)(.*?)\s*=\s*(json\.load|yaml\.load|yaml\.safe_load)\((.*?)\)"
        )

        def replace_file_loading(match: re.Match[str]) -> str:
            indent = match.group(1)
            var_assignment = match.group(2)
            load_func = match.group(3)
            load_args = match.group(4)

            return (
                f"{indent}# TODO: Use FLEXT config file loading patterns\n"
                f"{indent}{var_assignment} = {load_func}({load_args})"
            )

        new_content = re.sub(file_load_pattern, replace_file_loading, content)
        if new_content != content:
            content = new_content
            changes_made = True

        if changes_made:
            with Path(file_path).open("w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"✅ Added FLEXT config TODOs to: {file_path}")
            return FlextResult.ok(data=True)
        logger.info(f"⏭️ No file loading changes needed: {file_path}")
        return FlextResult.ok(data=False)

    except (OSError, ValueError, TypeError) as e:
        logger.exception(f"❌ Error refactoring file loading in {file_path}")
        return FlextResult.fail(f"Failed to refactor file loading: {e}")


def create_flext_config_template(output_path: str) -> FlextResult[None]:
    """Create a template for FLEXT configuration consolidation.

    Args:
        output_path: Path where to create the template.

    Returns:
        FlextResult indicating success.

    """
    try:
        template_content = '''"""FLEXT Configuration Consolidation Template.

This template shows how to consolidate manual configuration handlers
to use standardized FLEXT configuration management patterns.
"""


from pydantic import BaseSettings, Field
from pydantic_settings import SettingsConfigDict

FlextCoreSettings


class ProjectSpecificSettings(FlextCoreSettings):
    """Project-specific configuration using FLEXT patterns.

    This replaces manual os.getenv() calls and direct config instantiation
    with standardized Pydantic-based configuration management.
    """

    model_config = SettingsConfigDict(
        env_prefix="PROJECT_",
        env_file=None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        env_nested_delimiter="__",
    )

    # Replace manual env vars like: host = os.getenv("HOST", "localhost")
    host: str = Field(default="localhost", description="Server hostname")
    port: int = Field(default=8080, description="Server port")
    debug_mode: bool = Field(default=False, description="Enable debug mode")

    # Database configuration
    db_host: str = Field(default="localhost", description="Database host")
    db_port: int = Field(default=5432, description="Database port")
    db_name: str = Field(description="Database name")
    db_user: str = Field(description="Database username")
    db_password: str = Field(description="Database password")


# Centralized configuration factory
_settings_instance: ProjectSpecificSettings | None = None


def get_project_settings() -> ProjectSpecificSettings:
    """Get project settings instance (singleton pattern).

    Returns:
        ProjectSpecificSettings instance.
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = ProjectSpecificSettings()
    return _settings_instance


# Usage examples:

# Instead of: host = os.getenv("HOST", "localhost")
# Use: settings = get_project_settings(); host = settings.host

# Instead of: config = SomeConfig()
# Use: settings = get_project_settings()

# Instead of: with open("config.json") as f: config = json.load(f)
# Use: class Settings with env_file="config.json" or json_file="config.json"
'''

        with Path(output_path).open("w", encoding="utf-8") as f:
            f.write(template_content)

        logger.info(f"✅ Created FLEXT config template: {output_path}")
        return FlextResult.ok(None)

    except (OSError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Failed to create template: {e}")


def main() -> None:
    """Main function to consolidate manual configuration handlers."""
    logger.info("🔍 Starting manual configuration consolidation...")

    # Create template
    template_result = create_flext_config_template("flext_config_template.py")
    if not template_result.success:
        logger.error(f"Failed to create template: {template_result.error}")
        return

    # Find manual config patterns
    patterns_result = find_manual_config_patterns()
    if not patterns_result.success:
        logger.error(f"Failed to find patterns: {patterns_result.error}")
        return

    patterns = patterns_result.data
    if not patterns:
        logger.info("✅ No manual configuration patterns found!")
        return

    # Process files by pattern type
    total_processed = 0
    total_modified = 0

    # Priority 1: Manual environment variables (security critical)
    logger.info("🔧 Processing manual environment variables...")
    for file_path in patterns["manual_env_vars"][:20]:  # Process first 20 files
        result = refactor_manual_env_vars(file_path)
        total_processed += 1
        if result.success and result.data:
            total_modified += 1

    # Priority 2: Manual Pydantic instantiation
    logger.info("🔧 Processing manual Pydantic instantiation...")
    for file_path in patterns["manual_pydantic"][:15]:  # Process first 15 files
        result = refactor_manual_pydantic(file_path)
        total_processed += 1
        if result.success and result.data:
            total_modified += 1

    # Priority 3: Manual file loading
    logger.info("🔧 Processing manual file loading...")
    for file_path in patterns["manual_file_loading"][:10]:  # Process first 10 files
        result = refactor_manual_file_loading(file_path)
        total_processed += 1
        if result.success and result.data:
            total_modified += 1

    logger.info("✅ Manual configuration consolidation completed!")
    logger.info(f"📊 Processed {total_processed} files, modified {total_modified}")
    logger.info("📋 Next steps:")
    logger.info("  1. Review TODO comments added to files")
    logger.info("  2. Implement FLEXT config classes based on template")
    logger.info("  3. Replace manual patterns with centralized config")
    logger.info("  4. Update imports to use flext-core configuration")


if __name__ == "__main__":
    main()
