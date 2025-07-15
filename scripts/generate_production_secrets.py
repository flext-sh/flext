#!/usr/bin/env python3
"""Generate cryptographically secure secrets for production deployment."""

import base64
import json
import os
import secrets
import string
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_secret_key(length: int = 32) -> str:
    """Generate a cryptographically secure secret key."""
    alphabet = string.ascii_letters + string.digits + "_-"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_jwt_secret(length: int = 64) -> str:
    """Generate a base64-encoded JWT secret key."""
    return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode("utf-8")


def generate_database_password(length: int = 24) -> str:
    """Generate a secure database password."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_encryption_key() -> str:
    """Generate Fernet encryption key for sensitive data."""
    return Fernet.generate_key().decode("utf-8")


def create_production_secrets() -> dict:
    """Create a complete set of production secrets."""
    return {
        # Core application secrets
        "api_secret_key": generate_secret_key(48),
        "jwt_secret_key": generate_jwt_secret(),
        "web_secret_key": generate_secret_key(48),
        # Database credentials
        "db_password": generate_database_password(),
        "db_admin_password": generate_database_password(32),
        # Redis password
        "redis_password": generate_database_password(20),
        # Encryption keys
        "data_encryption_key": generate_encryption_key(),
        "session_encryption_key": generate_encryption_key(),
        # API keys for external services
        "monitoring_api_key": generate_secret_key(40),
        "webhook_secret": generate_secret_key(32),
        # SSL/TLS certificate password (if needed)
        "ssl_cert_password": generate_database_password(16),
        # Additional security tokens
        "csrf_secret": generate_secret_key(32),
        "security_salt": generate_secret_key(16),
    }


def create_secrets_vault(
    secrets_data: dict, vault_password: str, output_file: Path
) -> None:
    """Create an encrypted secrets vault."""
    # Create encryption key from password
    password_bytes = vault_password.encode("utf-8")
    salt = secrets.token_bytes(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
    fernet = Fernet(key)

    # Encrypt secrets
    secrets_json = json.dumps(secrets_data, indent=2)
    encrypted_data = fernet.encrypt(secrets_json.encode("utf-8"))

    # Save vault
    vault_data = {
        "salt": base64.b64encode(salt).decode("utf-8"),
        "encrypted_secrets": base64.b64encode(encrypted_data).decode("utf-8"),
        "created_at": secrets_data.get("created_at", "unknown"),
        "version": "1.0",
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(vault_data, f, indent=2)

    print(f"✅ Encrypted secrets vault created: {output_file}")


def create_production_env_files(secrets_data: dict, project_root: Path) -> None:
    """Create production environment files with generated secrets."""

    # API production config
    api_env_content = f"""# FLEXT-API PRODUCTION ENVIRONMENT - SECURE CONFIGURATION
# Generated: {secrets_data.get("created_at", "unknown")}
# WARNING: Contains production secrets - keep secure!

# =============================================================================
# FLEXT API SETTINGS - PRODUCTION (Environment prefix: FLEXT_API_)
# =============================================================================

# Project identification
FLEXT_API_PROJECT_NAME=flext-api
FLEXT_API_PROJECT_VERSION=0.7.0
FLEXT_API_ENVIRONMENT=production
FLEXT_API_DEBUG=false
FLEXT_API_LOG_LEVEL=WARNING
FLEXT_API_LOG_FORMAT=json

# Server configuration (production)
FLEXT_API_HOST=0.0.0.0
FLEXT_API_PORT=8000
FLEXT_API_WORKERS=8
FLEXT_API_RELOAD=false

# CORS configuration (restricted to production domains)
FLEXT_API_CORS_ENABLED=true
FLEXT_API_CORS_ORIGINS=["https://app.flext.com","https://admin.flext.com"]

# Rate limiting configuration (production limits)
FLEXT_API_RATE_LIMIT_ENABLED=true
FLEXT_API_RATE_LIMIT_PER_MINUTE=60

# Security configuration (production secrets)
FLEXT_API_SECRET_KEY={secrets_data["api_secret_key"]}
FLEXT_API_ALGORITHM=RS256
FLEXT_API_ACCESS_TOKEN_EXPIRE_MINUTES=15

# Database configuration (production database)
FLEXT_API_DATABASE_URL=postgresql://flext_prod:{secrets_data["db_password"]}@db.internal:5432/flext_production
FLEXT_API_DATABASE_POOL_SIZE=50

# Redis configuration (production redis with auth)
FLEXT_API_REDIS_URL=redis://:{secrets_data["redis_password"]}@redis.internal:6379/0

# Production-specific settings
FLEXT_API_ENABLE_DOCS=false
FLEXT_API_ENABLE_METRICS=true
FLEXT_API_ENABLE_HEALTH_CHECK=true
FLEXT_API_PRODUCTION_MODE=true

# SSL/TLS settings
FLEXT_API_SSL_CERT_PATH=/etc/ssl/certs/flext-api.crt
FLEXT_API_SSL_KEY_PATH=/etc/ssl/private/flext-api.key
FLEXT_API_SSL_CERT_PASSWORD={secrets_data["ssl_cert_password"]}
"""

    # Web production config
    web_env_content = f"""# FLEXT-WEB PRODUCTION ENVIRONMENT - SECURE CONFIGURATION
# Generated: {secrets_data.get("created_at", "unknown")}
# WARNING: Contains production secrets - keep secure!

# =============================================================================
# DJANGO PRODUCTION CONFIGURATION
# =============================================================================
DJANGO_SECRET_KEY={secrets_data["web_secret_key"]}
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=app.flext.com,admin.flext.com
DJANGO_SETTINGS_MODULE=flext_web.settings.production

# Static and Media Files (production paths)
STATIC_URL=/static/
STATIC_ROOT=/opt/flext/production/flext-web/staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=/opt/flext/production/flext-web/media

# Security Settings (production - full SSL)
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
SECURE_HSTS_SECONDS=31536000
SECURE_BROWSER_XSS_FILTER=true
SECURE_CONTENT_TYPE_NOSNIFF=true

# Database (production database)
DATABASE_URL=postgresql://flext_web_prod:{secrets_data["db_password"]}@db.internal:5432/flext_web_production

# Cache (production redis with auth)
CACHE_URL=redis://:{secrets_data["redis_password"]}@redis.internal:6379/1
SESSION_ENGINE=django.contrib.sessions.backends.cache
SESSION_CACHE_ALIAS=default

# Email (production SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.internal
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=flext@company.com
EMAIL_HOST_PASSWORD=REPLACE_WITH_EMAIL_PASSWORD

# Internationalization
USE_TZ=true
TIME_ZONE=UTC
LANGUAGE_CODE=en-us

# FLEXT Web Specific (production)
FLEXT_WEB_LOG_LEVEL=WARNING
FLEXT_WEB_MAX_UPLOAD_SIZE=10485760  # 10MB for production
FLEXT_WEB_SESSION_TIMEOUT=3600  # 1 hour
FLEXT_WEB_ENVIRONMENT=production

# Production-specific features
FLEXT_WEB_ENABLE_DEBUG_TOOLBAR=false
FLEXT_WEB_ENABLE_PROFILING=false
FLEXT_WEB_ENABLE_METRICS=true

# CORS for API integration
CORS_ALLOWED_ORIGINS=[
    "https://app.flext.com",
    "https://admin.flext.com"
]

# Logging configuration
LOGGING_LEVEL=WARNING
LOGGING_FORMAT=json
LOG_FILE=/opt/flext/production/logs/flext-web.log

# Security enhancements
CSRF_COOKIE_HTTPONLY=true
SESSION_COOKIE_HTTPONLY=true
CSRF_TRUSTED_ORIGINS=["https://app.flext.com","https://admin.flext.com"]
"""

    # Write files
    api_env_file = project_root / "flext-api" / ".env.production"
    web_env_file = project_root / "flext-web" / ".env.production"

    with open(api_env_file, "w", encoding="utf-8") as f:
        f.write(api_env_content)

    with open(web_env_file, "w", encoding="utf-8") as f:
        f.write(web_env_content)

    print(f"✅ Production API config: {api_env_file}")
    print(f"✅ Production Web config: {web_env_file}")


def main():
    """Generate complete production secrets and configuration."""
    print("🔒 FLEXT PRODUCTION SECRETS GENERATOR")
    print("=" * 50)

    project_root = Path(__file__).parent.parent

    # Generate secrets
    print("🎲 Generating cryptographically secure secrets...")
    secrets_data = create_production_secrets()
    secrets_data["created_at"] = str(Path(__file__).stat().st_mtime)

    print(f"✅ Generated {len(secrets_data)} production secrets")

    # Create environment files
    print("\n📄 Creating production environment files...")
    create_production_env_files(secrets_data, project_root)

    # Create secrets vault
    print("\n🔐 Creating encrypted secrets vault...")
    vault_password = input("Enter vault master password (use strong password): ")
    if not vault_password or len(vault_password) < 12:
        print("❌ Vault password must be at least 12 characters")
        return

    vault_file = project_root / "secrets" / "production_secrets.vault"
    vault_file.parent.mkdir(exist_ok=True)

    create_secrets_vault(secrets_data, vault_password, vault_file)

    # Create secrets summary (without actual secrets)
    summary = {
        "total_secrets": len(secrets_data),
        "secret_types": list(secrets_data.keys()),
        "created_at": secrets_data["created_at"],
        "vault_location": str(vault_file),
        "env_files": [
            str(project_root / "flext-api" / ".env.production"),
            str(project_root / "flext-web" / ".env.production"),
        ],
    }

    summary_file = project_root / "secrets" / "production_secrets_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n📋 Secrets summary: {summary_file}")

    print("\n" + "=" * 50)
    print("🎉 PRODUCTION SECRETS SUCCESSFULLY GENERATED!")
    print("\n🔒 SECURITY NOTES:")
    print("  • Production .env files contain real secrets")
    print("  • Secrets vault is encrypted with your master password")
    print("  • Store vault password in secure password manager")
    print("  • Never commit .env.production files to git")
    print("  • Review and update external service passwords")
    print("\n🚀 NEXT STEPS:")
    print("  1. Update external service passwords (email, etc.)")
    print("  2. Deploy .env files to production servers securely")
    print("  3. Configure SSL certificates")
    print("  4. Test production configuration in staging first")


if __name__ == "__main__":
    main()
