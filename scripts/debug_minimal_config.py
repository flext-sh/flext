#!/usr/bin/env python3
"""Create a minimal configuration to isolate the issue."""

import os
import sys
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "flext-core" / "src"))


def test_minimal_config():
    """Test minimal pydantic-settings configuration."""
    print("🔍 TESTING MINIMAL PYDANTIC-SETTINGS...")

    class MinimalConfig(BaseSettings):
        model_config = SettingsConfigDict(
            env_prefix="FLEXT_API_",
            env_nested_delimiter="__",
            case_sensitive=False,
        )

        # Test fields
        debug: bool = Field(False, description="Debug mode")
        secret_key: str = Field(
            "default-secret", description="Secret key", alias="security__secret_key",
        )
        host: str = Field("default-host", description="Host", alias="server__host")

    # Set test environment variables
    os.environ["FLEXT_API_DEBUG"] = "true"
    os.environ["FLEXT_API_SECURITY__SECRET_KEY"] = "env-secret-123"
    os.environ["FLEXT_API_SERVER__HOST"] = "env-host-456"

    print("Environment variables set:")
    for key in [
        "FLEXT_API_DEBUG",
        "FLEXT_API_SECURITY__SECRET_KEY",
        "FLEXT_API_SERVER__HOST",
    ]:
        print(f"  {key} = {os.environ.get(key, 'NOT SET')}")

    try:
        config = MinimalConfig()

        print("\n📋 MINIMAL CONFIG RESULTS:")
        print(f"  debug: {config.debug} (should be True)")
        print(f"  secret_key: {config.secret_key} (should be 'env-secret-123')")
        print(f"  host: {config.host} (should be 'env-host-456')")

        if (
            config.debug
            and config.secret_key == "env-secret-123"
            and config.host == "env-host-456"
        ):
            print("  ✅ Minimal config working perfectly!")
        else:
            print("  ❌ Minimal config has issues")

    except Exception as e:
        print(f"❌ Minimal config failed: {e}")
        import traceback

        traceback.print_exc()


def test_inheritance_issue():
    """Test if the inheritance from flext-core is causing issues."""
    print("\n🔍 TESTING INHERITANCE ISSUE...")

    # Import the BaseSettings from flext-core
    try:
        from flext_core.config import BaseSettings as FlextBaseSettings

        class InheritedConfig(FlextBaseSettings):
            model_config = SettingsConfigDict(
                env_prefix="FLEXT_API_",
                env_nested_delimiter="__",
                case_sensitive=False,
            )

            debug: bool = Field(False, description="Debug mode")
            secret_key: str = Field(
                "default-secret", description="Secret key", alias="security__secret_key",
            )

        config = InheritedConfig()

        print("📋 INHERITED CONFIG RESULTS:")
        print(f"  debug: {config.debug}")
        print(f"  secret_key: {config.secret_key}")

        if config.debug and config.secret_key == "env-secret-123":
            print("  ✅ Inheritance working!")
        else:
            print("  ❌ Inheritance causing issues")

    except Exception as e:
        print(f"❌ Inheritance test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_minimal_config()
    test_inheritance_issue()
