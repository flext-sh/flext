#!/usr/bin/env python3
"""Load and test staging configuration with proper environment variable mapping."""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "flext-core" / "src"))
sys.path.insert(0, str(project_root / "flext-api" / "src"))


def load_staging_environment():
    """Manually load staging environment variables."""
    staging_env_file = project_root / "flext-api" / ".env.staging"

    if not staging_env_file.exists():
        print(f"❌ Staging env file not found: {staging_env_file}")
        return False

    print(f"📄 Loading environment from: {staging_env_file}")

    # Parse .env file manually
    env_vars = {}
    with open(staging_env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]

                env_vars[key] = value
                os.environ[key] = value

    print(f"✅ Loaded {len(env_vars)} environment variables")

    # Print key staging variables
    key_vars = [
        "FLEXT_API_ENVIRONMENT",
        "FLEXT_API_DEBUG",
        "FLEXT_API_SECURITY__SECRET_KEY",
        "FLEXT_API_CORS__ALLOW_ORIGINS",
        "FLEXT_API_SERVER__WORKERS",
    ]

    print("\n🔍 KEY STAGING VARIABLES:")
    for var in key_vars:
        if var in env_vars:
            if "SECRET" in var:
                print(f"  ✅ {var}: {env_vars[var][:8]}...")
            else:
                print(f"  ✅ {var}: {env_vars[var]}")
        else:
            print(f"  ❌ {var}: NOT SET")

    return True


def test_configuration_with_staging_env():
    """Test configuration loading with staging environment variables."""
    from flext_api.config import APIConfig

    print("\n🧪 TESTING CONFIGURATION WITH STAGING ENVIRONMENT...")

    try:
        # Create configuration instance
        config = APIConfig()

        print("✅ Configuration loaded successfully")
        print(f"  📋 Project: {config.project_name}")
        print(f"  🌍 Environment: {getattr(config, 'environment', 'test')}")
        print(f"  🐛 Debug: {config.debug}")
        print(f"  🌐 Host: {config.host}:{config.port}")
        print(f"  👥 Workers: {config.workers}")
        print(f"  🔄 Reload: {config.reload}")
        print(f"  🔒 Secret Key: {config.secret_key[:8]}...")
        print(f"  ⏱️ Token Expire: {config.access_token_expire_minutes}min")
        print(f"  🚦 Rate Limit: {config.rate_limit_per_minute}/min")
        print(f"  🌐 CORS Origins: {getattr(config, 'cors_origins', 'not set')}")

        # Validate staging configuration
        staging_valid = True
        issues = []

        if config.debug:
            issues.append("Debug mode is enabled")
            staging_valid = False

        if config.reload:
            issues.append("Auto-reload is enabled")
            staging_valid = False

        if "change" in config.secret_key.lower():
            issues.append("Default secret key detected")
            staging_valid = False

        if staging_valid:
            print("\n🎉 STAGING CONFIGURATION IS VALID!")
        else:
            print(f"\n⚠️ STAGING CONFIGURATION ISSUES ({len(issues)}):")
            for issue in issues:
                print(f"  ⚠️ {issue}")

        return staging_valid

    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 FLEXT STAGING CONFIGURATION LOADER")
    print("=" * 50)

    # Load staging environment
    env_loaded = load_staging_environment()

    if env_loaded:
        # Test configuration
        config_valid = test_configuration_with_staging_env()

        print("\n" + "=" * 50)
        if config_valid:
            print("🎉 STAGING CONFIGURATION SUCCESSFULLY LOADED AND VALIDATED!")
            sys.exit(0)
        else:
            print("⚠️ STAGING CONFIGURATION LOADED BUT HAS ISSUES")
            sys.exit(1)
    else:
        print("\n" + "=" * 50)
        print("❌ FAILED TO LOAD STAGING ENVIRONMENT")
        sys.exit(1)
