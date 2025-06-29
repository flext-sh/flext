# Oracle WMS CLI Guide - Guides

> **Function**: Complete command-line interface guide for Oracle WMS operations | **Audience**: Developers, operators | **Status**: ✅ VALIDATED

[![Oracle WMS](https://img.shields.io/badge/oracle-wms-red.svg)](./index.md)
[![CLI](https://img.shields.io/badge/cli-interface-blue.svg)](../../development/guides/cli-implementation.md)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../../index.md)

**Comprehensive command-line interface for Oracle WMS operations using the FLX Framework with validated implementation examples**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides](../index.md) → **📂 Oracle**: [Oracle Hub](./index.md) → **📄 Current**: Oracle WMS CLI Guide

### **📍 Learning Path Position**

```
[Oracle WMS Integration](./oracle-wms-comprehensive-integration-guide.md) → **[WMS CLI]** → [WMS Operations](./oracle-wms-operations-guide.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Oracle Integration Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Source Code**: [FLX Oracle WMS CLI](../../../flext_http_oracle_wms/scripts/)
- **🔗 Related**: [WMS Integration Guide](./oracle-wms-comprehensive-integration-guide.md), [CLI Implementation](../../development/guides/cli-implementation.md)

---

## 📋 **Overview**

This guide provides comprehensive command-line interface usage for Oracle WMS operations using the FLX Framework. It covers installation, configuration, and all available CLI commands with practical examples.

## 🔗 **Cross-Section Navigation**

### **⬅️ Prerequisites**

- [Oracle WMS Integration Guide](./oracle-wms-comprehensive-integration-guide.md) - Essential understanding of WMS client implementation and architecture
- [Getting Started Hub](../../getting-started/index.md) - FLX Framework installation and environment setup required
- [Development Hub](../../development/index.md) - CLI development patterns and command-line interface fundamentals

### **➡️ Next Steps**

- [Oracle WMS Operations Guide](./oracle-wms-operations-guide.md) - Advanced WMS operations and business logic patterns
- [Oracle WMS API Reference](./oracle-wms-complete-api-reference.md) - Complete API documentation for programmatic WMS access
- [Oracle WMS Integration Validated](./oracle-wms-integration-validated.md) - Production integration patterns and troubleshooting

### **🔗 Related Topics**

- [Examples Hub](../../examples/index.md) - Working Oracle WMS CLI examples and automation scripts
- [Authentication Hub](../authentication/index.md) - Authentication patterns for Oracle WMS CLI access
- [Infrastructure Hub](../../infrastructure/index.md) - Production infrastructure for CLI automation and batch operations
- [Development Hub](../../development/index.md) - Testing frameworks for CLI applications and automation workflows
- [Security Hub](../../security/index.md) - Security implementation patterns for CLI tools accessing Oracle systems

### **What You'll Learn**

- Oracle WMS CLI installation and configuration
- Command-line operations and syntax
- Advanced CLI usage patterns
- Troubleshooting common CLI issues

## Installation

```bash
# Install from the flext_project directory
pip install -e .

# Or install using poetry
poetry install
```

## Prerequisites

### Environment Variables

Set up the following environment variables before using the CLI:

```bash
export WMS_HOST="your-wms-host.com"
export WMS_PORT="443"
export WMS_USERNAME="your-username"
export WMS_PASSWORD="your-password"
export WMS_USE_SSL="true"
export WMS_TIMEOUT="30"
export WMS_MAX_RETRIES="3"
```

### Configuration File (Optional)

Create a configuration file in JSON format:

```json
{
  "host": "your-wms-host.com",
  "port": 443,
  "username": "your-username",
  "password": "your-password",
  "use_ssl": true,
  "timeout": 30,
  "max_retries": 3
}
```

## Basic Usage

### Getting Help

```bash
# General help
flext-http-oracle-wms --help

# Command-specific help
flext-http-oracle-wms test-connection --help
```

### Version Information

```bash
flext-http-oracle-wms --version
```

## Core Commands

### 1. Connection Testing

Test your connection to the Oracle WMS system:

```bash
flext-http-oracle-wms test-connection
```

### 2. Entity Discovery

Discover all available entities in the WMS system:

```bash
flext-http-oracle-wms discover-entities
```

### 3. Schema Operations

Get the schema for a specific entity:

```bash
# Basic schema retrieval
flext-http-oracle-wms get-schema items

# Output in JSON format
flext-http-oracle-wms --output-format json get-schema items

# Output in YAML format
flext-http-oracle-wms --output-format yaml get-schema orders
```

### 4. Record Operations

#### List Records

```bash
# List first 10 records (default)
flext-http-oracle-wms list-records items

# List with custom limit and pagination
flext-http-oracle-wms list-records items --limit 50 --offset 100

# Output in different formats
flext-http-oracle-wms list-records items --format-output json
flext-http-oracle-wms list-records items --format-output yaml
```

#### Get Specific Record

```bash
# Get record by ID
flext-http-oracle-wms get-record items ITEM001

# Output in specific format
flext-http-oracle-wms get-record orders ORD-2024-001 --format-output json
```

#### Create New Record

```bash
# Create record from JSON file
flext-http-oracle-wms create-record items --data-file new_item.json
```

Example `new_item.json`:

```json
{
  "itemId": "ITEM001",
  "description": "Sample Item",
  "unitPrice": 29.99,
  "category": "Electronics",
  "active": true
}
```

#### Update Existing Record

```bash
# Update record from JSON file
flext-http-oracle-wms update-record items ITEM001 --data-file updated_item.json
```

#### Delete Record

```bash
# Delete with confirmation prompt
flext-http-oracle-wms delete-record items ITEM001

# Delete without prompt (use with caution!)
flext-http-oracle-wms delete-record items ITEM001 --confirm
```

### 5. Data Export

Export entity data to various formats:

```bash
# Export to JSON (default)
flext-http-oracle-wms export-data items items_backup.json

# Export to CSV
flext-http-oracle-wms export-data orders orders.csv --format-export csv

# Export to YAML with limit
flext-http-oracle-wms export-data locations locations.yaml --format-export yaml --limit 1000

# Export all records (no limit)
flext-http-oracle-wms export-data items all_items.json
```

### 6. Configuration

Show current configuration:

```bash
# Display configuration
flext-http-oracle-wms show-config

# Output as JSON
flext-http-oracle-wms --output-format json show-config
```

## Global Options

All commands support these global options:

### Debug and Verbose Mode

```bash
# Enable debug mode
flext-http-oracle-wms --debug test-connection

# Enable verbose output
flext-http-oracle-wms --verbose discover-entities

# Combine both
flext-http-oracle-wms --debug --verbose list-records items
```

### Output Formats

```bash
# JSON output
flext-http-oracle-wms --output-format json get-schema items

# YAML output
flext-http-oracle-wms --output-format yaml show-config

# Table output (default)
flext-http-oracle-wms --output-format table list-records items
```

### Custom Configuration File

```bash
# Use custom config file
flext-http-oracle-wms --config-file /path/to/config.json test-connection
```

## Advanced Usage

### Batch Operations

You can combine CLI commands in scripts for batch operations:

```bash
#!/bin/bash

# Export all entity data
entities=("items" "orders" "locations" "customers")

for entity in "${entities[@]}"; do
    echo "Exporting ${entity}..."
    flext-http-oracle-wms export-data "$entity" "${entity}_backup.json"
done
```

### Data Pipeline Integration

Use the CLI in data pipelines:

```bash
# 1. Discover entities
flext-http-oracle-wms discover-entities --output-format json > entities.json

# 2. Export data for each entity
cat entities.json | jq -r '.[]' | while read entity; do
    flext-http-oracle-wms export-data "$entity" "data/${entity}.json"
done

# 3. Validate export
for file in data/*.json; do
    echo "Validating $file..."
    jq . "$file" > /dev/null && echo "✓ Valid JSON" || echo "✗ Invalid JSON"
done
```

## Error Handling

The CLI provides comprehensive error messages:

### Connection Errors

```bash
$ flext-http-oracle-wms test-connection
❌ Connection failed: Unable to connect to host your-wms-host.com
```

### Authentication Errors

```bash
$ flext-http-oracle-wms discover-entities
❌ Discovery failed: Authentication failed - invalid credentials
```

### Not Found Errors

```bash
$ flext-http-oracle-wms get-record items NON_EXISTENT
❌ Failed to get record: Record NON_EXISTENT not found in entity items
```

## Performance Tips

1. **Use pagination** for large datasets:

   ```bash
   flext-http-oracle-wms list-records items --limit 100 --offset 0
   ```

2. **Enable debug mode** for troubleshooting:

   ```bash
   flext-http-oracle-wms --debug --verbose command
   ```

3. **Use specific output formats** for integration:

   ```bash
   flext-http-oracle-wms --output-format json discover-entities
   ```

## Integration with FLX Framework

The CLI is built on the FLX framework extension architecture, providing:

- **Dynamic Discovery**: Automatically discovers available entities and operations
- **Type Safety**: Runtime validation using Pydantic models
- **Extensibility**: Easy to add new commands and functionality
- **Standards Compliance**: Follows FLX framework patterns and conventions

## Troubleshooting

### Common Issues

1. **Environment Variables Not Set**

   ```bash
   # Check if variables are set
   echo $WMS_HOST $WMS_USERNAME

   # Set missing variables
   export WMS_HOST="your-host.com"
   ```

2. **SSL/TLS Issues**

   ```bash
   # Disable SSL for testing (not recommended for production)
   export WMS_USE_SSL="false"
   ```

3. **Timeout Issues**

   ```bash
   # Increase timeout
   export WMS_TIMEOUT="60"
   ```

4. **Permission Issues**

   ```bash
   # Check credentials
   flext-http-oracle-wms test-connection --debug
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
flext-http-oracle-wms --debug --verbose command
```

This will show:

- HTTP requests and responses
- Authentication details
- Error stack traces
- Performance metrics

## Examples

See the `examples/cli_usage.py` file for programmatic usage examples and additional CLI command demonstrations.

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Oracle WMS Integration Guide](./oracle-wms-comprehensive-integration-guide.md) - Understanding WMS client and configuration
- [Getting Started](../../getting-started/index.md) - FLX Framework installation and environment setup
- [CLI Implementation Guide](../../development/guides/cli-implementation.md) - CLI development patterns and best practices

### **Next Steps**

- [Oracle WMS Operations Guide](./oracle-wms-operations-guide.md) - Advanced WMS operations and workflows
- [Oracle Integration Mappings](./oracle-integration-mappings.md) - Data mapping patterns and transformations
- [Performance Optimization](../../optimization/performance/index.md) - CLI performance tuning strategies

### **Related Topics**

- [Oracle Authentication Guide](./oracle-authentication-unified-guide.md) - Authentication setup and troubleshooting
- [Development Testing](../../development/testing/integration-testing-guide.md) - CLI testing strategies
- [Examples Hub](../../examples/index.md) - Working CLI usage examples and scripts

---

## 🆘 **Support and Troubleshooting**

### **Common Issues**

For issues and questions:

1. Check the debug output with `--debug --verbose`
2. Verify environment variables and configuration
3. Test connection with `test-connection` command
4. Review the logs for detailed error information

### **Additional Resources**

- [Oracle WMS Integration Troubleshooting](./oracle-wms-comprehensive-integration-guide.md#troubleshooting)
- [CLI Development Guide](../../development/guides/cli-implementation.md)
- [Framework Support](../../getting-started/index.md#support)

---

**📂 Hub**: [Oracle Integration Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
