#!/usr/bin/env python3
"""Debug pydantic-settings field aliases for staging configuration."""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "flext-core" / "src"))
sys.path.insert(0, str(project_root / "flext-api" / "src"))


def debug_aliases():
    """Debug field aliases and environment variable loading."""
    print("🔍 DEBUGGING PYDANTIC-SETTINGS ALIASES...")

    # Manually set a few test environment variables
    test_vars = {
        "FLEXT_API_SECURITY__SECRET_KEY": "test-secret-key-123",
        "FLEXT_API_SERVER__HOST": "192.168.1.100",
        "FLEXT_API_SERVER__WORKERS": "8",
        "FLEXT_API_CORS__ALLOW_ORIGINS": '["https://test1.com","https://test2.com"]',
    }

    print("Setting test environment variables:")
    for key, value in test_vars.items():
        os.environ[key] = value
        print(f"  {key} = {value}")

    # Import and test configuration
    from flext_api.config import APIConfig

    try:
        config = APIConfig()

        print("\n📋 CONFIGURATION VALUES:")
        print(f"  secret_key: {config.secret_key}")
        print(f"  host: {config.host}")
        print(f"  workers: {config.workers}")
        print(f"  cors_origins: {config.cors_origins}")

        # Check if values match what we set
        print("\n🔍 ALIAS VALIDATION:")
        if config.secret_key == test_vars["FLEXT_API_SECURITY__SECRET_KEY"]:
            print("  ✅ secret_key alias working")
        else:
            print(
                f"  ❌ secret_key alias failed: got '{config.secret_key}', expected '{test_vars['FLEXT_API_SECURITY__SECRET_KEY']}'",
            )

        if config.host == test_vars["FLEXT_API_SERVER__HOST"]:
            print("  ✅ host alias working")
        else:
            print(
                f"  ❌ host alias failed: got '{config.host}', expected '{test_vars['FLEXT_API_SERVER__HOST']}'",
            )

        if config.workers == int(test_vars["FLEXT_API_SERVER__WORKERS"]):
            print("  ✅ workers alias working")
        else:
            print(
                f"  ❌ workers alias failed: got {config.workers}, expected {test_vars['FLEXT_API_SERVER__WORKERS']}",
            )

        # Test pydantic-settings debug
        print("\n🔧 PYDANTIC-SETTINGS DEBUG INFO:")
        print(f"  Model config: {config.model_config}")

        # Check what pydantic thinks about field sources
        try:
            print(f"  Model fields: {list(config.model_fields.keys())}")
            for field_name, field_info in config.model_fields.items():
                if hasattr(field_info, "alias"):
                    print(f"    {field_name}: alias={field_info.alias}")
        except Exception as e:
            print(f"  Field info error: {e}")

    except Exception as e:
        print(f"❌ Configuration creation failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_aliases()
