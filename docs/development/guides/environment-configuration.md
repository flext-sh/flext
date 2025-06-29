# Environment Configuration Guide - Development

> **Function**: Comprehensive environment configuration for FLX Framework | **Audience**: Developers, DevOps engineers | **Status**: ✅ Production Ready

[![Configuration](https://img.shields.io/badge/configuration-secure-green.svg)](#security-best-practices)
[![Environment](https://img.shields.io/badge/environment-automated-blue.svg)](#configuration-strategy)
[![Security](https://img.shields.io/badge/security-enterprise-red.svg)](#security-best-practices)

Enterprise-grade environment configuration guide for FLX Framework 0.4.0+ emphasizing security best practices and flexible configuration management

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Development](../index.md) → **📂 Guides**: [Guides Hub](./index.md) → **📄 Current**: Environment Configuration

### **📍 Learning Path Position**

```
[Development Hub](../index.md) → [Guides Hub](./index.md) → **[ENVIRONMENT CONFIG]** → [Development Tools](../tools/index.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Guides Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔧 Next Step**: [Schema Management](./schema-management-guide.md)

---

## 📋 **Overview**

This guide provides comprehensive environment configuration management for FLX Framework and Oracle WMS integration projects, emphasizing security best practices and flexible configuration management.

## Problems Addressed

### 1. Automatic Variable Export by IDEs

**Issue**: VSCode/Cursor automatically loaded `.env` files, exposing sensitive variables to all terminal sessions.

**Solution**: Implemented selective environment loading using `.env.local` files that are not automatically processed by IDEs.

### 2. Hardcoded Values in Source Code

**Issue**: Configuration values were defined directly in source code, violating security and configuration best practices.

**Solution**: Removed all hardcoded values and implemented environment-based configuration with validation.

## Configuration Strategy

### 1. Environment File Hierarchy

```bash
# Configuration file priority (highest to lowest)
.env.local          # Local development (not auto-loaded by IDEs)
.env.development    # Development environment defaults
.env.staging        # Staging environment configuration
.env.production     # Production environment configuration
.env.example        # Template file with no sensitive values
```

### 2. Security-First Approach

```python
# ✅ Secure configuration pattern
class WmsConfig:
    """WMS configuration using environment variables only."""

    def __init__(self):
        # No default values for sensitive configuration
        self.wms_url = os.getenv("WMS_URL")
        self.wms_username = os.getenv("WMS_USERNAME")
        self.wms_password = os.getenv("WMS_PASSWORD")

        # Validate required configuration
        self._validate_required_config()

    def _validate_required_config(self) -> None:
        """Validate that all required configuration is present."""
        required_vars = {
            "WMS_URL": self.wms_url,
            "WMS_USERNAME": self.wms_username,
            "WMS_PASSWORD": self.wms_password
        }

        missing_vars = [var for var, value in required_vars.items() if not value]

        if missing_vars:
            raise ConfigurationError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

# ❌ Insecure pattern (hardcoded values)
class WmsConfig:
    def __init__(self):
        self.wms_url = "https://default-tenant.wms.oraclecloud.com"  # ❌ Hardcoded
        self.wms_username = "default_user"  # ❌ Security risk
        self.wms_password = "default_password"  # ❌ Major security risk
```

### 3. Configuration Loading Implementation

```python
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class ConfigurationManager:
    """Manage environment configuration with security best practices."""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.cwd()
        self.loaded_files: list[str] = []
        self._load_environment_files()

    def _load_environment_files(self) -> None:
        """Load environment files in priority order."""
        env_files = [
            ".env.local",
            f".env.{os.getenv('ENVIRONMENT', 'development')}",
            ".env"
        ]

        for env_file in env_files:
            env_path = self.config_dir / env_file
            if env_path.exists():
                load_dotenv(env_path, override=True)
                self.loaded_files.append(str(env_path))
                break  # Load only the first found file

    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary without exposing sensitive values."""
        return {
            "loaded_files": self.loaded_files,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "config_sources": self._get_config_sources(),
            "validation_status": self._validate_all_configs()
        }

    def _get_config_sources(self) -> Dict[str, str]:
        """Map configuration keys to their sources."""
        config_sources = {}

        for key in os.environ:
            if any(prefix in key for prefix in ["WMS_", "DB_", "API_", "FLX_"]):
                config_sources[key] = "environment"

        return config_sources

    def _validate_all_configs(self) -> Dict[str, bool]:
        """Validate all configuration without exposing values."""
        validations = {}

        # WMS Configuration
        wms_required = ["WMS_URL", "WMS_USERNAME", "WMS_PASSWORD"]
        validations["wms"] = all(os.getenv(var) for var in wms_required)

        # Database Configuration
        db_required = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
        validations["database"] = all(os.getenv(var) for var in db_required)

        # API Configuration
        api_required = ["API_KEY", "API_SECRET"]
        validations["api"] = all(os.getenv(var) for var in api_required)

        return validations
```

## Configuration Templates

### .env.example Template

```bash
# WMS Configuration
WMS_URL=https://your-tenant.wms.ocs.oraclecloud.com/your_environment
WMS_USERNAME=your_username
WMS_PASSWORD=your_password
WMS_TIMEOUT=30
WMS_MAX_RETRIES=3

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wms_integration
DB_USER=wms_user
DB_PASSWORD=secure_password
DB_SSL_MODE=require

# API Configuration
API_KEY=your_api_key
API_SECRET=your_api_secret
API_BASE_URL=https://api.example.com/v1
API_TIMEOUT=60

# FLX Framework Configuration
FLX_LOG_LEVEL=INFO
FLX_ENVIRONMENT=development
FLX_DEBUG_MODE=false
FLX_METRICS_ENABLED=true

# Integration Configuration
INTEGRATION_BATCH_SIZE=100
INTEGRATION_RETRY_DELAY=5
INTEGRATION_MAX_CONCURRENT=10
```

### Environment-Specific Configuration

#### Development (.env.development)

```bash
# Development Environment Configuration
ENVIRONMENT=development
FLX_LOG_LEVEL=DEBUG
FLX_DEBUG_MODE=true

# Development Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wms_dev
DB_SSL_MODE=disable

# Development WMS (Sandbox)
WMS_URL=https://sandbox.wms.oraclecloud.com
WMS_TIMEOUT=60
```

#### Production (.env.production)

```bash
# Production Environment Configuration
ENVIRONMENT=production
FLX_LOG_LEVEL=INFO
FLX_DEBUG_MODE=false
FLX_METRICS_ENABLED=true

# Production Database (use secrets management)
DB_SSL_MODE=require
DB_CONNECTION_POOL_SIZE=20
DB_CONNECTION_TIMEOUT=30

# Production WMS
WMS_TIMEOUT=30
WMS_MAX_RETRIES=5
WMS_CIRCUIT_BREAKER_ENABLED=true
```

## Implementation Examples

### FLX Framework Configuration

```python
from flext.core.config import FlxConfig
from flext.core.logging import FlxLogger

class FlxIntegrationConfig(FlxConfig):
    """FLX framework configuration for Oracle integration."""

    def __init__(self):
        super().__init__()

        # WMS Integration Settings
        self.wms_url = self.get_required("WMS_URL")
        self.wms_username = self.get_required("WMS_USERNAME")
        self.wms_password = self.get_required("WMS_PASSWORD")
        self.wms_timeout = self.get_int("WMS_TIMEOUT", 30)

        # Database Settings
        self.db_host = self.get_required("DB_HOST")
        self.db_port = self.get_int("DB_PORT", 5432)
        self.db_name = self.get_required("DB_NAME")
        self.db_user = self.get_required("DB_USER")
        self.db_password = self.get_required("DB_PASSWORD")

        # FLX Framework Settings
        self.log_level = self.get("FLX_LOG_LEVEL", "INFO")
        self.debug_mode = self.get_bool("FLX_DEBUG_MODE", False)
        self.metrics_enabled = self.get_bool("FLX_METRICS_ENABLED", True)

    def get_database_url(self) -> str:
        """Build database URL from components."""
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def get_wms_config(self) -> dict[str, Any]:
        """Get WMS configuration dictionary."""
        return {
            "url": self.wms_url,
            "username": self.wms_username,
            "password": self.wms_password,
            "timeout": self.wms_timeout
        }
```

### Oracle WMS Adapter Configuration

```python
from flext.adapters.outbound.oracle import OracleWmsAdapter
from flext.core.exceptions import ConfigurationError

class WmsAdapterFactory:
    """Factory for creating configured WMS adapters."""

    @staticmethod
    def create_wms_adapter() -> OracleWmsAdapter:
        """Create WMS adapter with environment configuration."""
        config = FlxIntegrationConfig()

        try:
            adapter = OracleWmsAdapter(
                base_url=config.wms_url,
                username=config.wms_username,
                password=config.wms_password,
                timeout=config.wms_timeout,
                retry_config={
                    "max_retries": config.get_int("WMS_MAX_RETRIES", 3),
                    "retry_delay": config.get_int("WMS_RETRY_DELAY", 1),
                    "backoff_factor": config.get_float("WMS_BACKOFF_FACTOR", 2.0)
                },
                circuit_breaker_config={
                    "failure_threshold": config.get_int("WMS_CB_FAILURE_THRESHOLD", 5),
                    "recovery_timeout": config.get_int("WMS_CB_RECOVERY_TIMEOUT", 60),
                    "expected_exception": Exception
                }
            )

            return adapter

        except ConfigurationError as e:
            logger = FlxLogger("wms.adapter.factory")
            logger.error("Failed to create WMS adapter: %s", str(e))
            raise
```

## Development Workflow

### 1. Initial Setup

```bash
# 1. Copy example configuration
cp .env.example .env.local

# 2. Edit local configuration
nano .env.local

# 3. Verify configuration
python -c "from config import FlxIntegrationConfig; config = FlxIntegrationConfig(); print('Configuration valid')"
```

### 2. Configuration Validation Script

```python
#!/usr/bin/env python3
"""Validate environment configuration."""

import os
import sys
from pathlib import Path
from typing import Dict, List

def validate_environment() -> Dict[str, Any]:
    """Validate environment configuration."""
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "config_summary": {}
    }

    # Required variables by category
    required_vars = {
        "wms": ["WMS_URL", "WMS_USERNAME", "WMS_PASSWORD"],
        "database": ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"],
        "api": ["API_KEY", "API_SECRET"]
    }

    for category, vars in required_vars.items():
        missing_vars = [var for var in vars if not os.getenv(var)]

        if missing_vars:
            results["errors"].append(f"Missing {category} variables: {', '.join(missing_vars)}")
            results["valid"] = False
        else:
            results["config_summary"][category] = "configured"

    # Check for insecure default values
    insecure_patterns = ["default", "example", "changeme", "password"]

    for var_name in os.environ:
        if any(prefix in var_name for prefix in ["WMS_", "DB_", "API_"]):
            value = os.getenv(var_name, "").lower()
            if any(pattern in value for pattern in insecure_patterns):
                results["warnings"].append(f"{var_name} appears to use default/example value")

    return results

if __name__ == "__main__":
    validation = validate_environment()

    print("Environment Configuration Validation")
    print("=" * 40)

    if validation["valid"]:
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration has errors")
        for error in validation["errors"]:
            print(f"  - {error}")

    if validation["warnings"]:
        print("\n⚠️  Warnings:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")

    print(f"\nConfiguration Summary: {validation['config_summary']}")

    sys.exit(0 if validation["valid"] else 1)
```

### 3. IDE Integration

#### VSCode/Cursor Settings

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.envFile": "${workspaceFolder}/.env.local",
  "python.terminal.activateEnvironment": true,
  "files.exclude": {
    ".env.local": false,
    ".env.production": true,
    ".env.staging": true
  }
}
```

## Security Best Practices

### 1. Secrets Management

```python
# Production secrets management
import boto3
from typing import Optional

class SecretsManager:
    """Manage secrets from AWS Secrets Manager."""

    def __init__(self, region_name: str = "us-east-1"):
        self.client = boto3.client("secretsmanager", region_name=region_name)

    def get_secret(self, secret_name: str) -> Optional[str]:
        """Retrieve secret from AWS Secrets Manager."""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return response["SecretString"]
        except Exception as e:
            logger.error("Failed to retrieve secret %s: %s", secret_name, str(e))
            return None

    def get_database_config(self) -> Dict[str, str]:
        """Get database configuration from secrets."""
        db_secret = self.get_secret("wms-integration/database")
        if db_secret:
            return json.loads(db_secret)
        return {}
```

### 2. Configuration Auditing

```python
def audit_configuration() -> Dict[str, Any]:
    """Audit configuration for security issues."""
    audit_results = {
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "issues": [],
        "recommendations": []
    }

    # Check for insecure configurations
    if os.getenv("FLX_DEBUG_MODE", "").lower() == "true":
        if os.getenv("ENVIRONMENT") == "production":
            audit_results["issues"].append("Debug mode enabled in production")

    # Check for weak passwords
    password_vars = [var for var in os.environ if "PASSWORD" in var]
    for var in password_vars:
        password = os.getenv(var, "")
        if len(password) < 12:
            audit_results["issues"].append(f"{var} appears to be weak (length < 12)")

    # Check for HTTP URLs in production
    if os.getenv("ENVIRONMENT") == "production":
        url_vars = [var for var in os.environ if "URL" in var]
        for var in url_vars:
            url = os.getenv(var, "")
            if url.startswith("http://"):
                audit_results["issues"].append(f"{var} uses insecure HTTP in production")

    return audit_results
```

## Testing Configuration

### Unit Tests for Configuration

```python
import pytest
import os
from unittest.mock import patch
from config import FlxIntegrationConfig, ConfigurationError

class TestConfiguration:
    """Test configuration management."""

    def test_valid_configuration(self):
        """Test configuration with all required variables."""
        env_vars = {
            "WMS_URL": "https://test.wms.oraclecloud.com",
            "WMS_USERNAME": "test_user",
            "WMS_PASSWORD": "test_password",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "test_db",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_password"
        }

        with patch.dict(os.environ, env_vars):
            config = FlxIntegrationConfig()
            assert config.wms_url == "https://test.wms.oraclecloud.com"
            assert config.db_port == 5432

    def test_missing_required_configuration(self):
        """Test configuration with missing required variables."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError):
                FlxIntegrationConfig()

    def test_database_url_generation(self):
        """Test database URL generation."""
        env_vars = {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "test_db",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_password"
        }

        with patch.dict(os.environ, env_vars):
            config = FlxIntegrationConfig()
            expected_url = "postgresql://test_user:test_password@localhost:5432/test_db"
            assert config.get_database_url() == expected_url
```

## Troubleshooting

### Common Issues

#### 1. Configuration Not Loading

```bash
# Check if .env.local exists and is readable
ls -la .env.local
cat .env.local

# Verify environment variables are set
env | grep WMS_
env | grep DB_
```

#### 2. IDE Not Recognizing Configuration

```bash
# Restart IDE after changing .env.local
# Check IDE environment file settings
# Verify Python interpreter is correct
```

#### 3. Configuration Validation Failures

```python
# Run configuration validation script
python validate_config.py

# Check for typos in variable names
# Verify all required variables are set
# Check for conflicting environment files
```

## 🏗️ **Advanced Configuration Architecture**

### **Enterprise Configuration System**

The FLX framework includes a sophisticated configuration system with hierarchical management and multiple backend support:

```
/flext/src/flext/infra/config/
├── hierarchical.py      # Multi-level configuration management
├── backends.py          # YAML, Vault, KMS backend support
├── adapter.py           # Configuration adapter for hexagonal architecture
├── settings.py          # Advanced settings management
└── dynaconf_settings.py # Dynaconf integration for enterprise features
```

### **Hierarchical Configuration Management**

Production configuration system with automatic precedence handling:

```python
from flext.infra.config import ConfigManager

# Hierarchical configuration with automatic resolution
config = ConfigManager()
config.load_from_file("config/base.yaml")       # Base configuration
config.load_from_env("development")             # Environment overrides
config.load_from_vault("secret/myapp")          # Secrets from Vault
config.load_from_environment_variables()       # Environment variable overrides

# Automatic precedence: ENV_VARS > Vault > Environment > Base
database_url = config.get("database.url")
```

### **Multiple Backend Support**

Enterprise backend configuration management:

```python
# YAML file backend
config.add_backend("yaml", path="config/app.yaml")

# HashiCorp Vault backend (production secrets)
config.add_backend("vault", {
    "url": "https://vault.company.com",
    "token": "${VAULT_TOKEN}",
    "path": "secret/myapp"
})

# AWS KMS backend (encrypted configuration)
config.add_backend("kms", {
    "region": "us-east-1",
    "key_id": "alias/app-config"
})
```

### **Configuration Profiles**

Environment-specific configuration profiles:

```python
# Profile-based configuration management
config.set_profile("production")    # Activates production-specific settings
config.set_profile("development")   # Activates development-specific settings
config.set_profile("testing")       # Activates testing-specific settings

# Profile-specific configuration resolution
database_config = config.get_profile_config("database")
```

## See Also

- [Security Best Practices](../security/security-best-practices.md) - Comprehensive security guidelines
- [Configuration Patterns](../architecture/configuration-patterns.md) - Configuration architecture patterns
- [Deployment Guide](../deployment/deployment-guide.md) - Production deployment configuration
- [Testing Configuration](../development/testing-configuration.md) - Testing configuration management

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Development Hub](../index.md) - Development environment fundamentals and workflow setup
- [Getting Started Hub](../../getting-started/index.md) - Framework installation and basic configuration
- [Security Hub](../../security/index.md) - Security fundamentals before handling sensitive configuration

### **Next Steps**

- [Schema Management Guide](./schema-management-guide.md) - Database schema configuration using environment settings
- [Development Tools](../tools/index.md) - Tools that integrate with environment configuration
- [Infrastructure Hub](../../infrastructure/index.md) - Production infrastructure applying these configuration patterns

### **Related Topics**

- [Real-World Implementation Guide](../../getting-started/real-world-implementation-guide.md) - Production implementation examples using these configuration patterns
- [Infrastructure Services](../../infrastructure/infrastructure-services-comprehensive.md) - Infrastructure services leveraging environment configuration
- [Oracle Integration Guides](../../guides/oracle/index.md) - Oracle-specific configuration applying these patterns
- [Security Best Practices](../../security/index.md) - Advanced security practices for configuration management
- [Architecture Configuration](../../architecture/index.md) - System architecture supporting configuration strategies
- [Deployment Guide](../../deployment/index.md) - Production deployment using secure configuration management

---

**📂 Hub**: [Guides Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
