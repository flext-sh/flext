# Oracle OUD Automation Simplified Utilities

**Date**: January 2025
**Status**: Production Ready Tools
**Version**: Complete Utility Suite

## Overview

This document describes the simplified utility tools for Oracle Unified Directory (OUD) Automation. These tools provide a streamlined interface for common OUD operations and migration tasks.

## Installation

Run the script to create symbolic links of utilities in the `~/bin` directory:

```bash
python create_links.py
```

If you prefer a different directory, specify with the `-d` option:

```bash
python create_links.py -d /custom/path/bin
```

## Available Tools

### 1. LDAP Configuration Editor (`oud-simple-env`)

Tool for managing LDAP environment variables in the `.env` file.

#### Commands

**View current configuration:**

```bash
oud-simple-env show
```

**Edit Source LDAP configuration:**

```bash
oud-simple-env edit -e source
```

**Edit Target LDAP configuration:**

```bash
oud-simple-env edit -e target
```

### 2. LDAP Connection Test (`oud-simple-test`)

Tool for testing LDAP connections configured in the `.env` file.

#### Commands

**Test both connections (default):**

```bash
oud-simple-test
```

**Test only source connection:**

```bash
oud-simple-test --endpoint source
```

**Test only target connection:**

```bash
oud-simple-test --endpoint target
```

**Test with mock LDAP:**

```bash
oud-simple-test --mock
```

### 3. Simplified CLI (`oud-simple-cli`)

Simplified command-line interface for basic OUD Automation operations.

#### Commands

**View configuration:**

```bash
oud-simple-cli config --show
```

**Test connection:**

```bash
oud-simple-cli test-connection
oud-simple-cli test-connection --endpoint source
```

### 4. Test Environment Setup (`oud-setup-test`)

Tool for setting up a local test environment with mock LDAP servers.

#### Commands

**View setup instructions:**

```bash
oud-setup-test
```

**Create .env file for local testing:**

```bash
oud-setup-test --create-config
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
from flx.adapters.oracle.oud import OUDUtilities

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
   oud-simple-test --bind-dn "cn=admin,dc=company,dc=com"
   ```

### Debug Mode

Enable debug mode for detailed troubleshooting:

```bash
# Enable debug logging
export OUD_DEBUG=true

# Run with maximum verbosity
oud-simple-test --debug --verbose
```

## Related Documentation

- [Oracle OID to OUD Migration Workflow](oracle-oid-to-oud-migration-workflow.md)
- [Oracle OUD Automation Guide](oracle-oud-automation-guide.md)
- [Oracle Security Guide](oracle-security-guide.md)
- [Oracle SSO Authentication Setup](oracle-sso-authentication-setup.md)

## Notes

- Tools search for the `.env` file in the current directory, parent directory, or script directory
- These tools are independent of the complete OUD Automation framework, allowing use even with dependency issues
- All utilities support both interactive and non-interactive modes for automation
- Configuration changes are validated before being applied

This utility suite provides enterprise-grade tooling for Oracle OUD automation with comprehensive error handling and monitoring capabilities.
