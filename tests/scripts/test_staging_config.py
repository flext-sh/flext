#!/usr/bin/env python3
"""Test staging configuration functionality."""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "flext-core" / "src"))
sys.path.insert(0, str(project_root / "flext-api" / "src"))


def test_staging_configuration():
    """Test that staging configurations load properly and are secure."""
    print("🔍 TESTING STAGING CONFIGURATION SECURITY...")

    # Set environment to use staging config
    staging_env_file = project_root / "flext-api" / ".env.staging"

    # Import after setting path
    from flext_api.config import APIConfig

    try:
        # Load staging configuration
        staging_config = APIConfig(_env_file=str(staging_env_file))

        print("✅ Staging configuration loaded successfully")
        print(f"  📋 Project: {staging_config.project_name}")
        print(f"  🌍 Environment: {getattr(staging_config, 'environment', 'test')}")
        print(f"  🐛 Debug: {staging_config.debug}")
        print(f"  🌐 Host: {staging_config.host}:{staging_config.port}")
        print(f"  👥 Workers: {staging_config.workers}")
        print(f"  🔄 Reload: {staging_config.reload}")
        print(f"  🔒 Secret Key: {staging_config.secret_key[:8]}...")
        print(f"  ⏱️ Token Expire: {staging_config.access_token_expire_minutes}min")
        print(f"  🚦 Rate Limit: {staging_config.rate_limit_per_minute}/min")

        # Security validation
        security_issues = []
        security_ok = []

        # Check debug mode
        if staging_config.debug:
            security_issues.append("Debug mode is enabled")
        else:
            security_ok.append("Debug mode properly disabled")

        # Check secret key
        if (
            "change" in staging_config.secret_key.lower()
            or "development" in staging_config.secret_key.lower()
        ):
            security_issues.append("Using development/changeable secret key")
        else:
            security_ok.append("Secret key is properly configured")

        # Check CORS
        cors_origins = getattr(staging_config, "cors_origins", [])
        if any("localhost" in origin for origin in cors_origins):
            security_issues.append("CORS contains localhost references")
        else:
            security_ok.append("CORS properly restricted")

        # Check workers
        if staging_config.reload:
            security_issues.append("Auto-reload enabled (development setting)")
        else:
            security_ok.append("Auto-reload disabled (production setting)")

        # Print security assessment
        print("\n🛡️ SECURITY ASSESSMENT:")
        print(f"✅ Security OK ({len(security_ok)}):")
        for item in security_ok:
            print(f"  ✅ {item}")

        if security_issues:
            print(f"\n⚠️ Security Issues ({len(security_issues)}):")
            for issue in security_issues:
                print(f"  ⚠️ {issue}")
        else:
            print("\n🎉 NO SECURITY ISSUES FOUND!")

        # Test database connection string
        db_url = staging_config.database_url
        if "localhost" in db_url:
            print(f"📊 Database: {db_url} (localhost - staging OK)")
        else:
            print("📊 Database: configured for external host")

        # Test Redis connection
        redis_url = staging_config.redis_url
        if "localhost" in redis_url:
            print(f"🔴 Redis: {redis_url} (localhost - staging OK)")
        else:
            print("🔴 Redis: configured for external host")

        return len(security_issues) == 0

    except Exception as e:
        print(f"❌ Failed to load staging configuration: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_environment_variables():
    """Test that environment variables are properly loaded."""
    print("\n🔍 TESTING ENVIRONMENT VARIABLE LOADING...")

    staging_env_file = project_root / "flext-api" / ".env.staging"

    # Read the .env.staging file manually to verify content
    if staging_env_file.exists():
        print(f"✅ Staging env file exists: {staging_env_file}")

        with open(staging_env_file, encoding="utf-8") as f:
            content = f.read()

        # Check for key configurations
        checks = {
            "FLEXT_API_ENVIRONMENT=staging": "Environment set to staging",
            "FLEXT_API_DEBUG=false": "Debug disabled",
            "FLEXT_API_SERVER__WORKERS=4": "Production workers configured",
            "FLEXT_API_CORS__ALLOW_ORIGINS": "CORS origins configured",
            "FLEXT_API_SECURITY__SECRET_KEY": "Security secret configured",
        }

        for check, description in checks.items():
            if check in content:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ Missing: {description}")

    else:
        print(f"❌ Staging env file not found: {staging_env_file}")
        return False

    return True


if __name__ == "__main__":
    print("🚀 FLEXT STAGING CONFIGURATION TEST")
    print("=" * 50)

    # Test environment variable loading
    env_test = test_environment_variables()

    # Test configuration loading
    config_test = test_staging_configuration()

    print("\n" + "=" * 50)
    if env_test and config_test:
        print("🎉 ALL STAGING CONFIGURATION TESTS PASSED!")
        sys.exit(0)
    else:
        print("❌ STAGING CONFIGURATION TESTS FAILED!")
        sys.exit(1)
