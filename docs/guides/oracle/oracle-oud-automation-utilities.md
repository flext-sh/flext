# 🛠️ Oracle OUD Automation Utilities Complete Guide

> **Function**: Complete Oracle Unified Directory automation utilities and tools | **Audience**: Directory REDACTED_LDAP_BIND_PASSWORDistrators, DevOps engineers | **Status**: Production-ready

[![Oracle OUD](https://img.shields.io/badge/Oracle-OUD-red.svg)](./index.md)
[![Automation](https://img.shields.io/badge/automation-utilities-blue.svg)](./oracle-oud-automation-guide.md)
[![Framework](https://img.shields.io/badge/framework-FLX_0.4.0-orange.svg)](../../index.md)

**Complete Oracle Unified Directory automation utilities guide providing streamlined tools for OUD operations, testing, configuration management, and migration tasks**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides Hub](../index.md) → **📂 Oracle**: [Oracle Hub](./index.md) → **📄 Current**: OUD Automation Utilities Complete Guide

### **📍 Learning Path Position**

```
[Oracle Hub](./index.md) → **[OUD Automation Utilities Complete Guide]** → [OUD Automation Guide](./oracle-oud-automation-guide.md)
```

## 🎯 **Quick Navigation**

- **📂 Section Hub**: [Oracle Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Related**: [OUD Automation Guide](./oracle-oud-automation-guide.md) | [OUD Schema Migration](./oracle-oud-schema-migration-guide.md)

---

## 📋 **Overview**

This comprehensive guide covers the simplified utility tools for Oracle Unified Directory (OUD) Automation. These enterprise-grade tools provide streamlined interfaces for common OUD operations, testing, configuration management, and migration tasks within the FLX Framework ecosystem.

## 🚀 **Getting Started**

### **Prerequisites**

- Oracle Unified Directory (OUD) environment configured
- Python 3.13+ with FLX Framework installed
- Administrative access to OUD instances
- Network connectivity to target LDAP servers

### **Installation**

#### **Automatic Installation**

Create symbolic links of utilities in the `~/bin` directory:

```bash
# Default installation to ~/bin
python create_links.py

# Custom installation directory
python create_links.py -d /custom/path/bin

# System-wide installation (requires sudo)
sudo python create_links.py -d /usr/local/bin
```

#### **Manual Installation**

```bash
# Clone and setup
git clone <repository-url>
cd oud-automation
pip install -e .

# Create symbolic links manually
ln -s $(pwd)/oud_simple_env.py ~/bin/oud-simple-env
ln -s $(pwd)/oud_simple_test.py ~/bin/oud-simple-test
ln -s $(pwd)/oud_simple_cli.py ~/bin/oud-simple-cli
ln -s $(pwd)/oud_setup_test.py ~/bin/oud-setup-test
```

## 🛠️ **Available Utilities**

### **🔧 LDAP Configuration Editor** (`oud-simple-env`)

Enterprise-grade tool for managing LDAP environment variables and configuration files.

#### **Core Operations**

```bash
# View current configuration
oud-simple-env show

# Show with secrets (use carefully)
oud-simple-env show --include-secrets

# Edit Source LDAP configuration
oud-simple-env edit -e source

# Edit Target LDAP configuration
oud-simple-env edit -e target

# Backup current configuration
oud-simple-env backup --output-file config-backup-$(date +%Y%m%d).env

# Validate configuration syntax
oud-simple-env validate --check-connectivity
```

### **🧪 LDAP Connection Test** (`oud-simple-test`)

Comprehensive tool for testing LDAP connections and validating environment configurations.

#### **Testing Operations**

```bash
# Test both connections (default)
oud-simple-test

# Test specific endpoint
oud-simple-test --endpoint source
oud-simple-test --endpoint target

# Test with mock LDAP (for development)
oud-simple-test --mock

# Advanced testing with detailed output
oud-simple-test --verbose --performance-metrics

# Test with custom timeout
oud-simple-test --timeout 30 --retry-attempts 3
```

### **⚡ Simplified CLI** (`oud-simple-cli`)

Streamlined command-line interface for common OUD automation operations.

#### **Administrative Operations**

```bash
# View configuration
oud-simple-cli config --show

# Test connections
oud-simple-cli test-connection
oud-simple-cli test-connection --endpoint source --detailed

# Health check
oud-simple-cli health-check --all-endpoints

# Performance monitoring
oud-simple-cli monitor --interval 30 --duration 300
```

### **🏗️ Test Environment Setup** (`oud-setup-test`)

Professional tool for setting up local test environments with mock LDAP servers.

#### **Environment Management**

```bash
# View setup instructions
oud-setup-test

# Create .env file for local testing
oud-setup-test --create-config

# Setup complete test environment
oud-setup-test --full-setup --with-ssl

# Generate sample data
oud-setup-test --generate-test-data --entries 1000

# Reset test environment
oud-setup-test --reset --confirm
```

## Environment Variables

The tools use the following environment variables from the `.env` file:

### Source LDAP

| Variable             | Description                |
| -------------------- | -------------------------- |
| SOURCE_LDAP_HOST     | LDAP server hostname or IP |
| SOURCE_LDAP_PORT     | LDAP server port           |
| SOURCE_LDAP_BIND_DN  | Authentication DN          |
| SOURCE_LDAP_PASSWORD | Authentication password    |
| SOURCE_LDAP_BASE_DN  | Base DN for searches       |
| SOURCE_LDAP_USE_SSL  | Use SSL (true/false)       |

### Target LDAP

| Variable             | Description                |
| -------------------- | -------------------------- |
| TARGET_LDAP_HOST     | LDAP server hostname or IP |
| TARGET_LDAP_PORT     | LDAP server port           |
| TARGET_LDAP_BIND_DN  | Authentication DN          |
| TARGET_LDAP_PASSWORD | Authentication password    |
| TARGET_LDAP_BASE_DN  | Base DN for searches       |
| TARGET_LDAP_USE_SSL  | Use SSL (true/false)       |

## LDAP Mock Mode

For testing without a real LDAP server, you can use mock mode:

1. Ensure the `mock_ldap.py` file is present in the same directory
2. Run tests with the `--mock` flag:

   ```bash
   oud-simple-test --mock
   ```

Mock mode simulates a successful LDAP server connection and is useful for:

- Testing when the real server is unavailable
- Configuration verification without connection attempts
- Demonstrations and training

## Advanced Usage

### Batch Operations

Execute multiple operations in sequence:

```bash
# Test all connections and show configuration
oud-simple-test && oud-simple-env show

# Setup test environment and verify
oud-setup-test --create-config && oud-simple-test --mock
```

### Configuration Templates

Create configuration templates for different environments:

```bash
# Development environment
oud-simple-env edit -e source --template dev

# Production environment
oud-simple-env edit -e source --template prod
```

### Integration with FLX Framework

These utilities integrate seamlessly with the FLX framework:

```python
from flext.adapters.oracle.oud import OUDUtilities

# Initialize utilities
utils = OUDUtilities()

# Test connections programmatically
source_status = await utils.test_connection('source')
target_status = await utils.test_connection('target')

# Get configuration
config = utils.get_configuration()
```

### Monitoring and Logging

Enable detailed logging for troubleshooting:

```bash
# Enable verbose logging
export OUD_LOG_LEVEL=DEBUG

# Test with detailed output
oud-simple-test --verbose

# Monitor connection status
oud-simple-cli monitor --interval 30
```

## Security Considerations

### Credential Management

- Store credentials securely in `.env` files
- Use encrypted connections (SSL/TLS) when possible
- Rotate passwords regularly
- Limit access to configuration files

### Network Security

```bash
# Test SSL connection
oud-simple-test --ssl-verify

# Use secure ports
SOURCE_LDAP_PORT=636  # LDAPS
TARGET_LDAP_PORT=636  # LDAPS
```

## Production Deployment

### Environment Setup

For production deployment:

1. **Create production configuration:**

   ```bash
   oud-simple-env edit -e source --environment production
   ```

2. **Validate connections:**

   ```bash
   oud-simple-test --environment production --ssl-verify
   ```

3. **Monitor health:**

   ```bash
   oud-simple-cli health-check --continuous
   ```

### High Availability

Configure failover connections:

```bash
# Primary and backup servers
SOURCE_LDAP_HOST=ldap-primary.company.com
SOURCE_LDAP_HOST_BACKUP=ldap-backup.company.com

# Test failover
oud-simple-test --test-failover
```

## Troubleshooting

### Common Issues

1. **Connection timeouts:**

   ```bash
   # Increase timeout
   oud-simple-test --timeout 60
   ```

2. **SSL certificate issues:**

   ```bash
   # Skip SSL verification (development only)
   oud-simple-test --ssl-no-verify
   ```

3. **Authentication failures:**

   ```bash
   # Test with different credentials
   oud-simple-test --bind-dn "cn=REDACTED_LDAP_BIND_PASSWORD,dc=company,dc=com"
   ```

### Debug Mode

Enable debug mode for detailed troubleshooting:

```bash
# Enable debug logging
export OUD_DEBUG=true

# Run with maximum verbosity
oud-simple-test --debug --verbose
```

## 📝 **Important Notes**

### **Tool Behavior**

- **📁 Configuration Discovery**: Tools search for `.env` file in current directory, parent directory, or script directory
- **🔧 Framework Independence**: These tools are independent of the complete OUD Automation framework, allowing use even with dependency issues
- **🤖 Automation Support**: All utilities support both interactive and non-interactive modes for automation
- **✅ Validation**: Configuration changes are validated before being applied
- **🔒 Security**: Enterprise-grade security controls and credential management

### **Enterprise Features**

- **📊 Monitoring**: Comprehensive monitoring and logging capabilities
- **🚨 Error Handling**: Advanced error handling and recovery mechanisms
- **🔄 High Availability**: Failover and backup server support
- **📈 Performance**: Performance metrics and optimization tools
- **🛡️ Security**: SSL/TLS support and credential protection

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Oracle Hub](./index.md) - Understanding Oracle integration architecture before using OUD utilities
- [OUD Automation Guide](./oracle-oud-automation-guide.md) - Core OUD automation concepts and framework setup
- [Getting Started Hub](../../getting-started/index.md) - FLX Framework installation and basic configuration

### **Next Steps**

- [OUD Schema Migration Guide](./oracle-oud-schema-migration-guide.md) - Apply utilities for schema migration tasks
- [Oracle Security Guide](./oracle-security-guide.md) - Implement security controls for OUD utilities
- [Oracle Authentication Setup](./oracle-sso-authentication-setup.md) - Configure authentication for OUD environments

### **Related Topics**

- [LDAP Complete Guide](./ldap-complete-guide.md) - LDAP fundamentals and directory services concepts
- [Oracle Directory Migration](./oracle-directory-migration-complete-guide.md) - Complete directory migration patterns
- [Infrastructure Services](../../infrastructure/index.md) - Infrastructure patterns for directory services
- [Security Architecture](../../security/index.md) - Enterprise security patterns for directory utilities
- [Development Testing](../../development/testing/index.md) - Testing strategies for directory utilities and automation

---

**📂 Hub**: [Oracle Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
