#!/usr/bin/env python3
"""Debug the proper format for pydantic-settings aliases."""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "flext-core" / "src"))
sys.path.insert(0, str(project_root / "flext-api" / "src"))


def test_proper_format():
    """Test the proper environment variable format."""
    print("🔍 TESTING PROPER PYDANTIC-SETTINGS ALIAS FORMAT...")

    # Clear existing test variables
    for key in list(os.environ.keys()):
        if key.startswith("FLEXT_API_"):
            del os.environ[key]

    # Test format: FLEXT_API_ + alias (not field name)
    test_vars = {
        "FLEXT_API_SECURITY__SECRET_KEY": "test-secret-key-456",
        "FLEXT_API_SERVER__HOST": "10.0.0.1",
        "FLEXT_API_SERVER__WORKERS": "12",
    }

    print("Setting test environment variables (alias format):")
    for key, value in test_vars.items():
        os.environ[key] = value
        print(f"  {key} = {value}")

    from flext_api.config import APIConfig

    try:
        config = APIConfig()

        print("\n📋 CONFIGURATION VALUES:")
        print(f"  secret_key: {config.secret_key}")
        print(f"  host: {config.host}")
        print(f"  workers: {config.workers}")

        # Check if values match
        print("\n🔍 RESULTS:")
        if config.secret_key == test_vars["FLEXT_API_SECURITY__SECRET_KEY"]:
            print("  ✅ secret_key working with alias")
        else:
            print(f"  ❌ secret_key failed: got '{config.secret_key}'")

        if config.host == test_vars["FLEXT_API_SERVER__HOST"]:
            print("  ✅ host working with alias")
        else:
            print(f"  ❌ host failed: got '{config.host}'")

        if config.workers == int(test_vars["FLEXT_API_SERVER__WORKERS"]):
            print("  ✅ workers working with alias")
        else:
            print(f"  ❌ workers failed: got {config.workers}")

        print("\n🔧 TESTING ALTERNATIVE FORMAT...")

        # Clear and try alternative format
        for key in list(os.environ.keys()):
            if key.startswith("FLEXT_API_"):
                del os.environ[key]

        # Test direct field names
        alt_vars = {
            "FLEXT_API_SECRET_KEY": "alt-secret-key-789",
            "FLEXT_API_HOST": "172.16.0.1",
            "FLEXT_API_WORKERS": "16",
        }

        print("Setting alternative format (direct field names):")
        for key, value in alt_vars.items():
            os.environ[key] = value
            print(f"  {key} = {value}")

        config2 = APIConfig()

        print("\n📋 ALTERNATIVE CONFIGURATION:")
        print(f"  secret_key: {config2.secret_key}")
        print(f"  host: {config2.host}")
        print(f"  workers: {config2.workers}")

        if config2.secret_key == alt_vars["FLEXT_API_SECRET_KEY"]:
            print("  ✅ secret_key working with direct field name")
        else:
            print("  ❌ secret_key failed with direct field name")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_proper_format()
