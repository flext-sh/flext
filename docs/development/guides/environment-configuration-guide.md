# Environment Configuration Best Practices

> **Cross-References:**
>
> - [Development Standards](./standardization-plan.md) - Code quality standards and configuration management
> - [Oracle Integration Guide](../guides/oracle-integration-comprehensive-guide.md) - Oracle-specific environment setup
> - [Security Guidelines](../reference/security-policy.md) - Security best practices

## Overview

This guide establishes best practices for environment configuration management across the PyAuto workspace, with emphasis on security, flexibility, and maintainability. The approach eliminates hardcoded values and implements secure configuration patterns.

## Problems Addressed

### 1. Automatic Variable Export by IDEs

- **Issue**: VSCode/Cursor automatically loads `.env` files, exposing sensitive variables to all terminals
- **Solution**: Use `.env.local` files that are not automatically loaded

### 2. Hardcoded Values in Source Code

- **Issue**: Configuration values defined directly in source code violate security best practices
- **Solution**: All configuration comes exclusively from environment variables

### 3. Credential Exposure

- **Issue**: Sensitive information accidentally committed to version control
- **Solution**: Clear separation between templates and actual credentials

## Implementation Strategy

### 1. Environment File Hierarchy

```
Project Root/
├── .env.example          # Template with placeholder values
├── .env.local           # Local development (not auto-loaded)
├── .env.production      # Production configuration (encrypted/vault)
└── .env.test           # Test environment configuration
```

### 2. Configuration Loading Priority

```python
# Configuration loading order (highest to lowest priority)
from flx.core.config import ConfigLoader

config = ConfigLoader.load_with_priority([
    ".env.local",      # Local development (highest priority)
    ".env",            # Standard environment file
    "os.environ",      # System environment variables
    ".env.example"     # Template defaults (lowest priority)
])
```

### 3. Validation and Security

```python
from flx.core.config import ConfigValidator, RequiredConfig

class WMSConfig(RequiredConfig):
    """WMS configuration with validation."""

    wms_url: str
    wms_username: str
    wms_password: str
    wms_timeout: int = 30

    @classmethod
    def validate_required(cls) -> bool:
        """Validate all required configuration is present."""
        missing = []

        if not cls.wms_url:
            missing.append("WMS_URL")
        if not cls.wms_username:
            missing.append("WMS_USERNAME")
        if not cls.wms_password:
            missing.append("WMS_PASSWORD")

        if missing:
            raise ConfigurationError(
                f"Missing required configuration: {', '.join(missing)}"
            )
        return True
```

## Configuration Patterns

### 1. Oracle WMS Configuration

#### .env.example Template

```bash
# Oracle WMS Configuration Template
# Copy to .env.local and fill with actual values

# WMS Connection
WMS_URL=https://your-tenant.wms.ocs.oraclecloud.com/your_environment
WMS_USERNAME=your_username
WMS_PASSWORD=your_password
WMS_TIMEOUT=30

# Authentication
WMS_AUTH_TYPE=basic
WMS_CLIENT_ID=your_client_id
WMS_CLIENT_SECRET=your_client_secret

# Connection Pool
WMS_POOL_SIZE=10
WMS_POOL_MAX_OVERFLOW=20
WMS_POOL_TIMEOUT=30

# Logging
WMS_LOG_LEVEL=INFO
WMS_LOG_FORMAT=json
```

#### .env.local Example

```bash
# Local Development Configuration
# NEVER commit this file to version control

WMS_URL=https://dev-tenant.wms.ocs.oraclecloud.com/dev
WMS_USERNAME=dev_user
WMS_PASSWORD=SecureDevPassword123
WMS_TIMEOUT=60

WMS_AUTH_TYPE=oauth2
WMS_CLIENT_ID=dev_client_12345
WMS_CLIENT_SECRET=dev_secret_abcdef

WMS_POOL_SIZE=5
WMS_POOL_MAX_OVERFLOW=10
WMS_POOL_TIMEOUT=15

WMS_LOG_LEVEL=DEBUG
WMS_LOG_FORMAT=pretty
```

### 2. Database Configuration

#### PostgreSQL Configuration

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pyauto_dev
DB_USER=pyauto_user
DB_PASSWORD=SecureDbPassword123
DB_POOL_SIZE=20
DB_POOL_MAX_OVERFLOW=30
DB_SSL_MODE=prefer
```

#### Oracle Database Configuration

```bash
# Oracle Database Configuration
ORACLE_HOST=oracle-db.company.com
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=ORCL
ORACLE_USER=oracle_user
ORACLE_PASSWORD=SecureOraclePassword123
ORACLE_WALLET_PATH=/path/to/wallet
ORACLE_POOL_SIZE=15
```

### 3. API Integration Configuration

#### OAuth2 Configuration

```bash
# OAuth2 Authentication
OAUTH2_CLIENT_ID=your_client_id
OAUTH2_CLIENT_SECRET=your_client_secret
OAUTH2_TOKEN_URL=https://auth.oracle.com/oauth2/token
OAUTH2_SCOPE=wms.read,wms.write
OAUTH2_CACHE_TOKENS=true
```

#### JWT Configuration

```bash
# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Implementation Code

### 1. Configuration Class

```python
from dataclasses import dataclass
from typing import Optional
import os
from pathlib import Path

@dataclass
class EnvironmentConfig:
    """Environment configuration management."""

    # WMS Configuration
    wms_url: str
    wms_username: str
    wms_password: str
    wms_timeout: int = 30

    # Database Configuration
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "pyauto"
    db_user: str = ""
    db_password: str = ""

    # Security Configuration
    secret_key: str = ""
    jwt_algorithm: str = "HS256"

    @classmethod
    def from_environment(cls, env_file: Optional[str] = None) -> "EnvironmentConfig":
        """Load configuration from environment variables."""
        if env_file:
            cls._load_env_file(env_file)

        return cls(
            # WMS
            wms_url=os.getenv("WMS_URL", ""),
            wms_username=os.getenv("WMS_USERNAME", ""),
            wms_password=os.getenv("WMS_PASSWORD", ""),
            wms_timeout=int(os.getenv("WMS_TIMEOUT", "30")),

            # Database
            db_host=os.getenv("DB_HOST", "localhost"),
            db_port=int(os.getenv("DB_PORT", "5432")),
            db_name=os.getenv("DB_NAME", "pyauto"),
            db_user=os.getenv("DB_USER", ""),
            db_password=os.getenv("DB_PASSWORD", ""),

            # Security
            secret_key=os.getenv("SECRET_KEY", ""),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        )

    @staticmethod
    def _load_env_file(env_file: str) -> None:
        """Load environment variables from file."""
        env_path = Path(env_file)
        if not env_path.exists():
            raise FileNotFoundError(f"Environment file not found: {env_file}")

        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key] = value

    def validate(self) -> None:
        """Validate required configuration."""
        required_fields = [
            ("WMS_URL", self.wms_url),
            ("WMS_USERNAME", self.wms_username),
            ("WMS_PASSWORD", self.wms_password),
            ("SECRET_KEY", self.secret_key),
        ]

        missing = [field for field, value in required_fields if not value]

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
```

### 2. Configuration Factory

```python
from typing import Union
from pathlib import Path

class ConfigurationFactory:
    """Factory for creating environment-specific configurations."""

    @staticmethod
    def create_config(environment: str = "development") -> EnvironmentConfig:
        """Create configuration for specific environment."""
        env_files = {
            "development": [".env.local", ".env.development", ".env"],
            "testing": [".env.test", ".env"],
            "staging": [".env.staging", ".env"],
            "production": [".env.production", ".env"],
        }

        config = None
        for env_file in env_files.get(environment, [".env"]):
            if Path(env_file).exists():
                config = EnvironmentConfig.from_environment(env_file)
                break

        if config is None:
            config = EnvironmentConfig.from_environment()

        config.validate()
        return config
```

### 3. Secure Configuration Loading

```python
import keyring
from cryptography.fernet import Fernet
import base64

class SecureConfigLoader:
    """Secure configuration loading with encryption support."""

    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())

    def load_encrypted_config(self, config_file: str) -> dict[str, str]:
        """Load encrypted configuration file."""
        config = {}

        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, encrypted_value = line.split("=", 1)

                    # Decrypt value if cipher is available
                    if self.cipher and encrypted_value.startswith("encrypted:"):
                        encrypted_data = encrypted_value[10:]  # Remove "encrypted:" prefix
                        decrypted_value = self.cipher.decrypt(
                            base64.b64decode(encrypted_data)
                        ).decode()
                        config[key] = decrypted_value
                    else:
                        config[key] = encrypted_value

        return config

    def store_in_keyring(self, service: str, username: str, password: str) -> None:
        """Store credentials in system keyring."""
        keyring.set_password(service, username, password)

    def get_from_keyring(self, service: str, username: str) -> Optional[str]:
        """Retrieve credentials from system keyring."""
        return keyring.get_password(service, username)
```

## Development Workflow

### 1. Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd pyauto

# Copy environment template
cp .env.example .env.local

# Edit with your credentials
nano .env.local

# Test configuration
python -m scripts.test_env_vars
```

### 2. Testing Configuration

```python
#!/usr/bin/env python3
"""Test environment variable configuration."""

import os
from src.config import EnvironmentConfig

def test_environment_config():
    """Test that all required environment variables are set."""
    try:
        config = EnvironmentConfig.from_environment(".env.local")
        config.validate()
        print("✅ Configuration validation passed")

        # Test connections
        print("🔍 Testing connections...")
        test_wms_connection(config)
        test_database_connection(config)

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

    return True

def test_wms_connection(config: EnvironmentConfig) -> bool:
    """Test WMS connection with configuration."""
    from src.adapters.wms import WMSAdapter

    try:
        wms = WMSAdapter(
            url=config.wms_url,
            username=config.wms_username,
            password=config.wms_password,
            timeout=config.wms_timeout
        )

        if wms.test_connection():
            print("✅ WMS connection successful")
            return True
        else:
            print("❌ WMS connection failed")
            return False
    except Exception as e:
        print(f"❌ WMS connection error: {e}")
        return False

if __name__ == "__main__":
    test_environment_config()
```

### 3. IDE Configuration

#### VSCode Settings

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.envFile": "${workspaceFolder}/.env.local",
  "python.terminal.activateEnvironment": true,
  "files.exclude": {
    ".env.local": true,
    ".env.production": true,
    ".env.staging": true
  }
}
```

#### .gitignore Configuration

```gitignore
# Environment files with credentials
.env.local
.env.production
.env.staging
.env.development

# Keep templates
!.env.example
!.env.template

# IDE specific
.vscode/settings.json
```

## Security Best Practices

### 1. Credential Management

**Never Store in Code:**

```python
# ❌ BAD - Hardcoded credentials
WMS_URL = "https://prod.wms.oracle.com"
WMS_PASSWORD = "hardcoded_password"

# ✅ GOOD - From environment
WMS_URL = os.getenv("WMS_URL")
WMS_PASSWORD = os.getenv("WMS_PASSWORD")
```

**Use Secure Storage:**

```python
# ✅ GOOD - Use keyring for local development
import keyring

def get_secure_password(service: str, username: str) -> str:
    """Get password from secure keyring storage."""
    password = keyring.get_password(service, username)
    if not password:
        password = input(f"Enter password for {username}@{service}: ")
        keyring.set_password(service, username, password)
    return password
```

### 2. Environment Isolation

**Separate Configurations:**

```python
# Different configs for different environments
class ConfigFactory:
    """Configuration factory with environment isolation."""

    @staticmethod
    def get_config() -> EnvironmentConfig:
        environment = os.getenv("ENVIRONMENT", "development")

        config_files = {
            "development": ".env.local",
            "testing": ".env.test",
            "staging": ".env.staging",
            "production": ".env.production"
        }

        config_file = config_files.get(environment, ".env.local")
        return EnvironmentConfig.from_environment(config_file)
```

### 3. Encryption for Sensitive Data

```python
# Encrypt sensitive configuration values
from cryptography.fernet import Fernet

def encrypt_config_value(value: str, key: str) -> str:
    """Encrypt a configuration value."""
    cipher = Fernet(key.encode())
    encrypted = cipher.encrypt(value.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_config_value(encrypted_value: str, key: str) -> str:
    """Decrypt a configuration value."""
    cipher = Fernet(key.encode())
    decrypted = cipher.decrypt(base64.b64decode(encrypted_value))
    return decrypted.decode()
```

## Monitoring and Validation

### 1. Configuration Health Checks

```python
from flx.adapters.health import HealthCheck

class ConfigurationHealthCheck(HealthCheck):
    """Health check for configuration validation."""

    def check_health(self) -> HealthStatus:
        """Check configuration health."""
        try:
            config = ConfigurationFactory.create_config()
            config.validate()

            # Test critical connections
            wms_healthy = self._test_wms_connection(config)
            db_healthy = self._test_database_connection(config)

            if wms_healthy and db_healthy:
                return HealthStatus.HEALTHY
            else:
                return HealthStatus.DEGRADED

        except Exception as e:
            return HealthStatus.UNHEALTHY
```

### 2. Configuration Auditing

```python
import logging
from datetime import datetime

class ConfigurationAuditor:
    """Audit configuration access and changes."""

    def __init__(self):
        self.logger = logging.getLogger("config.audit")

    def log_config_access(self, config_key: str, source: str) -> None:
        """Log configuration value access."""
        self.logger.info(
            "Configuration accessed",
            extra={
                "config_key": config_key,
                "source": source,
                "timestamp": datetime.utcnow().isoformat(),
                "masked_value": self._mask_sensitive(config_key)
            }
        )

    def _mask_sensitive(self, key: str) -> str:
        """Mask sensitive configuration keys."""
        sensitive_keys = ["password", "secret", "key", "token"]

        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            return "***MASKED***"
        return "logged"
```

## Related Documentation

### Development Standards

- [Development Standards](./standardization-plan.md) - Complete development standards
- [Security Guidelines](../reference/security-policy.md) - Security best practices

### Integration Guides

- [Oracle Integration Guide](../guides/oracle-integration-comprehensive-guide.md) - Oracle-specific configuration
- [Database Integration](../guides/database-integration.md) - Database configuration patterns

### Operations

- [Deployment Guide](../operations/deployment-guide.md) - Production configuration management
- [Monitoring Guide](../operations/monitoring-guide.md) - Configuration monitoring

---

**Configuration Status**: ✅ Secure and Standardized
**Security Level**: Production-Ready
**Validation**: Automated health checks
**Best Practices**: Fully implemented
